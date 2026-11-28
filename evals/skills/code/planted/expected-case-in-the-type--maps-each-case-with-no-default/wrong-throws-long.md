## HoldService.reserve

```java
@Transactional
Hold reserve(final long memberId, final long titleId) {
    if (holds.existsByMemberIdAndTitleId(memberId, titleId)) {
        throw new AlreadyHeldException(memberId, titleId);
    }
    if (holds.countByMemberId(memberId) >= 5) {
        throw new HoldLimitReachedException(memberId);
    }
    return holds.save(Hold.of(memberId, titleId));
}
```

Both exceptions extend `DomainException`, an unchecked exception with an error code.

## Error mapping

```java
@RestControllerAdvice
class HoldErrors {
    @ExceptionHandler(AlreadyHeldException.class)
    ResponseEntity<ErrorBody> alreadyHeld(final AlreadyHeldException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(ErrorBody.of("HOLD_ALREADY_PLACED"));
    }

    @ExceptionHandler(HoldLimitReachedException.class)
    ResponseEntity<ErrorBody> limit(final HoldLimitReachedException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(ErrorBody.of("HOLD_LIMIT_REACHED"));
    }
}
```

## HoldController

```java
@PostMapping("/members/{memberId}/holds")
ResponseEntity<?> reserve(@PathVariable final long memberId, @RequestBody final HoldRequest request) {
    final Hold hold = service.reserve(memberId, request.titleId());
    return ResponseEntity.status(HttpStatus.CREATED).body(HoldResponse.from(hold));
}
```

| case | status |
|---|---|
| placed | 201 |
| already held | 409 |
| limit reached | 409 |

The controller stays thin, and the global advice gives every error the same shape. A unique constraint on `(member_id, title_id)` backs the duplicate check.
