---
description: A design charges a fine through an outside payment service and says nothing about what happens when the call fails. The design review should flag it under SR11.
expected_outcome: The payment decision gets an open or conflict verdict that names the missing failure path (SR11).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this design with crq before I approve it. Give every decision one verdict.

The spec's AC-1: "A member returning a book 7 or more days late is charged a fine of 2.00."

The design:

```markdown
## Design
1. On return, `ReturnService.returnBook()` computes the fine with `FineCalculator`.
2. It then calls `PaymentClient.charge(memberId, amount)`, the outside payment service, and marks the loan closed.
3. Alternative rejected: charging at the next login, because members forget.
4. One slice: a late return charges the fine; proved by `./gradlew test --tests ReturnServiceSpec`.
```
