"""Build review/rule-reasons.html (skills #98): ledger rule + drafted reason + cite, grouped by domain.

Inputs: research/19-approved-rules.md (rule text, source cell) and review/reasons.json (drafts:
groups[].items[] = {line, id, reason, kind, cite, basis}; excluded[] = {line, id, why}).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROW = re.compile(r'^\|\s*([A-Za-z0-9-]+)\s*\|(.*)\|\s*$')

ledger = {}
for n, line in enumerate((ROOT / "research/19-approved-rules.md").read_text().splitlines(), 1):
    m = ROW.match(line)
    if not m or m.group(1) == "id":
        continue
    cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", m.group(2))]
    # id · reference · rule · reason · source · evidence · status (older: no reason, no evidence)
    has_reason = len(cells) >= 5
    ledger[(m.group(1), n)] = {
        "ref": cells[0],
        "rule": cells[1],
        "source": cells[3 if has_reason else 2],
    }

words = lambda s: len(s.split())
drafts = json.loads((ROOT / "review/reasons.json").read_text())
groups = []
for g in drafts["groups"]:
    items = []
    for d in g["items"]:
        row = ledger[(d["id"], d["line"])]
        reason = d["reason"] if d["kind"] != "none" else "NO-REASON"
        items.append({**d, **row, "reason": reason,
                      "rw": words(row["rule"]), "ow": 0 if d["kind"] == "none" else words(reason)})
    groups.append({"key": g["key"], "name": g["name"], "items": items})
excluded = [{**e, "rule": ledger[(e["id"], e["line"])]["rule"]} for e in drafts["excluded"]]

tpl = (ROOT / "review/template-reasons.html").read_text()
data = json.dumps({"groups": groups, "excluded": excluded}).replace("</", "<\\/")
(ROOT / "review/rule-reasons.html").write_text(tpl.replace('/*DATA*/{"groups":[],"excluded":[]}', data))
print({g["key"]: len(g["items"]) for g in groups}, "excluded", len(excluded))
