---
type: llm
---

Check: for each changed behaviour, name the consumers outside the diff it reaches at file:line, and say what the change does to each.

PASS if the review names `MemberLookupService.java:57` (or `MemberLookupService` with line 57) and says that lookups now use the new format while the stored rows hold the old one, so existing members are no longer found. Naming the other consumers as well does not fail it.

FAIL if the review accepts "nothing else changes", calls the lookup safe, or does not find that stored phones no longer match.
