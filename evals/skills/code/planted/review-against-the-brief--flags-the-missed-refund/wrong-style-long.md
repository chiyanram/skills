## Review

The change is small and reads well.

| # | where | comment |
|---|---|---|
| 1 | `cancel` | `orElseThrow()` throws `NoSuchElementException`; prefer a domain outcome such as `CancelOutcome.NotFound`. |
| 2 | `cancel` | `Refund.full(order)` could be a method on `Order`: `order.fullRefund()`. |
| 3 | naming | `TooLate` could be `NotCancellable`, which says more. |
| 4 | tests | Both tests pass. |

AC1 to AC3 look covered. Verdict: approve with nits.
