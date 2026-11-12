---
type: llm
---

Check P8: build generators by mapping and combining, not filtering; never loosen the discard limit to pass.

PASS if the answer replaces the heavy `.filter` calls with a generator that maps from bounded draws (for example drawing an integer number of cents in a range) and does not raise the discard limit.

FAIL if the answer keeps the filters that discard most cases, or loosens the discard limit.
