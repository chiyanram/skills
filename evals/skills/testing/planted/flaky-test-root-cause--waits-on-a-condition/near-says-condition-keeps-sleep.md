Wait on the condition: keep `Thread.sleep(500)` and then check `outbox.messages().size() == 1` with PollingConditions.
