---
description: The same rescue as last week, whose retro added a written rule. The retro should propose a check or script this time, not another written rule.
expected_outcome: One action of type check or script that catches a widened matcher mechanically; not a new or reworded written rule.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

I am starting a full retro with crq on this merged change. Propose the actions; I will accept or reject each.

Timeline record:
- Ticket: overdue reminder text (feature lane). Review rounds: 2.
- Human rescue: the implementer widened `verify(notifier).send(eq("Loan 7 is overdue"))` to `send(any())` in an
  existing test, and the review did not flag it. The human restored the exact matcher.

Last week's retro, accepted: "the same rescue (an `eq(...)` widened to `any()` in an existing test); action: a
written rule telling reviewers to check widened matchers — type rule, owner Priya, done."
