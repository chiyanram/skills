"""Build review/llm-testing-rules.html (G34, skills #133): LLM-testing rules for the operator to approve.
Inputs: review/llm-testing.json (groups, each id's recommendation and why); the candidate lines in
research/69-llm-testing-in-agent-sdks.md (LT) and research/70-agent-scenario-tests.md (LS),
"- **ID** — rule text — sources"; each rule's status in the "LLM testing" section of research/19-approved-rules.md;
and, for approved rules, the neutral Good/Bad pair and the reference's own code in research/71-llm-testing-good-bad.md.
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

LEDGER_ROW = re.compile(r"^\| (L[TS]\d+) \|.*\| ([^|]*) \|$", re.M)
status = {rid: st.strip() for rid, st in LEDGER_ROW.findall((R / "19-approved-rules.md").read_text())}


def block(section, label):
    m = re.search(r"\*\*" + label + r"\*\* \(neutral\)\n```(\w*)\n(.*?)\n```\n(.*?)(?=\n\n\*\*|\Z)", section, re.S)
    return {"lang": m.group(1), "code": m.group(2), "note": " ".join(m.group(3).split())} if m else None


pairs = {}
for section in re.split(r"^### ", (R / "71-llm-testing-good-bad.md").read_text(), flags=re.M)[1:]:
    rid = section.split()[0]
    ref = re.search(r"\*\*How the reference does it\*\* — (.*?)\n```(\w*)\n(.*?)\n```\n?(.*?)(?=\n### |\Z)", section, re.S)
    pairs[rid] = {
        "bad": block(section, "Bad"),
        "good": block(section, "Good"),
        "ref": {"where": ref.group(1).replace("`", ""), "lang": ref.group(2), "code": ref.group(3),
                "note": " ".join(ref.group(4).replace("`", "").split())} if ref else None,
    }

groups = json.loads((ROOT / "review/llm-testing.json").read_text())
data = []
for g in groups:
    items = []
    for it in g["items"]:
        r = rules.get(it["id"])
        if r is None:
            raise SystemExit(f"{it['id']} has no candidate line in {', '.join(SOURCES)}")
        items.append({**it, **r, "status": status.get(it["id"], ""), "pair": pairs.get(it["id"])})
    data.append({"key": g["key"], "name": g["name"], "note": g["note"], "items": items})

tpl = (ROOT / "review/template-llm-testing.html").read_text()
(ROOT / "review/llm-testing-rules.html").write_text(tpl.replace("/*DATA*/[]", json.dumps(data)))
print({d["key"]: len(d["items"]) for d in data})
