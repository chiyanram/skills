---
description: A request with five open business choices. The coordinator should ask every choice in one round, and turn none into a default the human did not answer.
expected_outcome: One round with all five questions, each with choices and a recommendation; no choice is decided or turned into a default the human did not answer.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Plan this change with crq, up to the spec. Ask me only what you cannot find out yourself.

Request: "Members should get a reminder before a loan is due."

The code at the default branch:

```java
// src/main/java/library/Loan.java
8   record Loan(LoanId id, MemberId member, BookId book, LocalDate due) {
9   }
```

Nothing in the code or the docs says how many days before the due date to remind, by which channel (email, SMS or
both), whether a member may opt out, whether a renewed loan gets a second reminder, or at what time of day reminders
go out.
