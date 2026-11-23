---
approved: operator
---

Before changing `FreeShippingRule`, test the report's premise: a test that `applies(new BigDecimal("100"))` is true passes, so the rule is not at fault. The cause is `movePointLeft(3)` in `CheckoutService`, which turns 10000 cents into 10.000 instead of 100.00, so a 100 EUR order gets standard shipping (it must be `movePointLeft(2)`). Write a failing test at `CheckoutService` for a cart of 10000 cents expecting free shipping, see it fail, fix the conversion, see it pass. `FreeShippingRule` is not changed.
