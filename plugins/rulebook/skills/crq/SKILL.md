---
name: crq
description: Use when you take a change from request to merge, or run one phase of it - picking the lane, intake, research, clarify, spec, design, design review, build, verify, cleanup, code review, gate, pull request and retro. Lists the pipeline, who runs each phase, and each crq reference.
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
| clarify | coordinator with the human | answers on the issue: rounds of at most five questions, each with options and a recommendation | `spec-review` (planning) |
| spec | coordinator | intent quoted, acceptance criteria a test can decide, non-goals, edge cases | `acceptance-criteria` (planning) |
| design | coordinator | two candidate shapes and the chosen one; slices with their proving commands | `program-design`, `spec-review`, `diagrams` (planning) |
| design review | fresh reviewer | a verdict per decision and findings | `spec-review` (planning) |
| — | **human** | `/approved` on the merge request | — |
| build | one fresh writer per merge request | one commit per slice; a bug's failing test first | `strategy` (testing) and the `code` references the diff touches |
| verify | writer, then a script at the pushed commit | an evidence line per acceptance criterion | `strategy`, `value-bar` (testing) |
| cleanup | writer | a behaviour-neutral tidy diff | `deslop` skill |
| code review | fresh reviewer | findings in buckets; at most three rounds | the Review checks of every reference in scope |
| gate | CI | green at the head commit | — |
| pull request | writer | why, evidence, rollback, where to look | `diagrams` (planning) |
| — | **human** | merge | — |
| retro | coordinator | each lesson as a rule, a script check, a review item or nothing | — |

## References

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [lanes](references/lanes.md) | LN1–LN3 | when you take in a new change, or when a change turns out bigger, riskier or smaller than its lane |
<!-- /index -->
