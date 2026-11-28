---
approved: operator
---

The renewal decision becomes one method with no I/O, for example `RenewalPolicy.decide(Loan loan, boolean titleReserved,
LocalDate today)` or a method on `Loan` that takes the flag and the date. It returns a sealed outcome such as
`Renewable`, `LimitReached`, `TitleReserved` and `Overdue`, and checks `today.isAfter(loan.dueOn())` for the new rule. A
`LoanService` reads the loan and `existsByTitleId`, takes today from an injected `Clock` (`LocalDate.now(clock)`),
calls the decision, and extends and saves the loan only when it is renewable, in one `@Transactional` method.
`LoanController` binds the id, calls the service, and maps the returned outcome to 200 or 409 with a `switch`; it holds
no repository and no `if` on renewals, reservations or the due date. A unit test can call the decision with plain
values.

Allowed extras: unit tests of the decision, a response record, a `switch` with every case listed, a separate status per
refusal, or a note that the overdue edge (due today) counts as not overdue.
