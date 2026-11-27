---
type: llm
---

Check the guard rule: a new null check or `try`/`catch` on a value from an injected field or an in-repo caller is a finding.

PASS if the pass names the `clock == null` check as a guard on an injected field that should not be there (by the guard rule's words or in plain words), whether it reports it or removes it.

FAIL if the null check is left in place and not mentioned, or is praised as defensive.
