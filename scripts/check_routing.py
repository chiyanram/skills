"""A free, offline stand-in for the skill router: does each skill's description carry the words people use?

Each router (`plugins/*/skills/<name>/SKILL.md`) has a case file, `evals/routing/<name>.json`:

    {"skill": "<name>",
     "should": ["a request that must pick this router", ...],
     "near_miss": [{"prompt": "a request that shares its words", "owner": "<the router it belongs to>"}, ...]}

Every request is scored against every router's name and description with TF-IDF over crudely stemmed words, by
cosine similarity. The check fails when:
- a router has no case file, or a case file names no router;
- a file has fewer than MIN_CASES requests of either kind;
- a `should` request does not rank its router first;
- a `near_miss` names an unknown owner, or its owner does not outrank the router whose file holds it;
- two descriptions are near-duplicates (cosine at or above COLLISION).

It approximates the real router: it sees words, not meaning. A model-graded run (`claude plugin eval`) costs tokens,
so it stays a manual step and never runs here.
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

CASES_DIR = Path("evals/routing")
MIN_CASES = 8
COLLISION = 0.75

STOP = set("""
a an and any are as at be been before but by can do does each for from has have how i if in into is it its it's
me my need needs no not of on one or our should so that the their them then there these this those to up
us use used uses using via want was we what when where which while who why will with without you your
""".split())

SUFFIXES = ("ations", "ation", "ings", "ing", "ies", "ied", "ers", "er", "es", "ed", "ly", "s")


def stem(word: str) -> str:
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    return word[:-1] if word.endswith("e") and len(word) > 4 else word


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9]+", text.lower())
    return [stem(w) for w in words if w not in STOP and len(w) > 1]


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}
    block = text[4:].split("\n---", 1)[0]
    return {k.strip(): v.strip() for k, _, v in (line.partition(":") for line in block.splitlines()) if v}


def routers(root: Path) -> dict[str, str]:
    found = {}
    for path in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
        meta = frontmatter(path)
        name = meta.get("name", path.parent.name)
        found[name] = f"{name} {meta.get('description', '')}"
    return found


class Corpus:
    def __init__(self, docs: dict[str, str]):
        self.tf = {name: Counter(tokens(text)) for name, text in docs.items()}
        df = Counter(term for tf in self.tf.values() for term in tf)
        n = len(docs)
        self.idf = {term: math.log(1 + n / (1 + count)) for term, count in df.items()}

    def vector(self, tf: Counter) -> dict[str, float]:
        return {t: f * self.idf[t] for t, f in tf.items() if t in self.idf}

    def rank(self, prompt: str) -> list[tuple[str, float]]:
        query = self.vector(Counter(tokens(prompt)))
        scores = [(name, cosine(query, self.vector(tf))) for name, tf in self.tf.items()]
        return sorted(scores, key=lambda s: (-s[1], s[0]))


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(v * b.get(t, 0.0) for t, v in a.items())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def problems(root: Path) -> list[str]:
    docs = routers(root)
    if not docs:
        return []
    corpus = Corpus(docs)
    found = []
    files = {p.stem: p for p in sorted((root / CASES_DIR).glob("*.json"))}
    for name in docs:
        if name not in files:
            found.append(f"{CASES_DIR}/{name}.json: router {name} has no routing cases")
    for stem_name, path in files.items():
        where = f"{CASES_DIR}/{path.name}"
        if stem_name not in docs:
            found.append(f"{where}: names no router; routers are {', '.join(docs)}")
            continue
        cases = json.loads(path.read_text())
        should, near = cases.get("should", []), cases.get("near_miss", [])
        if len(should) < MIN_CASES or len(near) < MIN_CASES:
            found.append(f"{where}: needs at least {MIN_CASES} should and {MIN_CASES} near_miss requests, "
                         f"has {len(should)} and {len(near)}")
        for prompt in should:
            ranking = corpus.rank(prompt)
            if ranking[0][0] != stem_name or ranking[0][1] == 0:
                top = ", ".join(f"{n} {s:.2f}" for n, s in ranking[:3])
                found.append(f"{where}: \"{prompt}\" should pick {stem_name}, ranks {top}")
        for case in near:
            prompt, owner = case.get("prompt", ""), case.get("owner", "")
            if owner not in docs or owner == stem_name:
                found.append(f"{where}: near miss \"{prompt}\" needs an owner other than {stem_name}, has \"{owner}\"")
                continue
            scores = dict(corpus.rank(prompt))
            if scores[owner] == 0 or scores[owner] <= scores[stem_name]:
                found.append(f"{where}: near miss \"{prompt}\" belongs to {owner} ({scores[owner]:.2f}), "
                             f"but {stem_name} scores {scores[stem_name]:.2f}")
    names = list(docs)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            similarity = cosine(corpus.vector(corpus.tf[a]), corpus.vector(corpus.tf[b]))
            if similarity >= COLLISION:
                found.append(f"routers {a} and {b}: descriptions are {similarity:.0%} alike; make each name its own work")
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
