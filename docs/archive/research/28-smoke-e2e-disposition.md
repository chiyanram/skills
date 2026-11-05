# R24 · Smoke / e2e full disposition (2026-10-02)

Ticket: chiyanram/skills **#47** — R24, every existing smoke rule re-decided. Feeds **#2** (G9a testing, where e2e rules E1–E11 are on hold). Nothing in this file is approved.

Baseline is `origin/master` @ `55a5bc9b` (2026-10-02), read with `git show`. `AP` means `/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3`. SK means `.claude/skills/smoke-spec/SKILL.md`. RB means `docs/guides/playwright-rubric.md`. CA means `.claude/skills/smoke-spec/scripts/check-antipatterns.sh`. Spec paths are relative to `aruvii-ui/playwright/e2e/smoke/`.

Operator framing, applied throughout. What we already have is the authentic baseline. It is checked against two things only: Playwright's official docs, and primary guidance from the Playwright team or large tech companies. The goal is the **smallest rule set that serves our four tiers**: core, full, `@llm` and property. A rule that does not earn its place is cut.

## Summary
1. **Our baseline holds up.** Where the Playwright docs speak, they agree with K-00…K-07 and K-11. K-08…K-10 and K-17 are platform rules with no upstream equivalent, and openclaw's deterministic-vs-live lanes back them. The scored rubric (RB) adds four useful rows. The other 34 rows of RB are duplicates, metric noise, or stale.
2. **The mechanical layer runs nowhere, and fails under a C locale.**
   - No hook and no `make` target calls CA or `smoke:lint` (§4 F1–F2).
   - Under `LC_CTYPE=C`, the banner regex flags all **93/93** specs, because the em-dash bytes fall inside its multibyte character class. Under UTF-8 the result is 0/93.
   - The self-test passes 44/44 either way, because it never feeds an em dash.
3. **New gap, not in any of our rules: `networkidle`.** It appears 145 times across 72 specs. Playwright marks it "DISCOURAGED … Don't use this method for testing".
4. **SK's own Good example for K-09 fails CA's rule R15.** The example calls `pollForToolFrame` without `toolFrameSucceeded`.
5. **Five more stale facts:**
   - `CORE_SPECS` no longer exists.
   - `smoke-57-agent-lifecycle` no longer exists.
   - The `injectToken` rule polices a helper that was deleted.
   - smoke-69 T2 is still `fixme` although #618 — the RAG metadataFilter defect it waits on — is closed.
   - 10 sites still pick the workspace with `data[0]`, the #309 flake.
6. **Proposal:** 26 rules in 4 groups, replacing K-00…K-17, RB A–H, SK §authoring and the reviewer agent. The scanner is kept, moved, fixed for locale, and wired into `make lint`.

## 0 · Sources

Star counts come from `gh api repos/X --jq .stargazers_count`, read 2026-10-02.

| source | stars / authority | read | used for |
|---|---|---|---|
| playwright.dev (microsoft/playwright) | 96,984 · the Playwright team | best-practices, locators, test-assertions, class-page, test-fixtures, auth, test-retries, test-timeouts, test-parallel, test-annotations, api/class-test (`test.step`, serial), trace-viewer-intro, pom | primary authority |
| Google Testing Blog — Wacker, *Just Say No to More End-to-End Tests* (2015-04-22) | Google | testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html | keep e2e few |
| *Software Engineering at Google*, ch. 14 "Larger Testing" | Google | abseil.io/resources/swe-book/html/ch14.html | hermetic SUT · no real third-party API · polling, not sleeps · flake = high priority |
| Google Testing Blog — Micco, *Flaky Tests at Google…* (2016-05-27) | Google | testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html | flake rate ~1.5% · rerun or quarantine only marked flakes |
| Microsoft *Code-With Engineering Playbook*, E2E testing | Microsoft (2,736★) | microsoft.github.io/code-with-engineering-playbook/automated-testing/e2e-testing/ | pyramid: e2e tests are few and cover critical journeys |
| addyosmani/agent-skills @2686b62 | 100,390 | `references/testing-patterns.md:197-235` · `agents/test-engineer.md:25-28` · `skills/test-driven-development/SKILL.md:150,184-185` | role locators · e2e only for critical paths · its own example logs in through the UI |
| openclaw/openclaw @b94e5177 | 391,181 | `.agents/skills/control-ui-e2e/SKILL.md` (all 142 lines) · `openclaw-docker-e2e-authoring/SKILL.md` (all 64 lines) | deterministic fake by default; live only when needed (`docker-e2e:13-18`, `control-ui-e2e:47`) · the fake logs requests and the test asserts the payload (`docker-e2e:26-27`) · wait on asserted states (`control-ui-e2e:139`) · never commit screenshots (`:75`) |
| obra/superpowers @8ca22db | 294,076 | `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md:50-60,235-262` | an e2e run that hit a stale server gave wrong results (supports "deploy first") |
| kunchenguid/no-mistakes @6bb5f9f | 8,713 (<10k) | `CONTRIBUTING.md:39-41` · `AGENTS.md:13-14` | recorded fixtures; re-record only when the wire format changes. Principle only |
| affaan-m/everything-claude-code @c70874f | 270,807 | `skills/e2e-testing/SKILL.md:46-59,145-151,190` | **rejected for e2e.** It contradicts the Playwright docs: `networkidle`, testid-first locators, `test.skip(CI)` as quarantine |
| PatrickJS/awesome-cursorrules | 40,871 | (already read in R18) | rejected in R18 for `page.route` mocking and "3-5 tests per file" |
| Playwright rule sets ≥10k★ | `gh search repos` "playwright best practices" and "playwright skill" | best results: lackeyjb/playwright-skill 3,163 · currents-dev 386 · testdino 381 | **none ≥10k** apart from the two rejected above |

