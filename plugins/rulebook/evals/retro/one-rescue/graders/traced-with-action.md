---
type: llm
---

The finder marked CR7 (the check for removed chunks) "not applicable" although the diff deleted the reservation check: that is where the review failed.

PASS if the retro traces the rescue to the review check for removed code (CR7, or the finder skipping it) rather than stopping at "the model missed it", and proposes one action with a type, an owner, a due date and a ticket.

FAIL if the retro stops at "the model got it wrong", proposes no action, or gives an action without an owner or due date.
