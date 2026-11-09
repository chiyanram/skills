---
type: llm
---

F1 and F2 are the same real problem: the same line, the same rule.

PASS if exactly one of F1 and F2 is act_on, and the other is dismissed with a why that names it a duplicate of the kept one.

FAIL if both are kept in any bucket other than dismissed, if both are dismissed, or if the real problem is not act_on.
