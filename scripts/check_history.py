"""A doc line or code comment outside plugins/ says what and why, never who decided, when, or on which issue.

History has one home: the ledger for rules, and the git log, the pull requests and the ADRs for the rest. The check
reads only the lines a change adds since it left the base branch (default `origin/main`), so notes already on the base
pass and go when a file is edited anyway. Uncommitted and untracked files count as added.

It reads prose in markdown (not fences, inline code, link targets, headings or HTML comments) and comment text in code
(a Python comment or docstring, a JS comment, a `#` comment in YAML, TOML, shell or a Makefile). It fails a who-decided
phrase, an ISO date beside a person or decision word, and an issue number. It spares `plugins/` (check_provenance.py
reads it), fixtures, `docs/agents/`, `evals/`, the CHANGELOGs, ledger rows, an ADR's or PRINCIPLES.md's status line
and an ADR's table rows, and one pointer line (`See` or `History:` and issue refs) per markdown section or code header.
"""
import ast
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

from check_provenance import CODE_SPAN, FENCE

REF = r"(?:[\w.-]+/[\w.-]+)?#\d+"
WHO = re.compile(r"\b(?:decided|agreed|approved|chosen|picked|requested)\s+(?:by|with)\b"
                 r"|\boperator\s+(?:decided|chose|approved|agreed|asked|said)\b", re.I)
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
DECIDER = re.compile(r"\b(?:operator|maintainer|decided|approved|agreed)\b|(?<![\w.])@[A-Za-z0-9-]+\b", re.I)
ISSUES = [re.compile(r"(?<![\w&/$])#\d+\b"), re.compile(r"\b[\w.-]+/[\w.-]+#\d+"),
          re.compile(r"\b(?:issue|PR|ticket)\s+#?\d+\b", re.I)]
POINTER = re.compile(rf"^(?:See|History:)\s+{REF}(?:(?:,\s*|\s+and\s+){REF})*\.?$")
MARKER = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+|//+\s*|/?\*+\s*|#+\s*)?")
HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s|$)")
LINK_TARGET = re.compile(r"\]\([^)]*\)|^\s*\[[^\]]+\]:\s*\S+")
HTML_COMMENT = re.compile(r"<!--.*?-->")
HASH_COMMENT = re.compile(r"(?:^|\s)#(?!!)(.*)$")
STATUS = re.compile(r"^\s*(?:\*\*)?Status(?:\*\*)?:", re.I)

SPARED = ("plugins/", "tests/fixtures/", "docs/agents/", "evals/")
LEDGER = "docs/rulebook/approved-rules.md"
HASH_FILES = (".yml", ".yaml", ".toml", ".sh")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", *args], capture_output=True, text=True)


def note_in(text: str) -> str | None:
    if WHO.search(text):
        return "who decided"
    if DATE.search(text) and DECIDER.search(text):
        return "a dated decision"
    if any(pattern.search(text) for pattern in ISSUES):
        return "an issue number"
    return None


def is_pointer(text: str) -> bool:
    return bool(POINTER.match(MARKER.sub("", text, count=1).strip()))


def markdown(path: str, lines: list[str]) -> tuple[dict[int, str], dict[int, int]]:
    """Prose by line number, and the section each line sits in."""
    prose, sections, fence, in_comment, section = {}, {}, None, False, 0
    adr = path.startswith("docs/adr/")
    for number, line in enumerate(lines, 1):
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
        if HEADING.match(line):
            section += 1
            continue
        text = HTML_COMMENT.sub("", line)
        if in_comment:
            if "-->" not in text:
                continue
            text, in_comment = text.split("-->", 1)[1], False
        if "<!--" in text:
            text, in_comment = text.split("<!--", 1)[0], True
        if line.lstrip().startswith("|") and (path == LEDGER or adr):
            continue
        if STATUS.match(line) and (adr or path == "PRINCIPLES.md"):
            continue
        prose[number] = LINK_TARGET.sub("", CODE_SPAN.sub("``", text))
        sections[number] = section
    return prose, sections


