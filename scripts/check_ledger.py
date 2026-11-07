"""The ledger (docs/rulebook/approved-rules.md) is append-only and merged with git's `union` driver
(.gitattributes), so a merge keeps both sides' new sections without a conflict.

Union has one blind spot: when two branches edit the same row, it keeps both versions. So this check fails
when two rows carry the same rule ID for the same reference, unless the later row says in its own text that it
supersedes the earlier one ("Supersedes"). It also fails on a left-over conflict marker.
"""
import re
import sys
from pathlib import Path

LEDGER = Path("docs/rulebook/approved-rules.md")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
MARKER = re.compile(r"^(<{7}|={7}|>{7})( |$)")


def rows(text: str):
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("| ") or line.startswith("| id ") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in CELL_SPLIT.split(line)[1:-1]]
        if len(cells) >= 3 and cells[0]:
            yield number, cells[0], cells[1], line


def problems(root: Path) -> list[str]:
    path = root / LEDGER
    if not path.is_file():
        return []
    text = path.read_text()
    found = [f"{LEDGER}:{n}: conflict marker left in the ledger"
             for n, line in enumerate(text.splitlines(), start=1) if MARKER.match(line)]
    first: dict[tuple[str, str], int] = {}
    for number, rule_id, reference, line in rows(text):
        key = (rule_id, reference)
        if key in first and "Supersedes" not in line:
            found.append(f"{LEDGER}:{number}: {rule_id} for {reference} repeats line {first[key]}; "
                         "say \"Supersedes\" in the later row, or remove the copy a merge kept")
        first.setdefault(key, number)
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
