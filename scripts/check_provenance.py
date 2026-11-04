"""A rule file holds only what an agent needs to act; where a rule came from lives in the ledger
(research/19-approved-rules.md) and the research files (agent-factory#59).

Fails on a shipped skill file (a SKILL.md or a reference under plugins/*/skills/) that carries provenance:
a source citation (`pstack :15`, `r47 :456`), an "Operator preference" line, a credit on an example
(`**Bad** (from …)`), a "(neutral)" label, a "Real evidence" note, a date or an agent-factory issue reference.
Tool names stay when they are the action itself, and cross-references to other rules stay.
"""
import re
import sys
from pathlib import Path

from repo_files import files

PATTERNS = [
    (re.compile(r"Operator preference", re.I), "an operator-preference line"),
    (re.compile(r"\b[\w.-]+ :\d+(?:-\d+)?\b"), "a source citation (name :line)"),
    (re.compile(r"\*\*(?:Bad|Good)\*\*\s*\("), "a credit or label on an example"),
    (re.compile(r"Real evidence", re.I), "a ledger-evidence note"),
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "a date"),
    (re.compile(r"agent-factory(?:#\d+|\s+research/)"), "an agent-factory issue or research reference"),
]
FENCE = re.compile(r"^\s*(```|~~~)")


def shipped(root: Path) -> list[Path]:
    return [f for f in files(root, "*.md") if "skills" in f.relative_to(root).parts
            and f.relative_to(root).parts[0] == "plugins"]


def problems_in(path: Path) -> list[str]:
    found, in_code = [], False
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        for pattern, what in PATTERNS:
            if pattern.search(line):
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
