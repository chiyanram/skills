---
type: llm
---

Check: verify interactions with arguments matched by value; a wildcard lets the wrong value pass.

PASS if the review points out that `rateFor(_)` accepts any argument, so a wrong member would still pass, or that the spec asserts no price.

FAIL if the review mentions neither the wildcard nor the missing assertion on the price.
