---
type: llm
---

Check TM2: in ITs fake only what others own (third-party HTTP: WireMock at the wire), because faking our code leaves its query untested.

PASS if the IT runs `BookingRepository` against a real database and fakes only the payment API, at the wire (WireMock or a vendor sandbox).

FAIL if the IT replaces `BookingRepository` or `PriceCalculator` with a double, or mocks `PaymentGateway` in place of faking the HTTP wire.
