---
name: planning
description: Use when you write or review a design, a plan or a build order before code exists, or when the build needs to change what a design approved. Lists each planning reference and when to read it.
---

# Planning

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

| reference | rule IDs | read it when |
|---|---|---|
| [program-design](references/program-design.md) | PD | you write or review a design's call trees, file trees, types and signatures, build slices and their proof, or change an approved design during the build phase |
