# The plan card

One comment on the ticket, updated as each stage ends, so another session or machine resumes from it. Read it when
you post, update or resume from a card.

## Shape

```text
crq · #502 — fix the health probe       lane: bug     flag: –
  [x] intake      ticket, map #500, blocker #498 (closed), no linked PR
  [x] grill       2 questions, answered
  [ ] red test
  [ ] build
  [ ] review      code + testing
  [-] spec        n/a: the ticket already has 3 acceptance criteria
  [-] deslop      n/a: optional, not turned on
  [ ] check       module: make verify-module MOD=probe-worker
  [ ] PR
```

- Post one card, and edit it in place; a second card splits the truth in two.
- Tick a line only on `status: done`, and add what the stage wrote: a path, a link or a count.
- Write each skip as `[-] <stage>  n/a: <why>`, because a skip with no reason reads as forgotten.
- Put the bug lane's criterion line and the person's approval, quoted, under the card.

## Resuming

Read the card, then `git log` on the branch. Compare what is done with what is pending, start at the first unchecked
line, and redo nothing. When the card and the history disagree, the history wins: fix the card first.

## The report

End each session with these sections, in this order, each one line or "none":

```text
Decision        what was decided, and by whom
What ran @SHA   the commands and their results, at the pushed commit
Open questions  each with its decider
Deviations      each change from the approved design, with why
Follow-ups      each ticket filed
Learnings       what a skill got wrong or lacked, for skill feedback
Next            the next stage, or the one step the person takes
```
