## Review

| # | where | finding | ask |
|---|---|---|---|
| 1 | guard | AC1 allows a cancel only for `PLACED` and `PAID`. The guard refuses only `SHIPPED`, so `DELIVERED` and `CANCELLED` orders pass through. | Refuse every status except `PLACED` and `PAID`. |
| 2 | email | The cancellation email is not in the ticket. | Remove it or ticket it. |
| 3 | refund | AC2 is met: a `PAID` order gets `Refund.full(order)` in the same method. | none |
| 4 | transaction | AC3 is met: one `@Transactional` method. | none |

Add a test for a `DELIVERED` order.

Verdict: request changes.
