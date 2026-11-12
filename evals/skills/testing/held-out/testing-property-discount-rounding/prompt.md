---
description: A property test for a discount rule that uses a heavy filter and a conditional property that may never reach its branch.
expected_outcome: The generator is built by mapping, not heavy filtering (P8), and the conditional property counts which branch each case hits and fails if one is never reached (P3).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, review this property test and give the version you would land. The requirement: for any order, a loyalty discount of 10% applies only when the order total is at least 500.00, and the discounted total is never negative.

```java
@Property
void discountOnlyForBigOrders(@ForAll("orders") Order order) {
    Money discounted = pricer.discounted(order);
    if (order.total().isAtLeast(Money.of("500.00"))) {
        assertThat(discounted).isEqualTo(order.total().times("0.90"));
    }
    assertThat(discounted.isNegative()).isFalse();
}

@Provide
Arbitrary<Order> orders() {
    return Arbitraries.bigDecimals().ofScale(2)
        .map(Order::ofTotal)
        .filter(o -> o.total().isAtLeast(Money.of("500.00")) && o.total().isAtMost(Money.of("10000.00")))
        .filter(o -> !o.total().isNegative());
}
```
