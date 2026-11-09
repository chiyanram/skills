"""The crq process files an engine reads: the lanes file and the role cards (docs/DESIGN.md section 4, #237).

Fails when a lanes file misses a lane or a field, or lets a lane above tiny run without approval (the approval floor);
when a role card is not one of the known roles, misses a frontmatter field or adds one, cites a rule ID no reference
holds, or lacks the job, a "done when" line, numbered steps or an "it's working if" list; or when a role has fewer
than three eval scenarios, each a folder with a `prompt.md` and a grader under `graders/`.
"""
import json
import re
import sys
from pathlib import Path

from index_table import RULE_ID, rules

ROLES = {"coordinator", "design-reviewer", "test-first", "implementer", "cleanup", "finder", "verify-pass", "retro",
         "onboarder"}
FIELDS = ["role", "steps", "input", "must_not_see", "hand_off", "tools", "enforced_guardrails", "rules", "next"]
LANES = ["tiny", "bug", "feature", "one-way door"]
LANE_FIELDS = {"lane", "approval", "starts_on", "design_review", "test_first", "lenses", "retro"}
CITED = re.compile(r"\b[A-Z]+\d+[a-z]?\b")
FIELD = re.compile(r"^([a-z_]+):\s*(.*)$")
BODY_PARTS = [(re.compile(r"\*\*The job\.\*\*"), "the job"), (re.compile(r"\*\*Done when\*\*"), "a \"done when\" line"),
              (re.compile(r"^1\. ", re.M), "numbered steps"), (re.compile(r"\*\*It's working if:\*\*"),
                                                                  "an \"it's working if\" list")]
MIN_SCENARIOS = 3


def frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    head, body = text[4:].split("\n---\n", 1)
    fields = {}
    for line in head.splitlines():
        found = FIELD.match(line)
        if found:
            fields[found.group(1)] = found.group(2).strip()
    return fields, body


def known_ids(plugin: Path) -> set[str]:
    return {f"{p}{n}{s}" for reference in plugin.glob("skills/*/references/*.md")
            for p, n, s in RULE_ID.findall(rules(reference.read_text()))}


def scenario_problems(plugin: Path, role: str) -> list[str]:
    cases = sorted(d for d in (plugin / "evals" / role).glob("*/") if d.is_dir())
    found = [f"{case}: no prompt.md, or no grader under graders/" for case in cases
             if not (case / "prompt.md").is_file() or not any(case.glob("graders/*.md"))]
    if len(cases) < MIN_SCENARIOS:
        found.append(f"{plugin / 'evals' / role}: {len(cases)} eval scenarios, needs {MIN_SCENARIOS}")
    return found


def card_problems(card: Path, plugin: Path, ids: set[str]) -> list[str]:
    parsed = frontmatter(card.read_text())
    if parsed is None:
        return [f"{card}: no frontmatter"]
    fields, body = parsed
    found = []
    if card.stem not in ROLES:
        found.append(f"{card}: `{card.stem}` is not a role ({', '.join(sorted(ROLES))})")
    if fields.get("role") != card.stem:
        found.append(f"{card}: role `{fields.get('role')}` is not its file name")
    found += [f"{card}: frontmatter field `{f}` is missing or empty" for f in FIELDS if not fields.get(f)]
    found += [f"{card}: frontmatter field `{f}` is not a card field" for f in fields if f not in FIELDS]
    found += [f"{card}: rule `{rule}` is in no reference's Rules section"
              for rule in CITED.findall(fields.get("rules", "")) if rule not in ids]
    found += [f"{card}: the body lacks {what}" for pattern, what in BODY_PARTS if not pattern.search(body)]
    return found + scenario_problems(plugin, card.stem)


def lanes_problems(path: Path) -> list[str]:
    try:
        lanes = json.loads(path.read_text()).get("lanes", [])
    except (json.JSONDecodeError, AttributeError):
        return [f"{path}: not a JSON object with a `lanes` list"]
    found = []
    if [lane.get("lane") for lane in lanes] != LANES:
        found.append(f"{path}: lanes are not {', '.join(LANES)}, in that order")
    for lane in lanes:
        missing = LANE_FIELDS - set(lane)
        if missing:
            found.append(f"{path}: lane `{lane.get('lane')}` misses {', '.join(sorted(missing))}")
        if lane.get("lane") != "tiny" and lane.get("approval") is not True:
            found.append(f"{path}: lane `{lane.get('lane')}` drops approval, below the approval floor")
    return found


def problems(root: Path) -> list[str]:
    entries = json.loads((root / ".claude-plugin/marketplace.json").read_text()).get("plugins", [])
    found = []
    for entry in entries:
        plugin = root / entry["source"]
        ids = known_ids(plugin)
        for process in sorted(plugin.glob("skills/*/process/")):
            lanes = process / "lanes.json"
            found += lanes_problems(lanes) if lanes.is_file() else [f"{process}: no lanes.json"]
            if not (process / "glossary.md").is_file():
                found.append(f"{process}: no glossary.md")
            found += [p for card in sorted(process.glob("roles/*.md")) for p in card_problems(card, plugin, ids)]
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
