---
name: crq
description: Use when you take a change from request to merge, or need its lane or the order of its phases. Lists the phases, who runs each, and each crq reference.
---

# crq

One pipeline takes every change from a request to a merge. A coordinator talks with the human and plans. Fresh
workers build and review. Scripts check what a model must not judge. The human approves the plan and merges.

```text
intake ─▶ research ─▶ clarify ─▶ spec ─▶ design ─▶ design review ─▶ HUMAN /approved
   ─▶ build ─▶ verify ─▶ cleanup ─▶ code review ─▶ gate ─▶ pull request ─▶ HUMAN merge ─▶ retro
```

## Phases

The lane picks which phases run (`lanes` reference). The `planning`, `testing` and `code` skills hold the rules
each phase applies.

| phase | who | produces | rules to apply |
|---|---|---|---|
| intake | coordinator | an issue with its lane; a map when the work is foggy | `lanes` |
| research | coordinator, read-only helpers | how the touched code works today, at `file:line`; parts to reuse; test patterns | `spec-review` (planning) |
| clarify | coordinator with the human | answers on the issue; each open question with its decider, options and recommendation | `spec-review` (planning) |
| spec | coordinator | intent quoted, acceptance criteria a test can decide, non-goals, edge cases | `acceptance-criteria` (planning) |
| design | coordinator | the chosen shape and a rejected alternative; slices with their proving commands | `program-design`, `spec-review`, `diagrams` (planning) |
| design review | fresh reviewer | a verdict per decision and findings | `review-process`, `spec-review` (planning) |
| — | **human** | `/approved` on the pull request | — |
| build | one fresh writer per pull request | the slices; for a bug, its failing test first | `strategy` (testing) and the `code` references the diff touches |
| verify | writer, then a script at the pushed commit | an evidence line per acceptance criterion | `strategy`, `value-bar` (testing) |
| cleanup | writer | a behaviour-neutral tidy diff | `deslop` skill |
| code review | fresh reviewer | findings in buckets | `review-process`, and the Review checks of every reference in scope |
| gate | CI | green at the head commit | — |
| pull request | writer | why, evidence, rollback, where to look | `diagrams` (planning) |
| — | **human** | merge | — |
| retro | coordinator | each lesson as a rule, a script check, a review item or nothing | — |

## References

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [code-review](references/code-review.md) | CR1–CR4 | when you review a pull request's code, or before you split a change |
| [lanes](references/lanes.md) | LN1–LN3 | when you take in a new change, or when a change turns out bigger, riskier or smaller than its lane |
| [pr-readiness](references/pr-readiness.md) | PR1–PR7 | when you write a pull request body, or when you check one before merge |
| [review-process](references/review-process.md) | RV1–RV5 | before you run, write or tune a review |
| [verify-done](references/verify-done.md) | VB1–VB7 | when you build a change, before you call it ready, or when you check a writer's proof |
<!-- /index -->
