---
type: llm
---

Check DS7: an unused member, a vestigial parameter, a commented-out block or a `// removed` note in a touched file is a finding.

PASS if the pass removes the unused `locale` parameter of `sum` (and the `Locale.ROOT` argument), or reports it as dead code.

FAIL if the `locale` parameter is left in place and not mentioned.
