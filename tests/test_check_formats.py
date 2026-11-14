import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, run_check

FORMATS = FIXTURES / "formats"
SCHEMA = Path("plugins/rulebook/skills/crq/process/schema")


class Release:
    """A git repo in a temp dir: each commit lays a fixture tree over the last and may tag it."""

    def __init__(self, tmp: str):
        self.root = Path(tmp)
        self.git("init", "--quiet")

    def git(self, *args: str):
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
                       check=True, capture_output=True)

    def lay(self, fixture: str):
        shutil.copytree(FORMATS / fixture, self.root, dirs_exist_ok=True)

    def commit(self, fixture: str, tag: str | None = None):
        self.lay(fixture)
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "--message", fixture)
        if tag:
            self.git("tag", tag)


def released(tmp: str) -> Release:
    release = Release(tmp)
    release.commit("released", "rulebook--v3.0.0")
    return release


class CheckFormatsTest(unittest.TestCase):
    def check(self, root: Path, expected: int) -> str:
        result = run_check("formats", root)
        self.assertEqual(result.returncode, expected, result.stdout)
        if expected:
            self.assertTrue(result.stdout.strip(), "a failing check names the problem")
        return result.stdout

    def test_should_pass_an_unchanged_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.check(released(tmp).root, 0)

    def test_should_pass_a_new_version_beside_the_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.lay("new-version")
            self.check(release.root, 0)

    def test_should_pass_a_schema_no_release_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.commit("unreleased-schema")
            (release.root / SCHEMA / "finding-v1.schema.json").write_text("{}\n")
            self.check(release.root, 0)

    def test_should_pass_a_changed_data_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.lay("data-changed")
            self.check(release.root, 0)

    def test_should_read_the_newest_tag_by_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = Release(tmp)
            release.commit("older", "rulebook--v9.0.0")
            release.commit("released", "rulebook--v10.0.0")
            self.check(release.root, 0)

    def test_should_ignore_a_toolbox_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.commit("toolbox", "toolbox--v9.0.0")
            release.lay("released")
            self.check(release.root, 0)

    def test_should_fail_a_released_schema_edited_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.lay("edited-in-place")
            out = self.check(release.root, 1)
            self.assertIn("card-v1.schema.json: differs from rulebook--v3.0.0", out)
            self.assertIn("card-v2.schema.json", out)

    def test_should_fail_an_edit_once_committed(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.commit("edited-in-place")
            self.check(release.root, 1)

    def test_should_fail_a_whitespace_only_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            release.lay("whitespace-only")
            self.assertIn("lanes-v1.schema.json", self.check(release.root, 1))

    def test_should_fail_a_removed_released_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = released(tmp)
            (release.root / SCHEMA / "lanes-v1.schema.json").unlink()
            self.assertIn("removed", self.check(release.root, 1))

    def test_should_fail_with_no_release_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            release = Release(tmp)
            release.commit("released", "toolbox--v1.0.0")
            self.assertIn("git fetch --tags", self.check(release.root, 1))

    def test_should_fail_outside_a_git_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(FORMATS / "released", tmp, dirs_exist_ok=True)
            self.check(Path(tmp), 1)


if __name__ == "__main__":
    unittest.main()
