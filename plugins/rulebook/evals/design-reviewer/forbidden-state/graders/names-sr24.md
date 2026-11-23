---
type: llm
---

Decision 1 adds a record that can hold `refundedAt` while `status` is `OPEN` or `SHIPPED`, a combination the domain forbids. It also stores `itemCount`, which `items` already decides.

PASS if the review reports both problems: that the record's fields allow a forbidden combination of `status` and `refundedAt`, and that `itemCount` repeats what `items` decides. It may name SR24 or state the rule in its own words. Other findings, on any decision, do not matter.

FAIL if it misses either problem. Saying only that refunds are outside the spec is not the forbidden-combination problem.
