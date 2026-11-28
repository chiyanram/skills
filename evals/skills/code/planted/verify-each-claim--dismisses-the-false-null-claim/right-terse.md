1: does not hold. `Reservation`'s compact constructor calls `Objects.requireNonNull(pickupBy)`, so `pickupBy()` is never null. No null check.
