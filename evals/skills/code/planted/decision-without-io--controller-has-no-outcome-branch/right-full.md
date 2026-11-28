## The decision, with no I/O

```java
sealed interface RenewalDecision {
    record Renewable() implements RenewalDecision {}
    record LimitReached() implements RenewalDecision {}
    record TitleReserved() implements RenewalDecision {}
    record Overdue() implements RenewalDecision {}
}

final class RenewalPolicy {
    private static final int MAX_RENEWALS = 2;

    static RenewalDecision decide(final Loan loan, final boolean titleReserved, final LocalDate today) {
        if (today.isAfter(loan.dueOn())) {
            return new RenewalDecision.Overdue();
        }
        if (loan.renewals() >= MAX_RENEWALS) {
            return new RenewalDecision.LimitReached();
        }
        if (titleReserved) {
            return new RenewalDecision.TitleReserved();
        }
        return new RenewalDecision.Renewable();
    }
}
```

## The service does the I/O

```java
@Service
class LoanService {
    private final LoanRepository loans;
    private final ReservationRepository reservations;
    private final Clock clock;

    // constructor takes all three

    @Transactional
    RenewOutcome renew(final long loanId) {
        final Loan loan = loans.findById(loanId).orElseThrow();
        final RenewalDecision decision = RenewalPolicy.decide(
            loan, reservations.existsByTitleId(loan.titleId()), LocalDate.now(clock));
        if (decision instanceof RenewalDecision.Renewable) {
            loan.extendBy(Duration.ofDays(14));
            loans.save(loan);
        }
        return new RenewOutcome(decision, loan);
    }
}
```

## The controller only maps

```java
@PostMapping("/loans/{loanId}/renew")
ResponseEntity<LoanResponse> renew(@PathVariable final long loanId) {
    final RenewOutcome outcome = service.renew(loanId);
    return switch (outcome.decision()) {
        case RenewalDecision.Renewable _ -> ResponseEntity.ok(LoanResponse.from(outcome.loan()));
        case RenewalDecision.LimitReached _, RenewalDecision.TitleReserved _, RenewalDecision.Overdue _ ->
            ResponseEntity.status(HttpStatus.CONFLICT).build();
    };
}
```

## Unit test of the rules, no Spring, no database

| case | renewals | reserved | due | today | expected |
|---|---|---|---|---|---|
| renewable | 0 | no | 10 Mar | 10 Mar | `Renewable` |
| overdue | 0 | no | 10 Mar | 11 Mar | `Overdue` |
| limit | 2 | no | 10 Mar | 9 Mar | `LimitReached` |
| reserved | 1 | yes | 10 Mar | 9 Mar | `TitleReserved` |

A loan due today is not overdue, so the edge case is renewable.
