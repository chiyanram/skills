---
description: A small, clean branch diff. Cleanup should find nothing to tidy and make no commit.
expected_outcome: No cleanup commit; the reply says there was nothing behaviour-neutral to tidy.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, run the cleanup step on this branch diff. Show the cleanup commits you would make and anything you would
defer.

```diff
--- a/src/main/java/library/MemberName.java
+++ b/src/main/java/library/MemberName.java
@@ -6,7 +6,7 @@ public record MemberName(String value) {
     public MemberName {
         Objects.requireNonNull(value, "value");
-        if (value.isBlank()) {
+        value = value.strip();
+        if (value.isEmpty()) {
             throw new IllegalArgumentException("a member name is not blank");
         }
     }
```
