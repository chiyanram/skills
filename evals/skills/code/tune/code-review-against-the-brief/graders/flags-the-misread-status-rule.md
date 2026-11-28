---
type: llm
---

Check: the review compares the diff with each acceptance criterion and finds a criterion the code misreads.

PASS if the review says that the guard refuses only `SHIPPED`, while AC1 allows a cancel only for `PLACED` and `PAID`, so a `DELIVERED` or an already `CANCELLED` order can still be cancelled. Naming one of those two statuses is enough.

FAIL if the review accepts the `SHIPPED` guard as meeting AC1, or does not mention which statuses the guard lets through.
