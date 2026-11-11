import json
import sys
import unittest

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from schema_lite import unknown_keywords, validate  # noqa: E402

SCHEMA_DIR = ROOT / "plugins" / "rulebook" / "skills" / "crq" / "process" / "schema"
FINDING = {"id": "F1", "lens": "standards", "axis": "standards", "kind": "rule", "file": "src/a.py", "line": 12,
           "rule": "CR1", "category": "style", "severity": "blocker", "grade": "walked", "evidence": "a.py:12 reads x",
           "finding": "the name hides the unit", "fix": "rename to timeout_ms"}


class SchemaLiteTest(unittest.TestCase):
    def setUp(self):
        self.finding = json.loads((SCHEMA_DIR / "finding-v1.schema.json").read_text())

    def test_should_run_every_keyword_the_shipped_schemas_use(self):
        for path in SCHEMA_DIR.glob("*.schema.json"):
            with self.subTest(path.name):
                self.assertEqual(unknown_keywords(json.loads(path.read_text())), [])

    def test_should_accept_a_finding(self):
        self.assertEqual(validate(FINDING, self.finding), [])
        self.assertEqual(validate({**FINDING, "kind": "logic", "rule": None, "line": "40-44"}, self.finding), [])
        self.assertEqual(validate({**FINDING, "line": "12"}, self.finding), [])

    def test_should_fail_a_broken_finding(self):
        cases = {"bad-grade": {**FINDING, "grade": "guessed"}, "bad-axis": {**FINDING, "axis": "style"},
                 "no-evidence": {k: v for k, v in FINDING.items() if k != "evidence"},
                 "line-not-number-or-text": {**FINDING, "line": [12]}, "empty-finding": {**FINDING, "finding": ""},
                 "line-not-a-cite": {**FINDING, "line": "near the top"}, "line-open-range": {**FINDING, "line": "40-"},
                 "extra-field": {**FINDING, "confidence": "high"},
                 "free-text-severity": {**FINDING, "severity": "Act on"},
                 "unknown-category": {**FINDING, "category": "naming"}}
        for case, finding in cases.items():
            with self.subTest(case):
                self.assertTrue(validate(finding, self.finding))

    def test_should_refuse_a_keyword_it_does_not_run(self):
        self.assertEqual(len(unknown_keywords({"type": "string", "format": "email"})), 1)


if __name__ == "__main__":
    unittest.main()
