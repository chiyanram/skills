---
type: llm
---

Check DG2: a call tree that a design changes is drawn as a fenced diff, not as a Mermaid chart.

PASS if the review flags the flowchart as hiding the added `WaitlistService.promote` and removed `DepositPolicy.check`, and the corrected diagram is a fenced `diff` with `+` and `-` lines for those two calls.

FAIL if the call tree stays a Mermaid chart, or the diff does not mark both the added and the removed call.
