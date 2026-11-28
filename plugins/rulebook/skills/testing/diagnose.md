# Diagnose

**Build a loop that goes red before you form any theory: the loop finds the cause, and reading the code only guesses
at it.** Read this file for a hard bug: the premise test of "Fixing a bug" stays green and no other test goes red,
the bug is flaky or slow, or it shows only in one environment. An easy bug keeps to "Fixing a bug" in
[SKILL.md](SKILL.md).

## Build the loop

- **Redact** every secret in a command, output or captured payload you show: write `<REDACTED>`. Pass a credential in
  a command as `$VAR`, never as its value.
- Drive the surface the bug names (the API, the screen, the job) yourself, as far as it goes. When the surface is out
  of reach, stop and ask the person, with the reason and how far you got; in crq, the stage ends `needs-human`.
- Build the loop from the first of these that reaches the bug: a failing Spock spec at the owning seam; `curl`
  against the running app; the CLI with a fixture, diffed against a known-good output; a Playwright spec; a captured
  payload replayed through the code path; a Testcontainers harness of one service; a property loop over many inputs;
  `git bisect run` between a good and a bad commit; one input through the old and the new version, diffed.
- **Tighten** it: faster (narrow the scope, skip unrelated setup), sharper (assert the exact symptom, not "no
  crash"), deterministic (pin time, seed random values, isolate files and network).
- For a flaky bug, raise the reproduction rate (loop the trigger, add load, narrow the timing) and state it as 1 in N
  runs, because at a low rate a green run after a fix cannot be told from luck. This loop runs on your machine; a red
  CI check still follows `code`'s verify notes and is never re-run.
- When no loop can be built, stop and ask the person (in crq, `needs-human`): list what you tried, and ask for one
  of: access to the environment that shows it, a redacted captured artifact, or a yes for temporary instrumentation.

Done when one command, already run and shown with its output, drives the bug's code path, asserts the symptom the
reporter gave, needs no person, and goes red in every run, or for a flaky bug in at least 1 of every N runs, with N
stated. With no such command, form no theory.

## Find the cause

- **Minimise.** Cut inputs, callers, config, data and steps one at a time, rerunning the loop after each cut. Done
  when every remaining element is load-bearing: removing any one turns the loop green.
- **Hypothesise.** Write 3 to 5 ranked hypotheses before you test any, because one hypothesis anchors on the first
  plausible idea. Write each as a prediction: "If <X> is the cause, then <changing Y> makes the bug disappear." Put
  them in the PR body; they are not a stop. Test first the one whose result rules out the most of the rest.
- **Instrument** one variable at a time, each probe tied to one prediction: a debugger when you can drive one from
  the shell (`jdb`, a test breakpoint), else a log at the boundary that tells two hypotheses apart. Tag each debug log
  with one prefix, such as `[DEBUG-a4f2]`, so one grep removes them all. For a slow path, measure a baseline first,
  then bisect.
- When a result surprises you, check what you observed before you blame the system: the commit, the file, the
  environment and the input the loop ran on.

## Fix and clean up

- Turn the minimised loop into the failing test of "Fixing a bug" step 2 in [SKILL.md](SKILL.md), and go on from
  there.
- Done when the original loop runs green N times in a row (N from the rate stated above, once for a bug that always
  reproduced), the regression test passes, `git grep '\[DEBUG-'` prints nothing, `git diff --stat` lists only the fix
  and its test, and the PR names the hypothesis that held.

## Review

Walk the diagnosis in the PR. Each line is a finding.

- A theory or a fix with no red loop shown before it.
- A repro not minimised, a hypothesis list with fewer than three, or one with no prediction.
- A `[DEBUG-` tag in the diff, or an unredacted secret in the PR.
- A fix whose PR does not name the hypothesis that held.
