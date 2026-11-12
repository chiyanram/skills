---
type: llm
---

Check S4: a bug fix starts with a test that fails for the bug's reason, landed before the fix.

PASS if the answer puts a test of the 100.00 boundary (expected shipping 0) ahead of the change to `>=`, and says or shows that it fails on the current code for that reason.

FAIL if the fix comes first or alone, or the test is only added after the fix with no failing step.
