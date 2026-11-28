```java
final class LateFeePolicy {
    private static final long CENTS_PER_DAY = 25;
    private static final long GRACE_DAYS = 2;

    long feeCents(final LocalDate due, final LocalDate returned) {
        return Math.max(0, ChronoUnit.DAYS.between(due, returned) - GRACE_DAYS) * CENTS_PER_DAY;
    }
}
```
