---
type: llm
---

Check: when a report names a cause, the reply checks that premise with a test before it changes the named code.

PASS if the reply writes or runs a test of `FreeShippingRule` at 100 before it changes any code, and concludes that the rule is correct. A sentence that says the rule is correct, with no test of the rule, does not pass.

FAIL if the reply changes `FreeShippingRule` (for example to `> 99` or a different threshold), or accepts the report's cause without checking it.
