---
type: llm
---

Check DS8: a new null check or `try`/`catch` on a value from an injected field or an in-repo caller is a finding.

PASS if the pass names the `try`/`catch` around `stocks.save` as a catch that silences a failure, and reports it for the author or review instead of keeping it as fine.

FAIL if the catch is not mentioned, or the pass calls it acceptable.
