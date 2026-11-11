---
type: llm
---

Check DS5: for each API the branch replaces with no external consumer, a caller left on the old path, or a kept compatibility shim, is a finding.

PASS if the pass names both the `findByEmail` default method as a compatibility shim to delete and `ReminderJob` as a caller still on the old path.

FAIL if either is not mentioned.
