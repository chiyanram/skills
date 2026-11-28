# Spec review

**You own whether the builder can build the right thing from this text alone.** How a spec and its design are
researched, written and checked before approval: research, cited claims, open questions, intent, assumptions and a sound
design. Read it when you write, revise or review a spec or a design before approval.

## Rules

### Research

- Before the spec, research how the touched code works (its flow, where things live, gotchas at `file:line`) and why it
  is shaped so (commits, PRs, issues), because changing code without its reason brings old bugs back. A change that only
  adds new code has no history to read. For one file or function, use one read-only helper. For more than one module,
  use two to four helpers, one angle each, then one helper that joins their results.
- Research **blind**, in two steps. First write questions from the ticket, each about how the code works today, with the
  files and links the ticket names, and none naming the wanted change. Then give only that questions file to a fresh
  read-only helper, never the ticket, the spec or the wanted change, because a helper that knows the goal reports what
  supports it. It reports what is there, with no fixes, critique or proposals.
- Look up what code and docs can answer before you ask the human. Each question still open at approval names its
  decider, options with a recommendation, and why it does not block building, because a bare question outlives the
  build. A draft spec may hold open questions.

### The spec

- Give the spec an intent with an actor, an action and a benefit, ACs a test can check, and an out-of-scope list,
  because without them the builder guesses who it serves, when it is done, and where it stops.
- List each assumption behind the spec as stated, inferred from code at `file:line`, or a chosen default, and have
  the human confirm the last two, because an unconfirmed guess becomes a requirement. A fact about today's code that
  the design cites needs no confirmation; a change in a lane with no spec has none to list.

### The design

- **Cite** `file:line` on the main branch for each claim about today's code, and open each cite when you review, because
  an uncited false claim can settle a decision. The spec names no paths, and planned behaviour has no cite yet.
- Verify each cite with a check that can be run (the **cite check**), because a drifted cite is otherwise found only by
  chance. A cite pinned to a commit (`file:line @commit`) cannot drift.
- Check each decision against the ADRs and patterns it touches, and report an unnamed departure, or two documents that
  disagree, for the human to settle, because a silent departure overrides a recorded decision. A departure the design
  names, with its reason and its new decision recorded, is a decision.
