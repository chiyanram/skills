# Spec review

How a reviewer checks a spec and its design before the approval gate: one round, cited claims, no open question without
a decider, and complete stories. Read it when you write, revise or review a spec or a design before the approval gate.

Contents: Rules · When X, use Y · Good / Bad (SR2, SR3, SR4) · Decided edges · Review checks

## Rules

- **SR1** — Report every finding the rubric produces in one review round; a later-round finding on unchanged text is
  a reviewer miss, because findings raised one per round stretch one review over several rounds.
- **SR2** — In the design, cite `file:line` on the main branch for each claim about today's code, and the reviewer
  opens each cite; the spec names no paths, because an uncited false claim can settle a decision.
- **SR3** — Treat a `file:line` cite in a design that no longer points at the named symbol as a finding, found by a
  check that can be run, because drifted cites are otherwise found only by chance.
- **SR4** — Before the spec is approved, empty its open-questions list or make each item name its decider and why it
  does not block building, because a question with no decider stays open after the build.
- **SR6** — Check each story for actor, action and benefit, scenarios a test can check, and an out-of-scope list,
  because without them the builder guesses who it serves, when it is done, and where it stops.

## When X, use Y

| situation | use | why |
|---|---|---|
| the review finds more than one problem | report them all in this round (SR1) | findings raised one per round stretch one review over several rounds |
| a design sentence states how the code behaves today | a `file:line` cite on the main branch, opened by the reviewer (SR2) | check the request against the actual code and record `file:line`; a spec can say X while the code does Y |
| a spec sentence states how the code behaves today | move the claim and its cite into the design (SR2) | a spec holds no file paths, because they go out of date fast |
| a design carries `file:line` cites | run a check that resolves each cite to its symbol (SR3) | a cite that drifts is a false claim the next reader believes |
| the spec reaches the approval gate with open questions | resolve each, or name its decider and why it does not block (SR4) | an open question with no decider stays open after the build |
| a story has no "as a … so that …" line | add actor, action and benefit (SR6) | without actor, action and benefit, the builder guesses who the story serves |
| a scenario says "works well" or "is fast" | rewrite it as a condition a test can check (SR6) | a vague criterion such as "works well" gives no test a pass condition |
| a story has no out-of-scope list | add one (SR6) | without an out-of-scope list, the builder guesses where the story ends |

## Good / Bad

### SR2 — Cite today's behaviour in the design, not the spec

**Bad**
```markdown
## Design — overdue reminders

Today, loans renew automatically when no other member holds a reservation.
So the reminder job emails only members whose loan is overdue.
```
The claim has no cite, so the reviewer cannot check it. If renewal is manual, the job misses every loan due today.

**Good**
```markdown
## Design — overdue reminders

Today, loans renew automatically when no other member holds a reservation
(`loans/RenewalPolicy.java:42`, `canRenew`, on the main branch).
So the reminder job emails only members whose loan is overdue.
```
The reviewer opens line 42 and confirms the claim before the decision rests on it. The spec for this change states
the behaviour in words and names no path.

### SR3 — A drifted cite is a finding, found by a check

**Bad**
```markdown
Renewal skips a loan with a reservation (`loans/RenewalPolicy.java:42`, `canRenew`).
```
```java
42  import java.time.Clock;
```
`canRenew` moved to line 58 after a refactor. The cite now points at an import, and only a reader who opens it sees
the drift.

**Good**
```text
$ check-cites design.md
design.md:12  loans/RenewalPolicy.java:42  canRenew  DRIFTED (found at :58)
1 drifted cite
```
A check resolves each cite to its symbol on every change. The reviewer reports the drifted line as a finding.

### SR4 — Every open question names its decider

**Bad**
```markdown
## Open questions

- Should a renewal reset the overdue fine?
- Do library sites share one reservation queue?
```
Nobody owns either question. The build starts, and both are still open when it ends.

**Good**
```markdown
## Open questions

- Should a renewal reset the overdue fine? Decides: the circulation lead.
  Does not block: the fine stays as it is until the lead answers, and the
  rule is one setting.
```
The queue question was answered before approval and moved into the design. The fine question names who decides it
and why building can go on.

## Decided edges

- **Skip when** a later round reports a problem in text that changed since the last round: that is a new finding. —
  **Do not skip when** the text is unchanged: the late finding is a miss of the earlier round (SR1). — **Confidence**
  high
- **Skip when** the sentence states planned behaviour: there is no code to cite yet. — **Do not skip when** the
  sentence states what the code does today, with or without the word "today" (SR2). — **Confidence** high
- **Skip when** the claim sits in the spec: move it to the design and cite it there; the spec names no paths. —
  **Do not skip when** the design restates that claim: the design cites it (SR2). — **Confidence** high
- **Skip when** a cite pins a commit (`file:line @commit`): it cannot drift. — **Do not skip when** the cite points at
  the main branch (SR3). — **Confidence** medium
- **Skip when** the spec is still a draft: an open-questions section is normal then. — **Do not skip
  when** the spec reaches the approval gate (SR4). — **Confidence** high
- **Skip when** a scenario is plain prose, not Gherkin: the bar is that a test can check it, not the format. — **Do not
  skip when** a scenario names no observable result (SR6). — **Confidence** high

## Review checks

Walk the whole spec and the whole design in one round, every section, before you report.

- [ ] SR1 — Report every finding in this round. A finding on text unchanged since an earlier round is a miss of that
  round; say so.
- [ ] SR2 — Open each `file:line` cite in the design on the main branch. A cite that does not show the claimed
  behaviour is a finding, and so is a claim about today's code with no cite. A file path in the spec is a finding.
- [ ] SR3 — Run the cite check over the design. Each cite that no longer points at its named symbol is a finding.
- [ ] SR4 — Read the open-questions list. Each item without a decider, or without a reason it does not block
  building, is a finding.
- [ ] SR6 — For each story, check an actor, an action and a benefit, scenarios a test can check, and an out-of-scope
  list. Each one missing is a finding.
