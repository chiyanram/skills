---
description: A request with five open business choices. The coordinator should ask at most three in its first round and turn the rest into marked defaults.
expected_outcome: One round with at most three questions, each with choices and a recommendation; the other choices appear as defaults, each marked so "accept all" takes it or the human can change it.
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
