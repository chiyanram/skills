---
name: planning
description: Use when you write or review a spec, its acceptance criteria, a design or a work item before any code exists. Lists each planning reference and when to read it.
---

# Planning

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [acceptance-criteria](references/acceptance-criteria.md) | GA1–GA2, GA4–GA6, AC7–AC10, AC12 | when you write or review the acceptance criteria of a spec |
| [break-the-design](references/break-the-design.md) | BK1–BK4 | when you try to break a design before the approval gate, or when you close the break scenarios it raised |
| [diagrams](references/diagrams.md) | DG1–DG6 | when you draw or review a diagram in a design, a spec, a decision record, a Markdown doc or a chat reply |
| [program-design](references/program-design.md) | PD1–PD7, PD9–PD11 | when you write or review a design's call trees, file trees, types and signatures, or its build slices and their proof, or when the build phase needs to change what the design approved |
| [spec-review](references/spec-review.md) | SR1–SR4, SR6, SR9–SR15, SR17–SR23 | when you write, revise or review a spec or a design before the approval gate |
| [writing-docs](references/writing-docs.md) | WD1–WD2, WD4–WD5, WD7 | when you write or review a design, a spec, a guide or a README, or decide which spec a change updates |
<!-- /index -->
