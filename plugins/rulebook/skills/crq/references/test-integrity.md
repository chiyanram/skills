# Test integrity

How a finder judges a diff's edits to tests that already exist: changed expected values, rewritten tests, new
doubles, wider matchers and regenerated snapshots. Read it when you review a diff that edits an existing test, a
snapshot or a golden file.

Contents: Rules · When X, use Y · Good / Bad (TI4) · Decided edges · Review checks

## Rules

- **TI1** — Report each changed expected value in an existing test that no spec or acceptance-criterion change
  explains, because an expectation edited to match the code hides the defect the old value caught.
- **TI2** — For each rewritten test, name the acceptance criterion it checked before and the one it checks now;
  report a change no spec line explains, because a rewrite can keep its name and drop its check.
- **TI3** — Report a test double that replaces a real call an existing test made, unless the PR names why
  the real call cannot run there, because the double passes while the real dependency breaks.
- **TI4** — Report an exact matcher widened in an existing test (to `any()`, `contains`, a wildcard) unless that
  value is outside the test's promise, because a wide matcher lets a wrong value pass.
- **TI5** — For each updated snapshot or golden file, name the code or spec change behind each changed line; report
  a line none explains, because regenerating a snapshot records whatever the code now does, bug included.

## When X, use Y

| situation | use | why |
|---|---|---|
| an assertion in an existing test expects a new value | the spec line or acceptance criterion that changes that behaviour; none is a finding (TI1) | only a behaviour change gives an existing test a new answer |
| the new value comes with a reason only in a test comment or the commit message | still a finding (TI1) | a plausible comment is how an edited expectation reads |
| an existing test's body is rewritten: new setup, new action or new assertions | the criterion before and after, side by side (TI2); a weaker check is also VB6 (`verify-done`) | the name stays while the check moves |
| a mock, stub or fake now stands where the test called real code | the PR's reason the real call cannot run there (TI3); a mock that implements the asserted behaviour: the junk-test list (`testing` skill) | a double cannot fail on a bug in what it replaces |
| an exact argument or value matcher becomes `any()`, `_`, `contains`, `startsWith` or a type match | the value is outside the test's promise, or a finding (TI4); a Spock verified interaction: the `testing` skill's Spock notes | the wide matcher accepts the wrong value too |
| a snapshot or golden file changes | each changed line traced to a code or spec change in this diff (TI5) | a regenerated snapshot also records a bug |
| a test the diff touches still asserts the old behaviour | CR6 (`code-review`) | that is a stale test, not an edited one |
| the diff adds a test or a snapshot file | the junk-test list (`testing` skill), not this reference | a new test's worth is judged there |

**Do not report.** A floor guard is a script that reads the diff and fails it on the moves that lower the bar.
When one ran at the head and its result is in the PR, leave these to it:

| the diff | owner when no floor guard ran |
|---|---|
| deletes a test or a test file | VB6 (`verify-done`) |
| adds a skip marker | VB6 (`verify-done`); a person's quarantine entry is VB11 (`verify-done`) |
| removes an assertion line from a test that stays | VB6 (`verify-done`) |
| adds a suppression with no reason, or an empty `catch` | CR4 (config); CM7 (`code/comments`); ER3 (`code/errors`) |
| edits a judge file: a build file, a file the verify command runs, test config | CR3 (`code-review`) |

Leave to the gate a failure it already reports: a red test, a lint or type error. A generated snapshot is the
deliberate exception: a snapshot regenerated to match the code passes the gate, so TI5 reviews it.

## Good / Bad

### TI4 — A widened matcher needs the value to be outside the promise

**Bad**
```diff
 @Test
 void shouldTellTheBorrowerWhenALoanIsOverdue() {
     reminders.run(today);

-    verify(notifier).send(eq("Loan 7 is overdue"));
+    verify(notifier).send(any());
 }
```
The message changed, so the matcher was widened. A message about loan 8, or an empty one, now passes. The
criterion promises the loan number in the message.

