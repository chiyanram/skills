---
approved: operator
---

`reserve` returns a sealed `HoldOutcome` with three records: `Placed(Hold hold)`, `AlreadyHeld()` and
`LimitReached()`. The service throws no exception for the two refusals, because they are foreseeable outcomes, and a
thrown expected case is not in the signature. The service checks `existsByMemberIdAndTitleId` and
`countByMemberId(...) >= 5` before it calls `save`, in one `@Transactional` method. `HoldController` maps the outcome
with a `switch` that lists `Placed`, `AlreadyHeld` and `LimitReached` and has no `default`: `Placed` gives 201 with a
response type (not the `Hold` entity), and each refusal gives a 4xx status such as 409 or 422 with a catalogue message.

Allowed extras: a fourth case such as `MemberNotFound`, a pure decision method that takes the count and the flag,
named constants for the limit, a response record, tests, or a note on a race between the count and the save.
