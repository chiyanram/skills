# Verify

How the implementer proves a change is done before review: what it asks instead of guessing, which tests prove the
change, what evidence goes in the PR, and what to do with a red check, a conflict or a quarantine. Read it when you
build a change, before you call it ready, or when you check an implementer's evidence rows.

## Rules

- When the spec does not settle a point the code must decide, post it as an open question on the PR and stop; never
  guess an acceptance criterion, because a guessed criterion ships the wrong behaviour with passing tests. A test that
  fails and looks wrong is an open question too, not an edit to the test.
- Give each changed behaviour a test that fails when the change is reverted, because a test that passes either way
  proves nothing about the change. A refactor with no behaviour change names the tests that cover it instead.
- For a bug fix, have a test-first run write the failing test from the bug spec before the fix is written, and paste
  its red output (`testing` skill, Fixing a bug), because an implementer that tests its own fix shares its misreading.
  When the bug cannot be reproduced in a test, say so and ask.
- Never delete, skip or weaken a test to reach green; fix the code, or ask, because a weakened test hides the defect
  it was written to catch. A test whose behaviour the spec removes goes with it, named in the PR.
- Call a change ready only when its build, lint and touched tests pass at the pushed commit, checked by a script,
  because an implementer's "done" is a report, not evidence.
- For each acceptance criterion a user can see (a screen, an API response, a message), drive the running app and
  paste the call and what came back, because passing tests can still leave the feature broken for the user.
- Map every acceptance criterion to its evidence in the PR (criterion, command, result, at the pushed commit),
  because a criterion with no evidence is unproved:

  | the criterion | its evidence |
  |---|---|
  | one a user sees | the app run: the call and what came back |
  | one only code sees | the test that proves it, by name |
  | what a file says | `grep` or `git diff` on that file, and what it printed |

- Copy each result from its command's output, and never cite a gate run as evidence for file content or for more
  than one criterion, because a gate proves only what its tests check.
- Resolve a conflict with the base by reading why each side changed (commits, PR, ticket), keeping both where they
  fit, in a stated order, and rerunning the checks, because picking ours or theirs silently drops a deliberate change.
  Two intents that cannot both hold go to the human with each side's reason and a recommendation. Regenerate a lock
  file or other generated file with its tool. Both sides from this branch's own commits need no history read.
- Treat a red check as a failure: fix the code, and never re-run it automatically. A check that looks flaky is
  reported red; a person may re-run it once, naming the cause or filing a bug with the failing value. A second failure
  stays red, because a re-run until green hides an intermittent bug.
- Quarantine only one failing test whose cause is outside the change, never a whole job, done by a person, with an
  owner, a ticket and an expiry within the project's limit, because a broad or endless quarantine hides the next real
  failure. With only job names known, ask a person, and file a ticket to report test ids.
- When a check passes only because a test is quarantined, name each test and its expiry in the PR's status note,
  because a green that hides a failure reads as all clear.

## Good / Bad

### Every criterion has its evidence

**Bad**
```text
All tests pass. Ready for review.
```
No criterion is named, and nothing says which command ran or at which commit.

**Good**
```text
Evidence at 4f2c9e1
| criterion                         | command                                   | result       |
| a reserved loan is not renewed    | ./gradlew test --tests '*RenewalSpec*'    | 6 passed     |
| renewal answers 409 when reserved | curl -X POST localhost:8080/loans/7/renew | 409 Conflict |
```
Each criterion points at a command and its result at the pushed commit.

## Review

Walk the PR body, its commits and the diff of its tests. Each line is a finding.

- A decision on a point the spec did not settle, made by the implementer alone.
- A changed behaviour with no test that fails when the change is reverted.
- A bug fix with no commit that adds the failing test before the fix commit, or no note that a test-first run wrote
  it.
- A removed, skipped or loosened test whose behaviour stays.
- No script result for build, lint and touched tests at the PR's head, or one at another commit.
- A criterion a user can see with no app run.
- A criterion with no evidence row, a described result, a gate run as evidence for file content, or one gate run on
  more than one row.
- A conflict resolved with a side dropped for no reason, a hand-edited lock file, conflict markers left, no note of
  what each side changed and why, or no check run at the new head.
- A check that went from red to green at the same commit by an automatic re-run, a second re-run, or a re-run with no
  named cause or bug.
- A quarantine entry with a missing test id, owner, ticket or expiry, a whole job, or an expiry past the limit.
- A green with a quarantined test named only in a log, or not at all.
