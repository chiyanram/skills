---
type: llm
---

PASS if the output gives one test that withdraws exactly the whole balance and expects it to succeed (no exception, balance zero), says it fails today because `InsufficientFundsException` is thrown, and proposes no change to `AccountService` or any other production file.

FAIL if the output changes or proposes a change to `AccountService.java` (for example `>=` to `>`), writes no test, or the test expects the exception.
