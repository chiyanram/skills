---
type: llm
---

Check: wait on a condition, never on time; sleeps are what make tests flaky.

PASS if the changed spec removes `Thread.sleep(500)` and waits on the condition instead (for example `PollingConditions.eventually`, Awaitility, or a latch), with a timeout.

FAIL if the spec keeps a fixed sleep (even a longer one) as the way to wait.
