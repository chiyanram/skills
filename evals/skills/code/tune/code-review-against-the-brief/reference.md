---
approved: operator
---

Three findings against the ticket. First, AC1 is misread: the guard refuses only `SHIPPED`, so a `DELIVERED` or an
already `CANCELLED` order can be cancelled; the guard must allow only `PLACED` and `PAID` (for example
`status != PLACED && status != PAID` returns `TooLate`). Second, AC2 is not met: `markCancelled()` runs before the
`PAID` check, so the status is already `CANCELLED` and no refund is ever created; read the status before the change
(or create the refund first). Third, the cancellation email is behaviour the ticket does not ask for; ask the author
to remove it or to get it added to the ticket. The passing tests do not cover a `PAID` order, so they miss the refund
bug; ask for a test that cancels a `PAID` order and expects a full refund.

Allowed extras: a note that the email inside the transaction can go out for a rollback, a request for a
`DELIVERED` test, a finding on `orElseThrow()` for a missing order, or a verdict line such as "request changes".
