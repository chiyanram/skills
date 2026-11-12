---
type: llm
---

Check SR14: no abstraction, port or extension point is added without a second user, today or in this spec.

PASS if the review flags `ExportFormatProvider` as having one implementation and no second user in the spec, and asks to remove it until a second user exists.

FAIL if the interface is accepted because PDF or XML export may come later.
