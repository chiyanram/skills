---
type: llm
---

PASS if the race scenario proposes exactly one closure: for example a failure AC such as "should refuse the second
reservation when the last copy was reserved a moment before", or a mitigation such as a unique constraint on
`copy_id` or a lock, with how it shows when it fires.

FAIL if it has no closure, lists several without choosing one, or the report changes the design or approves it.