## 1 · Disposition table — one row per existing item

Decision key:
- **KEEP** — keep as is.
- **REWRITE** — keep the substance, change the words or the facts.
- **MERGE→x** — fold into proposed rule *x* (rule ids are in §5).
- **DROP** — remove.

"PW" means playwright.dev/docs.

### 1a · SK review rubric K-00…K-17 (SK:227-351)

| id | says (≤12 words) | true on master? | PW position | refs | decision | why |
|---|---|---|---|---|---|---|
| K-00 | test fails with the feature removed | rule holds. smoke-78 B01:407-414 is a repaired instance | best-practices#test-user-visible-behavior | SWE@G ch14 "verification" | KEEP→**A1** | the strongest rule we have; upstream says it more weakly |
| K-01 | own data, cleaned up, unique per worker | fixtures do it (`fixtures.ts:53-106`); 10 sites use `data[0]` workspace (smoke-16:34, 65:63, 78:89 …) | best-practices#make-tests-as-isolated-as-possible; test-parallel#isolate-test-data-between-parallel-workers | openclaw control-ui-e2e:47 | MERGE→**B1** | merges with K-11; adds `defaultWorkspaceId` (`api-helpers.ts:95`) |
| K-02 | no ordering chain between tests | 5 serial files, each with a written reason | test-parallel: "Using serial is not recommended" | — | MERGE→**B2** | same subject as K-05 |
| K-03 | shared setup read-only, fails loudly | true at smoke-51:29-45, but that block calls `apiLogin` (K-11) | test-retries: beforeAll reruns in a new worker after a failure | — | MERGE→**B3** | keep the substance; it becomes a sub-clause of B1/B3 |
| K-04 | no catch turns failure green | holds | — | addy testing-patterns "No async error handling" row | MERGE→**A3** | one "cannot-fail" rule covers catch, `\|\|true`, `??[]` and `if` guards |
| K-05 | serial justified inline | 5/5 justified ("taxonomy B5") | api/class-test: serial not recommended | — | MERGE→**B2** | — |
| K-06 | landmark real, role/text/testid over CSS | smoke-55:18 Good; 51 raw-CSS locators in 23 files | locators priority list; "CSS and XPath are not recommended" | addy :204-215 role locators | MERGE→**A2** (+E1) | landmark and locator are one rule |
| K-07 | waits are condition-based with named budget | 0 `waitForTimeout`; **145 `networkidle` in 72 files**; `pollHistory` sleeps 10s before its first read (`api-helpers.ts:130`) | class-page `networkidle` DISCOURAGED; test-assertions `expect.poll`/`toPass` | SWE@G ch14 "polling … not time-based sleeps"; openclaw :139 | REWRITE→**C1** (+E4) | add `networkidle`; the existing wording missed it |
| K-08 | `@llm` asserts a structural signal | holds (smoke-65 N01-N03) | — | TM3 approved | MERGE→**A4** | one LLM-signal rule |
| K-09 | tool test proves that tool ran | true in specs; **SK's own Good example (SK:119-122) omits `toolFrameSucceeded`**, so CA R15 would HARD-fail it | — | openclaw docker-e2e:26-27 | REWRITE→**A4** | require `toolFrameSucceeded` (or `isApprovalPause` when the gate is the subject) |
| K-10 | unreachable tool asserts failure shape | smoke-65 N08:320-352 | — | — | KEEP→**A5** | a small, real false-green guard |
| K-11 | fixtures, not per-test login | 42 `apiLogin(` in 17 files; 179 `loginViaForm` calls | auth: authenticate once in a setup project, then reuse `storageState` | addy example logs in through the UI | MERGE→**B1** (+E7 open) | §2 E7 |
| K-12 | Given/When/Then why-comments | comments today; 0 `test.step` | api/class-test `test.step` "shown in the report" | GT2 APPROVED (one `test.step` per step) | REWRITE→**D1** | GT2 already decides the form |
| K-13 | tag set legal; `@llm+@core` whitelist | holds: 4 `@llm+@core` (16, 65, 69, 74 live) = `core.config:22-28` | test-annotations#tag-tests | — | KEEP→**D4** | — |
| K-14 | named fullPage screenshot per spec | 92/93 specs have one | best-practices#configure-debugging (trace) | openclaw :75 never commit screenshots | DROP the named-file mandate; keep "≥1 UI test" in **D3** | config `screenshot:{mode:'on'}` already captures every test (`smoke.config:59`); `generate-gallery.mjs` reads both |
| K-15 | coverage matrix for introduced statuses | partly (smoke-51:110-124) | — | GA5 approved (failure path per AC) | MERGE→**D3** | GA5 plus GT5 already cover it |
| K-16 | new tool type has dry-run test | rule stands; cites "root CLAUDE.md §Tool-Authoring DoD" — **no such heading** | — | — | MERGE→tool-types reference Review check | belongs with tool authoring, not with smoke style |
| K-17 | model-reaching test declares model mode | 2 files tagged (69, 92); #609 open | — | openclaw docker-e2e:13-18; TM2/TM3 | KEEP→**D2** | core of the tier model |

### 1b · SK authoring sections (SK:6-198, 384-402)

