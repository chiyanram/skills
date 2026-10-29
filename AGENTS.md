# AGENTS.md

This repo is the generic rulebook: one Claude Code plugin, `rulebook`, in `plugins/rulebook/`. Only that folder ships.
Everything else is the design work behind it.

## Check

Run both before you push. CI runs the same two targets on every pull request and on push to `main`.

```bash
make lint   # skill frontmatter, one version, links, size budgets, packaging, `claude plugin validate --strict`
make test   # python3 -m unittest: each check against its planted fixtures, and each review/ builder
```

`make lint` needs the Claude Code CLI (`claude`). The checks are Python 3 stdlib in `scripts/`, one file per check.

## Add a check

1. Plant a bad fixture under `tests/fixtures/<check>/`, or write it to a temp dir when it is a `SKILL.md`.
2. Add a test that expects the check to fail on it. Watch it fail.
3. Write `scripts/check_<name>.py` and add it to `make lint`.

`scripts/repo_files.py` skips `tests/fixtures/`, so a planted failure never breaks `make lint`.

## Issue tracker

GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`.

Triage labels: `docs/agents/triage-labels.md`. Domain docs: `docs/agents/domain.md`.
