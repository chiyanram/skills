---
type: llm
---

Check PD4: the build is planned as slices that each run end-to-end and can be tried, never one step per layer.

PASS if the review flags the plan as one step per layer (table, service, controller), and the corrected plan has slices that each deliver a behaviour that can be tried, such as a request or a test.

FAIL if the layer-by-layer plan is kept, or only renamed.
