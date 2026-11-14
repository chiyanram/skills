import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from branch_size import blocks, bucket, counted  # noqa: E402

SCRIPT = ROOT / "scripts" / "branch_size.py"
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
INDEX = "<!-- index: built by make index -->\n| a |\n| b |\n<!-- /index -->\n"
LANES = "<!-- lanes-table: built by make index -->\n| a |\n<!-- /lanes-table -->\n"
DIAGRAM = "<!-- lanes-diagram: built by make index -->\n```\n<!-- /lanes-diagram -->\n"


class HelpersTest(unittest.TestCase):
    def test_should_split_paths_into_code_tests_evals_and_docs(self):
        self.assertEqual([bucket(p) for p in ["scripts/a.py", "tests/b.py", "plugins/p/evals/r/prompt.md",
                                              "plugins/p/skills/s/SKILL.md", "README.md", "evals/x.md"]],
                         ["code", "tests", "evals", "docs", "docs", "docs"])

    def test_should_find_index_and_lanes_blocks_with_their_marker_lines(self):
        self.assertEqual(blocks("x\n" + INDEX + "y\n" + LANES + DIAGRAM), [range(2, 6), range(7, 10), range(10, 13)])

    def test_should_make_no_block_from_an_opening_marker_with_no_closing_marker(self):
        self.assertEqual(blocks("x\n<!-- index: open -->\n| a |\n<!-- /lanes-table -->\n"), [])

    def test_should_count_only_added_lines_outside_the_blocks(self):
        self.assertEqual(counted([1, 2, 5, 6], [range(2, 6)]), 2)


class BranchSizeTest(unittest.TestCase):
    """A temp git repo: `main` holds the base, `topic` the change."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.write({"scripts/gone.py": "a\nb\n", "docs/r.md": "top\n" + INDEX, "tests/old.py": "x\n"})
        self.commit("base")
        self.git("switch", "-q", "-c", "topic")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=self.repo, check=True,
                       capture_output=True, env={**os.environ, **IDENTITY})

    def write(self, contents: dict[str, str]) -> None:
        for path, text in contents.items():
            (self.repo / path).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / path).write_text(text)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def size(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), "main", *args], cwd=self.repo, capture_output=True,
                              text=True)

    def test_should_split_the_count_and_skip_a_change_only_inside_a_block(self):
        self.write({"scripts/new.py": "1\n2\n3\n", "tests/test_new.py": "1\n2\n",
                    "plugins/p/evals/r/prompt.md": "1\n", "docs/r.md": "top\n" + INDEX.replace("| b |", "| c |")})
        self.commit("change")

        result = self.size()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "code      3 lines   1 files",
            "tests     2 lines   1 files",
            "evals     1 lines   1 files",
            "docs      0 lines   0 files",
            "total     6 lines   3 files (PD9: 400 lines, 15 files)",
        ])

    def test_should_count_a_py_file_that_holds_both_markers(self):
        self.write({"scripts/markers.py": INDEX})
        self.commit("markers")

        self.assertIn("code      4 lines   1 files", self.size("HEAD").stdout)

    def test_should_count_a_deleted_file_and_a_renamed_file_as_changed(self):
        self.git("rm", "-q", "scripts/gone.py")
        self.git("mv", "tests/old.py", "tests/new.py")
        self.commit("delete and rename")

        lines = self.size().stdout.splitlines()

        self.assertEqual(lines[:2], ["code      0 lines   1 files", "tests     0 lines   1 files"])

    def test_should_say_over_pd9_and_still_exit_0_past_a_limit(self):
        self.write({f"docs/{n}.md": "x\n" for n in range(16)})
        self.commit("sixteen files")

        result = self.size()

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines()[-1],
                         "total    16 lines  16 files (PD9: 400 lines, 15 files) over PD9")

    def test_should_say_over_pd9_past_the_line_limit(self):
        self.write({"docs/long.md": "x\n" * 401})
        self.commit("long")

        self.assertTrue(self.size().stdout.splitlines()[-1].endswith("401 lines   1 files (PD9: 400 lines, 15 files) "
                                                                     "over PD9"))

    def test_should_not_say_over_pd9_at_exactly_the_limits(self):
        self.write({f"docs/{n}.md": "x\n" for n in range(14)} | {"docs/long.md": "x\n" * 386})
        self.commit("fifteen files, four hundred lines")

        self.assertEqual(self.size().stdout.splitlines()[-1],
                         "total   400 lines  15 files (PD9: 400 lines, 15 files)")

    def test_should_count_against_the_merge_base_not_the_base_tip(self):
        self.write({"scripts/new.py": "1\n"})
        self.commit("topic")
        self.git("switch", "-q", "main")
        self.write({"scripts/main_only.py": "1\n2\n"})
        self.commit("main moves on")

        self.assertEqual(self.size("topic").stdout.splitlines()[0], "code      1 lines   1 files")


if __name__ == "__main__":
    unittest.main()
