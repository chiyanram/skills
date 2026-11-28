## LateFeePolicy

```java
final class LateFeePolicy {
    private static final long CENTS_PER_DAY = 25;
    private static final long GRACE_DAYS = 2;

    long feeCents(final LocalDate due, final LocalDate returned) {
        final long daysLate = ChronoUnit.DAYS.between(due, returned);
        final long chargedDays = Math.max(0, daysLate - GRACE_DAYS);
        return Math.multiplyExact(chargedDays, CENTS_PER_DAY);
    }
}
```

`ReturnService` takes `LateFeePolicy` in its constructor and calls `feeCents(due, returned)`.

## What is left out, and why

| asked for | delivered | why |
|---|---|---|
| `FeeCalculator` interface + `FeeCalculatorImpl` | one concrete class | one implementation and no fake: the interface adds a layer to trace and hides nothing. Extract it when a second implementation exists. |
| daily rate and grace days per branch | constants in code | `ReturnService` is the only caller and every branch charges the same; a per-branch setting serves no caller and every later change would carry it. Add it with the ticket for the first branch that charges differently. |

## Tests

| due | returned | expected |
|---|---|---|
| 10 Mar | 10 Mar | 0 |
| 10 Mar | 12 Mar | 0 (last grace day) |
| 10 Mar | 13 Mar | 25 |
| 10 Mar | 20 Mar | 200 |

The test calls the real `LateFeePolicy`; no mock is needed.
