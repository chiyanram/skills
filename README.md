# skills

[![ci](https://github.com/chiyanram/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/chiyanram/skills/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

One shared rulebook for coding agents: the agent that writes the code and the agent that reviews it read the same rules.

Two Claude Code plugins:

- [`rulebook`](plugins/rulebook/): skills the model loads by task. `code` and `testing` lean on Java, Spring, JPA,
  Spock and Angular; the others apply to any stack.
- [`toolbox`](plugins/toolbox/): tools a person types, such as `/toolbox:deslop`. Most are copied from other skill
  repos, with their licence notices.

Each skill is a short procedure for one job, with notes files beside it for what only some tasks need. Project values,
such as commands and paths, stay in the project's own `AGENTS.md`. Claude Code is the main harness and GitHub Copilot
CLI the second.

## Quick start

1. Install the plugins. On a machine with no GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` first.

   ```bash
   claude plugin marketplace add chiyanram/skills
   claude plugin install rulebook@chiyanram
   claude plugin install toolbox@chiyanram
   ```

   In GitHub Copilot CLI, run `copilot plugin marketplace add chiyanram/skills`, then `copilot plugin install` for
   each plugin. Copilot CLI cannot keep a skill typed-only, so a toolbox skill can load there without being typed.
2. Paste this block into the file your agent reads for project instructions, so it loads the skills on a task that
   does not name them. In Claude Code, paste it into `CLAUDE.md`, or keep it in `AGENTS.md` and add the line
   `@AGENTS.md` to `CLAUDE.md`.

<!-- agents-index: built by `make index` from plugins/rulebook/hooks/index.txt; do not edit by hand -->
```text
Rulebook skills (rulebook plugin). Load the skill before you start, even when the task does not name it.
- `code`: before you write, change or review production code, a small fix or a refactor included.
- `testing`: before you write, change or review a test, and with each code change that needs a test.
- `playwright`: before you write, run or fix a browser end-to-end test, or its CI job.
- `agent`: before you write or review code that calls a language model or runs an agent.
Then read the notes file that the skill names for your task.
```
<!-- /agents-index -->

3. Type `/toolbox:onboard` in the project once. It proposes the lines an agent needs for that project, such as its
   verify command.

If the agent skips the skills, set `RULEBOOK_INDEX=1` in the `env` of `.claude/settings.json`: the plugin then prints
the same block at the start of each session. `RULEBOOK_REPORT_RULES=1` prints
[`hooks/report-rules.txt`](plugins/rulebook/hooks/report-rules.txt), the rules for replies a person reads.
Update with `claude plugin marketplace update chiyanram`.

## Use

| skill | load it when you |
|---|---|
| [testing](plugins/rulebook/skills/testing/SKILL.md) | choose, write or review a test |
| [playwright](plugins/rulebook/skills/playwright/SKILL.md) | write, run or fix a Playwright end-to-end or smoke spec |
| [code](plugins/rulebook/skills/code/SKILL.md) | write or review production code |
| [agent](plugins/rulebook/skills/agent/SKILL.md) | write or review code that calls a model or runs an agent |
| [skill-feedback](plugins/rulebook/skills/skill-feedback/SKILL.md) | turn a session's skill failures into issues |
| [migrations](plugins/rulebook/skills/migrations/SKILL.md) | write or review a database migration |
| [obs](plugins/rulebook/skills/obs/SKILL.md) | write or review a log call, a metric or a trace |
| [planning](plugins/rulebook/skills/planning/SKILL.md) | write or review a spec, a design or a diagram |
| [writing](plugins/rulebook/skills/writing/SKILL.md) | write or review a doc, a README, an AGENTS.md, a skill or a PR body |
| [crq](plugins/rulebook/skills/crq/SKILL.md) | take a ticket to ready to merge, stage by stage, with four stops |
| [grilling](plugins/rulebook/skills/grilling/SKILL.md) | want a plan, decision or idea questioned in rounds |
| [chief-of-staff](plugins/rulebook/skills/chief-of-staff/SKILL.md) | want to know where you are across all your open work, and the one next move |


A project points at a skill by name, never by path: "use the `testing` skill (rulebook plugin) and read its notes on
tests that call a model". The [rulebook README](plugins/rulebook/README.md) and the
[toolbox README](plugins/toolbox/README.md) have more on each skill.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) for people, [AGENTS.md](AGENTS.md) for coding agents.

## License

[MIT](LICENSE)