| id | says | true? | PW | refs | decision | why |
|---|---|---|---|---|---|---|
| SA-1 | `smoke-NN-<feature>.spec.ts`, NN stable | 93 files match; duplicate NN exists (`smoke-90-collection-scoping`, `smoke-90-model-roles`) | — | — | KEEP (one line in When-X) | — |
| SA-2 | reference specs 57-lifecycle/66/60/46 | **`smoke-57-agent-lifecycle` does not exist** (it is `smoke-57-agent-error-paths`) | — | — | REWRITE | stale name |
| SA-3 | two layers: hook blocks every edit; CI runs lint | **FALSE** (§4 F1-F3) | — | — | REWRITE (§3) | — |
| SA-4 | import test/expect from fixtures | 93/93 (CA clean) | test-fixtures | — | MERGE→**B1** | — |
| SA-5 | A5 `loginViaForm`, never `injectToken` | **helper deleted** (`page-helpers.ts:11-12`); calling it fails `typecheck:pw` | — | — | DROP | the compiler already guards it |
| SA-6 | own data + finally + unique names | see K-01 | — | — | MERGE→**B1** | — |
| SA-7 | A1 bootstrap throws, skip only capability | 7 skips, all `externalReachable` (smoke-41) | test-annotations#conditionally-skip-a-test | addy "test.skip permanently" row | MERGE→**A6** | — |
| SA-8 | A4 swallowed catch | — | — | — | MERGE→**A3** | — |
| SA-9 | serial only if unavoidable | — | — | — | MERGE→**B2** | — |
| SA-10 | B1 no waitForTimeout | — | — | — | MERGE→**C1** | — |
| SA-11 | A2/A3 chrome gate, role/text/testid | — | — | — | MERGE→**A2** | — |
| SA-12 | B2 signal table (TOOL frame…) | true; table row "tool_call_log not reachable" unverified | — | — | MERGE→**A4** (table kept as Decided edge) | — |
| SA-13 | failure shape for unreachable tool | — | — | — | = K-10 | — |
| SA-14 | GWT, titles, no banners, enums, desc 20–500 | 20–500 is real (`CreateToolRequest.java:19`) | — | — | SPLIT: GWT→**D1**; banners→general comment rule; enums→code std; 20–500→DROP (the API enforces it with a 400) | — |
| SA-15 | exactly one domain tag + cross-cutting | 93/93 (CA, UTF-8) | annotations#tag-tests | — | KEEP→**D4** | — |
| SA-16 | DoD: UI test + screenshot + matrix + dry-run | — | — | — | split per K-14/15/16 | — |
| SA-17 | model-mode table scripted/real | true (`fixtures.ts:114-145`; smoke config projects) | — | openclaw docker-e2e:13-18 | KEEP→**D2** | — |
| SA-18 | author proposes mode, user confirms | — | — | — | KEEP (Decided edge of D2) | — |
| SA-19 | interim: `@llm` alone = real until #609 | #609 open | — | — | KEEP (Decided edge, dated) | — |
| SA-20 | scripted wiring facts (steps, retries ×4, 500 on unknown key) | matches the fixture | — | no-mistakes recorded fixtures | KEEP as When-X reference | — |
| SA-21 | assert `fakeLlm.requests`, never scripted text | holds (smoke-92) | — | openclaw docker-e2e:26-27 | KEEP→**D2** | — |
| SA-22 | path step 1 copy nearest reference | — | — | — | KEEP (When-X) | — |
| SA-23 | context7 for live API docs | — | — | — | DROP | general tooling advice, not a smoke rule |
| SA-24 | dev loop `cd aruvii-ui && npx …`; gate `npm run smoke` | **contradicts CLAUDE.md** (`make` is the front door; `npm run smoke` does not deploy) | — | superpowers stale-server note | REWRITE→**C5** | — |
| SA-25 | run scanner then reviewer agent | the reviewer agent is deleted under G3 | — | — | REWRITE (§3) | — |
| SA-26 | reporter one path per tier, `open:'never'` | true (`smoke.config:51-55`, `core.config:42-46`) | — | — | KEEP (Decided edge) | config is the operative artefact |
| SA-27 | `screenshot on, fullPage` | true | — | — | KEEP (Decided edge) | — |
| SA-28 | `trace:'retain-on-failure'`, never `'on'` | true | trace-viewer-intro recommends `on-first-retry` | — | KEEP (Decided edge) | our first attempt is the evidence; `retries:0` on core would otherwise lose the trace |
| SA-29 | results/traces/screenshots git-ignored | true (`.gitignore:23-29`) | — | openclaw :75 | KEEP (one line) | — |
| SA-30 | grow core by adding glob to `CORE_SPECS` | **FALSE** — tag `grep:/@core/` (`core.config:17-20,32`) | — | — | REWRITE→**D5** | — |

### 1c · RB items A–H (scored rubric, 38 items + scoring)

RB is read by nothing in `.claude/`. Its only reference is `docs/research/audit-25-routes-selectors.md`.

