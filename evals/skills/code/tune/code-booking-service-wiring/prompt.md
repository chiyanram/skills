---
description: A bean uses field injection and calls its own transactional method. The review should flag both.
expected_outcome: Field injection is reported (LY6); the self-invoked @Transactional method is reported (SC21).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, review this booking service and list each rule it breaks, with the fix.

```java
@Service
class BookingService {
    @Autowired
    private BookingRepository bookings;

    @Autowired
    private AuditLog audit;

    void confirmAll(final List<BookingId> ids) {
        for (final BookingId id : ids) {
            confirmOne(id);
        }
    }

    @Transactional
    public void confirmOne(final BookingId id) {
        final Booking booking = bookings.getReferenceById(id);
        bookings.save(booking.confirm());
        audit.record("confirmed", id);
    }
}
```

The author expects each `confirmOne` call to run in its own transaction.
