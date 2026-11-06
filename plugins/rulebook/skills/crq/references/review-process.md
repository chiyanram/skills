# Review process

How every review in the pipeline runs: design review and code review alike. It covers the passes, what the reviewer
reads, which findings get posted, and how the review checks stay honest. Read it before you run, write or tune a
review.

## Rules

- **RV1** — Run every review as a find pass over every review check, then a fresh verify pass that re-opens each
  finding's evidence before anything is posted, because one pass either misses findings or posts false ones.
- **RV2** — Post a finding only when the change introduced it, shows at `file:line`, can be acted on and the author
  would fix it, because marginal findings bury real ones and slow every merge.
- **RV3** — Give the reviewer the approved spec and design, the full code at the head and the references in scope,
  never the writer's account, because a reviewer that reads the writer's claims grades the claims.
- **RV4** — Report at most five nits in a review and never block on one, because a long list of nits hides the
  findings that matter.
- **RV5** — Log each finding by its review check, with its bucket and what the human did, because a check that
  nobody measures drifts into noise or silence.

## When X, use Y

| situation | use | why |
|---|---|---|
| the verified finding holds, applies and its check blocks | **Act on**: the writer fixes it before the gate | a blocking check failed (RV1) |
| the verified finding holds, but its check does not block | **Consider**: the human decides | it is real, but not a reason to stop |
| the finding is true but the change did not introduce it | **Noted**: a follow-up issue | the change is not the place to fix it (RV2) |
| the evidence does not hold, or the case is a check's "not a finding" | **Dismissed**, with one line why | a false finding costs the writer a round (RV2) |
| the change breaks code it does not touch, such as a caller or an invariant | a finding at the broken line, citing the change | the change introduced the break, so RV2 holds |
| more than 30% of a check's findings are dismissed over 20 findings | rewrite the check with an example | the check is mis-worded or mis-scoped (RV5) |
| a check never fires in 30 reviews where it applies | retire it, or move it to a script | it costs reading time and catches nothing (RV5) |

## Good / Bad

### RV2 — Post only what the change introduced and the author would fix

**Bad**
```text
- Consider renaming `svc` to something clearer. (LoanService.java:12)
- The fine calculation has no upper bound. (FineCalculator.java:30, not in this diff)
- This might be slow for large libraries.
```
A style wish, a problem the change did not touch, and a guess with no evidence. The one real problem gets lost.

**Good**
```text
CR1 · Act on · LoanService.java:44
renew() extends a loan that has an open reservation; the approved spec
says "a reserved loan cannot be renewed". Add the reservation check.
Coverage: 12 of 14 checks applied, 2 not applicable.
```
One finding, introduced by the change, shown at its line, with the fix.

## Decided edges

- **Skip when** the change is in the tiny lane: one find pass with the short checklist is enough. — **Do not skip
  when** the change is a bug, a feature or a one-way door: verify every finding (RV1). — **Confidence** high
- **Skip when** a finding sits in code the change did not touch and does not break: it is Noted, not posted as a
  thread. — **Do not skip when** the change breaks that code: it is the change's finding (RV2). — **Confidence** high
- **Skip when** a writer's commit message explains a choice: the reviewer may read the diff and the commits. — **Do
  not skip when** the text is the writer's summary of its own work or test results: keep it out of the reviewer's
  input (RV3). — **Confidence** medium

## Review checks

Walk the review's summary note, its threads and the finding log.

- [ ] RV1 — Find the coverage line and a verify result for each posted finding. A finding posted without a verify
  result is a finding.
- [ ] RV2 — For each posted finding, check that it cites `file:line` in the change or in code the change breaks, and
  names the fix. A style wish, a guess or a pre-existing problem posted as a thread is a finding.
- [ ] RV3 — Open the reviewer's input. It holds the approved spec and design, the code at the head and the
  references in scope. The writer's own summary in the input is a finding.
- [ ] RV4 — Count the nits. More than five, or a nit marked blocking, is a finding.
- [ ] RV5 — Find a log entry for each finding, with its check, its bucket and the human's action. A finding with no
  entry is a finding.
