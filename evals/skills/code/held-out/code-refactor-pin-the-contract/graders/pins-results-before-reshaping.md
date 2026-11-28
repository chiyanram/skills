---
type: llm
---

Check: before a refactor, pin the current results with tests, because a type check and a linter do not show that behaviour is unchanged.

PASS if the reply writes tests of `shippingCostCents` (or gives them as the first step) that are run against the current code before the method is changed, and that include at least one case at a threshold (a total of 5000 for DE, or 10000 for other countries). It passes whether the reply says it ran the tests or gives running them as a step.

FAIL if the reply changes the method before any test exists, writes the tests only after the change, or relies on compiling and the linter as the proof.
