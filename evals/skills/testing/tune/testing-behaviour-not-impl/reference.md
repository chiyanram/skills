---
approved: operator
---

Two problems. First, `DiscountRules` is the team's own pure class, so it should not be mocked: use the real object and assert the observable result, `price(...) == 90.00`, worked out by hand. Mocking it ties the test to the internal call and breaks on a refactor that keeps the behaviour, and the test asserts no price at all. Second, the `_` wildcard on `rateFor` lets any argument pass, so a call with the wrong member still passes; if an interaction is verified, match the argument by value.
