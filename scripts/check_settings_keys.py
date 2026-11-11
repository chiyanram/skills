"""A number a project tunes (memory ceiling, machine size, port, timeout) is written only as a settings key.

Shipped prose names the key, never its value: the value belongs to each project's settings, and a number written
into a rule goes stale on the first project that sets it differently. The check reads every markdown file in a
plugin's skills, outside fenced code, and fails a paragraph where such a key, in backticks, has a number in the same clause.
"""
import re
import sys
from pathlib import Path

from repo_files import files

SHIPPED = re.compile(r"^plugins/[^/]+/skills/")
KINDS = {"timeout", "port", "memory", "ceiling", "machine", "heap"}
FENCE = re.compile(r"^\s*(```|~~~)")
BLOCK_START = re.compile(r"^\s*([-*+]|\d+\.|#+|\|)\s")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
KEY = re.compile(r"^[A-Za-z][\w.-]*$")
KEY_WITH_VALUE = re.compile(r"^([A-Za-z][\w.-]*)\s*[=:]\s*['\"]?\d")
NUMBER = re.compile(r"(?<![\w.-])\d+(?:[.,_]\d+)*(?:[A-Za-z]{1,3})?(?![\w-])")
CLAUSE_END = re.compile(r"[.;!?](?=\s|$)")


def name_parts(key: str) -> set[str]:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)
    return {part.lower() for part in re.split(r"[\s._-]+", spaced) if part}


def is_setting(key: str) -> bool:
    return bool(KEY.match(key)) and bool(name_parts(key) & KINDS)


def paragraphs(text: str) -> list[tuple[int, str]]:
    found, current, start, fenced = [], [], 0, False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
        if fenced or FENCE.match(line) or not line.strip() or BLOCK_START.match(line):
            if current:
                found.append((start, " ".join(current)))
            current = [line] if not fenced and not FENCE.match(line) and line.strip() else []
            start = number
            continue
        if not current:
            start = number
        current.append(line.strip())
    if current:
        found.append((start, " ".join(current)))
    return found


def clause_around(paragraph: str, begin: int, end: int) -> str:
    stops = [m.end() for m in CLAUSE_END.finditer(paragraph)]
    left = max([s for s in stops if s <= begin], default=0)
    right = min([s for s in stops if s >= end], default=len(paragraph))
    return paragraph[left:begin] + " " + paragraph[end:right]


def paragraph_problems(paragraph: str) -> list[str]:
    found = []
    for span in CODE_SPAN.finditer(paragraph):
        token = span.group(1).strip()
        with_value = KEY_WITH_VALUE.match(token)
        if with_value and is_setting(with_value.group(1)):
            found.append(token)
        elif is_setting(token) and NUMBER.search(clause_around(paragraph, *span.span())):
            found.append(token)
    return found


def problems(root: Path) -> list[str]:
    found = []
    for path in files(root, "*.md"):
        if not SHIPPED.match(path.relative_to(root).as_posix()):
            continue
        for line, paragraph in paragraphs(path.read_text()):
            found += [f"{path}:{line}: `{key}` has a number beside it; name the settings key and leave its value to "
                      f"the project's settings" for key in paragraph_problems(paragraph)]
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
