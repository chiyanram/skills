The new rule goes into the existing check:

```java
@PostMapping("/loans/{loanId}/renew")
ResponseEntity<LoanResponse> renew(@PathVariable final long loanId) {
    final Loan loan = loans.findById(loanId).orElseThrow();
    final boolean overdue = loan.dueOn().isBefore(LocalDate.now(clock));
    if (overdue || loan.renewals() >= 2 || reservations.existsByTitleId(loan.titleId())) {
        return ResponseEntity.status(HttpStatus.CONFLICT).build();
    }
    loan.extendBy(Duration.ofDays(14));
    loans.save(loan);
    return ResponseEntity.ok(LoanResponse.from(loan));
}
```

`Clock` is injected into the controller so the date is testable.

## Test

`LoanControllerTest` is a `@WebMvcTest` with `@MockBean` repositories:

| case | expected |
|---|---|
| due yesterday | 409 |
| 2 renewals | 409 |
| title reserved | 409 |
| none of these | 200 |

The change is one line in production code, so the diff stays small.
