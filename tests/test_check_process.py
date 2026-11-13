import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT, run_check

sys.path.insert(0, str(ROOT / "scripts"))
from schema_lite import validate  # noqa: E402

SCHEMA_DIR = ROOT / "plugins" / "rulebook" / "skills" / "crq" / "process" / "schema"
SCHEMAS = {f"skills/crq/process/schema/{f.name}": f.read_text() for f in SCHEMA_DIR.glob("*.schema.json")}

MARKETPLACE = {"name": "m", "owner": {"name": "o"}, "plugins": [{"name": "p", "source": "./plugins/p"}]}
REFERENCE = "# Demo\n\nRead it when testing.\n\n## Rules\n\n- **DM1** — Do one thing, because two break.\n"
CARD = ("---\nrole: finder\nsteps: [code review]\ninput: the diff\nmust_not_see: the implementer's report\n"
        "hand_off: findings\ntools: [Read]\nenforced_guardrails: [read-only]\nrules: [DM1]\n---\n\n"
        "**The job.** Find.\n\n**Done when** every check was walked.\n\n1. Walk.\n\n**It's working if:**\n- it finds.\n")
LANE = {"starts_on": "START only", "design_review": False, "test_first": False, "lenses": "1", "retro": "record"}
LANES = {"lanes": [{"lane": "tiny", "approval": False, **LANE},
                   *({"lane": name, "approval": True, **LANE} for name in ("bug", "feature", "one-way door"))]}

PHASES_V2 = [
    {"id": "intake", "actor": "coordinator", "outcomes": {"done": "next", "asked": "human, then same"}},
    {"id": "approval", "actor": "human", "outcomes": {"approved": "next", "changes": {"to": "intake"}}},
    {"id": "build", "actor": "implementer", "report": "urn:rulebook:crq:report:1", "outcomes": {"done": "next"}},
    {"id": "gate", "actor": "engine", "outcomes": {"green": "next", "stuck": "human",
                                                    "red": {"to": "build", "counts": "gate_red"}}},
    {"id": "timeline-record", "actor": "engine", "outcomes": {"done": "end"}},
]
LANE_V2 = {"lens_cap": 3, "review_model": "standard", "effort": "medium"}
LANES_V2 = {
    "$schema": "urn:rulebook:crq:lanes:2",
    "caps": {"gate_red": 2},
    "conditions": {"design-needed": "more than one module changes"},
    "lane_raise": {"from": "any phase after intake", "to": "intake", "then": "approval again"},
    "skipped_target": "the nearest earlier phase the run took",
    "phases": PHASES_V2,
    "lanes": [{"lane": "tiny", **LANE_V2, "lens_cap": 1, "effort": "low",
               "phases": ["intake", "build", "gate", "timeline-record"]},
              {"lane": "bug", **LANE_V2, "phases": ["intake", "approval", {"phase": "build", "when": "design-needed"},
                                                    "gate", "timeline-record"]},
              {"lane": "feature", **LANE_V2, "phases": ["intake", "approval", "build", "gate", "timeline-record"]},
              {"lane": "one-way door", "lens_cap": "all", "review_model": "strongest", "effort": "high",
               "phases": ["intake", "approval", "build", "gate", "timeline-record"]}],
}
V2 = "skills/crq/process/lanes-v2.json"


def lanes_v2(change) -> str:
    """The valid lanes-v2 document, changed in a copy by `change(doc)`."""
    doc = json.loads(json.dumps(LANES_V2))
    change(doc)
    return json.dumps(doc)


REVIEW = {"baseline": [{"skill": "crq", "reference": "demo"}]}

