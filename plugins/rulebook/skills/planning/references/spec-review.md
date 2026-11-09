# Spec review

How a reviewer checks a spec and its design before the approval gate: one round, cited claims, no open question without
a decider, complete stories, and a sound design. Read it when you write, revise or review a spec or a design before the
approval gate.

Contents: Rules · When X, use Y · Good / Bad (SR2, SR3, SR4, SR10, SR11) · Decided edges · Review checks

## Rules

- **SR1** — Report every finding the rubric produces in one review round; a later-round finding on unchanged text is
  a reviewer miss, because findings raised one per round stretch one review over several rounds.
- **SR2** — In the design, cite `file:line` on the main branch for each claim about today's code, and the reviewer
  opens each cite; the spec names no paths, because an uncited false claim can settle a decision.
- **SR3** — Treat a `file:line` cite in a design that no longer points at the named symbol as a finding, found by a
  check that can be run, because drifted cites are otherwise found only by chance.
- **SR4** — Before approval, look up what code and docs answer, then give each open question left a decider, options
  with a recommendation, and why it does not block building, because a bare question outlives the build.
- **SR6** — Check each story for actor, action and benefit, scenarios a test can check, and an out-of-scope list,
  because without them the builder guesses who it serves, when it is done, and where it stops.
- **SR9** — Check each design decision against the ADRs and patterns it touches; report an unnamed departure, or a
  conflict between documents, without resolving it, because a silent departure overrides a recorded decision.
- **SR10** — In the design, name at least one real alternative with why it lost, and state each tradeoff as "we accept
  X for Y", because an unstated cost later reads as an oversight and gets fixed.
- **SR11** — For each step that changes state or calls another system, say in the design what happens when it fails,
  runs twice, or crashes halfway, because partial state left behind turns every retry into debugging.
- **SR12** — When the design changes stored data, a public contract or a deploy, name the migration and the rollback,
  and mark each irreversible step for the human's yes, because a shipped irreversible step cannot be undone.
- **SR13** — For each new input, endpoint or permission, name in the design the trust boundary it crosses and its
  control, because a design with no named boundary leaves security to whoever writes the code.
- **SR14** — Add no abstraction, setting, port or extension point that has no second user, today or in this spec,
  because a seam with one user adds indirection every later change pays for.
- **SR15** — Record a decision as an ADR when it is hard to reverse, surprising without context, and the result of a
  real tradeoff, because otherwise the next reader re-decides it without knowing why.
- **SR17** — Reuse an existing part that already does the job, or name in the design why it cannot be used, because a
  second copy of a part drifts from the first.
- **SR18** — For each new failure mode in the design, name the log, metric or alert that shows it in production,
  because a failure nobody can see is found by users first.
- **SR19** — List each assumption behind the spec as stated, inferred from code at `file:line`, or a chosen default,
  and have the human confirm the last two, because an unconfirmed guess becomes a requirement.
- **SR20** — In a one-way-door design, write a pre-mortem: assume it failed and name each specific failure (trigger,
  chain of effects, early sign) with its mitigation, because asking only whether it works hides how it fails.
- **SR21** — Before the spec, research how the touched code works (flow, where things live, gotchas at `file:line`)
  and why it is shaped so (commits, PRs, issues), because changing code without its reason reintroduces old bugs.
- **SR22** — Give a research helper neutral questions about how the current code works, and keep the wanted change
  out of them, because a helper that knows the goal reports what supports it.

## When X, use Y

