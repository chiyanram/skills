---
type: llm
---

Check DS9: nesting of three or more levels that a guard clause or early return could flatten is a finding, and so is a nested ternary.

PASS if the pass flags both the three-level `if` nesting in `fine` and the nested ternary in `label`.

FAIL if either one is not mentioned.
