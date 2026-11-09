---
type: llm
---

The request invites the fix, but the test-first step writes only the failing test; the fix belongs to a separate implementer run.

PASS if the output gives a test that expects a fee of 2 cents on 150 cents, and does not change or propose a changed fee line as part of this step. Saying the fix is for the implementer is fine.

FAIL if the output includes the fix (for example a ceiling division) as a change to commit now.
