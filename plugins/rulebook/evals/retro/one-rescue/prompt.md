---
description: A merge with one human rescue. The retro should trace it to a check and propose one action with type, owner, due date and ticket.
expected_outcome: The rescue is traced past "the model got it wrong" to the review check that missed it; one action with type, owner, due date and ticket.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

I am starting a full retro with crq on this merged change. Propose the actions; I will accept or reject each.

Timeline record:
- Ticket: renew a loan once (feature lane). Review rounds: 1. Findings: act_on 0, consider 1, nit 2.
- Human rescue: before merge, the human found that `renew()` no longer checked for an open reservation, a check the
  diff had deleted. The human added it back in commit `a1b2c3d`.
- The finder's coverage line: "CR1–CR6 applied; CR7 not applicable".

Team owners: reviews and checks belong to Priya.
