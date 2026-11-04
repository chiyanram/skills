import unittest

from tests.support import FIXTURES, run_check

# check name -> (fixtures that must pass, planted fixtures that must fail)
CASES = {
    "versions": (["good"], ["mismatch", "missing"]),
    "links": (["good", "archived"], ["broken", "broken-after-nested-fence"]),
    "sizes": (["good", "good-template", "rules-heading-ours"],
              ["root-too-long", "chain-over-32k", "rule-too-long", "rules-heading-variant", "no-rules-section"]),
    "plugin": (["good"], ["source-is-root", "root-is-a-plugin", "no-readme", "no-icon", "no-license"]),
    "index": (["good"], ["unlisted", "stale", "no-block", "no-read-it"]),
    "routers": (["good"], ["unlisted", "no-router"]),
    "provenance": (["good"], ["citation", "preference", "credit", "date", "evidence", "agent-factory", "neutral",
                              "fileline", "section", "url", "nested-fence"]),
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
