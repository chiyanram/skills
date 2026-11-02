---
name: planning
description: Use when you write or review a spec, its acceptance criteria, a design or a work item before any code exists. Lists each planning reference and when to read it.
---

# Planning

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

| reference | rule IDs | read it when |
|---|---|---|
| [acceptance-criteria](references/acceptance-criteria.md) | GA1–GA6, CV1, AC7–AC10 | you write or review the acceptance criteria of a spec as Gherkin scenarios |
| [diagrams](references/diagrams.md) | DG | you draw or review a diagram in a design, a spec, a decision record, a Markdown doc, a chat reply or a change-request comment |
| [spec-review](references/spec-review.md) | SR1–SR4, SR6 | you write, revise or review a spec or its design before the approval gate |
