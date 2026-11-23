---
description: A spec waits with a sleep and fails about one run in twenty; the author proposes a retry. The skill should replace the sleep with a wait on a condition and reject the retry.
expected_outcome: The sleep becomes a condition wait (for example PollingConditions); the retry is rejected because it hides the flake.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing This spec fails about 1 in 20 CI runs. The author wants to add `@Retry(count = 3)`. What do you recommend? Show the changed spec.

```groovy
def "publishes a reminder when a loan becomes overdue"() {
    given:
    loans.save(overdueLoan())

    when:
    scheduler.runOnce()
    Thread.sleep(500)

    then:
    outbox.messages().size() == 1
}
```

`scheduler.runOnce()` hands the work to an executor and returns at once.
