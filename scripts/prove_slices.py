"""Run each proving command in a spec's Slices table on a base commit, and print what it prints today.

Usage: python3 scripts/prove_slices.py <spec.md> [<base>]   (base defaults to origin/main)

The spec names a proving command per slice. This script finds the table whose header has a `proving command`
column, takes each backtick span in that cell, and runs the spans that are commands in a temporary git worktree at
the base. It prints each command before it runs it, then its exit code and its last output line. When the cell says
`prints N (M today)` after a command, the script compares the last line with M.

The commands come from a spec the operator wrote, and run with the shell. The worktree is a working folder, not a
sandbox. It skips `make test`, `make lint` and `make index` (CI runs them, and the worktree has no untracked
dependencies), and any text after `Manual:`.

Exit 0 when nothing is flagged, 1 when a command is flagged, 2 when the spec or the base cannot be used.
"""
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT = 60
DEFAULT_BASE = "origin/main"
HEADER = "proving command"
SKIP = re.compile(r"\bmake\s+(test|lint|index)\b")
SPAN = re.compile(r"`([^`]+)`")
CLAIM = re.compile(r"^\s*prints\s+(\S+)\s+\((\S+)\s+today\)")
MANUAL = "Manual:"


def split_row(line: str) -> list[str]:
    """Split a table row on each pipe that is not escaped and not inside a backtick span; strip each cell."""
    cells, current, in_code, i = [], [], False, 0
    while i < len(line):
        char = line[i]
        if char == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            current.append("\\|")
            i += 2
            continue
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append("".join(current))
            current = []
        else:
            current.append(char)
        i += 1
    cells.append("".join(current))
    stripped = line.strip()
    if stripped.startswith("|"):
        cells = cells[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def slices(markdown: str) -> list[tuple[str, str]]:
    """Each (slice, proving cell) of every table whose header has a column containing `proving command`."""
    found, column, in_table = [], None, False
    for line in markdown.splitlines():
        if not line.lstrip().startswith("|"):
            column, in_table = None, False
            continue
        cells = split_row(line)
        if not in_table:
            in_table = True
            column = next((i for i, cell in enumerate(cells) if HEADER in cell.lower()), None)
            continue
        if column is None or all(set(cell) <= set("-: ") for cell in cells):
            continue
        if column < len(cells):
            found.append((cells[0], cells[column]))
    return found


def _is_command(span: str) -> bool:
    try:
        words = shlex.split(span)
    except ValueError:
        words = span.split()
    if not words or shutil.which(words[0]) is None:
        return False
    return not all(word.startswith("-") for word in words[1:])


def spans(cell: str) -> list[tuple[str, str]]:
    """Each piece of the cell as (text, verdict): verdict is `run`, `not a command` or `skip (<why>)`.

    A span's `\\|` becomes `|`. The text after `Manual:` is one skipped piece.
    """
    body, manual, after = cell.partition(MANUAL)
    found = []
    for match in SPAN.finditer(body):
        text = match.group(1).replace("\\|", "|")
        if SKIP.search(text):
            found.append((text, "skip (CI runs it)"))
        elif _is_command(text):
            found.append((text, "run"))
        else:
            found.append((text, "not a command"))
    if manual:
        found.append(((manual + after).strip(), "skip (manual)"))
    return found


def commands(cell: str) -> list[str]:
    """The backtick spans of a proving cell that run, with `\\|` unescaped."""
    return [text for text, verdict in spans(cell) if verdict == "run"]


def claim(cell: str, command: str) -> tuple[str, str] | None:
    """The (target, today) of `prints N (M today)` written right after the command's span, or None."""
    for match in SPAN.finditer(cell):
        if match.group(1).replace("\\|", "|") == command:
            found = CLAIM.match(cell[match.end():])
            return (found.group(1), found.group(2)) if found else None
    return None


def judge(claimed: tuple[str, str] | None, code: int | None, last_line: str) -> str | None:
    """The flag for one run, or None when the run matches what the spec says."""
    if code is None:
        return f"timed out after {TIMEOUT} s"
    if claimed is None:
        return "passes on base" if code == 0 else None
    target, today = claimed
    if last_line == target:
        return f"already prints the target {target}"
    if last_line != today:
        return f"today value differs: prints {last_line!r}, the spec says {today}"
    return None


def run(command: str, worktree: Path, timeout: float = TIMEOUT) -> tuple[int | None, str]:
    """Run one command in the worktree with the shell; return (exit code, last output line). Code None: timed out."""
    process = subprocess.Popen(command, shell=True, cwd=worktree, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               start_new_session=True)
    try:
        output, _ = process.communicate(timeout=timeout)
        code = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        output, _ = process.communicate()
        code = None
    lines = [line for line in (output or "").splitlines() if line.strip()]
    return code, lines[-1].strip() if lines else ""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def prove(rows: list[tuple[str, str]], worktree: Path, out) -> int:
    flagged = 0
    for name, cell in rows:
        print(name, file=out)
        for text, verdict in spans(cell):
            if verdict != "run":
                print(f"  {verdict}: {text}", file=out)
                continue
            print(f"  $ {text}", file=out, flush=True)
            code, last_line = run(text, worktree)
            print(f"    exit {'timeout' if code is None else code} · last line: {last_line}", file=out)
            flag = judge(claim(cell, text), code, last_line)
            if flag:
                flagged += 1
                print(f"    FLAG: {flag}", file=out)
    return flagged


def main(argv: list[str], repo: Path | None = None, out=sys.stdout) -> int:
    if len(argv) not in (1, 2):
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    repo = repo or Path.cwd()
    spec = Path(argv[0]) if Path(argv[0]).is_absolute() else repo / argv[0]
    base = argv[1] if len(argv) == 2 else DEFAULT_BASE
    try:
        text = spec.read_text()
    except (OSError, UnicodeDecodeError) as error:
        print(f"{argv[0]}: cannot read ({error})", file=sys.stderr)
        return 2
    rows = slices(text)
    if not rows:
        print(f"{argv[0]}: no table with a `{HEADER}` column", file=sys.stderr)
        return 2
    _git(repo, "worktree", "prune")
    holder = Path(tempfile.mkdtemp(prefix="prove-slices-"))
    worktree = holder / "base"
    added = False
    try:
        result = _git(repo, "worktree", "add", "--detach", str(worktree), base)
        if result.returncode != 0:
            print(f"git worktree add {base} failed (exit {result.returncode}): {result.stderr.strip()}",
                  file=sys.stderr)
            return 2
        added = True
        print(f"base {base} in {worktree}", file=out)
        return 1 if prove(rows, worktree, out) else 0
    finally:
        if added:
            removed = _git(repo, "worktree", "remove", "--force", str(worktree))
            if removed.returncode != 0:
                print(f"git worktree remove failed: {removed.stderr.strip()}", file=sys.stderr)
        shutil.rmtree(holder, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
