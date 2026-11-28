## LateFeePolicy

```java
final class LateFeePolicy {
    private final Map<BranchId, Rate> rates;
    private final Rate standard = new Rate(25, 2);

    LateFeePolicy(final Map<BranchId, Rate> rates) {
        this.rates = Map.copyOf(rates);
    }

    long feeCents(final BranchId branch, final LocalDate due, final LocalDate returned) {
        final Rate rate = rates.getOrDefault(branch, standard);
        final long chargedDays = Math.max(0, ChronoUnit.DAYS.between(due, returned) - rate.graceDays());
        return Math.multiplyExact(chargedDays, rate.centsPerDay());
    }

    record Rate(long centsPerDay, int graceDays) {}
}
```

## No interface

One class implements the fee rule and tests use the real one, so a `FeeCalculator` interface would add a layer and hide nothing. It can be extracted when a second implementation exists.

## Per-branch rates

The map is empty today, so every branch gets 25 cents after 2 grace days. A branch with another rate is one map entry.

| days late | expected cents |
|---|---|
| 2 | 0 |
| 3 | 25 |
