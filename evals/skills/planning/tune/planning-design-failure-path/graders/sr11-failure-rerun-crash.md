---
type: llm
---

Check SR11: for each step that changes state or calls another system, the design says what happens when it fails, runs twice, or crashes halfway.

PASS if the review flags that the charge, save and send steps have no stated failure, second-run or crash-halfway behaviour, for example a charge that succeeds and a save that fails.

FAIL if the review accepts the design as complete on failure behaviour, or only asks a general question without naming the steps.
