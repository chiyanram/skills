---
name: crq
description: Use when you take a change from request to merge, or need its lane or the order of its phases. Lists the phases, who runs each, and each crq reference.
---

# crq

One pipeline takes every change from a request to a merge. A coordinator talks with the human and plans. Fresh
workers build and review. Scripts check what a model must not judge. The human approves the plan and merges.

```text
intake ─▶ research ─▶ clarify ─▶ spec ─▶ design ─▶ design review ─▶ HUMAN approval
   ─▶ build ─▶ verify ─▶ cleanup ─▶ code review ─▶ gate ─▶ pull request ─▶ HUMAN merge ─▶ retro
```

## Phases

The lane picks which phases run (`lanes` reference). The `planning`, `testing` and `code` skills hold the rules
each phase applies.

| phase | who | produces | rules to apply |
|---|---|---|---|
| intake | coordinator | an issue with its lane; a map of issues when the work is unclear | `lanes` |
| research | coordinator, read-only helpers | how the touched code works today, at `file:line`; parts to reuse; test patterns | `spec-review` (planning) |
| clarify | coordinator with the human | answers on the issue; each open question with its decider, options and recommendation | `spec-review` (planning) |
| spec | coordinator | a draft pull request with the intent quoted, acceptance criteria a test can decide, non-goals and edge cases | `acceptance-criteria` (planning) |
| design | coordinator | the chosen shape and a rejected alternative; slices with their proving commands | `program-design`, `spec-review`, `diagrams` (planning) |
| design review | fresh reviewer | a verdict per decision and findings | `review-process`, `spec-review` (planning) |
| — | **human** | an explicit approval of the spec and design, at the pull request's head | — |
| build | for a bug, a separate run that writes the failing test; then one fresh writer per pull request | the slices as commits | `verify-done`, `strategy` (testing) and the `code` references the diff touches |
| verify | writer, then a script at the pushed commit | an evidence line per acceptance criterion | `verify-done`, `value-bar` (testing) |
| cleanup | writer | a behaviour-neutral tidy diff | `deslop` skill |
| code review | fresh reviewer | findings in buckets | `review-process`, `code-review`, and the Review checks of every reference in scope |
| gate | CI | green at the head commit | — |
| pull request | writer | why, evidence, rollback, where to look | `pr-readiness`, `diagrams` (planning) |
| — | **human** | merge | — |
| retro | coordinator | each lesson as a rule, a script, a review check or nothing | `retro` |

## References

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [code-review](references/code-review.md) | CR1–CR7 | when you review a pull request's code, or before you split a change |
| [lanes](references/lanes.md) | LN1–LN4 | when you take in a new change, or when a change turns out bigger, riskier or smaller than its lane |
| [pr-readiness](references/pr-readiness.md) | PR1–PR7 | when you write a pull request body, or when you check one before merge |
| [retro](references/retro.md) | RT1–RT6 | when a pull request is merged, rescued or reverted, or a defect escapes |
| [review-process](references/review-process.md) | RV1–RV7 | before you run, write or tune a review |
| [verify-done](references/verify-done.md) | VB1–VB8 | when you build a change, before you call it ready, or when you check a writer's proof |
<!-- /index -->
