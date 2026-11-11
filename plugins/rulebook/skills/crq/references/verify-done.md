# Verify done

How the implementer proves a change is done before review: what it asks instead of guessing, which tests prove the
change, and what evidence goes in the PR. Read it when you build a change, before you call it ready, or when you
check an implementer's evidence rows.

## Rules

- **VB1** — When the spec does not settle a question, post it as an open question and stop; never guess an
  acceptance criterion, because a guessed criterion ships the wrong behaviour with passing tests.
- **VB2** — Give each changed behaviour a test that fails when the change is reverted, because a test that passes
  either way proves nothing about the change.
- **VB3** — Call a change ready only when its build, lint and touched tests pass at the pushed commit, checked by a
  script, because an implementer's "done" is a report, not evidence.
- **VB4** — For each acceptance criterion a user can see, drive the running app and paste what it returned, because
  passing tests can still leave the feature broken for the user.
- **VB5** — Map every acceptance criterion to its evidence in the PR (criterion, command, result), because
  a criterion with no evidence is unproved.
- **VB6** — Never delete, skip or weaken a test to reach green; fix the code, or ask, because a weakened test hides
  the defect it was written to catch.
- **VB7** — For a bug fix, have a test-first run write the failing test from the bug spec before the fix is written,
  because an implementer that tests its own fix shares its misreading.
- **VB8** — Resolve a conflict with the base by reading why each side changed (commits, PR, ticket), keeping both
  where they fit, and rerunning the checks, because picking ours or theirs silently drops a deliberate change.
- **VB9** — Treat a red check as a failure: never re-run it automatically; a person may re-run it once, naming the
  cause or a bug ticket with the failing value, because a re-run until green hides failures.
- **VB10** — Copy each evidence row's result from its command's output; never cite a gate run as evidence for file
  content or for more than one criterion, because a gate proves only what its tests check.
- **VB11** — Quarantine one failing test, never a whole job, with an owner, a ticket and an expiry within the
  project's quarantine limit, because a broad or endless quarantine hides the next real failure.
- **VB12** — When a check passes only because a test is quarantined, say so where people read the result, naming each
  test and its expiry, because a green that hides a failure reads as all clear.

## When X, use Y

| situation | use | why |
|---|---|---|
| the spec is silent or unclear on a point the code must decide | an open question on the PR, then stop (VB1) | a guess becomes behaviour nobody approved |
| a test fails and the test looks wrong | an open question, not an edit to the test (VB6, VB1) | the test may be the only record of the behaviour |
| a criterion a user sees: a screen, an API response, a message | a run of the app: the call made and what came back (VB4) | the test may miss how the parts fit |
| a criterion only code sees | the test that proves it, by name (VB5) | the test is the evidence |
| a criterion about what a file says | `grep` or `git diff` on that file, and what it printed (VB10) | a gate run passes whatever the file says |
| a bug fix | a test-first run writes the failing test first (VB7); the implementer runs it locally and pastes the failure (S6) | the test and the fix stay independent |
| a conflict between two changes that can both hold, such as two sections added at the end of one file | both sides kept, in a stated order (VB8) | each side was made on purpose |
| a conflict between two intents that cannot both hold | an open question to the human (VB1), with each side's reason and a recommendation | choosing between intents is the human's call |
| a conflict in a lock file or another generated file | the file regenerated with its tool, never merged by hand (VB8) | a hand-merged lock file is broken or stale |
| a check fails and the cause is in the change | fix the code; never re-run hoping for green (VB9) | a fail is a fail |
| a check fails and looks flaky | report it red; a person may re-run it once, naming the cause or filing a bug ticket with the failing value (VB9) | a flaky test re-run until green hides an intermittent bug |
| the person's one re-run fails again | it stays red: fix it or file the bug, with no second re-run (VB9) | a second re-run is the automatic retry again |
| a test fails again and again for a cause outside the change | a person quarantines that one test, with an owner, a ticket and an expiry within the project's limit (VB11) | the rest of the check still guards the change |
| only job names are known, not test ids | the job is quarantined as a stated limit, with the shortest expiry, and the ticket says so (VB11) | a job-wide entry hides any new failure in that job |
| a check is green only because of a quarantined test | the PR's status note names each quarantined test and its expiry (VB12) | people read the status note, not the log |

