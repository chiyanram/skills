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

`make lint` fails a break of each of these:

- Keep provenance out of `plugins/`: no citation, URL, date, credit or evidence note outside code; a copied toolbox
  skill's source and licence go only in `plugins/toolbox/THIRD_PARTY_NOTICES.md` (`check_provenance.py`).
- Make every toolbox skill typed-only (`disable-model-invocation: true`), with no push or merge (`check_toolbox.py`).
- Say what and why in the repo's own docs and code comments, never who decided, when or on which issue
  (`check_history.py`).
- Fill in every line of `.github/pull_request_template.md`, with no `<placeholder>`, because the squash merge makes
  it the commit on `main` (`pr_body.py`).

No check can enforce these:

- Add or change a rule only in a pull request the operator merges, with its two sources in the pull request body,
  because an unapproved rule reaches every project that installs the plugin.
- Keep `plugins/` generic: no project names, paths or business terms, because every project installs the same files.
- Never edit a router table, a `version` or a `CHANGELOG*.md` by hand, because `make index` and the release write them.
- Read Sonar rules for calibration only. Never copy their text, because their licence does not permit it.
- Put a new role, phase or field in a new format version, and say in the pull request what a tool must learn to read
  it, because a tool on the old version keeps working only if the old file stays.
- Start a new check, role or outside skill as a typed-only toolbox skill, and move it into the crq process only after
  measured use, with a person deciding each step up, because a step nobody has run by hand reaches every project's
  automatic flow unproven.
- Make each branch in its own worktree from the latest `origin/main`, never in the main checkout:
  `git fetch origin main && git worktree add .claude/worktrees/<slug> -b <type>/<issue>-<slug> origin/main`.
  Update it with `git rebase origin/main`, never a merge, and push with `git push --force-with-lease`; never
  force-push without a lease, onto another person's branch, or onto `main`. A cloud session's own fresh clone, on
  the branch it was given, counts as its worktree.

## Where things go

- A rulebook skill is `plugins/rulebook/skills/<domain>/SKILL.md`: a short procedure with notes files beside it
  (`testing`), or a router over `references/` until it is rewritten.
- A toolbox skill is `plugins/toolbox/skills/<name>/SKILL.md`, typed-only. It is either copied, with its source,
  commit and licence in a `THIRD_PARTY_NOTICES.md` section, or written here and listed under that file's
  `## Written here`.
- Each `scripts/check_<name>.py` ships with planted cases in `tests/fixtures/<name>/`.

## Pointers

- The principles behind the plugins, K1–K8: `PRINCIPLES.md`. A change that departs from one changes `PRINCIPLES.md` first, in its
  own pull request, because skills rewritten against the old principles break them silently.
- A new rule, reference or check: `CONTRIBUTING.md`.
- Commit and PR format: `CONTRIBUTING.md#commit-messages`. Commit types and what each releases:
  `CONTRIBUTING.md#releases`.
- Issues: GitHub issues on `chiyanram/skills`, through `gh`. See `docs/agents/issue-tracker.md`,
  `docs/agents/triage-labels.md` and `docs/agents/domain.md`.
