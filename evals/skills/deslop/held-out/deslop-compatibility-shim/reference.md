---
approved: null
---

Findings: the `findByEmail` default method is a compatibility shim with no outside consumer, because `MemberRepository` is used only in this repository. `ReminderJob.java:41` is a caller still on the old path. Edit: move `ReminderJob` to `findByEmailAddress(EmailAddress.of(address))` and delete the shim, or report both for the author. Every lookup returns the same member.
