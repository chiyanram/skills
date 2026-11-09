---
description: A branch diff with a restating comment and a parameter nothing reads. Cleanup should remove both and keep behaviour and evidence the same.
expected_outcome: The comment and the unused parameter (with its callers' argument) are removed; no behaviour changes; the evidence rows are run again with the same result.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, run the cleanup step on this branch diff. Show the cleanup commits you would make and anything you would
defer. The implementer's evidence row: `./gradlew test --tests FineCalculatorSpec` → passed.

```diff
--- a/src/main/java/library/FineCalculator.java
+++ b/src/main/java/library/FineCalculator.java
@@ -10,3 +10,8 @@ final class FineCalculator {
+    // compute the fine
+    long fineCents(final int daysLate, final boolean verbose) {
+        return daysLate >= 7 ? 200 : 0;
+    }
--- a/src/main/java/library/ReturnService.java
+++ b/src/main/java/library/ReturnService.java
@@ -30,1 +30,1 @@ final class ReturnService {
-        final long fine = 0;
+        final long fine = fines.fineCents(daysLate, false);
```

`fineCents` has no other caller.
