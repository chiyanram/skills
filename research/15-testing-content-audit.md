# R13 · Testing content audit — is what we have correct, consistent, complete?

Ticket: `../issues/27-research-testing-content-audit.md` · feeds G9a (`../issues/23`) · shape per G5 (`../issues/13`).
Checked against **`origin/master` @ `309982e1`** (2026-10-01), not this worktree (`e0cc30e8`, behind; it differs
from master in `rules/smoke.md` and `smoke-spec/SKILL.md` only — the master versions were audited).
Every "evidence" cell is `git -C ROOT show origin/master:<path>` or `git grep … origin/master` unless it says otherwise.

## Summary (6 lines)

1. **No file is SOUND.** 3 REWRITE (`coverage-design`, `testing`, `it-testing`), 9 NEEDS FIXES, `tdd` copy → plugin, 0 sound.
2. **`coverage-design.md` teaches a wrong mnemonic:** RIGHT-BICEP is 6 dimensions (Right · B · I · C · E · P — plinth 130), ours invents 9 (R/I/G/H/T/…) and swaps E↔P.
3. **Build-system rot:** `it-testing` §Build & run, `test-quality` §2 and `smoke-spec` still describe Maven/failsafe/`pom.xml`/CI; the Gradle `maxParallelForks=1`, coverage-ON and "no CI" facts contradict them in the same files.
4. **Spock is the rule but the content is JUnit:** `testing.md`, `test-quality.md`, `boundaries-correct.md`, `it-testing` show only `@Test`/Mockito/AssertJ; `it-testing` never names `@EnableAruviiSpec` (12 specs) or the 3 Groovy IT bases (27 specs).
5. **False enforcement claims:** smoke-spec's "PostToolUse hook hard-blocks every edit" — no such hook in `.claude/settings.json`; `injectToken` rule polices a helper that no longer exists.
6. **Missing entirely:** tier choice review check, unit-level mocking rule (Mock vs Stub vs Fake), "assert behaviour not defaults / no change detectors", run-existing-tests-first, boundaries trigger, Prove-It for bugs.

---

## Verdicts

