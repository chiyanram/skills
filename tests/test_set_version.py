import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, ROOT

SCRIPT = ROOT / "scripts" / "set_version.py"


class SetVersionTest(unittest.TestCase):
    """semantic-release calls set_version.py in its prepare step; check_versions.py must pass on what it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(FIXTURES / "versions" / "good", self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, version: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), version, str(self.root)], capture_output=True, text=True)

    def versions(self) -> set[str]:
        market = json.loads((self.root / ".claude-plugin" / "marketplace.json").read_text())
        found = set()
        for entry in market["plugins"]:
            found.add(entry["version"])
            found.add(json.loads((self.root / entry["source"] / ".claude-plugin" / "plugin.json").read_text())["version"])
        return found

    def test_should_write_the_version_to_every_manifest(self):
        result = self.run_script("1.2.3")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.versions(), {"1.2.3"})
        check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_versions.py"), str(self.root)],
                               capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_should_refuse_a_version_that_is_not_semver(self):
        result = self.run_script("v1.2")
        self.assertEqual(result.returncode, 1)
        self.assertNotEqual(self.versions(), {"v1.2"})


if __name__ == "__main__":
    unittest.main()
