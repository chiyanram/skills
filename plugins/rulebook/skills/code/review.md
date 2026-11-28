# Review

**You own what this change breaks. The approved spec and design are the bar.** A code review grades the change
against six **criteria** and reports each finding at its `file:line`. The passes, buckets and rounds a review runs
in are in [review-run.md](review-run.md).

Walk the approved spec and design, then the whole diff, with the review list of every notes file in scope. Each
criterion ends as pass or fail; a criterion that does not apply says so in one line.

## 1. Matches the approved spec

- Walk the approved spec and design against the diff, criterion by criterion. Report each criterion missing, each
  behaviour nobody asked for and each criterion misread, because code can pass every test and still build the wrong
  thing.

Done when every acceptance criterion is marked met, missing or misread.

## 2. Safe outside the diff

- For each changed behaviour that code outside the diff relies on (shared code, a public contract, configuration, a
  minor or major dependency bump), name each **consumer** at its own `file:line`, never as a group such as "callers of
  X", and prove the one fact the change's safety rests on with a script or test that runs the real code, because
  breakage outside the diff never shows in it. A private method whose callers are all in the change has no outside
  consumer.
- For each **removed guard**, a check, default, error path or call the change removes or replaces, name the behaviour it
  carried and where the change puts it back or why it is retired, because a removed guard leaves no line to review. A
  reference left to removed code is a finding. A pure rename, a format change or unreachable code carried nothing.

Done when each changed behaviour names its consumers, or "no outside consumer", and each removed guard its new home.

## 3. Tests can fail

- For each changed behaviour, name its **smallest regression**, a realistic break such as a branch inverted, a default
  dropped or a field left out, and the assertion that fails on it, because a test that cannot fail on it sees nothing. A
  skipped, flaky, not-run-by-default, no-throw, snapshot-only or mock-call check does not count; the assertion runs by
  default and is stable on unchanged code. A test the diff touches that still asserts the old behaviour is a finding
  naming what it should assert. A change with no behaviour (formatting, a rename, a type-only change), or one the
  compiler enforces, has no regression to name. A new test is judged by the `testing` skill's junk-test list.

**Edits to existing tests.** Walk the diff of every existing test, snapshot and golden file, with the spec beside
it. A new test or a new snapshot is judged by the `testing` skill's junk-test list, not here.

- Trace each changed expected value in an existing test to a spec line or acceptance criterion in this change, and
  report one with none, because an expectation edited to match the code hides the defect the old value caught. A reason
  given only in a test comment or the commit message is still a finding.
- For each rewritten test (new setup, action or assertions), name the criterion it checked before and the one it
  checks now. Report a change no spec line explains, because a rewrite can keep its name and drop its check.
- (warning) Keep an existing test on the real code it called. Report a mock, stub or fake that now stands where an
  existing test called real code, unless the PR names why the real call cannot run there (slow, flaky, outside the
  system), because the double passes while the real dependency breaks. In an integration or smoke test, a double for
  this repository's own code is always a finding.
- (warning) Constrain each value the test can know and promises. Report an exact matcher widened to `any()`, `_`,
  `contains`, `startsWith` or a type match, unless that value is outside the test's promise or the test cannot know it
  (a generated id, a timestamp), because a wide matcher lets a wrong value pass.
- Trace each changed line in an existing snapshot or golden file to the code or spec change in this diff behind it,
  and report a line none explains, because a regenerated snapshot records whatever the code now does, bug included.

Done when each changed behaviour has its regression and its failing assertion, and each test edit its reason.

## 4. Gate untouched

- Send to the human each change to a **gate file**: CI config (`.github/workflows/`, `.gitlab-ci.yml`), a build file, a
  new dependency, `CODEOWNERS` or agent instruction files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `.agents/`), because an
  agent that edits its own gate, rules or dependencies can pass any change. A patch-level bump that changes only a
  version is listed in the PR instead.
- Give each lowered threshold or disabled check in a config file its reason on the line above, because a silent
  exception hides the problem the check was built to catch. A raised threshold needs none.

A floor guard is a script that reads the diff and fails it on the moves that lower the bar. When one ran at the head
and its result is in the PR, leave these to it; when none ran, report them by the rule named:

