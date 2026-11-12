---
description: A client retries a non-idempotent booking POST in an unbounded loop with no timeout. The review should flag both.
expected_outcome: The missing timeout is reported (CC3); the unbounded retry of a non-idempotent call is reported (CC8).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, review this client for the booking service and list each rule it breaks, with the fix.

```java
@Component
class BookingClient {
    private final RestClient http = RestClient.create("https://bookings.example.test");

    BookingConfirmation confirm(final BookingRequest request) {
        while (true) {
            try {
                return http.post()
                        .uri("/v1/bookings")
                        .body(request)
                        .retrieve()
                        .body(BookingConfirmation.class);
            } catch (final RestClientException e) {
                // try again
            }
        }
    }
}
```

`POST /v1/bookings` creates a new booking each time it is accepted.
