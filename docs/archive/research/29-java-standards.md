# R25 · Java standards — our rules vs master vs primary sources

Ticket: `chiyanram/skills#48` (part of #9, feeds #33 G9b). Read 2026-10-02 at agent-platform
`origin/master` **`0aa04944`** (the worktree `crq-597-b837e3` is behind; every claim below was read via
`git show/grep origin/master`). Nothing here is approved — §4 is a menu for the operator.

Abbreviations: **AS/** = `.claude/skills/aruvii-standards/references/` · **RJ** = `.claude/rules/java-standards.md`
· **RO** = `.claude/rules/observability.md` · **SR** = `standards-review/SKILL.md` · **CM** = root `CLAUDE.md`
· **AT** = `aruvii-architecture-tests/src/test/java/ai/aruvii/arch/ArchitectureRulesTest.java` · **pl NNN** =
plinth `skills/NNN-*/references/*.md` @`5e338bb` · **GJS** = Google Java Style Guide · **corpus** =
`~/workspace/claude/analysis/skills-analysis/docs/extractions/`.

## 0. What was read

| source | depth |
|---|---|
| AS/ SKILL + 14 refs (modern-java, functional-java, types-and-null, type-design, error-handling, comments, services, concurrency, secure-coding, messaging, ood-smells, logging, metrics, tracing) | full |
| RJ, RO, `rules/dependencies.md` (BOM, non-rules 1–3), CM blocks Java/imports/API/credentials/logging | full |
| SR head + groups L T E C J O D | full |
| AT (domain/shared/Spring-AI/Jackson/javax/layer rules) · `checkstyle.xml` module list · `GlobalExceptionHandler` · ADR-0008 | full / targeted |
| pl 121 principles, 122, 124, 125, 126, 141, 142, 144, 181, 182, 183 | principles + example titles in full; examples read where cited (125 Ex13, 126 Ex13, 181 Ex1/Ex5) — **not every example body** |
| OpenJDK JEP 491 (Java 24), JEP 441 (Java 21) · GJS (4.1.1, 4.8.4.3, 6.2, 3.3.1, 7.3) · Spring Boot 4.1.1 tracing reference | targeted fetch |
| corpus: `stephanj-java-best-practices-skill`, `airails-java-conventions-cli-and-microprofile`, `cursor-java-oop-and-type-design`, `dr-jskill-spring-boot-backend-reference-standards`, `micronaut-platform-coding-…`, `java-optionals-skill` | directive lists |

## 1. Disposition per existing rule

`true on master?` = what the code does today. `src` = do primary sources agree (✓ agree · ~ partly · ✗ disagree · — silent).

### Java block (CM:187-197 = RJ:12-28, restated twice)

| rule | where | true on master? | src | disp. |
|---|---|---|---|---|
| `domain/` zero framework imports | CM:187 · SR L-01 | **yes** — 0 hits; **gated** by AT:72 `domain_packages_have_no_framework_imports` | ✓ pl 144 | KEEP, mark gated (drop SR L-01 as review item) |
| `domain/` = only records/interfaces/enums | CM:187 · SR L-01 MET | **no** — 18 classes (exceptions, `LicenseValidator`, `PromptAssembler`) | — | REWRITE "no framework types" only |
| `aruvii-shared` pure; Spring AI only in worker | CM:203-205 · SR L-02/03 | yes; gated AT:92, AT:104 | — | KEEP, gated |
| AssertJ only | RJ:12 · CM:189 | test rule | — | MOVE → testing (already ledger) |
| `final` wherever applicable | RJ:13 · CM:189 · SR T-04 | **mostly no** — ≈645 sig lines start `(final X` vs ≈2630 with non-final first param; Checkstyle has no `FinalParameters`/`FinalLocalVariable` | ~ stephanj: locals+fields; airails: NEVER on locals/params; GJS silent; EJ Item 17 = fields | REWRITE (narrow, see TY4) |
| No `null` to decide a case | RJ:14 · SR T-01 | new-code rule; 1422 `==/!= null` lines in main | ✓ pl 142/144, JEP 441, corpus "illegal states unrepresentable" | KEEP |
| GWT + `shouldXxx` + helpers last | RJ:15 | test rule | — | MOVE → testing |
| No banner/restating comments | RJ:16 · SR C-01/02 | 47 banner lines in 18 main files | ~ GJS 6.2/7.3 (javadoc on visible members — we do not require) | KEEP |
| Enums over string literals | RJ:17 · SR T-10 | 39 `.equals("UPPER")` lines/18 files; 6 role literals | ✓ cursor-oop (no ordinals) | KEEP |
| Structured `AruviiException`, no bare `ResponseEntity…build()` | RJ:18-20 · SR E-02 | 18 bare `.build()` sites remain (debt, stated) | ✓ pl 126 Ex14 (translate at boundary) | KEEP |
| Expected outcome = return type | RJ:21-27 · SR E-01 | yes — `AddMemberOutcome` exists as cited | ✓ pl 126 Ex7 · JEP 441 | KEEP (trim prose) |
| Whitespace: blank line between members, no tabs | RJ:28 | 0 tabs; nothing gates it | ~ GJS 4.6 | DROP as rule (taste; not gated, not reviewed) |
| No dead code / unused imports / magic strings | CM:195-196 | unused imports **gated** (Checkstyle `UnusedImports`) | — | KEEP, mark part gated |
| JPA block (13 bullets) | RJ:30-67 | mixed: `open-in-view: false` ✓; **`@PrePersist` sets `createdAt` in 25 entities** vs RJ:61; 5 `FetchType.EAGER` with no stated reason vs RJ:47-48 | ✓ dr-jskill (no unbounded `findAll`, paginate) | MOVE → `code/references/persistence.md` (out of scope here; R12 plan) |

### Imports / dependencies (CM:200-216)

| rule | true? | src | disp. |
|---|---|---|---|
| Jakarta only (SE `javax.*` allowed) | yes; **gated** AT:163 `no_pre_jakarta_javax_imports` | ✓ micronaut "NEVER javax.inject" | KEEP, gated |
| Jackson 3; `com.fasterxml…annotation` allowed | yes; **gated** AT:146 `no_jackson_2_imports_in_source` (+ domain AT:72) | — | KEEP, gated |
| No BOM override / read BOM / no pre-release | dependencies.md:13-23 | ✓ micronaut "NEVER hard-code versions" | KEEP (rules/dependencies) |

### aruvii-standards references

| ref · rule | true? | src | disp. |
|---|---|---|---|
| types-and-null §1-3 sealed + exhaustive | yes; 66 `sealed` lines/56 files (21 in shared) | ✓ JEP 441 "exhaustive switch without match-all is better" | KEEP → code/types |
| types-and-null §4 nulls stop at wire | yes (`ErasureLookupResult`) | — | KEEP |
| types-and-null §5 `final var` preference | not gated; **contradicts SR T-05** (§2 below) | ~ airails MUST var; GJS silent | MERGE with modern-java §4, one rule |
| type-design §1 domain types; §2 BigDecimal | §2 true (#157 double paths open) | ✓ pl 122 Ex "financial accuracy"; EJ Item 60 | KEEP |
| type-design §3 family naming, §5 aligned signatures, §7 whitespace, §8 table | derived from pl 122 ("font family", "type weights") | pl 122 itself | MERGE §3+§5 → one NIT; DROP §7 |
| type-design §4 / services §1 interface + package-private `Default` | **no** — 5 `Default*` classes; ≈45 of ≈47 `*Service` classes are `public class`; 1 `LlmAdapterRegistryImpl` | ✗ airails NEVER one-impl interface; type-design §4 itself says don't | REWRITE (LY2) |
| services §3 thin controllers | partly (ADR/AT `controllers_do_not_inject_repositories_directly`) | ✓ pl 126 Ex14 | KEEP |
| services §4 inseparable ops behind one method | yes (`DefaultErasureLookupService`) | — | KEEP |
| error-handling §1-3 outcome vs fault, catalogue | yes; **65** `ErrorCode` entries (ref says 35) | ✓ pl 126 Ex7/9/14 | KEEP, delete count |
| error-handling §4 never swallow, chain cause | mostly; **`ChatOrchestrator:226` `catch (Exception ignored)`** cited as Good by metrics.md | ✓ pl 126 Ex4/11, GJS 6.2 | KEEP + decided edge |
| error-handling §5 narrow catch, never Throwable | 266 `catch (Exception` lines/112 files; 0 `Throwable` | ✓ pl 126 Ex18, stephanj | KEEP |
| error-handling §6 validate at boundary | yes | ✓ pl 124 Ex1, pl 126 Ex1 | KEEP |
| error-handling §7 no Either/VAVR | yes (no VAVR) | ✗ pl 142 Ex "Use Either", pl 143 | KEEP (decided edge — ours wins) |
| comments §1-7 | yes | ~ GJS 7.3 (requires javadoc on visible members; we deliberately don't) | KEEP |
| modern-java §1 Instant + inject Clock | **238 `Instant.now()` lines/117 files vs 15 `Clock clock`**; `JwtService:56-57` cited as correct | ✓ pl 141 java.time; U4 approved | KEEP; fix JwtService example (§2) |
| modern-java §2 no `parallelStream` | yes, 0 | ✓ pl 125 #12 | KEEP |
| modern-java §3 text blocks | yes (30 files; ref says 13) | ✓ pl 141 Ex11 | KEEP NIT, delete count |
| modern-java §5 Optional return only | yes, 0 fields; 1 param (`TriggerPrincipalResolver:24`) | ✓ EJ Item 55 via corpus java-optionals | KEEP |
| modern-java §6 streams side-effect free | — | ✓ pl 142, stephanj | KEEP |
| modern-java §7 no hand DCL; §8 `List.of` edges; §9 JEP 513 | yes | ~ pl 141 Ex12 | KEEP §8; DROP §7, §9 (teaching, no decision) |
| modern-java §10 no JPMS | yes, but text says "Maven modules" — build is Gradle | ✗ pl 141 Ex8 recommends JPMS | KEEP as decided edge; fix wording |
| functional-java §2 collectors edges | yes | ✓ pl 142 Ex "downstream/merging collectors" | KEEP |
| functional-java §3 omit `default` on sealed switch | counter-example still live (`PromptBuilderController:236`) | ✓ JEP 441; GJS 4.8.4.3 only demands exhaustive | KEEP |
| functional-java §4-5 gatherers, laziness | — | ✓ pl 142 | DROP (teaching, no rule) |
| functional-java §6 "always pass an executor"; "none blocks" | **false on master** — 13 tool handlers call `CompletableFuture.supplyAsync(...)` with no executor (e.g. `HttpToolHandler:220`) = blocking I/O on the common pool | ✓ pl 125 #12 | KEEP; make it a review check (CC2) |
| concurrency §1 virtual threads for I/O; **"never `synchronized` around blocking — pins"** | 7 VT sites; 22 `synchronized` lines | **✗ JEP 491 (Java 24) removed `synchronized` pinning**; pl 125 Ex13 + dr-jskill also stale | REWRITE (CC1) |
| concurrency §2 bounded queue; §3 lock order; §4 owned state | 18 `volatile`, 22 `synchronized` | ✓ pl 125 #10, #11 | KEEP §2; MERGE §3+§4 |
| secure-coding §1-7 | §4 cites "JdbcTemplate … per ADR-0007" — ADR-0007 is RAG pgvector; 80 JpaRepository vs 22 JdbcTemplate files | ✓ pl 124 Ex1,2,6,7,8 | KEEP; fix §4 citation |
| messaging §1-6 | `KafkaTriggerManager:111` auto-commit still true; §4 cites `aruvii-worker/pom.xml` (Gradle now, `libs.versions.toml:121`) | — (project-specific) | KEEP; fix path |
| ood-smells §1-8 + SR X-01..13 | — | ✓ pl 121 (SOLID, DRY, YAGNI) | MERGE (R12 plan) |
| logging §1 placeholders | yes — 0 concatenated log lines | ✓ pl 181 Ex3, dr-jskill | KEEP, NIT |
| logging §2 exception last; WARN = class+msg no stack | yes | ✓ pl 181 Ex3 | KEEP |
| logging §3 guard only expensive args | yes (1 guard) | ✓ pl 181 Ex3 | KEEP NIT |
| logging §4 strip CR/LF from untrusted text | 2 sites do it (`ToolService:228`, `RagSearchService:126`); 5 `toolName=` INFO lines | ✓ pl 181 Ex5, pl 124 | KEEP |
| logging §5 `private static final Logger log` | 176 `log` / 7 `LOG` | ✓ dr-jskill `getLogger(Class)` | KEEP (NIT, unenforced) |
| logging §6 actuator curl, port 9090 | yes (`application.yml:76-85`) | ✓ Boot | MOVE → ops doc (not a coding rule) |
| RO: level table + 7 rules | `action=` in 53 of 120 files with `log.info`; GEH logs validation/auth failures at **INFO** while RO:16 puts them at WARN | ~ pl 126 Ex13 "log once at boundary"; dr-jskill "NEVER log and throw" | REWRITE (LG1-LG4) |
| metrics §1 cardinality; §2 types; §3 naming; §4 LongTaskTimer; §5 histograms; §6 test | "four meters, all in worker" false — `tool.args.unvalidated` in `ToolService:170`; `ChatOrchestrator:213` now `:222`; §6 example is JUnit `@Test` | ✓ pl 182 Ex1-5 | KEEP §1,§2,§6; MERGE §3-§5 |
| metrics §7 no Prometheus | yes (exposure `health,info,metrics,loggers`; #160) | pl 182 Ex6 wants scrape | KEEP as fact, not rule |
| tracing §1 Brave not OTel | yes (`libs.versions.toml:91`, 0 `io.opentelemetry`) | ✗ pl 183 is OTel-only | KEEP as decided edge |
| tracing §2 sampling 1.0 | yes (`application.yml:91`) | Boot default 0.1 (Boot 4.1.1 tracing ref) | KEEP decided edge |
| tracing §3 traceId on the message | yes (`ChatRequestEnvelope`) | — | KEEP |
| tracing §4 tolerate absent tracer — "`WebhookController.currentTraceId()` … pattern to copy" | method is in **`AgentTaskController:135`**; the copied code violates T-01/TY4/U4 (§2) | — | KEEP rule, replace example |

### SR groups — meta

| item | finding | disp. |
|---|---|---|
| SR rule 1 (:37-41) "Jackson 3, Jakarta … review-only ground" | false — AT gates both | REWRITE |
| L-01, L-02, L-03, D-02, D-03 | all decided by AT ⇒ by SR's own rule 1 they should not be reported | DROP as review checks; keep "run `make test ONLY=arch`" |
| SR authority (:27 "reference wins" vs :69 table CLAUDE.md first) | self-contradiction; plus AS/SKILL:12 "CLAUDE.md wins", RJ:10 "rules here win" | decide once (OQ1) |
| O-03 EDGE "semgrep already flags" | semgrep deleted | REWRITE |

## 2. Contradictions and false claims (evidence)

1. **ProblemDetail.** CM API block says errors are RFC 9457 ProblemDetail; ADR-0008 records "DRIFT … `ProblemDetail` … used nowhere"; `GlobalExceptionHandler:71` builds `ApiResponse.error(...)`. `ModelRoleController:73` comment repeats the false claim.
2. **"Nothing gates" Jackson 3 / Jakarta / domain purity.** CM:174-182 and SR:39-41 say semgrep's deletion left these to review. AT:72, :92, :104, :146, :163 enforce all five.
3. **Precedence, four answers.** AS/SKILL:12 CLAUDE.md wins · RJ:10 rules win · SR:27 reference wins · SR:69 CLAUDE.md first.
4. **Interface + Default.** services.md §1 and SR L-05 require it for every service; type-design.md §4 says don't add an interface with one impl and no seam. Master: 5 `Default*` vs ≈45 public service classes. SR L-05 EDGE points at "services.md §1 states when" — it states nothing of the kind.
5. **`var` on a method call.** types-and-null §5 Good: `final var outcome = logPort.findCompletedBySubjectEmailHash(hash)`. SR T-05 EDGE: `var x = service.find(id)` is UNMET. Same shape, opposite verdict.
6. **Virtual-thread pinning** (concurrency §1; pl 125 Ex13; dr-jskill:122). JEP 491, delivered in Java 24: virtual threads blocking in `synchronized` "release their underlying platform threads". Repo is Java 25. Remaining pinning: native frames, class init.
7. **"Always pass an executor; none blocks"** (functional-java §6). 13 tool handlers `supplyAsync` without executor, e.g. `HttpToolHandler.java:220` does blocking HTTP on the common pool; #627 raised it.
8. **Good examples that break other rules.** tracing §4 "pattern to copy" (`AgentTaskController:135-144`): `!= null` decides cases (T-01), non-final locals, `UUID.randomUUID()` (U4), brace-less `if` (GJS 4.1.1). modern-java §1 blesses `JwtService:56-57` `new Date()` / `Instant.now()` (U4). metrics.md Constraints blesses `ChatOrchestrator:226` `catch (Exception ignored)` (E-03). metrics §6 uses JUnit `@Test` (Spock required for new tests).
9. **Dangling `CLAUDE.md §` pointers** — §4, §2 DDD, §Observability, §Database, §Critical Architecture Rules, DoD §Code Quality, §Angular Icon & Select Standard: none exist (comments:3, error-handling:6/82/102, logging:3, functional-java:36/230, metrics:12, modern-java:63, tracing:8/144, types-and-null:3, type-design:7/119/181, services:3, AS/SKILL:8/69). SR:46 points to "CLAUDE.md §Doc drift" — it is ARCHITECTURE.md. `application.yml:82` points to CLAUDE.md "Runtime log toggling" — absent.
10. **Rotting counts** (CLAUDE.md doc rule forbids): ErrorCode 35→65; text-block files 13→30; CompletableFuture files 19→16; "four meters all in worker"; `ChatOrchestrator:213`→222; "three sealed types in shared"→21 files; "45 records in shared"→56; "~270 broad catches" (266, close).
11. **Stale build facts**: modern-java §10 "Maven modules", messaging §4 `aruvii-worker/pom.xml`, type-design "`ErasureLookupRequest` on !27, once that merges".
12. **Level drift**: RO:16 puts "RBAC denials, validation errors" at WARN; `GlobalExceptionHandler:90,105` log auth failure and validation at INFO, `:79` access denied at WARN.
13. **Two log policies**: RO:26 "every catch logs WARN/ERROR" vs pl 126 Ex13 / dr-jskill:289 "log once, never log-and-throw". SR O-02 EDGE already allows rethrow-without-log; RO does not say so.
14. **Possible duplicate traceId in log lines** (unverified): api `logging.pattern.level` adds `%X{traceId}` (`application.yml:111`) while Boot 4.1.1 also prints correlation IDs by default ("Spring Boot automatically includes correlation IDs in logs"). Check one real log line before writing a rule.

## 3. Missing rules worth adding (primary-source backed)

| rule | source | why it earns a place here |
|---|---|---|
| Restore interrupt: never swallow `InterruptedException` | pl 125 #9, pl 126 Ex5 | 10 sites, 8 restore — a quiet hang class; no rule today |
| Log once where handled; rethrow-with-cause does not log | pl 126 Ex13, dr-jskill:289 | resolves contradiction 13; GEH already logs per `ErrorCode` severity |
| Blocking work gets a named, bounded executor (not common pool) | pl 125 #2/#12 | contradiction 7, live on 13 handlers |
| Every remote call has a timeout; `orTimeout` does not stop the task | pl 125 #15, pl 126 Ex16 | handlers rely on `orTimeout`; underlying I/O keeps running |
| try-with-resources for every `AutoCloseable` | pl 126 Ex2, stephanj | standard, not stated anywhere in AS/ |
| Return empty collection, never `null` | cursor-oop:243 (EJ Item 54) | sharpens "no null decides a case" |
| Braces on every `if/for/while` | GJS 4.1.1 | the copied tracing example shows the gap; Checkstyle `NeedBraces` would gate it (mechanical → hook/Checkstyle, not review) |

Rejected from sources: JPMS (pl 141 Ex8), `Either` (pl 142/143), OTel API + `@WithSpan` (pl 183), javadoc on every visible member (GJS 7.3), `@NullMarked` everywhere (micronaut), package-private fields (airails), field injection (airails).

## 4. Groups for the operator (nothing approved)

Shape per G5: each target reference = Rules · When X use Y · Good/Bad (real code ≤15 lines, file:line) · Decided edges · Review checks.

### G-A · code/java (modern Java usage)

1. **JV1** Compute time in `Instant`/`Duration`; convert to `Date`/zoned types only at a library or display boundary. — modern-java §1, pl 141 · **ADOPT** (Clock = U4, already approved)
2. **JV2** No `parallelStream()`/`.parallel()` in request- or queue-serving code. — modern-java §2, pl 125 #12 · **ADOPT**
3. **JV3** Streams compute; effects (I/O, logging, mutation) stay outside `map`/`filter`; no `peek` for logging. — modern-java §6, pl 142, stephanj · **ADOPT**
4. **JV4** `toMap` without merge function only when a DB constraint guarantees uniqueness, named in a comment. — functional-java §2, pl 142 · **ADOPT**
5. **JV5** `final var` only when the right-hand side shows the type: constructor, factory, literal, or a method whose name states it. — types-and-null §5 + SR T-05 merged · **ADAPT** (fixes contradiction 5)
6. **JV6** `Optional` is a return type only — never a field, parameter, or collection element. — modern-java §5, corpus java-optionals · **ADOPT**
7. **JV7** Multi-line SQL/JSON/HTML in Java is a text block. — modern-java §3, pl 141 Ex11 · **ADOPT** (NIT)
8. **JV8** Every `AutoCloseable` opened in a method is closed by try-with-resources. — pl 126 Ex2, stephanj · **ADOPT** (new)
9. **JV9** Braces on every `if/else/for/while`, even one statement. — GJS 4.1.1 · **ADAPT**: gate via Checkstyle `NeedBraces`, not review
10. Decided edge: **no JPMS** — module boundaries are Gradle modules + AT `module_dependency_allowlist`. — modern-java §10 vs pl 141 Ex8 · **ADOPT** (reword "Maven")
11. DROP: whitespace rule (RJ:28), hand-DCL §7, JEP 513 §9, gatherers/laziness §4-5 — teaching, no decision. · **REJECT** as rules

### G-B · code/types

1. **TY1** No `null` decides a case: absence is `Optional`, a sealed interface + records, or an enum. — RJ:14, JEP 441, pl 144 · **ADOPT**
2. **TY2** A closed set of ≥2 cases is sealed (or an enum); its switch has no `default`. — types-and-null §2-3, JEP 441 · **ADOPT**
3. **TY3** A record's compact constructor rejects every component combination the domain forbids. — types-and-null §1, pl 142 · **ADOPT**
4. **TY4** `final` on fields always; on locals and parameters in new code; never a reason to touch old lines. — RJ:13 narrowed; stephanj, EJ Item 17 · **ADAPT**
5. **TY5** Money, cost, price: `BigDecimal` with explicit scale and rounding; `double` only for latencies and scores. — type-design §2, pl 122 · **ADOPT**
6. **TY6** A closed set of states/roles/modes is an enum, never a string literal; persisted as `EnumType.STRING`. — RJ:17, RJ:44, cursor-oop · **ADOPT**
7. **TY7** Return an empty collection, never `null`, from a method returning a collection. — cursor-oop:243 (EJ Item 54) · **ADOPT** (new)
8. **TY8** Wrap a primitive in a domain type only when it carries an invariant worth stating; not a quota. — type-design §1 (vs SR T-06 "UNMET inside domain") · **ADAPT** (softens T-06)
9. Decided edges: nulls allowed only in wire DTO mapping (types-and-null §4); no builders, no `Impl` suffix, no nested-class hierarchies (type-design §8). · **ADOPT**

### G-C · code/errors

1. **ER1** A foreseeable non-success (not found, already exists, over limit) is a sealed outcome in the return type; only faults throw. — RJ:21-27, pl 126 Ex7 · **ADOPT**
2. **ER2** A fault throws `AruviiException` with an `ErrorCode` from the catalogue; never a bare `ResponseEntity…build()`. — RJ:18-20, ADR-0008, pl 126 Ex14 · **ADOPT**
3. **ER3** A rethrown exception chains its cause; a caught exception is handled, rethrown, or logged with its class name — never empty. — error-handling §4, pl 126 Ex4/11, GJS 6.2 · **ADOPT**
4. **ER4** Catch the narrowest type; `catch (Exception)` only at a must-not-fail boundary, with a comment; never `Throwable`. — error-handling §5, pl 126 Ex18 · **ADOPT**
5. **ER5** Catching `InterruptedException`: restore with `Thread.currentThread().interrupt()` or rethrow. — pl 125 #9, pl 126 Ex5 · **ADOPT** (new)
6. **ER6** Validate request input at the boundary (Bean Validation); `requireNonNull`/`IllegalArgumentException` only for programming errors. — error-handling §6, pl 124 Ex1 · **ADOPT**
7. Decided edge: **no `Either`/VAVR** — loses the `traceId` envelope. — error-handling §7 vs pl 142/143 · **ADOPT**
8. Decided edge: best-effort metric/audit calls may catch-and-continue but log at DEBUG with class name, never an empty block. — fixes `ChatOrchestrator:226` · **ADAPT**
9. Fix: CM API block "errors are ProblemDetail" → "errors are `ApiResponse` with `success=false`". — ADR-0008 · **ADOPT**

### G-D · code/comments

1. **CM1** No banner or divider comments, in any file type. — comments §1 · **ADOPT**
2. **CM2** No comment restating the code, a dependency, or a config value. — comments §2-3 · **ADOPT**
3. **CM3** A kept comment states why — reason, constraint, or consequence — once, where the decision is made. — comments §4-5 · **ADOPT**
4. **CM4** A comment asserting a fact ("nothing else calls this", "because X") is checked before it lands. — comments §7 · **ADOPT**
5. **CM5** Javadoc on an interface only when the contract is not obvious; none on its implementation. — services §2 vs GJS 7.3 · **ADOPT** (decided edge vs GJS)
6. Drop comments §6 "length is a smell" as a rule (signal, stays as example). · **ADAPT**

### G-E · code/services + layering

1. **LY1** Controllers bind, delegate, shape the response; any branch choosing an outcome lives in a service. — services §3, pl 126 Ex14 · **ADOPT**
2. **LY2** Add an interface only when something fakes it in a test or it is a module boundary; its single implementation is `Default<Name>`, package-private. — type-design §4 + services §1 merged · **ADAPT** (fixes contradiction 4)
3. **LY3** Two operations that must not be split (answer + audit) sit behind one method. — services §4 · **ADOPT**
4. **LY4** `domain/` and `aruvii-shared` hold no Spring/JPA/Spring AI/Jackson-databind type; Spring AI stays in `aruvii-worker`. — CM:187/203, AT · **ADOPT** as *gated* — reviewer runs `make test ONLY=arch`, does not re-check by eye
5. Fix: CM/SR say Jackson 3, Jakarta, domain purity are ungated — they are gated by AT. · **ADOPT**

### G-F · code/concurrency

1. **CC1** Use virtual threads for blocking I/O fan-out, never pool them; `synchronized` is fine on Java 25 (JEP 491) — avoid blocking inside class initialisers. — JEP 491, pl 125 #8 · **ADAPT** (replaces stale pinning rule)
2. **CC2** Blocking work submitted async gets an explicit, named executor — never no-arg `supplyAsync`/`runAsync`. — functional-java §6, pl 125 #2/#12 · **ADOPT** (13 live violations, #627)
3. **CC3** Every remote call has a timeout that stops the work; `orTimeout` alone only abandons the future. — pl 125 #15, pl 126 Ex16 · **ADOPT** (new)
4. **CC4** A bounded pool has a bounded queue and a stated rejection behaviour. — concurrency §2, pl 125 #10 · **ADOPT**
5. **CC5** Shared mutable state has one owner; two locks only in one documented order. — concurrency §3-4, pl 125 #11 · **ADOPT**
6. **CC6** Never `join()`/`get()` mid-pipeline in request-serving code. — functional-java §6 · **ADOPT**

### G-G · obs/logging

1. **LG1** Service entry logs INFO `action=<verb> key=value…` with the ids; one line per interesting event. — RO:23, CM:296 · **ADOPT**
2. **LG2** Log a failure once, where it is handled; code that rethrows with cause does not also log. — pl 126 Ex13, dr-jskill:289 · **ADAPT** (replaces "every catch logs")
3. **LG3** WARN = handled, class + message, no stack; ERROR = needs investigation, throwable last for the stack. — RO table, logging §2, pl 181 · **ADOPT**
4. **LG4** No PII, prompts, tool args or secrets at INFO+; DEBUG/TRACE only via `PiiRedactor`. — RO:32-36, pl 181 Ex5 · **ADOPT**
5. **LG5** Strip CR/LF from any user-, model- or caller-supplied text in a log message; prefer logging the id. — logging §4, pl 181 Ex5, pl 124 · **ADOPT**
6. **LG6** `{}` placeholders, never concatenation; guard only an expensive argument. — logging §1,§3, pl 181 Ex3 · **ADOPT** (NIT)
7. **LG7** Long calls log duration on completion; scheduled jobs log tick start and completion with counts. — RO:29-31,44 · **ADOPT**
8. **LG8** Logger: `private static final Logger log = LoggerFactory.getLogger(ThisClass.class)`. — logging §5 · **ADOPT** (NIT; 7 `LOG` outliers)
9. Fix: RO table vs `GlobalExceptionHandler` levels for validation/auth (contradiction 12) — operator picks which is right. · OQ4

### G-H · obs/metrics + tracing

1. **MX1** Meter tags are closed sets you control; never an id, email, URL, model-supplied name or exception message. — metrics §1, pl 182 Ex2 · **ADOPT**
2. **MX2** Timer for completed durations, LongTaskTimer for in-flight jobs, Counter for events, Gauge on a strong reference. — metrics §2,§4, pl 182 Ex1/Ex4 · **ADOPT**
3. **MX3** Names dot-separated lower case, outcome as a tag; a rename is a migration with its own change. — metrics §3, pl 182 Ex2 · **ADOPT**
4. **MX4** New meter has a unit spec asserting name and tags on `SimpleMeterRegistry` (Spock). — metrics §6, pl 182 Ex3 · **ADAPT** (Spock, not JUnit)
5. **TR1** A new async hop carries `traceId` as a field on the message, not via thread-local context. — tracing §3 · **ADOPT**
6. **TR2** `Tracer` via `ObjectProvider`; code works with tracing absent. — tracing §4 · **ADOPT** (replace example, contradiction 8)
7. **TR3** No PII or high-cardinality span attributes; hand-made spans end in `finally`. — tracing §5, pl 183 Ex2 · **ADOPT**
8. Decided edges: Micrometer Tracing + Brave, not OTel API (vs pl 183); sampling 1.0 because traces correlate, not profile (vs Boot default 0.1); no Prometheus until #160. · **ADOPT**

### G-I · code/security (credentials block lives here; decrypt-site ND-4 unresolved)

1. **SE1** A fetch of a URL not in code allows only http/https, through the checked-fetch type from #527. — secure-coding §1, pl 124 Ex1 · **ADOPT**
2. **SE2** Decryption failure stops the call; never fall back to unauthenticated or cached. — secure-coding §2 · **ADOPT**
3. **SE3** SQL binds parameters; a dynamic identifier comes from a code-defined allowlist. — secure-coding §4, pl 124 Ex2 · **ADOPT** (fix ADR-0007 citation)
4. **SE4** A path from user input is resolved, normalised, then checked `startsWith(base)`. — secure-coding §5 · **ADOPT**
5. **SE5** Untrusted JSON binds to a fixed DTO; no polymorphic typing from payload fields. — secure-coding §6, pl 124 Ex7 · **ADOPT**
6. **SE6** `[innerHTML]`/`bypassSecurityTrust*` only for code-controlled content. — secure-coding §7, pl 124 Ex8 · **ADOPT**

### G-J · code/messaging (project-specific; no external source disagrees or applies)

1. **MS1** Internal api⇄worker traffic is Redis Streams (requests) and Pub/Sub (tokens); no Kafka internally. — messaging §1, ADR-0002 · **ADOPT**
2. **MS2** New Kafka consumers are built programmatically from runtime settings, no `@KafkaListener`. — messaging §3 · **ADOPT**
3. **MS3** No second consumer assuming a delivery guarantee until #162 decides ack mode and dedup key. — messaging §5 · **ADOPT**
4. **MS4** A message we did not author that cannot be parsed is skipped with partition+offset logged; our own failures are not skipped. — messaging §6 · **ADOPT**
5. **MS5** Every XADD passes `XAddOptions.maxlen` — already gated by AT `every_stream_append_is_bounded`. · **ADOPT** (note gated)

### Good/Bad candidates (real code, master `0aa04944`)

| rule | Good | Bad |
|---|---|---|
| ER1/TY2 | `aruvii-auth/.../application/AddMemberOutcome.java:13-23` + `WorkspaceController.java:112-114` | — |
| TY2 | — | `aruvii-api/.../controller/PromptBuilderController.java:225-237` (`default -> "event"`) |
| JV1/U4 | `aruvii-worker/.../scheduling/DataRetentionJob.java:78` `Instant.now(clock)` | `aruvii-auth/.../application/JwtService.java:56-57` |
| CC2 | — | `aruvii-tools/.../handlers/HttpToolHandler.java:220-226` |
| MX1 | `aruvii-worker/.../chat/ChatOrchestrator.java:222-225` | (same file `:226` is ER3/ER-edge Bad) |
| LG5 | `aruvii-tools/.../application/ToolService.java:228` | — |
| TR1 | `ChatRequestEnvelope` `traceId` field (tracing §3) | — |

## 5. Open questions

| # | decide | facts |
|---|---|---|
| OQ1 | one precedence rule for CLAUDE.md vs rules vs references vs SR | four files, four answers (§2 item 3) |
| OQ2 | `final` scope (TY4): fields only · fields+locals · everything | master ≈1 in 5 signatures final; no Checkstyle gate; sources split (stephanj yes, airails no, GJS silent) |
| OQ3 | gate mechanical rules in Checkstyle (`NeedBraces`, `FinalLocalVariable`, `FileTabCharacter`) instead of review? | checkstyle.xml has 22 naming/import modules, nothing on final/braces |
| OQ4 | validation/auth failures: INFO (code) or WARN (RO:16)? | `GlobalExceptionHandler:90,105` INFO |
| OQ5 | interface-per-service (LY2): accept "only when faked or module boundary"? | 5 of ≈50 services follow services.md §1 today |
| OQ6 | fix the CC2 violations under #627, or exempt tool handlers? | 13 handlers, common pool |
| OQ7 | persistence (RJ:30-67): own research pass? | `@PrePersist` sets timestamps in 25 entities contrary to RJ:61; 5 unexplained EAGER |
| OQ8 | duplicated `traceId` in log pattern (§2 item 14) — check a real log line, then decide `logging.pattern.correlation` | Boot 4.1.1 adds correlation by default |
