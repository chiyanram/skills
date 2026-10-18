"""Build review/neutral-pairs.html (skills #99): neutral Good/Bad pairs from research/68a-f, one tab per file.

Each pair: "### <ID> — <title>", "**Bad** (<kind>)" + fence + "What goes wrong: …", "**Good** (<kind>)" + fence +
"Why: …", "Evidence: …". Rule text and reason come from the ledger research/19-approved-rules.md.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS = [
    ("68a-neutral-testing-strategy.md", "strategy", "Testing: strategy, coverage, boundaries, value bar"),
    ("68b-neutral-testing-unit-it-spock.md", "unit-it-spock", "Testing: unit, IT, Spock"),
    ("68c-neutral-testing-mutation-property-scenarios.md", "mut-prop-scen", "Testing: mutation, property, scenarios"),
    ("68d-neutral-testing-smoke.md", "smoke", "Testing: smoke specs"),
    ("68e-neutral-planning.md", "planning", "Planning"),
    ("68f-neutral-code.md", "code", "Code (G9b)"),
]
ROW = re.compile(r'^\|\s*([A-Za-z0-9-]+)\s*\|(.*)\|\s*$')
FENCE = re.compile(r'^(~~~~|```)(\w*)[^\n]*\n(.*?)\n\1\s*$', re.S | re.M)

ledger = {}
for line in (ROOT / "research/19-approved-rules.md").read_text().splitlines():
    m = ROW.match(line)
    if m and m.group(1) != "id":
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", m.group(2))]
        ledger.setdefault(m.group(1), {"rule": cells[1], "reason": cells[2]})


def side(block, name):
    m = re.search(r'^\*\*' + name + r'\*\*\s*\(([^)]*)\)(.*?)(?=^\*\*(?:Good|Bad)\*\*|^Evidence:|\Z)', block, re.S | re.M)
    if not m:
        return None
    kind, body = m.group(1), m.group(2)
    code = FENCE.search(body)
    why = re.search(r'^(?:What goes wrong|Why):\s*(.+)$', body, re.M)
    rest = body[code.end():] if code else body
    return {"side": name, "kind": kind, "lang": code.group(2) if code else "",
            "code": code.group(3).rstrip() if code else "", "loc": "",
            "why": why.group(1).strip() if why else rest.strip()[:300], "note": ""}


def parse(path):
    items = []
    for part in re.split(r'^### ', (ROOT / "research" / path).read_text(), flags=re.M)[1:]:
        head, _, block = part.partition("\n")
        rid = head.split(" ")[0]
        ev = re.search(r'^Evidence:\s*(.+)$', block, re.M)
        sides = [s for s in (side(block, "Good"), side(block, "Bad")) if s]
        bad = next((s for s in sides if s["side"] == "Bad"), None)
        if bad and ev:
            bad["loc"] = "Evidence (ledger only): " + ev.group(1).strip()
        row = ledger.get(rid, {})
        items.append({"id": rid, "title": head.split("—", 1)[-1].strip(), "rule": row.get("rule", ""),
                      "reason": row.get("reason", ""), "sides": sides, "evidence": ev.group(1).strip() if ev else ""})
    return items


data = [{"key": k, "name": n, "file": f, "items": parse(f)} for f, k, n in GROUPS if (ROOT / "research" / f).exists()]
(ROOT / "review/neutral-pairs.json").write_text(json.dumps(
    [{"file": g["file"], "pairs": [{"id": i["id"], "evidence": i["evidence"]} for i in g["items"]]} for g in data], indent=1))
tpl = (ROOT / "review/template-neutral.html").read_text()
(ROOT / "review/neutral-pairs.html").write_text(tpl.replace("/*DATA*/[]", json.dumps(data).replace("</", "<\\/")))
print({g["key"]: len(g["items"]) for g in data})
