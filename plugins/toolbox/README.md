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

A tool joins only after it has been read in full, tied to a real moment in our work, and tried once on a named task.
