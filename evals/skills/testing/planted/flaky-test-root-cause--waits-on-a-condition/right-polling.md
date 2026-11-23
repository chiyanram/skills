```groovy
then:
new PollingConditions(timeout: 5).eventually {
    assert outbox.messages().size() == 1
}
```
The sleep is gone.
