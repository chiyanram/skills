---
description: A PIT report shows a surviving conditional-boundary mutant. The agent should name the missing case and cover the edge on both sides, not aim at the one line.
expected_outcome: The answer names the CORRECT letter the mutant breaks and adds that case (M2), with tests just inside and just outside the edge (B3).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, answer this mutation report: say what the surviving mutant means and show the tests you would add.

```text
SURVIVED  ShippingPricer.java:7  ConditionalsBoundaryMutator: changed conditional boundary (>= replaced by >)

final class ShippingPricer {
    BigDecimal shipping(final BigDecimal orderTotal) {
        return orderTotal.compareTo(new BigDecimal("100.00")) >= 0 ? BigDecimal.ZERO : new BigDecimal("5.00");   // line 7
    }
}

// existing tests: shipping(50.00) == 5.00 ; shipping(250.00) == 0
```
