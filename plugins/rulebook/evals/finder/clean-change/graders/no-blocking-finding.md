---
type: llm
---

The diff is correct: `strip()` then `isEmpty()` rejects the same blank names as before, and the new test checks the stripped value.

PASS if the review raises no finding it says must be fixed before merge. Nits, optional suggestions and questions are fine.

FAIL if the review blocks the change, or reports a defect that is not there.
