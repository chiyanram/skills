# skills — the generic rulebook

This repo holds the generic engineering rules that every project shares. They ship as skills in one plugin,
[`rulebook`](plugins/rulebook/). Claude Code reaches them as a plugin. Other agent tools reach them with
`npx skills add`. Rules that belong to one project stay in that project's own `AGENTS.md` files.

## Install

The repo is private, so git needs credentials first. A `GH_TOKEN` alone is not enough; it has to go through a
credential helper.

**Claude Code**

```bash
gh auth setup-git
claude plugin marketplace add chiyanram/skills
claude plugin install rulebook@chiyanram
```

Update with `claude plugin marketplace update chiyanram`. Auto-update is off for third-party marketplaces unless you
turn it on.

**Other agent tools**

```bash
npx skills add chiyanram/skills
```

**Worker container.** Add the marketplace and the plugin to the managed settings:

```json
"extraKnownMarketplaces": { "chiyanram": { "source": { "source": "github", "repo": "chiyanram/skills" } } },
"enabledPlugins": { "rulebook@chiyanram": true }
```

`bake-plugins.sh` reads the BuildKit secret `skills_token` for the clone. The whole repo is cloned, but only
`plugins/rulebook/` is copied into the plugin cache.

## Layout

| path | what it holds |
|---|---|
| [`plugins/rulebook/`](plugins/rulebook/) | the plugin: the only folder that ships |
| [`scripts/`](scripts/), [`tests/`](tests/) | the checks behind `make lint`, and their tests |
| [`research/`](research/), [`review/`](review/), [`issues/`](issues/), [`p1/`](p1/), [`refs/`](refs/) | the design work behind the rules |

Every approved rule is in [research/19-approved-rules.md](research/19-approved-rules.md). Issues are tracked in GitHub
issues.

## Contribute

Read [AGENTS.md](AGENTS.md). Run `make lint` and `make test` before you push.
