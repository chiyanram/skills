## Verdicts

| # | claim | verdict | evidence | action |
|---|---|---|---|---|
| 1 | `pickupBy()` can be null in `isDue` | does not hold | The compact constructor of `Reservation` calls `Objects.requireNonNull(pickupBy)`, so no `Reservation` with a null `pickupBy` can exist. | Dismiss. A null check in `isDue` would be dead code. |
| 2 | `due.sort(...)` throws on the `toList()` result | holds | `Stream.toList()` returns an unmodifiable list, and its `sort` throws `UnsupportedOperationException`, even for an empty list. | Act on it. |
| 3 | `LocalDate.now(clock)` uses the wrong zone | not decided | The zone comes from the injected `Clock`, whose bean is outside the diff. | Check the `Clock` bean's zone against the library's zone before acting. |

## Fix for 2

```java
List<Reservation> dueToday(final List<Reservation> all) {
    return all.stream()
        .filter(this::isDue)
        .sorted(Comparator.comparing(Reservation::pickupBy))
        .toList();
}
```

A test with two due reservations in reverse order shows the fix: it throws on the current code and passes after.
