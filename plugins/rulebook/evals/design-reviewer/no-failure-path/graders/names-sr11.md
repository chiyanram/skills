---
type: llm
---

Decision 2 calls an outside system and changes state (closes the loan), but the design never says what happens when the charge fails or times out, or how anyone would see it.

PASS if the review gives decision 2 an open or conflict verdict (or a blocking finding) for the missing failure path, and names SR11 or describes the rule (what happens when the call fails).

FAIL if decision 2 is marked aligned, or the missing failure path is not reported.
