import shutil
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, run_check

TYPED = "---\nname: {name}\ndescription: Does one thing when typed.\ndisable-model-invocation: true\n---\n\n{body}\n"
INVOCABLE = "---\nname: {name}\ndescription: Does one thing.\n---\n\n{body}\n"
NOTICE = "## {name}\n\n- Source: owner/repo, `skills/{name}/SKILL.md`\n- Commit: abc1234\n- Licence: MIT\n"


class ToolboxFixture:
    """A repo root with plugins/toolbox/, written to a temp dir (CONTRIBUTING.md: a SKILL.md fixture)."""

    def __init__(self, tmp: str):
        self.root = Path(tmp)
        self.toolbox = self.root / "plugins" / "toolbox"
        (self.toolbox / "skills").mkdir(parents=True)

    def skill(self, name: str, template: str = TYPED, body: str = "Do the one thing.", notice: str | None = NOTICE):
        folder = self.toolbox / "skills" / name
        folder.mkdir()
        (folder / "SKILL.md").write_text(template.format(name=name, body=body))
        if notice is not None:
            with (self.toolbox / "THIRD_PARTY_NOTICES.md").open("a") as notices:
                notices.write(notice.format(name=name) + "\n")
        return folder


class CheckToolboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = ToolboxFixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, name: str = "toolbox"):
        return run_check(name, self.repo.root)

    def assert_fails(self, says: str, name: str = "toolbox"):
        result = self.check(name)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(says, result.stdout)

    def test_should_pass_a_typed_only_skill_with_its_notice(self):
        self.repo.skill("tidy")
        self.assertEqual(self.check().returncode, 0, self.check().stdout)

    def test_should_fail_a_skill_the_model_can_invoke(self):
        self.repo.skill("tidy", template=INVOCABLE)
        self.assert_fails("disable-model-invocation: true")

    def test_should_fail_a_skill_with_no_notice_section(self):
        self.repo.skill("tidy")
        self.repo.skill("sort", notice=None)
        self.assert_fails("no `## sort` section")

    def test_should_pass_a_skill_written_here_with_no_notice(self):
        self.repo.skill("tidy")
        self.repo.skill("sort", notice="## Written here\n\n- `{name}`\n")
        self.assertEqual(self.check().returncode, 0, self.check().stdout)

    def test_should_fail_an_unlisted_skill_when_another_is_written_here(self):
        self.repo.skill("tidy", notice="## Written here\n\n- `{name}`\n")
        self.repo.skill("sort", notice=None)
        self.assert_fails("no `## sort` section")

    def test_should_fail_a_written_here_name_with_no_skill(self):
        self.repo.skill("tidy", notice="## Written here\n\n- `{name}`\n- `gone`\n")
        self.assert_fails("`## Written here` lists `gone`, which is no toolbox skill")

    def test_should_fail_a_notice_without_its_commit(self):
        self.repo.skill("tidy", notice="## tidy\n\n- Source: owner/repo\n- Licence: MIT\n")
        self.assert_fails("has no `Commit:` line")

    def test_should_fail_a_push_merge_cursor_path_or_grok_model(self):
        for body, says in [("Then run `git push origin HEAD`.", "`git push`"), ("Run gh pr merge --squash.", "`gh pr merge`"),
                           ("Save it in `.cursor/skills/`.", "`.cursor/` path"), ("Use grok-4 for search.", "Grok model")]:
            with self.subTest(says), tempfile.TemporaryDirectory() as tmp:
                self.repo = ToolboxFixture(tmp)
                self.repo.skill("tidy", body=body)
                self.assert_fails(says)

    def test_should_pass_a_repo_without_a_toolbox(self):
        shutil.rmtree(self.repo.toolbox)
        self.assertEqual(self.check().returncode, 0)

    def test_should_check_provenance_only_in_a_toolbox_skill_md(self):
        folder = self.repo.skill("tidy")
        (folder / "SURVEY.md").write_text("- [Tracker](https://tracker.example.com/pricing): the tool's own link.\n")
        self.assertEqual(self.check("provenance").returncode, 0, self.check("provenance").stdout)
        (folder / "SKILL.md").write_text(TYPED.format(name="tidy", body="Adapted from https://example.com/tidy."))
        self.assert_fails("a URL", name="provenance")

    def test_should_skip_a_typed_only_skill_in_routing(self):
        shutil.copytree(FIXTURES / "routing" / "good", self.repo.root, dirs_exist_ok=True)
        self.repo.skill("tidy")
        self.assertEqual(self.check("routing").returncode, 0, self.check("routing").stdout)
        (self.repo.toolbox / "skills" / "tidy" / "SKILL.md").write_text(INVOCABLE.format(name="tidy", body="x"))
        self.assert_fails("router tidy has no routing cases", name="routing")


if __name__ == "__main__":
    unittest.main()
