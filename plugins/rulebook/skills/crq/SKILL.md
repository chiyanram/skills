---
name: crq
description: Use when the human types /crq, or asks to take a change from request to merge, or asks for its lane or the order of its phases. Runs the whole change in this session, and stops only for the human's answers, approval and push.
---

# crq

Take one change from a request to an open PR in this session. You drive every phase. The human answers the grill,
approves the spec and the design, and allows the push. An engine such as agent-factory runs the same phases from
`process/` and does not read this file.

When the human only asks which lane or which phase, answer from [lanes](references/lanes.md) and do not start the
steps.

<!-- lanes-diagram: built by make index from process/lanes-v2.json; do not edit by hand -->
```text
intake ─▶ research ─▶ clarify ─▶ spec ─▶ design ─▶ design-review ─▶ HUMAN approval ─▶ test-first
   ─▶ build ─▶ verify ─▶ cleanup ─▶ code-review ─▶ gate ─▶ pr ─▶ HUMAN merge ─▶ timeline-record

design-review  act-on     ─▶ design  cap design_review_rounds = 3
design-review  round-cap  ─▶ human
approval       changes    ─▶ design
verify         red        ─▶ build   cap ready = 3
verify         round-cap  ─▶ human
code-review    act-on     ─▶ build   cap code_review_rounds = 3
code-review    round-cap  ─▶ human
gate           red        ─▶ build   cap gate_red = 2
gate           round-cap  ─▶ human
```
<!-- /lanes-diagram -->

## Stops

Stop only for these five. A phase that ends is not a stop: post its status block (`report.md`) and start the
next step in the same turn.

1. A grill round waits for the human's answers.
2. The spec and the design wait for the human's approval.
3. The next act cannot be undone and the human has not allowed it: a push, a PR, a merge, a migration on shared data,
   a delete.
4. A review or verify loop ends its third round with findings still open (RV9).
5. A subagent ends with status `asked` or `blocked`: show its questions or its cause, and wait (VB1, VB13).

A question about how the flow runs (the order of the subagents, a file name, which lens), decide it. Write it in the
ledger as `Ruling: <what> - <why> - <cost if wrong>` and go on. A question about what the spec or the design means is
never a ruling: it is a grill question (VB1).

## Steps

Keep a ledger beside the spec, in the spec home: one line per phase done, each ruling, each approval. When a new
session starts on the same ticket, read the ledger and continue at the first phase it does not record.

Each subagent below starts fresh. Give it the role card's body and the files its `input` names; never give it what
its `must_not_see` names or this conversation.

1. **Intake.** Restate the request in one sentence. Pick the lane from what it touches ([lanes](references/lanes.md),
   LN1) and put it in the first status block. A tiny change goes to step 7.
2. **Research.** Start a read-only subagent on the code the request touches, with neutral questions only (SR22).
   Do not wait for it: start the grill, and use its facts from round 2.
3. **Grill.** Follow [grill](grill.md). Done when no question is open and the human says the picture is
   right.
4. **Spec and design.** Write them in the spec home, as steps 4 and 5 of the
   [coordinator](process/roles/coordinator.md) card say. Done when its "Done when" holds.
5. **Design review.** Run a [design-reviewer](process/roles/design-reviewer.md) subagent, then a
   [verify pass](process/roles/verify-pass.md) subagent on its findings. Fix each `act_on` finding in the design
   and run both again, at most three rounds. Then stop (stop 2): show the spec, the design and the open `consider`
   findings, and ask for approval. Write the human's words and the `git hash-object` of the spec and the design in the
   ledger (LN4).
6. **Test-first.** In the bug lane, run a [test-first](process/roles/test-first.md) subagent. Check that its test
   fails for the reason the spec states.
7. **Build.** Run an [implementer](process/roles/implementer.md) subagent. Then do the ready check yourself: run
   every evidence row's command, and check that no test was removed, skipped or weakened (VB6). A red row sends the
   implementer back with that row, at most three rounds.
8. **Deslop.** Use the Skill tool for `rulebook:deslop` on the branch diff. Run every evidence row again after it.
   Its reported items go into the final report, not into a commit. Code review then reads the tidied diff.
9. **Code review.** Run one [finder](process/roles/finder.md) subagent per lens, up to the lane's lens cap in
   `process/lanes-v2.json`, each with the baseline in `process/review.json`. Then run one verify pass subagent on all
   findings. Send the `act_on` list, and only that list, to a new implementer subagent, then repeat the ready check
   and this step, at most three rounds. Deslop does not run again.
10. **Gate.** Run the project's full test command at the head commit. Red goes back to step 7, at most two rounds.
11. **PR.** Check that `.factory/pr.md` meets [pr-readiness](references/pr-readiness.md). Then stop (stop 3): show
    the branch, the push command and the PR title, and push only on the human's yes.
12. **Report.** Write the final message as `report.md` says.

## Process files

The engine reads these. The steps above use the same files.

- [lanes.json](process/lanes.json) and [lanes-v2.json](process/lanes-v2.json): each lane's phases, caps and lenses.
- [review.json](process/review.json): the baseline every review reads.
- [glossary](process/glossary.md): the words every role card and hand-off uses.
- Role cards: [coordinator](process/roles/coordinator.md), [design-reviewer](process/roles/design-reviewer.md),
  [test-first](process/roles/test-first.md), [implementer](process/roles/implementer.md),
  [cleanup](process/roles/cleanup.md), [finder](process/roles/finder.md),
  [verify pass](process/roles/verify-pass.md), [retro](process/roles/retro.md).

## References

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [code-review](references/code-review.md) | CR1–CR8 | when you review a PR's code, or before you split a change |
| [lanes](references/lanes.md) | LN1–LN4 | when you take in a new change, or when a change turns out bigger, riskier or smaller than its lane |
| [pr-readiness](references/pr-readiness.md) | PR1–PR7 | when you write a PR body, or when you check one before merge |
| [retro](references/retro.md) | RT1–RT10 | when the engine writes a merge's timeline record, when a human starts a full retro, or when you write a lesson's PR |
| [review-process](references/review-process.md) | RV1–RV11 | before you run, write or tune a review |
| [test-integrity](references/test-integrity.md) | TI1–TI5 | when you review a diff that edits an existing test, a snapshot or a golden file |
| [verify-done](references/verify-done.md) | VB1–VB13 | when you build a change, before you call it ready, or when you check an implementer's evidence rows |
<!-- /index -->
