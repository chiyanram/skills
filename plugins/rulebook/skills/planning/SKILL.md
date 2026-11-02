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
| [program-design](references/program-design.md) | PD | you write or review a design's call trees, file trees, types and signatures, build slices and their proof, or change an approved design during the build phase |
| [spec-review](references/spec-review.md) | SR1–SR4, SR6 | you write, revise or review a spec or its design before the approval gate |
| [writing-docs](references/writing-docs.md) | WD1, WD2, WD4, WD5, WD7 | you write or review a design, a spec, a guide or a README, or decide which spec a change updates |
