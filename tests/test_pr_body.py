import os
import subprocess
import sys
import unittest

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import pr_body  # noqa: E402

SCRIPT = ROOT / "scripts" / "pr_body.py"
TEMPLATE = (ROOT / ".github" / "pull_request_template.md").read_text()

FILLED = "\n".join([
    "Why: a reserved loan could be renewed; it now cannot. Spec: #42",
    "",
    "Breaking change: no",
    "Rollback: revert this PR; no released format changes.",
    "Where to look: the reservation check in testing/references/strategy.md.",
    "",
    "## Checklist",
    "",
    "- [x] Tests: tests/fixtures/provenance/ gains a planted case",
    "* [X] Docs: none, because no page describes the check",
    "",
    "Closes #42",
])


class PrBodyTest(unittest.TestCase):
    """The description becomes the commit body on main, so CI fails one that still reads as the template."""

    def run_script(self, body: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT)], input=body, capture_output=True, text=True)

    def test_passes_a_description_with_every_line_filled_in(self):
        self.assertEqual(pr_body.problems(FILLED, TEMPLATE), [])
        self.assertEqual(self.run_script(FILLED).returncode, 0)

    def test_fails_the_template_on_each_placeholder_and_each_checklist_item(self):
        found = pr_body.problems(TEMPLATE, TEMPLATE)
        self.assertEqual(len([p for p in found if p.startswith("the placeholder ")]),
                         len(pr_body.placeholders(TEMPLATE)))
        self.assertEqual(len([p for p in found if "is not ticked" in p]),
                         sum(1 for line in TEMPLATE.splitlines() if line.startswith("- [ ]")))
        self.assertEqual(self.run_script(TEMPLATE).returncode, 1)

    def test_fails_an_empty_description_on_the_why_line_and_each_label_line(self):
        self.assertEqual(pr_body.problems("", TEMPLATE), [
            'the first line must be "Why: " and the reason for the change, in one sentence',
            'the "Breaking change:" line is missing or has no answer',
            'the "Rollback:" line is missing or has no answer',
            'the "Where to look:" line is missing or has no answer',
        ])

    def test_names_each_placeholder_left_and_each_unticked_item_by_its_line(self):
        body = (FILLED.replace("Spec: #42", "Spec: #<the approved spec; with no spec, the issue>")
                .replace("- [x] Tests", "- [ ] Tests"))
        self.assertEqual(pr_body.problems(body, TEMPLATE), [
            "the placeholder <the approved spec; with no spec, the issue> is still there: replace it",
            "line 9 is not ticked: answer it, then tick it: - [ ] Tests: tests/fixtures/provenance/ gains a planted case",
        ])

    def test_passes_a_breaking_change_that_carries_all_three_marks(self):
        body = (FILLED.replace("Breaking change: no", "Breaking change: yes, the strategy reference moved")
                .replace("Closes #42", "BREAKING CHANGE: read testing/strategy.md, not references/strategy.md\nCloses #42"))
        self.assertEqual(pr_body.problems(body, TEMPLATE, "feat(testing)!: move the strategy reference (#42)"), [])

    def test_fails_a_breaking_change_whose_line_footer_and_title_disagree(self):
        yes = FILLED.replace("Breaking change: no", "Breaking change: Yes, the reference moved")
        self.assertEqual(pr_body.problems(yes, TEMPLATE, "feat(testing): move the strategy reference (#42)"), [
            'the "Breaking change:" line says yes: add a "BREAKING CHANGE: " footer, what breaks and what to do',
            'the "Breaking change:" line says yes: add "!" after the title\'s scope',
        ])
        footer = FILLED.replace("Closes #42", "BREAKING CHANGE: the reference moved\nCloses #42")
        self.assertEqual(pr_body.problems(footer, TEMPLATE, "feat(testing)!: move the strategy reference (#42)"), [
            'there is a "BREAKING CHANGE:" footer: the "Breaking change:" line must say yes',
            'the title has "!" after its scope: the "Breaking change:" line must say yes',
        ])

    def test_checks_the_titles_mark_only_when_a_title_is_given(self):
        body = (FILLED.replace("Breaking change: no", "Breaking change: yes, the reference moved")
                .replace("Closes #42", "BREAKING CHANGE: the reference moved\nCloses #42"))
        self.assertEqual(pr_body.problems(body, TEMPLATE), [])

    def test_reads_the_title_from_pr_title(self):
        body = FILLED.replace("Breaking change: no", "Breaking change: yes, the reference moved").replace(
            "Closes #42", "BREAKING CHANGE: the reference moved\nCloses #42")
        result = subprocess.run([sys.executable, str(SCRIPT)], input=body, capture_output=True, text=True,
                                env={**os.environ, "PR_TITLE": "feat(testing): move the strategy reference (#42)"})
        self.assertEqual(result.returncode, 1)
        self.assertIn('add "!" after the title\'s scope', result.stdout)

    def test_allows_angle_brackets_the_template_does_not_hold(self):
        self.assertEqual(pr_body.problems(FILLED + "\n\n<details>list<str></details>", TEMPLATE), [])


if __name__ == "__main__":
    unittest.main()
