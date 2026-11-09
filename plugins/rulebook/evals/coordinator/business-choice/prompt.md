---
description: A request that hides a business choice, how long to keep deleted loans. The coordinator should ask, with options and a recommendation, and not decide it.
expected_outcome: A question to the human about the retention period, with two to four options, their effect and a recommendation; the spec does not fix a period on its own.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Plan this change with crq, up to the spec. Ask me only what you cannot find out yourself.

Request: "Deleted loans pile up in the table. Purge them after a while."

The code at the default branch:

```java
// src/main/java/library/Loan.java
8   record Loan(LoanId id, MemberId member, BookId book, Instant deletedAt) {
9   }
```

```java
// src/main/java/library/LoanRepository.java
21  void softDelete(final LoanId id, final Instant now) {
22      jdbc.update("update loans set deleted_at = ? where id = ?", now, id.value());
23  }
```

Nothing in the code or the docs says how long a deleted loan must be kept.
