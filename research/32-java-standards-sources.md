# R27 · Java standards — operator-supplied sources mapped onto R25

Ticket: `chiyanram/skills#59` (part of #9, feeds #33 G9b). Read 2026-10-02. Baseline: R25
`research/29-java-standards.md` (groups G-A…G-J). Approved ledger: `research/19-approved-rules.md`.
**Nothing here is approved.** Our project rules are the authentic baseline; sources only confirm,
add or conflict.

Abbrev: **REF** = `agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs` ·
**pl NNN** = `REF/plinth-java-skills/NNN-*/` (`S` = SKILL.md, `R` = references/<main>.md) ·
**jvm** = `REF/jvm-skills-jvm-skills/skills/` · **Jeff** = `REF/Jeffallan-claude-skills/skills/`.
Line numbers are `path:line` in those files.

## 1. Per-source summaries and rules

### 1.1 pl 121 — object-oriented design (SKILL + 8 refs, ~11k words)

Effective-Java-shaped OOD review: SOLID/DRY/YAGNI, classes & interfaces, enums, methods, object
creation, smells, exception contracts. Every example is a toy (`NutritionFacts`, `Car`/`Engine`).
Workflow is Maven-bound (`./mvnw compile` mandatory, S:29-31) — not portable to our Gradle `make` front door.

1. Compile before refactoring; stop on failure; full verify after. — S:27-31 (Maven; ours = `make verify`)
2. Minimise accessibility of classes and members. — classes-interfaces:44-46
3. Accessor methods, not public fields, in public classes. — classes-interfaces:102-104
4. Minimise mutability; make classes immutable where possible. — classes-interfaces:153-155
5. Composition over inheritance for code reuse. — classes-interfaces:224-226
6. Design and document for inheritance, else make the class `final`. — classes-interfaces:288-290
7. Enums, not int constants; instance fields, not ordinals. — enums-annotations:44-46, :113-115
8. `EnumSet`/`EnumMap` instead of bit fields / ordinal indexing. — enums-annotations:151-153, :193-195
9. Always `@Override`. — enums-annotations:253-255
10. Validate parameters early; defensive copies of mutable inputs. — methods:44-46, :100-102
11. Return empty collections, never null. — methods:231-233
12. `Optional` for returns only; Bad: fields, params, `Optional<List>`. — methods:301-303, Bad block :354-365
13. Exceptions only for exceptional conditions, not control flow. — exceptions:44-46
14. Checked for recoverable, runtime for programming errors. — exceptions:95-97
15. Never ignore an exception; failure-capture info in messages. — exceptions:236-238, :329-331
16. Builder for many optional constructor params; DI over hardwiring. — object-creation:85-87, :246-248
17. Smells: God Class, Feature Envy, Inappropriate Intimacy, Refused Bequest, Shotgun Surgery, Data Clumps. — code-smells:45-127
18. SOLID / DRY / YAGNI one example each. — principles:47-396

### 1.2 pl 122 — type design (SKILL + 1 ref, ~4.5k words)

Typography metaphor ("font family", "kerning", "type weights") over 12 examples. Our AS/type-design.md
was already derived from it (R25 §1). Substance: value objects, BigDecimal, interface/impl contrast,
precise collection types. Pre-records style (`EmailAddress` is a class with `getValue()`, R:241-270).

1. Organise types into a clear hierarchy (nested static classes allowed). — R:56-58
2. Uniform naming patterns across a type family. — R:129-131
3. Whitespace for readability. — R:200-202
4. Wrap primitives/String in domain types that enforce invariants. — R:241-243
5. Generic type parameters for reusable types. — R:344-346
6. Fluent builders / DSLs for domain expression. — R:449-451
7. Separate contract (interface) from implementation. — R:511-513
8. Aligned, consistent method signatures across related classes. — R:565-567
9. BigDecimal for money/precision calculations. — R:670-672
10. Most precise type; interfaces over concrete; `Set` vs `List` by semantics; `Optional` for absence. — R:778-780
11. Process: compile first (Maven), stop on failure. — S:31-35

### 1.3 pl 123 — design + integration patterns (SKILL + 5 refs, ~7.5k words)

Problem-first pattern catalogue: classic GoF (6), REST (5), Kafka (5), persistence (5),
cross-cutting (5). Strongest anti-over-abstraction stance of any plinth skill (S:27-28, R:44-46).
Modern-Java-first (records, sealed, enums). REST ref mandates RFC 9457 — conflicts with ADR-0008.

1. Name the design pressure before naming a pattern; no pattern shopping. — S:26-28
2. No factory/strategy/decorator for a single stable implementation. — java-design-patterns:44
3. Prefer records, sealed interfaces, enums, pattern matching where they reduce ceremony. — java-design-patterns:45
4. Strategy only past two stable branches; else an enum switch. — java-design-patterns:59-61
5. Builder only for many optionals; prefer record constructor/static factory for small values. — java-design-patterns:110-112
6. Decorator for metrics/retry/logging without touching the core. — java-design-patterns:164-166
7. Adapter / anti-corruption layer translates external models at the boundary. — java-design-patterns:254-256, cross-cutting:44,57-59
8. State pattern keeps allowed transitions with the owning state. — java-design-patterns:295-297
9. Timeout first; retry only transient + idempotent; backoff with jitter; bounded attempts. — cross-cutting:42-43,92-94
10. Propagate correlation/trace context through services, messages, jobs. — cross-cutting:45,119-121
11. Bulkhead per slow dependency. — cross-cutting:149-151
12. Errors as RFC 9457 Problem Details; never leak stack/SQL/class names. — rest:44,114-116
13. Never expose persistence entities as API/messaging contracts. — rest:43, persistence:43
14. Transactions at use-case/service level; watch N+1, unbounded results, eager loading. — persistence:42-45
15. Kafka: idempotent consumers, intentional keys, versioned schemas, DLT/replay defined. — kafka:42-45

### 1.4 pl 124 — secure coding (SKILL + 1 ref, ~4.4k words)

Eight principles (R:21-30), one example each: validation, injection, least privilege, crypto,
secure exceptions, secrets, deserialization, XSS. R25 already cites Ex1,2,6,7,8 for SE1-SE6.
Examples are pre-Jakarta/Jackson-2 shaped (Ex7 imports `com.fasterxml.jackson.databind`, R:719-720).

1. Treat all external input as untrusted; validate type, length, format, range. — R:23, :55-57
2. Parameterised queries / safe APIs; never concatenate input into SQL/OS/LDAP. — R:24, :134-136
3. Least privilege; remove unused features, ports, accounts. — R:25, :242-244
4. BCrypt/Argon2 for passwords; AES-GCM for encryption; no MD5/SHA-1/DES. — R:26, :352-354
5. Generic message to clients; detailed non-sensitive diagnostics server-side; no stack traces out. — R:27, :526-528
6. No hardcoded secrets; load from env/secret manager; keep out of logs. — R:28, :644-646
7. No native deserialization of untrusted data; explicit DTOs, no default typing. — R:29, :709-711
8. Encode output to prevent XSS. — R:30, :758-760
9. Run a secrets scanner and a dependency CVE scan before release. — R:811-812

### 1.5 pl 126 — exception handling (SKILL + 1 ref, ~10.5k words; largest)

16 principles (R:21-36) and 20 examples. Strongest external backing for R25 G-C. Pro checked
exceptions (Ex8) and `@throws` javadoc on every checked exception (principle 7) — both against our
unchecked `AruviiException` + sealed outcomes. Ex14 maps to Problem Details (ADR-0008 conflict).

1. Specific exception types, never generic `Exception`/`RuntimeException`. — R:23, :75-77
2. try-with-resources for every resource. — R:24, :192-194
3. Validate early: `IllegalArgumentException`/`NullPointerException` with message. — R:25, :75-77
4. Generic message to user; detail in server log; no leakage. — R:26, :370-372
5. Chain the cause; preserve context. — R:27, :584-586
6. `InterruptedException`: restore interrupted status, then act. — R:28, :818-820
7. Document every checked exception with `@throws`. — R:29, :1140-1142
8. Exceptions only for exceptional conditions, not control flow. — R:1559-1561
9. Checked for recoverable, runtime for programming errors. — R:1612-1614
10. Favour standard exceptions; failure-capture info in message. — R:1696-1698, :1772-1774
11. Never ignore an exception. — R:1873-1875
12. Log once at the boundary that decides the response; lower layers rethrow without logging. — R:31, :2110-2114
13. Validation failure at boundary logged at **INFO**, system error at ERROR. — R:2127-2131 (bears on R25 OQ4)
14. Centralised handler translates domain errors to transport errors. — R:32, :2182-2186
15. Retry only idempotent ops, bounded, backoff, interruption-aware. — R:33, :2233-2235
16. Timeout → cancel the work, translate to a domain timeout error. — R:34, :2286-2290
17. `addSuppressed` for cleanup failures (twr does it). — R:35, :2330-2334
18. Never catch `Throwable`/`Error`. — R:36, :2371-2373
19. Handle checked exceptions inside lambdas explicitly. — R:2399-2403
20. Constructors fail fast; no half-built objects. — R:2455-2457

### 1.6 pl 128 — generics (SKILL + 1 ref, ~7.7k words)

17 examples, Effective-Java ch.5 in breadth (raw types, PECS, erasure, CRTP, heterogeneous
containers). Mostly library-author material; little an app service writes daily. Ex14 is Jackson 2
+ Gson (R:1464-1466). R25 had no generics group at all — this is the only source for one.

1. No raw types; parameterise every generic use. — R:61-63
2. PECS: `? extends` producers, `? super` consumers in parameters. — R:132-134, :1380-1382
3. Bound type parameters where the API needs capabilities. — R:223-225
4. Generic methods over `Object` + casts. — R:322-324
5. Diamond operator. — R:473-475
6. Know erasure: type tokens / `Class<T>` for runtime type. — R:580-582
7. Generics are invariant; model variance with wildcards. — R:756-758
8. Combine with records, sealed types, pattern matching. — R:976-978
9. `@SafeVarargs` only on provably safe varargs. — R:1242-1244
10. Wildcard-capture helper for `List<?>` mutation. — R:1293-1295
11. CRTP self-bound for fluent builder hierarchies. — R:1330-1332
12. Collections over arrays (array covariance). — R:1426-1428
13. `TypeReference`/`TypeToken` for generic (de)serialisation. — R:1458-1460
14. Fix unchecked warnings; `@SuppressWarnings("unchecked")` narrowest scope, provably safe only. — R:1504-1506
15. Single-letter conventional type-parameter names (`T`,`E`,`K`,`V`). — R:1546-1548

### 1.7 pl 141 — refactoring with modern features (SKILL + 1 ref, ~6.4k words)

Java 8→25 upgrade checklist: lambdas, streams, Optional, java.time, `var`, `List.of`, JPMS + JEP 511,
text blocks, JEP 513. A migration guide, not a standard — most items are already how master is written.
Its java.time Good example calls `Instant.now()`/`LocalDate.now()` inline (R:312-335) — against approved U4.

1. Lambdas / method references over anonymous classes. — R:54-56
2. Streams for declarative collection processing. — R:132-134
3. `Optional` for absent values (API returns). — R:203-205
4. `java.time` (`Instant` machine time, `Duration`, `Period`) replaces `Date`/`Calendar`. — R:291-293
5. Default methods for non-breaking interface evolution. — R:378-380
6. `var` only when the type is obvious; Bad: `var result = processData(data)`, numeric literals. — R:457-459, Bad :500-519
7. `List.of`/`Set.of`/`Map.of` unmodifiable factories. — R:532-534
8. JPMS `module-info` + JEP 511 module imports. — R:617-619
9. Mind performance of streams/boxing/Optional in hot paths. — R:698-700
10. Text blocks for multi-line strings. — R:911-913
11. JEP 513 flexible constructor bodies: validate before `super(...)`. — R:993-995

### 1.8 pl 142 — functional programming (SKILL + 1 ref, ~5.8k words)

23 examples: immutability, purity, streams, Optional idioms, records, sealed + pattern matching,
gatherers, currying, Either, async composition. Ex19 is the only plinth source that **passes an
executor** to `supplyAsync` (R:853) and forbids mid-pipeline `join()` (R:840). Ex21 `Either` is a
hand-rolled sealed interface (R:904-906), not VAVR — closer to our sealed outcomes than R25 implied.

1. Immutable objects and records; transformations return new instances. — R:23, :67-69, :106-108, :346-348
2. Pure functions; isolate side effects at the edges. — R:24, :127-129, :737-739
3. Functional interfaces, lambdas, method references. — R:154-156, :184-186
4. Streams; parallel streams "consider" for large data (mild clash with JV2). — R:225-229
5. Pattern matching for `instanceof`/`switch`; record patterns. — R:409-411, :813-815
6. Switch expressions over statement switches. — R:463-465
7. Sealed types for closed domain hierarchies. — R:517-519
8. Strong types for domain values. — R:557-559
9. Gatherers (JEP 461) for custom stream ops. — R:624-626
10. Optional via `map/flatMap/filter/orElse*`, not `isPresent()`+`get()`. — R:664-666
11. Currying / partial application. — R:702-704
12. Collectors: downstream, merging, unmodifiable. — R:769-771
13. Async: `thenApply/thenCompose/allOf`, explicit executor, no mid-flow `join()`. — R:836-840, :853
14. Either for value-or-error. — R:898-900
15. No shared mutable state in concurrent code. — R:953-955

### 1.9 pl 143 — functional exception handling (SKILL + 1 ref, ~6.3k words)

Business failures as values: `Optional`, **VAVR `Either`** (a required dependency, R:24-26), enums or
sealed records for error types. Agrees with our ER1 *principle* (outcomes are values, faults throw),
disagrees on the *carrier* (VAVR vs our domain-named sealed outcome). Constraint block is a
copy-paste error ("Maven validate … POM modifications", R:38-43).

1. Exceptions only for system failures / programming errors. — R:31, :218-220
2. Business/validation failures returned as values (`Optional`, `Either`). — R:32, :57-59
3. VAVR `Either<L,R>` is the carrier; add `io.vavr:vavr`. — R:24-26, S:30
4. Simple failure set → enum; rich failure → sealed interface + records. — R:376-378
5. Compose fallible steps with `map/flatMap`; no try/catch chains. — R:824-826, :1267-1269
6. Business failures log WARN/INFO; ERROR only for system failures. — R:985-987
7. Specific exception types when unavoidable; consistent `*Exception` naming. — R:33, :35
8. Checked exceptions sparingly, only for recoverable errors. — R:34

### 1.10 pl 144 — data-oriented programming (SKILL + 1 ref, ~5.5k words)

Data as immutable records, behaviour in separate services, pure transformations, flat ID references,
explicit pipelines. Confirms our records + sealed domain kernel. Two items fight our stack:
`Map<String,Object>` "generic until specific" (Ex5) and generic CRUD data access (Ex7).

1. Separate data (records) from behaviour (services/utility classes). — R:22, :52-54
2. Data immutable; transformations return new instances. — R:23, :129-131
3. Pure functions for data transformation. — R:24, :233-235
4. Flat, denormalised data with ID references over deep nesting. — R:25, :330-332
5. Start with `Map<String,Object>` for dynamic data; convert to records when processing. — R:25, :431-433
6. Validation as pure functions returning a validation result. — R:545-547
7. Generic CRUD data-access interfaces, interchangeable implementations. — R:652-654
8. Every transformation explicit and traceable; no hidden logic in data objects. — R:26, :771-773

### 1.11 pl 304 — Spring Boot security (SKILL + 1 ref, ~1.5k words)

Eight short Spring Security examples: filter chain, method security, CSRF/stateless, CORS, OAuth2
resource server, password encoding, 401/403 JSON, headers. Short and mostly sound. Assumes an
external IdP (`issuer-uri`, Ex5) — we mint our own JWTs (`JwtService`) with `PUBLIC_PATHS`.

1. Explicit matchers, most-specific first; `anyRequest().authenticated()` default; `permitAll` only for health/docs/true anonymous. — R:40-44
2. `@EnableMethodSecurity` + `@PreAuthorize` where URL rules cannot express ownership/tenant. — R:75-79
3. Disable CSRF only together with `STATELESS` session and bearer-only auth. — R:112-116
4. CORS: whitelist origins; never `*` with credentials. — R:134-138
5. Resource-server JWT via `issuer-uri`; never a hardcoded symmetric secret. — R:166-170
6. `DelegatingPasswordEncoder` for upgradeable hashes; never plaintext. — R:184-188
7. Custom 401/403 entry point + denied handler returning JSON, no stack traces. — R:214-218
8. Keep Spring Security default headers; deny framing for browser admin UIs. — R:258-262
9. Never weaken protection to green a test; never log tokens/passwords/Authorization. — R:293-294
10. Integration tests for unauthenticated and forbidden access. — R:288

### 1.12 jvm-skills catalogue (`jvm/framework/*.yaml` 15 · `jvm/language/*.yaml` 9 · repo `jvm-skills/jvm-skills` @`c6d477f`, 140★)

Catalogue entries (name, description, upstream repo, trust, tags) — **no rules of their own**. Of 24
entries, 7 are off-stack (Kotlin ×3, Quarkus ×2, Camel, KMP Firebase), 5 are scaffolding/migration
(dr-jskill, SivaLabs, restart, Boot-4 migration, Batch 6), 4 already mined in R25's corpus (plinth,
stephanj, airails ×2, java-optionals). Upstreams fetched only where the summary named a rule candidate:

