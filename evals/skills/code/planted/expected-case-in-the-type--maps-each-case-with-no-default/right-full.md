## Return type

```java
sealed interface HoldOutcome {
    record Placed(Hold hold) implements HoldOutcome {}
    record AlreadyHeld() implements HoldOutcome {}
    record LimitReached() implements HoldOutcome {}
}
```

## HoldService.reserve

```java
private static final int HOLD_LIMIT = 5;

@Transactional
HoldOutcome reserve(final long memberId, final long titleId) {
    if (holds.existsByMemberIdAndTitleId(memberId, titleId)) {
        return new HoldOutcome.AlreadyHeld();
    }
    if (holds.countByMemberId(memberId) >= HOLD_LIMIT) {
        return new HoldOutcome.LimitReached();
    }
    return new HoldOutcome.Placed(holds.save(Hold.of(memberId, titleId)));
}
```

## HoldController

```java
@PostMapping("/members/{memberId}/holds")
ResponseEntity<?> reserve(@PathVariable final long memberId, @RequestBody final HoldRequest request) {
    return switch (service.reserve(memberId, request.titleId())) {
        case HoldOutcome.Placed placed ->
            ResponseEntity.status(HttpStatus.CREATED).body(HoldResponse.from(placed.hold()));
        case HoldOutcome.AlreadyHeld _ ->
            ResponseEntity.status(HttpStatus.CONFLICT).body(ErrorBody.of("HOLD_ALREADY_PLACED"));
        case HoldOutcome.LimitReached _ ->
            ResponseEntity.status(HttpStatus.CONFLICT).body(ErrorBody.of("HOLD_LIMIT_REACHED"));
    };
}
```

| outcome | status | body |
|---|---|---|
| `Placed` | 201 | `HoldResponse` |
| `AlreadyHeld` | 409 | catalogue code `HOLD_ALREADY_PLACED` |
| `LimitReached` | 409 | catalogue code `HOLD_LIMIT_REACHED` |

Notes:

- Both refusals are foreseeable outcomes, so they are cases of `HoldOutcome`, not exceptions. A caller cannot forget them, because the switch does not compile without them.
- The switch has no `default`, so a new case such as `MemberSuspended` is a compile error until it is mapped.
- The count and the save can race between two requests from the same member. A unique constraint on `(member_id, title_id)` closes the duplicate race; the limit race needs a lock on the member row if it matters.
- Tests: `HoldServiceSpec` covers each outcome, with the limit at 4 holds (placed) and 5 holds (refused).
