---
type: llm
---

Check: the regression test fails for the bug's real reason.

PASS if the reply identifies that `movePointLeft(3)` in `CheckoutService` converts cents wrongly (it should move two places), and the failing test is on that conversion or on `CheckoutService.shippingFor`.

FAIL if the reply does not find the conversion error in `CheckoutService`.
