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
    """semantic-release calls set_version.py once per plugin; check_versions.py must pass on what it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(FIXTURES / "versions" / "apart", self.root)
        self.market = self.root / ".claude-plugin" / "marketplace.json"
        self.before = self.market.read_text()

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, version: str, plugin: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), version, str(self.root), "--plugin", plugin],
                              capture_output=True, text=True)

    def versions(self) -> dict[str, tuple[str, str]]:
        found = {}
        for entry in json.loads(self.market.read_text())["plugins"]:
            manifest = json.loads((self.root / entry["source"] / ".claude-plugin" / "plugin.json").read_text())
            found[entry["name"]] = (entry["version"], manifest["version"])
        return found

    def test_should_write_the_version_to_one_plugins_manifests_only(self):
        result = self.run_script("1.2.3", "p")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.versions(), {"p": ("1.2.3", "1.2.3"), "q": ("0.1.0", "0.1.0")})
        check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_versions.py"), str(self.root)],
                               capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_should_refuse_a_version_that_is_not_semver(self):
        result = self.run_script("v1.2", "p")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.market.read_text(), self.before)

    def test_should_refuse_a_plugin_the_marketplace_does_not_list(self):
        result = self.run_script("1.2.3", "r")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no plugin `r`", result.stdout)
        self.assertEqual(self.market.read_text(), self.before)


if __name__ == "__main__":
    unittest.main()
