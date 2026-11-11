---
description: A real finding whose evidence is graded cited only. The verify pass should bucket it consider, not act_on.
expected_outcome: F1 goes to consider, with a why that names its cited-only grade; it is not act_on.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the verify pass of the code review on this finding, before a human sees it. Give each finding one bucket
(act_on, consider, noted or dismissed) and a one-line why. The approved spec says: "AC-2: page 1 is the first page;
each page holds `size` loans."

The diff:

```diff
--- a/src/main/java/library/LoanQuery.java
+++ b/src/main/java/library/LoanQuery.java
@@ -14,3 +14,4 @@ final class LoanQuery {
     List<Loan> page(final int page, final int size) {
-        return loans.list(0, size);
+        final int offset = page * size;
+        return loans.list(offset, size);
     }
```

The finding:

```json
{"id": "F1", "lens": "spec", "file": "src/main/java/library/LoanQuery.java", "line": 16,
 "rule": "CR1", "severity": "blocker", "grade": "cited",
 "finding": "AC-2 makes page 1 the first page; page * size skips the first page of loans.",
 "fix": "Use (page - 1) * size."}
```
