---
description: A draft acceptance-criteria section for order cancellation names a class and a test level, has no refusal AC, and has a topic line. The review should flag each.
expected_outcome: The review flags the class and test level and the missing refusal AC (GA5), and the non-sentence AC text (GA6), and proposes rewritten ACs.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review the acceptance-criteria section of this draft spec and list your findings, then give the corrected ACs.

```text
## Acceptance criteria
AC-1 — should call OrderCancellationService.cancel, which sets the status to CANCELLED in OrderRepository (unit test)
AC-2 — Cancellation refund amount
```

The spec covers one behaviour: a customer cancels an order that has not shipped. Shipped orders cannot be cancelled.
