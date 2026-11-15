# Debugging specs

The steps and the rules for every job are in [SKILL.md](SKILL.md).

## Read the failure

The run already recorded everything up to the failure. Read it before you rerun anything.

1. **The error and its call log.** The call log under the error says what the locator matched, how often it retried
   and what blocked it ("element is not visible", "waiting for getByRole('button', { name: 'Return' })").
2. **The trace:** `npx playwright show-trace test-results/<test>/trace.zip`, or the trace link in the HTML report.
   It shows each action with the DOM before and after, the console, and every network call. Open the step that
   failed and read the page as it was.
3. **The app's output** in the run (`webServer.stdout: 'pipe'`): a server error at that moment is the cause, not the
   locator.

Fix every line the evidence covers, not only the one that failed. The DOM at the failure shows the names the next
lines need; each wrong line you leave costs another run.

## App, spec or environment?

| You see | It is | Do |
|---|---|---|
| the same step fails with the same error on every run | the app, or a screen that changed | reproduce once with `--headed`; fix the app, or update the locator and its expectation together |
| the step fails on some runs only | a flake in the spec or a race in the app | the flaky table below |
| the app never became ready, a seed call failed, a secret is missing | the environment | fix the environment; do not touch the spec |
| a strictness error: the locator matched two elements | the spec, or two of the same control on the page | narrow the locator; if the user also cannot tell them apart, it is an app bug |
| it passes locally and fails in CI | timing, data, or the operating system | run in the CI container, or with `--workers` set to CI's count |

## Flaky specs

| Cause | Sign | Fix |
|---|---|---|
| a one-shot read caught the page mid-update | `expect(await locator.textContent())` | a web-first matcher |
| the wait started after its trigger | a `waitForResponse` or popup wait after the click | start the wait first (`writing-specs.md`) |
| shared data | fails only with other tests, or on a retry | run-unique data from a fixture, deleted after `use()` |
| the app was not ready for the action | acts on the previous page's element | assert on the element you are about to use, or on the URL |
| time | fails near midnight, a month end or in another time zone | `page.clock`, and a fixed `timezoneId` in the config |
| an animation or an overlay | "element intercepts pointer events" | wait for the overlay to go (`toBeHidden`); never `force: true` |
| test order | passes alone, fails in the suite | find the test that leaves state behind; every test passes alone |

Measure the fix: `npx playwright test <file>:<line> --repeat-each=10 --retries=0` before and after. A fix is done at
ten of ten. A retry or a longer timeout that turns it green hides the race; it is not a fix.

## Tools

- `--headed` watches the run; `--ui` reruns on each save and keeps the trace of each run.
- `--debug` (or `PWDEBUG=1`) opens the inspector and pauses before each action; the inspector also picks a locator
  for an element you point at.
- `npx playwright codegen <url>` records locators for a screen you have not seen. Use what it gives as a draft: keep
  the role and label locators, replace any CSS it falls back to.
- `await page.pause()` stops at one line. Remove it before you commit; the lint fails it.

## Quarantine

A spec that fails for a reason you cannot fix now is quarantined, never deleted and never retried until it passes:

```ts
test.fixme('a member renews a loan twice', { annotation: { type: 'issue', description: '#482' } }, async () => {
  // ...
});
```

- Quarantine one test, never a file or the job, with an open issue, an owner and an expiry.
- Say in the run's summary which tests are quarantined, so a green run does not read as all clear.
- Remove the `fixme` when the issue closes, and watch the spec pass.
