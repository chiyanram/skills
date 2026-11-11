---
description: A branch renames an internal repository method and keeps the old one as a delegating shim, with one caller still on it. The pass should flag the shim and the caller.
expected_outcome: The kept shim and the caller left on the old path are both named (DS5).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/library/MemberRepository.java
+++ b/src/main/java/library/MemberRepository.java
@@ -9,8 +9,14 @@ interface MemberRepository {
-    Optional<Member> findByEmail(String email);
+    Optional<Member> findByEmailAddress(EmailAddress email);
+
+    /** Kept for compatibility. */
+    default Optional<Member> findByEmail(final String email) {
+        return findByEmailAddress(EmailAddress.of(email));
+    }
--- a/src/main/java/library/SignupService.java
+++ b/src/main/java/library/SignupService.java
@@ -30,7 +30,7 @@ final class SignupService {
-        if (members.findByEmail(request.email()).isPresent()) {
+        if (members.findByEmailAddress(EmailAddress.of(request.email())).isPresent()) {
```

`MemberRepository` is used only inside this repository. `grep -rn 'findByEmail(' src` also shows
`src/main/java/library/ReminderJob.java:41:        members.findByEmail(address)`.
