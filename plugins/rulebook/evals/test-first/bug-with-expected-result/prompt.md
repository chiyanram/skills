---
description: A bug spec with a clear input and expected result. The test-first run should write one test that fails for the stated reason, and change no production file.
expected_outcome: One Spock test that withdraws exactly the balance and expects success; it says the test fails today with InsufficientFundsException; no change to AccountService.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, do the test-first step of the bug lane for this bug spec. Show the test you would commit and the command
that proves it fails.

Bug spec:
- Current: a member with a balance of 50.00 who withdraws 50.00 gets `InsufficientFundsException`.
- Expected: the withdrawal succeeds and the balance is 0.00.
- Unchanged: a withdrawal of more than the balance is still rejected.

The code at the branch head:

```java
// src/main/java/bank/AccountService.java
18  public Receipt withdraw(final AccountId id, final long amountCents) {
19      final Account account = accounts.find(id);
20      if (amountCents >= account.balanceCents()) {
21          throw new InsufficientFundsException(id, amountCents);
22      }
```

Tests live in `src/test/groovy/bank/` and use Spock.
