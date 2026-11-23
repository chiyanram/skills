---
type: llm
---

Check: nothing may turn a failure green; a retry hides the cause of a flaky test.

PASS if the reply recommends against `@Retry` (or any rerun on failure) as the fix, because it hides the race.

FAIL if the reply accepts or adds `@Retry` or a rerun, even beside another change.
