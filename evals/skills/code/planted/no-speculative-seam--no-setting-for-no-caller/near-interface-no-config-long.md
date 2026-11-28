## FeeCalculator

```java
public interface FeeCalculator {
    long feeCents(LocalDate due, LocalDate returned);
}

@Service
class FeeCalculatorImpl implements FeeCalculator {
    private static final long CENTS_PER_DAY = 25;
    private static final long GRACE_DAYS = 2;

    @Override
    public long feeCents(final LocalDate due, final LocalDate returned) {
        final long chargedDays = Math.max(0, ChronoUnit.DAYS.between(due, returned) - GRACE_DAYS);
        return Math.multiplyExact(chargedDays, CENTS_PER_DAY);
    }
}
```

## Per-branch settings: not added

No current caller needs a second rate: `ReturnService` is the only caller and every branch charges 25 cents after 2 grace days. A per-branch setting would be generality that every later change must carry. The constants live in the class until a branch with another rate is ticketed.

## Tests

| days late | expected cents |
|---|---|
| 0 | 0 |
| 2 | 0 |
| 3 | 25 |
| 10 | 200 |
