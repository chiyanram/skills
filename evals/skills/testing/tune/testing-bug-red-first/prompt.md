---
description: A bug report on a late-fee rule. The skill should write one regression test at the seam that owns the rule and run it red before the fix.
expected_outcome: One failing test in the policy's unit spec, seen red before the fix, then green after it; no copies at other layers.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Fix this bug. Show the test you add, the order of your steps, and what you put in the PR.

Bug report: a book returned on its due date is charged one day's fee. It should cost nothing.

```java
final class LateFeePolicy {
    Money fee(final LocalDate due, final LocalDate returned) {
        final long days = ChronoUnit.DAYS.between(due, returned) + 1;
        return days > 0 ? Money.cents(days * 25) : Money.ZERO;
    }
}
```

`LateFeePolicy` is called by `ReturnService`, which is called by `ReturnController`. There is a Spock spec `LateFeePolicySpec` with cases for 3 and 10 days late.
