# R18 · Playwright / E2E and frontend unit testing — sources vs ours (2026-10-02)

Ticket: `issues/33-research-playwright-frontend.md`. Ours = `git -C ROOT show origin/master:<path>`. Nothing here is approved.

## Summary
1. Playwright official docs **confirm** our core K-rules (isolation, condition waits, real landmarks, serial-only-if-justified); K-08..K-10, K-16, K-17 are platform-specific with no upstream equivalent.
2. **Missing from K-\***: web-first matchers over `expect(await x.getAttribute())`, no `.first()` to dodge strictness, storageState auth, `no-floating-promises` lint, timeout-as-flake-mask. `docs/guides/playwright-rubric.md` has several of them, so there are **two rubrics** for the same files.
3. **New false facts**: the scanner runs **nowhere automatically**. No PostToolUse hook calls it, and `smoke:lint` is in no `make` target. `CORE_SPECS` (smoke-spec:400, rubric.md:73,104) no longer exists; core membership is the `@core` tag (core config:17-20).
4. Frontend unit: Jest 30 + zoneless preset, 81 specs. Only written rule is one CLAUDE.md line. Tests lean on component instance (197 method calls vs 131 DOM reads). Sources say test through the DOM.
5. Candidates: 11 E-rules (e2e) + 10 F-rules (frontend-unit), each with source. All PENDING, for the operator one by one.
6. Below-10k sources (testing-library, KCD blog, angular-testing-library) used only for principles; cursorrules is above 10k stars but adds nothing useful (see §1).

## 1 · Sources (stars via `gh api repos/X --jq .stargazers_count`, 2026-10-02)

| source | stars | used for | verdict |
|---|---|---|---|
| microsoft/playwright — playwright.dev docs | 96,983 | best-practices, locators, test-assertions, test-fixtures, auth, test-retries, test-timeouts, class-page | primary |
| angular/angular — angular.dev testing guides | 101,027 | testing, components-scenarios, zoneless, http/testing, using-component-harnesses | primary |
| affaan-m/everything-claude-code | 270,758 | `rules/angular/testing.md`, `skills/e2e-testing/SKILL.md` | mixed; see contradictions |
| addyosmani/agent-skills | 100,364 | `references/testing-patterns.md:197-235`, `skills/test-driven-development/SKILL.md:305` | adds nothing beyond PW docs (agrees with R13) |
| PatrickJS/awesome-cursorrules | 40,869 | `rules/playwright-e2e-testing-…mdc:21-37`, `rules/jest-unit-testing-…mdc:24-31` | weak: "3-5 tests per file", `page.route` mocking. **Reject** |
| goldbergyoni/javascript-testing-best-practices | 24,617 | README §2.7, §3.2, §3.4, §3.6 | confirms per-test data, stable attributes, no sleep |
| jestjs/jest | 45,461 | runner only | no rules taken |
| testing-library/react-testing-library | 19,657 | flagship of the org whose principles page is cited | principle source |
| testing-library/dom-testing-library · jest-dom | 3,334 · 4,598 | testing-library.com/docs/guiding-principles | <10k, cited for principle 1 only |
| testing-library/angular-testing-library | 791 | — | <10k; **noted, not used** |
| kentcdodds/kentcdodds.com | 2,497 | blog: testing-implementation-details, write-tests | <10k; principle source by author authority |
| thymikee/jest-preset-angular | 919 | our preset (`setup-jest.ts:1-3`) | infra only |

**Contradictions inside sources**

| claim | where | conflicts with |
|---|---|---|
| use `data-cy`, "do not rely on … text content" | ECC `rules/angular/testing.md:155-156` | PW locators: role > text > … > testid |
| `waitForLoadState('networkidle')` | ECC `skills/e2e-testing/SKILL.md:53,59,190` | PW class-page: networkidle "DISCOURAGED … Don't use this method for testing" |
| `fakeAsync` + `tick` | ECC `rules/angular/testing.md:84-96` | Angular: fakeAsync needs zone.js; we are zoneless (`setup-jest.ts:1`) |
| mock with `page.route` | cursorrules `playwright-e2e…mdc:25,33` | our smoke tier runs against the live stack (fake-llm only) |

