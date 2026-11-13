import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT, run_check

sys.path.insert(0, str(ROOT / "scripts"))
from lanes_render import cell, diagram, files, gates, lanes_table  # noqa: E402

SCRIPT = ROOT / "scripts" / "build_index.py"
CRQ = ROOT / "plugins" / "rulebook" / "skills" / "crq"
MARKETPLACE = {"name": "m", "owner": {"name": "o"}, "plugins": [{"name": "p", "source": "./plugins/p"}]}
DIAGRAM = "<!-- lanes-diagram: built by make index from process/lanes-v2.json; do not edit by hand -->"
TABLE = "<!-- lanes-table: built by make index from process/lanes-v2.json; do not edit by hand -->"
END_TABLE = "<!-- /lanes-table -->"
DOC = {
    "caps": {"gate_red": 2},
    "conditions": {"design-needed": "more than one module changes"},
    "phases": [
        {"id": "intake", "actor": "coordinator", "outcomes": {"done": "next", "asked": "human, then same"}},
        {"id": "approval", "actor": "human", "outcomes": {"approved": "next", "changes": "intake"}},
        {"id": "gate", "actor": "engine", "outcomes": {"green": "next", "red": {"to": "intake", "counts": "gate_red"}}},
        {"id": "timeline-record", "actor": "engine", "outcomes": {"done": "end"}},
    ],
    "lanes": [{"lane": "tiny", "phases": ["intake", {"phase": "gate", "when": "design-needed"}, "timeline-record"]},
              {"lane": "bug", "phases": [{"phase": "intake", "when": "design-needed"}, "approval", "gate",
                                         "timeline-record"]}],
}


