## LoanService

```java
@Service
class LoanService {
    private final LoanRepository loans;
    private final ReservationRepository reservations;
    private final Clock clock;

    @Transactional
    RenewalOutcome renew(final long loanId) {
        final Loan loan = loans.findById(loanId).orElseThrow();
        if (loan.dueOn().isBefore(LocalDate.now(clock))) {
            return new RenewalOutcome.Overdue();
        }
        if (loan.renewals() >= 2) {
            return new RenewalOutcome.LimitReached();
        }
        if (reservations.existsByTitleId(loan.titleId())) {
            return new RenewalOutcome.TitleReserved();
        }
        loan.extendBy(Duration.ofDays(14));
        return new RenewalOutcome.Renewed(loans.save(loan));
    }
}
```

## LoanController

```java
@PostMapping("/loans/{loanId}/renew")
ResponseEntity<LoanResponse> renew(@PathVariable final long loanId) {
    return switch (service.renew(loanId)) {
        case RenewalOutcome.Renewed r -> ResponseEntity.ok(LoanResponse.from(r.loan()));
        case RenewalOutcome.Overdue _, RenewalOutcome.LimitReached _, RenewalOutcome.TitleReserved _ ->
            ResponseEntity.status(HttpStatus.CONFLICT).build();
    };
}
```

## Test

`LoanServiceSpec` stubs `LoanRepository` and `ReservationRepository` with Spock mocks and a fixed `Clock`, and has one case per outcome. It runs with no Spring context and no database.

| outcome | status |
|---|---|
| `Renewed` | 200 |
| `Overdue` | 409 |
| `LimitReached` | 409 |
| `TitleReserved` | 409 |
