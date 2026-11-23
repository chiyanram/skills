---
type: llm
---

Check: the regression test sits at the seam that owns the behaviour, and is not copied into every layer the bug crosses.

PASS if the regression test is in the policy's own unit spec (`LateFeePolicySpec` or a unit test of `LateFeePolicy`), and the reply adds no copy of it in `ReturnService` or `ReturnController` tests.

FAIL if the reply puts the only regression test in a service or controller test, or adds the same check at two or more layers.