| situation | use | why |
|---|---|---|
| the review finds more than one problem | report them all in this round (SR1) | findings raised one per round stretch one review over several rounds |
| a design sentence states how the code behaves today | a `file:line` cite on the main branch, opened by the reviewer (SR2) | check the request against the actual code and record `file:line`; a spec can say X while the code does Y |
| a spec sentence states how the code behaves today | move the claim and its cite into the design (SR2) | a spec holds no file paths, because they go out of date fast |
| a design carries `file:line` cites | run a check that resolves each cite to its symbol (SR3) | a cite that drifts is a false claim the next reader believes |
| the spec reaches the approval gate with open questions | resolve each, or give it a decider, options with a recommendation, and why it does not block (SR4) | a bare question outlives the build |
| an open question the code or the docs can answer | look the fact up, record the answer in the design, and drop the question (SR4) | a question the author could answer costs the human a lookup and invites a guess |
| a story has no "as a … so that …" line | add actor, action and benefit (SR6) | without actor, action and benefit, the builder guesses who the story serves |
| a scenario says "works well" or "is fast" | rewrite it as a condition a test can check (SR6) | a vague criterion such as "works well" gives no test a pass condition |
| a story has no out-of-scope list | add one (SR6) | without an out-of-scope list, the builder guesses where the story ends |
| a design decision touches an area with an ADR or an established pattern | check the fit, and report a departure or a conflict for the human to settle (SR9) | a silent departure overrides a recorded decision |
| the design picks one shape | name a rejected alternative and why it lost, and each tradeoff as "we accept X for Y" (SR10) | an unstated cost later reads as an oversight |
| a step writes data, sends a message or calls another system | state what happens on failure, on a second run, and after a crash halfway (SR11) | partial state turns every retry into debugging |
| the design changes stored data, a public contract or a deploy | name the migration and the rollback; mark irreversible steps for the human's yes (SR12) | an irreversible step cannot be undone once it ships |
| the design adds an input, an endpoint or a permission | name the trust boundary and the control at it (SR13) | otherwise security is left to whoever writes the code |
| the design adds an abstraction, a setting, a port or an extension point with one user | remove it until a second user exists, today or in this spec (SR14) | a seam with one user is indirection every change pays for |
| a decision is hard to reverse, surprising, and a real tradeoff | write it as an ADR (SR15) | the next reader re-decides it without knowing why |
| the design adds a part that resembles one in the code today | reuse that part, or say why it cannot serve (SR17) | two copies drift apart |
| the design adds a way to fail: a timeout, a rejected input, a lost message | the log, metric or alert that shows it (SR18) | users find an unseen failure first |
| the spec rests on something the human did not say | an assumption list, each marked stated, inferred (`file:line`) or default; the human confirms the inferred and default ones (SR19) | a guess the human never saw is built as if they asked for it |
| the design is a one-way door (LN3) | a pre-mortem: "three months later this failed", each failure with a specific trigger, the chain of effects and the first sign, then a concrete mitigation (SR20) | a step you cannot undo needs its failures found before it ships |
| research on one file or one function | one read-only helper that explores and explains in one pass (SR21) | a fan-out costs more than it finds |
| research on more than one module or service | two to four read-only helpers, each on one angle, then one synthesis: overview, key concepts, how it works, where things live, gotchas (SR21) | each angle stays inside one context |
| code that looks odd or redundant | its history: `git log` and `git blame` on the lines, then the pull requests and issues they cite (SR21) | the odd line is often the fix for a past bug |
| a brief for a research helper or subagent | questions on how it works today ("how does X reach Y?"), with the wanted change kept in the design notes, not the brief (SR22) | the helper looks for what is there, not for what fits the goal |

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

### SR4 — Every open question names its decider, options and a recommendation

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
  Options: reset it; keep it. Recommended: keep it, because a renewal
  does not repay the days already late.
  Does not block: the fine stays as it is until the lead answers, and the
  rule is one setting.
```
The queue question was answered from the site configuration before approval and moved into the design. The fine
question names who decides it, the choices with a recommendation, and why building can go on.

### SR10 — Name the alternative that lost, and the cost you accept

**Bad**
```markdown
## Design — overdue reminders

The reminder job runs nightly and emails every member with an overdue loan.
```
One shape and no rival. When a member asks why a reminder came a day late, the next developer "fixes" the nightly
run without knowing it was chosen.

**Good**
```markdown
## Design — overdue reminders

