---
description: A small diff changes the output format of a shared helper. The review should name each consumer outside the diff at file:line, find the lookup that stops matching stored rows, and name a run of the real code that proves the claim the change rests on. Today's skill has no step for consumers outside the diff; the planned blast-radius piece adds it.
expected_outcome: The review lists the three consumers from the grep at file:line, finds that MemberLookupService no longer matches phones stored in the old format, and asks for a test or query against the real code before the change is called safe.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Review this diff. The author says: "Small cleanup, `normalize` now returns E.164. Nothing else changes."

```diff
 final class PhoneNumbers {
     static String normalize(final String raw) {
         final String digits = raw.replaceAll("[^0-9+]", "");
-        return digits.startsWith("+") ? "00" + digits.substring(1) : digits;
+        return digits.startsWith("00") ? "+" + digits.substring(2) : digits;
     }
 }
```

The diff changes no other file. The author ran this grep:

```text
$ grep -rn "PhoneNumbers.normalize" src/main
src/main/java/lib/sms/SmsSender.java:41:        gateway.send(PhoneNumbers.normalize(member.phone()), text);
src/main/java/lib/member/MemberLookupService.java:57:        return members.findByPhone(PhoneNumbers.normalize(input));
src/main/java/lib/member/MemberImport.java:28:        row.setPhone(PhoneNumbers.normalize(csv.get("phone")));
```

`members.phone` holds about 40,000 rows written by `MemberImport` before this change. `findByPhone` is a derived query: `where phone = :phone`.
