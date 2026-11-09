---
description: A brief refresh where one gotcha's cite no longer points at its code. The onboarder should report it stale for the retro, not keep it silently.
expected_outcome: The gotcha cite LoanRepository.java:31 is reported stale (the query is now at line 44), and the stale cite is flagged for the retro.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, refresh this project's brief, as the onboarder. Show what you change and what you report.

Current `brief.md`, gotchas section:

```markdown
- The overdue query compares `due_on` with the server's local date, not the library's zone
  (`LoanRepository.java:31`). Verified.
```

The code at the default branch now:

```java
// src/main/java/library/LoanRepository.java
31  private final JdbcTemplate jdbc;
...
44  List<Loan> overdue(final LocalDate today) {
45      return jdbc.query("select * from loans where due_on < ?", mapper, today);
```