## 2 · K-* rubric vs Playwright official (`smoke-spec/SKILL.md:227-351`)

| K | ours | Playwright docs | verdict |
|---|---|---|---|
| K-00 fails with feature removed | BLOCKER | "verify … works for end users" (best-practices) | confirm, ours stronger |
| K-01 own data + cleanup | try/finally | isolation + "Fixtures encapsulate setup and teardown" (test-fixtures) | confirm; PW prefers fixture over try/finally |
| K-02 no ordering chain | BLOCKER | "usually better to make your tests isolated" (test-retries) | confirm |
| K-03 read-only `beforeAll` | allowed | beforeAll reruns on every new worker after a failure; worker fixtures preferred | partial |
| K-04 no swallowing catch | BLOCKER | — | ours |
| K-05 serial justified | GAP | serial "not recommended" (rubric.md:51 citing test-parallel) | confirm |
| K-06 real landmark, role/text/testid | BLOCKER | locator priority role>text>label>…>testid; "CSS and XPath are not recommended" | confirm; 50 `locator('.` hits remain |
| K-07 condition waits | GAP | waitForTimeout: "Tests that wait for time are inherently flaky"; networkidle DISCOURAGED; `toPass` default timeout 0 | confirm |
| K-08/09/10/16/17 | platform | — | N/A upstream |
| K-11 fixtures not per-test login | GAP | auth once in setup project → `storageState` | **partial**: `loginViaForm(` ×179, `storageState` ×0 |
| K-12 GWT | NIT | — | ours |
| K-13 tags | GAP | tags + grep supported | ours |
| K-14 screenshot | GAP | traces on CI on first retry | compatible (`trace: 'retain-on-failure'`, smoke config:60) |
| K-15 coverage matrix | GAP | — | ours |

**Missing from K-\*** (PW docs say it; our K-rubric does not)

| missing | PW source | our evidence |
|---|---|---|
| web-first matcher, not `expect(await loc.getAttribute())` | test-assertions "Prefer auto-retrying assertions" | Bad `smoke-33-agent-studio-gallery.spec.ts:100,108`; only in rubric.md A1/A3 |
| `.first()/.nth()` "not recommended" | locators | 105 `.first()` hits |
| reuse auth via `storageState` | auth | 179 UI logins |
| lint with `no-floating-promises` | best-practices "Lint tests" | `eslint.config.js:38` lints `src/**` only; playwright/ gets `tsc` only (`package.json:14`) |
| raised timeout ≠ flake fix | test-timeouts | `test.setTimeout(` ×29; only in rubric.md D4 |
| no third-party sites | best-practices | only rubric.md C5 |
| cross-browser projects | best-practices | chromium only (configs `projects`) — decide N/A? |

**Stale / false (beyond R13)**

| claim | where | fact |
|---|---|---|
| scanner "run on every edit by a PostToolUse hook" | smoke-spec:21-28, :214-219 | `.claude/settings.json:28-29` allow-lists it; PostToolUse `:65-80` runs 3 other hooks |
| `npm run smoke:lint` gates the suite | smoke.md:10-11; smoke-spec:28 | no `Makefile` target calls `smoke:lint` (`lint` = eslint + `typecheck:pw`, Makefile:345-347) → **scanner runs nowhere** |
| "add its glob to `CORE_SPECS`" | smoke-spec:400-402; rubric.md:73,104 | `playwright.core.config.ts:17-20,32` — `grep: /@core/`, no list |
| `retries` | smoke config:49 = 1 | PW: retried pass = `flaky`; `check-flaky.mjs:1-13` surfaces it — consistent |

## 3 · Frontend unit (Angular 21 + Jest)

