---
name: playwright
description: Use when you write, run, fix or review a Playwright end-to-end spec or smoke spec in the browser - its locators, waits and assertions, a sign-in setup and storageState, test data fixtures, page objects, playwright.config.ts and webServer, a failing or flaky browser test, a trace, visual snapshots, or the Playwright job in CI.
---

# Playwright

A spec drives the real app in a browser the way a user does, and fails when a journey breaks. Which journeys deserve a
spec, and every rule that holds for all tests, are in the `testing` skill; this skill is how to write, run and fix
the spec once you know it belongs in the browser.

## Start here: read the file for the job

Read the one file that matches the job before you do anything else. The Rules below hold for every job.

| When you are | Read |
|---|---|
| Writing or changing a spec: its shape, fixtures and data, sign-in, locators, waits, assertions, time, network, page objects | [writing-specs.md](writing-specs.md) |
| Setting up or changing `playwright.config.ts`, starting the app, running specs from the CLI, the CI job, visual snapshots | [running.md](running.md) |
| Fixing a failed or flaky spec, reading a trace, deciding whether it is the app, quarantining | [debugging.md](debugging.md) |

## Workflow: writing a spec

1. Read the config and one passing spec next to the one you write. Use their fixtures, setup project and tags; a
   second way to sign in or seed data drifts from the first.
2. Shape the file first: one `test.describe` per feature, one test per behaviour, each title naming the outcome it
   checks. Each test runs arrange, act, assert, with every `expect` last.
3. Start each test on the screen it covers: the saved sign-in, `page.goto` on the screen's path, and data from a
   fixture that calls the API. Every step before that screen runs on every run.
4. Learn the accessible names from the component source or a `--headed` run, never from memory. Write each locator
   by role, then label or text.
5. Run only that test, `npx playwright test tests/<feature>.spec.ts:<line>`, and watch it pass.
6. Break the feature on purpose (comment out the handler, change the text it shows) and watch the spec fail for that
   reason. A spec never seen failing proves nothing. Undo the break.

## Workflow: fixing a failed spec

1. Read the failure: the error, the call log under it, and the trace (`npx playwright show-trace <trace.zip>`). The
   trace already holds every step, the DOM and the network up to the failure; do not walk the flow again by hand.
2. Decide what failed: the app, the spec, or the environment (`debugging.md`). A step that fails at the same place
   with the same error on every run is the app or a changed screen, not a flake.
3. Fix every line the evidence covers, not only the one that failed; the screen at failure shows the names the next
   lines need. Never add a sleep, raise a timeout or loosen a screenshot tolerance to get past it.
   Refresh a baseline only for a change you meant (`running.md`).
4. Rerun only that test while you fix it: by `file:line`, `--retries=0`, and `--headed` when you need to see it.
5. After it passes, run it ten times, `--repeat-each=10 --retries=0`. Ten of ten, or it is still flaky.

## Workflow: reproducing a reported bug

A reported bug, or a finding from a review or an exploration, is a claim until a spec proves it.

1. Write a spec that does the reported steps and asserts the expected behaviour, so it fails today.
2. Run it. It fails on the reported defect: the bug is confirmed. It passes: the bug did not reproduce, so say so and
   keep the spec only as a regression test. It fails on something else: the repro is wrong; sharpen it.
3. Assert only the defect. A count or a record another test changes makes the spec fail for the wrong reason.
4. Fix the app; the same spec turning green is the proof, and it stays as the regression test.

## Rules

- Lint the spec files with `eslint-plugin-playwright`: `missing-playwright-await`, `prefer-web-first-assertions`,
  `no-wait-for-timeout`, `no-networkidle`, `no-nth-methods`, `no-raw-locators`, `no-conditional-in-test`,
  `no-conditional-expect`, `no-force-option`, `expect-expect`, `no-focused-test`, `no-page-pause`, `require-annotation-reason`. A lint
  fails every time; prose can be missed.
- Find elements by role, then label or text, test id last; never a CSS class or XPath, which change with styling.
- Check page state with web-first matchers (`await expect(locator).toHaveText(...)`), never a one-shot read, which
  runs before the page settles.
- Wait on a state (an assertion, a URL, a response), never on time; no `waitForTimeout`, no `networkidle`.
- Await every action and every `expect`. An un-awaited `expect` can end the test green before it checks.
- One behaviour per test; an "and" in a title is two tests. Every test passes alone and in any order.
- Reach dependencies through a fake or a local instance. Real internet only in a test tagged `@external` that skips
  when the site is unreachable.
- Use test accounts and test data only; a trace, video or screenshot keeps what the page showed and what was typed.
- Skip only for a named missing capability, with the reason. Quarantine with `test.fixme` naming an open issue.
