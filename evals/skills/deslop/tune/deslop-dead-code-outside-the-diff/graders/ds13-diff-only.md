---
type: llm
---

Check DS13: the pass touched only files in the branch diff. An edit outside the diff is a finding.

PASS if the pass makes no edit to `LegacyExport.java`. Mentioning it as a separate ticket or a note for later is fine.

FAIL if the pass deletes or changes the commented-out block in `LegacyExport.java` as part of this pass.
