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
@Transactional
HoldOutcome reserve(final long memberId, final long titleId) {
    if (holds.existsByMemberIdAndTitleId(memberId, titleId)) {
        return new HoldOutcome.AlreadyHeld();
    }
    if (holds.countByMemberId(memberId) >= 5) {
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
        default -> ResponseEntity.status(HttpStatus.CONFLICT).body(ErrorBody.of("HOLD_REFUSED"));
    };
}
```

| outcome | status |
|---|---|
| `Placed` | 201 |
| any refusal | 409 |

The refusals are returned, not thrown, so they are visible in the signature. The `default` arm keeps the controller short: every refusal is a 409 with one catalogue code.
