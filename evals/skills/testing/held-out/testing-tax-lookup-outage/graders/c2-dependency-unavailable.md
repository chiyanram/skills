---
type: llm
---

Check C2: test each external dependency's unavailable case: a predictable failure, a WARN or ERROR log, no hang.

PASS if one of the tests makes the tax-rate service unavailable (error or timeout) and asserts a defined failure plus a WARN or ERROR log, and that the call does not hang.

FAIL if no test covers the tax-rate service being unavailable.
