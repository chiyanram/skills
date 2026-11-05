import re, json
from pathlib import Path

# Spring core + Security (R33 #77, R34 #78) review page: same shell as build-g9b.py.
H = Path(__file__).resolve().parent
groups = json.loads((H / "r33.json").read_text()) + json.loads((H / "r34.json").read_text())

def rec_of(x):
    r = re.sub(r"^\W+", "", x["recommend"]).lower()
    if r.startswith("approved"): return "approved"
    if r.startswith("decided"): return "approved"
    if r.startswith("rejected"): return "rejected"
    if r.startswith(("agree", "sharpen", "fold")): return "adopt"
    if x["kind"].lower().startswith("decision") or re.match(r"^(X|OQ|ND)", x["id"]): return "decision"
    if r.startswith("hold"): return "hold"
    if r.startswith(("reject", "drop", "remove")): return "reject"
    if r.startswith(("adopt", "adapt", "keep", "approve", "accept", "replace", "rewrite", "fix", "new", "agree", "sharpen", "fold")): return "adopt"
    return "decision"

for g in groups:
    for x in g["items"]:
        x["rec"] = rec_of(x)
        s = x["source"].lower()
        if x["rec"] not in ("approved", "rejected") and "pstack" not in s and "mattpocock" not in s:
            x["source"] = "pstack, mattpocock: silent. " + x["source"]

page = (H / "planning-rules.html").read_text()
page = re.sub(r"^const D=\[.*\];$", lambda m: "const D=" + json.dumps(groups) + ";", page, count=1, flags=re.M)
swaps = [
    ("<title>Planning Rules Review</title>", "<title>Spring Rules Review</title>"),
    ('const KEY="planning-rules-v1";', 'const KEY="spring-rules-v1";'),
    ("<h1>Planning rules</h1>", "<h1>Spring core and Security rules</h1>"),
    ("Candidate rules for the five planning references (#35, G9d, map #9).",
     "Candidate rules from the Spring Boot 4.1 / Framework 7 and Security 7.1 references (R33 #77, R34 #78), for the code references of #33 (G9b, map #9). "
     "Purple <b>decision</b> items need your choice: Approve takes the recommendation, Change names another."),
    ('const recOf=r=>/^\\*{0,2}(adopt|hold|reject)/i.exec((r||"").replace(/^\\*+/,""));',
     'const recOf=x=>x.rec?[x.rec,x.rec]:null;'),
    ("const rm=recOf(x.recommend)", "const rm=recOf(x)"),
    ("const m=recOf(x.recommend);", "const m=recOf(x);"),
    ("let st={};try{st=JSON.parse(localStorage.getItem(KEY)||\"{}\")}catch(e){st={}}",
     "let st={};try{st=JSON.parse(localStorage.getItem(KEY)||\"{}\")}catch(e){st={}}\n"
     "D.forEach(g=>g.items.forEach(x=>{if(!st[x.id]&&x.rec===\"approved\")st[x.id]={v:\"ok\"};if(!st[x.id]&&x.rec===\"rejected\")st[x.id]={v:\"no\"}}));"),
    ('const L=["Planning rules (#35):"];', 'const L=["Spring core + Security rules (#77, #78):"];'),
    (".rec.adopt{color:var(--ok)}", ".rec.adopt{color:var(--ok)} .rec.approved,.rec.rejected{color:var(--muted,#888)} .rec.decision{color:#8250df}"),
]
for a, b in swaps:
    assert a in page, a
    page = page.replace(a, b)
(H / "spring-rules.html").write_text(page)
print(len(groups), sum(len(g["items"]) for g in groups),
      {k: sum(x["rec"] == k for g in groups for x in g["items"]) for k in ("approved", "adopt", "decision", "hold", "reject")})
