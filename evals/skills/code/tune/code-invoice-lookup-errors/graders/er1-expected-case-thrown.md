---
type: llm
---

Check ER1: a foreseeable non-success such as not found is returned as a case of a sealed return type, and only faults are thrown.

PASS if the review says `find` throws `InvoiceNotFoundException` for an expected not-found and recommends a sealed outcome (for example found / not found) instead.

FAIL if the review accepts the thrown not-found as fine, or does not mention it.
