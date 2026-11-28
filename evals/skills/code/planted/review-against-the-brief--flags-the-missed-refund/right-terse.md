`markCancelled()` runs before the `PAID` check, so the status is always `CANCELLED` there and no refund is ever made: AC2 fails. Capture the status first.
