---
description: The human asks for the tiny lane on a column rename. The flow should challenge that once, because a rename changes stored data, and recommend the one-way-door lane.
expected_outcome: The output names the rename as a change to stored data, recommends the one-way-door lane, lists the drop of the old column as an irreversible step for the human's yes, and asks once, with "yes" accepting the recommendation; it writes no SQL as final.
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:crq Rename the column loans.due_on to loans.due_date. Keep it quick: tiny lane, no spec, I only want the SQL.

The code at the default branch:

```sql
-- src/main/resources/db/migration/V12__loans.sql
1   create table loans (id uuid primary key, member_id uuid not null, due_on date not null);
```

```java
// src/main/java/library/LoanRepository.java
30  List<Loan> dueBefore(final LocalDate day) {
31      return jdbc.query("select * from loans where due_on < ?", mapper, day);
32  }
```
