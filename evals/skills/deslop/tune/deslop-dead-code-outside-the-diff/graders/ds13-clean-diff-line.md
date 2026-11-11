---
type: llm
---

Check DS13 and the pass's report: a clean diff still gets its report line, so a skipped pass and an empty one look different.

PASS if the pass proposes no edit to `OrderNumbers.java` and its report says the diff had nothing to clean.

FAIL if it proposes a change to the diff's lines, or ends with no report line.
