---
type: llm
---

Check TY5: money is held as `BigDecimal` or as a `long` of minor units, never `float` or `double`.

PASS if the review flags `price` (and the deposit calculation) as `double` and recommends `BigDecimal` or minor units.

FAIL if the `double` money is accepted or not mentioned.
