"""Every relative link in a markdown file resolves to a file or folder. Code spans and fenced blocks are skipped."""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from repo_files import files

LINK = re.compile(r"\[[^\]]*\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CODE_SPAN = re.compile(r"(`+).*?\1")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def closes(fence: str, line: str) -> bool:
    match = FENCE.match(line)
    return bool(match) and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
        and not match.group(2).strip()


def prose_lines(text: str):
    fence = ""
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            fence = "" if closes(fence, line) else fence
        elif FENCE.match(line):
            fence = FENCE.match(line).group(1)
        else:
            yield number, CODE_SPAN.sub("", line)


def broken(markdown: Path, root: Path) -> list[str]:
    found = []
    for number, line in prose_lines(markdown.read_text()):
        for target in LINK.findall(line):
            path = unquote(target.split("#", 1)[0])
            if not path or SCHEME.match(target):
                continue
            resolved = root / path.lstrip("/") if path.startswith("/") else markdown.parent / path
            if not resolved.exists():
                found.append(f"{markdown}:{number}: link target `{target}` does not exist")
    return found


def problems(root: Path) -> list[str]:
    return [p for markdown in files(root, "*.md") for p in broken(markdown, root)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
