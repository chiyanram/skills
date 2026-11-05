# AGENTS.md

This repo is the generic rulebook: one Claude Code plugin, `rulebook`, in `plugins/rulebook/`. Only that folder ships.
Everything else keeps it correct and releases it. People start at `README.md`; `ARCHITECTURE.md`, `CONTRIBUTING.md`
and `DEVELOPMENT.md` hold the rest. `docs/archive/` is frozen design history: never edit it or cite it as current.

## Check

Run both before you push. CI runs the same two targets on every pull request and on push to `main`.

```bash
make index  # rebuild each skill router's reference table from its references
make lint   # skill frontmatter, one version, links, size budgets, packaging, router index, skill routers, provenance, `claude plugin validate --strict`
make test   # python3 -m unittest: each check against its planted fixtures, the index builder, the release config
```

`make lint` needs the Claude Code CLI (`claude`). The checks are Python 3 stdlib in `scripts/`, one file per check.

## Add a check

1. Plant a bad fixture under `tests/fixtures/<check>/`, or write it to a temp dir when it is a `SKILL.md`.
2. Add a test that expects the check to fail on it. Watch it fail.
3. Write `scripts/check_<name>.py` and add it to `make lint`.
4. Add a row for it to the checks table in `CONTRIBUTING.md`.

`scripts/repo_files.py` skips `tests/fixtures/` and `docs/archive/`, so a planted failure never breaks `make lint`.

## Add a reference

No rule goes in without the operator's explicit yes and a row in `docs/rulebook/approved-rules.md`. Follow
`docs/rulebook/reference-format.md`, give the file one "Read it when …" sentence above its first section, then run
`make index` to rebuild its domain's `SKILL.md` table. Never edit that table by hand; `check_index.py` fails while it
is stale.

Read Sonar rules for calibration only. Never copy their text into a reference, because Sonar's source-available
licence does not permit vendoring its rule text.

## Releases

semantic-release cuts every release from the commits on `main` (`release.config.mjs`). Never bump a `version` or edit
`CHANGELOG.md` by hand. A change to what ships is `feat(<domain>)` or `fix(<domain>)`; design work is scoped
`research`, `review` or `repo` and never releases. Table: `CONTRIBUTING.md#releases`.

## Issue tracker

GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`.

Triage labels: `docs/agents/triage-labels.md`. Domain docs: `docs/agents/domain.md`.
