---
approved: operator
---

Compiling and a passing linter do not show that the results are unchanged, so the first step pins today's results with
tests, run green on the current code before any change. The cases cover each branch and both thresholds: DE at 4999
(490 standard, 990 express) and at 5000 (0, also when express); outside DE, express is 1990 at any total (also over
10000), and standard is 1490 at 10000 and 0 at 10001. Then reshape, for example with guard clauses:

```java
long shippingCostCents(final Order order) {
    if (order.country().equals("DE")) {
        if (order.totalCents() >= 5000) {
            return 0;
        }
        return order.express() ? 990 : 490;
    }
    if (order.express()) {
        return 1990;
    }
    return order.totalCents() > 10000 ? 0 : 1490;
}
```

The pinned tests stay green after the change. The result keeps `>= 5000` for DE and `> 10000` elsewhere, free DE
shipping for express orders, and no free shipping for express orders outside DE.

Allowed extras: a table-driven or parameterized test, named constants, a note that the two thresholds differ on
purpose or should be checked with the product owner (without changing them), or a sealed or enum zone type.
