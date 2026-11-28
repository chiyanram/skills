---
type: llm
---

Check: a controller binds, delegates and shapes the response; a branch that chooses an outcome goes in a service.

PASS if `LoanController` holds no repository and has no `if` on renewals, a reservation or the due date; it calls a service and maps the outcome that the service returns. A `switch` that lists the returned outcome's cases is shaping and passes.

FAIL if `LoanController` still calls a repository, or still holds an `if` (or ternary) that tests renewals, a reservation or the due date to choose the status.
