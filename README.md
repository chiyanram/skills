# skills

[![ci](https://github.com/chiyanram/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/chiyanram/skills/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

One shared rulebook for coding agents: the agent that writes the code and the agent that reviews it read the same rules.

## What it is

`skills` ships the Claude Code plugin [`rulebook`](plugins/rulebook/). It holds the engineering rules that every
project shares: tests, code, agents, migrations, observability and planning. Each rule has a reason and an approved
source. A second plugin, [`toolbox`](plugins/toolbox/), holds tools a person types, copied from other skill repos with
their licence notices.

- **One file, two readers.** The writer follows the rules. The reviewer checks the same rules.
- **Load only what the task needs.** Each domain has a router, so an agent opens one reference, not the whole book.
- **Project values stay in the project.** Commands, paths and module names go in that project's own `AGENTS.md`.

It is for teams that run coding agents (Claude Code, Codex, Cursor) and want one standard across their repos. The
current version is in the [changelog](CHANGELOG.md).

## Quick start

The repo is private. Give git your GitHub credentials first.

```bash
gh auth setup-git
claude plugin marketplace add chiyanram/skills
claude plugin install rulebook@chiyanram
```

For other agent tools:

```bash
npx skills add chiyanram/skills
```

Update with `claude plugin marketplace update chiyanram`. To put the plugin in a worker container, add it to the
managed settings:

```json
"extraKnownMarketplaces": { "chiyanram": { "source": { "source": "github", "repo": "chiyanram/skills" } } },
"enabledPlugins": { "rulebook@chiyanram": true }
```

## How it works

```mermaid
flowchart LR
    T["task: write or<br/>review a test"] --> S["skill router<br/>testing/SKILL.md"]
    S -->|"reads only what<br/>the task needs"| R["reference<br/>strategy.md"]
    R --> A["writer follows the Rules,<br/>reviewer runs the Review checks"]
    P["project AGENTS.md<br/>project-only values"] -.-> A
```

Each domain is one skill. Its `SKILL.md` is a router: a table of its references and when to read each. Every
reference has the same five sections, in this order:

| section | holds |
|---|---|
| Rules | one line per rule: an ID, an instruction, and *because* + the failure it prevents |
| When X, use Y | situation → rule → action |
| Good / Bad | example pairs in a neutral domain |
| Decided edges | cases settled once, so nobody argues them again |
| Review checks | what a reviewer checks, each naming its rule ID |

A project points at a reference by skill and name, never by path:

```text
Tests here call the model: use the `testing` skill (rulebook plugin) and read its `llm-tests` reference.
```

## Use

| skill | load it when you |
|---|---|
| [testing](plugins/rulebook/skills/testing/SKILL.md) | choose, write or review a test |
| [code](plugins/rulebook/skills/code/SKILL.md) | write or review production code |
| [agent](plugins/rulebook/skills/agent/SKILL.md) | write or review code that calls a model or runs an agent |
| [deslop](plugins/rulebook/skills/deslop/SKILL.md) | clean up a branch's diff before review |
| [migrations](plugins/rulebook/skills/migrations/SKILL.md) | write or review a database migration |
| [obs](plugins/rulebook/skills/obs/SKILL.md) | write or review a log call, a metric or a trace |
| [planning](plugins/rulebook/skills/planning/SKILL.md) | write or review a spec, a design or a diagram |
| [meta](plugins/rulebook/skills/meta/SKILL.md) | write or review a reference of this rulebook |
| [crq](plugins/rulebook/skills/crq/SKILL.md) | take a change from request to merge, or run one of its phases |

The [plugin README](plugins/rulebook/README.md) has more on each skill.

## Docs

- [CONTRIBUTING.md](CONTRIBUTING.md): set up, add a rule, a reference or a check, and how releases work.
- [AGENTS.md](AGENTS.md): instructions for coding agents that work in this repo.
- [docs/rulebook/approved-rules.md](docs/rulebook/approved-rules.md): every approved rule, with its reason and source.

## License

[MIT](LICENSE)
