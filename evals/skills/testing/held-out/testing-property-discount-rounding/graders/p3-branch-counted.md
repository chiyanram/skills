---
type: llm
---

Check P3: in every conditional property, count which branch each case hits and fail if a branch is never reached.

PASS if the answer adds a coverage count or classification (for example `Statistics.collect` or a label with a check) for the below-500 and at-or-above-500 branches and fails when either is never reached.

FAIL if the conditional property stays without any count of the branches it reaches.
