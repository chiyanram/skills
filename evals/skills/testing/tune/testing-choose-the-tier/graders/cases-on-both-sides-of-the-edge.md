---
type: llm
---

Check: for a range, test just inside and just outside each edge, so an off-by-one cannot pass.

PASS if the cases include a loan due on `today` (the edge, not overdue under `<`) and a loan due the day before (overdue).

FAIL if the cases do not include a loan due exactly on `today`.
