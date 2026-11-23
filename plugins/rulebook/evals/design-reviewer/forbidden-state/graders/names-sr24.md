---
type: llm
---

Decision 1 adds a record with a forbidden state: it can hold `refundedAt` while `status` is `OPEN` or `SHIPPED`. It also stores a derived value: `itemCount`, which `items` already decides.

PASS if the review reports both problems: the forbidden state of `status` and `refundedAt`, and the derived value `itemCount`. It may name SR24 or state the rule in its own words. Other findings, on any decision, do not matter.

FAIL if it misses either problem. Saying only that refunds are outside the spec is not the forbidden-state problem.