| id | says | true? | PW | decision | why |
|---|---|---|---|---|---|
| scoring | 100-point deduction, A/B grade | — | — | DROP | G3 verdicts are MET/UNMET; two grading systems for one file is noise |
| A1 | web-first, not `expect(await loc.isVisible())` | 0 `isVisible()`; 2 `getAttribute` (smoke-33:100,108) | test-assertions "Prefer auto-retrying" | MERGE→**C2** | — |
| A2 | every expect awaited | not gated (eslint covers `src/**` only, `eslint.config.js:38`) | best-practices#lint-your-tests | MERGE→**C4** | — |
| A3 | no `toBe` on textContent/getAttribute | 2 sites | test-assertions | MERGE→**C2** | — |
| A4 | sync matchers only for API data | 3 `expect(await resp.text())` are API data, so MET | — | MERGE→**C2** (Decided edge) | — |
| A5 | `expect.soft` for batches | 0 uses | best-practices#use-soft-assertions ("productivity tip") | DROP | a tip, not a correctness rule |
| A6 | `expect.poll`/`toPass` over loops | 4 `expect.poll`; `pollHistory`/`pollForToolFrame` are hand loops | test-assertions | MERGE→**C1** | helpers stay (they join frames); new polling uses `expect.poll` |
| B1 | locator priority role > … > testid | 259 getByRole / 34 getByTestId | locators | MERGE→**A2** | — |
| B2 | no raw CSS | 51 in 23 files | locators | MERGE→**A2** | — |
| B3 | no XPath | 0 | locators | MERGE→**A2** | — |
| B4 | no `.first()/.nth()` to dodge strictness | 109 in 52 files | locators "not recommended" | MERGE→**C3** | — |
| B5 | app-icon/app-select convention | `pickFromSelect` exists | — | DROP | an Angular UI rule (`rules/angular-ui.md`), not smoke |
| C1 | no module-level mutable state | 0 module `let`; 70 describe-scope `let` in 15 files | best-practices isolation | MERGE→**B1** | — |
| C2 | no implicit cross-test chain | — | test-parallel | MERGE→**B2** | — |
| C3 | unique data per worker | fixtures yes | test-parallel#isolate | MERGE→**B1** | — |
| C4 | serial sparingly | — | — | MERGE→**B2** | — |
| C5 | no third-party sites | smoke-41/78 hit open-meteo under `@external` | best-practices#avoid-testing-third-party-dependencies | MERGE→**B4** | — |
| D1 | no waitForTimeout | 0 | class-page | MERGE→**C1** | — |
| D2 | no setTimeout sleeps | 2 raw in specs; helpers loop | — | MERGE→**C1** | — |
| D3 | no `waitForSelector` | 0 | — | DROP | nothing to police |
| D4 | timeouts not to mask flakes | 29 `test.setTimeout` in 13 files, all `@llm`-class | test-timeouts | MERGE→**C5** | — |
| D5 | per-assertion big timeouts targeted | — | — | MERGE→**C5** | — |
| E1 | worker-isolated data | — | — | = C3 → **B1** | duplicate |
| E2 | one feature per file | — | — | DROP | naming already covers it; unenforceable |
| E3 | no ordering list files | none exist | — | DROP | nothing to police |
| E4 | core = stable; `CORE_SPECS` | **stale** (`CORE_SPECS` gone) | — | MERGE→**D5** | — |
| F1 | fixtures, not copied login | — | test-fixtures | MERGE→**B1** | — |
| F2 | POM / helpers, not duplicated selectors | no POM; `page-helpers.ts` has 2 helpers | pom "one such approach" (optional) | DROP | optional upstream; three-use rule in B1 covers it |
| F3 | teardown paired with setup | — | test-fixtures "encapsulate" | MERGE→**B1** | — |
| F4 | worker-scoped expensive fixtures | none exist | test-fixtures#worker-scoped-fixtures | DROP (Decided edge) | license caps use semaphores instead (`workspace-lock.ts`) |
| G1 | trace retain-on-failure | true | trace-viewer-intro | = SA-28 | duplicate |
| G2 | named screenshot per spec | — | — | = K-14 → DROP | — |
| G3 | screenshot config on/fullPage | true | — | = SA-27 | — |
| G4 | every spec drives UI via page | 92/93 call `page.goto` | — | MERGE→**D3** | — |
| G5 | no `.only`, `page.pause`, console.log | 0 `.only`; 8 `console.log` (smoke-78 latency log, deliberate) | — | MERGE→**A6** (`.only`) | Playwright's `forbidOnly` covers `.only` in config — not set (Decided edge) |
| H1 | `smoke-NN-feature` naming | — | — | = SA-1 | — |
| H2 | behaviour titles | — | — | MERGE→**D1** (GT1) | — |
| H3 | coverage matrix | — | — | = K-15 → **D3** | — |
| H4 | Ollama specs out of core (16,19,20,24) | **contradicts K-13**: smoke-16 is `@llm+@core` by design | — | DROP | stale; K-13 / D4 decides |

### 1d · CA patterns (CA:61-227)