# Written to a temp dir, never committed: a planted card under plugins/ would be found by the other checks.
# Each planted case: (a path under the plugin root, its new text or None to delete it, and optionally a substring
# the failure must print).
PLANTED = {
    "role-not-file-name": ("skills/crq/process/roles/finder.md", CARD.replace("role: finder", "role: reviewer")),
    "missing-field": ("skills/crq/process/roles/finder.md", CARD.replace("must_not_see: the implementer's report\n", "")),
    "extra-field": ("skills/crq/process/roles/finder.md", CARD.replace("rules:", "persona: a senior\nrules:")),
    "next-dropped": ("skills/crq/process/roles/finder.md", CARD.replace("rules:", "next: verify pass\nrules:")),
    "unknown-rule": ("skills/crq/process/roles/finder.md", CARD.replace("[DM1]", "[DM1, DM9]")),
    "no-done-when": ("skills/crq/process/roles/finder.md", CARD.replace("**Done when**", "Finish when")),
    "no-steps": ("skills/crq/process/roles/finder.md", CARD.replace("1. Walk.", "Walk.")),
    "two-scenarios": ("evals/finder/c3", None),
    "no-grader": ("evals/finder/c2/graders/g.md", None),
    "lane-drops-approval": ("skills/crq/process/lanes.json",
                            json.dumps(LANES).replace('"feature", "approval": true', '"feature", "approval": false')),
    "lane-missing": ("skills/crq/process/lanes.json", json.dumps({"lanes": LANES["lanes"][:3]})),
    "lane-out-of-order": ("skills/crq/process/lanes.json",
                          json.dumps({"lanes": [LANES["lanes"][0], LANES["lanes"][2], LANES["lanes"][1],
                                                LANES["lanes"][3]]})),
    "lane-approval-not-boolean": ("skills/crq/process/lanes.json",
                                  json.dumps(LANES).replace('"bug", "approval": true', '"bug", "approval": "yes"')),
    "lane-field-missing": ("skills/crq/process/lanes.json", json.dumps(LANES).replace('"lenses": "1", ', "", 1)),
    "unknown-guardrail": ("skills/crq/process/roles/finder.md", CARD.replace("[read-only]", "[read-only, no-sudo]")),
    "empty-field": ("skills/crq/process/roles/finder.md", CARD.replace("input: the diff", "input:")),
    "no-card-schema": ("skills/crq/process/schema/card-v1.schema.json", None),
    "no-finding-schema": ("skills/crq/process/schema/finding-v1.schema.json", None),
    "no-report-schema": ("skills/crq/process/schema/report-v1.schema.json", None, "report-v1.schema.json: missing"),
    "card-unknown-id": ("skills/crq/process/roles/finder.md",
                        CARD.replace("hand_off: findings", "hand_off: findings (urn:rulebook:crq:finding:9)"),
                        "finder.md: cites urn:rulebook:crq:finding:9, which no schema in process/schema/ declares"),
    "schema-unknown-keyword": ("skills/crq/process/schema/lanes-v1.schema.json",
                               SCHEMAS["skills/crq/process/schema/lanes-v1.schema.json"].replace(
                                   '"minItems": 4', '"maxItems": 4, "minItems": 4')),
    "no-glossary": ("skills/crq/process/glossary.md", None, "process: no glossary.md"),
    "no-review": ("skills/crq/process/review.json", None, "process: no review.json"),
    "baseline-empty": ("skills/crq/process/review.json", json.dumps({"baseline": []})),
    "baseline-unshipped": ("skills/crq/process/review.json",
                           json.dumps({"baseline": [{"skill": "crq", "reference": "missing"}]})),
    "baseline-twice": ("skills/crq/process/review.json", json.dumps({"baseline": REVIEW["baseline"] * 2})),
    "baseline-extra-field": ("skills/crq/process/review.json",
                             json.dumps({"baseline": [{"skill": "crq", "reference": "demo", "why": "x"}]})),
    # lanes-v2: (path, new text, a substring the failure must print).
    "v2-missing": (V2, None, "process: no lanes-v2.json"),
    "v2-not-json": (V2, "{", "lanes-v2.json: not JSON"),
    "v2-no-schema": ("skills/crq/process/schema/lanes-v2.schema.json", None, "lanes-v2.schema.json: missing"),
    "v2-schema-unknown-keyword": ("skills/crq/process/schema/lanes-v2.schema.json",
                                  SCHEMAS["skills/crq/process/schema/lanes-v2.schema.json"].replace(
                                      '"minItems": 4', '"maxItems": 4, "minItems": 4'), "`maxItems`"),
    "v2-lane-missing": (V2, lanes_v2(lambda d: d["lanes"].pop()), "lanes: has 3 items, needs at least 4"),
    "v2-lane-extra": (V2, lanes_v2(lambda d: d["lanes"].append(d["lanes"][3])), "lanes[4]: not allowed"),
    "v2-lane-out-of-order": (V2, lanes_v2(lambda d: d["lanes"].insert(1, d["lanes"].pop(2))),
                             "lanes[1].lane: 'feature' is not 'bug'"),
    "v2-lens-cap-missing": (V2, lanes_v2(lambda d: d["lanes"][1].pop("lens_cap")), "lanes[1]: `lens_cap` is missing"),
    "v2-lens-cap-word": (V2, lanes_v2(lambda d: d["lanes"][1].update(lens_cap="many")), "lanes[1].lens_cap"),
    "v2-review-model-missing": (V2, lanes_v2(lambda d: d["lanes"][2].pop("review_model")),
                                "lanes[2]: `review_model` is missing"),
    "v2-review-model-bad": (V2, lanes_v2(lambda d: d["lanes"][2].update(review_model="best")),
                            "lanes[2].review_model: 'best'"),
    "v2-effort-missing": (V2, lanes_v2(lambda d: d["lanes"][3].pop("effort")), "lanes[3]: `effort` is missing"),
    "v2-effort-bad": (V2, lanes_v2(lambda d: d["lanes"][3].update(effort="max")), "lanes[3].effort: 'max'"),
    "v2-unknown-id": (V2, lanes_v2(lambda d: d.update({"$schema": "urn:rulebook:crq:lanes:9"})),
                      "lanes-v2.json: cites urn:rulebook:crq:lanes:9, which no schema in process/schema/ declares"),
    "v2-unknown-id-graph-broken": (V2, lanes_v2(lambda d: (d.update({"$schema": "urn:rulebook:crq:lanes:9"}),
                                                           d["lanes"][0]["phases"].reverse())),
                                   "lanes-v2.json: cites urn:rulebook:crq:lanes:9"),
    "v2-extra-key": (V2, lanes_v2(lambda d: d.update(notes="x")), "the top level: `notes` is not a known field"),
    "v2-phase-extra-key": (V2, lanes_v2(lambda d: d["phases"][2].update(reports="x")),
                           "phases[2]: `reports` is not a known field"),
    "v2-when-extra-key": (V2, lanes_v2(lambda d: d["lanes"][1]["phases"][2].update(why="x")),
                          "lanes[1].phases[2]: `why` is not a known field"),
    "v2-lane-raise-extra-key": (V2, lanes_v2(lambda d: d["lane_raise"].update(by="x")),
                                "lane_raise: `by` is not a known field"),
    "v2-phase-id-pattern": (V2, lanes_v2(lambda d: d["phases"][2].update(id="Build_x")),
                            "phases[2].id: 'Build_x' does not match"),
    "v2-report-version": (V2, lanes_v2(lambda d: d["phases"][2].update(report="urn:rulebook:crq:report:2")),
                          "phases[2].report: 'urn:rulebook:crq:report:2' is not"),
    # lanes-v2 graph rules, run once the schema passes.
    "v2-lane-unknown-phase": (V2, lanes_v2(lambda d: d["lanes"][2]["phases"].insert(1, "triage")),
                              "lane `feature`: phase `triage` is not in the phase order"),
    "v2-lane-out-of-phase-order": (V2, lanes_v2(lambda d: d["lanes"][0]["phases"].reverse()),
                                   "lane `tiny`: phase `gate` comes after `timeline-record`"),
    "v2-lane-phase-repeated": (V2, lanes_v2(lambda d: d["lanes"][0]["phases"].insert(0, "intake")),
                               "lane `tiny`: phase `intake` appears twice"),
    "v2-lane-when-out-of-order": (V2, lanes_v2(lambda d: d["lanes"][1]["phases"].insert(
        0, d["lanes"][1]["phases"].pop(2))), "lane `bug`: phase `intake` comes after `build`"),
    "v2-phase-twice": (V2, lanes_v2(lambda d: d["phases"].insert(3, d["phases"][2])),
                       "phase `build`: appears 2 times"),
    "v2-no-outcomes": (V2, lanes_v2(lambda d: d["phases"][2].update(outcomes={})), "phase `build`: has no outcomes"),
    "v2-edge-number": (V2, lanes_v2(lambda d: d["phases"][2]["outcomes"].update(done=42)),
                       "phase `build`, outcome `done`: must be a string"),
    "v2-edge-no-to": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"].update(red={"counts": "gate_red"})),
                      "phase `gate`, outcome `red`: must be a string"),
    "v2-edge-to-number": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"].update(red={"to": 7})),
                          "phase `gate`, outcome `red`: must be a string"),
    "v2-edge-extra-key": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"].update(
        red={"to": "build", "count": "gate_red"})), "phase `gate`, outcome `red`: must be a string"),
    "v2-edge-counts-number": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"].update(
        red={"to": "build", "counts": 3})), "phase `gate`, outcome `red`: must be a string"),
    "v2-edge-target": (V2, lanes_v2(lambda d: d["phases"][1]["outcomes"].update(changes="design")),
                       "phase `approval`, outcome `changes`: points at `design`"),
    "v2-edge-object-target": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"]["red"].update(to="builds")),
                              "phase `gate`, outcome `red`: points at `builds`"),
    "v2-counts-uncapped": (V2, lanes_v2(lambda d: d["phases"][3]["outcomes"]["red"].update(counts="ready")),
                           "phase `gate`, outcome `red`: counts `ready`, which has no cap"),
    "v2-cap-zero": (V2, lanes_v2(lambda d: d["caps"].update(gate_red=0)), "cap `gate_red`: 0 is not an integer"),
    "v2-cap-text": (V2, lanes_v2(lambda d: d["caps"].update(gate_red="2")), "cap `gate_red`: '2' is not an integer"),
    "v2-cap-boolean": (V2, lanes_v2(lambda d: d["caps"].update(gate_red=True)), "cap `gate_red`: True is not"),
    "v2-when-unknown": (V2, lanes_v2(lambda d: d["lanes"][1]["phases"][2].update(when="big-change")),
                        "lane `bug`: phase `build` has when `big-change`, which names no condition"),
    "v2-condition-empty": (V2, lanes_v2(lambda d: d["conditions"].update({"design-needed": " "})),
                           "condition `design-needed`: its text is empty"),
    "v2-condition-number": (V2, lanes_v2(lambda d: d["conditions"].update({"design-needed": 3})),
                            "condition `design-needed`: is not text"),
    "v2-no-approval": (V2, lanes_v2(lambda d: d["lanes"][3]["phases"].remove("approval")),
                       "lane `one-way door`: no plain `approval` entry"),
    "v2-approval-with-when": (V2, lanes_v2(lambda d: d["lanes"][2]["phases"].__setitem__(
        1, {"phase": "approval", "when": "design-needed"})), "lane `feature`: no plain `approval` entry"),
    "v2-no-timeline-record": (V2, lanes_v2(lambda d: d["lanes"][2]["phases"].pop()),
                              "lane `feature`: does not end with a plain `timeline-record` entry"),
    "v2-timeline-record-with-when": (V2, lanes_v2(lambda d: d["lanes"][0]["phases"].__setitem__(
        3, {"phase": "timeline-record", "when": "design-needed"})),
        "lane `tiny`: does not end with a plain `timeline-record` entry"),
    "v2-actor-unknown": (V2, lanes_v2(lambda d: d["phases"][2].update(actor="builder")),
                         "phase `build`: actor `builder` is not a card role"),
    "v2-lens-cap-zero": (V2, lanes_v2(lambda d: d["lanes"][1].update(lens_cap=0)), "lane `bug`: lens_cap 0 is below 1"),
    "v2-lane-raise-target": (V2, lanes_v2(lambda d: d["lane_raise"].update(to="spec")),
                             "lane_raise: `to` names `spec`"),
}

