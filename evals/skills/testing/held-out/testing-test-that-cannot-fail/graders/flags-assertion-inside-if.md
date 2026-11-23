---
type: llm
---

Check: let nothing turn a failure green; no assertion inside an `if`.

PASS if the review flags that the assertion is inside an `if`, so the spec can pass without asserting anything, and asks to assert unconditionally.

FAIL if the review does not mention the `if` around the assertion.
