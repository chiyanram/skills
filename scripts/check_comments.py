"""Code says what it does; a comment is allowed only where code cannot say it.

Kept: the module header (a Python docstring is not a comment; a leading comment block is the header), a line with an
http(s) link to a rule we cannot change, and a tool directive (`#!`, `# noqa`, `# type:`, `biome-ignore`, `@ts-` and
the like). Every other comment line in a tracked `.py`, `.mjs` or `.js` file outside `tests/fixtures/` counts against
`scripts/comment-baseline.json`, per file. A count above its baseline fails, so no file gains a comment. A count below
it fails until `--shrink` writes it, so a deleted comment does not come back. A file not in the baseline holds none.
`.claude/commands/delete-comment.md` sorts and deletes the rest.

    python3 scripts/check_comments.py [ROOT]            check (make lint)
    python3 scripts/check_comments.py --shrink [ROOT]   write the lower counts; never raises one
"""
import io
import json
import re
import sys
import tokenize
from pathlib import Path

from check_history import javascript, leading
from repo_files import files

BASELINE = Path("scripts/comment-baseline.json")
LINK = re.compile(r"https?://")
PY_DIRECTIVE = re.compile(r"^#!|^#\s*(?:noqa|type:|pragma|fmt:|pylint:|ruff:|mypy:)")
JS_DIRECTIVE = re.compile(r"^\s*(?:biome-ignore|eslint-|@ts-|prettier-ignore|istanbul\s|c8\s|@vitest-)")
JS_COMMENT_LINE = re.compile(r"^\s*(?://|/\*|\*)")


def python_lines(source: str) -> list[int]:
    lines = source.splitlines()
    header = leading(lines, lambda line: line.lstrip().startswith("#"))
    found = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type != tokenize.COMMENT:
                continue
            number, text = token.start[0], token.string
            if number not in header and not PY_DIRECTIVE.search(text) and not LINK.search(text):
                found.append(number)
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return []
    return found


def javascript_lines(source: str) -> list[int]:
    lines = source.splitlines()
    header = leading(lines, JS_COMMENT_LINE.match)
    return [n for n, text in javascript(lines).items()
            if n not in header and not JS_DIRECTIVE.match(text) and not LINK.search(text)]


def banned(path: Path) -> list[int]:
    source = path.read_text(encoding="utf-8")
    return python_lines(source) if path.suffix == ".py" else javascript_lines(source)


def counts(root: Path) -> dict[str, list[int]]:
    found = {}
    for glob in ("*.py", "*.mjs", "*.js"):
        for path in files(root, glob):
            if numbers := banned(path):
                found[path.relative_to(root).as_posix()] = numbers
    return found


def read_baseline(root: Path) -> dict[str, int]:
    path = root / BASELINE
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def problems(root: Path) -> list[str]:
    found, baseline = counts(root), read_baseline(root)
    out = []
    for name, numbers in sorted(found.items()):
        if len(numbers) > baseline.get(name, 0):
            lines = ", ".join(str(n) for n in numbers)
            out.append(f"{name}: {len(numbers)} comment line(s), baseline {baseline.get(name, 0)} (lines {lines}); "
                       "say it in code or the module header, or run /delete-comment")
    for name, allowed in sorted(baseline.items()):
        if len(found.get(name, [])) < allowed:
            out.append(f"{name}: {len(found.get(name, []))} comment line(s), baseline {allowed}; "
                       "run `python3 scripts/check_comments.py --shrink` so the deleted comments stay deleted")
    return out


def shrink(root: Path) -> None:
    found, baseline = counts(root), read_baseline(root)
    lower = {name: min(len(found.get(name, [])), allowed) for name, allowed in baseline.items()}
    path = root / BASELINE
    path.write_text(json.dumps({k: v for k, v in sorted(lower.items()) if v}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    args = sys.argv[1:]
    target = Path(next((a for a in args if a != "--shrink"), "."))
    if "--shrink" in args:
        shrink(target)
    found = problems(target)
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
