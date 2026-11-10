---
description: Two real findings with the wrong grade. The verify pass should lower the grade the evidence does not support, and never raise the other.
expected_outcome: F1's verdict sets grade cited (or walked), lower than the finder's ran; F2's verdict keeps grade cited or leaves the grade out, and never sets walked or ran.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the verify pass of the code review on these findings, before a human sees them. Give each finding one bucket
(act_on, consider, noted or dismissed) and a one-line why. The approved spec says: "AC-1: a member may hold at most 3
loans."

The diff:

```diff
--- a/src/main/java/library/LoanService.java
+++ b/src/main/java/library/LoanService.java
@@ -30,4 +30,4 @@ final class LoanService {
     Loan lend(final MemberId member, final BookId book) {
-        if (loans.countOpen(member) >= MAX_OPEN) {
+        if (loans.countOpen(member) > MAX_OPEN) {
             throw new LoanLimitReached(member);
         }
```

The findings:

```json
[{"id": "F1", "lens": "spec", "file": "src/main/java/library/LoanService.java", "line": 31,
  "rule": "CR1", "severity": "blocker", "grade": "ran",
  "evidence": "line 31 now uses > instead of >=",
  "finding": "A member with 3 open loans can take a 4th, against AC-1.",
  "fix": "Keep >= MAX_OPEN."},
 {"id": "F2", "lens": "correctness", "file": "src/main/java/library/LoanService.java", "line": 31,
  "rule": "correctness", "severity": "warning", "grade": "cited",
  "evidence": "line 31",
  "finding": "The limit check is off by one.",
  "fix": "Keep >= MAX_OPEN."}]
```

No test was run: F1's evidence names the line, it shows no run.
