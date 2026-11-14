---
description: A design retries a fine's charge on a timeout with no idempotency key. The tool should find the double charge, reachable from the retry decision, and propose one closure.
expected_outcome: A blocker scenario for the double charge, with a trigger, a chain, a first sign and decision 2 as its hit, closed by one closure such as an idempotency key.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/toolbox:break-design Try to break this design before I approve it. Report each break scenario.

The spec's AC-1: "A member returning a book 7 or more days late is charged a fine of 2.00."

The design:

```markdown
## Design
1. On return, `ReturnService.returnBook()` computes the fine with `FineCalculator`.
2. It calls `PaymentClient.charge(memberId, amount)`, the outside payment service, with a 3-second timeout. On a
   timeout it retries the same call up to 3 times.
3. When a charge returns success, it marks the loan closed. When all tries fail, it leaves the loan open and logs
   `fine.charge.failed` with the loan id.
4. Alternative rejected: charging at the next login, because members forget.
5. One slice: a late return charges the fine; proved by `./gradlew test --tests ReturnServiceSpec`.
```

The code at the default branch:

```java
// src/main/java/library/PaymentClient.java
8  public interface PaymentClient {
9      ChargeResult charge(MemberId memberId, Money amount);
10 }
```
