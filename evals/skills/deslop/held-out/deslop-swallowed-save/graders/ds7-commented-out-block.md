---
type: llm
---

Check DS7: a commented-out block in a touched file is a finding.

PASS if the pass removes the two commented-out lines, or reports them as dead code.

FAIL if the commented-out lines are left and not mentioned.
