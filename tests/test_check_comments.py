"""check_comments.py --shrink writes the lower counts and never raises one."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, ROOT


class ShrinkTest(unittest.TestCase):
    def shrink(self, fixture: str) -> tuple[subprocess.CompletedProcess, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / fixture
            shutil.copytree(FIXTURES / "comments" / fixture, target)
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_comments.py"), "--shrink",
                                     str(target)], capture_output=True, text=True)
            return result, json.loads((target / "scripts" / "comment-baseline.json").read_text())

    def test_should_write_the_lower_count_after_a_deletion(self):
        result, baseline = self.shrink("below-baseline")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(baseline, {})

    def test_should_not_raise_a_count(self):
        result, baseline = self.shrink("raised")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(baseline, {"scripts/demo.py": 1})


if __name__ == "__main__":
    unittest.main()
