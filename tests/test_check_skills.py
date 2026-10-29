import tempfile
import unittest
from pathlib import Path

from tests.support import run_check

DESCRIPTION = "Use when testing the skill check."

# Written to a temp dir, never committed: `npx skills add` walks the repo for SKILL.md files.
CASES = {
    "good": f"---\nname: demo\ndescription: {DESCRIPTION}\n---\n# Demo\n",
    "good-folded": f"---\nname: demo\ndescription: >\n  {DESCRIPTION}\n  Second line.\n---\n# Demo\n",
    "missing-name": f"---\ndescription: {DESCRIPTION}\n---\n# Demo\n",
    "missing-description": "---\nname: demo\n---\n# Demo\n",
    "name-not-folder": f"---\nname: other\ndescription: {DESCRIPTION}\n---\n# Demo\n",
    "description-1025-chars": f"---\nname: demo\ndescription: {'x' * 1025}\n---\n# Demo\n",
    "no-frontmatter": "# Demo\n",
}


def skill_tree(body: str) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    skill = Path(tmp.name) / "skills" / "demo" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(body)
    return tmp


class CheckSkillsTest(unittest.TestCase):
    def test_should_pass_a_valid_skill(self):
        for case in ("good", "good-folded"):
            with self.subTest(case), skill_tree(CASES[case]) as root:
                result = run_check("skills", Path(root))
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_fail_each_bad_skill(self):
        for case in ("missing-name", "missing-description", "name-not-folder",
                     "description-1025-chars", "no-frontmatter"):
            with self.subTest(case), skill_tree(CASES[case]) as root:
                result = run_check("skills", Path(root))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("SKILL.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
