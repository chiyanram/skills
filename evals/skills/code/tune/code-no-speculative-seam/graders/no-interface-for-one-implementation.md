---
type: llm
---

Check: add an interface only where two implementations exist now (a test fake counts) or at a module boundary.

PASS if the delivered code has no `FeeCalculator` interface with a single implementation (a concrete class only), and the reply says why: one implementation, so the interface adds a layer and hides nothing. Saying that an interface can be added when a second implementation exists does not fail it.

FAIL if the delivered code declares an interface with one implementation, even when the reply gives testability or future branches as the reason, or if the reply drops the interface without saying why.
