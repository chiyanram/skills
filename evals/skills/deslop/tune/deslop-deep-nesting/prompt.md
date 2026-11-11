---
description: A branch adds three levels of nested ifs and a nested ternary. The pass should report both and not restructure the control flow itself.
expected_outcome: Both the deep nesting and the nested ternary are reported (DS9); the control flow is left for review.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/library/FineCalculator.java
+++ b/src/main/java/library/FineCalculator.java
@@ -8,6 +8,22 @@ final class FineCalculator {
+    Money fine(final Loan loan, final LocalDate today) {
+        if (loan.isReturned() == false) {
+            if (today.isAfter(loan.dueDate())) {
+                if (loan.member().isStudent()) {
+                    return Money.cents(daysLate(loan, today) * 10);
+                } else {
+                    return Money.cents(daysLate(loan, today) * 25);
+                }
+            }
+        }
+        return Money.ZERO;
+    }
+
+    String label(final Loan loan) {
+        return loan.isReturned() ? "returned" : loan.isOverdue() ? "overdue" : "on loan";
+    }
```
