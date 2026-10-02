# R17 · Mutation (PIT) and property-based testing — research

Ticket: `../issues/32-research-mutation-and-property.md` · read on `origin/master` · 2026-10-02.
Nothing here is approved. Every candidate rule goes to the operator one at a time.

## 1 · Our current state

| thing | where (origin/master) | fact |
|---|---|---|
| PIT versions | `gradle/libs.versions.toml:60-62` | plugin 1.19.0 (latest per plugin site) · pitest 1.30.0 · junit5 bridge 1.2.3 |
| PIT conventions | `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts` | `mutationThreshold=0` (report, never gate, #456) · `failWhenNoMutations=true` · targets `ai.aruvii.guardrails.*` hard-coded · excludes `*Config`, `*Properties` · `avoidCallsTo` re-lists 4 logging pkgs + `org.springframework.http.client` · threads = cores/2 (≥1) · HTML+XML · **no `mutators` set → PIT DEFAULTS** · **no history/incremental** |
| modules applying it | `aruvii-guardrails/build.gradle.kts:3` | **one** module |
| make target | `Makefile:236-246` `make mutation` | `gradlew :aruvii-guardrails:pitest`; absent from `verify`, `verify-fast`, `verify-full`, `check` |
| last measured score | #505 commit `2bf77d1d` | 184 mutants · 156 killed · 18 survived · 10 no-coverage · **85%** (was 78%) |
| wall-clock cost | — | **never recorded** anywhere on master |
| JVM property harness | `aruvii-guardrails/src/test/java/.../property/{Property,Gen}.java` | home-grown; 1000 cases; seed random per run, replay via `-Daruvii.property.seed`; coordinate-wise shrink, 100 steps max; arity 1–3 |
| JVM property users | `ToolOutputSanitizerPropertyTest.java` | **only one** (plus the harness's own `PropertyTest`); runs inside `make test` (#440) |
| UI property harness | `aruvii-ui/playwright/support/property.ts` (#359) | home-grown, fast-check-shaped; default `runs=200`, **default seed fixed `0x5eed`**; retries 0 |
| UI property tier | `make test-property` → `playwright.property.config.ts` | one spec: `history.property.spec.ts`; in `verify` and `verify-fast` |
| fast-check / jqwik dep | `aruvii-ui/package.json`, catalog | **neither** present |
| guidance today | `.claude/skills/gherkin-to-test/SKILL.md:52-72`; `.claude/rules/dependencies.md` §6 | gherkin-to-test names `PiiRedactorTest` as a runner user — **false** (it does not call `Property`); says "run it on any module" — but only guardrails is wired |

## 2 · When to use which

| technique | answers | use when | source |
|---|---|---|---|
| example test | "does this case give this result?" | the default; every RIGHT-BICEP / CORRECT case (C1, B1–B3) | 19-approved-rules C1, B1 |
| property test | "does this law hold for every input?" | a rule stated over a range: invariant, round-trip, idempotence, security collapse; pure functions | fast-check *why-property-based* ("identify edge cases… not considered"); ECC kotlin-testing:788 ("pure functions"); agentlayer yjs-fs README:73 (convergence) |
| mutation test | "would a test notice if the code were wrong?" | after tests exist, to audit the suite — not to design cases | pitest.org: coverage "does **not** check that your tests are actually able to **detect faults**" |

Relationship to the approved rules:

| approved | complements |
|---|---|
| B3 just-inside/just-outside | PIT DEFAULTS includes *Conditionals Boundary* (`<`→`<=`) — a surviving one is a missing B3 case |
| B1 Cardinality (0,1,many) | #505: one entity left `offset` at 0, so `start+offset`≡`start-offset`; 7 survivors died only with a second entity |
| B1 Range | jqwik injects min/max/0/1 edge cases by default (MIXIN); our harness does **not** |

## 3 · jqwik vs `Property.java` — facts only

| | jqwik 1.10.1 | `Property.java` (ours) |
|---|---|---|
| engine | own JUnit Platform engine; `@Property` is not usable inside a Spock spec | plain static call; works from JUnit **or** Spock |
| tries | 1000 default | 1000 fixed |
| edge cases | MIXIN default (min, max, 0, 1 mixed in) | none |
| shrinking | BOUNDED default (10 s) · FULL · OFF | coordinate-wise, 100 steps; `map` loses shrink |
| replay | seed + AfterFailureMode (SAMPLE_FIRST default) | seed printed; `-Daruvii.property.seed` |
| statistics / coverage checks | `Statistics.collect` + coverage checks | none — the gap that let a conditional property pass 1000× never reaching its branch (`ToolOutputSanitizerPropertyTest` javadoc) |
| stateful | action chains / state machines | none |
| output | 1.10+ prints an anti-agent line to stdout every run; `jqwik.hideAntiAiClause` only erases it on a terminal | silent |
| author intent | release notes 1.10.1: "not meant to be used by any 'AI' coding agents at all"; 1.10.0 withdrawn | n/a |
| home | external dep | guardrails test tree; promotion deferred until a 2nd module wants it |

Fact: the repo already decided against jqwik (Property.java javadoc; gherkin-to-test:57-61). Primary sources confirm both stated reasons. No primary source contradicts keeping ours. Options are **keep** (status quo) or **keep + extend** (edge cases, a "condition reached" count); **replace with jqwik** conflicts with the author's published terms.

## 4 · Candidate rules (unapproved — put ONE BY ONE)

### `testing/references/mutation.md`

| id | rule (≤25 words) | source | rec |
|---|---|---|---|
| M1 | Mutation testing is a report, never a gate; `mutationThreshold` stays 0 until a measured score exists and the operator chooses one. | ours #456, `dependencies.md` §6; spring-skills ext :165 ("not before a real score exists; just below it") | ADOPT |
| M2 | Read a surviving mutant as a missing case: name the CORRECT/RIGHT-BICEP letter it violates, then add that example test. | ours #505 (Cardinality, 7 survivors); pitest DEFAULTS *Conditionals Boundary* ↔ B3 | ADAPT |
| M3 | Report score **and** test strength (killed ÷ (killed+survived)); NO_COVERAGE means "not reached", survived means "not asserted". | pitest.org maven `testStrengthThreshold`; spring-skills ext :502 | ADOPT |
| M4 | Exclude only code with no decision in it (wiring, config); never exclude to raise the number — `is*`/`get*` that decide stay measured. | ours #505 + conventions file; spring-skills ext :285 | ADOPT |
| M5 | After changing exclusions or `avoidCallsTo`, compare per-class mutant counts before and after; an over-matching glob looks like success. | spring-skills ext :413; ours #505 (`avoidCallsTo` replaces defaults, +14 survivors) | ADOPT |
| M6 | Keep PIT's DEFAULTS mutators; never `ALL` — non-default operators are excluded for instability and equivalent mutants. | pitest.org mutators; jvm-skills ext :355 | ADOPT |
| M7 | Run `make mutation` after adding branching logic to `aruvii-guardrails`; for another module, wire it in first and say so in the MR. | gherkin-to-test:66-71 (corrected: only one module is wired) | ADAPT |
| M8 | Treat a mutant as equivalent only with a stated reason; when unsure, record it as a gap, not as equivalent. | pitest.org basic concepts; jvm-skills ext :304 | ADOPT |
| M9 | Do not rely on `withHistory` for a verdict you will trust; PIT calls its dependency-change assumption "unproven". | pitest.org incremental analysis | ADOPT |
| M10 | A mutation-kill test written against correct code passes on first run; prove it with a hand mutation (revert after), not a Red run. | jvm-skills ext :317; tension with TDD "never skip Red" | ADAPT |

### `testing/references/property-based.md`

| id | rule (≤25 words) | source | rec |
|---|---|---|---|
| P1 | Write a property when the requirement says "for any input" — invariant, round-trip, idempotence; otherwise write examples. | fast-check *why*; gherkin-to-test:54-56 | ADOPT |
| P2 | A property never replaces the examples: keep the named CORRECT / just-inside-outside cases as examples beside it. | 19-approved B1–B3; ToolOutputSanitizerPropertyTest javadoc (examples explain, properties generalise) | ADOPT |
| P3 | The generator must reach the condition the property names; a conditional property whose generator cannot satisfy it is no test. | ours `ToolOutputSanitizerPropertyTest:57-60` | ADOPT |
| P4 | Seed is random per run and printed on failure; replay with the printed seed; never retry a failing property. | `Property.java` seed(); `playwright.property.config.ts` retries 0; fast-check seed docs | ADAPT (UI default seed is fixed) |
| P5 | Use `Property.forAll` (JVM) or `support/property.ts` (UI); do not add jqwik — its 1.10+ engine writes an anti-agent line to every log. | Property.java javadoc; jqwik release notes 1.10.1, user guide | ADOPT |
| P6 | Generators must include the B1 Range edges (min, max, 0, 1, empty); random draws alone rarely hit them. | jqwik user guide EdgeCasesMode MIXIN; B1/B3 | ADAPT (harness has no edge-case injection) |
| P7 | A JVM property is a unit test: it runs in `make test`, counts in coverage, and is never tagged out of the gate. | ours #440, `Makefile:280-285` | ADOPT |

## 5 · Open questions

| # | question | why it matters |
|---|---|---|
| Q1 | How long does `make mutation` take? | No number on master; M7 and any wider rollout need it |
| Q2 | Make `targetClasses` a parameter so a 2nd module can apply the convention? | Hard-coded `ai.aruvii.guardrails.*` — applying it elsewhere mutates nothing (`failWhenNoMutations` would fail) |
| Q3 | Add test strength (M3) to the `make mutation` echo? | today only the HTML report shows it |
| Q4 | Extend `Gen` with edge-case injection and a "branch reached" counter (P3, P6)? | the two gaps vs jqwik that have already bitten |
| Q5 | UI harness defaults seed to fixed `0x5eed`; JVM is random per run. Align? | a fixed seed is "a thousand fixed examples" per Property.java's own reasoning |
| Q6 | Fix gherkin-to-test:61 (`PiiRedactorTest` is not a runner user) and :70 ("any module") | stale guidance an agent will follow |
| Q7 | Promote `Property`/`Gen` to a shared test home now? | the worker windower property is unwritten for lack of it (ToolOutputSanitizerPropertyTest javadoc) |
| Q8 | M10 vs TDD "never skip Red" — which wins for kill tests? | needs operator call |

## Sources

Primary: [pitest mutators](https://pitest.org/quickstart/mutators/) · [basic concepts](https://pitest.org/quickstart/basic_concepts/) · [incremental analysis](https://pitest.org/quickstart/incremental_analysis/) · [maven params](https://pitest.org/quickstart/maven/) · [pitest.org](https://pitest.org/) · [gradle-pitest-plugin](https://gradle-pitest-plugin.solidsoft.info/) · [jqwik user guide 1.10.1](https://jqwik.net/docs/current/user-guide.html) · [jqwik release notes](https://jqwik.net/release-notes.html) · [fast-check why PBT](https://fast-check.dev/docs/introduction/why-property-based/).
Corpus: `extractions/spring-skills-mutation-testing-with-pit-on-gradle.md` · `extractions/jvm-skills-testing-coverage-and-mutation-skills.md` · `refs/addyosmani-agent-skills/skills/constraint-driven-development/SKILL.md:160,200,242` (Stryker; "≥60% to start") · `r9/affaan-m_everything-claude-code/skills/kotlin-testing/SKILL.md:788` · `refs/humanlayer-agentlayer/packages/yjs-fs/README.md:73`. superpowers / openclaw / plinth-pinned: no mutation or property guidance found. plinth `112-…-profile-pitest.xml` sets `mutationThreshold` from a user-chosen level (Maven).