| the diff | rule, when no floor guard ran |
|---|---|
| deletes a test or a test file, adds a skip marker, removes an assertion from a test that stays | never weaken a test to reach green ([verify.md](verify.md)) |
| a person's quarantine entry | quarantine one test ([verify.md](verify.md)) |
| adds a suppression with no reason, or an empty `catch` | a lowered threshold above; the Comments and Errors rules in `SKILL.md` |
| edits a build file, a file the verify command runs, or test config | send it to the human, above |

Leave to the gate a failure it already reports, such as a red test or a lint error. A regenerated snapshot passes the
gate, so it is reviewed here.

## 5. Reviewable size

- Keep a change within the pull-request size limit (`planning`'s program-design notes), and split a larger one into
  tickets along its slices, because review usefulness falls as a change grows. Generated files, lock files and a
  mechanical rename do not count; list them in the PR. Split out a rename or formatter pass mixed with new logic.

## 6. Health, only with numbers

- Report a codebase-health finding only where the project publishes module numbers (complexity, size, coupling,
  coverage) and a touched module's number got worse, citing before and after, because a health finding without a
  measure is opinion. With no numbers, report none. A PR that names a refactor ticket for it still gets the finding,
  with the ticket linked.

## Good / Bad

### Compare the diff with what was approved

**Bad**
```text
Review: tests pass, code is clean. No findings.
```
The spec says a reserved loan cannot be renewed. The diff has no reservation check and adds a renewal limit nobody
asked for.

**Good**
```text
Act on · LoanService.java:44 — missing: "a reserved loan cannot be renewed"
Act on · LoanService.java:51 — extra: a limit of 3 renewals is not in the spec
```
Each finding names the criterion or the extra behaviour, and its line.

### Name the consumers outside the diff and prove the fact

**Bad**
```text
Review: dueDate() now returns UTC. Callers of dueDate() should be fine. No findings.
```
"Callers of dueDate()" names no one, and "should be fine" proves nothing. The reminder job still compares the date
with local midnight.

**Good**
```text
consumers of LoanService.dueDate(), now UTC:
- ReminderJob.java:30 compares it with LocalDate.now(): a day off in zones ahead of UTC
- LoanExport.java:12 formats it as ISO-8601 with its zone: safe
proved: DueDateZoneTest runs the real ReminderJob in UTC+2; it fails
Act on · ReminderJob.java:30 — convert to the library's zone before comparing
```
Each consumer is named at its line, and the claim the change rests on is run, not argued.

### Post only what the change introduced and the author would fix

**Bad**
```text
- Consider renaming `svc` to something clearer. (LoanService.java:12)
- The fine calculation has no upper bound. (FineCalculator.java:30, not in this diff)
- This might be slow for large libraries.
```
A style wish, a problem the change did not touch, and a guess with no evidence. The one real problem gets lost.

**Good**
```text
Act on · LoanService.java:44
renew() extends a loan that has an open reservation; the approved spec
says "a reserved loan cannot be renewed". Add the reservation check.
Coverage: 12 of 14 checks applied, 2 not applicable.
```
One finding, introduced by the change, shown at its line, with the fix.

### A widened matcher needs the value to be outside the promise

**Bad**
```diff
 @Test
 void shouldTellTheBorrowerWhenALoanIsOverdue() {
     reminders.run(today);

-    verify(notifier).send(eq("Loan 7 is overdue"));
+    verify(notifier).send(any());
 }
```
The message changed, so the matcher was widened. A message about loan 8, or an empty one, now passes. The criterion
promises the loan number in the message.

**Good**
```diff
 @Test
 void shouldTellTheBorrowerWhenALoanIsOverdue() {
     reminders.run(today);

-    verify(notifier).send(eq("Loan 7 is overdue"));
+    verify(notifier).send(eq("Loan 7 is overdue since 2 May"));
 }
```
The spec's new criterion names the message, so the exact new value replaces the old one. When part of the message is
generated, an `argThat` on the promised part only, the loan number, is right.

## Review

Walk the six criteria above against the review's findings. Each line is a finding, a blocker.

- A criterion with no result: pass, fail, or "does not apply" with its reason.
- A finding with no `file:line`, or a criterion marked pass with a finding open under it.