| file | verdict | top 3 fixes |
|---|---|---|
| `AS/test-value-bar.md` | NEEDS FIXES | 1. re-pin junk example: `PricingDomainTest` is deleted (#539) → `AlertTriggerTypeSpec:8-13` + `RefusalReasonSpec:44-51` · 2. add openclaw candidate-evidence list (oc `:111-122`) for the audit workflow · 3. add Review checks (4 questions + junk list as MET/UNMET) |
| `AS/coverage-design.md` | **REWRITE** | 1. correct RIGHT-BICEP to 6 dimensions · 2. add Right-results "independent expected value" + "record missing cases as explicit gaps" (plinth) · 3. pin `RunModeSpec:49-60` (Bad) / `RotationReminderBoundarySpec:42-71` (Good) |
| `AS/boundaries-correct.md` | NEEDS FIXES | 1. swap invented classes (`AccessToken`, `Team`, `DisplayName`…) for real Spock specs · 2. fix line refs + `CLAUDE.md §Database` · 3. Review checks that name concrete probes per letter (P1 F7) |
| `AS/testing.md` | **REWRITE** | 1. Spock-first (where:, power asserts, Mock/Stub, closure-assert) · 2. delete §8 `@WebMvcTest`/`MockMvcTester` (0 uses, contradicts "never MockMvc") · 3. fix PRESERVE count + `CLAUDE.md §4` refs; merge with test-quality per G9a Q1 |
| `AS/test-quality.md` | NEEDS FIXES | 1. delete "JaCoCo off by default (`pom.xml`)" and Maven `BUILD SUCCESS` text · 2. PRESERVE list 8 → 9 (`model_role_binding`) · 3. fix "§4/§Database/§Test Results" CLAUDE.md citations |
| `SK/aruvii-standards/SKILL.md` (ladder) | NEEDS FIXES | 1. add step "tier choice" (between 0 and 1) · 2. correct `SKILL.md:83` "every citation points at code you can open" (≥13 invented classes) · 3. `CLAUDE.md §4/§Angular…/§Observability` no longer exist |
| `SK/it-testing/SKILL.md` | **REWRITE** | 1. delete §Build & run (failsafe, `forkCount=0.25C`, `pom.xml`) · 2. add Spock archetypes (`@EnableAruviiSpec`, `@DataJpaTest` bases) · 3. drop dead "39 unmigrated / rollout order" history; update @Scheduled table, quarantine, `@MockitoBean` reality |
| `rules/it-testing.md` | NEEDS FIXES | 1. `:12` say `/java` **or `/groovy`** · 2. move rules 2–3 (AC→file, count queries) out — process, not Spock · 3. settle naming (sentence vs `shouldXxx`) once, here |
| `rules/smoke.md` | NEEDS FIXES | 1. `:10-11` "in CI" — no CI (#440) · 2. "smoke-spec-reviewer" (G9a deletes it) · 3. "`-only` variants" — no such target; it is `DEPLOY=0` |
| `SK/smoke-spec/SKILL.md` | NEEDS FIXES | 1. delete "PostToolUse hook hard-blocks" + "GitHub Actions `angular` job" (both false) · 2. drop A5 `injectToken` (helper removed) · 3. authoring step 4 `cd … npx` / "`npm run smoke` is the DoD gate" → `make smoke FULL=1` |
| `SK/gherkin-to-test/SKILL.md` | NEEDS FIXES | 1. `:81` "happy path by default, don't invent negatives" contradicts CLAUDE.md:221 · 2. unit row "mock a collaborator" → port Fake/Stub rule · 3. `@ParameterizedTest/@CsvSource` → Spock `where:`; note `Property` is test-scoped to guardrails |
| `SK/acceptance-criteria-writing/SKILL.md` | NEEDS FIXES | 1. add "assert behaviour, not a default" (FS:6) · 2. every AC names its failure/refusal path · 3. pin REQ-500:312 (outline) as Good |
| `SK/tdd/*` (repo copy) | delete → plugin (as decided) | 1. carry 2 deltas to testing/SKILL.md · 2. resolve "Refactoring is not part of the loop" vs CLAUDE.md:85 "Red → Green → Refactor" · 3. resolve plugin `tests.md:47-53` "DB query = BAD" vs our IT DB-row asserts |

---

## Per file

### 1 · `test-value-bar.md` (110 lines) — NEEDS FIXES

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| `PricingDomainTest.costConfidenceCoversTheFourKnownLevels` is junk | :109 | class no longer exists; `aruvii-shared/.../pricing/PricingDomainSpec.groovy:8-22` records its **deletion** under this bar (#539) | STALE pin (good precedent, dead target) |
| `ErrorCodeTest.everyCodeIsKebabCased` keep | :110 | `aruvii-shared/src/test/java/.../error/ErrorCodeTest.java:16-21` | OK |
| "`gradle.properties`' eleven COVEREDRATIO floors" | :10-11 | `gradle.properties:14-24` = 11 `aruvii.coverage.*` keys; `COVEREDRATIO` lives in `build-logic/.../aruvii.jacoco-conventions.gradle.kts:27` | OK (rot-prone count) |
| "#166 62.9% … 255 classes at zero" | :10 | not in repo; GitLab only | unverifiable; count that rots (CLAUDE.md "no counts that rot") |
| `#170` D1–D5 "already decided" | :25, :59 | no D1–D5 anywhere in `docs/` or `.claude/` | decision not in repo — reader cannot open it |
| `audit-28` "0 of 87 … 81" | :73-74 | `docs/research/audit-*` exist; counts rot | rot-prone |

**(b) Contradictions** — `:3-6` ladder order matches `SKILL.md:27-38` ✓. None internal. But `:96` "do not `@Ignore`" vs `it-testing` §Quarantine "zero disabled" while 2 `@Disabled` ITs exist (`WebhookControllerIT.java:136`, `AllToolTypesIT.java:727`).

**(c) Completeness gaps**

| gap | source |
|---|---|
| candidate-evidence fields before deleting (name, what it detects, non-test callers, stronger owner proof, history, unlock, risk) | oc `test-audit/SKILL.md:111-122` [drift 2026-10-17: test-audit cut to 57 lines at d8faf8876, detail moved to `references/audit.md`, see research/64d] — needed for G9a `workflows/audit.md` |
| "read the full test + owner + callers + siblings before judging" | oc `:75-79` |
| junk: "self-comparisons and identity copiers", "provider-local replays of shared helpers" | oc `:48`, `:53` |
| **no change detectors** — a test only an intentional decision can fail (constant value, name list) | sp `writing-good-tests.md:41-45`, gate `:65-79` |
| "your code, not the framework"; constructors/getters/constants earn tests only when they validate/normalise/default/derive | sp `:54-63` — exactly the `pricingOverrideRecordPreservesAllFields` / RunModeSpec class |
| mental mutation check before finishing | sp `:157-169` |

**(d) G5 distance** — has Rules (4 questions) + junk list + retention bar + a Good/Bad pair. Missing: When-X-use-Y, Decided edges (the pair is half of one), Review checks. **Close — reshape, don't rewrite.**

| pin | file:line (origin/master) | why |
|---|---|---|
| Bad · cannot fail | `aruvii-platform/src/test/groovy/ai/aruvii/platform/domain/AlertTriggerTypeSpec.groovy:8-13` | `valueOf(x) != null` — `valueOf` throws, never returns null (P1 Std 7) |
| Bad · change detector | `aruvii-worker/src/test/groovy/ai/aruvii/worker/chat/RefusalReasonSpec.groovy:44-51` | enum `name()` set vs hand-copied list — same shape as deleted `PricingDomainTest` |
| Good · wire contract | `RefusalReasonSpec.groovy:19-26, 74-90` | literal legacy exit-status strings, compared both ways; fails on a rename an operator would feel |
| Good · deletion record | `aruvii-shared/src/test/groovy/ai/aruvii/shared/pricing/PricingDomainSpec.groovy:8-28` | says what was removed and why, and what was kept despite looking similar |

### 2 · `coverage-design.md` (59 lines) — REWRITE

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| "Nine questions" R·I·G·H·T·B·I·C·E·P | :3, :17-52 | plinth 130 RIGHT-BICEP = **Right · Boundary · Inverse · Cross-check · Error · Performance** (corpus extraction `plinth-java-testing-strategies…md:158-300`, directive at `:158`) — "RIGHT" is the word *right*, not five letters | **FALSE** — invented letters G/H/T, "I = boundary", E = performance, P = parallel |
| "C — Conform to a specification" | :35 | C = Cross-check in source | FALSE |
| `docs/spec/REQ-500-…` uses it informally | :8 | file exists | OK |

Net: the real dimensions all appear somewhere (Right :19, Boundary :22, Inverse :25, Cross-check :29, Error :32, Performance :46), plus an extra "Parallel" (:50) which is useful but not RIGHT-BICEP.

**(b) Contradictions** — `:39-41` "B as CORRECT" and `:22` "I — boundary" duplicate each other inside the file. `:55` says RIGHT-BICEP before CORRECT; matches ladder.

**(c) Completeness gaps** (all plinth 130 via corpus `…extraction.md`)

| gap | corpus line |
|---|---|
| Right result proved by an **independently understandable expected value** | `:192` |
| just-inside AND just-outside values; **name the business-critical boundary**; **record missing boundary cases as explicit gaps** | `:219-236` — the P1 F7 miss |
| inverse test runs both directions with representative + edge values | `:240-254` |
| cross-check oracle independent of implementation; never reimplement the algorithm | `:261-275` |
| force the error directly; verify the public error contract | `:282-292` |
| performance as stable guardrail, not micro-benchmark | `:185-188` |
| output a **gap matrix** per dimension for a review | `:143` |

**(d) G5 distance** — no Rules (all questions), no Good/Bad, no edges, no Review checks. Far.

| pin | file:line | why |
|---|---|---|
| Bad · tautological "coverage" | `aruvii-agents/src/test/groovy/ai/aruvii/agents/domain/RunModeSpec.groovy:49-60` | iterates `Reason.values()`, asserts record accessor returns its input (P1 F5 "exhaustive test proves nothing") |
| Good · Right + Boundary + Error | `aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:42-71` | at / one-second-past / one-day-inside threshold on a `Clock.fixed` |
| Good · Error forced | `RunModeSpec.groovy:17-26` | `where: version << [0, -1]` → `thrown(IllegalArgumentException)` |

### 3 · `boundaries-correct.md` (223 lines) — NEEDS FIXES

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| `UserErasureLogAdapter:37` cap 100 | :105 | clamp is at `:43` | STALE line |
| `InteractionAdapter:90` cap 200 | :106 | clamp at `:119` | STALE line |
| `AuditLogAdapter:42` cap 500 | :107 | `:42` | OK |
| `ErasureEmailHasher` isBlank | :157-160 | `ErasureEmailHasher.java:37-40` | OK |
| `DataErasureController` takes `Clock`; `retentionPreview` cutoff | :217-218 | `DataErasureController.java:51,125` | OK |
| V25 TIMESTAMP→TIMESTAMPTZ | :221-222 | `V25__session_model_swaps_tz.sql:1-8` | OK |
| "`CLAUDE.md` §Database" TIMESTAMPTZ | :220 | no such section; no TIMESTAMPTZ in CLAUDE.md | **FALSE cite** |
| `type-design.md` §1 `@Email` | :61 | `type-design.md:37,65` | OK |
| `InvalidSlugException`, `DisplayName`, `InvalidDisplayNameException`, `AccessToken`, `Team`, `DuplicateMemberException` | :57, 148-151, 176-197 | 0 files each | invented — contradicts `SKILL.md:83` |
| every example is JUnit `@Test`/`@ParameterizedTest`/Mockito `when()` | throughout | rules/it-testing.md:62 "every new test is Spock" | outdated idiom |

**(b) Contradictions** — `:132` "never `@MockitoBean`… full rules: it-testing" while `:124` uses Mockito `when()` in a unit test — fine, but it is the only place unit-level mocking is shown, and nothing says Mockito is allowed at unit level. `:16` "Never `Thread.sleep`" vs `UiModelSwapE2EIT.java:604` (live violation, unmentioned).

**(c) Completeness** — plinth CORRECT (`…extraction.md:558-806`) adds per-letter "validation signals"; ours has examples but no signal list. Missing the trigger: *when* to load (any new branch on a value, collection, time, or external ref) — the P1 F7 lesson is "consider boundaries" fails; probes must be named.

**(d) G5 distance** — strong Rules + examples; no Review checks, invented samples. Medium.

| pin | file:line | why |
|---|---|---|
| Good · Time/Range | `RotationReminderBoundarySpec.groovy:42-52` | exclusive cutoff proved at the instant and 1 s past |
| Good · Existence | `RotationReminderBoundarySpec.groovy:81-90` | null `created_at`, gap recorded "not endorsed" |
| Bad · sleep | `aruvii-api/src/integrationTest/java/ai/aruvii/api/modelswap/UiModelSwapE2EIT.java:604` | `Thread.sleep(250)` poll |
| Good · Range clamp source | `aruvii-infra/.../UserErasureLogAdapter.java:43`, `InteractionAdapter.java:119`, `AuditLogAdapter.java:42` | per-adapter caps |

### 4 · `testing.md` (252 lines) — REWRITE

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| "`CLAUDE.md` §4" holds the rules | :3 | CLAUDE.md has no numbered sections; rules are `<important if="writing or reviewing Java">` CLAUDE.md:185-198 | FALSE cite |
| PRESERVE "the eight" | :88 | `aruvii-test-support/.../AruviiTestReset.java:45-59` lists **9** (+`model_role_binding`) | STALE count |
| `DatabaseResetExtension` truncates / restores | :87 | mechanism moved to `AruviiTestReset`; extension is a 3-line Jupiter adapter (`DatabaseResetExtension.java:26-31`) | partly stale |
| `ToolTrustStoreWiringIT:77` reflection | :170 | `ToolTrustStoreWiringIT.java:77-78` | OK |
| `JwtServiceTest:146` fixture reflection | :188 | now at `:207` | STALE line |
| `comments.md` §7 | :200 | `comments.md:137` | OK |
| §8 harness: `MockitoExtension` / **`@WebMvcTest`** / **`@JsonTest`** / `MockMvcTester` | :203-234 | `@WebMvcTest` 0 code files, `@JsonTest` 0, `MockMvcTester` 0; CLAUDE.md:233 "RestTestClient, never MockMvc" | recommends forbidden/unused harness |
| `PricingService`/`DiscountRepository` example | :218-229 | 0 files | invented |

**(b) Contradictions**

| this file | other side |
|---|---|
| all examples JUnit + Mockito (:37-252) | `rules/it-testing.md:62` "every new test is a Spock specification"; `aruvii.test-conventions.gradle.kts:7` |
| §8 `@WebMvcTest` + `MockMvcTester` | CLAUDE.md:233, `it-testing/SKILL.md:12` "No MockMvc" |
| `shouldXxx` (:58) | `rules/it-testing.md:54` "feature names read as sentences"; live specs use three styles: sentences `RefusalReasonSpec:28`, `"should report …"` `RotationReminderBoundarySpec:42`, camel `"shouldRegister…#group"` `ConsumerIdentityIT.groovy:48` |
| `java-standards.md:15` routes GWT/shouldXxx to `test-quality.md` | `standards-review` Q-05 routes the same rule to `testing.md` §1 (R7:56 drift, still present) |

**(c) Completeness gaps**

| gap | source |
|---|---|
| Spock mechanics: `Mock()` vs `Stub()` (62 specs use `Mock()`, 2 use `Stub()`; `RotationReminderBoundarySpec:31-33` Mocks used only to stub) | spock idiom; repo count via `git grep -l "= Mock()"` |
| test state not interactions; interaction only when the call **is** the contract | addy `test-driven-development/SKILL.md:190-209`; sp `writing-good-tests.md:114-117` |
| test-double preference real > fake > stub > mock | addy `:234-246` |
| mock earns no assertions; mirror real data completely | sp `:83-97`, `:119-122` |
| DAMP over DRY in tests | addy `:211-232` |
| assert the exception **type/message** (domain error) | plinth 131 corpus `:1056-1062` (we have it only in boundaries §1) |
| no conditionals / loops computing the expected value | plinth 131 corpus `:1013`; sp warning signs `:191` |

**(d) G5 distance** — Good/Bad pairs exist but in the wrong language and partly invented; §8 must go. Far; merge with test-quality into `unit-tests.md` (G9a Q1).

| pin | file:line | why |
|---|---|---|
| Good · Spock where: table, literal oracle | `RefusalReasonSpec.groovy:53-66` | |
| Good · mock-closure with `assert … true` | `aruvii-agents/src/test/groovy/ai/aruvii/agents/application/AgentEvalServiceSpec.groovy:221-226` | rules/it-testing rule 1 done right |
| Bad · reflection seam | `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/ToolTrustStoreWiringIT.java:55-56,77-78` | |
| Good · JSONB parsed, `singleElement()` | (keep current §1/§3/§4 snippets — they are from `ErasureLookupControllerIT`; re-pin by file:line) | |

### 5 · `test-quality.md` (253 lines) — NEEDS FIXES

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| "80 % JaCoCo gate is **off by default** (`pom.xml`, `jacoco.skip.check`)" | :107-108 | Gradle; coverage ON (#390), per-module floors `gradle.properties:14-24`; CLAUDE.md "Coverage enforcement is ON" | **FALSE** |
| filter matching nothing reports `BUILD SUCCESS`, read `Tests run:` | :73-74 | `verification.md:36` "This specific trap is now closed. A `TEST=` pattern matching nothing fails the build" | **FALSE (Maven-era)** |
| "Runs from a standard command, in CI and locally" | :40 | no CI (#440) | stale |
| "`CLAUDE.md` DoD §Test Results", "§4" ×3, "§Database" | :68, 101, 231, 141 | none exist | FALSE cites |
| PRESERVE = eight tables (listed) | :180-182 | 9 — `model_role_binding` missing (`AruviiTestReset.java:55`) | STALE |
| snapshot once per JVM fork | :182 | `AruviiTestReset.java:113` "run once per JVM (fork)" | OK |
| "scope creep rule 3 forbids" | :16 | no "rule 3" anywhere it points to | dangling |
| examples `InMemoryUserRepository`, `RegistrationService`, `Cart`, `TrialPeriod`, `PasswordPolicy`, `ShippingMethod` | :43-228 | 0 files each | invented |

**(b) Contradictions** — `:20-21` "A quarantined test that still runs is better than a green one that proves nothing" vs `it-testing/SKILL.md:336-337` "zero ITs disabled; don't add `@Disabled`" — and 2 exist. `:100-101` "`assertThrows` is banned — `CLAUDE.md` §4" correct in substance (CLAUDE.md:190), wrong cite.

**(c) Completeness** — A-TRIP letters match plinth (`…extraction.md:360-557`). Missing: plinth's "validation signals" per letter; "Professional" lacks "no logic in tests" (plinth `:1013`). Flakiness has no pointer to the `check-flaky.mjs` smoke postscript (`aruvii-ui/package.json:19-20`).

**(d) G5 distance** — Rules + Good/Bad present (invented); no edges, no Review checks. Merge target per G9a Q1.

| pin | file:line | why |
|---|---|---|
| Good · Independent on shared container | `aruvii-test-support/.../AruviiTestReset.java:45-59` + the `PRESERVE` comment for `model_role_binding` | "captures empty so AC-14 cannot pass by accident" |
| Good · Repeatable time | `RotationReminderBoundarySpec.groovy:16-24` | javadoc explains why `Instant.now()` twice made it unassertable (#512) |
| Bad · Repeatable | `UiModelSwapE2EIT.java:604` | sleep-poll |

### 6 · `aruvii-standards/SKILL.md` ladder (:27-38) — NEEDS FIXES

| issue | line | evidence |
|---|---|---|
| no tier-choice step — "unit, IT or smoke?" is decided nowhere in the ladder | :27-38 | tier choice lives only in `gherkin-to-test:13-28`, which "never fired" (R2:61) |
| "`CLAUDE.md` §4 / §Angular Icon & Select Standard / §Observability" | :8, :69 | none exist (CLAUDE.md uses `<important if>` blocks at :185, :246, :294) |
| "Every citation in these references points at code you can open" | :83-84 | ≥13 invented classes across `boundaries-correct`, `test-quality`, `testing` (table rows above) |
| step 3 "Write it → testing.md" | :37 | points Spock authors at a JUnit-only file |
| no step for "run the existing tests that touch what you change" | — | FS:6 `RefusalReasonSpec` not run (`00-fleet-self-reports.md:5`) |

G5 distance: router, not a reference. Becomes `testing/SKILL.md` (ladder 0–4 + tier choice) per G9a Q1.

### 7 · `it-testing/SKILL.md` (354 lines) — REWRITE

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| consumed "at `<scope>test</scope>` by api/tools/worker" | :9-10 | Gradle; wired by `build-logic/.../aruvii.integration-test-conventions.gradle.kts` for every IT module | STALE |
| `@EnableAruviiIT` = initializer + import + `{DatabaseResetExtension, RedisReachabilityCheck}` | :53 | `EnableAruviiIT.java`: `@ExtendWith({DatabaseResetExtension, ResettableExtension, RedisReachabilityCheck})` | incomplete (misses `ResettableExtension`) |
| `DatabaseResetExtension` snapshots/truncates; `DatabaseResetExtension.PRESERVE`; `DatabaseResetExtension.flushRedis` | :55, :59, :207 | logic + `PRESERVE` + `flushRedis` live in `AruviiTestReset.java:45,171` | STALE names |
| "The 39 unmigrated classes" / archetype 3 / rollout order | :58-59, :100-127, :219-233 | `SharedRedis.registerProperties` used by **1** IT (`SetupControllerIT`); `RedisFlushExtension` by 1 | **STALE** — migration done; history, not standard |
| archetype 4 "tools handler ITs — pattern being finalized" | :129-133 | — | undated TBD |
| archetype 5 SSE "deferred", `ChatStreamingIT` | :135-138 | `aruvii-api/src/integrationTest/java/.../chat/ChatStreamingIT.java` exists | TBD never closed |
| `SsoFlowIT` "no `@Container` at all", Keycloak as `@Bean` | :156-158 | `SsoFlowIT.java:54,75` — `@Container` only in a comment | OK |
| §Build & run: **maven-failsafe**, verify phase, **`forkCount=0.25C` (`pom.xml`)**, `reuseForks` | :193-200 | Gradle `maxParallelForks = 1` (`aruvii.integration-test-conventions.gradle.kts:30`); the file's own :37 says so | **FALSE + self-contradiction** |
| @Scheduled table lists 5 jobs | :307-313 | worker has 12 `@Scheduled`: missing `TaskTimeoutJob` (60 s, **immediate**), `EvalSweepJob`, `LeaseSweepJob`, `PendingReclaimJob`, `StrandedResumeSweepJob` (30 s), `TurnLeaseRegistry` renewal, `LitellmPricingRefreshJob` | incomplete — the rule "seed outside every job's predicate" now needs 7 more predicates |
| Quarantine: "zero ITs are disabled" | :336 | `WebhookControllerIT.java:136`, `AllToolTypesIT.java:727` `@Disabled` | **FALSE** |
| "No `@MockitoBean`" non-negotiable | :12, :175 | **14** IT files still use it (e.g. `DryRunIT`, `AgentEvalControllerIT`, `AgentTriggerControllerIT`) | rule true, reality not acknowledged — no "existing debt" edge |
| `@TestBean` for `@Primary` prod beans | :185 | `AuditLogControllerIT`, `ExplanationControllerIT`, `FakePortsConfig.java:14` | OK |

**(b) Contradictions**

| this file | other side |
|---|---|
| description "`*IT.java`", all examples JUnit | `rules/it-testing.md:62` Spock for every new test; 38 Groovy ITs exist |
| no `@EnableAruviiSpec` anywhere | `rules/it-testing.md:68-70,94-97`; `testsupport/spock/EnableAruviiSpec.java` |
| no `@DataJpaTest` archetype | `InfraRepositoryIT.groovy` (10 subclasses), `AgentsRepositoryIT.groovy` (12), `ChatIT.groovy` (5) — `@DataJpaTest` + rollback, **no** `DatabaseResetExtension` |
| :37 `maxParallelForks = 1` | :194 `forkCount=0.25C` |
| checklist :350 "`shouldXxx` names" | `rules/it-testing.md:54` sentences |

**(c) Completeness gaps**

| gap | source |
|---|---|
| register WireMock stubs per test, not in base/`@BeforeAll` (insertion-order matching) | plinth 132 corpus `:1418` |
| never Mockito a typed HTTP client in an IT — WireMock so the real pipeline runs | plinth 132 `:1454` (we say it in the doubles table :174, keep) |
| assert from the **server/system of record**, not from re-reading the code | in-repo precedent `ConsumerIdentityIT.groovy:19-30` |
| IT owns what a unit can't reach (transport, lifecycle, SQL) — link to value-bar Q3 | oc `:23-27` |

**(d) G5 distance** — huge file, half history. Rules + doubles table + checklist (→ Review checks) are reusable.

| pin | file:line | why |
|---|---|---|
| Good · Spock IT, truth from Redis server | `aruvii-worker/src/integrationTest/groovy/ai/aruvii/worker/stream/ConsumerIdentityIT.groovy:31-67` | `@EnableAruviiSpec`, declared `ApplicationContext`, `XINFO` as oracle |
| Good · @Scheduled via registered task | `aruvii-worker/src/integrationTest/java/ai/aruvii/worker/scheduling/DataRetentionJobIT.java:44-56` | |
| Good · slice base | `aruvii-infra/src/integrationTest/groovy/ai/aruvii/infra/repository/InfraRepositoryIT.groovy` (class javadoc + `@DataJpaTest @AutoConfigureTestDatabase(replace = NONE)`) | `replace = NONE` is load-bearing |
| Bad · `@MockitoBean` in IT | `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/DryRunIT.java` | |

### 8 · `rules/it-testing.md` (105 lines) — NEEDS FIXES

| issue | line | evidence |
|---|---|---|
| "`src/integrationTest/java`" only | :12 | CLAUDE.md:223 and standards-review Q-03 say `/java` **or `/groovy`**; 38 Groovy ITs |
| rule 2 (every AC gets a file) and rule 3 (count `@Query`s) are not Spock rules and not IT rules | :42-49 | they belong to `/crq` stage 8 / review; glob means they load on any `*Spec.groovy` read |
| rule 5 "feature names read as sentences" | :54-55 | CLAUDE.md:191 `shouldXxx`; `java-standards.md:15` `shouldXxx` (glob `**/*.java` — never loads for Groovy, so Groovy gets only this line) |
| "power assertions replace AssertJ … AssertJ-only governs Java" | :99-101 | consistent with standards-review Q-04; **not** reflected in `testing.md`/`test-quality.md`, which say "AssertJ only" unqualified |
| "The pattern — `@EnableAruviiIT`, … `DatabaseResetExtension` — is the it-testing skill" | :103-105 | it-testing has no Spock pattern (see §7) |
| glob omits `**/*Test.groovy`, `**/src/test/**` | :2-5 | G9a Q1 decides `rules/testing.md` glob = all test paths |

G5: it is a L2 rule file; G9a Q1 splits MUSTs → `rules/testing.md`, Spock know-how → `references/spock.md`. Pins for spock.md: Good closure `AgentEvalServiceSpec.groovy:221-226`; Good described blocks `RotationReminderBoundarySpec.groovy:43-51`; Bad bare-label search target (none found by grep — find one during write-up).

### 9 · `rules/smoke.md` (28 lines, master) — NEEDS FIXES

| claim | line | evidence | status |
|---|---|---|---|
| mechanical subset "runs over the whole suite **in CI** via `npm run smoke:lint`" | :10-11 | `smoke:lint` exists (`aruvii-ui/package.json:31`); CI deleted #440 | stale "CI" |
| judgement rules are "the `smoke-spec-reviewer` agent's" | :11 | G9a deletes that agent | will be stale |
| `make smoke` ~19 core specs | :17 | 19 files carry `@core` | OK, rot-prone count |
| "all 76+" | :18 | 92 `smoke-NN-*.spec.ts` | true but rotting count |
| "the `-only` variants skip the deploy" | :20-21 | no `-only` make target; `Makefile:401-408` uses `DEPLOY=0` | **FALSE** |
| `§Done means` anchor | :19, :28 | CLAUDE.md `### Done means` | OK |

### 10 · `smoke-spec/SKILL.md` (352 lines, master) — NEEDS FIXES

**(a) Correctness**

| claim | line | evidence | status |
|---|---|---|---|
| scanner "is run on *every* edit … by a PostToolUse hook … **hard-blocks**" | :21-26, :214-218 | `.claude/settings.json` PostToolUse = 3 `warn-*` hooks only; `check-antipatterns.sh` appears only in the allow-list (:28-29) | **FALSE** — rule 1 of the rubric ("never report what the scanner blocks; those never reach you") is therefore wrong |
| "`npm run smoke:lint` (wired into the `angular` GitHub Actions job)" | :28 | `.github/workflows` deleted #440 | **FALSE** |
| A5 `injectToken` deprecated shim at `api-helpers.ts:146-149` | :46-51 | `page-helpers.ts:11` "The `injectToken` shim … went with the split"; 0 definitions | STALE rule |
| reference specs "smoke-57-agent-lifecycle", "smoke-46 (settings + shell UI)" | :11-13, :190 | `smoke-57-agent-error-paths`, `smoke-46-notifications` | STALE names |
| fixtures dedupe names `fixtures.ts:31-51` | :57 | `workerIndex` at `fixtures.ts:59,81,97` | STALE line |
| `playwright.core.config.ts` comment `:22-28` names 4 `@llm`+`@core` specs | :137, :321 | comment at `:22-28` names smoke-16/65/69/74 | OK |
| `fullyParallel` false | :32-33 | `playwright.smoke.config.ts:31` | OK |
| smoke-51:29-45 shared read-only setup as Good | :75, :253 | `smoke-51:29-30` calls `apiLogin` in `beforeAll` | Good example breaks K-11 "fixtures, not apiLogin" |
| K-16 REF "root `CLAUDE.md` §Tool-Authoring DoD" | :340 | it is `<important if="adding a new tool type">` CLAUDE.md:406 | stale cite |

**(b) Contradictions**

| this file | other side |
|---|---|
| step 4 "`cd aruvii-ui && npx playwright test …`" | CLAUDE.md "Avoid `cd <dir> && <cmd>`"; make is the front door |
| step 4 "The DoD gate is … `npm run smoke`" | CLAUDE.md "`npm run smoke*` does not deploy"; `rules/smoke.md:17-21` `make smoke FULL=1` |
| step 5 + :31 "run the smoke-spec-reviewer agent" | G9a Q1 deletes it; FS:6 3rd reviewer subagent |

**(c) Completeness** — already the best-shaped file (author standard + K-00..K-17 rubric). addy `testing-patterns.md:197-235` adds nothing we lack. Missing: a pointer to `check-flaky.mjs` / stability report (`package.json:19-20`).

**(d) G5 distance** — closest of all: Rules ✓, Good/Bad pinned `smoke-NN:line` ✓, Review checks ✓ (K-rows carry EDGE = Decided edges). Missing only an explicit When-X-use-Y block (scripted vs real already is one). **Fix facts, keep shape.**

| pin | file:line | why |
|---|---|---|
| Good · real landmark | `aruvii-ui/playwright/e2e/smoke/smoke-06-admin.spec.ts:95-105` | role heading + named screenshot |
| Good · scripted model | `smoke-92-scripted-model.spec.ts` | `fakeLlm.requests` as oracle |
| Bad · K-11 inside a "Good" | `smoke-51-spreadsheet-tool.spec.ts:29-30` | `apiLogin` in `beforeAll` |

### 11 · `gherkin-to-test/SKILL.md` (95 lines) — NEEDS FIXES

| issue | line | evidence |
|---|---|---|
| "Happy path by default … don't invent negative cases the scenario didn't describe" | :81-82 | CLAUDE.md:221 "every business rule tested — happy path **and** failure/edge cases"; standards-review Q-01; boundaries ladder step 2 |
| unit tier "mock a collaborator if needed" | :36 | no rule anywhere on how (Mock/Stub/Fake) at unit level |
| "becomes a `@ParameterizedTest`/`@CsvSource`" | :82-83 | Spock `where:` (`rules/it-testing.md:99`) |
| IT "Then → assert the response and/or a real DB row" | :37 | plugin `tdd/tests.md:47-53` calls DB-side verification BAD — undecided edge |
| `Property.forAll` "this repo's runner" | :55-57 | `aruvii-guardrails/src/test/java/.../property/Property.java` — **test** source of one module; other modules cannot use it without a test-fixtures dependency (unsaid) |
| `make mutation` → `:aruvii-guardrails:pitest`, report not gate | :66-68 | `Makefile:242-246`; `aruvii.mutation-conventions.gradle.kts` | OK |
| worked examples `ToolOutputSanitizerPropertyTest`, `PiiRedactorTest` | :61-62 | both exist | OK |
| engine removed (`acceptance/`, `features/`) | :9-10 | dirs absent | OK |
| "Not this skill's job to check" whether tests satisfy the scenario | :87-91 | standards-review has no tier-choice check either → nobody checks (09-wiki) |

Completeness: addy pyramid + decision guide (`test-driven-development/SKILL.md:144-186`) and test sizes (`:163-173`) are the model for a When-X-use-Y block; we have the table but no "lowest tier that can prove it" principle, which value-bar Q3 states and this file should cite. G5 distance: medium (has When-X-use-Y; lacks pins, edges, checks).

| pin | file:line | why |
|---|---|---|
| Good · scenario outline | `docs/spec/REQ-500-login-throttle-progressive-delay.md:312` (`Given <failures> consecutive failed attempts`) | table → Spock `where:` |
| Good · tier: IT only because it needs the server | `ConsumerIdentityIT.groovy:22-30` | javadoc explains why a unit can't prove it |

### 12 · `acceptance-criteria-writing/SKILL.md` (97 lines) — NEEDS FIXES

All claims check out (`to-spec/SKILL.md:44,49` call it; engine removed). No aruvii samples — every example is a made-up "template".

| gap | evidence |
|---|---|
| "an AC asserts behaviour, not a default" | FS `00-fleet-self-reports.md:6` qa: "ACs asserting defaults not behaviour"; !230 |
| each AC names its failure/refusal path (pairs with CLAUDE.md:221) | — |
| AC numbering (`AC-14`, `R1`) so tests/`@DisplayName` can cite it | `REQ-027:267`, `RunModeSpec:6` "REQ-075 R1", `testing.md:39` "REQ-024 AC10" |
| Good pin | `REQ-500:298-370` (outline + shared preconditions) |

G9a: moves to `planning/references/acceptance-criteria.md` (Q3 answer) — not a testing reference.

### 13 · `tdd/*` repo copy vs mattpocock plugin 1.2.3 — delete → plugin

| file | delta vs `~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills/1.2.3/skills/engineering/tdd/` |
|---|---|
| `mocking.md` | identical |
| `tests.md` | identical |
| `SKILL.md` | punctuation (— vs :) + `/codebase-design` wording at :26; **two additions**: mutation/PIT para `:34-39`, Beck "make the change easy" `:41-52` |

Contradictions the plugin brings in (must be Decided edges in testing/SKILL.md):

| plugin | ours |
|---|---|
| `SKILL.md:38` "Refactoring is not part of the loop" | CLAUDE.md:85 "Red → Green → Refactor" |
| `tests.md:47-53` verifying via DB query = BAD | `gherkin-to-test:37`; `testing.md` §1/§3 assert `audit_log` rows; `AruviiTestReset` comment "AC-14 cannot pass by accident" |
| `tests.md:42` red flag "asserting on call counts/order"; `mocking.md:10-14` "don't mock your own classes" | `rules/it-testing.md:19-40` `1 * repo.save(...)`; 62 specs `Mock()` own ports; value-bar retention "call ordering where observable" (:90-91) |
| `SKILL.md:22` "confirm seams with the user" before any test | `/crq` stage 6 is AFK after `/approved` — seams must come from the approved design instead |

---

## Cross-file — rules MISSING entirely

| # | missing rule | why it matters (our evidence) | best source |
|---|---|---|---|
| M1 | **tier choice** as a ladder step + a Review check ("lowest tier that can prove it; a second tier needs a distinct risk") | only `gherkin-to-test:13-28` (never fires, R2:61); no standards-review Q-row | addy TDD `:144-186`; oc `:23-27` |
| M2 | **unit-level doubles**: when Mock vs Stub vs Fake vs real; port Fakes at unit level too? interaction assert only when the call is the contract | 62 specs `Mock()` vs 2 `Stub()`; plugin says "don't mock own classes"; nothing in repo says which wins | addy `:234-246`; sp `:83-127`; plugin `mocking.md:1-14` |
| M3 | **assert behaviour, not defaults / no change detectors** (constants, enum name lists, record accessors, `!= null` on things that can't be null) | `AlertTriggerTypeSpec:8-13`, `RefusalReasonSpec:39-51`, `RunModeSpec:49-60`; FS:6 | sp `writing-good-tests.md:41-63` |
| M4 | **run the existing tests that cover what you touch, before and after** | `RefusalReasonSpec` not run (FS row developer) | plinth 131 corpus `:1122-1128`; addy red flag `:375-385` |
| M5 | **boundaries trigger**: a diff adding a comparison, collection, clock or external ref MUST list its CORRECT probes in the test or as a named gap | P1 F7 missed with the file in the packet | plinth RIGHT-BICEP `:219-236` ("name the business-critical boundary; record gaps") |
| M6 | **Prove-It for bug fixes**: red reproduction first, at the owner boundary | value-bar `:35-38` says it for regressions only; not in ladder or review | addy `:96-142`; sp `SKILL.md:113-128` |
| M7 | **verify RED for the right reason** (fails, not errors; message expected) for every new test | CLAUDE.md "never skip Red" has no how | sp `SKILL.md:113-128` |
| M8 | **mental mutation check** before done (wrong constant, wrong branch, missing side effect, empty return, missing validation) | PIT only on guardrails | sp `:157-169` |
| M9 | **one naming convention for Spock features** | three styles live (see §4 table) | decide once in `rules/testing.md` |
| M10 | **test-debt edges**: 14 `@MockitoBean` ITs, 2 `@Disabled`, 54 `MockitoExtension` units, `Thread.sleep` — "touched file gets fixed; untouched is debt, don't copy" | none acknowledged | pattern exists in `java-standards.md:18-20` ("existing inline catches are tech debt") |
| M11 | **delete-a-test evidence** (for `workflows/audit.md`, ND-9) | value-bar dropped audit mode on purpose (:8-11) | oc `:111-122`, `:124-133` |
| M12 | **assert from the system of record**, not from the code's own constants | `ConsumerIdentityIT:22-30` does it; nowhere stated | sp `:27-39` (derive expectations independently) |

## Cross-file — contradictions to settle once (G9a decides)

| topic | side A | side B |
|---|---|---|
| test language | `rules/it-testing.md:62` Spock always | `testing.md`, `test-quality.md`, `boundaries-correct.md`, `it-testing` — JUnit only |
| feature names | CLAUDE.md:191, `java-standards.md:15` `shouldXxx` | `rules/it-testing.md:54` sentences |
| assertions | CLAUDE.md:190 "AssertJ only" (unqualified) | `rules/it-testing.md:99`, SR Q-04 power asserts in Groovy |
| GWT owner | `java-standards.md:15` → `test-quality.md` | SR Q-05 → `testing.md` §1 |
| coverage | CLAUDE.md:220 "80%+ line coverage" | `gradle.properties:14-24` floors 0.19–0.90; `test-quality.md:107` "off" |
| negatives | `gherkin-to-test:81` happy path by default | CLAUDE.md:221 happy **and** failure |
| harness | `testing.md` §8 `@WebMvcTest`/MockMvc | CLAUDE.md:233 never MockMvc |
| smoke gate | `smoke-spec:195-197` `npm run smoke` | CLAUDE.md, `rules/smoke.md` `make smoke FULL=1` |
| refactor | plugin `tdd/SKILL.md:38` not in loop | CLAUDE.md:85 Red→Green→Refactor |
| IT forks | `it-testing:37` 1 fork | `it-testing:194` `0.25C` |

## Sources read

Repo (origin/master): the 15 files above in full; `AruviiTestReset.java`, `EnableAruviiIT.java`, `EnableAruviiSpec.java`,
`DatabaseResetExtension.java`, `.claude/settings.json`, `gradle.properties`, `build-logic/…/aruvii.{integration-test,test,jacoco,mutation}-conventions.gradle.kts`,
`Makefile`, `aruvii-ui/package.json`, `playwright.{core,smoke}.config.ts`, `standards-review/SKILL.md:408-460`, `java-standards.md`, sample specs cited.
References: addy `skills/test-driven-development/SKILL.md`, `references/testing-patterns.md`; superpowers
`skills/test-driven-development/{SKILL,writing-good-tests}.md` (r9 scratch clone); openclaw `.agents/skills/test-audit/SKILL.md`;
mattpocock tdd 1.2.3 plugin cache; corpus `~/workspace/claude/analysis/skills-analysis/docs/extractions/plinth-java-testing-strategies-and-the-test-layer-split.md`.
Local: `../p1/lead-judgment.md`, `../p1/report-standards.md`, `00-fleet-self-reports.md`, `14-disposition-table.md` §G9a.
