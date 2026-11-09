# PR readiness

What a PR body holds before the human merges it, and the extra readiness items of a one-way door. Read it
when you write a PR body, or when you check one before merge.

## Rules

- **PR1** — Open the PR body with its reason in one sentence and a link to the approved spec, because a
  human or finder who does not know why cannot judge whether the change does it.
- **PR2** — Put the evidence table (VB5) in the PR body, because the merger needs the evidence rows without running
  anything again.
- **PR3** — State "Breaking change: yes" or "no", and for yes, what callers must change, because an unannounced break
  reaches callers before anyone warns them.
- **PR4** — State in one line how to roll the change back or switch it off, because the person on call needs that
  line when the change fails.
- **PR5** — Show the change as a tree of changed files, each marked added, changed or deleted, or as a call tree,
  because a picture shows the merger its shape before the lines.
- **PR6** — Name the one to three riskiest places under "Where to look", because the human's review time is best spent
  where a mistake costs most.
- **PR7** — For a one-way door, list each dependency's failure plan, timeout and retry, an alert per new failure, the
  expected load and a staged rollout, because an irreversible change cannot be fixed after shipping.

## When X, use Y

| situation | use | why |
|---|---|---|
| any PR | the body below, in this order | the merger finds each part in the same place |
| the change has no spec (tiny lane) | the reason in one sentence and the ticket link (PR1) | there is no spec to link |
| the rollback is a plain revert | "Rollback: revert this PR; no data changes" (PR4) | the line still tells the person on call it is safe |
| the change is one file | a one-line "Change:" instead of a tree (PR5) | a tree of one file shows nothing |
| the one-way-door lane | the readiness items of PR7, under their own heading | the human approves each irreversible step |

## Good / Bad

### PR1 — The reason first, then the evidence

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
Evidence at 4f2c9e1: (the VB5 table)
Change:
  M src/main/java/library/LoanService.java
  A src/test/groovy/library/RenewalSpec.groovy
```
The merger reads why, what could break, how to undo it and where to look first.

## Decided edges

- **Skip the spec link when** the change is in the tiny lane: link the ticket. — **Do not skip when** the change had
  an approved spec (PR1). — **Confidence** high
- **Skip the tree when** the change touches one file. — **Do not skip when** it touches two files or more (PR5). —
  **Confidence** high
- **Skip PR7 when** the change is not a one-way door. — **Do not skip when** it changes stored data, a public contract
  or a deploy (PR7). — **Confidence** high

## Review checks

Walk the PR body before merge.

- [ ] PR1 — Find the one-sentence reason and the spec link at the top. Each one missing is a finding.
- [ ] PR2 — Find the evidence table (VB5), at the pushed commit. Its absence is a finding.
- [ ] PR3 — Find the breaking-change line, and for yes, what callers must change. Its absence is a finding.
- [ ] PR4 — Find the rollback line. Its absence is a finding.
- [ ] PR5 — For a change of two files or more, find the file tree or call tree. Its absence is a finding.
- [ ] PR6 — Find "Where to look" with one to three places. Its absence is a finding.
- [ ] PR7 — For a one-way door, find each readiness item; the alerts are the design's (SR18). Each one missing is a
  finding.
