---
type: llm
---

Check ER3: a rethrow passes the caught exception as its cause.

PASS if the review says `SettlementFailedException` is thrown without the caught `GatewayException` as its cause and recommends passing it.

FAIL if the dropped cause is not mentioned, or the rethrow is called fine.