| yaml | upstream (★) | candidate? | what was read |
|---|---|---|---|
| framework/spring-boot.yaml:3-8 | adityamparikh/spring-boot-skill (0★) | yes — "virtual-thread discipline, JSpecify/NullAway" | corpus extraction `adityamparikh-spring-boot-skill.md` :39, :197-238, :466-492 |
| language/streams-java.yaml:3-8 | martinfrancois/java-streams-skill (0★) | yes — "when parallelStream() is appropriate", collector pitfalls | corpus `java-streams-skill.md` :115-299 |
| language/logging-patterns-java.yaml:3-6 | piomin/claude-ai-spring-boot (1303★) | weak — JSON logs + MDC | corpus `claude-ai-spring-boot-jpa-logging-spring.md` :69-72 |
| language/optional-java.yaml | martinfrancois/java-optionals-skill | already R25 (JV6) | — |
| others | — | no (off-stack, scaffolding, or already mined) | yaml only |

Rules surfaced (upstream, via corpus extraction):

1. Never pool virtual threads. — adityamparikh ext:473-475 (confirms CC1)
2. `ReentrantLock` not `synchronized` around blocking I/O "(pins carrier)". — ext:479-481 (**stale on Java 25**, JEP 491; same error R25 found in pl 125)
3. No `ThreadLocal` for large/long-lived state; `ScopedValue` (final in 25) or explicit context. — ext:486-488 (**new**)
4. Never set priority/daemon on virtual threads. — ext:490-492
5. NullAway + JSpecify `@NullMarked`, build fails on violation. — ext:203-238 (R25 rejected `@NullMarked`; see OQ)
6. Do not build stream results by mutating external state from `forEach`. — streams ext:266-268 (confirms JV3)
7. Never claim parallel-stream speedup without measurement. — streams ext:115-128, :278 (confirms JV2)
8. Prefer JSON-structured logs for machine/AI analysis. — piomin ext:69-71 (ops choice, not a code rule)

