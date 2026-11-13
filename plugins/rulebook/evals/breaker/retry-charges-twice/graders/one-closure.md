---
type: llm
---

PASS if the double-charge scenario proposes exactly one closure, for example a mitigation (an idempotency key such as
the loan id on every charge attempt) or a failure AC in the form "should charge the fine once when …". The closure may
come with a short why.

FAIL if the scenario has no closure, offers several closures without choosing one, or the report edits the design or
approves it itself.