ROW = {"criterion": "AC-1", "command": "make test", "result": "OK"}
QUESTION = {"question": "Which lane?", "choices": ["bug", "feature"], "recommended": 1}
DEVIATION = {"what": "renamed f to g", "why": "g is free", "file": "a.py", "line": "4-6"}
# Each report case: (the report, a substring of the first problem, or None when it is valid).
REPORTS = {
    "done": ({"status": "done", "evidence": [ROW]}, None),
    "done-deferred-deviations": ({"status": "done", "evidence": [ROW], "deferred": ["inline x"],
                                  "deviations": [DEVIATION, {**DEVIATION, "line": 4}]}, None),
    "asked": ({"status": "asked", "questions": [QUESTION, {**QUESTION, "choices": ["a", "b", "c", "d"]}]}, None),
    "blocked": ({"status": "blocked", "blocker": "the runner has no network"}, None),
    "unknown-status": ({"status": "stuck", "blocker": "x"}, "'stuck' is not one of"),
    "done-no-evidence": ({"status": "done"}, "`evidence` is missing"),
    "done-empty-evidence": ({"status": "done", "evidence": []}, "evidence: has 0 items"),
    "asked-one-choice": ({"status": "asked", "questions": [{**QUESTION, "choices": ["a"]}]},
                         "choices: has 1 items, needs at least 2"),
    "asked-five-choices": ({"status": "asked", "questions": [{**QUESTION, "choices": list("abcde")}]},
                           "choices[4]: not allowed"),
    "extra-key": ({"status": "blocked", "blocker": "x", "by": "human"}, "`by` is not a known field"),
    "row-extra-key": ({"status": "done", "evidence": [{**ROW, "note": "x"}]},
                      "evidence[0]: `note` is not a known field"),
    "deviation-bad-line": ({"status": "done", "evidence": [ROW], "deviations": [{**DEVIATION, "line": "near 4"}]},
                           "deviations[0].line: 'near 4' does not match"),
    "blocked-empty": ({"status": "blocked", "blocker": ""}, "blocker: is empty"),
    "done-extra-key": ({"status": "done", "evidence": [ROW], "by": "x"}, "`by` is not a known field"),
    "asked-extra-key": ({"status": "asked", "questions": [QUESTION], "by": "x"}, "`by` is not a known field"),
    "question-extra-key": ({"status": "asked", "questions": [{**QUESTION, "why": "x"}]},
                           "questions[0]: `why` is not a known field"),
    "deviation-extra-key": ({"status": "done", "evidence": [ROW], "deviations": [{**DEVIATION, "by": "x"}]},
                            "deviations[0]: `by` is not a known field"),
    "question-no-recommended": ({"status": "asked", "questions": [{"question": "Which lane?", "choices": ["a", "b"]}]},
                                "questions[0]: `recommended` is missing"),
    "deviation-no-why": ({"status": "done", "evidence": [ROW],
                          "deviations": [{"what": "renamed f", "file": "a.py", "line": 4}]},
                         "deviations[0]: `why` is missing"),
    "asked-with-evidence": ({"status": "asked", "evidence": [ROW]}, "status: 'asked' is not 'done'"),
    "deferred-empty-entry": ({"status": "done", "evidence": [ROW], "deferred": [""]}, "deferred[0]: is empty"),
}


