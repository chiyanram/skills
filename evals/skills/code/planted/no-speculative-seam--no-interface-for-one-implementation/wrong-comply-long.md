## FeeCalculator

```java
public interface FeeCalculator {
    long feeCents(BranchId branch, LocalDate due, LocalDate returned);
}

@Service
class FeeCalculatorImpl implements FeeCalculator {
    private final FeeProperties properties;

    FeeCalculatorImpl(final FeeProperties properties) {
        this.properties = properties;
    }

    @Override
    public long feeCents(final BranchId branch, final LocalDate due, final LocalDate returned) {
        final FeeProperties.Rate rate = properties.rateFor(branch);
        final long chargedDays = Math.max(0, ChronoUnit.DAYS.between(due, returned) - rate.graceDays());
        return Math.multiplyExact(chargedDays, rate.centsPerDay());
    }
}
```

## Settings

```java
@Validated
@ConfigurationProperties("library.fees")
record FeeProperties(@NotNull Rate defaults, Map<String, Rate> branches) {
    record Rate(@Positive long centsPerDay, @PositiveOrZero int graceDays) {}

    Rate rateFor(final BranchId branch) {
        return branches.getOrDefault(branch.value(), defaults);
    }
}
```

```yaml
library:
  fees:
    defaults:
      cents-per-day: 25
      grace-days: 2
    branches: {}
```

Every branch uses the defaults today; a new branch with another rate needs only a YAML entry. The interface lets `ReturnServiceSpec` mock the calculator.
