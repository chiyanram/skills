---
description: An automated reviewer left three findings on a diff; one is false, one is true, and one cannot be decided from the diff. The skill should check each claim against the code before it tells the author to act, dismiss the false one with the line that disproves it, and keep the true one. Today's skill has no step to verify a review claim; the planned "verify each claim" and verdict pieces add it. Its true finding is covered by the stack notes.
expected_outcome: Finding 1 does not hold, because the compact constructor rejects a null pickupBy; finding 2 holds, because Stream.toList() is unmodifiable and sort throws; finding 3 is not decided without the clock's zone.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code An automated reviewer left three findings on the diff below. For each one, say whether the author should act on it, and why.

```java
record Reservation(long id, long memberId, LocalDate pickupBy) {
    Reservation {
        Objects.requireNonNull(pickupBy);
    }
}

@Service
class PickupReminder {
    private final Clock clock;

    PickupReminder(final Clock clock) {
        this.clock = clock;
    }

    boolean isDue(final Reservation reservation) {
        final LocalDate today = LocalDate.now(clock);
        return reservation.pickupBy().minusDays(1).isEqual(today);
    }

    List<Reservation> dueToday(final List<Reservation> all) {
        final List<Reservation> due = all.stream().filter(this::isDue).toList();
        due.sort(Comparator.comparing(Reservation::pickupBy));
        return due;
    }
}
```

Findings:

1. `PickupReminder.isDue`: `reservation.pickupBy()` can be null and throw a `NullPointerException`. Add a null check.
2. `PickupReminder.dueToday`: `toList()` returns an unmodifiable list, so `due.sort(...)` throws `UnsupportedOperationException`.
3. `PickupReminder.isDue`: `LocalDate.now(clock)` uses the wrong time zone, so reminders go out on the wrong day.

The `Clock` bean is defined in a configuration class that is not in the diff.
