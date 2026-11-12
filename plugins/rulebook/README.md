# rulebook

Generic engineering rules for coding agents. The agent that writes the code and the agent that reviews it read the same
file. Project-specific values (commands, paths, module names) stay in each project's own `AGENTS.md`.

Each domain is one skill: `testing`, `code`, `agent`, `migrations`, `obs`, `planning` and `meta`. A skill is moving to
one short procedure in `SKILL.md`, with a file beside it only for what some runs need, such as one stack's traps
(`testing` is the first). From a project's `AGENTS.md`, point at a skill or its file by name, never by path, because
the plugin's install folder differs per machine and per version:

```text
Tests here call the model: use the `testing` skill (rulebook plugin) and read its `model-calls` notes.
```

## Install

```bash
# Claude Code
claude plugin marketplace add chiyanram/skills
claude plugin install rulebook@chiyanram

# Other agent tools
npx skills add chiyanram/skills
```

The repo is private. See the [root README](../../README.md#quick-start) for credentials and the worker-container setup.

## Two shapes, for now

`testing` is a short procedure: `SKILL.md` holds the steps and the rules, each with its reason, and Good / Bad pairs
only where a model's default is wrong. The other skills still have a router `SKILL.md` and references with five
sections (Rules, When X use Y, Good / Bad, Decided edges, Review checks), described in
[reference-format.md](../../docs/rulebook/reference-format.md), until each is rewritten.

## Skills

A router skill's `SKILL.md` lists its references, their rule IDs and when to read each one. `make index` builds that
list from the references, and `make lint` fails when it is stale.

| skill | read it when you |
|---|---|
| [crq](skills/crq/SKILL.md) | take a change from request to merge, or run one phase: lanes, spec, design, build, review, pull request, retro |
| [testing](skills/testing/SKILL.md) | choose, write or review a test: where it goes, which cases, junk tests, mutation testing; Spock, ITs, Playwright and model calls in its notes |
| [code](skills/code/SKILL.md) | write or review production code: Java, Spring, types, errors, services, API design, security, concurrency, persistence, scheduled jobs, Redis, Angular |
| [agent](skills/agent/SKILL.md) | write or review code that calls a model or runs an agent: adapter, tool loop, context, guards, GenAI spans, evals, budgets |
| [deslop](skills/deslop/SKILL.md) | clean up an implemented branch's diff, behaviour-neutral, before review |
| [migrations](skills/migrations/SKILL.md) | write or review a database migration |
| [obs](skills/obs/SKILL.md) | write or review a log call, a metric or a trace |
| [planning](skills/planning/SKILL.md) | write or review a spec, its acceptance criteria, a design or a diagram |
| [meta](skills/meta/SKILL.md) | write or review a reference of this rulebook |

## Where a rule comes from

Each rule has a source. A rule goes in only after the operator says yes; the
[ledger](../../docs/rulebook/approved-rules.md) lists every approved rule with its reason and source. How to propose one:
[CONTRIBUTING.md](../../CONTRIBUTING.md).
