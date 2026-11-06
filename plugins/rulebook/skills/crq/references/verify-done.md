# Verify done

How a writer proves a change is done before review: what it asks instead of guessing, which tests prove the change,
and what evidence goes in the pull request. Read it when you build a change, before you call it ready, or when you
check a writer's proof.

## Rules

- **VB1** — When the spec does not settle a question, post it as an open question and stop; never guess an
  acceptance criterion, because a guessed criterion ships the wrong behaviour with passing tests.
- **VB2** — Give each changed behaviour a test that fails when the change is reverted, because a test that passes
  either way proves nothing about the change.
- **VB3** — Call a change ready only when its build, lint and touched tests pass at the pushed commit, checked by a
  script, because a writer's "done" is a report, not proof.
- **VB4** — For each acceptance criterion a user can see, drive the running app and paste what it returned, because
  passing tests can still leave the feature broken for the user.
- **VB5** — Map every acceptance criterion to its evidence in the pull request (criterion, command, result), because
  a criterion with no evidence is unproved.
- **VB6** — Never delete, skip or weaken a test to reach green; fix the code, or ask, because a weakened test hides
  the defect it was written to catch.
- **VB7** — For a bug fix, have a separate run write the failing test from the bug spec before the fix is written,
  because a writer that tests its own fix shares its misreading.

## When X, use Y

| situation | use | why |
|---|---|---|
| the spec is silent or unclear on a point the code must decide | an open question on the pull request, then stop (VB1) | a guess becomes behaviour nobody approved |
| a test fails and the test looks wrong | an open question, not an edit to the test (VB6, VB1) | the test may be the only record of the requirement |
| a criterion a user sees: a screen, an API response, a message | a run of the app: the call made and what came back (VB4) | the test may miss how the parts fit |
| a criterion only code sees | the test that proves it, by name (VB5) | the test is the evidence |
| a bug fix | a separate run writes the failing test first (VB7); the writer runs it locally and pastes the failure (S6) | the test and the fix stay independent |

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

- **Skip a test that fails on revert when** the change is a refactor with no behaviour change and the tests that cover it are
  named. — **Do not skip when** any public result changes (VB2). — **Confidence** high
- **Skip the app run when** no acceptance criterion is visible to a user. — **Do not skip when** a criterion names a
  screen, a response or a message (VB4). — **Confidence** high
- **Skip VB6 when** the spec removes a behaviour and its test goes with it, named in the pull request. — **Do not skip
  when** a test is removed, skipped or loosened while its behaviour stays (VB6). — **Confidence** high
- **Skip the separate test run when** the bug cannot be reproduced in a test: say so, and ask. — **Do not skip
  when** the bug spec names inputs and an expected result (VB7). — **Confidence** medium

## Review checks

Walk the pull request body, its commits and the diff of its tests.

- [ ] VB1 — For each behaviour the spec does not settle, find the open question and its answer. A decision the
  writer made alone is a finding.
- [ ] VB2 — For each changed behaviour, find a test that fails when the change is reverted. No such test is a
  finding.
- [ ] VB3 — Find the script's result for build, lint and touched tests at the pushed commit, the pull request's head.
  A result at another commit, or none, is a finding.
- [ ] VB4 — For each criterion a user can see, find the app run: the call and what came back. Each one missing is a
  finding.
- [ ] VB5 — Find one evidence line per acceptance criterion. Each criterion without one is a finding.
- [ ] VB6 — In the test diff, find each removed, skipped or loosened test. One whose behaviour stays is a finding.
- [ ] VB7 — For a bug fix, find the commit that adds the failing test, before the fix commit, and the note that a
  separate run wrote it. Each one missing is a finding.
