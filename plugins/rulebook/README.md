# rulebook

Generic engineering rules for coding agents. The agent that writes the code and the agent that reviews it read the same
file. Project-specific values (commands, paths, module names) stay in each project's own `AGENTS.md`.

Each domain is one skill: `testing`, `playwright`, `code`, `agent`, `migrations`, `obs`, `planning` and `writing`. A skill is moving to
one short procedure in `SKILL.md`, with a file beside it only for what some runs need, such as one stack's traps
(every skill but `crq`). From a project's `AGENTS.md`, point at a skill or its file by name, never by path, because
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

See the [root README](../../README.md#quick-start) for GitHub Copilot CLI and the worker-container setup.

## One shape

Every skill is a short procedure: `SKILL.md` holds the steps and the rules, each with its reason, with notes files
beside it for what only some runs need, and Good / Bad pairs only where a model's default is wrong.

## Skills

| skill | read it when you |
|---|---|
| [crq](skills/crq/SKILL.md) | take a ticket to a pull request: its lane, its stages and stops, its plan card, resuming it, PR readiness |
| [grilling](skills/grilling/SKILL.md) | want a plan, decision or idea questioned in rounds until you share an understanding |
| [testing](skills/testing/SKILL.md) | choose, write or review a test: where it goes, which cases, junk tests, mutation testing; Spock, ITs and model calls in its notes |
| [playwright](skills/playwright/SKILL.md) | write, run, fix or review a Playwright end-to-end or smoke spec: locators, waits, sign-in, fixtures, config, CI, traces, flakes |
| [code](skills/code/SKILL.md) | write, change or review production code: where logic goes, types, errors, names, comments; Java, Spring, JPA, Angular, concurrency, jobs, Redis, HTTP APIs and security in its notes |
| [agent](skills/agent/SKILL.md) | write or review code that calls a model or runs an agent: adapter, tool loop, context, guards, GenAI spans, evals, budgets |
| [skill-feedback](skills/skill-feedback/SKILL.md) | end a session and want its skill failures filed as issues for this repo |
| [migrations](skills/migrations/SKILL.md) | write or review a database migration |
| [obs](skills/obs/SKILL.md) | write or review a log call, a metric or a trace |
| [planning](skills/planning/SKILL.md) | write or review a spec, its acceptance criteria, a design or a diagram |
| [writing](skills/writing/SKILL.md) | write or review a doc, a README, an AGENTS.md, a skill or agent instruction, or a PR body |

## Where a rule comes from

Each rule has two sources. A rule goes in only in a pull request the operator merges, and that pull request names the
sources. How to propose one: [CONTRIBUTING.md](../../CONTRIBUTING.md).
