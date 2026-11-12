---
type: llm
---

Check GA4: ACs that differ only in values are one AC-n line with a table of input and expected result, one row per case.

PASS if the review flags AC-1 to AC-3 as differing only in values, and the corrected ACs hold one AC line with a table that has input columns and an expected-result column.

FAIL if the three lines are left as separate ACs, or the table has no expected-result column.
