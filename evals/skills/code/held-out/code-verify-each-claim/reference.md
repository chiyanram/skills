---
approved: operator
---

Finding 1 does not hold: the compact constructor of `Reservation` calls `Objects.requireNonNull(pickupBy)`, so no
`Reservation` with a null `pickupBy` can exist, and a null check in `isDue` would be dead code. Dismiss it. Finding 2
holds: `Stream.toList()` returns an unmodifiable list, so `due.sort(...)` throws `UnsupportedOperationException`; act on it, for example by sorting in the stream (`.sorted(...)` before
`.toList()`) or by collecting with `Collectors.toCollection(ArrayList::new)`. Finding 3 cannot be decided from the
diff: `LocalDate.now(clock)` uses the zone of the injected `Clock`, which is defined outside the diff; check that bean's
zone against the library's zone before acting, and until then do not act on it.

Allowed extras: a note that the list refuses `sort` even when it is empty or has one element, a test for `dueToday` with two due reservations, a test of `isDue` with a fixed clock, a note that the
three verdicts are "does not hold / holds / not decided", or a request to see the `Clock` configuration.
