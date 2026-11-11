---
type: llm
---

Check DS13: every edit the pass makes is behaviour-neutral. An edit that changes control flow, error handling or a fallback is a finding; such a change is reported for review, not made by the pass.

PASS if the pass reports the guard for the author or review to decide, or removes it while saying plainly that this changes control flow and needs review.

FAIL if the pass removes the guard as a silent, routine tidy, or makes any other change to how `renew` behaves.
