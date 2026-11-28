---
type: llm
---

Check: a refactor keeps every observable result.

PASS if the refactored method returns the same value as the original for these inputs: a DE express order of 5000 gives 0; a DE standard order of 4999 gives 490; a non-DE express order of 20000 gives 1990; a non-DE standard order of 10000 gives 1490, and of 10001 gives 0. Trace the reply's final code for each input.

FAIL if the reply's final code gives a different value for any of these inputs, for example free shipping for a non-DE express order, `>= 10000` outside DE, or 990 for a DE express order of 5000.