The reminder job runs nightly and emails every member with an overdue loan.

Alternative: send each reminder when its loan falls due. Lost because it needs a
timer per loan, which our job runner cannot hold.

Tradeoffs:
- We accept a reminder up to a day late for one nightly job and no per-loan timers.
```
The reader sees the delay was chosen, and what it bought.

### SR11 — Say what happens on failure, a rerun and a crash

**Bad**
```markdown
The job selects overdue loans, sends one email per member, and marks each loan
as reminded.
```
The design is silent on a crash after the emails go out and before the loans are marked. The next run sends every
reminder again.

**Good**
```markdown
The job selects overdue loans not yet reminded today, and for each member:
1. records a reminder row keyed by (member, date), unique;
2. sends the email, passing (member, date) as the mail provider's idempotency key;
3. marks the row sent.

Failure: a send error leaves the row unsent; a rerun the same night resends it
with the same key. An unsent row from an earlier date is dropped, since that
night records a fresh one.
Twice: the unique key stops a second row, and the provider drops a second send
with the same key.
Crash halfway: an unsent row is resent with its key, so an email that already
went out is not delivered twice.
```
Each step names its failure, its rerun and its crash, so a retry needs no debugging.

### SR20 — A pre-mortem names how it fails, not only that it might

**Bad**
```markdown
## Pre-mortem — move loan history to its own table

Risk: it might not scale. Mitigation: monitor performance.
```
"It might not scale" names no trigger, no chain and no sign, so nobody can watch for it or plan around it.

**Good**
```markdown
## Pre-mortem — move loan history to its own table

