---
type: llm
---

A question about lanes is answered, not run as a change.

PASS if the output says a patch-level bump with no behaviour change takes the tiny lane, lists its phases (intake,
build, verify, code review, gate, PR, merge, timeline record, or close to it), and does not start a grill, write a spec
or ask what change to make.

FAIL if it gives a patch-level bump with no behaviour change a lane other than tiny, or starts the steps of a change.
Naming the lane a minor or major bump takes is not a failure.
