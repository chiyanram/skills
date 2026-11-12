---
type: llm
---

Check U3: double only at boundaries; mocking your own classes breaks tests on refactors that keep behaviour.

PASS if neither the spec nor the IT mocks `PriceCalculator` (it is used for real) and the answer does not mock `BookingRepository` in a unit spec as the primary test of confirm.

FAIL if `PriceCalculator` or `BookingRepository` is replaced by `Mock()`, `Stub()` or `@MockBean`.