**Good**
```diff
 @Test
 void shouldTellTheBorrowerWhenALoanIsOverdue() {
     reminders.run(today);

-    verify(notifier).send(eq("Loan 7 is overdue"));
+    verify(notifier).send(eq("Loan 7 is overdue since 2 May"));
 }
```
The spec's new criterion names the message, so the exact new value replaces the old one (TI1, TI4). When part of
the message is generated, an `argThat` on the promised part only, the loan number, is the decided edge.

## Decided edges

- **Skip TI1 and TI2 when** a spec line or an acceptance criterion in this change names the behaviour change. —
  **Do not skip when** the only reason is a test comment or the commit message. — **Confidence** high
- **Skip TI3 when** the PR names why the real call cannot run in that test: it is slow, flaky or outside
  the system. — **Do not skip when** the double replaces code in this repository that the test ran before, with no
  reason given, or the test is an integration or smoke test and the double replaces this repository's own code
  (`testing` skill). — **Confidence** medium
- **Skip TI4 when** the widened value is outside what the test promises, or the test cannot know it (a generated
  id, a timestamp): constrain the fields it can know. — **Do not skip when** the criterion promises that value. —
  **Confidence** high
- **Skip TI5 when** the snapshot or golden file is new: it is a new test (`testing` skill, Junk tests). — **Do not skip when** an existing
  file changes, even in one line. — **Confidence** high
- **Skip the floor-guard moves when** a floor guard ran at the head and its result is in the PR. — **Do not
  skip when** no floor guard ran: report them under VB6, CR3, CR4, CM7 or ER3. — **Confidence** high

## Review checks

Walk the diff of every existing test file, snapshot file and golden file, with the spec beside it. Each finding
cites the `file:line` and the rule ID.

- [ ] TI1 — For each changed expected value in an existing test, find the spec line or acceptance criterion that
  changes that behaviour. A changed value with none is a finding.
  Applies when: an assertion, an expected literal, or a fixture value the assertion compares against changes in an
  existing test file
  Evidence: the old and new line at `file:line`, and the spec searched
  Not a finding: behaviour change named in the spec (decided edge)
  Severity: blocker
  Verify: re-open the spec and the acceptance criteria at the head
- [ ] TI2 — For each rewritten test, write the criterion it checked before and the one it checks now. A different
  criterion that no spec line explains is a finding.
  Applies when: the setup, action or assertions of an existing test change
  Evidence: the two criteria, and the test at `file:line` before and after
  Not a finding: behaviour change named in the spec (decided edge)
  Severity: blocker
  Verify: re-open the test at the base and at the head
- [ ] TI3 — For each mock, stub or fake that now stands where an existing test called real code, find the pull
  request's reason. One with no reason is a finding.
  Applies when: an existing test gains a double for code it called before
  Evidence: the double at `file:line` and the real call it replaces
  Not a finding: a slow, flaky or outside call with a named reason (decided edge)
  Severity: warning
  Verify: re-open the test at the base to confirm it called the real code
- [ ] TI4 — For each matcher an existing test widens, find what the criterion promises about that value. A widened
  matcher on a promised value is a finding.
  Applies when: an exact matcher in an existing test becomes `any()`, `_`, `contains`, `startsWith` or a type match
  Evidence: the old and new matcher at `file:line`, and the criterion
  Not a finding: a value outside the promise or unknowable in the test (decided edge)
  Severity: warning
  Verify: re-open the criterion and the old matcher
- [ ] TI5 — For each changed line in an existing snapshot or golden file, find the code or spec change in this diff
  that explains it. A line none explains is a finding.
  Applies when: an existing snapshot or golden file changes
  Evidence: the changed snapshot line at `file:line`, and the code searched
  Not a finding: a new snapshot or golden file (decided edge)
  Severity: blocker
  Verify: re-open the snapshot diff and the code change it traces to
