"""The crq process files an engine reads: the lanes files, the review baseline and the role cards (docs/DESIGN.md
section 4, #237).

Fails when a lanes file misses a lane or a field, or lets a lane above tiny run without approval (the approval floor);
when the lanes-v2 file is missing or does not validate against its schema, which covers the four lanes in order and
each lane's lens cap, review model and effort; or when its graph breaks (scripts/lanes_graph.py): a lane names a
phase outside the phase order or out of it, the order holds a phase twice, a phase has no outcomes, an edge is not a
string or an object with a string `to`, an optional string `counts` and no other key, points at no phase or end, or
counts a key with no cap, a cap is not an integer of at least 1, a `when` names no condition or a condition is not text
or is empty, a lane above tiny has no plain approval entry, a lane does not end with a plain timeline-record entry, an
actor is not a card role, human or engine, a lens cap is below 1, or lane_raise goes to no phase;
when the review file's baseline is empty, has an entry that is not exactly a skill and a reference, names a reference
twice, or names one the plugin does not ship;
when a role card is not one of the known roles, misses a frontmatter field or adds one, cites a rule ID no Rules section
holds, or lacks the job, a "done when" line, numbered steps or an "it's working if" list; or when a role has fewer
than three eval scenarios, each a folder with a `prompt.md` and a grader under `graders/`; or when a card's
frontmatter or the lanes-v2 file cites a `urn:rulebook:crq:<name>:<n>` id that no process/schema/*.schema.json file
declares as its `$id`.

The roles, the card fields, the guardrail IDs and the lanes come from the versioned schemas the plugin ships in
process/schema/ (card, lanes, lanes-v2, finding, and report for the writers' .factory/report.json); the check fails
when one is missing or uses a keyword schema_lite cannot run.
"""
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path

import lanes_graph
from index_table import RULE_ID, rules
from schema_lite import unknown_keywords, validate

SCHEMAS = {"card": "card-v1.schema.json", "lanes": "lanes-v1.schema.json", "lanes-v2": "lanes-v2.schema.json",
           "finding": "finding-v1.schema.json", "report": "report-v1.schema.json"}
CITED = re.compile(r"\b[A-Z]+\d+[a-z]?\b")
URN = re.compile(r"urn:rulebook:crq:[a-z0-9-]+:\d+")
FIELD = re.compile(r"^([a-z_]+):\s*(.*)$")
BODY_PARTS = [(re.compile(r"\*\*The job\.\*\*"), "the job"), (re.compile(r"\*\*Done when\*\*"), "a \"done when\" line"),
              (re.compile(r"^1\. ", re.M), "numbered steps"), (re.compile(r"\*\*It's working if:\*\*"),
                                                                  "an \"it's working if\" list")]
MIN_SCENARIOS = 3


def value(raw: str) -> str | list[str]:
    """A frontmatter value: `[a, b]` is a list, anything else a string."""
    if raw.startswith("[") and raw.endswith("]"):
        return [item.strip() for item in raw[1:-1].split(",") if item.strip()]
    return raw


def frontmatter(text: str) -> tuple[dict, str] | None:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    head, body = text[4:].split("\n---\n", 1)
    fields = {}
    for line in head.splitlines():
        found = FIELD.match(line)
        if found:
            fields[found.group(1)] = value(found.group(2).strip())
    return fields, body


def known_ids(plugin: Path) -> set[str]:
    """Rule IDs from each reference's Rules section, and from a skill that keeps its rules in its SKILL.md."""
    sources = [*plugin.glob("skills/*/references/*.md"), *plugin.glob("skills/*/SKILL.md")]
    return {f"{p}{n}{s}" for source in sources for p, n, s in RULE_ID.findall(rules(source.read_text()))}


def scenario_problems(plugin: Path, role: str) -> list[str]:
    cases = sorted(d for d in (plugin / "evals" / role).glob("*/") if d.is_dir())
    found = [f"{case}: no prompt.md, or no grader under graders/" for case in cases
             if not (case / "prompt.md").is_file() or not any(case.glob("graders/*.md"))]
    if len(cases) < MIN_SCENARIOS:
        found.append(f"{plugin / 'evals' / role}: {len(cases)} eval scenarios, needs {MIN_SCENARIOS}")
    return found


def cited_ids(text: str) -> list[str]:
    """Each schema id the text cites, once, in order."""
    return list(dict.fromkeys(URN.findall(text)))


def unknown_id_problems(path: Path, text: str, declared: set[str]) -> list[str]:
    return [f"{path}: cites {cited}, which no schema in process/schema/ declares"
            for cited in cited_ids(text) if cited not in declared]


