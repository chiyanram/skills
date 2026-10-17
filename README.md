# skills — one-rulebook working repo

Decisions, research and the approved-rules ledger for redesigning how rules, roles and review work across the laptop
`/crq` pipeline and the agent fleet. Planning only: nothing here is wired into a project yet. Once the design is done,
the result is split into the three projects (agent-platform, aruvii-agent-fleet, agent-fleet).

Start at [map.md](map.md) · requirements in [requirements.md](requirements.md) · whole picture in
[design-overview.md](design-overview.md) · every approved rule in [research/19-approved-rules.md](research/19-approved-rules.md).
Tickets are markdown files in [issues/](issues/) (local wayfinder tracker). Third-party reference repos are not copied —
[refs/README.md](refs/README.md) lists each with its URL and pinned commit.

## Install the plugin

This repo is a Claude Code plugin marketplace (`chiyanram`) with one plugin, `rulebook`: generic skills, references
and the `/crq` workflow (decision G23, [#93](https://github.com/chiyanram/skills/issues/93)). The plugin lives in
[plugins/rulebook/](plugins/rulebook/); `research/`, `review/` and `issues/` are not part of it.

**Laptop.** The repo is private, so git needs credentials first (a `GH_TOKEN` alone is not enough; it has to go
through a credential helper):

```bash
gh auth setup-git
claude plugin marketplace add chiyanram/skills
claude plugin install rulebook@chiyanram
```

Update: `claude plugin marketplace update chiyanram`. Auto-update is off for third-party marketplaces unless you turn it on.

**Worker container** ([agent-fleet#79](https://github.com/chiyanram/agent-fleet/pull/79)). The managed settings
already allow-list this repo; to bake the plugin, add it to `extraKnownMarketplaces` and `enabledPlugins`:

```json
"extraKnownMarketplaces": { "chiyanram": { "source": { "source": "github", "repo": "chiyanram/skills" } } },
"enabledPlugins": { "rulebook@chiyanram": true }
```

`bake-plugins.sh` reads the BuildKit secret `skills_token` for the clone. Note that the whole repo is cloned
(including `research/`), but only `plugins/rulebook/` is copied into the plugin cache.

**Codex.** Codex is not documented to read Claude Code plugins. Until the G20 delivery probe
([#90](https://github.com/chiyanram/skills/issues/90)) shows that `codex exec` sees these skills, treat them as Claude-only.

**Check before pushing:** `make lint` (runs `claude plugin validate --strict` on the marketplace and the plugin).
