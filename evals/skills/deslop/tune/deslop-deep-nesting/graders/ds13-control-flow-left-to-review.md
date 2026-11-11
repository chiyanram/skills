---
type: llm
---

Check DS13: an edit that changes control flow is a finding; the pass reports it instead of making it.

PASS if the pass reports the nesting and the ternary (with a suggested shape if it likes) and does not present a restructured `fine` or `label` as a behaviour-neutral edit it made.

FAIL if the pass rewrites `fine` or `label` itself as a routine tidy without saying it changes control flow and needs review.
