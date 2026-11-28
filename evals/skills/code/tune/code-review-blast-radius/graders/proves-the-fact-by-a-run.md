---
type: llm
---

Check: prove the fact a change's safety rests on by running code, not by argument.

PASS if the review names at least one run of the real code that would prove or disprove the claim, such as a repository or service test that stores an old-format phone and looks it up, a query that counts stored rows per format, or a gateway contract test. It passes whether the review writes the test, gives it as a step, or asks the author for it.

FAIL if the review names no run at all and rests every conclusion on reading the code, or calls a consumer safe with no run behind the claim and no note that it is unproved.
