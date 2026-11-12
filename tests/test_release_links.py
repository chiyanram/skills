import json
import subprocess
import unittest

from tests.support import ROOT

CONTEXT = {"host": "https://github.com", "owner": "chiyanram", "repository": "skills"}
SKILLS = "https://github.com/chiyanram/skills/issues"
OTHER = "https://github.com/chiyanram/other/issues"

# subject as the conventionalcommits preset renders it -> subject after scripts/release_links.mjs
CASES = {
    "bare repo#N, the 0.2.0 bug": (
        f"boundaries rule file (other[#31]({SKILLS}/31), 1 of 11) ([#113]({SKILLS}/113))",
        f"boundaries rule file ([chiyanram/other#31]({OTHER}/31), 1 of 11) ([#113]({SKILLS}/113))"),
    "owner/repo#N": (
        f"strategy (other-org/tool[#7]({SKILLS}/7))",
        "strategy ([other-org/tool#7](https://github.com/other-org/tool/issues/7))"),
    "this repo's own #N stays": (
        f"spock rule file ([#120]({SKILLS}/120))",
        f"spock rule file ([#120]({SKILLS}/120))"),
    "no reference": ("plain subject", "plain subject"),
}

SCRIPT = """
import { crossRepoLinks } from './scripts/release_links.mjs'
const { cases, context } = JSON.parse(process.argv[1])
console.log(JSON.stringify(Object.fromEntries(Object.entries(cases).map(([k, [given]]) => [k, crossRepoLinks(given, context)]))))
"""


class ReleaseLinksTest(unittest.TestCase):
    """The preset links every #N in a subject to this repo; release_links.mjs points repo#N at its own repo."""

    def test_should_link_each_reference_to_its_own_repo(self):
        result = subprocess.run(["node", "--input-type=module", "-e", SCRIPT, json.dumps({"cases": CASES, "context": CONTEXT})],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        got = json.loads(result.stdout)
        for name, (_, expected) in CASES.items():
            with self.subTest(name):
                self.assertEqual(got[name], expected)


if __name__ == "__main__":
    unittest.main()
