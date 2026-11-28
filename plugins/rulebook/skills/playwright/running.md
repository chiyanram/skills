# Running specs

The steps and the rules for every job are in [SKILL.md](SKILL.md).

## The config

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

const port = Number(process.env.E2E_PORT ?? 4200);
const ci = !!process.env.CI;

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: ci,                       // a committed test.only fails the run in CI
  retries: ci ? 1 : 0,                  // one retry in CI to report a flake, never to hide one
  failOnFlakyTests: ci,                 // a test that passed only on the retry fails the run
  reporter: ci ? [['html', { open: 'never' }], ['junit', { outputFile: 'test-results/junit.xml' }]] : 'list',
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/librarian.json' },
      dependencies: ['setup'],
    },
  ],
  webServer: {
    command: `npm run start -- --port ${port}`,
    url: `http://127.0.0.1:${port}/health`,
    reuseExistingServer: !ci,
    stdout: 'pipe',
    timeout: 120_000,
  },
});
```

- **`webServer.url`** probes a health endpoint, so the run starts when the app is ready, not when the port opens.
- **`reuseExistingServer: !ci`** reuses your running server on a laptop and always starts a fresh one in CI. A
  server you started from another branch tests old code: stop it, or run on another port.
- **Take the port from the environment**, so two checkouts (yours and a second agent run) run side by side.
- **`stdout: 'pipe'`** shows the app's output in the run, so a startup error is visible.
- **Retries in CI only, and at most one.** A retry that passes marks the test flaky; `failOnFlakyTests` then fails
  the run, so a flake gets fixed and not hidden.
- **One browser project** until a defect has shown up in only one browser. Each project runs every spec again.

## Running from the CLI

| You want | Run |
|---|---|
| one test while you work on it | `npx playwright test tests/loans.spec.ts:12 --retries=0` |
| to watch it | add `--headed`, or `--ui` for the watch-mode runner |
| to step through it | `--debug`, or `PWDEBUG=1` |
| one feature or tag | `npx playwright test tests/loans.spec.ts`, `--grep @smoke`, `--grep-invert @external` |
| to check a fix of a flake | `--repeat-each=10 --retries=0` |
| only the tests that failed last time | `--last-failed` |
| only specs touched by your change | `--only-changed=origin/main` |
| a full trace for a run | `--trace=on` |
| one CI shard | `--shard=2/4` |
| the report of the last run | `npx playwright show-report` |

## In CI

- **Run the whole suite on the default branch.** On a pull request, `--only-changed=origin/main` can run the specs
  your change touches first, but the gate still runs every spec before merge.
- **Upload the report and traces on every run, failed ones too:** `if: always()` on the upload step, with
  `playwright-report/` and `test-results/`. A failed run without its trace has to be reproduced by hand.
- **Point the CI test view at the JUnit file**, so a failure shows by name in the pull request.
- **Install only the browser you run:** `npx playwright install --with-deps chromium`.
- **Stop early when the app is down:** `--max-failures=10`, so a broken deploy does not wait out every timeout.
- **Shard when the suite is slow**, with `fullyParallel: true` so the shards are even. Give each shard the `blob`
  reporter and merge them into one report with `npx playwright merge-reports`.
- **Make the job a required check.** A spec that does not block merges is a report, not a gate.
- **Test accounts only, from CI secrets.** Traces and screenshots from CI are kept as artifacts.

## Visual snapshots

Use `toHaveScreenshot` only for a defect a role or text check cannot see: layout, overlap, a chart. For structure,
`toMatchAriaSnapshot` checks the accessible tree and does not break on a font.

- The first run writes the baseline and fails. Look at the image, then commit it with the spec.
- Baselines are per browser and operating system (`-chromium-linux.png`). Make the ones CI compares against on CI's
  operating system, in CI or in the same container image, with `--update-snapshots`; a baseline made on a laptop
  never matches Linux CI.
- Mask what changes on its own: `mask: [page.getByTestId('clock')]`. Fix the clock and the data too.
- Before a change you claim has no visual effect, make sure the screen has a baseline. If it has none, make one from
  the code before your edit, then run your change against it; do not commit that laptop baseline. With no baseline,
  the claim is a guess.
- A failing diff is a fail: find the pixels that moved and why. Never raise `maxDiffPixels`, `maxDiffPixelRatio` or
  `threshold`, or edit the `expect.toHaveScreenshot` options or the baseline image to make it pass, because the
  baseline and its tolerance are the spec. Mask only a region you showed changes on its own, never one because it
  failed, and fix its source too.
- If your change moved pixels you did not mean to move, fix or revert that change. Never add markup or CSS whose only
  job is to match the old image, because it hides the real change from the next reader.
- Run `--update-snapshots` only for a change you meant: a design change, a new screen, or a Playwright, browser or
  image upgrade. Run it only on the tests the change touched (`file:line`), on CI's operating system, and review each
  image diff in the pull request like code, because one broad run rewrites the baselines that caught a regression.
- If the baseline itself looks wrong, stop and ask, because then the spec is wrong and only its owner can say what is
  right.
