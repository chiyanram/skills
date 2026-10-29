import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT

PLUGIN = Path("plugins/rulebook")
SHIPPED = [Path("LICENSE"), PLUGIN / "README.md", PLUGIN / ".claude-plugin/icon.png"]


def validate(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["claude", "plugin", "validate", "--strict", "--profile", "directory", str(repo / PLUGIN)],
                          capture_output=True, text=True)


def copy_of_plugin(tmp: str) -> Path:
    repo = Path(tmp)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    shutil.copytree(ROOT / PLUGIN, repo / PLUGIN)
    shutil.copy(ROOT / "LICENSE", repo / "LICENSE")
    return repo


@unittest.skipUnless(shutil.which("claude"), "the Claude Code CLI is not installed; CI installs it")
class PluginValidateTest(unittest.TestCase):
    def test_should_pass_the_shipped_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = validate(copy_of_plugin(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_should_fail_when_a_shipped_file_is_missing(self):
        for missing in SHIPPED:
            with self.subTest(str(missing)), tempfile.TemporaryDirectory() as tmp:
                repo = copy_of_plugin(tmp)
                (repo / missing).unlink()
                result = validate(repo)
                self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
