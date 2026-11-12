---
type: llm
---

Check C4: record each case you knowingly leave untested as one gap row in the MR description (dimension, missing, risk), never left unsaid.

PASS if the merge request text lists each case the answer does not test as a row naming the dimension, what is missing and the risk.

FAIL if the answer leaves cases untested with no gap row, or the merge request text has no gaps section.
