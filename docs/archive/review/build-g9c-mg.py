import re, json
from pathlib import Path

# G9c (#34) migrations rules review page: planning-rules.html shell + research/60a.
H = Path(__file__).resolve().parent
src = (H.parent / "research/60a-g9c-migrations.md").read_text()
TIER_B = {5,10,11,12,13,14,15,16,19,22,23,24,41,43,44,45,46,47,52}

rows = []
sec1 = src.split("## 1 ·")[1].split("## 2 ·")[0]
for l in sec1.splitlines():
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    if len(c) == 5 and c[0].startswith("`skel") or (len(c) == 5 and c[0].startswith("hooks")):
        rows.append({"id": f"F{len(rows)+1}", "title": c[0][:80], "rule": f"{c[0]} → {c[1]} · {c[2]}",
                     "source": c[3], "kind": "file row", "recommend": "ADOPT — " + c[4], "extra": "", "drop": ""})

groups = [{"name": "0 · File rows (R12, G1b-corrected) — where each current file goes", "items": rows}]
deferred = []
for sec in re.split(r"^### ", src.split("## 2 ·")[1].split("## 3 ·")[0], flags=re.M)[1:]:
    head = sec.splitlines()[0]
    items = []
    for l in sec.splitlines():
        m = re.match(r"^- \*\*(MG(\d+))\*\* — (.*)$", l)
        if not m: continue
        p = m.group(3).split(" — ")
        it = {"id": m.group(1), "title": p[0][:70], "rule": p[0], "source": " — ".join(p[1:-1]),
              "kind": "rule", "recommend": p[-1].strip("* "), "extra": "", "drop": ""}
        if int(m.group(2)) in TIER_B:
            it["recommend"] = "DECIDED 2026-10-04: deferred to #57 (applies from the first production deploy)"
            deferred.append(it)
        else:
            items.append(it)
    if items: groups.append({"name": f"{len(groups)} · {head}", "items": items})
groups.append({"name": f"{len(groups)} · Tier B — deferred to #57 Later·Persistence (already decided, shown for the record)", "items": deferred})

def rec_of(x):
    r = re.sub(r"^\W+", "", x["recommend"]).lower()
    if r.startswith("decided"): return "approved"
    if "project decision" in r: return "decision"
    if r.startswith(("drop", "reject")): return "reject"
    return "adopt"
for g in groups:
    for x in g["items"]: x["rec"] = rec_of(x)

page = (H / "planning-rules.html").read_text()
page = re.sub(r"^const D=\[.*\];$", lambda m: "const D=" + json.dumps(groups) + ";", page, count=1, flags=re.M)
swaps = [
    ("<title>Planning Rules Review</title>", "<title>Migration Rules</title>"),
    ('const KEY="planning-rules-v1";', 'const KEY="g9c-mg-rules-v1";'),
    ("<h1>Planning rules</h1>", "<h1>Migration rules</h1>"),
    ("Candidate rules for the five planning references (#35, G9d, map #9).",
     "Migration rules for #34 (G9c, map #9). Dev mode: only tier A is up for approval; tier B is deferred to #57 until the first production deploy. "
     "Every rule cites the reference it comes from (SRC1). Purple <b>decision</b> items need your choice."),
    ('const recOf=r=>/^\\*{0,2}(adopt|hold|reject)/i.exec((r||"").replace(/^\\*+/,""));', 'const recOf=x=>x.rec?[x.rec,x.rec]:null;'),
    ("const rm=recOf(x.recommend)", "const rm=recOf(x)"),
    ("const m=recOf(x.recommend);", "const m=recOf(x);"),
    ("let st={};try{st=JSON.parse(localStorage.getItem(KEY)||\"{}\")}catch(e){st={}}",
     "let st={};try{st=JSON.parse(localStorage.getItem(KEY)||\"{}\")}catch(e){st={}}\n"
     "D.forEach(g=>g.items.forEach(x=>{if(!st[x.id]&&x.rec===\"approved\")st[x.id]={v:\"ok\"}}));"),
    ('const L=["Planning rules (#35):"];', 'const L=["G9c migration rules (#34):"];'),
    (".rec.adopt{color:var(--ok)}", ".rec.adopt{color:var(--ok)} .rec.approved{color:var(--muted,#888)} .rec.decision{color:#8250df}"),
]
for a, b in swaps:
    assert a in page, a
    page = page.replace(a, b)
(H / "g9c-migration-rules.html").write_text(page)
print([(g["name"][:50], len(g["items"])) for g in groups])
