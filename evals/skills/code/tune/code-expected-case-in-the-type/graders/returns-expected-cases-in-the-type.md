---
type: llm
---

Check: return a foreseeable non-success as a case of a sealed, domain-named return type, and throw only faults.

PASS if `reserve` returns a sealed type (a sealed interface with records, or an enum) that has a case for "already holds this title" and a case for "hold limit reached", and the service throws no exception for either of those two outcomes. Extra cases, such as a member that does not exist, do not fail it.

FAIL if the service throws an exception (checked, unchecked, or `ResponseStatusException`) for either refusal, or signals a refusal with `null`, a `boolean`, a string code or an `Optional`.
