---
type: llm
---

Check CC3: every remote call has a client connect and read timeout that ends the call.

PASS if the review says the `RestClient` has no connect or read timeout and recommends setting both.

FAIL if the missing timeout is not mentioned.
