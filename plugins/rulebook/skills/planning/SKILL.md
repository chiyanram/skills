---
name: planning
description: Use when you write or review a spec for a new feature, its acceptance criteria, a design or a work item before any code exists, a break-the-design pass, a map of the decisions for a big goal, or a diagram in a doc or a chat reply. Lists each planning notes file and when to read it.
---

# Planning

A plan earns its place when the builder needs no guess and the reviewer can check every claim in it. Everything below
serves that.

## The order

1. **Research** how the touched code works today and why, blind to the wanted change: [spec-review.md](spec-review.md),
   Research. Done when each claim you will make about today's code has a `file:line`.
2. **Spec**: intent, assumptions, acceptance criteria and out of scope, behaviour only, no paths:
   [spec-review.md](spec-review.md), The spec, and [acceptance-criteria.md](acceptance-criteria.md). Done when every
   behaviour has an AC for its success and one for its failure.
3. **Design**: call trees, file trees, types, slices and their proof, with each claim cited:
   [program-design.md](program-design.md) and [spec-review.md](spec-review.md), The design. Draw each picture by
   [diagrams.md](diagrams.md). Done when every AC has a slice and every slice has a command.
4. **Break it** before approval: walk the break catalogue over each decision that changes state, calls out or takes
   input: [break-the-design.md](break-the-design.md). Done when each kept scenario has exactly one closure.
5. **Review** the spec and design in one round, by the review list at the end of each notes file above. Done when
   every finding is reported, and each open question names its decider.
6. **Approval** is the human's. After it, an AC edit is a spec change and a design change is a `[writer] DEVIATION:`
   note: [program-design.md](program-design.md).

## Notes

- Acceptance criteria of a spec: [acceptance-criteria.md](acceptance-criteria.md).
- Research, the spec's intent and assumptions, a design's claims, failure paths, trust boundaries and seams, ADRs,
  and reviewing a spec or a design: [spec-review.md](spec-review.md).
- A design's call trees, file trees, types and signatures, build slices and their proof, the size of a pull request,
  a prototype, or a change during the build: [program-design.md](program-design.md).
- Trying to break a design, or closing the scenarios that did: [break-the-design.md](break-the-design.md).
- A goal too big for one ticket, where the way is not clear yet: chart a map by [maps.md](maps.md).
- A diagram in a design, a spec, a decision record, a Markdown doc or a chat reply: [diagrams.md](diagrams.md).
- A guide, a README or any project doc, its claims and counts, or which spec a change updates:
  [writing-docs.md](writing-docs.md).

Name a finding by the notes file and its rule's words, quoted.
