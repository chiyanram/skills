import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, run_check

HISTORY = FIXTURES / "history"

FAILING = ["decided-by", "dated-decision", "issue", "other-repo", "ledger-prose", "py-comment", "docstring",
           "js-comment", "yml-comment", "make-comment", "second-pointer"]
PASSING = ["plain", "bare-date", "code-span", "fence", "link", "heading", "html-comment", "py-string", "ledger-row",
           "adr", "principles-status", "changelog", "fixture", "docs-agents", "evals", "one-pointer", "module-pointer"]


class Branch:
    """A git repo in a temp dir: `origin/main` holds the base tree, and a case's files are appended on top."""

    def __init__(self, tmp: str):
        self.root = Path(tmp)
        self.git("init", "--quiet")
        shutil.copytree(HISTORY / "base", self.root, dirs_exist_ok=True)
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def git(self, *args: str):
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)

    def commit(self, message: str):
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "--message", message)

    def lay(self, case: str):
        for source in sorted(p for p in (HISTORY / case).rglob("*") if p.is_file()):
            target = self.root / source.relative_to(HISTORY / case)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("a") as out:
                out.write(source.read_text())


class CheckHistoryTest(unittest.TestCase):
    def check(self, root: Path, expected: int) -> str:
        result = run_check("history", root)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected:
            self.assertTrue(result.stdout.strip(), "a failing check names the problem")
        return result.stdout

    def run_case(self, case: str, expected: int) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            branch = Branch(tmp)
            branch.lay(case)
            branch.commit(case)
            return self.check(branch.root, expected)

    def test_should_fail_each_added_note(self):
        for case in FAILING:
            with self.subTest(case):
                self.run_case(case, 1)

    def test_should_pass_each_spared_or_plain_line(self):
        for case in PASSING:
            with self.subTest(case):
                self.run_case(case, 0)

    def test_should_name_the_file_line_and_kind(self):
        out = self.run_case("decided-by", 1)
        self.assertIn("CONTRIBUTING.md:11: who decided", out)
        self.assertEqual(len(out.splitlines()), 1, "the notes already on the base do not fail")

    def test_should_pass_at_the_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.check(Branch(tmp).root, 0)

    def test_should_pass_a_renamed_file_with_old_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            branch = Branch(tmp)
            branch.git("mv", "CONTRIBUTING.md", "GUIDE.md")
            branch.commit("rename")
            self.check(branch.root, 0)

    def test_should_fail_an_uncommitted_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            branch = Branch(tmp)
            branch.lay("decided-by")
            self.check(branch.root, 1)

    def test_should_fail_an_untracked_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            branch = Branch(tmp)
            branch.lay("untracked")
            self.assertIn("docs/new.md:1", self.check(branch.root, 1))

    def test_should_fail_without_the_base_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            branch = Branch(tmp)
            branch.git("update-ref", "-d", "refs/remotes/origin/main")
            self.assertIn("git fetch origin main", self.check(branch.root, 1))


if __name__ == "__main__":
    unittest.main()