- Sketch two shapes (the caller's usage and the types, no bodies) before you choose, and pick the one where each piece
  of state has one owner, each task has one way to do it, and the caller needs to know least. Name the other and why it
  lost, and state each tradeoff as "we accept X for Y", because an alternative written after the choice is a straw man,
  and an unstated cost later reads as an oversight and gets "fixed". A shape that a named constraint forced needs no
  invented rival.
- For a design the person marks contested, ask the person to run `/toolbox:arena` on the shape before you choose, or
  name the risk when the toolbox is not installed, because one author's two sketches share that author's blind spots.
- When the same workaround appears in two places, redesign the shape in the design instead of patching a third, because
  each workaround shows a shape that does not fit.
- For each step that writes, sends or calls another system, say what happens when it fails, runs twice, or crashes
  halfway, because partial state turns every retry into debugging.
- When the design changes stored data, a public contract or a deploy, name the migration and the rollback, and mark
  each irreversible step for the human's yes, because a shipped irreversible step cannot be undone. An add-only change
  that old data and old clients survive says so in one line.
- For each new input, endpoint or permission, name the **trust boundary** it crosses and the control at it, because a
  design with no named boundary leaves security to whoever writes the code.
- For each new failure mode, name the log, metric or alert that shows it in production, because users find an unseen
  failure first.
- Reuse an existing part that does the job, or say why it cannot serve, because a second copy drifts from the first.
- Add an abstraction, setting, port or extension point only with a second user, today or in this spec, because a seam
  with one user is indirection every later change pays for. The variants of one type are not seams.
- Give a type one variant per allowed state, each with only its own fields, because a guard against a forbidden state
  gets skipped. Work out a derived value on read, or keep it only as a cache with one owner, because a copy drifts.
- Say for each existing module the design touches whether it needs a refactor first, and propose that refactor as its
  own ticket, because building the change on a module that resists the change makes the next change harder too. The
  refactor ticket names its pin (the tests, snapshot or old-against-new diff that hold today's behaviour; a type
  check or lint is not a pin) and the trace it shortens, such as "a reader of X opens 2 files, not 5", because a
  refactor that shortens no trace adds churn for nothing.
- Record a decision as an ADR when it is hard to reverse, surprising without context, and a real tradeoff, because the
  next reader otherwise re-decides it without knowing why. Any other decision is one line in the design.
- In a design with the one-way-door flag, write a **pre-mortem**: assume it failed, and name each failure with its
  trigger, chain of effects, early sign and mitigation, because asking only whether it works hides how it fails.

### The review

- Report every finding in one round. If a later round raises a finding on text that has not changed, count it as a miss
  of the earlier round, because findings raised one per round stretch one review over several.

## Good / Bad

### Cite today's behaviour in the design, not the spec

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

### A drifted cite is a finding, found by a check

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
$ sed -n 42p loans/RenewalPolicy.java | grep -c canRenew
0
$ grep -n canRenew loans/RenewalPolicy.java
58:    boolean canRenew(Loan loan) {
```
The check opens each cite's line and looks for the named symbol. Line 42 no longer holds `canRenew`, so the reviewer
reports the cite in the design as drifted, with its new line.

### Every open question names its decider, options and a recommendation

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

### Name the alternative that lost, and the cost you accept

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

### Say what happens on failure, a rerun and a crash

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

### A pre-mortem names how it fails, not only that it might

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

## Review

Read `docs/agents/domain.md` first, by crq's [worker.md](../crq/worker.md). When the spec's change touches no code,
build file or migration, skip the standards that `domain.md` lists, and mark criteria 3 to 5 `n/a: no code in scope`.
Walk the whole spec and the whole design in one round, every section, before you report. Grade six **criteria**, then
the project's spec rubric when `domain.md` names one. Each criterion ends as `met`, `unmet` or `n/a` with its reason,
and each finding names the source it rests on. Each line under a criterion is a finding, a blocker unless marked
(warning).

- (warning) A miss: a finding on text unchanged since an earlier round. Report the finding at its own severity, and add
  this warning for the miss.

### 1. Grounded in today's code

- Research notes that do not show how the code works at `file:line`, or a line the design deletes or reshapes with no
  stated reason (a commit, PR, issue, or "no recorded reason").
- Research that is not **blind**: a question or a helper's input that states the wanted change or a planned design, or a
  helper that read the ticket or spec.
- A claim about today's code with no cite, a cite that does not show the claim, or a file path in the spec.
- A main-branch cite that no longer points at its named symbol, by the **cite check**.

### 2. A complete, testable spec

- An open question at approval with no decider, options and recommendation, or reason it does not block; or one the
  code or docs could answer.
- An intent with no actor, action or benefit, no ACs a test can check, or no out-of-scope list.
- No assumption list, or an inferred or default assumption the human has not answered.

### 3. A sound shape

- No rejected alternative, unless the design names the constraint that forced its shape; a rejected shape whose loss is
  not one of: state with two owners, a task with two ways to do it, or a caller that must know more; or a cost not
  stated as "we accept X for Y".
- A new part that duplicates an existing one, neither reused nor ruled out.
- A new abstraction, setting, port or extension point with no second user.
- (warning) A type that can hold a forbidden state, or a derived value that is not a cache with one owner.
- (warning) A touched module with no "refactor first?" answer, or a refactor folded into this change's slices.
- (warning) A refactor-first ticket with no pin or no trace it shortens.

### 4. Safe when it fails

- A step that writes, sends or calls out with no failure, rerun or crash-halfway answer.
- A change to stored data, a public contract or a deploy with no migration or rollback, or an irreversible step not
  marked for the human's yes.
- A design with the one-way-door flag and no pre-mortem, or a failure in it with no trigger, chain of effects, early
  sign or mitigation.

### 5. Guarded and visible in production

- A new input, endpoint or permission with no trust boundary and control.
- A new failure mode with no log, metric or alert.

### 6. Fits what was decided

- An unnamed departure from an ADR or pattern, or two documents that disagree.
- A hard-to-reverse, surprising tradeoff decision with no ADR.
