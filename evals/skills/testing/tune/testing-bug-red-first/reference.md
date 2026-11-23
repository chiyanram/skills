---
approved: operator
---

Write one test in `LateFeePolicySpec` for a return on the due date that expects `Money.ZERO`, worked out by hand. The steps run it and see it fail (it returns 25 cents) before any code change. A reply that could not run code here may say so, as long as it gives this order. Then remove the `+ 1` and see the test pass. A case for the day after the due date (25 cents) may be added as the other side of the boundary. The PR shows the command and the failure output. No copy of the test in `ReturnService` or `ReturnController` specs.