def card_problems(card: Path, plugin: Path, ids: set[str], schema: dict, declared: set[str]) -> list[str]:
    parsed = frontmatter(card.read_text())
    if parsed is None:
        return [f"{card}: no frontmatter"]
    fields, body = parsed
    found = []
    if fields.get("role") != card.stem:
        found.append(f"{card}: role `{fields.get('role')}` is not its file name")
    found += [f"{card}: {problem}" for problem in validate(fields, schema)]
    cited = fields.get("rules") if isinstance(fields.get("rules"), list) else []
    found += [f"{card}: rule `{rule}` is in no reference's Rules section"
              for rule in cited if CITED.fullmatch(rule) and rule not in ids]
    found += unknown_id_problems(card, json.dumps(fields), declared)
    found += [f"{card}: the body lacks {what}" for pattern, what in BODY_PARTS if not pattern.search(body)]
    return found + scenario_problems(plugin, card.stem)


def load_json(path: Path) -> tuple[object, list[str]]:
    """The parsed file, or one line saying it is not JSON."""
    try:
        return json.loads(path.read_text()), []
    except json.JSONDecodeError:
        return None, [f"{path}: not JSON"]


def schema_ids(process: Path) -> set[str]:
    """The `$id` of every schema in process/schema/, whether SCHEMAS names it or not."""
    docs = (load_json(path)[0] for path in process.glob("schema/*.schema.json"))
    return {doc["$id"] for doc in docs if isinstance(doc, dict) and isinstance(doc.get("$id"), str)}


def lanes_problems(path: Path, schema: dict) -> list[str]:
    lanes, found = load_json(path)
    return found or [f"{path}: {problem}" for problem in validate(lanes, schema)]


def lanes_v2_problems(path: Path, schema: dict, roles: list[str]) -> list[str]:
    """The not-JSON line, else the schema lines, else the graph lines."""
    lanes, found = load_json(path)
    found = found or [f"{path}: {problem}" for problem in validate(lanes, schema)]
    return found or [f"{path}: {problem}" for problem in lanes_graph.problems(lanes, roles)]


def load_schemas(process: Path) -> tuple[dict[str, dict], list[str]]:
    schemas, found = {}, []
    for part, name in SCHEMAS.items():
        path = process / "schema" / name
        try:
            schemas[part] = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            found.append(f"{path}: missing, or not JSON")
            continue
        found += [f"{path}: {problem}" for problem in unknown_keywords(schemas[part])]
    return schemas, found


def baseline_problems(path: Path, plugin: Path) -> list[str]:
    try:
        baseline = json.loads(path.read_text()).get("baseline")
    except (json.JSONDecodeError, AttributeError):
        baseline = None
    if not isinstance(baseline, list) or not baseline:
        return [f"{path}: not a JSON object with a non-empty `baseline` list"]
    found = []
    seen = set()
    for entry in baseline:
        if not isinstance(entry, dict) or set(entry) != {"skill", "reference"}:
            found.append(f"{path}: baseline entry {json.dumps(entry)} is not exactly {{skill, reference}}")
            continue
        name = f"{entry['skill']}/{entry['reference']}"
        if name in seen:
            found.append(f"{path}: baseline names `{name}` twice")
        seen.add(name)
        if not (plugin / "skills" / str(entry["skill"]) / "references" / f"{entry['reference']}.md").is_file():
            found.append(f"{path}: baseline names `{name}`, which the plugin does not ship")
    return found


def required(path: Path, check: Callable[[Path], list[str]]) -> list[str]:
    """`check(path)` on a file that is there, else one line naming the folder and the missing file."""
    return check(path) if path.is_file() else [f"{path.parent}: no {path.name}"]


def process_problems(process: Path, plugin: Path, ids: set[str]) -> list[str]:
    schemas, found = load_schemas(process)
    if found:
        return found
    roles = schemas["card"]["properties"]["role"]["enum"]
    files = [("lanes.json", lambda path: lanes_problems(path, schemas["lanes"])),
             ("lanes-v2.json", lambda path: lanes_v2_problems(path, schemas["lanes-v2"], roles)),
             ("review.json", lambda path: baseline_problems(path, plugin)),
             ("glossary.md", lambda path: [])]
    found = [line for name, check in files for line in required(process / name, check)]
    declared, v2 = schema_ids(process), process / "lanes-v2.json"
    found += unknown_id_problems(v2, v2.read_text(), declared) if v2.is_file() else []
    cards = sorted(process.glob("roles/*.md"))
    return found + [line for card in cards for line in card_problems(card, plugin, ids, schemas["card"], declared)]


def problems(root: Path) -> list[str]:
    entries = json.loads((root / ".claude-plugin/marketplace.json").read_text()).get("plugins", [])
    found = []
    for plugin in (root / entry["source"] for entry in entries):
        ids = known_ids(plugin)
        found += [line for process in sorted(plugin.glob("skills/*/process/"))
                  for line in process_problems(process, plugin, ids)]
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
