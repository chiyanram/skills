import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT, run_check

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

REVIEW = {"baseline": [{"skill": "crq", "reference": "demo"}]}

# Written to a temp dir, never committed: a planted card under plugins/ would be found by the other checks.
# Each planted case: (a path under the plugin root, its new text, or None to delete it).
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
    "schema-unknown-keyword": ("skills/crq/process/schema/lanes-v1.schema.json",
                               SCHEMAS["skills/crq/process/schema/lanes-v1.schema.json"].replace(
                                   '"minItems": 4', '"maxItems": 4, "minItems": 4')),
    "no-glossary": ("skills/crq/process/glossary.md", None),
    "no-review": ("skills/crq/process/review.json", None),
    "baseline-empty": ("skills/crq/process/review.json", json.dumps({"baseline": []})),
    "baseline-unshipped": ("skills/crq/process/review.json",
                           json.dumps({"baseline": [{"skill": "crq", "reference": "missing"}]})),
    "baseline-twice": ("skills/crq/process/review.json", json.dumps({"baseline": REVIEW["baseline"] * 2})),
    "baseline-extra-field": ("skills/crq/process/review.json",
                             json.dumps({"baseline": [{"skill": "crq", "reference": "demo", "why": "x"}]})),
}


def process_tree() -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    texts = {
        "skills/crq/references/demo.md": REFERENCE,
        "skills/crq/process/glossary.md": "# Glossary\n",
        "skills/crq/process/lanes.json": json.dumps(LANES),
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

    def test_should_fail_each_planted_case(self):
        for case, (name, text) in PLANTED.items():
            with self.subTest(case), process_tree() as root:
                plant(Path(root), name, text)
                result = run_check("process", Path(root))
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertTrue(result.stdout.strip(), "a failing check names the problem")


if __name__ == "__main__":
    unittest.main()
