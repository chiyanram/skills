---
approved: operator
---

Write one concrete class, such as `LateFeePolicy`, with a method like `long feeCents(LocalDate due, LocalDate returned)`
that charges 25 cents for each day after the 2 grace days and 0 within them, using a `long` of cents. Add no
`FeeCalculator` interface, because there is one implementation and no fake, so the interface adds a layer and hides
nothing; add it when a second implementation exists. Add no per-branch rate or grace setting and no branch
parameter, because no current caller needs a second rate, and every later change would carry the unused generality.
The reply says both reasons and offers to add the seam when a second branch rate is real.

Allowed extras: named constants, a `Clock`, unit tests at the grace edge, overflow-safe arithmetic, a short note on
how to add a per-branch rate later, or one global settings value for the rate.
