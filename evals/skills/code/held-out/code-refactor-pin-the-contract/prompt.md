---
description: A request to reduce a method's complexity, with the claim that compiling and a passing linter make it safe. The skill should pin the current results with tests before it reshapes the method, and keep every edge, including the two thresholds that differ (`>=` and `>`) and the branches where express is checked in a different order. Today's skill has no refactoring step; the planned "type check and lint are not a pin" piece adds it.
expected_outcome: Tests that pin today's results at both thresholds come first; the flatter method returns the same cents as the original for every input.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Refactor `shippingCostCents` to reduce its complexity. It compiles and the linter passes, so the behaviour is safe. Show your steps and the result.

```java
final class ShippingCost {
    long shippingCostCents(final Order order) {
        if (order.country().equals("DE")) {
            if (order.totalCents() >= 5000) {
                return 0;
            } else {
                if (order.express()) {
                    return 990;
                } else {
                    return 490;
                }
            }
        } else {
            if (order.express()) {
                return 1990;
            } else {
                if (order.totalCents() > 10000) {
                    return 0;
                }
                return 1490;
            }
        }
    }
}
```

`Order` is a record with `country()` (a `String`, never null), `totalCents()` (a `long`) and `express()` (a `boolean`). There is no test of `ShippingCost` yet.
