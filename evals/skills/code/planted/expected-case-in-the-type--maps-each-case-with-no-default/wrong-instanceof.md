```java
final HoldOutcome outcome = service.reserve(memberId, request.titleId());
if (outcome instanceof HoldOutcome.Placed placed) {
    return ResponseEntity.status(201).body(HoldResponse.from(placed.hold()));
} else if (outcome instanceof HoldOutcome.AlreadyHeld) {
    return ResponseEntity.status(409).build();
} else {
    return ResponseEntity.status(409).build();
}
```
