"""Each check against its fixtures: the good ones must pass and the planted ones must fail."""
import unittest

from tests.support import FIXTURES, run_check

CASES = {
    "versions": (["good", "apart"], ["mismatch", "missing"]),
    "links": (["good"], ["broken", "broken-after-nested-fence"]),
    "sizes": (["good", "good-template", "rules-heading-ours"],
              ["root-too-long", "chain-over-32k", "rule-too-long", "rules-heading-variant", "no-rules-section"]),
    "plugin": (["good"], ["source-is-root", "root-is-a-plugin", "no-readme", "no-icon", "no-license"]),
    "index": (["good"], ["unlisted", "agents-stale", "agents-no-block"]),
    "provenance": (["good"], ["citation", "preference", "credit", "date", "evidence", "repo-ref", "neutral",
                              "fileline", "section", "url", "nested-fence"]),
    "glossary": (["good"], ["avoid-word", "avoid-word-in-crq"]),
    "comments": (["good", "good-at-baseline"], ["py-comment", "js-comment", "raised", "below-baseline"]),
    "settings_keys": (["good"], ["number-after-key", "number-before-key", "value-in-span", "wrapped-line"]),
    "routing": (["good"], ["no-cases", "too-few", "misrouted", "near-miss-wins", "unknown-owner", "collision"]),
    "eval_proof": (["good", "good-normal-unproven"],
                   ["core-no-baseline", "core-reference-not-approved", "core-baseline-not-approved", "core-no-planted",
                    "core-planted-failed", "stale-approved-baseline", "no-plugin", "unknown-tier"]),
}


class FixtureChecksTest(unittest.TestCase):
    def test_should_pass_each_good_fixture(self):
        for check, (good, _) in CASES.items():
            for fixture in good:
                with self.subTest(f"{check}/{fixture}"):
                    result = run_check(check, FIXTURES / check / fixture)
                    self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_fail_each_planted_fixture(self):
        for check, (_, bad) in CASES.items():
            for fixture in bad:
                with self.subTest(f"{check}/{fixture}"):
                    result = run_check(check, FIXTURES / check / fixture)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertTrue(result.stdout.strip(), "a failing check names the problem")


if __name__ == "__main__":
    unittest.main()
