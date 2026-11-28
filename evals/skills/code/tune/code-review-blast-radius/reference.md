---
approved: operator
---

The change is not "nothing else changes": it reaches three consumers outside the diff.
`MemberLookupService.java:57` now looks up `+4930…` while the 40,000 stored rows hold `004930…`, written by the old
`MemberImport`, so every lookup of an existing member by phone finds nothing. `MemberImport.java:28` now writes the new
format, so the table holds two formats. `SmsSender.java:41` now sends `+…` to the gateway; whether the gateway accepts
it is not shown and must be proved, not assumed. Ask for a run of the real code before the change is called safe: for
example a repository test that stores a phone in the old format and looks it up through `MemberLookupService`, which
fails on this diff, and a gateway contract test or a query of the stored formats.

Allowed extras: a data migration of `members.phone` to the new format, or a lookup that matches both formats; a
rollout order, a count query of rows per format, a request to split the cleanup from the format
change, or a note on numbers with no prefix.
