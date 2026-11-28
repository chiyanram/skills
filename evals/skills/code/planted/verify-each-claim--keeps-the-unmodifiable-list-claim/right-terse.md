2 holds: `Stream.toList()` is unmodifiable, so `sort` throws. Use `.sorted(Comparator.comparing(Reservation::pickupBy)).toList()`.
