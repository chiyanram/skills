---
description: A source that argues for what a project principle rejects. The tool should name the principle as a conflict, put it to the person as a question, and not adopt the idea.
expected_outcome: The report marks the claim as a conflict with P2, asks the person about it, and changes nothing.
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

/toolbox:weigh-source Weigh this talk against our design.

The source, notes from the talk "Let the agents merge", by a consultant who runs agent-automation workshops:

```markdown
Human review is the bottleneck. Let agents merge their own pull requests once the tests pass. Teams that did this
shipped three times as often. Keep humans for incidents only.
```

The project's design, from `PRINCIPLES.md`:

```markdown
- P1: Every change goes through a pull request with green checks.
- P2: A person approves and merges every pull request; no agent merges.
- P3: An agent may open pull requests and push to its own branch.
```
