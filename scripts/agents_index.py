"""The root README holds a copy of each plugin's hooks/index.txt for a project to paste into its AGENTS.md, and
`make index` writes that copy, so the pasted text and the text the opt-in hook prints never differ."""
from pathlib import Path

README = Path("README.md")
INDEX = Path("hooks/index.txt")
END = "<!-- /agents-index -->"


def start(index: Path) -> str:
    return f"<!-- agents-index: built by `make index` from {index.as_posix()}; do not edit by hand -->"


def with_index(readme: str, index: Path, text: str) -> str | None:
    """The README with the block for `index` replaced by `text`, or None when it has no such block."""
    marker = start(index)
    if marker not in readme or END not in readme.split(marker, 1)[1]:
        return None
    head, rest = readme.split(marker, 1)
    return head + "\n".join([marker, "```text", text.rstrip("\n"), "```", END]) + rest.split(END, 1)[1]


def built(root: Path, folder: Path) -> tuple[str, str | None] | None:
    """The README as it is and as `make index` builds it, or None when the plugin ships no index."""
    index = folder / INDEX
    if not index.is_file():
        return None
    current = (root / README).read_text() if (root / README).is_file() else ""
    return current, with_index(current, index.relative_to(root), index.read_text())
