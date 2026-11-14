# toolbox

Tools a person types. Each one runs only when you type its name, never on its own, and none pushes or merges. Where
each came from, and its licence, is in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Install

```bash
claude plugin marketplace add chiyanram/skills
claude plugin install toolbox@chiyanram
```

The repo is private. See the [root README](../../README.md#quick-start) for credentials.

## Tools

| tool | type | what it does |
|---|---|---|
| [correct](skills/correct/SKILL.md) | `/toolbox:correct` | finds the mistakes agents repeat here and proposes a fix for each at the highest level: architecture, types, a lint, a test, then docs |
| [grilling](skills/grilling/SKILL.md) | `/toolbox:grilling` | asks about a plan or decision one question at a time, each with a recommended answer, until you agree on it |
| [loop-me](skills/loop-me/SKILL.md) | `/toolbox:loop-me` | grills you into workflow specs an agent could build without a question, kept in `workflows/*.md` |
| [diagram-brief](skills/diagram-brief/SKILL.md) | `/toolbox:diagram-brief` | briefs a change as a `diff` call tree with proof, message vs diff, callers and what may break |
| [onboard](skills/onboard/SKILL.md) | `/toolbox:onboard` | sets up a repo for the rulebook: its confirmed commands, which stack notes apply, and the codebase-health rule, as one block in `AGENTS.md` or `CLAUDE.md` |
| [break-design](skills/break-design/SKILL.md) | `/toolbox:break-design` | tries to break a design before you approve it: each reachable failure with one proposed closure, using the rulebook's break catalogue |
| [software-factory](skills/software-factory/SKILL.md) | `/toolbox:software-factory` | the shared words for designing a software factory: tasks, runs, runners and the services they plug into, with a survey per slot |
| [weigh-source](skills/weigh-source/SKILL.md) | `/toolbox:weigh-source` | weighs a shared article, talk or post against this project's design and the field: what to take, reject or watch |

A tool joins only after it has been read in full, tied to a real moment in our work, and tried once on a named task.
