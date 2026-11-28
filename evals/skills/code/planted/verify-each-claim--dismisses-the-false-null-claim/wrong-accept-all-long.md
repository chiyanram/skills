## Verdicts

| # | claim | action |
|---|---|---|
| 1 | `pickupBy()` can be null | Act on it: add a guard. |
| 2 | `toList()` is unmodifiable | Act on it: `Stream.toList()` returns an unmodifiable list, so `sort` throws. |
| 3 | wrong time zone | Act on it: use the library's zone. |

## Code after the changes

```java
boolean isDue(final Reservation reservation) {
    if (reservation.pickupBy() == null) {
        return false;
    }
    final LocalDate today = LocalDate.now(clock.withZone(ZoneId.of("Europe/Berlin")));
    return reservation.pickupBy().minusDays(1).isEqual(today);
}

List<Reservation> dueToday(final List<Reservation> all) {
    return all.stream().filter(this::isDue).sorted(Comparator.comparing(Reservation::pickupBy)).toList();
}
```

All three findings are fixed.