def process_tree() -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    texts = {
        "skills/crq/references/demo.md": REFERENCE,
        "skills/crq/process/glossary.md": "# Glossary\n",
        "skills/crq/process/lanes.json": json.dumps(LANES),
        V2: json.dumps(LANES_V2),
        "skills/crq/process/review.json": json.dumps(REVIEW),
        "skills/crq/process/roles/finder.md": CARD,
        **SCHEMAS,
        **{f"evals/finder/c{n}/prompt.md": "Review it.\n" for n in (1, 2, 3)},
        **{f"evals/finder/c{n}/graders/g.md": "---\ntype: llm\n---\nPASS if it finds.\n" for n in (1, 2, 3)},
    }
    marketplace = Path(tmp.name) / ".claude-plugin" / "marketplace.json"
    marketplace.parent.mkdir()
    marketplace.write_text(json.dumps(MARKETPLACE))
    for name, text in texts.items():
        target = Path(tmp.name) / "plugins" / "p" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return tmp


def plant(root: Path, name: str, text: str | None) -> None:
    target = root / "plugins" / "p" / name
    if text is not None:
        target.write_text(text)
    elif target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()


class CheckProcessTest(unittest.TestCase):
    def test_should_pass_a_valid_process(self):
        with process_tree() as root:
            result = run_check("process", Path(root))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_accept_a_rule_from_a_skill_router(self):
        with process_tree() as root:
            router = Path(root) / "plugins" / "p" / "skills" / "tidy" / "SKILL.md"
            router.parent.mkdir(parents=True)
            router.write_text("# Tidy\n\n## Rules\n\n- **TD1** — Tidy only, because a fix hides.\n")
            plant(Path(root), "skills/crq/process/roles/finder.md", CARD.replace("[DM1]", "[DM1, TD1]"))
            result = run_check("process", Path(root))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_accept_prose_guardrails_in_version_1(self):
        with process_tree() as root:
            plant(Path(root), "skills/crq/process/roles/finder.md",
                  CARD.replace("[read-only]", "read-only tools; no push"))
            result = run_check("process", Path(root))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_accept_an_id_from_a_schema_the_check_does_not_load(self):
        with process_tree() as root:
            plant(Path(root), "skills/crq/process/schema/note-v1.schema.json", '{"$id": "urn:rulebook:crq:note:1"}')
            plant(Path(root), "skills/crq/process/roles/finder.md",
                  CARD.replace("hand_off: findings", "hand_off: findings (urn:rulebook:crq:note:1)"))
            result = run_check("process", Path(root))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_should_fail_each_planted_case(self):
        for case, (name, text, *named) in PLANTED.items():
            with self.subTest(case), process_tree() as root:
                plant(Path(root), name, text)
                result = run_check("process", Path(root))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertTrue(result.stdout.strip(), "a failing check names the problem")
                for words in named:
                    self.assertIn(words, result.stdout)


class ReportSchemaTest(unittest.TestCase):
    def test_should_take_only_the_three_closed_shapes(self):
        schema = json.loads((SCHEMA_DIR / "report-v1.schema.json").read_text())
        for case, (report, words) in REPORTS.items():
            with self.subTest(case):
                found = validate(report, schema)
                if words is None:
                    self.assertEqual(found, [])
                else:
                    self.assertTrue(found, "a bad report fails")
                    self.assertIn(words, found[0])

    def test_should_have_each_card_cite_its_hand_off_schema(self):
        roles = SCHEMA_DIR.parent / "roles"
        cites = {"implementer": "report", "test-first": "report", "cleanup": "report", "finder": "finding"}
        for role, name in cites.items():
            with self.subTest(role):
                hand_off = re.search(r"^hand_off:(.*)$", (roles / f"{role}.md").read_text(), re.M).group(1)
                self.assertIn(f"(urn:rulebook:crq:{name}:1, process/schema/{name}-v1.schema.json)", hand_off)

    def test_should_declare_the_report_id(self):
        schema = json.loads((SCHEMA_DIR / "report-v1.schema.json").read_text())
        self.assertEqual(schema["$id"], "urn:rulebook:crq:report:1")


if __name__ == "__main__":
    unittest.main()
