---
description: Two lenses report the same file:line and rule. The verify pass should keep one and dismiss the other as a duplicate.
expected_outcome: One of F1 and F2 is kept (act_on); the other is dismissed as "duplicate of" the kept one.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the verify pass of the code review on these findings, before a human sees them. Give each finding one bucket
(act_on, consider, noted or dismissed) and a one-line why. The contract: a member may withdraw their whole balance.

The diff:

```diff
--- a/src/main/java/bank/AccountService.java
+++ b/src/main/java/bank/AccountService.java
@@ -20,3 +20,3 @@ public final class AccountService {
         final Account account = accounts.find(id);
-        if (amountCents > account.balanceCents()) {
+        if (amountCents >= account.balanceCents()) {
             throw new InsufficientFundsException(id, amountCents);
```

The findings:

```json
[{"id": "F1", "lens": "spec", "file": "src/main/java/bank/AccountService.java", "line": 21,
  "rule": "CR1", "severity": "Act on", "grade": "walked",
  "finding": "A withdrawal of exactly the balance now throws; the contract allows it.",
  "fix": "Restore >."},
 {"id": "F2", "lens": "boundaries", "file": "src/main/java/bank/AccountService.java", "line": 21,
  "rule": "CR1", "severity": "Act on", "grade": "walked",
  "finding": "amount == balance is rejected, against the contract.",
  "fix": "Compare with >."}]
```
