---
description: The request asks for an interface with one implementation and per-branch configuration that no caller needs. The skill should write one concrete class with the current rate and grace days, and say why it adds no interface and no per-branch setting. Today's skill teaches this in "Before you change code" (step 3) and "Where logic goes" (the interface rule).
expected_outcome: One concrete fee class with 25 cents a day after 2 grace days; no FeeCalculator interface; no per-branch rate; the reply gives the reason for each.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Write the late fee calculation for returns. Create a `FeeCalculator` interface and a `FeeCalculatorImpl`, and make the daily rate and the grace days configurable per branch, because we may open branches with other rates later.

Facts today:

- Every branch charges 25 cents a day after 2 grace days.
- `ReturnService` is the only caller. It has the due date and the return date as `LocalDate`.
- Money is held as a `long` of cents.
- No second fee rule is planned or ticketed.
