import re
import subprocess
import sys
import unittest

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import pr_title  # noqa: E402

SCRIPT = ROOT / "scripts" / "pr_title.py"

PASS = (
    "feat(testing): spock rule file (#123)",
    "chore(release): rulebook 2.0.0",
    "build(deps): bump x",
    "fix(crq): x (owner/repo#12)",
)
FAIL = (
    "docs(crq): DESIGN.md and the glossary describe lanes-v2 as the flow (#364)",
    "feat(crq): a title with no issue",
    "feat: a title with no scope (#123)",
)
# The line the inline rule in ci.yml printed before this script held it.
CI_ERROR = ("::error::PR title \"{title}\" must be 'type(scope): lower-case summary (#issue)', "
            "e.g. 'feat(testing): spock rule file (#123)'. See CONTRIBUTING.md#releases.")


class PrTitleTest(unittest.TestCase):
    """CI's pr-title job and the coordinator run the same rule, so a title CI fails is caught before the PR."""

    def run_script(self, title: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), title], capture_output=True, text=True)

    def test_passes_a_title_that_follows_the_rule(self):
        for title in PASS:
            with self.subTest(title=title):
                result = self.run_script(title)
                self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_fails_a_title_with_the_error_ci_prints(self):
        for title in FAIL:
            with self.subTest(title=title):
                result = self.run_script(title)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, CI_ERROR.format(title=title) + "\n")

    def test_commitizen_schema_pattern_is_the_same_rule(self):
        # A regex, not tomllib: tomllib needs Python 3.11 and the repo supports 3.10.
        found = re.search(r"^schema_pattern = '(.*)'$", (ROOT / ".cz.toml").read_text(), re.MULTILINE)
        self.assertIsNotNone(found, ".cz.toml has no schema_pattern line")
        self.assertEqual(found.group(1), pr_title.PATTERN)


if __name__ == "__main__":
    unittest.main()