def python(source: str) -> tuple[dict[int, str], set[int]]:
    """Comment and docstring text by line number, and the lines of the module header."""
    found: dict[int, str] = {}
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                found[token.start[0]] = token.string.lstrip("#")
        tree = ast.parse(source)
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return found, set()
    lines = source.splitlines()
    header: set[int] = set()
    for node in [tree, *ast.walk(tree)]:
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            span = range(first.lineno, first.end_lineno + 1)
            found.update({n: lines[n - 1].replace('"""', "").replace("'''", "") for n in span})
            if node is tree:
                header.update(span)
    if not header:
        header = leading(lines, lambda line: line.lstrip().startswith("#"))
    return found, header


def javascript(lines: list[str]) -> dict[int, str]:
    found, block = {}, False
    for number, line in enumerate(lines, 1):
        text, quote, i = [], None, 0
        while i < len(line):
            pair = line[i:i + 2]
            if block:
                if pair == "*/":
                    block, i = False, i + 2
                    continue
                text.append(line[i])
            elif quote:
                quote = None if line[i] == quote and line[i - 1] != "\\" else quote
            elif pair == "//":
                text.append(line[i + 2:])
                break
            elif pair == "/*":
                block, i = True, i + 2
                continue
            elif line[i] in "'\"`":
                quote = line[i]
            i += 1
        if text:
            found[number] = "".join(text)
    return found


def hashed(lines: list[str]) -> dict[int, str]:
    return {n: m.group(1) for n, line in enumerate(lines, 1) if (m := HASH_COMMENT.search(line))}


def leading(lines: list[str], is_comment) -> set[int]:
    header = set()
    for number, line in enumerate(lines, 1):
        if line.strip() and not is_comment(line):
            break
        header.add(number)
    return header


def file_problems(root: Path, path: str, added: set[int]) -> list[str]:
    name = Path(path).name
    if path.startswith(SPARED) or (name.startswith("CHANGELOG") and name.endswith(".md")):
        return []
    try:
        source = (root / path).read_text()
    except (OSError, UnicodeDecodeError):
        return []
    lines = source.splitlines()
    groups: dict[int, int] = {}
    if name.endswith(".md"):
        text, groups = markdown(path, lines)
    elif name.endswith(".py"):
        text, header = python(source)
        groups = {n: 0 for n in header}
    elif name.endswith((".js", ".mjs")):
        text = javascript(lines)
        groups = {n: 0 for n in leading(lines, lambda line: line.lstrip().startswith(("//", "/*", "*")))}
    elif name.endswith(HASH_FILES) or name == "Makefile":
        text = hashed(lines)
        groups = {n: 0 for n in leading(lines, lambda line: line.lstrip().startswith("#"))}
    else:
        return []
    found, pointed = [], set()
    for number in sorted(text):
        if is_pointer(text[number]) and number in groups:
            first = groups[number] not in pointed
            pointed.add(groups[number])
            if number in added and not first:
                found.append(f"{path}:{number}: a second pointer here; keep one per section: {lines[number - 1].strip()[:80]}")
            continue
        what = note_in(text[number]) if number in added else None
        if what:
            found.append(f"{path}:{number}: {what}; say what and why, the history is in git: {lines[number - 1].strip()[:80]}")
    return found


def added_lines(root: Path, base: str) -> dict[str, set[int]]:
    added: dict[str, set[int]] = {}
    fork = git(root, "merge-base", base, "HEAD").stdout.strip()
    diff = git(root, "diff", "-U0", "--find-renames", "--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/",
               fork, "--").stdout
    path = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@") and path:
            start, _, count = re.match(r"@@ -\S+ \+(\d+)(,(\d+))?", line).groups()
            first, length = int(start), int(count) if count is not None else 1
            added.setdefault(path, set()).update(range(first, first + length))
    for path in git(root, "ls-files", "-o", "--exclude-standard").stdout.splitlines():
        lines = (root / path).read_text(errors="replace").splitlines() if (root / path).is_file() else []
        added[path] = set(range(1, len(lines) + 1))
    return added


def problems(root: Path, base: str = "origin/main") -> list[str]:
    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != root.resolve():
        return [f"{root}: not the root of a git repository; the check reads the lines a change adds"]
    if git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
        return [f"{root}: cannot resolve {base}; run `git fetch origin main`"]
    return [p for path, lines in sorted(added_lines(root, base).items()) for p in file_problems(root, path, lines)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."), *sys.argv[2:3])
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
