# Code review

What the code review checks beyond each topic reference: that the diff builds what was approved, that it stays a
reviewable size, and that the agent did not change its own gate. Read it when you review a pull request's code, or
before you split a change.

## Rules

- **CR1** — Check the diff against the approved spec and design, and report each criterion missing, each behaviour
  nobody asked for and each requirement misread, because code can pass every test and still build the wrong thing.
- **CR2** — Keep a change within about 400 changed lines and 15 files, and split it beyond 20 files, not counting
  generated files, because review usefulness falls as a change grows.
- **CR3** — Send a change to CI config, build files, code-owner files or agent instruction files to the human, because
  an agent that edits its own gate or rules can pass any change.
- **CR4** — Give each raised threshold or disabled check in a config file its reason on the line above it, because a
  silent exception hides the problem the check was built to catch.

## When X, use Y

| situation | use | why |
|---|---|---|
| the diff passes every test | still compare it with the spec and design, criterion by criterion (CR1) | tests prove what was written, not what was asked |
| the change is over 20 files | split it into issues along its slices (CR2, PD9) | a reviewer stops reading closely |
| generated files, lock files or a mechanical rename | leave them out of the count, and list them in the pull request (CR2) | they are not read line by line |
| the diff touches `.github/workflows/`, `.gitlab-ci.yml`, a build file, `CODEOWNERS`, `AGENTS.md`, `CLAUDE.md` or `.claude/` | the human reviews that file before the gate (CR3) | it changes how the change is judged |
| a lint or coverage threshold goes down, or a check is switched off | its reason on the line above, in the same change (CR4) | the next reader sees why the rule bends |

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

## Decided edges

- **Skip the size budget when** the change is one mechanical rename or a formatter run. — **Do not skip when** the
  change mixes such a pass with new logic: split the pass out (CR2). — **Confidence** high
- **Skip the human stop when** a patch-level dependency bump changes only a version in a build file: list it in the
  pull request. — **Do not skip when** CI config, code owners or agent instruction files change (CR3). —
  **Confidence** medium
- **Skip CR4 when** a threshold goes up or a check is switched on. — **Do not skip when** a threshold goes down or a
  check is switched off. — **Confidence** high

## Review checks

Walk the approved spec and design, then the whole diff.

- [ ] CR1 — For each acceptance criterion, find the code that meets it. For each behaviour in the diff, find the
  criterion that asked for it. Each one missing, extra or misread is a finding.
- [ ] CR2 — Count the changed lines and files, generated files excluded, except the decided edges above. Over 20 files
  is an Act-on finding; over 400 lines or 15 files is a Consider finding.
- [ ] CR3 — List the files the diff changes under CI config, build files, `CODEOWNERS` and agent instruction files,
  except the decided edges above. Each one without the human's review is a finding.
- [ ] CR4 — For each lowered threshold or disabled check in a config file, find its reason on the line above. Each
  one without a reason is a finding.
