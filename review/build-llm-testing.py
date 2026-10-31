"""Build review/llm-testing-rules.html (G34, skills #133): candidate LLM-testing rules for the operator to approve.
Inputs: review/llm-testing.json (groups, each id's recommendation and why) and the candidate lines in
research/69-llm-testing-in-agent-sdks.md (LT) and research/70-agent-scenario-tests.md (LS):
"- **ID** — rule text — sources".
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "research"
SOURCES = ("69-llm-testing-in-agent-sdks.md", "70-agent-scenario-tests.md")
CANDIDATE = re.compile(r"^- \*\*(L[TS]\d+)\*\* — (.*)$", re.M)

rules = {}
for name in SOURCES:
    for rid, rest in CANDIDATE.findall((R / name).read_text()):
        text, _, cites = rest.rpartition(" — ")
        rules[rid] = {"rule": text.strip(), "cites": cites.replace("`", "").strip(), "file": f"research/{name}"}

groups = json.loads((ROOT / "review/llm-testing.json").read_text())
data = []
for g in groups:
    items = []
    for it in g["items"]:
        r = rules.get(it["id"])
        if r is None:
            raise SystemExit(f"{it['id']} has no candidate line in {', '.join(SOURCES)}")
        items.append({**it, **r})
    data.append({"key": g["key"], "name": g["name"], "note": g["note"], "items": items})

tpl = (ROOT / "review/template-llm-testing.html").read_text()
(ROOT / "review/llm-testing-rules.html").write_text(tpl.replace("/*DATA*/[]", json.dumps(data)))
print({d["key"]: len(d["items"]) for d in data})
