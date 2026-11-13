---
name: crq
description: Use when you take a change from request to merge, or need its lane or the order of its phases. Lists the phases, who runs each, and each crq reference.
---

# crq

One pipeline takes every change from a request to a merge. A coordinator talks with the human and plans. Fresh
runs build and review. Scripts check what a model must not judge. The human approves the plan and merges.

<!-- lanes-diagram: built by make index from process/lanes-v2.json; do not edit by hand -->
```text
intake ─▶ research ─▶ clarify ─▶ spec ─▶ design ─▶ design-review ─▶ HUMAN approval ─▶ test-first
   ─▶ build ─▶ verify ─▶ cleanup ─▶ code-review ─▶ gate ─▶ pr ─▶ HUMAN merge ─▶ timeline-record

design-review  act-on     ─▶ design  cap design_review_rounds = 3
design-review  round-cap  ─▶ human
approval       changes    ─▶ design
verify         red        ─▶ build   cap ready = 3
code-review    act-on     ─▶ build   cap code_review_rounds = 3
code-review    round-cap  ─▶ human
gate           red        ─▶ build   cap gate_red = 2
```
<!-- /lanes-diagram -->

## Phases

The lane picks which phases run (`lanes` reference). The `planning`, `testing` and `code` skills hold the rules
each phase applies.

| phase | who | produces | rules to apply |
|---|---|---|---|
| intake | coordinator | a ticket with its lane; a map of tickets when the work is unclear | `lanes` |
| research | coordinator, read-only helpers | how the touched code works today, at `file:line`; parts to reuse; test patterns | `spec-review` (planning) |
| clarify | coordinator with the human | answers on the ticket; each open question with its decider, options and recommendation | `spec-review` (planning) |
| spec | coordinator | a draft PR with the intent quoted, acceptance criteria a test can decide, non-goals and edge cases | `acceptance-criteria` (planning) |
| design | coordinator | the chosen shape and a rejected alternative; slices with their proving commands | `program-design`, `spec-review`, `diagrams` (planning) |
| design review | a design-reviewer run, then a verify pass | a verdict per decision and findings | `review-process`, `spec-review` (planning) |
| — | **human** | an explicit approval of the spec and design, at the PR's head, recorded with both hashes | `lanes` |
| build | for a bug, a test-first run; then one fresh implementer run per PR | the slices as commits | `verify-done`, the `testing` skill and the `code` references the diff touches |
| verify | implementer, then the engine's ready check at the pushed commit | an evidence row per AC | `verify-done`, the `testing` skill |
| cleanup | cleanup | a behaviour-neutral tidy diff | `deslop` skill |
| code review | automated review: one finder run per lens, then a verify pass | findings in buckets | `review-process`, `code-review`, `test-integrity` when the diff edits an existing test, and the Review checks of every reference in scope |
| gate | the gate: CI, a queue or a local run | green at the head commit | — |
| PR | implementer | why, evidence, rollback, where to look | `pr-readiness`, `diagrams` (planning) |
| — | **human** | merge | — |
| timeline record | engine, no model | rounds, findings, tokens per phase, rescues | `retro` |
| full retro (only when a human starts one) | retro run | each lesson as a rule, a script, a review check or nothing | `retro` |

## Process files

An engine reads these to run the same process a person runs with `/crq`.

- [lanes.json](process/lanes.json): per lane, whether it needs approval, design review and test-first, its lenses
  and its retro. An engine may make a lane stricter, never looser.
- [lanes-v2.json](process/lanes-v2.json): the phase graph, each phase's actor and outcome edges, the round caps and
  conditions, and per lane its phases, lens cap, review model and effort. It sits beside lanes.json until an engine
  reads it.
- [review.json](process/review.json): the baseline references every automated review reads, whatever the repo's
  own instruction files say.
- [glossary](process/glossary.md): the words every role card and hand-off uses.
- Role cards, one per role, each with three eval scenarios in the plugin's `evals/<role>/`:
  [coordinator](process/roles/coordinator.md), [design-reviewer](process/roles/design-reviewer.md),
  [test-first](process/roles/test-first.md), [implementer](process/roles/implementer.md),
  [cleanup](process/roles/cleanup.md), [finder](process/roles/finder.md), [verify
  pass](process/roles/verify-pass.md), [retro](process/roles/retro.md). The onboarder's card is the engine's own.

## References

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [code-review](references/code-review.md) | CR1–CR8 | when you review a PR's code, or before you split a change |
| [lanes](references/lanes.md) | LN1–LN4 | when you take in a new change, or when a change turns out bigger, riskier or smaller than its lane |
| [pr-readiness](references/pr-readiness.md) | PR1–PR7 | when you write a PR body, or when you check one before merge |
| [retro](references/retro.md) | RT1–RT10 | when the engine writes a merge's timeline record, when a human starts a full retro, or when you write a lesson's PR |
| [review-process](references/review-process.md) | RV1–RV9 | before you run, write or tune a review |
| [test-integrity](references/test-integrity.md) | TI1–TI5 | when you review a diff that edits an existing test, a snapshot or a golden file |
| [verify-done](references/verify-done.md) | VB1–VB12 | when you build a change, before you call it ready, or when you check an implementer's evidence rows |
<!-- /index -->