**What we have** (master): `jest.config.ts` preset jest-preset-angular, jsdom, coverage 80/80/80/70 (`:13-20`); `setup-jest.ts:1-3` zoneless. 81 `*.spec.ts`, 833 `it(`. TestBed in 79 files · `provideHttpClientTesting` 33 · `HttpTestingController` 24 · `componentRef.setInput` 12 · `detectChanges` 49 · `whenStable` 10 · `fakeAsync` 0 · harnesses 0 · `@testing-library` 0. Component specs: `component.x(` ×197 vs `querySelector/nativeElement` ×131. Written rules: CLAUDE.md *"Unit tests for all service calls, signal state and error paths"*; `docs/guides/DEVELOPING.md:271`. No reference file.

| topic | sources | ours | verdict |
|---|---|---|---|
| runner | Angular default is Vitest; Jest not mentioned (angular.dev/guide/testing) | Jest 30 | keep; open Q5 |
| async under zoneless | "`fakeAsync` cannot be used … no zone.js patch"; use native fake timers | `fakeAsync` 0; `jest.useFakeTimers` omnibar:19,36 | confirm |
| change detection | zoneless guide: avoid `detectChanges`, prefer `await fixture.whenStable()`; existing suites may keep it | 49 vs 10 | gap (new tests) |
| inputs | `componentRef.setInput` | Good `agent-feedback-tab.component.spec.ts:58` | confirm |
| DOM vs instance | TL principle 1 "DOM nodes rather than component instances"; KCD: impl-details → false negatives/positives | Bad `agent-feedback-tab…spec.ts:96-103` (asserts `totalPages()` signal); Bad `omnibar.component.spec.ts:64-70` (titled "backdrop clicked", calls `close()`) | gap |
| HTTP | provide `provideHttpClient()` before `provideHttpClientTesting()`; `verify()` in afterEach; `flush(…,{status})` for errors | Good `core/agent.service.spec.ts:39-54` | confirm |
| doubles | Angular: `useValue` stubs, spies | `useValue` + `jest.fn` (feedback-tab:47-52) | confirm; matches U3 |
| harnesses | Angular + ECC `rules/angular/testing.md:46-48` | 0 uses; Material is a dependency | open Q4 |
| pure logic | ECC `:136` pipes without TestBed; Angular basics: class alone tests much | not stated | add |
| coverage target | KCD: diminishing returns past ~70% | 80 lines | keep (operator decision) |

## 4 · Candidate rules — PENDING, put to operator one by one

### testing/references/smoke-specs.md (widened → e2e)

| id | rule (≤25 words) | source | Good/Bad | mode |
|---|---|---|---|---|
| E1 | Locate by role, then label/text; testid only without an accessible name; no CSS class or XPath except the feature's own component tag. | playwright.dev/docs/locators; K-06 EDGE smoke-spec:274 | Good smoke-06:103 | ADAPT |
| E2 | Assert page state with web-first matchers (`toHaveText`, `toHaveAttribute`, `toBeVisible`); never `expect(await locator.x()).toBe…`. | playwright.dev/docs/test-assertions | Bad smoke-33:100,108 | ADOPT |
| E3 | No `.first()`/`.nth()`/`.last()` to dodge a strictness error; narrow with role name, `filter`, or chaining. | playwright.dev/docs/locators | — | ADOPT (new code) |
| E4 | Never wait on time: no `waitForTimeout`, sleeps, or `networkidle`; wait on a locator, response, URL, or `expect.poll` with a timeout. | class-page (waitForTimeout, waitForLoadState) | Bad ECC e2e SKILL:53 | ADOPT |
| E5 | Raise a timeout only for a named slow dependency (live model) with a one-line reason; never to quiet a flake. | playwright.dev/docs/test-timeouts; rubric.md D4 | — | ADAPT |
| E6 | Every `expect` and action is awaited; `@typescript-eslint/no-floating-promises` covers `playwright/`. | best-practices "Lint tests" | eslint.config.js:38 gap | ADOPT (needs config change) |
| E7 | Authenticate once per role via a setup project and `storageState`; log in through the UI only in tests about login. | playwright.dev/docs/auth | 179 `loginViaForm` | ADAPT |
| E8 | Setup-with-teardown used by two or more specs becomes a fixture in `support/fixtures.ts`, not copied try/finally. | playwright.dev/docs/test-fixtures | Good fixtures.ts:17-20 | ADAPT |
| E9 | A non-obvious assertion carries a message: `expect(x, 'what failing means').…`. | test-assertions (custom message) | Good smoke-spec:121 | ADOPT |
| E10 | A pass on retry is a flake: read `check-flaky` output; never add retries, serial mode or timeouts to make it pass. | playwright.dev/docs/test-retries | check-flaky.mjs:1-13 | ADAPT |
| E11 | Never touch systems we do not control; external dependencies go through the stack's local fakes (`fake-llm`). | best-practices "Avoid third-party" | smoke-92 | ADOPT |

