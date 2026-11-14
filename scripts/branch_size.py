"""The size of a branch against PD9: added lines and changed files, split into code, tests, evals and docs.

Usage: python3 scripts/branch_size.py <base> [<head>]

It counts against `git merge-base <base> <head>`. Lines inside a generated block of a `*.md` file do not count: from
a line holding `<!-- index:` or `<!-- lanes-<name>:` to its `<!-- /index -->` or `<!-- /lanes-<name> -->`. A file
counts as changed when it has an added line outside a block, or when it is deleted or renamed. It is a report, not a
gate, so it exits 0 whatever the size.
"""
import fnmatch
import re
import subprocess
import sys

PD9_LINES = 400
PD9_FILES = 15
BUCKETS = ("code", "tests", "evals", "docs")
OPENING = re.compile(r"<!-- (index|lanes-[\w-]+):")
HUNK = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def blocks(text: str) -> list[range]:
    """The line numbers, counted from 1, of each generated block, both marker lines included."""
    found = []
    lines = text.splitlines()
    start = name = None
    for number, line in enumerate(lines, 1):
        if start is not None and f"<!-- /{name} -->" in line:
            found.append(range(start, number + 1))
            start = name = None
        elif start is None and (opening := OPENING.search(line)):
            start, name = number, opening.group(1)
    return found


def bucket(path: str) -> str:
    if path.startswith("scripts/"):
        return "code"
    if path.startswith("tests/"):
        return "tests"
    if fnmatch.fnmatch(path, "plugins/*/evals/*"):
        return "evals"
    return "docs"


def counted(added: list[int], ranges: list[range]) -> int:
    return sum(1 for line in added if not any(line in r for r in ranges))


def git(*args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True,
                          check=True).stdout


def changes(base: str, head: str) -> list[dict]:
    """One entry per file: its path, whether it was deleted or renamed, and the post-image numbers of added lines."""
    diff = git("diff", "--unified=0", "-M", "--no-color", "--no-ext-diff", "--no-textconv", base, head)
    found, current, old_left, new_left, line = [], None, 0, 0, 0
    for text in diff.splitlines():
        if old_left or new_left:
            if text.startswith("+"):
                current["added"].append(line)
                line += 1
                new_left -= 1
            elif text.startswith("-"):
                old_left -= 1
        elif text.startswith("diff --git "):
            current = {"path": text.rsplit(" b/", 1)[-1], "moved": False, "added": []}
            found.append(current)
        elif text.startswith(("deleted file mode", "rename from ")):
            current["moved"] = True
        elif text.startswith("rename to "):
            current["path"] = text[len("rename to "):]
        elif text.startswith("--- a/") and current["moved"]:
            current["path"] = text[len("--- a/"):]
        elif text.startswith("+++ b/"):
            current["path"] = text[len("+++ b/"):]
        elif hunk := HUNK.match(text):
            old_left = int(hunk.group(1) or 1)
            line, new_left = int(hunk.group(2)), int(hunk.group(3) or 1)
    return found


def measure(base: str, head: str) -> dict[str, list[int]]:
    """Per bucket, [lines, files]."""
    totals = {name: [0, 0] for name in BUCKETS}
    for change in changes(git("merge-base", base, head).strip(), head):
        ranges = blocks(git("show", f"{head}:{change['path']}")) if change["path"].endswith(".md") \
            and change["added"] else []
        lines = counted(change["added"], ranges)
        if lines or change["moved"]:
            totals[bucket(change["path"])][0] += lines
            totals[bucket(change["path"])][1] += 1
    return totals


def report(totals: dict[str, list[int]]) -> str:
    rows = [f"{name:<6}{lines:>5} lines {files:>3} files" for name, (lines, files) in totals.items()]
    lines, files = (sum(column) for column in zip(*totals.values()))
    over = " over PD9" if lines > PD9_LINES or files > PD9_FILES else ""
    rows.append(f"{'total':<6}{lines:>5} lines {files:>3} files (PD9: {PD9_LINES} lines, {PD9_FILES} files){over}")
    return "\n".join(rows)


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    print(report(measure(argv[1], argv[2] if len(argv) == 3 else "HEAD")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
