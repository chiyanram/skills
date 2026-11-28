# PR readiness

What a PR body holds before the person merges it, the extra items of a one-way door, and when a PR is ready. Read it
when you write a PR body, check one before merge, or call a PR ready.

## Rules

- Open the body with its reason in one sentence and a link to the approved spec, because a person or reviewer who
  does not know why cannot judge whether the change does it. Quote the person's approval and the spec commit it
  covers. A change with no spec links its ticket.
- Put the evidence table from `code`'s verify notes in the body, because the merger needs the evidence without
  running anything again.
- Trust an evidence row or a verdict from an older commit only when `git diff <base>...<old> | git patch-id --stable`
  prints the same id as it does for the head; otherwise run it again, because a rebase gives the change a new commit,
  and only an equal patch id shows the change itself is the same.
- State "Breaking change: yes" or "no", and for yes, what callers must change, because an unannounced break reaches
  callers before anyone warns them.
- State in one line how to roll the change back or switch it off, because the person on call needs that line when
  the change fails. A plain revert says "Rollback: revert this PR; no data changes".
- Show the change as a tree of changed files, each marked added, changed or deleted, or as a call tree, because a
  picture shows its shape before the lines. A one-file change takes a one-line "Change:".
- Name the one to three riskiest places under "Where to look", because the person's review time is best spent where
  a mistake costs most.
- For a one-way door, list under their own heading each dependency's failure plan, timeout and retry, an alert per new
  failure, the expected load and a staged rollout, because an irreversible change cannot be fixed after shipping.
- Open a PR ready for review. Open a draft only for work that will take more commits before anyone should read it,
  and mark it ready when the last one is pushed, because a draft hides finished work from its reviewers.
- Call a PR ready to merge only when every required check on its head commit passed and the host reports it mergeable,
  such as `gh pr view <n> --json mergeStateStatus` printing `CLEAN`, and read it again after any edit to the body,
  because an edit can start a run that cancels the one that passed.
- After a merge command, read the PR back (`gh pr view <n> --json state,mergedAt,baseRefName`): landed reads merged,
  with trunk as its base, because a merge queue or a requested auto-merge reports success without a merge.

## Stacked PRs

A **stack** is a chain of PRs, each based on the branch of the one below it, the bottom one on **trunk** (both in
[glossary.md](glossary.md), with **verdict**).

- Give each PR its own verdict, such as from the rulebook `code-reviewer` agent, because an author checks what it
  meant to build. Green checks and an approving bot are not a verdict.
- Land only the unbroken run of `PASS` from the bottom: walk up from the lowest unmerged PR and stop at the first one
  without `PASS`. A `PASS` above it waits, because it cannot land without the code below it.
- List the landing order and name the next PR to merge, with its verdict and why it is next; the person merges it,
  as `code`'s review-run notes keep every merge theirs. Read it back after each merge: a PR whose base is still its
  parent's branch merged into that branch, not trunk.
- Arm auto-merge only on the person's yes, and only on a PR whose verdict covers its current head, because it lands
  whatever head is ready.
- After a merge, the next PR's base moves to trunk and its patch onto the merge result, pushed with
  `--force-with-lease`. Do it only on the person's yes (stop 3), then trust its verdict only by the patch-id rule above.
- While the stack lands, change no other branch or base. When a merge stalls, find out why before you change
  anything, because a merge lands whatever its branch and base hold at that moment.

## Good / Bad

**Bad**
```text
Fixes renewal. See commits.
```
No reason, no evidence, no rollback, and no hint where a mistake would hide.

**Good**
```text
Why: a reserved loan could be renewed; it now cannot. Spec: #42
Breaking change: no
Rollback: revert this PR; no data changes.
Where to look: LoanService.renew, the reservation check.
Evidence at 4f2c9e1: (the evidence table from `code`'s verify notes)
Change:
  M src/main/java/library/LoanService.java
  A src/test/groovy/library/RenewalSpec.groovy
```
The merger reads why, what could break, how to undo it and where to look first.

## Review

Walk the PR body and its checks before merge. Each line is a finding.

- No one-sentence reason, no spec or ticket link, or a spec with no quoted approval, at the top.
- No evidence table at the pushed commit.
- No breaking-change line, or a "yes" with no change for callers.
- No rollback line.
- A change of two files or more with no file tree or call tree.
- No "Where to look" with one to three places.
- A one-way door missing a readiness item.
- A PR called ready while a required check on its head is pending, failed or cancelled.
- An evidence row or verdict from an older commit with no patch-id match to the head.
- A stacked PR merged above one without `PASS`, a merge done by an agent, or a merge reported with no read-back.
