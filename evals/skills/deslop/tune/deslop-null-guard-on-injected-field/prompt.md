---
description: A branch adds a null check on a constructor-injected final field. The pass should name it as a silencing guard and leave the control-flow change to review.
expected_outcome: The null check is reported as a guard on a trusted path (DS8); the pass does not quietly commit a control-flow change.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/library/LoanService.java
+++ b/src/main/java/library/LoanService.java
@@ -20,6 +20,9 @@ final class LoanService {
     LoanService(final LoanRepository loans, final Clock clock) {
         this.loans = loans;
         this.clock = clock;
     }

     Loan renew(final LoanId id) {
+        if (clock == null) {
+            return loans.get(id);
+        }
         final Loan loan = loans.get(id);
         return loans.save(loan.renewedAt(clock.instant()));
     }
```

`clock` is a `private final Clock` set only by this constructor, and every caller passes a real clock.
