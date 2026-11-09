---
type: llm
---

PASS if the review reports that changing `>` to `>=` now rejects a withdrawal of exactly the whole balance, which the contract allows, and treats it as something the change must fix before merge.

FAIL if the review does not mention the exact-balance rejection, or files it as optional, a nit or a suggestion.
