---
type: llm
---

Check: a bug fix starts with one test that fails for the bug's reason, and the test is run and seen failing before the code changes.

PASS if the reply writes a test for a return on the due date that expects no fee, and the new test is run and seen failing before `LateFeePolicy` is changed. It passes whether the reply says it ran the test or gives running it as a step.

FAIL if the reply fixes the code first, writes the test only after the fix, or has no step where the new test is seen failing before the fix.
