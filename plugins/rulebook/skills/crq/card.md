# The plan card

The session's todo list, one line per stage, ticked as each stage ends. Read it when you write the card or start a
new session on a ticket already under way.

## Shape

```text
crq · #502 — fix the health probe       lane: bug     flag: –
  [x] intake      ticket, map #500, blocker #498 (closed), no linked PR
  [x] grill       2 questions, answered
  [ ] red test
  [ ] build
  [ ] review      code + testing
  [-] spec        n/a: the ticket already has 3 acceptance criteria
  [-] deslop      n/a: optional, the person did not run /toolbox:deslop
  [ ] check       module: make verify-module MOD=probe-worker
  [ ] PR
```

- Write it in the session's todo list, not on the ticket: the ticket stays the person's.
- Tick a line only on `status: done`, and add what the stage wrote: a path, a link or a count.
- Write each skip as `[-] <stage>  n/a: <why>`, because a skip with no reason reads as forgotten.
- Put the bug lane's criterion line under the card, and the person's approval in the PR body, quoted.

## A new session

Rebuild the card from what is there now, because the repo and the tracker are the truth, not memory: the branch and
its `git log`, the spec and design files, the open PR and its checks, and the ticket's comments. Tick each stage whose
output exists, start at the first one that has none, and redo nothing done.

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

Before you write `What ran @SHA`, match each line to a command this session ran at that commit. Write `not run` on a
line with no such command, because the next session trusts the report and runs nothing again.
