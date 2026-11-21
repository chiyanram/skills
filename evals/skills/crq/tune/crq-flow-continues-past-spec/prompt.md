---
description: The human typed /crq and answered every question in advance. The flow should go on past the spec to the design and its review in the same turn, and stop only to ask for approval.
expected_outcome: In one turn, a spec and a design are written, a design review runs, and the turn ends at the approval stop with the spec, the design and the review's open findings shown. A short status follows each phase.
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

/rulebook:crq Members may renew a loan at most 3 times.

My answers in advance, so you need not ask them: the limit is 3 for every member; a reserved loan still cannot be
renewed; a member past the limit gets the message "Renewal limit reached". A loan that is reserved and also at the
limit gets "Book is reserved", so the reservation check stays first. `renewals` counts renewals already granted and
starts at 0, so renewals 1 to 3 succeed and the 4th is refused. On any other question, I accept your recommendation,
and the picture is right. Write the spec home in `docs/specs/`. Take the change as far as you can in this turn.

The code at the default branch:

```java
// src/main/java/library/Loan.java
8   record Loan(LoanId id, MemberId member, BookId book, LocalDate due, int renewals) {
9   }
```

```java
// src/main/java/library/LoanService.java
40  Loan renew(final LoanId id, final LocalDate today) {
41      final Loan loan = loans.get(id);
42      if (reservations.isReserved(loan.book())) {
43          throw new RenewalRefused("Book is reserved");
44      }
45      final Loan renewed = new Loan(loan.id(), loan.member(), loan.book(), loan.due().plusDays(14), loan.renewals() + 1);
46      loans.save(renewed);
47      return renewed;
48  }
```
