```java
final class LateFeePolicy {
    long feeCents(final LocalDate due, final LocalDate returned) {
        return Math.max(0, ChronoUnit.DAYS.between(due, returned) - 2) * 25;
    }
}
```
