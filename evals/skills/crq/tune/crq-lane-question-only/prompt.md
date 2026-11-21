---
description: The human typed /crq only to ask which lane a patch bump takes. The skill should answer from the lanes reference and not start the steps.
expected_outcome: The answer names the tiny lane and its phases; no grill question, spec or ticket follows.
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:crq Which lane does a patch-level dependency bump take, and which phases does that lane run?
