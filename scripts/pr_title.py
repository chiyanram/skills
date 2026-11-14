"""The one PR-title rule. CI's pr-title job calls it, and so does anyone before `gh pr create`.

A title needs a type, a scope, a lower-case summary and the issue it works on, as (#N) or (owner/repo#N).
Dependabot (scope deps) and the release commit name no issue. `.cz.toml` schema_pattern repeats PATTERN for
commitizen; tests/test_pr_title.py keeps the two equal.
"""
import re
import sys

PATTERN = r'^(feat|fix|perf|revert|docs|style|refactor|test|build|ci|chore)\([a-z0-9-]+\)!?: [^A-Z].*\([^)]*#[0-9]+[^)]*\)'
EXEMPT = r'^[a-z]+\(deps\): |^chore\(release\): '


def is_valid(title: str) -> bool:
    return bool(re.search(PATTERN, title) or re.search(EXEMPT, title))


def error(title: str) -> str:
    return (f"::error::PR title \"{title}\" must be 'type(scope): lower-case summary (#issue)', "
            f"e.g. 'feat(testing): spock rule file (#123)'. See CONTRIBUTING.md#releases.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 scripts/pr_title.py \"<title>\"", file=sys.stderr)
        sys.exit(2)
    if not is_valid(sys.argv[1]):
        print(error(sys.argv[1]))
        sys.exit(1)
