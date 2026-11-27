import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, ROOT, run_check

SCRIPT = ROOT / "scripts" / "build_index.py"


class BuildIndexTest(unittest.TestCase):
    """`make index` runs build_index.py; check_index.py must pass on what it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, fixture: str) -> subprocess.CompletedProcess:
        shutil.copytree(FIXTURES / "index" / fixture, self.root)
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)

    def test_should_copy_the_plugin_index_into_the_readme_so_the_index_check_passes(self):
        result = self.build("agents-stale")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(run_check("index", self.root).returncode, 0)
        self.assertEqual((self.root / "README.md").read_text(), (FIXTURES / "index" / "good" / "README.md").read_text())

    def test_should_name_the_readme_when_it_has_no_block_for_the_plugin_index(self):
        result = self.build("agents-no-block")

        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md: no AGENTS.md block", result.stdout)


if __name__ == "__main__":
    unittest.main()
