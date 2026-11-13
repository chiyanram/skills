---
type: llm
---

The design only reads data the page already loads and formats it with an existing helper. No decision changes state,
calls another system or takes new input, so the break catalogue does not apply to any of them.

PASS if the report raises no blocker scenario, and any scenario it does raise is tied to a decision and is reachable
from it. Saying that no decision needed the catalogue is a good answer. A note about formatting is fine as a nit.

FAIL if the report raises a blocker, or invents scenarios the design cannot reach, such as an outage of an outside
service the design never calls.
