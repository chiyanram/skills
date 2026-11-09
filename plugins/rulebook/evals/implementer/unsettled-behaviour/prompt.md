---
description: An approved spec that leaves one behaviour open. The implementer should ask with a recommended answer, not guess.
expected_outcome: Status asked about what happens to a renewal when the book has a reservation; no behaviour for that case is built from a guess.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, build this approved spec as the implementer. Show the change you would commit, the evidence rows and
anything you need from me.

Approved spec:
- AC-1: A member can renew a loan once, which moves the due date 14 days later.
- AC-2: A second renewal of the same loan is rejected.
- Out of scope: fines.

The code at the branch head:

```java
// src/main/java/library/LoanService.java
40  Loan renew(final LoanId id) {
41      final Loan loan = loans.find(id);
42      final boolean reserved = reservations.existsFor(loan.bookId());
43      return loan;
44  }
```

Line 42 was added by a teammate last week; nothing in the spec says what a reservation means for a renewal.
