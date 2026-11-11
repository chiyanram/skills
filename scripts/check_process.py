"""The crq process files an engine reads: the lanes file, the review baseline and the role cards (docs/DESIGN.md
section 4, #237).

Fails when a lanes file misses a lane or a field, or lets a lane above tiny run without approval (the approval floor);
when the review file's baseline is empty, has an entry that is not exactly a skill and a reference, names a reference
twice, or names one the plugin does not ship;
when a role card is not one of the known roles, misses a frontmatter field or adds one, cites a rule ID no Rules section
holds, or lacks the job, a "done when" line, numbered steps or an "it's working if" list; or when a role has fewer
than three eval scenarios, each a folder with a `prompt.md` and a grader under `graders/`.

The roles, the card fields, the guardrail IDs and the lanes come from the versioned schemas the plugin ships in
process/schema/ (card, lanes, finding); the check fails when one is missing or uses a keyword schema_lite cannot run.
"""
import json
import re
import sys
from pathlib import Path

from index_table import RULE_ID, rules
from schema_lite import unknown_keywords, validate

SCHEMAS = {"card": "card-v1.schema.json", "lanes": "lanes-v1.schema.json", "finding": "finding-v1.schema.json"}
CITED = re.compile(r"\b[A-Z]+\d+[a-z]?\b")
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


def card_problems(card: Path, plugin: Path, ids: set[str], schema: dict) -> list[str]:
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
    found += [f"{card}: the body lacks {what}" for pattern, what in BODY_PARTS if not pattern.search(body)]
    return found + scenario_problems(plugin, card.stem)


def lanes_problems(path: Path, schema: dict) -> list[str]:
    try:
        lanes = json.loads(path.read_text())
    except json.JSONDecodeError:
        return [f"{path}: not JSON"]
    return [f"{path}: {problem}" for problem in validate(lanes, schema)]


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


def problems(root: Path) -> list[str]:
    entries = json.loads((root / ".claude-plugin/marketplace.json").read_text()).get("plugins", [])
    found = []
    for entry in entries:
        plugin = root / entry["source"]
        ids = known_ids(plugin)
        for process in sorted(plugin.glob("skills/*/process/")):
            schemas, schema_found = load_schemas(process)
            found += schema_found
            if schema_found:
                continue
            lanes = process / "lanes.json"
            found += lanes_problems(lanes, schemas["lanes"]) if lanes.is_file() else [f"{process}: no lanes.json"]
            review = process / "review.json"
            found += baseline_problems(review, plugin) if review.is_file() else [f"{process}: no review.json"]
            if not (process / "glossary.md").is_file():
                found.append(f"{process}: no glossary.md")
            found += [p for card in sorted(process.glob("roles/*.md")) for p in card_problems(card, plugin, ids, schemas["card"])]
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
