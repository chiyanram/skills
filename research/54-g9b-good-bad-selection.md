# 54 — G9b Good/Bad selection (#33, map #9) — step 3a

Which approved G9b rules get a Good/Bad pair. **Selection only — no pairs written here.**
Scope: every APPROVED/DECIDED row that states an author rule in `19-approved-rules.md` §Code + observability, the round-1
table and §Spring core + Security (R33 #77, R34 #78), with amendments applied (TR4a, AP3a, AP4a, SE7a, sharpened LY6/LY7,
SC7/SC9 per OQ-SC1 d, OQ-SC4, OQ-SC5, SC1). Skipped: REJECTED, MOVED, FL*, pure decisions (OQ1, OQ3, OQ5, ND-2, ND-3,
OQ-R27-6, OQ-NG3, OQ-NG7, OQ-SC6, SE-verdict, X1–X8 "settled by" duplicates).

Test for "misreadable" (`00-reference-format.md` Good/Bad rule 5, #35): a competent developer or agent can follow the
words and still get it wrong — unclear boundary, a term with two readings, a common look-alike that is allowed or
forbidden, or an edge already decided. Gated rules (Checkstyle, ArchUnit, eslint) and rules whose sentence lists the
exact forbidden form get none.

Paths: agent-platform `origin/master` pinned at **`772736bf`** (2026-10-03) unless another commit is named; every
`path:lines` below was read at that commit. Module prefixes are dropped where the file name is unique.
"adapt" = no real code fits; build it under GB1a. "partial" = real code that breaks another rule, so the Good is adapted.

**Count: 44 selected of 207 in scope.**

---

## 1 · Selected, per target reference

### java.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| JV1 | time in `Instant`/`Duration`; zoned only at a boundary | `long` millis arithmetic feels "not Date", so it passes; jjwt `Date.from(…)` looks like a breach but is the boundary | `DataRetentionJob.java:78` `Instant.now(clock).minus(…)` | `PipelineExecutionService.java:49,58,68` `System.currentTimeMillis()` deltas (also breaks LG3 at :59-60) |
| JV5 | `final var` only when the RHS shows the type | "a method whose name states it" read as any method | `AgentEvalService.java:79` `final var run = new AgentEvalRun(` | `ProviderController.java:58-59` `final var result = providerService.create(…).orThrow(…)` (also NM1) |

### types.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| TY1 | no `null` decides a case | `!= null` on an optional collaborator is not seen as "deciding a case" | `shared/agents/Version.java:18-31` (`None` / `Of`) | `GuardrailPipeline.java:34-36,123` nullable tiers, `if (nerEnabled && tier2 != null)` |
| TY3 | sealed variants first; compact ctor checks only the rest | either-or field pairs get validated by branching instead of modelled | `RetentionWindow.java:22-36` (cases + `Days` rejects `count <= 0` only) | `TrustedCertificateController.java:54-61` "either pem or uri+fingerprint" checked by `if/else` |
| TY8 | wrap a primitive on swap risk or an invariant | read as "wrap every id" or "wrap only with an invariant" (X4) | `shared/security/TrustId.java:10-23` | `TaskService.java:29-30` `submit(UUID agentId, UUID workspaceId, UUID sessionId, …)` — adapt the call-site swap; no swap incident found |
| TY9 | strengthen a type only where partiality shows | the brake on TY1/TY3/TY8 — over-wrapping looks like diligence | adapt | adapt |

### concurrency.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| CC3 | a timeout that stops the work; `orTimeout` only abandons | `orTimeout` looks like a timeout; the port javadoc even says so (`ToolHandlerPort.java:56`) | `WebhookCallbackSender.java:71-80` `HttpRequest.timeout(15s)` | `HttpToolHandler.java:221-222` `supplyAsync(…).orTimeout(…)` |
| CC4 | bounded pool has a bounded queue + stated rejection | `Executors.new*Pool(n)` looks bounded; its queue is not | `ActivityExecutorConfig.java:27-44` (queue 32, rejection stated) | `SseHeartbeatConfig.java:12-16` `newScheduledThreadPool(4, …)` — unbounded delay queue (verify intent; also pools virtual threads, CC1) |
| CC9 | success/failure/unknown; intent before the call; key from initiator | retrying layer mints its own key, or a timeout is treated as failure | `ScheduledTriggerJob.java:126-131` claim-and-advance before firing; `WebhookCallbackSender.java:75` job id header | adapt |

### errors.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| ER1 | foreseeable non-success is a sealed outcome; only faults throw | "name taken" feels exceptional, so the service throws | `AddMemberOutcome.java:13-23` | `DbConnectionService.java:73-76` throws `DB_CONNECTION_NAME_TAKEN` |
| ER4 | narrowest catch; `catch (Exception)` only at a must-not-fail boundary, commented | every best-effort site claims to be "a boundary" | `LeaseSweepJob.java:46-58` per-item loop, comment names why | `AdminActivityClient.java:86-88` `catch (Exception ignored)` around JSON parsing (also ER3) |
| ER8 | best-effort call may catch and continue; WARN with class | the allowed look-alike of ER3: "best effort" read as "may be silent" | `ChatOrchestrator.java:215-217` `log.warn(… e.toString())` | `ChatOrchestrator.java:222-228` `catch (Exception ignored)` in the same method |
| ER10 | error body carries the `ErrorCode` message only | `getMessage()` of a driver exception looks like useful detail | `GlobalExceptionHandler.java:75-84` fixed `AUTH_FORBIDDEN` message | `AgentController.java:186-190` returns `getMostSpecificCause().getMessage()` |

### comments.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| CM3 | a comment survives only for an outside constraint | any "why" comment about our own code feels allowed (X1) | `DbConnectionService.java:166-168` (HikariCP wraps the SQLException) | `ChatOrchestrator.java:219-221` justifies our own tag choice |
| CM4 | check a factual claim; encode "keep in sync" as type/test | a sync note feels like enough | `RetentionWindow.java:19-20` + sealed switch: the compiler holds the constraint | `SessionMessageController.java:231` "Stays in sync with docs/…/ARCHITECTURE.md"; `ChatOrchestrator.java:220` "tool types are an enum" over a `String toolType` (:202) |
| CM7 | never suppress a correctness lint; style rules may be | a written reason seems to make it fine (X6); edge vs TY10's one-statement `unchecked` | adapt (type `resolve` as `(value: boolean \| string \| null) => void`) | `aruvii-ui/src/app/core/confirm.service.ts:17-18` `eslint-disable-next-line no-explicit-any` |

### smells.md (incl. naming) + deslop/SKILL.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| DS1 | look for a restructure that deletes branches | moving a branch into a helper looks like a fix | `DataRetentionJob.java:69-77` switch on `RetentionWindow` (after #349, `dffd26e5`) | `dffd26e5^1`: `DataRetentionJob.java:69-73` + `DataErasureController.java:117-121`, the same `retentionDays == 0` branch twice |
| DS3 | no one-off `if` or second boolean in a flow | "just one more flag" | `agents/domain/RunMode.java:4-21` (third mode as a case) | `ChatOrchestrator.java:201-206` `boolean requiresApproval, … boolean mocked, String mockSource` |
| DS4 | remove pass-throughs and single-caller wrappers | collides with LY2: a module-boundary adapter looks like a pass-through | `PipelineExecutionAdapter.java:8-20` (port adapter across modules — stays) | `TriggerService.java:135-147` two one-line delegations, one caller (`ScheduledTriggerJob`) |
| DS8 | no null check / try-catch to silence a trusted path | a guard looks defensive, not like a hidden bug | adapt (drop the guard; fix the test that passes `null`) | `OpenApiSpecImporter.java:199` `toolGroupService == null` on a constructor-injected final field (:62,82) |
| DS12 | a rule-encoding literal is defined once | copies look harmless until one drifts | `aruvii-ui/playwright/support/smoke-name.ts:1-10` `isSmokeName` (#636, `917df5ea`) | `8f7bf163`: `aruvii-ui/playwright/global-setup.ts:52,85,100,117` `startsWith('smoke-')` ×4 (missed `smoke77-`, #636). Java alt: `currentTraceId()` copied in 5 classes (`GlobalExceptionHandler.java:219`, `AgentTaskController.java:135`, …) |
| DS14 | do not extract 2–3 similar lines with no shared rule | DS12 over-applied | `CustomPiiEndpointClient.java:46-51` and `LlmFakeGenerator.java:42-45` — similar factory lines, different timeouts, left alone | adapt |

### services.md + layering.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| LY1 | controller binds, delegates, shapes; outcome branches in a service | mapping an outcome to a status is a branch too — allowed | partial: `WorkspaceController.java:111-116` switch on `AddMemberOutcome` (drop :117-118, ER10/ER11) | `SessionMessageController.java:155-169` status check + slot claim decided in the controller |
| LY2 | interface only for a faked boundary or module boundary; `Default<Name>` package-private | old services.md §1 (interface for every service) still read as the rule | `eval/DefaultAgentEvalPublisher.java:15-16` | `LlmAdapterRegistryImpl.java:14-15` public `*Impl` of an internal registry (also TY13) |

### spring.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| LY6 | one constructor; optional/zero-or-more is `ObjectProvider<T>` resolved at use | taking an `ObjectProvider` but resolving it in the factory | `AgentToolHandler.java:40-44,122-128` | `AgentsAutoConfiguration.java:142-149` `@Lazy ObjectProvider` resolved at creation, throwing stub (also SC2, SC3). Alt Bad: `GuardrailPipeline.java:43-50` setters |
| LY7 | grouped settings in one validated record; a key bound once | `@Value` per class feels local and fine | `WorkerStreamsProperties.java:17-35` | `AdminActivityClient.java:44-46` vs `OllamaActivityClient.java:43-45` — `timeout-ms` default 5000 vs 1500 (covers SC12) |
| SC6 | `@Bean` returns the most specific type | clashes with "return the port" (hexagonal) | `ActivityExecutorConfig.java:27-29` returns `ThreadPoolTaskExecutor` | `AgentsAutoConfiguration.java:52-55` returns `AgentRepository`, builds `AgentRepositoryAdapter` |
| SC7 | several impls: `@ConditionalOnProperty` per value, exactly one, missing fails | `@ConditionalOnMissingBean` / `@Primary` look like the Spring way | **adapt** — no property-selected implementation on master (`ActivityClassifier.java:44` is an on/off switch only) | `ToolsAutoConfiguration.java:91-95` stub + `AgentsAutoConfiguration.java:78-83` `@Primary` |
| SC15 | settings record rejects bad values at startup, naming the key; runner spec proves it | OQ-SC5: Jakarta+`@Validated` **and** compact ctor, not either | partial: `WorkerStreamsProperties.java:26-35` + `WorkerStreamsStartupSpec.groovy:43-49` (no `@Validated`; spec names are camelCase, U2a) | `PlatformConfigProperties.java:7-11` — no validation at all |
| SC16 | no default for a secret/required endpoint; fail or named degraded mode at WARN | `@DefaultValue("")` reads as harmless; OQ-SC4 flag edge | adapt (blank key fails unless `aruvii.credentials.plaintext-allowed=true`) | `CredentialEncryptor.java:21-26` silent plaintext passthrough on blank key; fed by `application.yml:104` + `PlatformConfigProperties.java:9` |
| SC19 | must-finish-before-traffic → `ApplicationRunner`; later → thread from ready event | `@PostConstruct`/ready listener both "run at startup" | `TrustUpgradeCheckJob.java:58-61`; `AdminAutoSeeder.java:14-15` (runner) | `GlobalTrustStore.java:56-59` DB read in `@PostConstruct` (also SC18) |
| SC21 | proxied annotation works only from another bean; no `this` call | a same-class call looks fine and compiles | adapt (`SecretKeyStore` bean) | `SetupService.java:164-180` `getEffectiveSecretKey()` → `this.getOrGenerateSecretKey()` (`@Transactional` skipped; also SC13, NM3) |

### angular-ui.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| NGB3 | state in `signal()`, derived in `computed()`; `effect()` never copies | a `.set(filter(…))` in a handler looks like normal state | `aruvii-ui/src/app/features/agents/agent-list.component.ts:907-914` `filtered = computed(…)` | `aruvii-ui/src/app/features/pipelines/pipeline-builder.component.ts:225-226,264` `workspaceAgents.set(allAgents().filter(…))` (also NGC4 at :235) |

### api.md + tool-types.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| AP3a | role rule proven by a matrix IT incl. other-workspace member and API key | one wrong-platform-role 403 test feels like proof | partial: `SessionAccessMatrixIT.groovy:18-45` (no anonymous/API-key rows; test names not "should …") | `ToolControllerIT.java:57-106` — role-gated controller, zero 403/401 assertions |
| AP4a | `PUBLIC_PATHS` entry has an IT proving its replacement check; no secret in a URL | the MR sentence alone feels like enough | partial: `WebhookControllerIT.java:84-96` wrong secret → 401 (JUnit → Spock; secret in path, SS8/OQ-SS-3) | `SetupController.java:140-144` `POST /api/setup/complete` — no check, no refusal IT |
| TT2 | required args read off the handler; schema never stricter | "stricter is safer" | `EmailToolHandler.java:83-100` (`to` string-or-array, only `to`+`subject` required) | adapt from `CLAUDE.md:423-427` (`"to":{"type":"string"}`, `body` required) |

### security.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| SE1 | URL not in code only via the checked fetch: http/https, IPs after DNS, no redirects | a URL from a fetched document feels "ours"; edge: no address pinning (`SsrfGuard.java:20-23`, REQ-107 D4) | partial: `McpDiscoveryService.java:180-198,235-237` (throws `IllegalStateException`, ER2) | `OidcController.java:172-177` posts to `doc.tokenEndpoint()` unchecked |
| SE4 | `toRealPath()` then `startsWith(base)` | `normalize()` + `..` check looks complete; symlinks escape | **adapt** — no `toRealPath` on master | `FileToolHandler.java:50-58` `normalize()` + `contains("..")` |
| SE5 | untrusted JSON binds to a fixed record; `Map` only inside an adapter for an untypable shape (OQ-R27-3) | "it's inside the adapter" used for shapes that are easy to type | partial: `PresidioNerClient.java:54-63` + `PresidioEntity.java:4` (`var` breaks JV5) | `OidcSettingsService.java:105-114` `Map.class` then casts, though `OidcDiscoveryDoc` exists |
| SS13 | workspace resource guard asks `@wsAuth`; `hasRole` names platform roles only | `hasAnyRole('WORKSPACE_EDITOR')` reads as correct | `SessionController.java:160-166` `@wsAuth.canEditSession(#id)` | `ToolController.java:69-74` PATCH by role names only (probable BOLA, R34 §6 #1) |
| SS21 | passwords via `DelegatingPasswordEncoder`; machine secrets HMAC-SHA-256 (covers SE7a) | "BCrypt everything" looks safest | **adapt** — no HMAC or `DelegatingPasswordEncoder` on master | `ApiKeyService.java:240-247` BCrypt match per request; `AuthAutoConfiguration.java:16-19` one `BCryptPasswordEncoder(12)` for all |

### messaging.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| MS6 | answer "runs twice / crashed halfway"; reconcile when leftovers matter | "idempotent" claimed without naming the leftover | `DataRetentionAdapter.java:107-122` (release after delete, why the order is safe) | adapt (lead to check: `UserErasureAdapter.java:58-70` guards only a COMPLETED row) |

### logging.md + levels.md

| id | rule (short) | how it gets misread | Good | Bad |
|---|---|---|---|---|
| LG2 | log a failure once, where handled | "log context before rethrow" feels helpful | `GlobalExceptionHandler.java:66-73` (`logAtSeverity` at the handler) | `NotificationConfigService.java:140-142` `log.warn(…); throw e;` |
| LG3 | WARN = handled, no stack; ERROR = investigate, throwable last | `log.warn(msg, e)` prints a stack at WARN | `PresidioNerClient.java:64-67` WARN class+message; `LeaseSweepJob.java:56-57` ERROR with throwable | `SessionMessageController.java:318-320` `log.warn("Unexpected SSE failure…", e)` |

### metrics.md · tracing.md

None selected (see §2).

---

## 2 · No pair needed (163)

- **java.md** — JV2 explicit forbidden call · JV3 sentence names forms · JV4 condition stated plainly · JV6 forbidden positions listed · JV7 NIT, unambiguous · JV8 single clear form · JV9 Checkstyle gated · JV10 decided edge text · JV12 one-line misuse named
- **types.md** — TY2 compiler enforces exhaustiveness · TY4 Checkstyle gate (OQ2) · TY5 types named explicitly · TY6 TY11 gate catches · TY7 single clear form · TY10 "one statement" explicit · TY11 build gate · TY12 decided edge, TY1 · TY13 forms listed plainly
- **errors.md** — ER2 forms named exactly · ER3 sentence says it · ER5 two exact remedies · ER6 judgement, DS8 covers · ER7 library named outright · ER9 doc fix only · ER11 one place named
- **comments.md** — CM1 no ambiguity possible · CM2 CM3 pair covers · CM5 judgement, low risk · CM6 review check only
- **smells.md / deslop** — NM1 banned words listed · NM2 judgement, no real · NM3 "never writes" explicit · NM4 examples in rule · DS2 number, stated exception · DS5 condition stated plainly · DS6 DS1/DS4 cover it · DS7 list is explicit · DS9 mechanical, clear form · DS11 labelled heuristics list · DS13 process rule · DS15 doc fix only
- **services/layering** — LY3 sentence names case · LY4 ArchUnit gated · LY5 doc fix only
- **spring.md** — SC1 grep-able, exact form · SC2 LY6 pair covers · SC3 forms named exactly · SC4 annotations named outright · SC5 grep gate (OQ-SC6) · SC8 annotations listed plainly · SC9 test shape stated · SC10 NIT, attributes listed · SC11 NIT, forms listed · SC12 LY7 pair covers · SC13 forms named exactly · SC14 types named explicitly · SC17 one clear form · SC18 forbidden acts listed · SC20 edge in Decided · SC22 no use yet · OQ-SC3 decided edge text · OQ-SC4 SC16 pair covers
- **api.md / tool-types.md** — AP1 envelope named exactly · AP2 ArchUnit gated · AP5 "LIMIT" is explicit · TT1 checklist of artifacts
- **concurrency.md** — CC1 forms named, edge · CC2 exact call named · CC5 judgement, no real · CC6 calls named outright · CC7 exact type named · CC8 conditions listed plainly · CC10 checklist, clear
- **security.md** — SE2 "never fall back" explicit · SE3 standard, unambiguous · SE6 sinks named exactly · SE7a SS21 pair covers · SE8 single clear condition · SE10 sinks listed plainly · ND-4 ArchUnit gated allowlist · SS1 exact DSL call · SS2 decided edge text · SS3 exact form named · SS4 status stated plainly · SS5 forms named exactly · SS6 numbers stated plainly · SS7 claims listed plainly · SS8 forms listed, edge · SS9 attributes listed exactly · SS10 events listed plainly · SS11 framework mandated outright · SS12 ArchUnit gated · SS14 ArchUnit gated · SS15 annotation form named · SS16 decided edge text · SS17 annotations named outright · SS18 shape stated exactly · SS19 properties named exactly · SS20 review check only · SS22 decided edge text · SS23 AP3a pair covers · SS24 review check only · SS25 AP4a pair covers · SS26 process guidance · OQ-SS-2 future, not blocking · OQ-SS-3 edge under SS8 · OQ-SS-4 SS13 pair covers
- **messaging.md** — MS1 transport named outright · MS2 annotation named outright · MS3 blocked on #162 · MS4 "we authored" clear · MS5 ArchUnit gated · MS7 doc fix only
- **logging/levels** — LG1 format given literally · LG4 categories listed plainly · LG5 Good only, clear · LG6 standard SLF4J form · LG7 two events named · LG8 exact declaration given · LG9 field named exactly · LG10 marker form given · OQ4 table, not prose
- **metrics.md** — MX1 forbidden values listed · MX2 type per case · MX3 naming form stated · MX4 test shape stated · MX5 checklist (RED/USE) · MX6 process step · MX7 process step · MX8 decided edge (#160) · MX9 doc fix only
- **tracing.md** — TR1 field named exactly · TR2 master complies; FL24 example · TR3 two clear rules · TR4a wiring open (#55) · TR5 decided edge (X2)
- **angular-ui.md** — NGA1 flags, never loosen · NGA2 eslint gated · NGA3 forms named exactly · NGA4 one clear form · NGA5 exact idiom given · NGA6 order stated plainly · NGA7 single clear source · NGB1 forms named outright · NGB2 exact setting given · NGB4 decorators listed outright · NGB5 LY1 analogue, DS2 · NGC1 exact form given · NGC2 shape stated exactly · NGC3 cases listed plainly · NGC4 forms named exactly · NGD1 template lint gated · NGD2 a11y lint gated · NGD3 a11y lint gated · NGE1 component named exactly · NGE2 condition stated plainly · NGE3 form stated exactly · NGE4 decided edge text
- **eslint.config.js** — NGF1 config, not code · NGF2 config, not code · NGF3 lint gated · NGF4 config policy · OQ-NG2 config decision

---

## 3 · Approval batches (≤10, grouped by reference)

| batch | references | rules | n |
|---|---|---|---|
| **G9b-GB1 · Java language** | java.md · types.md · concurrency.md | JV1 JV5 TY1 TY3 TY8 TY9 CC3 CC4 CC9 | 9 |
| **G9b-GB2 · Errors, comments, layers** | errors.md · comments.md · services.md + layering.md | ER1 ER4 ER8 ER10 CM3 CM4 CM7 LY1 LY2 | 9 |
| **G9b-GB3 · Code shape and runtime** | smells.md · deslop/SKILL.md · messaging.md · logging.md + levels.md | DS1 DS3 DS4 DS8 DS12 DS14 MS6 LG2 LG3 | 9 |
| **G9b-GB4 · Frameworks** | spring.md · angular-ui.md | LY6 LY7 SC6 SC7 SC15 SC16 SC19 SC21 NGB3 | 9 |
| **G9b-GB5 · API and security** | api.md · tool-types.md · security.md | AP3a AP4a TT2 SE1 SE4 SE5 SS13 SS21 | 8 |

## 4 · Real Good missing on master (`772736bf`)

| id | state | note |
|---|---|---|
| SC7 | none | no bean is chosen among implementations by a property value; OQ-SC1 rewrite (#663) creates the first |
| SE4 | none | no `toRealPath` anywhere; `FileToolHandler` is the only path check |
| SS21 | none | no HMAC for machine secrets, no `DelegatingPasswordEncoder` |
| SC16 · SC21 · DS8 · CM7 · TY9 | none | adapt from the named Bad |
| SC15 · AP3a · AP4a · LY1 · SE1 · SE5 | partial | real code exists but breaks another rule (named above); Good is adapted |

Real Bad missing (adapt): TY9, CC9, DS14, MS6, TT2. Bads from older commits: DS1 (`dffd26e5^1`), DS12 (`8f7bf163`).
Stale candidates corrected against `49-g9b-candidates.md`: JV1's Bad `JwtService.java:56-57` is a library boundary
(allowed); SE1's Bad `OidcSettingsService.java:92` now goes through `SsrfGuard` (it is a partial Good); TR2's Bad
`AgentTaskController.java:135-144` obeys TR2 (it breaks TY1/U4/DS12 instead); DS12's TS Bad was fixed by #636.

## Operator approvals (2026-10-03)

- GB1 Java language: JV1 JV5 TY1 TY3 TY8 TY9 CC3 CC4 CC9 — approved as listed.
- GB2 Errors/comments/layers: ER1 ER4 ER8 ER10 CM3 CM4 CM7 LY1 LY2 — approved. Operator: ChatOrchestrator has too many issues to be a Good; use it only as a Bad. ER8's Good must come from another file (or be adapted).
- GB3 Shape+runtime: DS1 DS3 DS4 DS8 DS12 DS14 MS6 LG2 LG3 — approved. ER8 Good candidate: HealthController.java:84 (best-effort probe, WARN with class).
- GB4 Frameworks: LY6 LY7 SC6 SC7 SC15 SC16 SC19 SC21 NGB3 — approved.
- GB5 API+security: AP3a AP4a TT2 SE1 SE4 SE5 SS13 SS21 — approved. All 44 selected rules approved for pairs.
