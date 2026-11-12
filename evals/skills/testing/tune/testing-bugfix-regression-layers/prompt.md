---
description: A bug fix where the defect is in a pure pricing class reached through a controller and a service. The agent should write a failing test first, one regression test at the owning boundary.
expected_outcome: A failing test for the bug's reason is written before the fix (S4), and the bug gets one regression test at the layer that owns the pricing (V4), not copies at the controller and service.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, plan the fix for this bug: show the tests you would write, in what order, and the code change.

Bug report: an order of exactly 100.00 should get free shipping, but is charged 5.00.

```java
final class ShippingPricer {
    BigDecimal shipping(final BigDecimal orderTotal) {
        return orderTotal.compareTo(new BigDecimal("100.00")) > 0 ? BigDecimal.ZERO : new BigDecimal("5.00");
    }
}

final class OrderService {            // calls ShippingPricer, saves the order
    Order place(final Cart cart) { /* ... */ }
}

@RestController
final class OrderController {         // POST /orders, delegates to OrderService
}
```
