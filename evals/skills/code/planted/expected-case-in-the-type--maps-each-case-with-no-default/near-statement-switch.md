```java
final ResponseEntity<?> response;
switch (service.reserve(memberId, request.titleId())) {
    case HoldOutcome.Placed p -> response = ResponseEntity.status(201).body(HoldResponse.from(p.hold()));
    case HoldOutcome.AlreadyHeld _ -> response = ResponseEntity.status(409).body(ErrorBody.of("HOLD_ALREADY_PLACED"));
    case HoldOutcome.LimitReached _ -> response = ResponseEntity.status(409).body(ErrorBody.of("HOLD_LIMIT_REACHED"));
}
return response;
```
The switch lists every case and has no `default`.
