---
description: A request for tests of a booking service that tempts the agent to mock its own repository and calculator. The agent should double only what others own.
expected_outcome: Own classes are not mocked (U3) and, in the integration test, only the third-party payment HTTP API is faked at the wire (TM2).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, write the tests for `BookingService.confirm`: show the spec and the integration test, and say which doubles each uses.

```java
final class BookingService {
    private final BookingRepository bookings;      // our class, Spring Data JPA, Postgres
    private final PriceCalculator prices;          // our class, pure
    private final PaymentGateway payments;         // client for a third-party HTTP payment API

    Booking confirm(final BookingId id) {
        final Booking booking = bookings.get(id);
        final Money price = prices.priceFor(booking);
        payments.charge(booking.customer(), price);
        return bookings.save(booking.confirmed(price));
    }
}
```
