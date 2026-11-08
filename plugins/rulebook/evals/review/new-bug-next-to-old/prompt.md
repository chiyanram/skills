---
description: A diff that adds a new regression next to an older defect it did not touch. The review should block on the new one and keep the old one apart.
expected_outcome: The exact-balance rejection is a finding the change must fix; the fee rounding, if mentioned, is labelled as already present and not this change's finding.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this pull request before it merges. The contract: a member may withdraw their whole balance, and the fee is 1% of the amount, rounded up to the cent.

```diff
diff --git a/src/main/java/bank/AccountService.java b/src/main/java/bank/AccountService.java
--- a/src/main/java/bank/AccountService.java
+++ b/src/main/java/bank/AccountService.java
@@ -18,11 +18,11 @@ public final class AccountService {
     public Receipt withdraw(final AccountId id, final long amountCents) {
         final Account account = accounts.find(id);
-        if (amountCents > account.balanceCents()) {
+        if (amountCents >= account.balanceCents()) {
             throw new InsufficientFundsException(id, amountCents);
         }
         final long feeCents = amountCents / 100;
         accounts.debit(id, amountCents + feeCents);
-        return new Receipt(id, amountCents, feeCents);
+        return new Receipt(id, amountCents, feeCents, clock.instant());
     }
```