## Good / Bad

### VB5 — Every criterion has its evidence

**Bad**
```text
All tests pass. Ready for review.
```
No criterion is named, and nothing says which command ran or at which commit.

**Good**
```text
Evidence at 4f2c9e1
| criterion                         | command                                  | result       |
| a reserved loan is not renewed    | ./gradlew test --tests '*RenewalSpec*'   | 6 passed     |
| renewal answers 409 when reserved | curl -X POST localhost:8080/loans/7/renew | 409 Conflict |
```
Each criterion points at a command and its result at the pushed commit.

## Decided edges

- **Skip a test that fails on revert when** the change is a refactor with no behaviour change and the tests that cover
  it are named. — **Do not skip when** any public result changes (VB2). — **Confidence** high
- **Skip the app run when** no acceptance criterion is visible to a user. — **Do not skip when** a criterion names a
  screen, a response or a message (VB4). — **Confidence** high
- **Skip VB6 when** the spec removes a behaviour and its test goes with it, named in the PR. — **Do not skip
  when** a test is removed, skipped or loosened while its behaviour stays (VB6). — **Confidence** high
- **Skip the test-first run when** the bug cannot be reproduced in a test: say so, and ask. — **Do not skip
  when** the bug spec names inputs and an expected result (VB7). — **Confidence** medium
- **Skip the history read when** both sides of the conflict are this branch's own commits: their reason is already
  known. — **Do not skip when** the base side came from another PR (VB8). — **Confidence** high

## Review checks

Walk the PR body, its commits and the diff of its tests.

- [ ] VB1 — For each behaviour the spec does not settle, find the open question and its answer. A decision the
  implementer made alone is a finding.
- [ ] VB2 — For each changed behaviour, find a test that fails when the change is reverted. No such test is a
  finding.
- [ ] VB3 — Find the script's result for build, lint and touched tests at the pushed commit, the PR's head.
  A result at another commit, or none, is a finding.
- [ ] VB4 — For each criterion a user can see, find the app run: the call and what came back. Each one missing is a
  finding.
- [ ] VB5 — Find one evidence row per acceptance criterion. Each criterion without one is a finding.
- [ ] VB6 — In the test diff, find each removed, skipped or loosened test. One whose behaviour stays is a finding.
- [ ] VB7 — For a bug fix, find the commit that adds the failing test, before the fix commit, and the note that a
  test-first run wrote it. Each one missing is a finding.
- [ ] VB8 — For each merge or rebase commit that resolved conflicts, find the note of what each side changed and why,
  in the merge commit message or the PR body, and a check run at the new head. A side dropped with no
  reason, a hand-edited lock file, conflict markers left behind, or no check run after the merge, is a finding.
- [ ] VB9 — For each check that went from red to green at the same commit, find the person who re-ran it and their
  named cause or bug ticket with the failing value. An automatic re-run, a second re-run, or a re-run with neither is a
  finding.
- [ ] VB10 — For each evidence row, find a result copied from command output. A described result, a gate run as the
  evidence for file content, or one gate run on more than one criterion's row, is a finding.
- [ ] VB11 — For each quarantine entry the change adds or renews, find one test id (or a stated job-only limit), an
  owner, a ticket and an expiry within the project's limit. A missing field, a whole job with no stated limit, or an
  expiry past the limit is a finding.
- [ ] VB12 — For each check that passed with a quarantined test, find the status note naming each test and its expiry.
  A green with a quarantine named only in a log, or not at all, is a finding.
