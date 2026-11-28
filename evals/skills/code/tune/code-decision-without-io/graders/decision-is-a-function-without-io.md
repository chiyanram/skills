---
type: llm
---

Check: make each decision a function with no I/O, and keep I/O in a thin method that chooses no outcome.

PASS if the renewal decision, including the new overdue rule, is in one method that takes plain values (the loan or its fields, a reserved flag, today's date) and calls no repository, no no-argument `now()` and no other I/O; and the repository reads and the save are in another method that passes their results in. A method on `Loan` that takes the reserved flag and the date passes.

FAIL if the overdue check or any other part of the renewal decision is in a method that also calls a repository, or if the decision calls `LocalDate.now()` with no argument.
