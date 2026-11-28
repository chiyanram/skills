```java
return switch (service.reserve(memberId, request.titleId())) {
    case HoldOutcome.Placed p -> ResponseEntity.status(201).body(HoldResponse.from(p.hold()));
    case HoldOutcome.AlreadyHeld _ -> ResponseEntity.status(409).build();
    case HoldOutcome.LimitReached _ -> ResponseEntity.status(409).build();
    default -> throw new IllegalStateException("unknown outcome");
};
```
