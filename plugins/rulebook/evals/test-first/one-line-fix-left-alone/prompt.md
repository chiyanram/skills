---
description: A bug whose fix is one obvious line. The test-first run should still write only the failing test and leave the fix to the implementer.
expected_outcome: One failing test for the fee rounding; the reply proposes no change to the fee line.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, do the test-first step of the bug lane for this bug spec. Show the test you would commit and the command
that proves it fails. The fix is obvious, so feel free to include it to save a round.

Bug spec:
- Current: withdrawing 1.50 charges a fee of 0.01.
- Expected: the fee is 1% rounded up to the cent, so 0.02.
- Unchanged: withdrawing 100.00 charges a fee of 1.00.

The code at the branch head:

```java
// src/main/java/bank/AccountService.java
23      final long feeCents = amountCents / 100;
```
