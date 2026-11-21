---
name: crq
description: Use when the human types /crq, or asks to take a change from request to merge, or asks for its lane or the order of its phases. Runs the whole change in this session, and stops only for the human's answers, approval and push.
---

# crq

Take one change from a request to an open PR. Whoever runs it, a person in a chat or an agent, follows the same
steps. The human answers the grill, approves the spec and the design, and allows the push.

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

Stop only for these five. A phase that ends is not a stop: post its status block ([report](report.md)) and start
the next step in the same turn.

1. A grill round waits for the human's answers.
2. The spec and the design wait for the human's approval.
3. The next act cannot be undone and the human has not allowed it: a push, a PR, a merge, a migration on shared data,
   a delete.
4. A review or a build loop ends its third round with work still open (RV9).
5. A subagent ends with a question only the human can answer, or is blocked by a cause outside the change: show the
   question or the cause, and wait (VB1).

When no human is in the session, a stop ends the turn with its question; the next turn reads the ledger and goes on.

A question about how the flow runs (the order of the subagents, a file name, which lens), decide it. Write it in the
ledger as `Ruling: <what> - <why> - <cost if wrong>` and go on. A question about what the spec or the design means is
never a ruling: it is a grill question (VB1).

## Steps

Keep a ledger beside the spec: one line per phase done, each ruling, each approval. When a new session starts on the
same change, read the ledger and continue at the first phase it does not record.

Each subagent below starts fresh. Give it the files its step names, never this conversation, so it judges the work
and not the talk about it (RV1).

1. **Intake.** Restate the request in one sentence. Pick the lane from what it touches ([lanes](references/lanes.md),
   LN1) and put it in the first status block. A tiny change goes to step 7.
2. **Research.** Start a read-only subagent on the code the request touches: how it works today at `file:line`, the
   parts to reuse, the test patterns. Give it neutral questions, never the wanted change (SR22). Do not wait for it:
   start the grill.
3. **Grill.** Follow [grill](grill.md). Done when the frontier is empty and the human confirms the picture.
4. **Spec and design.** Write the spec: the intent in the human's words, the lane, acceptance criteria a test can
   decide, non-goals and edge cases (the `planning` skill). Write the design when the lane needs one: the chosen
   shape, one rejected alternative, and slices, each with the command that proves it.
5. **Design review.** Run a read-only subagent with the spec, the design and the code. It checks each decision
   against the code and the spec, and gives each finding a `file:line` and its evidence. Then run a second fresh
   subagent that sorts each finding into act on, consider, noted or dismissed. Fix each act-on finding and review
   again, at most three rounds. Then stop (stop 2): show the spec, the design and the consider findings, and ask for
   approval. Write the human's words and the `git hash-object` of the spec and the design in the ledger (LN4).
6. **Test-first.** In the bug lane, run a subagent that writes one test that fails for the reason the spec states, and
   commits only that test (VB7).
7. **Build.** Run a subagent with the spec and the design. It builds each slice, writes each changed behaviour's test
   and sees it fail without the change (VB2), and gives one evidence row per criterion: the criterion, the command,
   the result (VB5). Then check its work yourself: run every row's command, and check that no test was removed,
   skipped or weakened (VB6). A red row goes back to a new build subagent, at most three rounds.
8. **Deslop.** Use the Skill tool for `rulebook:deslop` on the branch diff. Run every evidence row again after it.
   Its reported items go into the final report, not into a commit.
9. **Code review.** Run two read-only subagents on the diff, each told nothing of the other: one on the spec (does
   the code do what each criterion says), one on the standards (the [code-review](references/code-review.md) checks
   and the `code` and `testing` skills). In the one-way-door lane, add a third on the irreversible steps (LN3). The
   tiny lane runs one for both. Then one fresh subagent sorts every finding, as in step 5. Send the act-on list, and only that list, to a new build subagent, then repeat step 7's check and this
   step, at most three rounds.
10. **Gate.** Run the project's full test command at the head commit. Red goes back to step 7, at most two rounds.
11. **PR.** Write the PR body to meet [pr-readiness](references/pr-readiness.md). Then stop (stop 3): show the branch,
    the push command and the PR title, and push only on the human's yes.
12. **Report.** Write the final message as [report](report.md) says.

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
