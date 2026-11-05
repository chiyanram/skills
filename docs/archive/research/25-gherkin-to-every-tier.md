# R21 · Analyst Gherkin → unit / IT / e2e that read the same (no Cucumber runtime)

Ticket: `issues/36-research-gherkin-to-every-tier.md` · informs G9a · 2026-10-02.
Given: S1, AT1, U2, V4 (19-approved-rules.md). Nothing below is approved.
Source key: *all_in_one* = spockframework.org/spock/docs/2.4/all_in_one.html · *extensions* = …/2.4/extensions.html · *class-test* = playwright.dev/docs/api/class-test.

## 0. What master does today (verified, `origin/master`)

| fact | evidence |
|---|---|
| Scenarios live **in the REQ**, in a fenced ```` ```gherkin ```` block, titled, no IDs | `docs/spec/REQ-500-login-throttle-progressive-delay.md:294-537` |
| Other REQs use numbered prose ACs (`AC-1 Given … When … Then`) + "Shared setup" | `REQ-075-certification-execution-gate.md:690-705` |
| REQ-500 scenarios carry **tier-ish tags** `@domain` / `@api` | `REQ-500:296,353` — contradicts `acceptance-criteria-writing` ("not the analyst's … to pre-tag") |
| Spock **names drift** from the scenario | `REQ-500:311` "…then grows, then stops at the cap" vs `LoginBackoffPolicySpec.groovy:25` "…then doubles to the cap"; column `backoff` → `expected` (:30) |
| ITs name **decisions**, not scenarios | `LoginThrottleServiceIT.groovy:56` "D4 — …"; `LoginThrottleIT.java:131` `@DisplayName` "the real owner gets back in…" for `REQ-500:354` "An attacker cannot keep a real user out" |
| Traceability = Javadoc/comment only | `LoginBackoffPolicySpec.groovy:9` "REQ-500 §Acceptance criteria"; 0 groovy files use `@Issue/@See/@Title/@Narrative` |
| Smoke: 0 `test.step`; G/W/T comments in 5 of 93 specs | `aruvii-ui/playwright/e2e/smoke/` |
| Jest names are method-shaped | `agent.service.spec.ts:49` `it('list() calls GET /api/agents…')`; 810 `it(` |
| Spock 2.4-groovy-5.0 | `gradle/libs.versions.toml:57` |

## 1. Storage and ownership

| option | pros (source) | cons (source) |
|---|---|---|
| **A · fenced `gherkin` block in the REQ** (today, REQ-500) | one document reviewed at stage 3–5 with the design; Gherkin is "specification, documentation, and executable tests" — first two survive without a runtime (cucumber.io/docs/gherkin/reference); no runtime temptation (`acceptance-criteria-writing` §Constraints) | no parser → syntax/Outline-header mismatch unchecked; no stable id; tags drift into tier hints (REQ-500:296) |
| B · `.feature` files, no runtime (plinth 133 model) | IDE/lint support; plinth parses it as the input contract (`133:57-60`, `scenario_{name}` methods `133:121`) | second source of truth beside the REQ; recreates the removed `acceptance/`/`features/` shape (`gherkin-to-test` intro); plinth filters by `@acceptance` tag and happy path only (`133:46-47`) — AT1 already rejected that |
| C · numbered prose ACs (REQ-075) | stable ids (`AC-1`), table rows | not Gherkin keywords; Outline/Examples not expressible as such |

Why "without automation" is legitimate: Adzic's 2020 survey — **29%** of teams use examples as acceptance criteria
without automating them; quality "great" 13% vs 26% automated (gojko.net/2020/03/17/sbe-10-years.html). Cucumber:
formulation alone gives "feedback from the whole team about our shared vision" (cucumber.io/docs/bdd). SbE pattern
"Automating validation **without changing specifications**" (Adzic, *SbE* ch.9, Manning TOC) = tests adapt to the
scenario, never the reverse.

Who writes (same survey): collaborative 47%, PO/BA 26%, developers 6%.

| who | owns | does not |
|---|---|---|
| Analyst | scenario text, Outline tables, shared setup, scenario id | tier choice, tags meaning tier |
| Developer | tier per scenario (S1), test names = scenario title, `where:`/`test.each` rows | rewording the scenario in the test |
| Reviewer (G3 Spec verdict) | scenario ↔ test table, "not done" bucket | judging wording |

## 2. Mapping table

| Gherkin | Spock (unit/IT) | Playwright (smoke) | Jest (Angular unit) |
|---|---|---|---|
| `Feature:` / REQ title | `@Title("REQ-500 — …")` ("natural-language name to a spec", spockframework.org/spock/docs/2.4/extensions.html §Title and Narrative) | `test.describe('[SMOKE-NN] …')` | `describe('REQ-500 …')` |
| feature description / "As a…" | `@Narrative("""…""")` | `describe` details `annotation` | — |
| `Rule:` | — (one spec per rule, or comment) | nested `test.describe` | nested `describe` |
| `Background:` / Shared setup | `setup()` / fields; `given:` text "shared setup" | `beforeEach` / fixture | `beforeEach` |
| `Scenario:` title | feature method name = title, verbatim (String literal names, all_in_one §Feature methods) | `test('<title>', …)` | `it('<title>')` |
| `Given` / `When` / `Then` | `given: "…"` `when: "…"` `then: "…"` (block descriptions, all_in_one §Specifications as Documentation) | `await test.step('Given …', …)` (class-test §test.step; shown in report + trace) | `// Given` comments (no step API) |
| `And` / `But` | `and: "…"` (does not change semantics) | another `test.step` | comment |
| `Scenario Outline` + `Examples` | `where:` table, `||` inputs‖outputs; name placeholders `#failures`, unrolled by default in 2.x (all_in_one §Data Driven Testing) | `for (const row of rows) test(\`… ${row.x}\`)` — titles must be unique (playwright.dev/docs/test-parameterize) | `test.each\`…\`('… $failures …')` (jestjs.io/docs/api §.each) |
| Gherkin `@tag` | `@Tag` (JUnit Platform tags) | `{ tag: ['@auth'] }` — must start with `@`, `--grep` (test-annotations §Tag tests) | — |
| Issue link | `@Issue("#500")` + `issueUrlPrefix` config (extensions §Issue) | `annotation: {type:'issue', description:'#500'}` (HTML report shows it) | — |
| Spec link | `@See("…/REQ-500-….md")` (extensions §See) | `annotation: {type:'scenario', …}` | — |
| Not yet implemented | `@PendingFeature` (fails if it passes) | `test.fixme` | `test.todo` |

spock-reports 2.6.1-groovy-5.0 renders per-spec HTML incl. block text (github.com/renatoathaydes/spock-reports); `@Issue/@See` rendering **not confirmed**.

## 3. Worked example — `REQ-500:311` (Outline) and `REQ-500:354` (@api)

Source (`REQ-500:311-329`, abridged):

```gherkin
Scenario Outline: The backoff is zero below the threshold, then grows, then stops at the cap
  Given <failures> consecutive failed attempts against one account
  When the next attempt is made
  Then the account backoff is <backoff> seconds
  Examples: | failures | backoff |  0|0  9|0  10|1 … 15|30  400|30
```

S1 says: pure logic → **unit only** (already exists, `LoginBackoffPolicySpec.groovy:25-41`). Re-rendered to mirror:

```groovy
@Issue("#500") @See("docs/spec/REQ-500-login-throttle-progressive-delay.md")
def "The backoff is zero below the threshold, then grows, then stops at the cap — #failures failures → #backoff s"() {
    given: "#failures consecutive failed attempts against one account"
    def policy = new LoginBackoffPolicy(unspread())
    when: "the next attempt is made"
    def decision = policy.decide(failures, 0)
    then: "the account backoff is #backoff seconds"
    secondsOf(decision) == backoff
    where:
    failures || backoff
    0        || 0
    9        || 0
    10       || 1
    15       || 30
    400      || 30
}
```

`REQ-500:354` — HTTP+Redis → IT (exists, renamed, `LoginThrottleIT.java:131`). Mirrored IT, and smoke only if a UI journey is in scope:

```groovy
@Issue("#500")
def "An attacker cannot keep a real user out"() {
    given: "an attacker has failed against the account enough times to reach the account cap"
    seedFailuresAt(settings.accountThreshold()); seedLastFailureAt(Duration.ofMinutes(1))
    when: "the real owner submits correct credentials after the cap has elapsed"
    def response = attemptLogin(PASSWORD)
    then: "the login succeeds"
    response.expectStatus().isOk()
}
```

```ts
test('An attacker cannot keep a real user out',
  { tag: ['@auth'], annotation: { type: 'issue', description: '#500' } }, async ({ page }) => {
  await test.step('Given an attacker has reached the account cap and the cap has elapsed', async () => { /* seed via API */ });
  await test.step('When the real owner submits correct credentials', async () => { /* fill + click */ });
  await test.step('Then the login succeeds', async () => { await expect(page).toHaveURL(/dashboard/); });
});
```

Jest would take the Outline as `it.each` with the same columns (§2 row); S1 does not pick it here — no UI logic owns the curve.

Per V4 the IT and smoke are **not** both warranted for `:354`; the developer picks one owning boundary.

## 4. Traceability and review

| link | today | candidate |
|---|---|---|
| scenario id | title only (REQ-500); `AC-n` (REQ-075) | `REQ-500 · <title>` or `AC-n`; analyst assigns |
| scenario → test | Javadoc / D-numbers / paraphrase | test name = scenario title verbatim; `@Issue("#NNN")` / Playwright `issue` annotation |
| test → scenario | grep `REQ-500` (107 test files mention a REQ) | grep the title string |
| review | G3 Spec verdict cites each AC file:line, 4 buckets (`issues/07-grill-review-shape.md` §Resolution) | one row per scenario `id · tier · file:line`; no row → "not done"; test without scenario → "additions" |
| mechanical aid | none (no CI, #440) | verbatim titles allow a `grep -F` of unmatched scenarios; ungated |

## 5. Candidate rules (put ONE BY ONE; none approved)

**→ `planning/references/acceptance-criteria.md`**

| id | rule (≤25 words) | source |
|---|---|---|
| GA1 | Scenarios live in the REQ's `## Acceptance criteria` as one fenced `gherkin` block; no `.feature` files, no runtime. | REQ-500:294; AT1; acceptance-criteria-writing §Constraints; cucumber.io/docs/gherkin/reference |
| GA2 | Every scenario has a stable id the analyst assigns (`AC-n`), unchanged once the REQ is approved; renumbering is a spec change. | REQ-075:700; gap in REQ-500 |
| GA3 | Scenario tags describe the domain (`@security`), never the tier (`@domain`, `@api`, `@ui`); tier is the developer's call. | acceptance-criteria-writing §What this skill does not cover; plinth 058:36; REQ-500:296 (Bad) |
| GA4 | Each Outline's Examples header names exactly its `<placeholders>`; shared preconditions go once, as Background or "Shared setup". | plinth 058:149; cucumber reference §Scenario Outline; REQ-075:692 (Good) |
| GA5 | Every scenario has one checkable Then; at least one scenario per AC names the failure or refusal path. | acceptance-criteria-writing rule 1; R13 (15-testing-content-audit.md:34) |

**→ `testing/workflows/scenario-to-tests.md`**

| id | rule (≤25 words) | source |
|---|---|---|
| GT1 | The test name is the scenario title verbatim (Outline adds `— #placeholders`); rewording a scenario in a test is a finding. | Spock all_in_one §Feature methods; SbE ch.9 "without changing specifications"; LoginBackoffPolicySpec:25 (Bad drift) |
| GT2 | Spock block descriptions repeat the scenario's Given/When/Then/And text; Playwright uses one `test.step` per step with the same text. | Spock §Specifications as Documentation; Playwright class-test §test.step; U2 |
| GT3 | An Outline becomes `where:` (Spock) or `test.each` (Jest) with the Examples column names unchanged; e2e takes one representative row. | Spock §Data Driven Testing; jestjs.io §.each; gherkin-to-test §Scope; V4 |
| GT4 | Each scenario's test carries `@Issue("#NNN")` (Spock) or an `issue` annotation (Playwright) naming its work item. | Spock extensions §Issue; Playwright test-annotations §Annotate tests; 0 uses on master |
| GT5 | Pick one owning tier per scenario by S1; a second tier only when it adds a risk the first cannot see. | S1, V4, IT1; gherkin-to-test Step 1 |
| GT6 | The MR description lists every scenario id → tier → test file:line; the Spec verdict marks an unlisted scenario "not done". | G3 §Resolution (Spec 4 buckets); C4 |

## 6. Open questions

| # | question | why it matters |
|---|---|---|
| Q1 | Id scheme: `AC-n` (REQ-075) or title-as-id (REQ-500)? Retrofit REQ-500? | GA2/GT6 need one |
| Q2 | Does GT1 apply to existing tests (LoginThrottleIT shouldXxx, D-named ITs) or new only? | U2 already exempts old JUnit |
| Q3 | Adopt spock-reports as living doc, or is the REQ the only doc? | adds a plugin; `@Issue` rendering unverified |
| Q4 | Analyst = a human role or the `/crq` stage-3 agent? Who answers grill questions about scenarios? | ownership table assumes a role |
| Q5 | Should a tiny script list scenario titles with no matching test name (advisory, like other hooks)? | review is the only check today (no CI) |
| Q6 | Jest: rename method-shaped `it('list() calls GET…')` or apply GT1 only to scenario-driven UI logic? | 810 existing `it(` |

## Sources

URLs cited inline (spockframework.org 2.4, github.com/renatoathaydes/spock-reports, playwright.dev, jestjs.io, cucumber.io, gojko.net + Manning *SbE* ch.1 sample) · plinth `refs/plinth-pinned/058`, `133` · ours: both skills + master files cited inline.
