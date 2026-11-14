import io
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from tests.support import FIXTURES, ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import prove_slices  # noqa: E402
from prove_slices import claim, commands, judge, main, run, slices, spans, split_row  # noqa: E402

S2 = (FIXTURES / "prove_slices" / "363-s2.md").read_text()
GREP_1 = "grep -c '^| test-first |' plugins/rulebook/skills/crq/SKILL.md"
GREP_2 = ("grep -cE '^[|] (design review|code review|timeline record|PR|—) [|]' "
          "plugins/rulebook/skills/crq/SKILL.md")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


class PureHelpersTest(unittest.TestCase):
    """The parser on the raw #363 S2 row: pipes in backticks stay, `\\|` is unescaped, non-commands are reported."""

    def cell(self) -> str:
        [(name, cell)] = slices(S2)
        self.assertTrue(name.startswith("S2 "))
        return cell

    def test_row_splits_into_three_cells(self):
        self.assertEqual(len(split_row(S2.splitlines()[2])), 3)

    def test_escaped_pipe_is_a_literal_pipe_in_the_command(self):
        self.assertEqual(commands(self.cell()), [GREP_1, GREP_2])

    def test_flags_only_and_unknown_spans_are_not_commands_and_make_lint_is_skipped(self):
        verdicts = dict(spans(self.cell()))
        self.assertEqual(verdicts["python3 -c"], "not a command")
        self.assertEqual(verdicts["lanes_graph.phase_ids"], "not a command")
        self.assertEqual(verdicts["make lint"], "skip (CI runs it)")
        self.assertEqual(verdicts["Manual: none"], "skip (manual)")

    def test_make_targets_skip_in_a_chain_and_a_program_off_path_is_not_a_command(self):
        self.assertEqual(dict(spans("`make test && make lint`; `git status`; `no-such-tool run it`")),
                         {"make test && make lint": "skip (CI runs it)", "git status": "run",
                          "no-such-tool run it": "not a command"})

    def test_claim_reads_target_and_today(self):
        self.assertEqual(claim(self.cell(), GREP_2), ("0", "6"))
        self.assertIsNone(claim("`git status` exits 0", "git status"))

    def test_judge(self):
        self.assertEqual(judge(("0", "6"), 0, "70"), "today value differs: prints '70', the spec says 6")
        self.assertIsNone(judge(("0", "6"), 0, "6"))
        self.assertEqual(judge(("0", "6"), 1, "0"), "already prints the target 0")
        self.assertEqual(judge(None, 0, ""), "passes on base")
        self.assertIsNone(judge(None, 1, ""))


class RunTest(unittest.TestCase):
    """One run against a temp repo; the worktree goes away after a failing command and a bad base."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "a.txt").write_text("base\n")
        git(self.repo, "add", "a.txt")
        git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        (self.repo / "a.txt").write_text("head\n")
        (self.repo / "spec.md").write_text(
            "| slice | proving command |\n|---|---|\n"
            "| S1 | `cat a.txt` prints done (base today); `cat missing.txt`; `false`; `make test`; Manual: look |\n")

    def tearDown(self):
        self.tmp.cleanup()

    def prove(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stderr(err):
            code = main(list(argv), repo=self.repo, out=out)
        return code, out.getvalue(), err.getvalue()

    def worktrees(self) -> int:
        return git(self.repo, "worktree", "list").count("\n")

    def test_runs_each_command_on_the_base_and_removes_the_worktree(self):
        code, out, _ = self.prove("spec.md", "HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("  $ cat a.txt\n    exit 0 · last line: base\n", out)
        self.assertIn("  $ cat missing.txt\n    exit 1 · last line: cat: missing.txt: No such file or directory\n", out)
        self.assertIn("  not a command: false\n", out)
        self.assertIn("  skip (CI runs it): make test\n", out)
        self.assertIn("  skip (manual): Manual: look\n", out)
        self.assertNotIn("FLAG", out)
        self.assertEqual(self.worktrees(), 1)

    def test_a_today_value_that_differs_is_flagged(self):
        (self.repo / "spec.md").write_text("| slice | proving command |\n|---|---|\n"
                                           "| S1 | `cat a.txt` prints done (7 today) |\n")
        code, out, _ = self.prove("spec.md", "HEAD")
        self.assertEqual(code, 1)
        self.assertIn("FLAG: today value differs", out)
        self.assertEqual(self.worktrees(), 1)

    def test_a_bad_base_is_reported_and_no_worktree_is_left(self):
        code, _, err = self.prove("spec.md", "no-such-ref")
        self.assertEqual(code, 2)
        self.assertIn("git worktree add no-such-ref failed", err)
        self.assertNotIn("remove failed", err)
        self.assertEqual(self.worktrees(), 1)

    def test_a_missing_spec_is_a_usage_error_not_a_flag(self):
        code, out, err = self.prove("no-such-spec.md", "HEAD")
        self.assertEqual(code, 2)
        self.assertIn("no-such-spec.md: cannot read", err)
        self.assertEqual(err.count("\n"), 1)
        self.assertEqual(out, "")

    def test_each_command_is_printed_before_it_runs(self):
        out = io.StringIO()

        def fake_run(text, worktree):
            self.assertTrue(out.getvalue().endswith(f"  $ {text}\n"), out.getvalue())
            return 0, ""

        with mock.patch.object(prove_slices, "run", fake_run):
            prove_slices.prove([("S1", "`git status`")], self.repo, out)
        self.assertIn("  $ git status\n    exit 0", out.getvalue())

    def test_a_stale_worktree_entry_is_pruned_at_start(self):
        stale = Path(self.tmp.name) / "stale"
        git(self.repo, "worktree", "add", "-q", "--detach", str(stale), "HEAD")
        shutil.rmtree(stale)
        self.prove("spec.md", "HEAD")
        self.assertEqual(self.worktrees(), 1)

    def test_a_remove_failure_does_not_hide_the_first_error(self):
        real = prove_slices._git

        def failing_remove(repo, *args):
            if args[:2] == ("worktree", "remove"):
                return subprocess.CompletedProcess(args, 1, "", "locked")
            return real(repo, *args)

        err = io.StringIO()
        with mock.patch.object(prove_slices, "_git", failing_remove), \
                mock.patch.object(prove_slices, "prove", side_effect=RuntimeError("first")), \
                redirect_stderr(err), self.assertRaisesRegex(RuntimeError, "first"):
            main(["spec.md", "HEAD"], repo=self.repo, out=io.StringIO())
        self.assertIn("git worktree remove failed: locked", err.getvalue())
        git(self.repo, "worktree", "prune")

    def test_a_command_that_runs_too_long_is_killed(self):
        started = time.monotonic()
        code, _ = run("sleep 5 & sleep 5", self.repo, timeout=0.5)
        self.assertIsNone(code)
        self.assertLess(time.monotonic() - started, 3)
        self.assertEqual(judge(None, code, ""), "timed out after 60 s")


if __name__ == "__main__":
    unittest.main()