### 1.13 jvm `testing/mutation-testing.yaml` → upstream `.claude/skills/mutation-testing/SKILL.md` (local, 389 lines, read in full)

yaml (:1-29) points at the jvm-skills repo's own skill (trust `official`, v0.5.0; SKILL body says
v0.1.0 at :375). Gradle `info.solidsoft.pitest`, Kotlin-first, with a scoped-on-diff run, survivor
triage into killable/equivalent/ambiguous, and an inverted-TDD kill loop. Paths below = `MT:line`.

1. Preflight: test sources compile, JUnit launcher version known, before any pitest run. — MT:22-39
2. Mutators `STRONGER`; never `ALL` (unstable, equivalent-prone). — MT:62, :362
3. `+FLOGCALL` + `avoidCallsTo` loggers; exclude generated members/classes. — MT:63-78, :358
4. Thresholds 60/60/60 (mutation, coverage, test strength) in bootstrap. — MT:88-90
5. History file on for incremental analysis; bust it after dep/branch changes. — MT:85-86, :361
6. `fullMutationMatrix` on so survivors name their covering tests. — MT:83, :175
7. Pin `junit5PluginVersion` to the project's Platform line; forward `tasks.test` jvmArgs. — MT:97-111
8. Scoped run from `git diff`; empty scope aborts, never falls back to whole codebase. — MT:135-154
9. SURVIVED ≠ NO_COVERAGE ≠ TIMED_OUT. — MT:192
10. Triage survivors before killing; archetypes A-D; bias toward AMBIGUOUS, not equivalent. — MT:194-235
11. Equivalent set is durable across sessions until the line changes. — MT:270
12. Kill test passes first run; RED proof = scoped rerun shows KILLED. — MT:282, :292, :344
13. Assert observable behaviour on a diverging input; reject tautological tests. — MT:289-290, :338
14. Verify: target KILLED, no KILLED→SURVIVED in class, killed count rose. — MT:332-336
15. Read `mutations.xml`, not the Gradle exit code. — MT:332

### 1.14 Jeffallan/claude-skills (`Jeff`, @`882ef55`, 11.7k★) — Java/JVM-relevant skills only

Of 66 skills, three are JVM: **`java-architect`** (SKILL 134 + 5 refs ~1.9k lines), **`spring-boot-engineer`**
(SKILL 197 + 5 refs ~2.2k lines), `kotlin-specialist` (off-stack, not read). `api-designer` only links
to spring-boot-engineer (:13). Both JVM skills target **Boot 3.x / Java 21**, use **Lombok** throughout
(49 annotation hits across refs), test with **MockMvc + `@MockBean` + H2** — all against our stack.

