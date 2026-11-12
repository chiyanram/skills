---
type: llm
---

Check V4: a bug gets ONE regression test, at the boundary that owns the behaviour, never replayed at every layer it crosses.

PASS if the answer adds the regression test at `ShippingPricer` (or states one owning boundary) and does not add copies of the same 100.00 case to `OrderService` or `OrderController` tests.

FAIL if the same regression case is added at two or more layers, or at a mocked layer that cannot see the bug.
