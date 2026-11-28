## Review

| # | where | finding | ask |
|---|---|---|---|
| 1 | refund | `markCancelled()` sets the status to `CANCELLED` before the `PAID` check, so `refunds.save(...)` is unreachable and AC2 fails. | Capture `order.status()` before `markCancelled()`. |
| 2 | email | `sendCancellationEmail` is not in the ticket and is sent inside the transaction. | Remove it or move it to an after-commit listener, with a ticket. |
| 3 | guard | The `SHIPPED` guard covers AC1: an order that has left the warehouse cannot be cancelled. | none |
| 4 | transaction | AC3 is met by `@Transactional`. | none |

Add a test that cancels a `PAID` order and asserts one refund of the full amount.

Verdict: request changes.
