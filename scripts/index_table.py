"""Builds a skill router's reference table from the references themselves, so a row is never written by hand and two
PRs never merge rows by hand (agent-factory#46)."""
import re
from pathlib import Path

START = "<!-- index: built by `make index` from each reference; do not edit by hand -->"
END = "<!-- /index -->"
HEADER = ["| reference | rule IDs | read it |", "|---|---|---|"]
RULE_ID = re.compile(r"^- \*\*([A-Z]+)(\d+)([a-z]?)\*\*", re.MULTILINE)
READ_IT = re.compile(r"\bRead it ((?:when|before) .+?)\.(?:\s|$)", re.DOTALL)


def intro(text: str) -> str:
    """The paragraph between the title and the first section, on one line."""
    body = text.split("\n## ", 1)[0].split("\n", 1)[-1]
    return " ".join(body.split())


def read_it(text: str) -> str | None:
    found = READ_IT.search(intro(text))
    return found.group(1) if found else None


def rules(text: str) -> str:
    return text.split("\n## Rules\n", 1)[1].split("\n## ", 1)[0] if "\n## Rules\n" in text else ""


def span(run: list[tuple[str, int, str]]) -> str:
    first, last = (f"{prefix}{number}{suffix}" for prefix, number, suffix in (run[0], run[-1]))
    return first if len(run) == 1 else f"{first}–{last}"


def follows(previous: tuple[str, int, str], current: tuple[str, int, str]) -> bool:
    return previous[0] == current[0] and current[1] == previous[1] + 1 and not previous[2] and not current[2]


def rule_ids(text: str) -> str:
    """Each rule ID, grouped by prefix in order of first use and sorted by number, with a run folded to `S1–S4`."""
    found = [(prefix, int(number), suffix) for prefix, number, suffix in RULE_ID.findall(rules(text))]
    order = {prefix: position for position, (prefix, _, _) in reversed(list(enumerate(found)))}
    runs: list[list[tuple[str, int, str]]] = []
    for current in sorted(found, key=lambda rule: (order[rule[0]], rule[1], rule[2])):
        if runs and follows(runs[-1][-1], current):
            runs[-1].append(current)
        else:
            runs.append([current])
    return ", ".join(span(run) for run in runs) or "—"


def row(reference: Path) -> str:
    text = reference.read_text()
    return f"| [{reference.stem}](references/{reference.name}) | {rule_ids(text)} | {read_it(text)} |"


def table(skill: Path) -> list[str]:
    return [START, *HEADER, *(row(reference) for reference in sorted(skill.glob("references/*.md"))), END]


def unreadable(skill: Path) -> list[str]:
    return [f"{reference}: no \"Read it when …\" or \"Read it before …\" sentence above its first section"
            for reference in sorted(skill.glob("references/*.md")) if read_it(reference.read_text()) is None]


def with_table(router: str, lines: list[str]) -> str | None:
    """The router with its index block replaced, or None when it has no index block."""
    if START not in router or END not in router:
        return None
    head, rest = router.split(START, 1)
    return head + "\n".join(lines) + rest.split(END, 1)[1]
