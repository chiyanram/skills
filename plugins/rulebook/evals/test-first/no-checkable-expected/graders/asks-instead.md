---
type: llm
---

The spec names no input, no member and no expected value, so no test can check it.

PASS if the output ends by asking for what is missing (which members, what the report shows now, what it should show) and writes no test as the commit.

FAIL if the output writes a test from a guessed expected result, or proposes a fix.
