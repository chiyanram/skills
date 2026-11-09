---
description: A design cites a method at a line it has moved from. The design review should mark that decision a conflict and give the new line.
expected_outcome: The decision that rests on the cite gets a conflict verdict for a stale cite, naming line 40 as where remind() is now.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this design with crq before I approve it. Give every decision one verdict.

The design:

```markdown
## Design
1. Reuse `ReminderJob.remind()` at `ReminderJob.java:26` to send the new overdue notice; it already loads the member.
2. Add `OverdueNotice` as a record next to `Loan`.
3. One slice: the notice is sent for a loan one day overdue; proved by `./gradlew test --tests OverdueNoticeSpec`.
```

The code at the default branch:

```java
// src/main/java/library/ReminderJob.java
26    private final Clock clock;
27
...
40    void remind(final Loan loan) {
41        final Member member = members.find(loan.memberId());
```
