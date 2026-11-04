"""A rule file holds only what an agent needs to act; where a rule came from lives in the ledger
(research/19-approved-rules.md) and the research files (agent-factory#59).

Fails on a shipped skill file (a SKILL.md or a reference under plugins/*/skills/) that carries provenance:
a source citation (`pstack :15`, `r47 :456`, `file.md:13`, `§Section`, a URL, `ADR-0007`, `research/41`), an
"Operator preference" line, a credit or label on an example (`**Bad** (from …)`, `(neutral)`), a "Real evidence"
note, a date or an agent-factory reference. Code fences and inline code spans are skipped.
Tool names stay when they are the action itself, and cross-references to other rules stay.
"""
import re
import sys
from pathlib import Path

from repo_files import files

PATTERNS = [
    (re.compile(r"Operator preference", re.I), "an operator-preference line"),
    (re.compile(r"\b[\w.-]+ :\d+(?:-\d+)?\b"), "a source citation (name :line)"),
    (re.compile(r"\b[\w./-]+\.(?:md|adoc|java|kt|ts|py|sgml|html|ya?ml):\d+"), "a source citation (file:line)"),
    (re.compile(r"\b(?:\d+[a-z]|R):\d+\b"), "a source citation (short form:line)"),
    (re.compile(r"§\s?\w"), "a section citation"),
    (re.compile(r"https?://"), "a URL"),
    (re.compile(r"\bADR-\d+|\bresearch/\d+|\bledger :?\d+|\bSonar S\d+"), "a reference to a decision, research file or source"),
    (re.compile(r"\*\*(?:Bad|Good)\*\*\s*\((?:from|neutral|adapted|real|source|n/a)", re.I), "a credit or label on an example"),
    (re.compile(r"Real evidence|Evidence: ledger", re.I), "a ledger-evidence note"),
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "a date"),
    (re.compile(r"agent-factory\W"), "an agent-factory reference"),
]
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")


def shipped(root: Path) -> list[Path]:
    return [f for f in files(root, "*.md") if "skills" in f.relative_to(root).parts
            and f.relative_to(root).parts[0] == "plugins"]


def problems_in(path: Path) -> list[str]:
    found, fence = [], None
    for number, line in enumerate(path.read_text().splitlines(), 1):
        opening = FENCE.match(line)
        if opening:
            marker = opening.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not line.strip()[len(marker):].strip():
                fence = None
            continue
        if fence is not None:
            continue
        prose = CODE_SPAN.sub("``", line)
        for pattern, what in PATTERNS:
            if pattern.search(prose):
                found.append(f"{path}:{number}: {what}: {line.strip()[:80]}")
                break
    return found


def problems(root: Path) -> list[str]:
    return [p for f in shipped(root) for p in problems_in(f)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