### testing/references/frontend-unit.md

| id | rule (≤25 words) | source | Good/Bad | mode |
|---|---|---|---|---|
| F1 | A component test asserts what renders (text, role, attribute); read a signal directly only when nothing on screen shows it. | testing-library guiding-principles #1; KCD impl-details | Bad feedback-tab:96-103 | ADAPT |
| F2 | Drive the component through DOM events on its elements, not by calling its methods. | TL principles #2; Angular components-basics | Bad omnibar:64-70 | ADAPT |
| F3 | New tests: after a state change, `await fixture.whenStable()`; `detectChanges()` stays only in existing tests. | angular.dev/guide/zoneless (Testing) | — | ADAPT |
| F4 | Set inputs with `fixture.componentRef.setInput`, never by assigning component fields. | angular.dev components-scenarios | Good feedback-tab:58 | ADOPT |
| F5 | HTTP: `provideHttpClient()` then `provideHttpClientTesting()`; match method + URL + params; `verify()` in afterEach; one error-flush case per call. | angular.dev/guide/http/testing | Good agent.service.spec:39-54 | ADOPT |
| F6 | Replace injected services with `useValue` objects of `jest.fn()`; never stub the class under test or Angular internals. | angular.dev scenarios (test doubles); U3 | Good feedback-tab:47-52 | ADAPT |
| F7 | No `fakeAsync`/`waitForAsync` (no zone.js); use Jest fake timers and restore them in `afterEach`. | angular.dev scenarios (fakeAsync note) | Good omnibar:19,36 | ADOPT |
| F8 | Pure functions and pipes are tested with plain Jest, no TestBed. | ECC rules/angular/testing.md:136; angular.dev components-basics | — | ADOPT |
| F9 | The test title names the user action and outcome; the body must perform that action (V3 #8). | KCD impl-details; ledger V3 | Bad omnibar:64-70 | ADAPT |
| F10 | Each component spec covers the loading, data, empty and error states the template renders. | CLAUDE.md "signal state and error paths"; ECC :135 | Good feedback-tab:76-83 (error) | ADAPT |

## 5 · Open questions

| # | decide | state now | recommendation |
|---|---|---|---|
| Q1 | two rubrics for smoke | `docs/guides/playwright-rubric.md` (scored A–H) + smoke-spec K-00..K-17 | fold missing rows into K-*, delete the guide |
| Q2 | E7 storageState migration | 179 UI logins, 0 storageState | new specs only; backlog the rest |
| Q3 | scanner has no runner | no hook, no make target | wire `smoke:lint` into `make lint` (cheap) |
| Q4 | DOM helper for unit tests | plain `querySelector`; 0 harnesses; angular-testing-library 791★ | plain DOM + CDK harness for Material only |
| Q5 | Jest vs Angular-default Vitest | Jest 30 | stay; out of scope |
| Q6 | cross-browser | chromium only | record N/A as a Decided edge |
| Q7 | existing violations (105 `.first()`, 50 CSS, 197 method calls) | untracked | rules bind new/touched code; no sweep |
| Q8 | e2e scope | `playwright/unit` + `property` configs exist beside smoke | e2e.md covers smoke only; note the other two tiers |
