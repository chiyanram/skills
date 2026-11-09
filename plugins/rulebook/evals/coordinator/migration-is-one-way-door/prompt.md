---
description: A column rename that changes stored data. The coordinator should propose the one-way-door lane and list the irreversible step for the human's yes.
expected_outcome: The lane is one-way door, and dropping the old column is listed as an irreversible step that waits for the human's yes.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Plan this change with crq, up to the spec. Ask me only what you cannot find out yourself.

Request: "Rename the column loans.due_on to loans.due_date; the old name confuses everyone."

The code at the default branch:

```sql
-- src/main/resources/db/migration/V7__loans.sql
1  create table loans (
2      id        bigint primary key,
3      member_id bigint not null,
4      due_on    date   not null
5  );
```

```java
// src/main/java/library/LoanRepository.java
30  List<Loan> overdue(final LocalDate today) {
31      return jdbc.query("select * from loans where due_on < ?", mapper, today);
32  }
```
