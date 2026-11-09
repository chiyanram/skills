---
description: A bug spec with no expected result a test can check. The test-first run should ask what is expected, and write no test.
expected_outcome: Status asked, with a question about the expected result; no test is written.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, do the test-first step of the bug lane for this bug spec. Show the test you would commit and the command
that proves it fails.

Bug spec:
- Current: the overdue report looks wrong for some members.
- Expected: the report is right.

The code at the branch head:

```java
// src/main/java/library/OverdueReport.java
14  List<ReportLine> lines(final LocalDate today) {
15      return loans.overdue(today).stream().map(ReportLine::of).toList();
16  }
```