1. Records, sealed classes, pattern matching (Java 21 features). — java-architect/SKILL:44
2. Flyway/Liquibase migrations; OpenAPI docs; externalise all config. — java-architect/SKILL:45-48
3. Never skip input validation; never store sensitive data unencrypted. — java-architect/SKILL:52-53
4. No blocking in reactive chains (`.block()` in WebFlux). — java-architect/SKILL:54, spring-boot-engineer/SKILL:192
5. Respect transaction boundaries; `readOnly = true` on reads, `@Transactional` on multi-step writes. — java-architect/SKILL:55, spring-boot-engineer/SKILL:184
6. Constructor injection; never field `@Autowired`. — spring-boot-engineer/SKILL:180, :189
7. `@Valid @RequestBody` on every mutating endpoint. — spring-boot-engineer/SKILL:181, :190
8. `@ConfigurationProperties` bound to a record for typed config. — spring-boot-engineer/SKILL:182
9. Specific stereotypes (`@Service`/`@Repository`) over `@Component`. — spring-boot-engineer/SKILL:183, :191
10. Exceptions → `@RestControllerAdvice`; problem details, no stack traces. — spring-boot-engineer/SKILL:185
11. Secrets from env/Config server, never `application.yml`. — spring-boot-engineer/SKILL:186, :193
12. No deprecated Boot 2.x APIs (`WebSecurityConfigurerAdapter`). — spring-boot-engineer/SKILL:195, java-architect/SKILL:51
13. Avoid N+1 with `JOIN FETCH`/`@EntityGraph`; DTO projections for reads; paginate. — java-architect/SKILL:99-105, refs/jpa-optimization:384-388
14. `open-in-view: false`. — java-architect/refs/spring-boot-setup:140
15. Coverage ≥85% before closing. — java-architect/SKILL:27

Defects worth naming: SKILL Quick Start controller returns the JPA entity (`List<Product>`,
spring-boot-engineer/SKILL:111) against its own "hide internals"; ProblemDetail handler echoes
`ex.getMessage()` to the client (java-architect/refs/spring-boot-setup:233-236); JWT secret default
`your-256-bit-secret-key-here-change-in-production` (java-architect/refs/spring-security:421);
`jdbc:h2:mem` test config (spring-boot-engineer/refs/testing:454).

## 2. Mapping onto R25 groups (master read at `origin/master` **`5fda6873`**)

Key: **✓** confirmed by · **✗** conflicts with (why) · **—** no source among R27's. Citations use §1 paths.

### G-A · code/java
- **JV1** Instant/Duration, convert at boundary — ✓ pl 141 R:291-293 · ✗ pl 141 R:312-335 Good example calls `Instant.now()` inline (loses to approved U4)
- **JV2** no `parallelStream` — ✓ streams ext:115-128, :278 (measure first) · ✗ mild: pl 142 R:225-229 "consider parallel streams for large data"
- **JV3** streams side-effect free — ✓ pl 142 R:24, :737-739; streams ext:266-268
- **JV4** `toMap` merge function — ✓ pl 142 R:769-771 (merging collectors)
- **JV5** `final var` only when RHS shows type — ✓ pl 141 R:457-459, Bad :500-505 (`var result = processData(data)` is Bad) — **settles R25 contradiction 5 in favour of SR T-05**
- **JV6** Optional return only — ✓ pl 121 methods:301-303, Bad :354-365 (fields, params, `Optional<List>`); pl 142 R:664-666 adds "no `isPresent()`+`get()`"
- **JV7** text blocks — ✓ pl 141 R:911-913
- **JV8** try-with-resources — ✓ pl 126 R:24, :192-194
- **JV9** braces — — (no R27 source)
- no JPMS (decided edge) — ✗ pl 141 R:617-619 (still recommends JPMS + JEP 511); ours wins, as R25

### G-B · code/types
- **TY1** no null decides a case — ✓ pl 142 R:517-519 (sealed), pl 143 R:376-378 (enum/sealed error types)
- **TY2** sealed + no `default` — ✓ pl 142 R:409-411, :463-465, :517-519; pl 123 java-design-patterns:45
- **TY3** compact constructor rejects forbidden combos — ✓ pl 126 R:2455-2457 (constructors fail fast); pl 122 R:241-243
- **TY4** `final` fields always; locals/params new code — ✓ fields: pl 121 classes-interfaces:153-155, pl 144 R:23 · — on locals/params (no source)
- **TY5** BigDecimal money — ✓ pl 122 R:670-672
- **TY6** enums over string literals; no ordinals — ✓ pl 121 enums-annotations:44-46, :113-115
- **TY7** empty collection, never null — ✓ pl 121 methods:231-233
- **TY8** domain wrapper only when it states an invariant — ✓ pl 122 R:241-243 ("enforce invariants") · ✗ mild: pl 142 R:557-559 wraps by default
- decided edge "no builders" — ✗ pl 121 object-creation:85-87, pl 122 R:449-451 (builders/fluent) · ✓ pl 123 java-design-patterns:110-112 (prefer record ctor/static factory for small values). Master: **0** builder classes.
- decided edge "nulls only at wire mapping" — ✗ pl 144 R:431-433 (`Map<String,Object>` until specific)

### G-C · code/errors
- **ER1** foreseeable non-success = sealed outcome — ✓ pl 143 R:31-32, :218-220; pl 121 exceptions:44-46; pl 126 R:1559-1561 · ✗ carrier: pl 143 R:24-26 VAVR `Either`
- **ER2** fault = `AruviiException`+`ErrorCode`; no bare `ResponseEntity` — ✓ pl 126 R:32, :2182-2186 (centralised translation) · ✗ envelope: pl 126 Ex14, pl 123 rest:44, Jeff java-architect/refs/spring-boot-setup:216-257 all say ProblemDetail (ADR-0008 says ApiResponse)
- **ER3** chain cause, never empty catch — ✓ pl 126 R:27, :584-586, :1873-1875; pl 121 exceptions:329-331
- **ER4** narrow catch, never Throwable — ✓ pl 126 R:23, :2371-2373
- **ER5** restore interrupt — ✓ pl 126 R:28, :818-820. Master: 8 `catch (InterruptedException` / 8 `currentThread().interrupt()` in main
- **ER6** validate at boundary — ✓ pl 124 R:23, pl 126 R:25, Jeff spring-boot-engineer/SKILL:181
- decided edge no Either/VAVR — ✗ pl 143 R:24-26, pl 142 R:898-900. Note pl 142's `Either` is a hand-rolled sealed type, not VAVR; our objection (generic `L` loses domain naming) still holds
- edge best-effort catch logs DEBUG — — (no R27 source)
- fix CM "errors are ProblemDetail" — sources unanimously say ProblemDetail; ADR-0008 is the decision. **Unchanged: ours wins** (§3)

### G-D · code/comments
- **CM1–CM4** — — (no R27 source speaks to comments)
- **CM5** javadoc only when contract non-obvious — ✗ pl 126 R:29 (`@throws` on every checked exception — moot: master defines **0** checked exceptions)

