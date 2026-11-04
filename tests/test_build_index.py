import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import FIXTURES, ROOT, run_check

SCRIPT = ROOT / "scripts" / "build_index.py"
ROUTER = Path("plugins/p/skills/demo/SKILL.md")


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

    def test_should_rebuild_a_stale_router_so_the_index_check_passes(self):
        result = self.build("stale")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(run_check("index", self.root).returncode, 0)
        self.assertEqual((self.root / ROUTER).read_text(), (FIXTURES / "index" / "good" / ROUTER).read_text())

    def test_should_fold_consecutive_rule_ids_and_keep_a_suffixed_one_apart(self):
        reference = self.root / "plugins/p/skills/demo/references/alpha.md"
        self.build("good")
        reference.write_text("# Alpha\n\nRead it when you alpha.\n\n## Rules\n\n"
                             + "".join(f"- **{rule}** — Do it, because.\n" for rule in ["K3", "K1", "K2b", "K2", "K5"]))

        subprocess.run([sys.executable, str(SCRIPT), str(self.root)], check=True)

        self.assertIn("| [alpha](references/alpha.md) | K1–K2, K2b, K3, K5 | when you alpha |",
                      (self.root / ROUTER).read_text())

    def test_should_leave_the_router_unchanged_when_a_reference_has_no_read_it_sentence(self):
        result = self.build("no-read-it")

        self.assertEqual(result.returncode, 1)
        self.assertIn("beta.md", result.stdout)
        self.assertEqual((self.root / ROUTER).read_text(),
                         (FIXTURES / "index" / "no-read-it" / ROUTER).read_text())


if __name__ == "__main__":
    unittest.main()
