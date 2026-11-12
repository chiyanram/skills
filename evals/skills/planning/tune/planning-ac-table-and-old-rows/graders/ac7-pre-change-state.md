---
type: llm
---

Check AC7: when a change alters stored data or a default, at least one AC starts from the state before the change.

PASS if the review notes that every AC uses a new invoice, and the corrected ACs add one that starts from an invoice stored before the column existed and expects the default late fee.

FAIL if no AC starts from an invoice that existed before the change.