### G-E · code/services + layering
- **LY1** thin controllers — ✓ pl 126 R:2182-2186; Jeff spring-boot-engineer/SKILL:183
- **LY2** interface only when faked or module boundary — ✓ pl 123 java-design-patterns:44 ("no factory/strategy/decorator for a single stable implementation"), S:27-28 · ✗ pl 122 R:511-513, pl 121 principles:431-433 (interface/impl contrast by default)
- **LY3** inseparable ops behind one method — ✓ pl 123 persistence:42, :114-116 (transaction at use-case level)
- **LY4** domain/shared purity, gated — ✓ pl 144 R:22; Jeff java-architect/SKILL:23 (DDD/clean boundaries)
- **NEW-ish** constructor injection only — ✓ Jeff spring-boot-engineer/SKILL:180, :189. Master: 11 `@Autowired` in main, e.g. setter injection with `required=false` at `GuardrailPipeline.java:42-49`

### G-F · code/concurrency
- **CC1** VTs for I/O, never pooled; `synchronized` fine on 25 — ✓ "never pool" adityamparikh ext:473-475 · ✗ adityamparikh ext:479-481 repeats the pre-JEP-491 pinning claim (stale)
- **CC2** explicit named executor for async — ✓ pl 142 R:836-840, :853
- **CC3** timeout that stops the work — ✓ pl 126 R:34, :2286-2290; pl 123 cross-cutting:42, :92-94
- **CC4** bounded pool + queue — ✓ pl 123 cross-cutting:149-151 (bulkhead)
- **CC5** one owner of shared mutable state — ✓ pl 142 R:953-955
- **CC6** no mid-pipeline `join()` — ✓ pl 142 R:836-840; Jeff java-architect/SKILL:54 (no blocking in reactive)

### G-G · obs/logging
- **LG1** `action=` INFO entry — — (pl 126 R:2110-2131 uses dotted event names `order.create.validation_failed`; not ours)
- **LG2** log once where handled — ✓ pl 126 R:31, :2110-2114
- **LG3** WARN class+msg, ERROR with stack — ✓ partial pl 143 R:985-987 (business failure WARN/INFO, system ERROR)
- **LG4** no PII/secrets at INFO+ — ✓ pl 124 R:28; pl 304 R:294 (never log tokens/Authorization)
- **LG5** strip CR/LF — — (pl 124 R:23 general input validation only)
- **LG6–LG8** — — (no R27 source)
- **OQ4** validation/auth at INFO or WARN — pl 126 R:2127 logs boundary validation failure at **INFO**; pl 143 R:985-987 "WARN or INFO". Sources lean INFO = what `GlobalExceptionHandler` does.

### G-H · obs/metrics + tracing
- **MX1–MX4** — — (no R27 source)
- **TR1** traceId on the message — ✓ pl 123 cross-cutting:45, :119-121 ("carry request identity through services, messages, and jobs")
- **TR2/TR3** — —

### G-I · code/security
- **SE1** checked fetch http/https — ✓ pl 124 R:23 (validate untrusted input)
- **SE2** decrypt failure stops — — 
- **SE3** bind SQL params — ✓ pl 124 R:24, :134-136
- **SE4** path normalise + `startsWith` — ✓ pl 124 R:23 ("path traversal")
- **SE5** fixed DTO, no polymorphic typing — ✓ pl 124 R:29, :709-711 (its Good example is Jackson 2 — rule fine, example not copyable). Master: 0 default-typing; but `GraphMailClient.java:85-86,146,184` binds Graph responses to `Map<String,Object>` with unchecked casts
- **SE6** innerHTML only for code-controlled — ✓ pl 124 R:30, :758-760

