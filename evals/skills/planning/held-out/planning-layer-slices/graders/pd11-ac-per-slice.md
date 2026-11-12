---
type: llm
---

Check PD11: each slice names the AC-n it delivers, and every AC has a slice.

PASS if the corrected plan names an AC-n for each slice and every one of AC-1, AC-2 and AC-3 appears in a slice, and the review notes that the plan named none.

FAIL if a slice names no AC-n, or an AC (for example the declined-deposit AC-2) has no slice.
