---
type: llm
---

Decision 2 retries a charge after a timeout. A timeout does not mean the charge failed: the payment service may have
charged the card and the reply was lost. `PaymentClient.charge` takes no idempotency key, so a retry can charge the
member twice.

PASS if the report has a scenario for the double charge on a retry after a timeout, ties it to decision 2, gives it a
concrete trigger and a first sign a person would see (for example a member or support noticing two charges), and marks
it a blocker or says it moves money.

FAIL if the double charge is not reported, or it is reported only as a vague "the payment call might fail".
