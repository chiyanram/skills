---
type: llm
---

PASS if all of these hold:
- each of AC-1 and AC-2 has its own evidence row with a plain command (no pipe, `&&` or redirect) and its result;
- a test checks the stripped value, so it fails if the change is reverted;
- the PR body has the reason with a link to the spec, the evidence table, a breaking-change yes or no, a rollback line, the changed files, and where to look first.

FAIL if an AC has no evidence row, the only evidence is "tests pass", or the PR body misses the rollback or the breaking-change line.