| id | flags | HARD/REVIEW | true on master? | PW / refs | decision | why |
|---|---|---|---|---|---|---|
| banner | `//─`, `─═{3,}` | HARD | **all 93 flagged under C locale** (em-dash byte overlap); 0 under UTF-8 | — | DROP from CA | a comment-style rule, not a false-green; locale-fragile. Belongs to the general comment rule (review) |
| injectToken | `injectToken(` | HARD | helper deleted | — | DROP | the compiler catches it |
| wrong import | test/expect from `@playwright/test` | HARD | 0 hits | test-fixtures | KEEP→**B1** | cheap; losing fixtures is silent |
| .sidebar | `locator(.sidebar` | HARD | 0 | locators | KEEP→**A2** | — |
| waitForTimeout | literal | HARD | 0 | class-page | KEEP→**C1**; **add `networkidle`** | — |
| passCount | lone `passCount`/`failCount` | HARD | 0 | TM3 | KEEP→**A4** | — |
| A1 skip | `test.skip(!` not a capability | HARD | 0 | annotations | KEEP→**A6** | — |
| dead-route | goto admin/tools·users·settings, /sessions | HARD | routes absent (`app.routes.ts`; `**`→dashboard :211) | — | KEEP→**A2** | — |
| tautology | `\|\| true)`, `expect(true).toBe(true)` | HARD | 0 | — | KEEP→**A3** | — |
| .or(body) | `.or(locator('body'` | HARD | 0 | — | KEEP→**A2** | — |
| R11 | status set spans 2xx + 4xx/5xx | HARD | 0 | — | KEEP→**A3** | — |
| R12 | `Array.isArray(x ?? [])`, also over 2 lines | HARD | 0 | — | KEEP→**A3** | — |
| R13 | every expect inside `if` | HARD | 0 | V3 junk #1 | KEEP→**A3** | — |
| R14 | test body with no expect (smoke-00 exempt) | HARD | 0 | V3 junk #1 | KEEP→**A1** | — |
| R15 | `pollForToolFrame` without `toolFrameSucceeded` | HARD | 0 in specs; **SK Good example violates it** | — | KEEP→**A4** | — |
| domain tag | exactly one domain tag | HARD | 93/93 | annotations | KEEP→**D4** | — |
| serial | `describe.serial` | REVIEW | 5 | test-parallel | KEEP (signal)→**B2** | — |
| .or( | any `.or(` | REVIEW | — | — | KEEP (signal)→**A2** | — |
| setTimeout | raw `setTimeout(` | REVIEW | 2 | — | KEEP (signal)→**C1** | — |
| describe let | indented `let` | REVIEW | 70 | — | KEEP (signal)→**B1** | — |
| catch→false | `.catch(() => false)` | REVIEW | 1 | — | KEEP (signal)→**A3** | — |
| `--hook` mode | PostToolUse blocking | — | **not registered** (`settings.json:65-80`) | — | DROP the mode, or register it as advisory (§3) | — |
| `--strict` | exit 1 on HARD | — | used by `smoke:lint` | — | KEEP | — |
| test.sh | 44 positive/negative cases | — | passes 44/44; run by nothing; header claims `smoke:lint -- --self-test` (**no such flag** in `lint-smoke-specs.sh`) | — | KEEP; wire into `make test-scripts`; add an em-dash negative case | — |

### 1e · `rules/smoke.md` MUSTs

| id | says | true? | decision | why |
|---|---|---|---|---|
| SM-1 | standard lives only in smoke-spec skill | will move | REWRITE (path → `testing/references/smoke-specs.md`) | — |
| SM-2 | mechanical subset runs "in CI" via smoke:lint | **FALSE** — no CI (#440), no make target | REWRITE→"`make lint`" once wired | — |
| SM-3 | judgement rules = smoke-spec-reviewer | agent deleted (G3) | REWRITE | — |
| SM-4 | model-reaching test declares mode; user confirms | true | KEEP (pointer to D2) | — |
| SM-5 | `make smoke` core (~19) · FULL=1 all (76+) | 19 `@core` files true; 93 specs; counts rot | REWRITE without counts | CLAUDE.md "no counts that rot" |
| SM-6 | "`-only` variants skip deploy" | **no such target**; it is `DEPLOY=0` (Makefile:404-408) | REWRITE | — |
| SM-7 | DoD: spec per feature: happy, 409/404, 401/403, ≥1 UI | — | MERGE→**D3** | — |
| SM-8 | completion = CLAUDE.md §Done means | anchor exists (`CLAUDE.md:462`) | KEEP | — |
| SM-9 | HTML report 0 failed via smoke-open; never file://; never `--reporter=list` | true (Makefile:412-416) | KEEP→**C6** | — |
| SM-10 | no regressions in previously passing specs | — | DROP | restates "0 failed" |

### 1f · `smoke-spec-reviewer` agent instructions

G3 decided one reviewer, which reads references by path. Every row therefore lands in the Review checks of `smoke-specs.md`, or nowhere.

| id | says | true? | decision | why |
|---|---|---|---|---|
| R-1 | judgement layer above scanner | the scanner runs nowhere, so there is no layer below | REWRITE as a Review-check preamble | — |
| R-2 | report only, never edit/run suite/deploy | — | MERGE→the ONE reviewer's contract | generic to all review |
| R-3 | re-read SK every review | — | DROP | the ONE reviewer loads by path |
| R-4 | MET/UNMET/N/A only | — | MERGE→reviewer contract (G3) | generic |
| R-5 | use REF/FIRES/CHECK/MET/EDGE | — | REWRITE: Review checks carry *fires / check / edge*; REF = rule id | G5 shape |
| R-6 | X-99 for unconsidered criterion | — | MERGE→reviewer contract | generic |
| R-7 | touched spec gets full treatment | — | KEEP as one Review-check line | prevents line-fix reviews |
| R-8 | read smoke.md + cite every file by path | — | MERGE→reviewer contract | generic |
| R-9 | compare against real sibling (57/66/60/46) | stale name 57 | REWRITE→Good/Bad section cites real `file:line` | GB1 |
| R-10 | find touched specs via merge-base diff | true | MERGE→review packet (G3 path glob) | — |
| R-11 | run scanner `--strict` first | — | KEEP→Review check 0 | — |
| R-12 | walk K-00…K-17 | — | REWRITE→walk A1…D5 | — |
| R-13 | out of scope: scanner items, backend, pass/fail, config, fix | — | KEEP (Decided edge in Review checks) | — |
| R-14 | output ①②③ + tally | — | MERGE→reviewer contract | G3 single format |
| model | `model: opus` | — | DROP with the agent | — |

## 2 · Where R18's E1–E11 land

| E | R18 rule (short) | fits | note |
|---|---|---|---|
| E1 | role > label/text > testid; no CSS/XPath except feature tag | **merges into A2** with K-06 | one landmark-and-locator rule |
| E2 | web-first matchers, never `expect(await loc.x())` | **new C2** (from RB A1/A3) | 2 Bad sites: smoke-33:100,108 |
| E3 | no `.first()/.nth()` to dodge strictness | **new C3**, new code only | 109 existing hits; no sweep |
| E4 | never wait on time incl. `networkidle` | **merges into C1** with K-07 | 145 `networkidle` hits — the biggest finding |
| E5 | raise timeout only for named slow dependency | **new C5** (from RB D4) | 29 `setTimeout`, all live-model |
| E6 | no floating promises; lint `playwright/` | **C4**, needs an eslint config change | `eslint.config.js:38` covers `src/**` only |
| E7 | auth once via setup project + `storageState` | **open question, not a rule yet** | `loginViaForm` comment claims localStorage alone fails the route guard (`page-helpers.ts:27-29`). PW auth docs say storageState covers localStorage. Needs a spike before it becomes a rule |
| E8 | shared setup+teardown becomes a fixture | **merges into B1** | — |
| E9 | non-obvious assertion carries a message | **merges into A1** as a clause | smoke-65:210 Good |
| E10 | pass on retry = flake; read check-flaky; never retry/serial/timeout it green | **new C6** | `check-flaky.mjs:1-13`; Google Micco 2016 |
| E11 | never touch systems we don't control | **merges into B4** with RB C5 + TM2 | `@external` is the one sanctioned exception |

## 3 · Target shape — `testing/references/smoke-specs.md`

**Name: keep `smoke-specs.md`, do not rename to e2e.** The tier is called smoke everywhere it is run: `make smoke`, `smoke-NN-*.spec.ts`, `rules/smoke.md`. A third name would make the operator translate between them. The property and unit Playwright tiers (`playwright/property`, `playwright/unit`) get one When-X line each. They are pure-function tests of the support helpers, not journeys.

```
smoke-specs.md
├─ Rules             A1–A6 · B1–B4 · C1–C6 · D1–D5   (§5, after approval)
├─ When X, use Y     · checking what the platform does with a reply → @model:scripted + scriptedAgent
│                    · checking what the shipped model can do → @model:real + @llm (workers 1)
│                    · a test names a tool → pollForToolFrame + toolFrameSucceeded
│                    · the gate is the subject → toolFrameSucceeded || isApprovalPause
│                    · need a user/workspace/provider → fixture (adminToken, nonAdminUser, workspace…)
│                    · need the seeded workspace → defaultWorkspaceId, never data[0]
│                    · a pure helper (history.ts) → playwright/unit or /property, not a smoke spec
│                    · run during dev → make smoke · gate → make smoke FULL=1 · report → make smoke-open
├─ Good / Bad        real file:line ≤15 lines (GB1):
│                    Good smoke-55:16-21 landmark · smoke-65:208-213 tool frame · smoke-92 scripted oracle
│                    · smoke-69:268-271 fixme with issue · fixtures.ts:76-94 workspace fixture
│                    Bad smoke-33:100 expect(await getAttribute) · smoke-65:357 networkidle
│                    · smoke-65:63 data[0] workspace · smoke-51:29-30 apiLogin in beforeAll
├─ Decided edges     trace retain-on-failure (not on-first-retry) · retries 1 full / 0 core / 0 property
│                    · fullyParallel false until shared-state specs gone · chromium only
│                    · @llm+@core whitelist lives in core.config:22-28 · @llm alone = real until #609
│                    · license caps via workspace-lock semaphores, not worker fixtures
│                    · smoke-78 load sections: observation + a >0 floor
└─ Review checks     0 run scanner --strict · then each rule's check, false-green first (A1–A6)
```

**What happens to the reviewer and the scanner:**

| item | now | proposed |
|---|---|---|
| `smoke-spec-reviewer` agent | separate opus subagent, rubric = SK | **DELETE** (G3, `14-disposition-table.md:44`). The ONE reviewer gets `smoke-specs.md` by path whenever the diff touches `aruvii-ui/playwright/e2e/smoke/**` or `playwright/support/**` |
| CA + test.sh | under the skill, wired to nothing | **MOVE** to `testing/scripts/` (L4). **Wire it into `make lint`** (`npm run smoke:lint`; currently 93/93 clean under UTF-8, deterministic, under 5 s). Wire `check-antipatterns.test.sh` into `make test-scripts`. **Fix the locale** (`export LC_ALL=C.UTF-8` in the script, or drop the banner rule). Drop `--hook`, or register it as an advisory PostToolUse hook. Recommendation: `make lint` only — one gate, no second path |
| RB | orphan scored doc | MERGE the 4 useful rows (A1/A3 → C2, A2 → C4, B4 → C3, D4 → C5), then **DELETE** |
| `rules/smoke.md` | path rule | KEEP. Fix SM-2, SM-3, SM-5, SM-6; it points to `smoke-specs.md` |

## 4 · False or stale claims found on master

| # | claim | where | fact |
|---|---|---|---|
| F1 | scanner "run on every edit by a PostToolUse hook … hard-blocks" | SK:20-28, :214-219; reviewer:16-17, :80; CA:8-11 | `settings.json:65-80` PostToolUse runs only 3 Java hooks; `:28-29` merely allow-lists CA |
| F2 | mechanical subset runs "in CI" / "wired into the angular GitHub Actions job" | SK:28; smoke.md:10-11; `lint-smoke-specs.sh:2,7` | CI deleted in #440; no `make` target calls `smoke:lint` (Makefile `lint` = eslint + `typecheck:pw`) |
| F3 | self-test runs "via `npm run smoke:lint -- --self-test`" | `check-antipatterns.test.sh:13` | `lint-smoke-specs.sh` ignores its arguments; nothing runs the test |
| F4 | banner rule is "unambiguous" | CA:13, :62 | under `LC_CTYPE=C` (this agent's shell) it flags **93/93** specs via em-dash bytes; the UTF-8 run is clean |
| F5 | K-09 Good example | SK:117-122 | lacks `toolFrameSucceeded`, so CA R15 HARD-fails it; `api-helpers.ts:163-179` says both assertions, always |
| F6 | "add its glob to `CORE_SPECS`" | SK:400-402; RB:73, :104 | no list; `grep: /@core/` (`core.config:17-20,32`) |
| F7 | RB H4 "keep Ollama specs (16,19,20,24) out of core" | RB:104 | smoke-16 is `@llm+@core` by design (`core.config:22-28`) |
| F8 | A5 `injectToken` shim at `api-helpers.ts:146-149` | SK:46-51 | deleted (`page-helpers.ts:11-12`); `api-helpers.ts:146` is now `pollForToolFrame` docs |
| F9 | reference spec `smoke-57-agent-lifecycle` | SK:11, :190; reviewer:44 | file is `smoke-57-agent-error-paths.spec.ts` |
| F10 | dev loop `cd aruvii-ui && npx …`; gate `npm run smoke` | SK:195-197 | CLAUDE.md: `make` is the front door; `npm run smoke*` does not deploy |
| F11 | "`-only` variants skip the deploy" | smoke.md:20-21 | no such targets; `DEPLOY=0` (Makefile:404-408) |
| F12 | K-16 REF "root CLAUDE.md §Tool-Authoring DoD" | SK:340 | no such heading on master; the rule is the "adding a new tool type" block |
| F13 | smoke-69 T2 `test.fixme` "until #618 … AC-10 removes this" | smoke-69:268-271 | #618 (RAG tool: model sends only a query) is **closed**; the fixme remains |
| F14 | workspace by `data[0]` | smoke-16:34, 32:39/197, 34:119, 41:40, 56:41/242, 65:63, 69:62, 78:89 | `api-helpers.ts:84-91`: `data[0]` is the *newest* workspace — the #309 flake; `defaultWorkspaceId` exists |
| F15 | smoke-65 header says `pollHistory` waits up to 900 s | smoke-65:15-16 | the test passes `POLL_BUDGET_MS = 240_000` (:186) |
| F16 | counts "~19 core", "76+" | smoke.md:17-18 | 19 `@core` files, 93 specs — a count that rots |
| F17 | duplicate stable id NN | SK:9 "NN is a stable id" | `smoke-90-collection-scoping` and `smoke-90-model-roles` share 90 |

## 5 · GROUPS for the operator — nothing approved

Format: id · rule (≤25 words) · source · **recommendation**.

### Group A — the test must be able to fail (false-green). 6 rules

1. A1 · Every test has an assertion that fails if the feature is removed; a polled condition is not an assertion; a non-obvious expect carries a message. · K-00, R14, E9; PW best-practices · **ADOPT**
2. A2 · Assert a landmark only the feature renders, located by role, then label/text, testid last; no chrome, CSS class, XPath or dead route. · K-06, E1, CA .sidebar/.or(body)/dead-route; PW locators · **ADOPT**
3. A3 · Nothing may turn a failure green: no catch around act-and-assert, no `\|\| true`, no `?? []` before a check, no expect only inside `if`, no 2xx+4xx status set. · K-04, CA R11–R13, tautology · **ADOPT**
4. A4 · A test naming a tool asserts `pollForToolFrame` by name and `toolFrameSucceeded` (or `isApprovalPause` when the gate is the subject); an assistant reply alone never suffices. · K-08, K-09, R15, B2; TM3 · **ADOPT**
5. A5 · A test making a dependency fail on purpose asserts the failure shape: a reply still arrives and no successful frame for it exists. · K-10, smoke-65 N08 · **ADOPT**
6. A6 · Skip only on a named capability with a reason; own failed setup throws; quarantine only via `test.fixme` naming an open issue, removed when it closes. · A1/SA-7, G5; PW annotations; Google flaky-tests quarantine · **ADOPT**

### Group B — isolation and what we fake. 4 rules

1. B1 · Get users, workspaces, providers and scripted agents from `support/fixtures.ts`, imported with `test`/`expect`; setup used by two specs becomes a fixture; seeded workspace via `defaultWorkspaceId`. · K-01, K-11, E8, CA import; PW test-fixtures · **ADOPT**
2. B2 · Every test passes run alone; `describe.serial` only for one expensive shared live call, with the reason written above it. · K-02, K-05; PW test-parallel "serial is not recommended" · **ADOPT**
3. B3 · `beforeAll` only for read-only setup that throws on failure and is never mutated by tests. · K-03; PW test-retries (beforeAll reruns per worker) · **ADOPT**
4. B4 · Touch nothing we do not control: model via fake-llm or bundled Ollama, real internet only in `@external` tests with a reachability skip. · E11, RB C5, TM2; PW best-practices; SWE@Google ch14 · **ADOPT**

### Group C — waiting, timing and flakes. 6 rules

1. C1 · Never wait on time: no `waitForTimeout`, sleeps or `networkidle`; wait on a web-first assertion, response, URL, or `expect.poll` with a budget. · K-07, E4; PW class-page "networkidle DISCOURAGED"; SWE@Google ch14 · **ADOPT** (new code; 145 existing `networkidle` swept separately)
2. C2 · Check page state with retrying matchers (`toHaveText`, `toHaveAttribute`, `toBeVisible`); never `expect(await locator.x())`. · E2, RB A1/A3; PW test-assertions · **ADOPT**
3. C3 · No `.first()`/`.nth()`/`.last()` to escape a strictness error; narrow by role name, `filter` or chaining. · E3, RB B4; PW locators · **ADOPT for new code only**
4. C4 · Every Playwright call and `expect` is awaited, enforced by `@typescript-eslint/no-floating-promises` over `playwright/`. · E6, RB A2; PW best-practices#lint-your-tests · **ADOPT** (needs an eslint config change)
5. C5 · Raise a timeout only for a named slow dependency (live model) with a one-line reason; a poll budget stays below the test timeout. · E5, RB D4/D5; PW test-timeouts · **ADOPT**
6. C6 · A pass on retry is a flake: read check-flaky output and fix the cause; never add retries, serial or timeouts to make it green. · E10; PW test-retries; Google Micco 2016 · **ADOPT**

### Group D — tiers, model mode and evidence. 5 rules (+1 open)

1. D1 · Test title = scenario title; each Given/When/Then is one `test.step` with the scenario's words; tests carry the issue annotation. · K-12 → GT1, GT2, GT4 (approved) · **ADOPT** (confirms already-approved GT rules for this file)
2. D2 · Every model-reaching test tags `@model:scripted` (assert `fakeLlm.requests` + history, never scripted text) or `@model:real` + `@llm`; author proposes, user confirms. · K-17, SA-17/21; openclaw docker-e2e:13-27 · **ADOPT**
3. D3 · A feature's spec drives its route in the UI at least once and asserts every status the change introduces, including its refusal path. · K-15, SM-7, RB G4/H3; GA5 · **ADOPT** (drops the named-screenshot mandate, K-14)
4. D4 · Exactly one domain tag per spec; `@llm` with `@core` only for the whitelist in `playwright.core.config.ts`, which runs one worker. · K-13, CA domain tag; PW annotations#tag-tests · **ADOPT**
5. D5 · Run with `make smoke` while developing and `make smoke FULL=1` as the gate; `@core` goes on a spec only after a 0-failed full run. · SA-24/30, SM-5/9, RB E4; superpowers stale-server note · **ADOPT**
6. (open) E7 · Authenticate once per role via a setup project and `storageState`; log in through the form only in login tests. · PW auth · **HOLD** — spike first, because `page-helpers.ts:27-29` claims storage injection fails our route guard

### Cut list (for one yes/no) — DROP

K-14 named screenshot · SA-5/CA `injectToken` · CA banner rule (moved to the general comment rule) · SA-14 description 20–500 (the API enforces it) · SA-23 context7 · RB scoring, A5, B5, D3, E2, E3, F2, F4, H4 · SM-10 · the reviewer agent and its opus model · CA `--hook` mode. **Recommendation: DROP all.**

### Wiring decisions (one yes/no each)

1. Wire `npm run smoke:lint` into `make lint`, and `check-antipatterns.test.sh` into `make test-scripts`. **Recommend yes** — the scanner currently gates nothing.
2. Fix CA's locale fragility (`LC_ALL=C.UTF-8`) and add an em-dash negative case to its test. **Recommend yes.**
3. Add `forbidOnly: true` to both smoke configs. **Recommend yes** — it replaces RB G5 at zero cost (PW `testConfig.forbidOnly`).
4. File follow-ups for F13 (smoke-69 T2 fixme after #618), F14 (10 `data[0]` sites) and the 145 `networkidle` hits. **Recommend yes, as separate issues.**

## Receipts

Read in full on `origin/master`:
- `.claude/skills/smoke-spec/SKILL.md`
- `scripts/check-antipatterns.sh` and `.test.sh`
- `.claude/agents/smoke-spec-reviewer.md` · `.claude/rules/smoke.md` · `docs/guides/playwright-rubric.md`
- `aruvii-ui/playwright.{smoke,core,property,unit}.config.ts` · `aruvii-ui/package.json` scripts
- `playwright/support/{fixtures,page-helpers,api-helpers,history,check-flaky.mjs,workspace-lock,lint-smoke-specs.sh}`
- heads of `generate-gallery.mjs`, `generate-stability-report.mjs`, `check-flaky.spec.mjs`, `property.ts`, `cleanup-test-data.ts` · `global-setup.ts:1-120`
- specs `smoke-55` (core), `smoke-65` (`@llm` + core), `smoke-78` (long, serial section)
- `Makefile` smoke/lint/test targets · `.claude/settings.json` hooks · `app.routes.ts` routes

Run against a `git archive` of master:
- `lint-smoke-specs.sh`: C locale → 93 fail; UTF-8 → 93 clean
- `check-antipatterns.test.sh`: 44/44
- grep counts as cited

Prior work built on: R18 `22-playwright-frontend-testing.md`, R13 `15-testing-content-audit.md`, `19-approved-rules.md`, `14-disposition-table.md:36-44`.
