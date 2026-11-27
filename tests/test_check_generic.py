import tempfile
import unittest
from pathlib import Path

from tests.support import run_check


class CheckGenericTest(unittest.TestCase):
    def repo(self, tmp: str, text: str) -> Path:
        skill = Path(tmp) / "plugins" / "rulebook" / "skills" / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: demo\ndescription: Does one thing.\n---\n\n# Demo\n")
        (skill / "notes.md").write_text(text)
        return Path(tmp)

    def test_passes_a_skill_that_names_only_the_person(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_check("generic", self.repo(tmp, "The person approves the spec.\n"))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_fails_a_notes_file_that_names_an_engine_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_check("generic", self.repo(tmp, "Intro.\nThe coordinator approves the spec.\n"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("notes.md:2: names \"coordinator\"", result.stdout)


if __name__ == "__main__":
    unittest.main()