class LanesRenderTest(unittest.TestCase):
    """`make index` builds the crq diagram and lanes table from lanes-v2.json; check_index fails when they differ."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.skill = self.root / "plugins" / "p" / "skills" / "crq"
        shutil.copytree(CRQ, self.skill)
        (self.root / ".claude-plugin").mkdir(parents=True)
        (self.root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(MARKETPLACE))
        (self.root / "plugins" / "p" / "README.md").write_text("# p\n\n- [crq](skills/crq/SKILL.md)\n")

    def tearDown(self):
        self.tmp.cleanup()

    def build(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)

    def snapshot(self) -> dict[Path, str]:
        return {path: path.read_text() for path in sorted(self.skill.rglob("*.md"))}

    def edit(self, relative: str, old: str, new: str) -> Path:
        path = self.skill / relative
        path.write_text(path.read_text().replace(old, new, 1))
        return path

    def assert_fails_naming(self, name: str):
        result = run_check("index", self.root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(name, result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_should_build_blocks_the_index_check_passes_and_leave_no_diff_on_a_second_build(self):
        self.assertEqual(self.build().returncode, 0)
        first = self.snapshot()

        self.assertEqual(self.build().returncode, 0)

        self.assertEqual(self.snapshot(), first)
        self.assertEqual(run_check("index", self.root).returncode, 0)
        self.assertIn("HUMAN approval", (self.skill / "SKILL.md").read_text())
        self.assertIn("| feature | intake → research", (self.skill / "references" / "lanes.md").read_text())

    def test_should_rewrite_a_stale_block_so_the_index_check_passes(self):
        self.build()
        lanes = self.skill / "process" / "lanes-v2.json"
        lanes.write_text(lanes.read_text().replace('"gate_red": 2', '"gate_red": 4'))

        self.assertEqual(self.build().returncode, 0)

        self.assertIn("gate           red        ─▶ build   cap gate_red = 4", (self.skill / "SKILL.md").read_text())
        self.assertEqual(run_check("index", self.root).returncode, 0)

    def test_should_fail_a_hand_edited_block_naming_the_file(self):
        self.build()
        self.edit("references/lanes.md", "| tiny | intake", "| tiny | start")

        self.assert_fails_naming("references/lanes.md: lanes block is stale")

    def test_should_fail_a_lanes_v2_change_without_make_index(self):
        self.build()
        lanes = self.skill / "process" / "lanes-v2.json"
        lanes.write_text(lanes.read_text().replace('"gate_red": 2', '"gate_red": 4'))

        self.assert_fails_naming("SKILL.md: lanes block is stale")

    def test_should_fail_a_missing_block(self):
        self.edit("SKILL.md", DIAGRAM, "")

        self.assert_fails_naming("no `lanes-diagram` block")

    def test_should_fail_a_block_twice_in_one_file(self):
        self.edit("SKILL.md", DIAGRAM, f"{DIAGRAM}\n{DIAGRAM}")

        self.assert_fails_naming("SKILL.md: the `lanes-diagram` block needs one START marker")

    def test_should_fail_a_block_in_two_files(self):
        (self.skill / "references" / "extra.md").write_text(f"# Extra\n\n{TABLE}\n<!-- /lanes-table -->\n")

        self.assert_fails_naming("extra.md: holds a `lanes-table` block, which is in 2 files")

    def test_should_fail_a_start_marker_with_no_end_marker_after_it(self):
        self.edit("references/lanes.md", "<!-- /lanes-table -->", "")

        self.assert_fails_naming("lanes.md: the `lanes-table` block needs one START marker and one END marker")

    def test_should_fail_an_end_marker_above_its_start_marker(self):
        self.edit("references/lanes.md", END_TABLE, "")
        self.edit("references/lanes.md", TABLE, f"{END_TABLE}\n{TABLE}")

        self.assert_fails_naming("lanes.md: the `lanes-table` block needs one START marker and one END marker")

    def test_should_report_one_line_and_leave_the_blocks_when_lanes_v2_is_not_json(self):
        (self.skill / "process" / "lanes-v2.json").write_text("{")
        before = self.snapshot()

        result = self.build()

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip().splitlines(), [f"{self.skill}/process/lanes-v2.json: not valid; "
                                                              "run check_process.py"])
        self.assertEqual(self.snapshot(), before)
        self.assert_fails_naming("lanes-v2.json: not valid")

    def test_should_report_the_schema_line_when_the_lanes_v2_schema_is_missing(self):
        (self.skill / "process" / "schema" / "lanes-v2.schema.json").unlink()
        before = self.snapshot()

        result = self.build()

        self.assertEqual(result.returncode, 1)
        self.assertIn("lanes-v2.schema.json: missing, or not JSON", result.stdout)
        self.assertEqual(self.snapshot(), before)
        self.assert_fails_naming("lanes-v2.schema.json: missing, or not JSON")

    def test_should_report_one_line_when_a_schema_valid_doc_breaks_a_graph_rule(self):
        lanes = self.skill / "process" / "lanes-v2.json"
        lanes.write_text(lanes.read_text().replace('"phases": ["intake", "build"', '"phases": ["intake", "nowhere"'))
        before = self.snapshot()

        result = self.build()

        self.assertEqual(result.returncode, 1)
        self.assertIn("lanes-v2.json: not valid; run check_process.py", result.stdout)
        self.assertEqual(self.snapshot(), before)
        self.assert_fails_naming("lanes-v2.json: not valid")

    def test_should_change_nothing_for_a_skill_without_lanes_v2(self):
        (self.skill / "process" / "lanes-v2.json").unlink()

        self.assertEqual(files(self.skill), ({}, []))


class RenderRowsTest(unittest.TestCase):
    def test_should_mark_a_human_phase(self):
        self.assertEqual(diagram(DOC)[1], "intake ─▶ HUMAN approval ─▶ gate ─▶ timeline-record")

    def test_should_show_a_counted_edge_with_its_cap_and_skip_next_end_and_human_then_same(self):
        self.assertEqual(diagram(DOC)[3:-1], ["approval  changes  ─▶ intake",
                                              "gate      red      ─▶ intake  cap gate_red = 2"])

    def test_should_show_a_when_entry_with_its_condition(self):
        self.assertEqual(cell({"phase": "design", "when": "design-needed"}), "design (when design-needed)")
        self.assertEqual(lanes_table(DOC)[-2:], ["", "design-needed: more than one module changes"])

    def test_should_show_each_lane_in_file_order_with_its_when_cells(self):
        self.assertEqual(lanes_table(DOC)[2:4], [
            "| tiny | intake → gate (when design-needed) → timeline-record | — |",
            "| bug | intake (when design-needed) → approval → gate → timeline-record | approval |"])

    def test_should_list_a_condition_once_when_two_lanes_use_it(self):
        self.assertEqual([line for line in lanes_table(DOC) if line.startswith("design-needed:")],
                         ["design-needed: more than one module changes"])

    def test_should_list_the_lanes_human_phases_as_its_gates(self):
        actors = {phase["id"]: phase["actor"] for phase in DOC["phases"]}

        self.assertEqual(gates(DOC["lanes"][1], actors), "approval")
        self.assertEqual(gates(DOC["lanes"][0], actors), "—")

    def test_should_wrap_the_phase_order_at_100_columns(self):
        doc = {**DOC, "phases": [{"id": f"phase-{n:02}", "actor": "engine", "outcomes": {"done": "next"}}
                                 for n in range(12)]}

        flow = diagram(doc)[1:3]

        self.assertTrue(all(len(line) <= 100 for line in flow))
        self.assertTrue(flow[1].startswith("   ─▶ "))


if __name__ == "__main__":
    unittest.main()
