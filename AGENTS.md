# AGENTS.md

This repo ships two Claude Code plugins: `rulebook` from `plugins/rulebook/`, and `toolbox`, typed-only
tools, from `plugins/toolbox/`. Everything else keeps them correct and releases them. People start at `README.md`;
`CONTRIBUTING.md` holds the procedures.

Codebase health: each change leaves the modules it touches no worse than it found them. If the change would make one
worse, say so in the design and propose the refactor as its own ticket. We care about the next change being easy, not
only this one working.

## Check

Run all three before you push. CI runs `make lint` and `make test` on every pull request and on push to `main`.

```bash
make index  # rebuild each skill router's reference table from its references
make lint   # every scripts/check_*.py, then `claude plugin validate --strict`
make test   # python3 -m unittest: each check against its planted fixtures, the index builder, the release config
```

`make lint` needs the Claude Code CLI (`claude`). `make test` needs `npm ci` first.

## MUSTs

- Add a rule to a reference only with the operator's explicit yes and a row in `docs/rulebook/approved-rules.md`,
  because an unapproved rule reaches every project that installs the plugin.
- Keep provenance out of `plugins/`: no citation, URL, date, credit or evidence note outside code, because the agent
  needs the rule and the ledger keeps the source. `check_provenance.py` fails it. A copied toolbox skill's source and
  licence go only in `plugins/toolbox/THIRD_PARTY_NOTICES.md`.
- Make every toolbox skill typed-only (`disable-model-invocation: true`), with no push or merge, because a person
  chooses when a tool runs. `check_toolbox.py` fails it.
- Keep `plugins/` generic: no project names, paths or business terms, because every project installs the same files.
- Never edit a router table, a `version` or a `CHANGELOG*.md` by hand, because `make index` and the release write them.
- Read Sonar rules for calibration only. Never copy their text, because their licence does not permit it.

## Where things go

```text
plugins/rulebook/skills/<domain>/SKILL.md        router; its table is built by make index
plugins/rulebook/skills/<domain>/references/     one file per topic, five sections
plugins/toolbox/skills/<tool>/SKILL.md           a typed-only tool, copied as written or with the operator's changes
plugins/toolbox/THIRD_PARTY_NOTICES.md           each tool's source, commit, licence and changes
docs/rulebook/approved-rules.md                  the ledger: one row per approved rule
docs/rulebook/reference-format.md                the template every reference follows
docs/agents/                                     issue tracker, labels, domain-doc conventions
scripts/check_<name>.py + tests/fixtures/<name>/ one check and its planted fixtures
evals/routing/<router>.json                      requests each router must pick, and near misses it must not
evals/skills/<skill>/                            a skill's tasks, run full and shorter, scored by its review checks
docs/DESIGN.md                                   the design on one page: rules, the crq process, role cards
```

## Pointers

- The principles behind the plugins, K1–K9: `PRINCIPLES.md`.
- A new rule, reference or check: `CONTRIBUTING.md`.
- Commit and PR format: `CONTRIBUTING.md#commit-messages`. Commit types and what each releases:
  `CONTRIBUTING.md#releases`.
- Issues: GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`,
  `docs/agents/triage-labels.md` and `docs/agents/domain.md`.
