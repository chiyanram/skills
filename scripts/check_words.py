"""Shipped prose uses the plain word. This check fails a word or phrase that marks text as machine-written filler, and
names it, so the writer rewrites the sentence.

It fails the AI word list (additionally, crucial, delve, enhance, enhancement, foster, pivotal, showcase, testament,
vibrant, and their inflected forms), the verbs "underscores" and "underscored", "boast" and its forms ("boasts"),
"serves as", "stands as", "in order to", "it is important to note that", "simply", and "utilize" or "utilise" with
their forms. A phrase can wrap across a line break. "landscape" and the noun "underscore" pass, because they name a
page layout and a character.

It reads every Markdown and text file under plugins/rulebook/, except the third-party notices and the copied grilling
skill, and the root README.md, CONTRIBUTING.md and AGENTS.md. It skips the toolbox, whose skills are copied from other
repos.
Code fences and inline code spans are skipped. "easy" and "just" stay out: they are correct outside a procedure, so
the writing skill's review owns them.
"""
import re
import sys
from pathlib import Path

from check_provenance import CODE_SPAN, FENCE
from repo_files import files

WORDS = ("additionally", "crucial", "delve", "enhance", "enhancement", "foster", "pivotal", "showcase", "testament",
         "vibrant", "boast", "simply", "utilize", "utilise")
PHRASES = ("underscores", "underscored", "serves as", "stands as", "in order to", "it is important to note that")
ROOT_DOCS = ("README.md", "CONTRIBUTING.md", "AGENTS.md")
RULEBOOK = "plugins/rulebook/"
SKIPPED = ("THIRD_PARTY_NOTICES.md",)
COPIED = ("plugins/rulebook/skills/grilling/",)


def forms(word: str) -> set[str]:
    """The word and its plain inflections: delve, delves, delved, delving."""
    if word.endswith("ly"):
        return {word}
    stem = word[:-1] if word.endswith("e") else word
    return {word, word + "s", stem + "ed", stem + "ing", word + "ly"}


PATTERN = re.compile(
    r"\b(" + "|".join(sorted({f for w in WORDS for f in forms(w)} | {p.replace(" ", r"\s+") for p in PHRASES},
                             key=len, reverse=True)) + r")\b",
    re.IGNORECASE)


def in_scope(relative: str) -> bool:
    if relative in ROOT_DOCS:
        return True
    return (relative.startswith(RULEBOOK) and Path(relative).name not in SKIPPED
            and not relative.startswith(COPIED))


def prose(text: str) -> str:
    """The text with fenced lines blanked and code spans emptied; line numbers stay where they were."""
    kept, fence = [], None
    for line in text.splitlines():
        opening = FENCE.match(line)
        if opening:
            marker = opening.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not line.strip()[len(marker):].strip():
                fence = None
            kept.append("")
            continue
        kept.append("" if fence is not None else CODE_SPAN.sub("``", line))
    return "\n".join(kept)


def problems_in(path: Path, root: Path) -> list[str]:
    text = prose(path.read_text())
    return [f"{path.relative_to(root)}:{text.count(chr(10), 0, hit.start()) + 1}: "
            f"\"{' '.join(hit.group(1).split())}\" is filler; rewrite the sentence with the plain word"
            for hit in PATTERN.finditer(text)]


def problems(root: Path) -> list[str]:
    found = []
    for pattern in ("*.md", "*.txt"):
        for path in files(root, pattern):
            if in_scope(path.relative_to(root).as_posix()):
                found += problems_in(path, root)
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
