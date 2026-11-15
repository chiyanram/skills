import json
import os
import subprocess
import unittest

from tests.support import ROOT

PLUGIN = ROOT / "plugins" / "rulebook"


class IndexHookTest(unittest.TestCase):
    """The rulebook SessionStart hook prints hooks/index.txt only when the project sets RULEBOOK_INDEX=1."""

    def run_hook(self, **env: str) -> subprocess.CompletedProcess:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        base = {key: value for key, value in os.environ.items() if key != "RULEBOOK_INDEX"}
        return subprocess.run(["sh", "-c", command], capture_output=True, text=True,
                              env={**base, "CLAUDE_PLUGIN_ROOT": str(PLUGIN), **env})

    def test_should_print_the_index_when_the_project_opts_in(self):
        result = self.run_hook(RULEBOOK_INDEX="1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (PLUGIN / "hooks" / "index.txt").read_text())

    def test_should_print_nothing_and_succeed_by_default(self):
        result = self.run_hook()

        self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
