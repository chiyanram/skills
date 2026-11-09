# Code review

What the code review checks beyond each topic reference: that the diff builds what was approved, that it stays a
reviewable size, and that the agent did not change its own gate. Read it when you review a PR's code, or
before you split a change.

## Rules

- **CR1** — Check the diff against the approved spec and design, and report each criterion missing, each behaviour
  nobody asked for and each AC misread, because code can pass every test and still build the wrong thing.
- **CR2** — Split a change past the PD9 size limit (`planning`'s `program-design`) into tickets along its slices, not
  counting generated files, because review usefulness falls as a change grows.
- **CR3** — Send a change to CI config, build files, a new dependency, code-owner files or agent instruction files to
  the human, because an agent that edits its own gate, rules or dependencies can pass any change.
- **CR4** — Give each raised threshold or disabled check in a config file its reason on the line above it, because a
  silent exception hides the problem the check was built to catch.
- **CR5** — For each changed behaviour, name the consumers outside the diff it reaches at `file:line`, and prove the
  fact its safety rests on by running code, because breakage outside the diff never shows in it.
- **CR6** — For each changed behaviour, name its smallest realistic regression and the assertion that would fail on
  it; a skipped, no-throw, snapshot-only or mock-call check does not count, because such a test passes while seeing nothing.
- **CR7** — For each removed or replaced chunk, name the behaviour or contract it carried and where the change
  re-establishes or retires it, because a removed guard leaves no line to review.

## When X, use Y

| situation | use | why |
|---|---|---|
| the diff passes every test | still compare it with the spec and design, criterion by criterion (CR1) | tests prove what was written, not what was asked |
| the change passes the size limit of PD9 in [program-design.md](../../planning/references/program-design.md) | split it into tickets along its slices (CR2) | a finder stops reading closely |
| generated files, lock files or a mechanical rename | leave them out of the count, and list them in the PR (CR2) | they are not read line by line |
| the diff touches `.github/workflows/`, `.gitlab-ci.yml`, a build file, a dependency manifest that adds a dependency, `CODEOWNERS`, `AGENTS.md`, `CLAUDE.md`, `.claude/` or `.agents/` | the human reviews that file before the gate (CR3) | it changes how the change is judged |
| a lint or coverage threshold goes down, or a check is switched off | its reason on the line above, in the same change (CR4) | the next reader sees why the rule bends |
| a change to a behaviour that code outside the diff relies on | each impacted consumer named at `file:line`, not "callers of X"; the one fact the change is safe because of, proved by a script or test that calls the real code (CR5) | a convincing write-up reads the same whether or not it is true |
| a changed behaviour | its smallest realistic regression (a branch inverted, a default dropped, a field left out) and the test assertion that fails on it (CR6) | "this line could go without a test failing" names no regression |
| the test that seems to cover it is skipped, flaky, not run by default, only checks that nothing was thrown, compares a snapshot, or checks a mock or log call | a finding: that test does not count (CR6) | it passes whether or not the behaviour is right |
| a test the diff touches still asserts the old behaviour, or no longer exercises anything | a finding naming what it should assert, or that it should go (CR6) | a stale test pins the wrong outcome |
| the diff adds a test | the junk patterns of V3 (`testing/value-bar.md`) | that is where a new test's worth is judged |
| the diff edits an existing test, a snapshot or a golden file | TI1–TI5 (`test-integrity`) | that is where an edit to a test's check is judged |
| the diff removes or replaces a check, a default, an error path or a call | where the change puts it back, or why it is retired on purpose; a reference left pointing at the removed code is a finding (CR7) | the removal shows as red lines nobody reads for what they did |

## Good / Bad

### CR1 — Compare the diff with what was approved

**Bad**
```text
Review: tests pass, code is clean. No findings.
```
The spec says a reserved loan cannot be renewed. The diff has no reservation check and adds a renewal limit nobody
asked for.

**Good**
```text
CR1 · Act on · LoanService.java:44 — missing: "a reserved loan cannot be renewed"
CR1 · Act on · LoanService.java:51 — extra: a limit of 3 renewals is not in the spec
```
Each finding names the criterion or the extra behaviour, and its line.

### CR5 — Name the consumers outside the diff and prove the fact

**Bad**
```text
Review: dueDate() now returns UTC. Callers of dueDate() should be fine. No findings.
```
"Callers of dueDate()" names no one, and "should be fine" proves nothing. The reminder job still compares the date
with local midnight.

**Good**
```text
CR5 · consumers of LoanService.dueDate(), now UTC:
- ReminderJob.java:30 compares it with LocalDate.now(): a day off in zones ahead of UTC
- LoanExport.java:12 formats it as ISO-8601 with its zone: safe
CR5 · proved: DueDateZoneTest runs the real ReminderJob in UTC+2; it fails
CR5 · Act on · ReminderJob.java:30 — convert to the library's zone before comparing
```
Each consumer is named at its line, and the claim the change rests on is run, not argued.

## Decided edges

- **Skip the size budget when** the change is one mechanical rename or a formatter run. — **Do not skip when** the
  change mixes such a pass with new logic: split the pass out (CR2). — **Confidence** high
- **Skip the human stop when** a patch-level dependency bump changes only a version in a build file: list it in the
  PR. — **Do not skip when** CI config, code owners or agent instruction files change (CR3). —
  **Confidence** medium
- **Skip CR4 when** a threshold goes up or a check is switched on. — **Do not skip when** a threshold goes down or a
  check is switched off. — **Confidence** high
- **Skip the consumer list when** the behaviour has no consumer outside the diff, such as a private method whose only
  callers are in the change. — **Do not skip when** it is shared code, a public contract, configuration or a minor or
  major library version bump (CR5). — **Confidence** high
- **Skip the regression search when** a part changes no behaviour (formatting, a rename, a type-only change) or the
  compiler or type checker already enforces it. — **Do not skip when** a return value, a thrown error, a side effect
  or observable state changes (CR6). — **Confidence** high
- **Skip the deletion check when** the removal is a pure rename, a formatting change or code nothing reached. —
  **Do not skip when** the removed code enforced a check, a default, an error path or a call (CR7). — **Confidence**
  high

## Review checks

Walk the approved spec and design, then the whole diff.

- [ ] CR1 — For each acceptance criterion, find the code that meets it. For each behaviour in the diff, find the
  criterion that asked for it. Each one missing, extra or misread is a finding.
- [ ] CR2 — Count the changed lines and files, generated files excluded, except the decided edges above. A change
  past the PD9 size limit is an Act-on finding.
- [ ] CR3 — List the files the diff changes under CI config, build files, `CODEOWNERS` and agent instruction files
  (`.agents/` included), and each dependency the diff adds, except the decided edges above. Each one without the human's review is a finding.
- [ ] CR4 — For each lowered threshold or disabled check in a config file, find its reason on the line above. Each
  one without a reason is a finding.
- [ ] CR5 — For each changed behaviour with a consumer outside the diff (shared code, a public contract, configuration,
  a dependency bump), find the named consumers and the run that proves the claim. "Callers of X" with no
  `file:line`, or a safety claim with nothing run behind it, is a finding.
- [ ] CR6 — For each changed behaviour, find its named regression and the assertion that fails on it. A behaviour
  with none, or covered only by a skipped, no-throw, snapshot-only or mock-call check, is a finding.
- [ ] CR7 — For each removed or replaced chunk, find the behaviour it carried and where it is re-established or why
  it is retired. One with neither, or a reference left to removed code, is a finding.
