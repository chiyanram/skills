# AGENTS.md

This repo is the generic rulebook: one Claude Code plugin, `rulebook`, in `plugins/rulebook/`. Only that folder ships.
Everything else is the design work behind it. People start at `README.md` and `CONTRIBUTING.md`.

## Check

Run both before you push. CI runs the same two targets on every pull request and on push to `main`.

```bash
make lint   # skill frontmatter, one version, links, size budgets, packaging, README index, `claude plugin validate --strict`
make test   # python3 -m unittest: each check against its planted fixtures, and each review/ builder
```

`make lint` needs the Claude Code CLI (`claude`). The checks are Python 3 stdlib in `scripts/`, one file per check.

## Add a check

1. Plant a bad fixture under `tests/fixtures/<check>/`, or write it to a temp dir when it is a `SKILL.md`.
2. Add a test that expects the check to fail on it. Watch it fail.
3. Write `scripts/check_<name>.py` and add it to `make lint`.
4. Add a row for it to the checks table in `CONTRIBUTING.md`.

`scripts/repo_files.py` skips `tests/fixtures/`, so a planted failure never breaks `make lint`.

## Add a reference

No rule goes in without the operator's explicit yes and a row in `research/19-approved-rules.md`. Follow
`research/00-reference-format.md`, then link the new file from the table in `plugins/rulebook/README.md`;
`check_index.py` fails until you do.

## Releases

semantic-release cuts every release from the commits on `main` (`release.config.mjs`). Never bump a `version` or edit
`CHANGELOG.md` by hand. A change to what ships is `feat(<domain>)` or `fix(<domain>)`; design work is scoped
`research`, `review` or `repo` and never releases. Table: `CONTRIBUTING.md#releases`.

## Issue tracker

GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`.

Triage labels: `docs/agents/triage-labels.md`. Domain docs: `docs/agents/domain.md`.
