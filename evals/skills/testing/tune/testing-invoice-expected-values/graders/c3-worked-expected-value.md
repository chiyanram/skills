---
type: llm
---

Check C3: write the expected value out, worked independently, never computed by the code under test or a copy of its logic.

PASS if the rewrite uses literal expected values worked by hand (net 33.50, gross 40.20) and no expected value calls `calculator` or repeats its formula.

FAIL if any expected value is still computed with `calculator.net(...)` or the VAT formula.
