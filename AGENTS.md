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
- Keep history out of the repo's own docs and code comments: say what and why, never who decided, when or on which
  issue, because the ledger, git log and pull requests keep it. `check_history.py` fails an added line.
- Keep `plugins/` generic: no project names, paths or business terms, because every project installs the same files.
- Never edit a router table, a `version` or a `CHANGELOG*.md` by hand, because `make index` and the release write them.
- Read Sonar rules for calibration only. Never copy their text, because their licence does not permit it.
- Never change a format file (`plugins/*/skills/*/process/schema/*-vN.schema.json`) once a release holds it. A change
  is a new `-v(N+1)` file beside it, because a tool pins a release and reads that version's format, and an edit in place
  breaks the tool on its next update. `check_formats.py` fails it.
- Put a new role, phase or field in a new format version, and say in the pull request what a tool must learn to read
  it, because a tool on the old version keeps working only if the old file stays, and its owner learns the change there.
- Start a new check, role or outside skill as a typed-only toolbox skill, and move it into the crq process only after
  measured use, with a person deciding each step up, because a step nobody has run by hand reaches every project's
  automatic flow unproven.

## Where things go

- A rulebook skill is `plugins/rulebook/skills/<domain>/SKILL.md`: a short procedure with notes files beside it
  (`testing`), or a router over `references/` until it is rewritten.
- A toolbox skill is `plugins/toolbox/skills/<name>/SKILL.md`, typed-only. It is either copied, with its source,
  commit and licence in a `THIRD_PARTY_NOTICES.md` section, or written here and listed under that file's
  `## Written here`.
- Each `scripts/check_<name>.py` ships with planted cases in `tests/fixtures/<name>/`.

## Pointers

- The principles behind the plugins, K1–K9: `PRINCIPLES.md`. A change that departs from one changes `PRINCIPLES.md` first, in its
  own pull request, because skills rewritten against the old principles break them silently.
- A new rule, reference or check: `CONTRIBUTING.md`.
- Commit and PR format: `CONTRIBUTING.md#commit-messages`. Commit types and what each releases:
  `CONTRIBUTING.md#releases`.
- Issues: GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`,
  `docs/agents/triage-labels.md` and `docs/agents/domain.md`.
