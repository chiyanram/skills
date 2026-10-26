import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT


def groups(file: str, rule_id: str) -> str:
    return json.dumps([{"key": "k", "name": "n", "file": file, "ids": [rule_id]}])


# builder -> (arguments, page it writes, text the page must carry)
BUILDERS = {
    "build.py": ([groups("47-good-rewrites.md", "S2")], "rule-review.html", '"id": "S2"'),
    "build-planning.py": ([groups("42-planning-good-bad.md", "SR2")], "planning-good-bad.html", '"id": "SR2"'),
    "build-good-rewrites.py": ([groups("47-good-rewrites.md", "C1")], "good-rewrites.html", '"id": "C1"'),
    "build-g9b.py": ([], "g9b-rules.html", "<title>Code and Obs Rules</title>"),
    "build-g9c-mg.py": ([], "g9c-migration-rules.html", "<title>Migration Rules</title>"),
    "build-spring.py": ([], "spring-rules.html", "<title>Spring Rules Review</title>"),
    "build-neutral.py": ([], "neutral-pairs.html", '"key": "strategy"'),
    "build-reasons.py": ([], "rule-reasons.html", '"excluded": ['),
}


class BuildersTest(unittest.TestCase):
    """Each builder runs from a copy of the repo and writes into that copy, so it reads no fixed path."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.copy = Path(cls.tmp.name)
        for folder in ("research", "review"):
            shutil.copytree(ROOT / folder, cls.copy / folder)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_should_build_each_page_inside_the_repo_it_runs_from(self):
        for builder, (args, page, marker) in BUILDERS.items():
            with self.subTest(builder):
                output = self.copy / "review" / page
                output.unlink(missing_ok=True)
                result = subprocess.run([sys.executable, str(self.copy / "review" / builder), *args],
                                        capture_output=True, text=True, cwd=self.copy)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(marker, output.read_text())


if __name__ == "__main__":
    unittest.main()
