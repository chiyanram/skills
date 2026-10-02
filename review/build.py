import re, json, html, sys
from pathlib import Path
R = Path("/Users/chiyanram/workspace/skills/research")
ledger = {}
for line in (R/"19-approved-rules.md").read_text().splitlines():
    m = re.match(r'^\|\s*([A-Za-z0-9-]+)\s*\|\s*([^|]*)\|\s*(.*?)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*$', line)
    if m: ledger[m.group(1)] = {"ref": m.group(2).strip(), "rule": m.group(3).strip()}

def parse(path, ids):
    txt = (R/path).read_text()
    parts = re.split(r'^### ', txt, flags=re.M)
    out = []
    for p in parts[1:]:
        head = p.splitlines()[0]
        rid = head.split(' ')[0]
        if rid not in ids: continue
        item = {"id": rid, "title": head.split('—',1)[-1].strip(), "rule": ledger.get(rid,{}).get("rule",""), "sides": []}
        for side in ("Good","Bad"):
            m = re.search(r'\*\*'+side+r'\*\*\s*\(([^)]*)\)(.*?)(?=\n\*\*(?:Good|Bad)\*\*|\Z)', p, re.S)
            if not m: continue
            kind, body = m.group(1), m.group(2)
            code = re.search(r'^(~~~~|```)(\w*)[^\n]*\n(.*?)\n\1', body, re.S|re.M)
            if code:
                _l, _t = code.group(2), code.group(3)
                class _C: pass
                code = _C(); code.group = (lambda i, _l=_l, _t=_t: _l if i == 1 else _t)
            loc = re.search(r'^`([^`]+)`\s*[—-]\s*(.*)$', body, re.M)
            if not code and loc:
                seg = body[:loc.start()]
                lines = seg.splitlines()
                idx = [n for n,l in enumerate(lines) if l.startswith("```")]
                if idx:
                    inner = lines[idx[0]+1: idx[-1] if len(idx)>1 and idx[-1]>idx[0] else len(lines)]
                    class C: pass
                    code = C(); code.group = (lambda i, _l=lines[idx[0]][3:].strip(), _t="\n".join(inner): _l if i==1 else _t)
            why = loc.group(2).strip() if loc else ""
            if not loc:
                w = re.search(r'^[—-]\s*(.+)$', body, re.M)
                why = w.group(1).strip() if w else body.strip()[:300]
            note = ""
            hdr = body.split('\n',1)[0].strip()
            if hdr: note = hdr
            item["sides"].append({"side": side, "kind": kind, "note": note, "lang": code.group(1) if code else "", "code": code.group(2).rstrip() if code else "", "loc": loc.group(1) if loc else "", "why": why})
        out.append(item)
    order = {i:n for n,i in enumerate(ids)}
    return sorted(out, key=lambda x: order[x["id"]])

groups = json.loads(sys.argv[1])
data = [{"key": g["key"], "name": g["name"], "items": parse(g["file"], g["ids"])} for g in groups]
tpl = Path("/Users/chiyanram/workspace/skills/review/template.html").read_text()
Path("/Users/chiyanram/workspace/skills/review/rule-review.html").write_text(tpl.replace("/*DATA*/[]", json.dumps(data)))
print({d["key"]: len(d["items"]) for d in data})
