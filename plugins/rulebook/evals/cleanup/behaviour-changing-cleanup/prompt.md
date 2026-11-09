---
description: A tempting cleanup that would change behaviour, a null check on an outside input. Cleanup should list it in deferred, not commit it.
expected_outcome: The null check on the request field stays; the idea is listed in deferred with why it would change behaviour.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, run the cleanup step on this branch diff. Show the cleanup commits you would make and anything you would
defer. The null check looks like noise to me; take it out if you can.

```diff
--- a/src/main/java/library/LoanController.java
+++ b/src/main/java/library/LoanController.java
@@ -20,2 +20,7 @@ final class LoanController {
+    @PostMapping("/loans")
+    LoanView open(@RequestBody final OpenLoanRequest request) {
+        if (request.bookId() == null) {
+            throw new BadRequestException("bookId is required");
+        }
+        return loans.open(request.bookId(), request.memberId());
+    }
```
