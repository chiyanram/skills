---
type: llm
---

Check: the review compares the diff with each acceptance criterion and finds a criterion the code does not meet.

PASS if the review says that the `PAID` check runs after `markCancelled()`, so the status is already `CANCELLED` and no refund is created, which breaks AC2. Any fix that reads the status before the change passes.

FAIL if the review does not find that the refund is never created, or says AC2 is met.
