---
type: llm
---

Check: the controller maps a returned outcome with a `switch` that lists every case and has no `default`, and never returns 2xx for a refusal.

PASS if `HoldController` uses a `switch` (or switch expression) over the outcome that names the placed case and both refusal cases, has no `default` branch, and gives each refusal a 4xx status. Extra cases in the switch do not fail it.

FAIL if the mapping has a `default` branch, uses an `if`/`else` or `instanceof` chain, returns a 2xx status for a refusal, catches exceptions in the controller, or has no switch over a returned outcome.
