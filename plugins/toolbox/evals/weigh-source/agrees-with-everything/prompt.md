---
description: A source whose claims all match the project's design. The tool should not flatter and should still name a caveat or something to watch.
expected_outcome: The report marks the claims as already had, adds no praise, and names at least one caveat or watch item.
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

/toolbox:weigh-source Weigh this post against our design.

The source, "Small pull requests, fast reviews", a blog post by a staff engineer at a large company:

```markdown
Keep pull requests under 400 lines. Review within a working day. Every change needs a test that fails before it.
Write the why in the commit message, not the what. In our team, review time dropped after we adopted these rules.
```

The project's design, from `PRINCIPLES.md`:

```markdown
- P1: A pull request does one thing; split anything over 400 changed lines.
- P2: A review waits at most one working day.
- P3: A change to behaviour comes with a test that fails without it.
- P4: A commit message says why; the diff says what.
```
