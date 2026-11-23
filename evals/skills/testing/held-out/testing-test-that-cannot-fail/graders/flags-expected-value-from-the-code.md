---
type: llm
---

Check: write the expected value out by hand, because a value computed by the code under test shares its defect.

PASS if the review says the expected value uses `calculator.rateFor`, the code under test, and asks for a hand-worked number.

FAIL if the review does not mention that the expected value comes from the calculator itself.
