---
type: llm
---

PASS if the cleanup removes the comment `// compute the fine` and the unused `verbose` parameter together with the `false` argument at its caller, changes no behaviour (the 7-day threshold and 200 stay), and says the evidence row is run again with the same result.

FAIL if either is left in place, or the cleanup changes the fine rule or the threshold.