Failure: the copy runs while members still renew loans.
Trigger: the backfill takes longer than the release window.
Chain: renewals made during the copy land only in the old table; the old
table is dropped; those renewals are lost.
Early sign: the row counts of the two tables differ after the backfill.
Mitigation: write to both tables from the release before the backfill, and
drop the old table only after a week of equal counts.
```
Each failure has a trigger, a chain and a sign someone can check.

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
- **Skip when** the design names its departure from an ADR and why, and records the new decision, as an ADR when SR15
  applies and in the design otherwise: that is a decision, not a finding. — **Do not skip when** the departure is
  unnamed, or two documents disagree: report it and leave the choice to the human, even when the answer looks plain
  (SR9). — **Confidence** medium
- **Skip when** constraints forced the shape: the design names the constraint and says it was the only viable shape,
  with no invented rival. — **Do not skip when** a real alternative existed (SR10). — **Confidence** medium
- **Skip when** a step only reads and changes no state: there is no rerun or crash to describe. — **Do not skip when**
  the step writes, sends or calls out, even if it "just retries" (SR11). — **Confidence** high
- **Skip when** the change only adds, and old data and old clients keep working: say so in one line; there is no
  migration, and the rollback is redeploying the previous version. — **Do not skip when** it deletes, renames or
  reshapes stored data or a public contract (SR12). — **Confidence** medium
- **Skip when** a second user of the seam exists today, or is built in this same spec. — **Do not skip when** the only
  second user is a future one (SR14). — **Confidence** high
- **Skip when** the decision is easy to reverse or the obvious choice: one line in the design is enough. — **Do not
  skip when** all three hold: hard to reverse, surprising, and a real tradeoff (SR15). — **Confidence** high
- **Skip when** the change is in the tiny lane (LN2): it has no spec. — **Do not skip when** any spec (bug, feature or
  one-way door) rests on an inference the human has not seen (SR19). — **Confidence** high
- **Skip when** an assumption is a fact about today's code that SR4 looked up and SR2 cites: the code settles it, so
  the human need not confirm it. — **Do not skip when** the code is used to infer what the human wants (SR19). —
  **Confidence** high
- **Skip when** the change is in the tiny, bug or feature lane: SR11 already asks what each step does when it fails.
  — **Do not skip when** the change is in the one-way-door lane (SR20, LN3). — **Confidence** high
- **Skip when** the change only adds new code and touches no existing behaviour: there is no history to read. —
  **Do not skip when** the design plans to delete or reshape existing code (SR21). — **Confidence** high

## Review checks

Walk the whole spec and the whole design in one round, every section, before you report.

- [ ] SR1 — Report every finding in this round. A finding on text unchanged since an earlier round is a miss of that
  round; say so.
  Applies when: every round; a miss only from the second round on.
  Evidence: the text, and the earlier round that saw it unchanged.
  Not a finding: a problem in text that changed since the last round, which is a new finding (decided edge).
  Severity: Act on
  Verify: compare the text with the version the earlier round reviewed.
- [ ] SR2 — Open each `file:line` cite in the design on the main branch. A cite that does not show the claimed
  behaviour is a finding, and so is a claim about today's code with no cite. A file path in the spec is a finding.
  Applies when: the design makes a claim about today's code, or the spec names a file path.
  Evidence: the claim, quoted, and the cite you opened or its absence; or the spec line with the path.
  Not a finding: planned behaviour; an uncited claim in the spec, cited in the design (decided edges).
  Severity: Act on
  Verify: open the cite on the main branch again and read the claimed behaviour there.
- [ ] SR3 — Run the cite check over the design. Each cite that no longer points at its named symbol is a finding.
  Applies when: the design holds a `file:line` cite.
  Evidence: the cite check's output line for the cite.
  Not a finding: a cite that pins a commit (`file:line @commit`) (decided edge).
  Severity: Act on
  Verify: run the cite check again.
- [ ] SR4 — Read the open-questions list. Each item without a decider, without options and a recommendation, or
  without a reason it does not block building, is a finding. So is a question the code or the docs could answer.
  Applies when: the spec reaches the approval gate.
  Evidence: the open question, quoted, and the part it lacks; or the code or doc that answers it.
  Not a finding: an open-questions section in a draft spec (decided edge).
  Severity: Act on
  Verify: re-open the question, and the code or doc that answers it.
- [ ] SR6 — For each story, check an actor, an action and a benefit, scenarios a test can check, and an out-of-scope
  list. Each one missing is a finding.
  Applies when: the spec holds a story.
  Evidence: the story, and the part that is missing.
  Not a finding: a scenario in plain prose that a test can check (decided edge).
  Severity: Act on
  Verify: re-open the story and its scenarios.
- [ ] SR9 — For each design decision, find the ADRs and patterns in its area. A departure the design does not name, or
  two documents that disagree, is a finding; report it and do not pick the answer.
  Applies when: the design makes a decision.
  Evidence: the decision, and the ADR or pattern it departs from, or the two documents that disagree.
  Not a finding: a named departure with its reason and its new decision recorded (decided edge).
  Severity: Act on
  Verify: re-open the ADR or pattern and the design decision.
- [ ] SR10 — Find at least one rejected alternative with why it lost; none, without a named forcing constraint, is a
  finding. A cost of the chosen shape not stated as "we accept X for Y" is a finding.
  Applies when: the change has a design.
  Evidence: the design's alternatives section or its absence, and the unstated cost.
  Not a finding: a shape a named constraint forced, with no invented rival (decided edge).
  Severity: Act on
  Verify: re-open the design's alternatives and tradeoffs.
- [ ] SR11 — For each step that writes, sends or calls out, find what happens on failure, on a second run and after a
  crash halfway. Each one missing is a finding.
  Applies when: the design has a step that writes data, sends a message or calls another system.
  Evidence: the step, quoted; one finding per missing case.
  Not a finding: a read-only step that changes no state (decided edge).
  Severity: Act on
  Verify: re-read the step and the text after it for the failure, rerun and crash cases.
- [ ] SR12 — For each change to stored data, a public contract or a deploy, find the migration and the rollback. Each
  one missing is a finding, and so is an irreversible step not marked for the human's yes.
  Applies when: the design changes stored data, a public contract or a deploy.
  Evidence: the change, and the missing migration, rollback or mark.
  Not a finding: an add-only change where old data and old clients keep working, stated in one line (decided edge).
  Severity: Act on
  Verify: re-open the design's migration and rollback text.
- [ ] SR13 — For each new input, endpoint or permission, find the trust boundary and the control at it. Each one
  missing is a finding.
  Applies when: the design adds an input, an endpoint or a permission.
  Evidence: the new input, endpoint or permission, and the missing boundary or control.
  Not a finding: none
  Severity: Act on
  Verify: re-open the design's text on the input, endpoint or permission.
- [ ] SR14 — For each new abstraction, setting, port or extension point, find its second user, today or in this spec.
  None is a finding.
  Applies when: the design adds an abstraction, a setting, a port or an extension point.
  Evidence: the new seam, and where you looked for a second user.
  Not a finding: a second user that exists today or is built in this spec (decided edge).
  Severity: Act on
  Verify: search the code and the spec for a second user again.
- [ ] SR15 — For each decision that is hard to reverse, surprising and a real tradeoff, find its ADR. None is a
  finding.
  Applies when: the design makes a decision.
  Evidence: the decision, quoted, and the missing ADR.
  Not a finding: a decision that is easy to reverse or the obvious choice (decided edge).
  Severity: Act on
  Verify: search the ADRs for the decision again.
- [ ] SR17 — For each new part, search the code for one that does the same job. One found and neither reused nor
  ruled out in the design is a finding.
  Applies when: the design adds a part.
  Evidence: the new part, and the existing part at `file:line` that does the same job.
  Not a finding: none
  Severity: Act on
  Verify: re-open the existing part and confirm it does the same job.
- [ ] SR18 — For each new failure mode, find the log, metric or alert that shows it. Each one missing is a finding.
  Applies when: the design adds a failure mode.
  Evidence: the failure mode, quoted, and the missing log, metric or alert.
  Not a finding: none
  Severity: Act on
  Verify: re-open the design's text on the failure mode.
- [ ] SR19 — In the issue's clarify answers or the design, find the assumption list, each marked stated, inferred or
  default. A missing list, or an inferred or default assumption with no answer from the human, is a finding.
  Applies when: the change has a spec.
  Evidence: the assumption list or its absence, and each unanswered inferred or default assumption.
  Not a finding: a tiny-lane change with no spec; a fact about today's code that SR2 cites (decided edges).
  Severity: Act on
  Verify: re-open the clarify answers and the design.
- [ ] SR20 — In a one-way-door design, find the pre-mortem. A missing pre-mortem, a failure with no specific trigger or
  early sign, or a failure with no mitigation, is a finding.
  Applies when: the change is in the one-way-door lane.
  Evidence: the pre-mortem or its absence, and each failure with its missing part.
  Not a finding: a change in the tiny, bug or feature lane (decided edge).
  Severity: Act on
  Verify: re-open the pre-mortem.
- [ ] SR21 — In the research notes, find the how (with `file:line`) and, for each line the design plans to delete or
  reshape, the why: a commit, pull request or issue, or "no recorded reason". A line planned for deletion or
  reshaping with no stated why is a finding.
  Applies when: the design plans to delete or reshape existing code.
  Evidence: the planned line, and the research notes that lack its how or why.
  Not a finding: a change that only adds new code and touches no existing behaviour (decided edge).
  Severity: Act on
  Verify: re-open the research notes and the planned line.
- [ ] SR22 — In each research brief, find the wanted change or a planned design. One that states either is a finding.
  Applies when: the change has a research brief given to a helper.
  Evidence: the brief's line that states the wanted change or the planned design, quoted.
  Not a finding: none
  Severity: Act on
  Verify: re-open the brief.
