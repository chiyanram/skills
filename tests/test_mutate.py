import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from mutate import schema_mutants  # noqa: E402

SCRIPT = ROOT / "scripts" / "mutate.py"
SCHEMA = '{"required": ["a"], "properties": {"a": {"minLength": 1}, "enum": {"const": 1}}}'
CHECK = """import json, sys
doc = json.load(open("tiny.schema.json"))
assert doc.get("required") == ["a"]
assert doc["properties"]["enum"].get("const") == 1
if "all" in sys.argv:
    assert doc["properties"]["a"].get("minLength") == 1
"""
MODULE = """def clamp(x):
    if x < 0:
        return 0
    if x > 10:
        return 10
    return x
"""
MODULE_CHECK = """import sys
from tiny import clamp
assert clamp(-1) == 0
if "all" in sys.argv:
    assert clamp(5) == 5
"""


EVERY_KEYWORD = {
    "additionalProperties": False, "required": ["a"], "minItems": 1, "minLength": 1, "const": 1, "enum": [1],
    "pattern": "a", "items": {}, "prefixItems": [],
    "properties": {"required": {"minLength": 1}}, "patternProperties": {"enum": {}}, "$defs": {"pattern": {}},
    "definitions": {"const": {}},
}


class SchemaMutantsTest(unittest.TestCase):
    """schema_mutants drops each AC-1 keyword once, and reads a key under a NAMED container as a name."""

    def test_each_keyword_is_dropped_once_and_names_are_not(self):
        self.assertEqual(
            ["additionalProperties", "required", "minItems", "minLength", "const", "enum", "pattern", "items",
             "prefixItems", "properties/required/minLength"],
            [path for path, _ in schema_mutants(EVERY_KEYWORD)])


class MutateTest(unittest.TestCase):
    """mutate.py names each mutant a test command does not kill, and leaves the file as it found it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write(self, name: str, text: str) -> Path:
        path = self.dir / name
        path.write_text(text)
        return path

    def mutate(self, file: Path, command: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), str(file), command], cwd=self.dir, capture_output=True,
                              text=True)

    def test_a_schema_keyword_the_test_does_not_check_survives(self):
        schema = self.write("tiny.schema.json", SCHEMA)
        self.write("check.py", CHECK)
        result = self.mutate(schema, f"{sys.executable} check.py")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual(["survivor: properties/a/minLength", "2/3 killed"], result.stdout.splitlines())
        self.assertEqual(SCHEMA, schema.read_text())

    def test_no_schema_keyword_survives_a_test_that_checks_each(self):
        schema = self.write("tiny.schema.json", SCHEMA)
        self.write("check.py", CHECK)
        result = self.mutate(schema, f"{sys.executable} check.py all")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["3/3 killed"], result.stdout.splitlines())
        self.assertEqual(SCHEMA, schema.read_text())

    def test_an_if_guard_the_test_does_not_check_survives(self):
        module = self.write("tiny.py", MODULE)
        self.write("check.py", MODULE_CHECK)
        result = self.mutate(module, f"{sys.executable} check.py")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual(["survivor: line 4", "1/2 killed"], result.stdout.splitlines())
        self.assertEqual(MODULE, module.read_text())

    def test_no_if_guard_survives_a_test_that_checks_each(self):
        module = self.write("tiny.py", MODULE)
        self.write("check.py", MODULE_CHECK)
        result = self.mutate(module, f"{sys.executable} check.py all")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["2/2 killed"], result.stdout.splitlines())
        self.assertEqual(MODULE, module.read_text())

    def test_a_test_command_that_fails_on_the_unmutated_file_stops_the_run(self):
        schema = self.write("tiny.schema.json", SCHEMA)
        result = self.mutate(schema, "false")
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual("", result.stdout)
        self.assertEqual(["mutate: baseline is red: 'false' fails on the unmutated file"], result.stderr.splitlines())
        self.assertEqual(SCHEMA, schema.read_text())

    def test_a_stopped_run_restores_the_file(self):
        for stop in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=stop.name):
                schema = self.write("tiny.schema.json", SCHEMA)
                started = self.dir / "started"
                started.unlink(missing_ok=True)
                command = "grep -q required tiny.schema.json || (touch started && sleep 30)"
                run = subprocess.Popen([sys.executable, str(SCRIPT), str(schema), command], cwd=self.dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                deadline = time.monotonic() + 10
                while not started.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertNotEqual(SCHEMA, schema.read_text())
                run.send_signal(stop)
                run.communicate(timeout=10)
                self.assertEqual(128 + stop, run.returncode)
                self.assertEqual(SCHEMA, schema.read_text())


if __name__ == "__main__":
    unittest.main()
