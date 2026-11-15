"""The crq glossary (plugins/rulebook/skills/crq/process/glossary.md) gives one word per idea, and its `checked`
column lists the avoid words a script can catch. This check fails when a crq or planning file uses a checked word,
and names the term to use instead.

Only words in `checked` are caught, because most avoid words ("step", "result") are also plain English. The
glossary itself is spared.
"""
import re
import sys
from pathlib import Path

GLOSSARY = Path("plugins/rulebook/skills/crq/process/glossary.md")
SCOPE = (Path("plugins/rulebook/skills/crq"), Path("plugins/rulebook/skills/planning"))
SUFFIXES = (".md", ".json")


def checked_words(text: str) -> dict[str, list[str]]:
    """Each checked word, lower-cased, with the terms the glossary gives for it."""
    words: dict[str, list[str]] = {}
    column = None
    for line in text.splitlines():
        if not line.startswith("|"):
            column = None
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if column is None:
            column = cells.index("checked") if "checked" in cells else -1
            continue
        if column < 0 or column >= len(cells) or set(cells[0]) <= {"-"}:
            continue
        term = cells[0].strip("*")
        for word in cells[column].split(","):
            word = word.strip().lower()
            if word and word != "—":
                words.setdefault(word, []).append(term)
    return words


def problems(root: Path) -> list[str]:
    glossary = root / GLOSSARY
    if not glossary.is_file():
        return []
    words = checked_words(glossary.read_text())
    if not words:
        return []
    pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) + r")\b",
                         re.IGNORECASE)
    found = []
    for folder in SCOPE:
        for path in sorted((root / folder).rglob("*")):
            if path.suffix not in SUFFIXES or path == glossary:
                continue
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                for match in pattern.finditer(line):
                    terms = " or ".join(words[match.group(1).lower()])
                    found.append(f"{path.relative_to(root)}:{number}: \"{match.group(1)}\" is an avoid word; "
                                 f"use {terms} ({GLOSSARY})")
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
