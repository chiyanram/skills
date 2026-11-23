---
description: A bug report blames a rule that is correct; the real cause is the caller passing cents. The skill should test the premise before it changes the rule. Today's skill states this only in part; PR 2 adds it in full.
expected_outcome: A test of the rule shows it is correct; the reply finds the units mismatch in the caller and leaves the rule as it is.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Fix this bug. Show your steps and the test.

Bug report: "Orders of 100 EUR or more get no free shipping. `FreeShippingRule` is broken."

```java
final class FreeShippingRule {
    boolean applies(final BigDecimal subtotalEur) {
        return subtotalEur.compareTo(new BigDecimal("100")) >= 0;
    }
}

final class CheckoutService {
    Shipping shippingFor(final Cart cart) {
        final BigDecimal subtotal = BigDecimal.valueOf(cart.subtotalCents()).movePointLeft(3);
        return rule.applies(subtotal) ? Shipping.FREE : Shipping.STANDARD;
    }
}
```
