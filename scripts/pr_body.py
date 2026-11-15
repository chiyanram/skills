"""The one PR-description rule. CI's pr-body job calls it on a pull request that is ready for review.

The squash merge makes the description the commit body on main, where it cannot be edited, so the description must
hold the template's lines, filled in:

- the first line is "Why: " and the reason for the change;
- a "Breaking change:", a "Rollback:" and a "Where to look:" line, each with its answer;
- no <placeholder> of .github/pull_request_template.md is left;
- every checklist item is ticked.

    gh pr view <N> --json body -q .body | python3 scripts/pr_body.py

chiyanram/agent-factory runs the same rule as scripts/check-pr-body.ts.
"""
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / ".github" / "pull_request_template.md"
LABELS = ("Breaking change:", "Rollback:", "Where to look:")
PLACEHOLDER = re.compile(r"<[^<>\n]+>")
UNTICKED = re.compile(r"^\s*[-*] \[ \]")


def placeholders(template: str) -> list[str]:
    """Each <placeholder> the template holds, once, in order."""
    return list(dict.fromkeys(PLACEHOLDER.findall(template)))


def problems(body: str, template: str) -> list[str]:
    lines = body.replace("\r\n", "\n").split("\n")
    found = []
    first = next((line.strip() for line in lines if line.strip()), "")
    if not re.match(r"Why: \S", first):
        found.append('the first line must be "Why: " and the reason for the change, in one sentence')
    for label in LABELS:
        if not any(line.startswith(label) and line[len(label):].strip() for line in lines):
            found.append(f'the "{label}" line is missing or has no answer')
    found += [f"the placeholder {p} is still there: replace it" for p in placeholders(template) if p in body]
    found += [f"line {i} is not ticked: answer it, then tick it: {line.strip()}"
              for i, line in enumerate(lines, 1) if UNTICKED.match(line)]
    return found


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("usage: gh pr view <N> --json body -q .body | python3 scripts/pr_body.py", file=sys.stderr)
        sys.exit(2)
    errors = problems(sys.stdin.read(), TEMPLATE.read_text())
    for error in errors:
        print(f"::error::{error}")
    if errors:
        print(f"pr_body: {len(errors)} problem(s); the description becomes the commit body on main, "
              f"so fill in .github/pull_request_template.md. See CONTRIBUTING.md#commit-messages.")
        sys.exit(1)
