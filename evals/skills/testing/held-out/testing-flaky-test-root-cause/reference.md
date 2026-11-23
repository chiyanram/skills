---
approved: operator
---

Do not add the retry: it hides the race and lets a real failure pass on a later try. The cause is the fixed sleep: the executor sometimes takes longer than 500 ms. Wait on the condition instead, for example `new PollingConditions(timeout: 5).eventually { assert outbox.messages().size() == 1 }`, so the test waits only as long as needed and fails clearly when the message never comes.
