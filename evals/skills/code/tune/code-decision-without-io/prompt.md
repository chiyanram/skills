---
description: A renewal rule sits in a controller beside repository calls, and a new rule must be added so it can be unit-tested without Spring or a database. The skill should make the renewal decision a function with no I/O and leave the controller with no branch that chooses the outcome. Today's skill teaches this in "Where logic goes".
expected_outcome: The renewal decision (renewal count, reserved title, overdue) is one method that takes plain values and calls no repository; the service does the reads and the save; the controller only maps the returned outcome.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Add a new rule: a loan that is overdue cannot be renewed. The team wants the renewal rules unit-tested without Spring and without a database. Show the code after your change.

```java
@RestController
class LoanController {
    private final LoanRepository loans;
    private final ReservationRepository reservations;

    LoanController(final LoanRepository loans, final ReservationRepository reservations) {
        this.loans = loans;
        this.reservations = reservations;
    }

    @PostMapping("/loans/{loanId}/renew")
    ResponseEntity<LoanResponse> renew(@PathVariable final long loanId) {
        final Loan loan = loans.findById(loanId).orElseThrow();
        if (loan.renewals() >= 2 || reservations.existsByTitleId(loan.titleId())) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
        loan.extendBy(Duration.ofDays(14));
        loans.save(loan);
        return ResponseEntity.ok(LoanResponse.from(loan));
    }
}
```

`Loan` has `renewals()`, `titleId()`, `dueOn()` (a `LocalDate`) and `extendBy(Duration)`.