### G-J · code/messaging
- **MS1–MS5** — ✓ in spirit pl 123 kafka:42-45 (idempotent consumers, keys, versioned schemas, DLT) — confirms MS3 (#162 ack/dedup) and MS4 (poison skip). No conflict.

### 2.1 NEW rules the sources add that our stack needs

1. **N1** Request- or call-scoped context (nesting depth, tenant, principal) is a `ScopedValue` or an explicit parameter, never a new `ThreadLocal`. — adityamparikh ext:486-488. Master: `AgentNestingContext.java:12` ThreadLocal, hand-copied across `supplyAsync` at `AgentToolHandler.java:76-82`.
2. **N2** An error response carries the `ErrorCode` message, never `ex.getMessage()` from a library, driver or JDK exception. — pl 124 R:27, :526-528; pl 123 rest:114-116. Master Bad: `AgentController.java:186-190` returns the DB driver's constraint message.
3. **N3** Exception→response mapping lives in `GlobalExceptionHandler` only; no per-controller `@ExceptionHandler`. — pl 126 R:32, :2182-2186 (Bad = scattered). Master: 14 controllers carry local handlers.
4. **N4** Spring beans take dependencies through the constructor; an optional collaborator is `ObjectProvider<T>`, never setter/field `@Autowired(required=false)`. — Jeff spring-boot-engineer/SKILL:180, :189. Master Bad: `GuardrailPipeline.java:42-49`.
5. **N5** No raw types; `@SuppressWarnings("unchecked")` sits on the single statement, never a method or class. — pl 128 R:61-63, :1504-1506. Master: Good `GraphMailClient.java:85`, Bad same file `:146`.
6. **N6** Retry only transient failures of idempotent calls: bounded attempts, backoff with jitter, after a timeout exists. — pl 126 R:33, :2233-2235; pl 123 cross-cutting:42-43, :92-94.
7. **N7** Never a JPA entity in an `ApiResponse`, DTO or message payload. — pl 123 rest:43, persistence:43. Master: 0 violations; ungated — a candidate ArchUnit rule, not a review item.
8. **N8** Grouped settings bind to a `@ConfigurationProperties` record; `@Value` only for a single scalar. — Jeff spring-boot-engineer/SKILL:182. Master Good: `PlatformConfigProperties.java:7-15`. (NIT)
9. **N9** Never weaken a security rule, matcher or `PUBLIC_PATHS` entry to make a test pass. — pl 304 R:293. (Fits CM's "adding a public path is a security decision".)

Considered and **not** proposed: classes `final` unless designed for inheritance (pl 121 classes-interfaces:288-290) —
Spring's CGLIB proxies (`@Transactional`, `@PreAuthorize` on 175 methods) need non-final bean classes;
records are already final. `@Override` always (pl 121 enums-annotations:253) — mechanical, belongs in Checkstyle
`MissingOverride` if anywhere. `addSuppressed` (pl 126 Ex17) — try-with-resources does it (JV8).

## 3. Conflicts with our stack or approved rules — stated plainly

1. **Lombok.** Jeff java-architect + spring-boot-engineer use it throughout (`@RequiredArgsConstructor` java-architect/SKILL:74, `@Data` spring-boot-engineer/SKILL:59; 49 hits in refs). Master: 0 Lombok. Records + constructors replace it. **Reject.**
2. **ProblemDetail (RFC 9457).** pl 123 rest:44, :114-116 · pl 126 R:2182-2210 · pl 304 R:288 · Jeff spring-boot-engineer/SKILL:185 · Jeff java-architect/refs/spring-boot-setup:216-257 — five sources, unanimous. ADR-0008 + `GlobalExceptionHandler` use `ApiResponse.error`. **Ours wins**; the CLAUDE.md API-block line saying ProblemDetail is the thing to fix (R25 G-C 9). The *principle* behind it (stable machine-readable code, no leaked internals) is adopted as N2 via `ErrorCode`.
3. **Checked exceptions.** pl 121 exceptions:95-97, pl 126 R:1612-1614 and R:29 (`@throws` on every checked one) — use checked for recoverable conditions. Master: 0 classes `extends Exception`, 31 extend `RuntimeException`/`AruviiException`; recoverable outcomes are sealed returns (ER1). **Reject** — our sealed outcome is the stronger form of the same intent (the caller cannot ignore it, and it does not cross lambdas badly — pl 126 Ex19 exists only because checked exceptions do).
4. **VAVR `Either`.** pl 143 R:24-26 makes it a required dependency. **Reject** (R25 decided edge). pl 142 Ex21's hand-rolled sealed `Either` is a generic `L`; ours names each case.
5. **Optional as field/param.** No source conflicts — all agree (pl 121 methods Bad :354-365).
6. **Spring Security defaults vs our JWT / `PUBLIC_PATHS`.**
   - pl 304 Ex5 + Jeff java-architect/SKILL:124 assume an external IdP (`oauth2ResourceServer().jwt()` + `issuer-uri`). We mint and validate our own JWTs (`JwtService`). Not applicable; their "no hardcoded symmetric secret" (pl 304 R:179-181) still holds — master signs via `SecretKeyPort` (`JwtService.java:28-31`), no literal.
   - pl 304 Ex1/Ex3 (explicit matchers, `authenticated()` default, CSRF off only with `STATELESS`) — **master already matches**: `SecurityConfig.java:59-60` csrf off + STATELESS, `:77` `PUBLIC_PATHS` permitAll, `:82` `anyRequest().authenticated()`, `:22` `@EnableMethodSecurity`, `:91` frame deny.
   - pl 304 Ex7 wants a JSON 401 body; master uses `HttpStatusEntryPoint(UNAUTHORIZED)` (`SecurityConfig.java:62`) — empty body, not `ApiResponse`. Small inconsistency with ADR-0008, not a security hole (OQ).
   - pl 304 Ex6 `DelegatingPasswordEncoder` vs master `new BCryptPasswordEncoder(12)` (`AuthAutoConfiguration.java:18`) and a second `BCryptPasswordEncoder(10)` (`TriggerService.java:22`). Two cost factors for two secrets types (OQ).
   - Jeff refs default the JWT secret to a placeholder string (java-architect/refs/spring-security:421) — the anti-pattern pl 304 forbids. **Reject.**
7. **Testing stack (out of scope here, noted).** Jeff: MockMvc + `@MockBean` + H2 (`spring-boot-engineer/refs/testing:454`, SKILL:155-158); CLAUDE.md: RestTestClient, fake ports, Testcontainers. **Reject.**
8. **Jackson 2 in examples.** pl 124 R:719-720, pl 128 R:1464-1465 import `com.fasterxml.jackson.databind` — gated out by AT `no_jackson_2_imports_in_source`. Rules transfer; code examples do not.
9. **JPMS** pl 141 R:617-619 — rejected (R25).
10. **Builders/fluent DSLs** pl 121 object-creation:85-87, pl 122 R:449-451 vs our "no builders" — pl 123 java-design-patterns:110-112 itself says prefer record ctor/static factory for small values. Keep our edge; master has 0 builders.
11. **`Map<String,Object>` generic-until-specific** pl 144 R:431-433 vs SE5 fixed DTO. **Reject** for anything crossing a trust boundary.
12. **Pinning myth** adityamparikh ext:479-481 (`ReentrantLock` over `synchronized`) — stale since JEP 491 (Java 24); we are on 25. **Reject** (R25 CC1).
13. **Inline `Instant.now()`** in pl 141 R:312-335 Good example vs approved **U4** (inject `Clock`). U4 wins.
14. **Maven-only workflows** — every plinth SKILL mandates `./mvnw compile`/`clean verify`; our gate is `make verify` (Gradle behind it). Adopt the intent (compile before refactor, verify after) as `make`; never the commands.

## 4. mutation-testing (jvm) vs approved M1–M10

| M | verdict | evidence (MT = upstream SKILL.md line) |
|---|---|---|
| M1 report, never gate; threshold 0 | **conflicts** | MT:88-90 bootstraps mutation/coverage/test-strength thresholds at 60; MT:14 lists "CI gate on mutation score" as a use. M1 stands — we have no measured score and no CI. |
| M2 survivor = missing case, name the CORRECT/BICEP letter | **confirms (partly)** | MT:289-290 "spell out both behaviours … assert observable behaviour on a specific input". No CORRECT/BICEP naming — ours is stricter. |
| M3 score + test strength; NO_COVERAGE vs SURVIVED | **confirms** | MT:90 testStrength, MT:192 SURVIVED ≠ NO_COVERAGE ≠ TIMED_OUT |
| M4 exclude only no-decision code | **confirms** | MT:75-78 generated members, :358 generated classes, :64-74 logger calls |
| M5 compare per-class counts after changing exclusions | **confirms (adjacent)** | MT:68-69 "verified empirically: removing these re-introduces 7+ survivors"; MT:325 prefix glob over-matches |
| M6 DEFAULTS, never ALL | **conflicts on DEFAULTS** · confirms never ALL | MT:62, :362 use `STRONGER`. M6 stands until someone measures STRONGER on `aruvii-guardrails` (OQ). |
| M7 run after branching logic in guardrails; wire others first | **confirms + adds** | MT:135-154 scoped-on-diff run; empty scope aborts, never whole-codebase |
| M8 equivalent only with a stated reason; unsure = gap | **confirms** | MT:194-235 archetypes A-D, "bias toward ambiguity, not toward equivalence" (:235) |
| M9 don't trust `withHistory` | **conflicts in default** · confirms the risk | MT:85-86 turns history on; MT:361 then warns "a stale cache silently reports wrong results". M9 stands. |
| M10 kill test passes first run; prove with hand mutation | **confirms** (different proof) | MT:282, :292, :344 — inverted TDD; proof = scoped pitest rerun shows KILLED, not a hand mutation |

**New from MT, candidates only** (none required by our stack today):
1. **MN1** Verify a kill by three facts: target KILLED, no KILLED→SURVIVED in the class, killed count rose. — MT:332-336
2. **MN2** Reject a kill test that asserts the mutated operator or constant (tautology). — MT:290, :338
3. **MN3** Read `mutations.xml`, never the build exit code, for the verdict. — MT:332 (fits CLAUDE.md's "a green exit is not proof")
4. **MN4** Turn on `fullMutationMatrix` for a survivor investigation so each survivor names its covering test. — MT:83, :175

## 5. FINAL GROUPS for the operator (nothing approved)

Minimal set: R25's rules that survived, plus R27's new ones. Source = ours first, then the strongest
external. Pointers are `origin/master` `5fda6873`. Rules already gated (ArchUnit/Checkstyle) are marked
*gated* — a reviewer runs `make test ONLY=arch`, never re-checks by eye.

### code/java
1. Compute time in `Instant`/`Duration`; take an injected `Clock` (U4); convert to `Date`/zoned types only at a library boundary. — R25 JV1, pl 141 R:291 · **ADOPT** · Good `DataRetentionJob.java:78` · Bad `JwtService.java:56-57`
2. No `parallelStream()`/`.parallel()` in request- or queue-serving code. — R25 JV2, streams ext:115-128 · **ADOPT**
3. Streams compute; I/O, logging and mutation stay outside `map`/`filter`/`forEach`. — R25 JV3, pl 142 R:737-739, streams ext:266 · **ADOPT**
4. `final var` only when the right-hand side names the type (constructor, factory, literal). — R25 JV5, pl 141 R:457-505 · **ADAPT** (settles R25 contradiction 5 for SR T-05)
5. `Optional` is a return type only; consume with `map`/`orElse*`, never `isPresent()`+`get()`. — R25 JV6, pl 121 methods:354-365, pl 142 R:664 · **ADOPT**
6. Every `AutoCloseable` opened in a method is closed by try-with-resources. — R25 JV8, pl 126 R:192 · **ADOPT**
7. Multi-line SQL/JSON/prompt text is a text block. — R25 JV7, pl 141 R:911 · **ADOPT** (NIT)
8. Decided edge: no JPMS; boundaries are Gradle modules + AT allowlist. — pl 141 R:617 rejected · **ADOPT**
9. Braces on every block — **ADAPT** to Checkstyle `NeedBraces` (R25 JV9; no R27 source)
- **REJECT**: `toMap` comment rule as standalone (fold into #3's review check), whitespace, gatherers/laziness, JEP 513 teaching.

### code/types
1. No `null` decides a case: `Optional`, sealed interface + records, or enum. — RJ:14, pl 142 R:517 · **ADOPT** · Bad `GuardrailPipeline.java:42-49` (nullable optional tiers)
2. A closed set of ≥2 cases is sealed or an enum; its switch has no `default`. — R25 TY2, pl 142 R:463-519 · **ADOPT** · Good `AddMemberOutcome.java:13` · Bad `PromptBuilderController.java:236`
3. A record's compact constructor rejects every component combination the domain forbids. — R25 TY3, pl 126 R:2455 · **ADOPT**
4. Fields `final`; locals/params `final` in new code only. — R25 TY4, pl 121 classes-interfaces:153 · **ADAPT** (OQ2 open)
5. Money is `BigDecimal` with explicit scale/rounding. — R25 TY5, pl 122 R:670 · **ADOPT**
6. States/roles/modes are enums, persisted `EnumType.STRING`; never ordinals. — R25 TY6, pl 121 enums-annotations:113 · **ADOPT**
7. Collection-returning methods return empty, never `null`. — R25 TY7, pl 121 methods:231 · **ADOPT**
8. Wrap a primitive only when the wrapper states an invariant. — R25 TY8, pl 122 R:241 · **ADAPT**
9. Decided edges: nulls only in wire-DTO mapping; no builders (record ctor or static factory instead). — pl 123 java-design-patterns:110-112 · **ADOPT**
- **REJECT**: `Map<String,Object>` until specific (pl 144 Ex5), Lombok, accessor getters on records (pl 121 classes-interfaces:102).

### code/errors
1. A foreseeable non-success is a sealed outcome in the return type; only faults throw. — RJ:21-27, pl 143 R:218, pl 126 R:1559 · **ADOPT** · Good `AddMemberOutcome.java:13-23`
2. A fault throws `AruviiException` with a catalogue `ErrorCode`; no checked exceptions, no bare `ResponseEntity…build()`. — RJ:18-20, ADR-0008 · **ADOPT** (rejects pl 121/126 checked advice)
3. **N3** Exception→response mapping lives only in `GlobalExceptionHandler`; no per-controller `@ExceptionHandler`. — pl 126 R:2182 · **ADAPT** (14 controllers today — new code only) · Bad `AgentController.java:162-190`
4. **N2** Responses carry the `ErrorCode` message, never a library/driver/JDK `getMessage()`. — pl 124 R:526, pl 123 rest:114 · **ADOPT** · Bad `AgentController.java:189`
5. Chain the cause on rethrow; never an empty catch. — R25 ER3, pl 126 R:584, :1873 · **ADOPT** · Bad `ChatOrchestrator.java:226`
6. Catch the narrowest type; `catch (Exception)` only at a must-not-fail boundary with a comment; never `Throwable`. — R25 ER4, pl 126 R:2371 · **ADOPT**
7. `InterruptedException`: restore the flag or rethrow. — R25 ER5, pl 126 R:818 · **ADOPT** · Good `ChatStreamConsumer.java:197`
8. Validate request input at the boundary with Bean Validation. — R25 ER6, pl 124 R:23, Jeff spring-boot-engineer/SKILL:181 · **ADOPT**
9. Decided edges: no `Either`/VAVR; ApiResponse not ProblemDetail. — vs pl 143 R:24, pl 123 rest:44 · **ADOPT**

### code/functional (small — most functional rules live in code/java)
1. Async composition uses `thenApply`/`thenCompose`/`allOf`; no `join()`/`get()` mid-pipeline. — R25 CC6, pl 142 R:836-840 · **ADOPT**
2. Pure core, effects at the edge: a function computing a decision does no I/O. — pl 142 R:737-739, pl 144 R:24 · **ADAPT** (review heuristic, not a hard rule)
- **REJECT**: currying/partial application (pl 142 Ex15), monadic control flow (pl 143 Ex7), gatherers as a rule.

### code/design (OO + patterns)
1. Name the design pressure before adding a pattern; no strategy/factory/decorator for one stable implementation. — pl 123 S:27-28, java-design-patterns:44 · **ADOPT**
2. **LY2** Interface only when a test fakes it or it is a module boundary; single impl `Default<Name>`, package-private. — R25 LY2, pl 123 java-design-patterns:44 · **ADAPT** (OQ5)
3. Controllers bind, delegate, shape; outcome-choosing branches live in a service. — R25 LY1, pl 126 R:2182 · **ADOPT**
4. Two operations that must not split sit behind one method / one transaction at use-case level. — R25 LY3, pl 123 persistence:42 · **ADOPT**
5. **N4** Constructor injection only; optional collaborator via `ObjectProvider<T>`. — Jeff spring-boot-engineer/SKILL:180,189 · **ADOPT** · Good `AgentsAutoConfiguration.java:145` · Bad `GuardrailPipeline.java:42-49`
6. **N7** Never a JPA entity in `ApiResponse`, DTO or message payload. — pl 123 rest:43 · **ADOPT** as ArchUnit rule (0 violations today)
7. **N8** Grouped settings bind to a `@ConfigurationProperties` record. — Jeff spring-boot-engineer/SKILL:182 · **ADOPT** (NIT) · Good `PlatformConfigProperties.java:7`
8. *gated*: domain/shared purity, Spring AI only in worker, Jakarta, Jackson 3. — AT · **ADOPT** as gated
- **REJECT**: `final` on every non-inheritance class (CGLIB proxies), interface-per-service by default (pl 122 Ex8), builders, smell catalogue as rules (keep as examples).

### code/generics (new reference — R25 had none)
1. **N5** No raw types; `@SuppressWarnings("unchecked")` on one statement with the reason it is safe. — pl 128 R:61, :1504 · **ADOPT** · Good `GraphMailClient.java:85` · Bad `GraphMailClient.java:146`
2. Wildcards in parameters follow PECS (`? extends` read, `? super` write). — pl 128 R:132 · **ADAPT** (NIT, library-facing code only)
- **REJECT** as rules: CRTP, heterogeneous containers, `@SafeVarargs`, naming letters — teaching material.

### code/security
1. SQL binds parameters; dynamic identifiers come from a code allowlist. — R25 SE3, pl 124 R:134 · **ADOPT**
2. Untrusted JSON binds to a fixed record DTO; no default/polymorphic typing, no `Map<String,Object>` past the adapter. — R25 SE5, pl 124 R:709 · **ADOPT** · Bad `GraphMailClient.java:86` (adapter-local is the allowed exception — OQ)
3. URL fetch: http/https only through the checked-fetch type (#527). — R25 SE1, pl 124 R:23 · **ADOPT**
4. User-supplied paths: resolve, normalise, check `startsWith(base)`. — R25 SE4, pl 124 R:23 · **ADOPT**
5. Credentials AES-GCM via `CredentialEncryptor`; passwords BCrypt; no MD5/SHA-1/DES. — CM credentials block, pl 124 R:352 · **ADOPT** · Good `CredentialEncryptor.java:13`
6. Decrypt failure stops the call. — R25 SE2 · **ADOPT**
7. `[innerHTML]`/`bypassSecurityTrust*` only for code-controlled content. — R25 SE6, pl 124 R:758 · **ADOPT**
8. **N9** Never weaken a matcher, role or `PUBLIC_PATHS` entry to green a test. — pl 304 R:293 · **ADOPT**
9. Never log tokens, passwords or `Authorization` headers. — pl 304 R:294, pl 124 R:28 · **ADOPT** (merge with obs/logging LG4)
- **REJECT**: `issuer-uri` resource server (pl 304 Ex5), CORS rule (no cross-origin config exists), JWT secret defaults (Jeff).

### code/concurrency
1. Virtual threads for blocking I/O fan-out, never pooled; `synchronized` is fine on Java 25 (JEP 491). — R25 CC1, adityamparikh ext:473 · **ADAPT** · Good `RagIngestExecutorConfig.java:23`
2. Blocking async work gets an explicit, named executor — never no-arg `supplyAsync`/`runAsync`. — R25 CC2, pl 142 R:853 · **ADOPT** · Bad `HttpToolHandler.java:220`
3. Every remote call has a timeout that stops the work; `orTimeout` only abandons the future. — R25 CC3, pl 126 R:2286 · **ADOPT** · Bad `HttpToolHandler.java:220-221`
4. **N6** Retry only transient failures of idempotent calls, bounded, with jittered backoff, after a timeout exists. — pl 126 R:2233, pl 123 cross-cutting:92 · **ADOPT**
5. Bounded pool → bounded queue + stated rejection. — R25 CC4, pl 123 cross-cutting:149 · **ADOPT**
6. Shared mutable state has one owner; two locks only in one documented order. — R25 CC5, pl 142 R:953 · **ADOPT**
7. **N1** Call-scoped context is a `ScopedValue` or a parameter, never a new `ThreadLocal`. — adityamparikh ext:486 · **ADAPT** (new code; existing one OQ) · Bad `AgentNestingContext.java:12`

### obs/logging
1. Service entry INFO `action=<verb> key=value`. — RO:23 · **ADOPT** (no R27 source; ours)
2. Log a failure once, where handled; rethrow-with-cause does not log. — R25 LG2, pl 126 R:2110 · **ADOPT**
3. WARN = handled, class+message; ERROR = needs investigation, throwable last. — R25 LG3, pl 143 R:985 · **ADOPT**
4. No PII, prompts, tool args, secrets, tokens at INFO+. — R25 LG4, pl 124 R:28, pl 304 R:294 · **ADOPT**
5. Strip CR/LF from untrusted text in log lines. — R25 LG5 · **ADOPT** · Good `ToolService.java:226-228`
6. `{}` placeholders; `private static final Logger log`. — R25 LG6/LG8 · **ADOPT** (NIT)
7. Long calls log duration; scheduled jobs log tick + completion. — R25 LG7 · **ADOPT**

### obs/metrics + tracing
Unchanged from R25 G-H (MX1–MX4, TR1–TR3, decided edges) — R27 sources add only TR1 confirmation (pl 123 cross-cutting:119). **ADOPT** as R25.

### code/messaging
Unchanged from R25 G-J (MS1–MS5); pl 123 kafka:42-45 confirms MS3/MS4. **ADOPT** as R25.

### testing/mutation (candidates beside M1–M10)
MN1–MN4 (§4) — **ADAPT** MN1+MN3 into `testing/references/mutation.md`; MN2 folds into M2; MN4 NIT.

## 6. Open questions

| # | decide | facts |
|---|---|---|
| OQ-R27-1 | Is N3 (one exception handler) worth a migration of the 14 controllers with local `@ExceptionHandler`, or new-code only? | `AgentController.java:162-190` also leaks a DB message (N2) — that one is a bug either way |
| OQ-R27-2 | Replace `AgentNestingContext`'s ThreadLocal with `ScopedValue` (final in Java 25)? | hand-propagated across `supplyAsync` at `AgentToolHandler.java:76-82`; works today, breaks if a hop forgets the copy |
| OQ-R27-3 | Is `Map<String,Object>` allowed *inside* an outbound adapter (Graph, MCP) if it never leaves it? | `GraphMailClient.java` 11 unchecked suppressions; SE5 as written forbids it only for untrusted *input* |
| OQ-R27-4 | 401 body: keep empty `HttpStatusEntryPoint` or return `ApiResponse.error` like every other error? | `SecurityConfig.java:62`; pl 304 Ex7 wants JSON |
| OQ-R27-5 | Two BCrypt cost factors (12 users, 10 trigger secrets) — intended? Move to `DelegatingPasswordEncoder`? | `AuthAutoConfiguration.java:18`, `TriggerService.java:22`; pl 304 Ex6 |
| OQ-R27-6 | NullAway/JSpecify — still rejected (R25), or the gate for TY1 "no null decides"? | adityamparikh ext:203-238; R25 rejected `@NullMarked` everywhere; no gate behind TY1 today |
| OQ-R27-7 | M6 DEFAULTS vs upstream STRONGER — measure on `aruvii-guardrails` before changing? | MT:62 vs M6; M1 keeps it a report either way |
| OQ-R27-8 | R25 OQ4 (validation/auth log level) — sources lean INFO (pl 126 R:2127; pl 143 R:985). Accept code over RO:16? | `GlobalExceptionHandler` INFO today |

## 7. What was read

| source | depth |
|---|---|
| pl 121 SKILL + 8 refs | SKILL full; every Role/Goal/Constraints + every example title; bodies of exceptions Ex3/Ex6, object-creation Ex3, classes Ex3/Ex6, methods Ex6 (+Bad), principles Ex9 |
| pl 122, 124, 126, 128, 141, 142, 143, 144, 304 | SKILL full; principles + constraints full; every example title; bodies of cited examples (122 Ex4/8/12; 123 constraints ×5, Ex1/2, cross Ex2, rest Ex3; 124 Ex4/5/7 + safeguards; 126 Ex7/8/13/14/16/17/19; 128 Ex14/15; 141 Ex4/6; 142 Ex6/19/21; 143 Ex2/3/5; 304 all 8) — **not every example body** |
| pl 123 SKILL + 5 refs | as above |
| jvm `framework/*.yaml` (15), `language/*.yaml` (9) | full |
| jvm `testing/mutation-testing.yaml` + upstream `.claude/skills/mutation-testing/SKILL.md` | full |
| upstreams of spring-boot.yaml, streams-java.yaml, logging-patterns-java.yaml | via corpus extractions (`~/workspace/claude/analysis/skills-analysis/docs/extractions/`), targeted lines — not the upstream repos |
| Jeff `java-architect`, `spring-boot-engineer` | SKILL full; refs: headings + targeted greps (Lombok, ProblemDetail, MockBean, H2, secrets) + spring-boot-setup:216-257 |
| agent-platform `origin/master` `5fda6873` | targeted `git grep`/`show` for every pointer cited |
