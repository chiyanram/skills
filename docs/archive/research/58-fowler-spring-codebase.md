# R36 · Fowler's smells and refactorings + how Spring's own code is written (#83 → #33 G9b)

Question (#83): what do Martin Fowler's own works and Spring's own codebase teach about well-shaped code, and which of it
should become (or sharpen) our rules — SEAM1 / ADR-0017 S-1..S-7, DS*, NM*, LY*, SC*, TY*, ER*?

Nothing here enters a reference without the operator's yes. Candidates are in §5 and `review/r36.json`.

**Legend.** `MF/<Page>` = https://martinfowler.com/bliki/<Page>.html (fetched 2026-10-03) · `MF-art/<x>` =
https://martinfowler.com/articles/<x> · `RC/<x>` = https://refactoring.com/catalog/<x>.html · `RK` =
rameezk/skills@937d90d `skills/code-review/martin-fowler-code-smells.md` · `SF` = spring-projects/spring-framework@69a298b8e ·
`SB` = spring-projects/spring-boot@f6142c9f4 · `SJF` = spring-io/spring-javaformat@525867fe8 · `ADR17` = agent-platform
`origin/docs/593-turn-journal-adr:docs/adr/0017-turn-journal-and-replay.md` · `AP` = agent-platform `origin/master`@772736bf
(evidence of violations only, SRC1) · ledger = `research/19-approved-rules.md`. `…/` in AP paths = `src/main/java/ai/aruvii/`.

---

## 1. The sources — why each is strong and how it is built

| Source | Why it carries weight | How it is built | Limits found |
|---|---|---|---|
| Fowler bliki (`MF/CodeSmell`, `TellDontAsk`, `AnemicDomainModel`, `GetterEradicator`, `FunctionLength`, `CommandQuerySeparation`, `FlagArgument`, `DataClump`, `InterfaceImplementationPair`, `RoleInterface`, `HeaderInterface`, `FluentInterface`, `ValueObject`, `BeckDesignRules`, `Yagni`, `ParallelChange`, `StranglerFigApplication`) | The author of the smell vocabulary, writing in his own voice; each page states a position *and its exceptions* | Short essays: a definition, one worked example, then "but" — the trade-off. E.g. `MF/CodeSmell` ¶2: "smells don't always indicate a problem"; `MF/TellDontAsk` ¶6: "personally, I don't use tell-dont-ask" | Every page is a heuristic with an escape hatch; none gives a number except `MF/FunctionLength` ("more than half-a-dozen lines … starts to smell") |
| `RC/` catalog (https://refactoring.com/catalog/) | The 2nd-edition refactoring names, first-party | One card per refactoring: name, aliases, before/after sketch. Motivation text sits in the paid web edition ("How do I access the web edition?" on every card, e.g. `RC/removeMiddleMan`) | **The smells chapter (Refactoring 2e ch. 3) is not on any public first-party page.** `MF-art/refactoring-2nd-changes.html` ¶3 only says the smells chapter "had a thorough overhaul … about three-quarters of it changed". So smell→cure pairs below are built from catalog names + bliki, not quoted from the book |
| `MF-art/injection.html` §Constructor versus Setter Injection | Fowler's DI article — the one Spring's own docs grew up beside | Argued trade-off: constructor first, setter when it hurts | Says "create multiple constructors" for valid-object combinations — written for objects in general, not Spring beans |
| `RK` | The baseline SEAM1 and ADR17:221-225 cite | 21 lines: two binding rules (`RK:5` repo overrides; `RK:6` always a judgement call, skip what tooling enforces) then 12 smells, one line each, "what it is → how to fix" (`RK:10-21`) | Claims "Martin Fowler's catalogue (_Refactoring_, ch.3)" (`RK:3`) but lists 12 of the chapter; see §2.1 |
| SF `CONTRIBUTING.md` §Source Code Style (:225-662) | The rules Spring's own committers are held to; "Many of these rules are enforced at build time by Checkstyle" (:229) | Based on Google Java Style (:228); each rule short, many with the Checkstyle id that enforces it | Library-oriented (javadoc `@since`, public API stability) — not all of it fits an application |
| SF `src/checkstyle/checkstyle.xml` (287 lines) + SJF `spring-checkstyle.xml` + SB `config/checkstyle/checkstyle.xml` (106 lines) + SB `import-control.xml` | What Spring actually *gates*, not what it hopes for | Boot pulls in SJF's `SpringChecks` (SB checkstyle.xml:9-13) and adds banned imports + regex checks; FW lists modules directly | Spring gates **nesting depth**, never cyclomatic complexity (no `CyclomaticComplexity` module in any of the three) |
| SF / SB sample classes (`RestClient`, `DefaultRestClient`, `DefaultRestClientBuilder`, `RetryPolicy`, `ObjectProvider`, `Assert`, `RestClientAutoConfiguration`, `RestClientCustomizer`, `RestClientBuilderConfigurer`, `ThreadPoolTaskExecutorBuilder`, `TaskExecutorConfigurations`, `HealthContributor`) | Shows the house style applied, including where Spring breaks its own ideals | Pattern: public interface + static factories + package-private `final` `Default*` impl; `*Customizer` callbacks applied by a configurer | Spring's core is **not** small classes: `DefaultListableBeanFactory.java` 2813 lines, `AbstractAutowireCapableBeanFactory.java` 2072, `RestClient.java` 1159 (SF, `wc -l`). Do not cite Spring for "small classes" |
| SF null-safety reference (https://docs.spring.io/spring-framework/reference/core/null-safety.html) | First-party JSpecify policy | §Defaults to non-null (`@NullMarked` in `package-info.java`), §Explicit nullability, §Configuration (NullAway `OnlyNullMarked=true`) | Spring returns `@Nullable T`, not `Optional` (SF `ObjectProvider.java:120` `default @Nullable T getIfAvailable()`) |

## 2. Fowler smell → cure → our rule

### 2.1 Does the rameezk baseline match Fowler?

**Names: yes, as far as public pages can check. Coverage: it is a 12-smell subset, not "the catalogue".**

| Check | Finding |
|---|---|
| Names | `RK` uses 2nd-edition names (Mysterious Name, Repeated Switches, Message Chains). Not verifiable line-by-line against ch. 3 (unpublished online) |
| Cures | Each `RK` cure maps to a real `RC/` refactoring (table 2.2). Two `RK` additions are not Fowler's: Repeated Switches "or one map both sites share" (`RK:15`) and Speculative Generality "inline back until a real need shows" (`RK:18` — Fowler's catalog has Inline Function / Inline Class / Collapse Hierarchy, `RC/` :65-67,:48) |
| Missing, verifiable online | **Long Function** — `MF-art/refactoring-video-store-js/` ("The statement function is an example of the smell Long Method"), `MF/FunctionLength`. **Long Parameter List / over-busy constructor** — `MF-art/injection.html` §Constructor versus Setter ("a long constructor is often a sign of an over-busy object that should be split"). **Data Class** — `MF/CodeSmell` ¶3 ("Data classes … good examples"), `MF/GetterEradicator` ("almost always a sign of trouble") |
| Missing nuance | `RK` lists Message Chains (cure: hide the walk, `RK:19`) and Middle Man (cure: cut it, `RK:20`) with no warning that the cures are inverses — `RC/removeMiddleMan`: "inverse of Hide Delegate" |
| Binding rules | `RK:5-6` match Fowler's own framing: smells are "an indicator of a problem rather than the problem" (`MF/CodeSmell` ¶2) |

### 2.2 Smell → cure → our rule

| Smell (Fowler source) | Fowler cure (`RC/` name) | Our rule | Verdict |
|---|---|---|---|
| Mysterious Name (`RK:10`) | Change Function Declaration, Rename Variable/Field | NM1, NM2 | confirms |
| Duplicated Code (`RK:11`; `MF/BeckDesignRules` "No duplication … Once and only Once") | Extract Function, Slide Statements | DS12, DS14 | confirms; Beck rule order note (`MF/BeckDesignRules`: "reveals intention" vs "no duplication" tension) is DS14's judgement line |
| Feature Envy (`RK:12`) | Move Function | DS11 | confirms |
| Data Clumps (`MF/DataClump`: "start and end … a data clump wanting to be a range") | Introduce Parameter Object, Extract Class | DS11, TY8 | confirms; AP `aruvii-tools/…/tools/domain/Tool.java:60` constructor with 29 params |
| Primitive Obsession (`RK:14`) | Replace Primitive with Object | TY8, ADR17:223 (`RunId`) | confirms |
| Repeated Switches (`RK:15`) | Replace Conditional with Polymorphism | DS3, TY2, S-4 | **sharpens**: S-4 deliberately keeps exhaustive switches over sealed results; Fowler's cure is polymorphism. Not a contradiction: the smell is the *same* switch repeated; one switch per seam boundary is S-4's design. State it in DS11 |
| Shotgun Surgery / Divergent Change (`RK:16-17`) | Move Function/Field, Combine Functions into Class, Split Phase | DS11, S-1 ("one reason to change") | confirms |
| Speculative Generality (`RK:18`; `MF/Yagni`: "any abstraction that makes it harder to understand the code for current requirements is presumed guilty") | Inline Function/Class, Collapse Hierarchy, Remove Dead Code | DS6, S-7 | confirms |
| Message Chains (`RK:19`) | Hide Delegate | DS11 | **sharpens** — inverse of Remove Middle Man |
| Middle Man (`RK:20`) | Remove Middle Man | DS4, S-7 | confirms; same inverse note |
| Refused Bequest (`RK:21`) | Replace Subclass/Superclass with Delegate | DS11 | confirms |
| **Long Function** (`MF/FunctionLength`: extract when "you have to spend effort … to figure out what it's doing", name it "after that 'what'") | Extract Function | S-6 (complexity ≤5), DS2 (file size) | **gap** — no rule on *method* length/intent; AP `aruvii-worker/…/worker/chat/ChatOrchestrator.java` 1405 lines → FW5 |
| **Long Parameter List / over-busy object** (`MF-art/injection.html` §Constructor versus Setter) | Extract Class, Introduce Parameter Object, Preserve Whole Object | none | **gap** → FW1; AP `ChatOrchestrator.java:133` constructor takes 32 params; 57 constructors in AP main take ≥7 |
| **Data Class / anemic** (`MF/GetterEradicator`, `MF/AnemicDomainModel`) | Move Function, Encapsulate Record | none; S-3 pushes decisions into pure policy classes | **gap + tension** → FW6, contradiction X5 |
| Flag Argument (`MF/FlagArgument`: "My general reaction to flag arguments is to avoid them") | Remove Flag Argument | DS3 (no second boolean in a flow) | **gap** for method signatures → FW2; AP `aruvii-tools/…/tools/rag/RagIngestionService.java:72` `ingest(…, boolean forceReembed)` used at :94 |
| Query that modifies (`MF/CommandQuerySeparation`; `RC/separateQueryFromModifier`) | Separate Query from Modifier | NM3 (getter-shaped name never writes) | **sharpens** → FW3 |

### 2.3 Other Fowler positions that bear on seams

| Page | Position (quoted, short) | Bears on |
|---|---|---|
| `MF/InterfaceImplementationPair` | "Using interfaces when you aren't going to have multiple implementations is extra effort"; published libraries differ | S-1, LY2 → X3 |
| `MF/RoleInterface` | "only use interfaces when you really need substitutability, and … think hard about what the consumer of that interface needs"; role interfaces follow ISP, header interfaces do not | S-1 → FW7 |
| `MF/ParallelChange` | expand → migrate → contract; "Even when you have control over all usages … still useful" | DS5 → X4, FW4 |
| `MF/StranglerFigApplication` | gradual replacement of a legacy system | context only (large modernisation, not a review rule) |
| `MF/TellDontAsk` / `MF/GetterEradicator` | Beck's rule: "beware of cases where some code invokes more than one method on the same object"; "things that change together should be together"; "Layering often trumps this" | FW6 |
| `MF/FluentInterface` | modifiers returning `this` suspend CQS — "I'm inclined to suspend the convention for this case" | FW3 exception; TY13 |
| `MF/ValueObject` | "value objects should be immutable" (aliasing bugs) | TY4, records — confirms |

## 3. Spring's own codebase → our rule

| Spring pattern (cite) | What it is | Our rule | Verdict |
|---|---|---|---|
| Public interface + static factories + package-private `final` `Default*` (SF `RestClient.java:84` `public interface RestClient`, :149-200 `static create()/builder()`, :231 nested `interface Builder`; `DefaultRestClient.java:86` `final class DefaultRestClient`; `DefaultRestClientBuilder.java:64` `final class`) | Callers see only the interface; the impl cannot be named or subclassed | S-1, LY2 | **confirms + sharpens**: impl is `final`. AP `aruvii-api/…/api/eval/DefaultAgentEvalPublisher.java:16` is `class` (not final); `aruvii-worker/…/worker/llm/LlmAdapterRegistryImpl.java:15` is `public class …Impl` (TY13 bans `Impl`) → SP13 |
| Public method in package-private class only if it overrides (SJF `SpringMethodVisibilityCheck.java:53-67`, wired via `SpringChecks`, SB checkstyle.xml:9) | Visibility can't be widened by accident | none | **new** (cheap gate) → SP14. AP scan found 0 violations |
| Strategy interface as a pure decision with static factories (SF `RetryPolicy.java:48`, :56 `boolean shouldRetry(Throwable)`, :98/:114/:123 `withDefaults()/withMaxRetries()/builder()`) | Decision = one method, no I/O | S-3 | confirms (Spring returns `boolean`; S-2's sealed result is stricter — keep ours) |
| `*Customizer` callbacks (SB `RestClientCustomizer.java` `@FunctionalInterface … void customize(RestClient.Builder)`); applied in order by a configurer (SB `RestClientAutoConfiguration.java:85` `customizerProvider.orderedStream().toList()`; `RestClientBuilderConfigurer.java:63-73`) | Many modules adjust one builder without knowing each other | S-5 (ordered rule list) | **confirms** S-5's shape (list of small functions applied in order). AP has 0 own `*Customizer` types — no current need → SP16 HOLD |
| Auto-configuration class `public final`, `@Bean` methods package-private, nested `static class … @Configuration(proxyBeanMethods = false)` (SB `RestClientAutoConfiguration.java:60,62-93,95-97`) | | SC5, SC6 | confirms (already approved) |
| `ObjectProvider` for optional/many collaborators, resolved in the factory (SB `RestClientAutoConfiguration.java:65-85`) | | LY6, SC2 | confirms |
| Immutable builder — each setter returns a new instance (SB `ThreadPoolTaskExecutorBuilder.java:48-70` all `private final`, :110-111 `return new ThreadPoolTaskExecutorBuilder(…)`) | | TY13 bans builder classes | **contradicts** TY13 for library-style config objects → X2 |
| Sealed types in new API (SB `HealthContributor.java:28` `public sealed interface HealthContributor permits HealthIndicator, CompositeHealthContributor`) | Boot 4 adopts sealed for closed hierarchies | TY2, S-2 | confirms |
| `@NullMarked` per package + `@Nullable` type-use + NullAway in build (SF CONTRIBUTING.md:494-560; null-safety ref §Defaults to non-null, §Configuration) | Null contract checked by the compiler | TY1, TY12, OQ-R27-6 (NullAway spike) | **sharpens** OQ-R27-6; AP has 0 `package-info.java` among 1020 main files, 0 `@NullMarked` → SP15 |
| Preconditions: `Assert.notNull(x, "X must not be null")` (SF CONTRIBUTING.md:470-492; `DefaultRestClientBuilder.java:124,153`) | Message names the parameter first | ER6 (`requireNonNull` for programming errors) | **sharpens** message form only; Spring `Assert` must not enter `domain/` (LY4). AP: 4 `requireNonNull` without message vs e.g. `aruvii-infra/…/RedisModelOverrideStoreAdapter.java:47` `"sessionId"` → SP20 |
| No `var` in main code (SF CONTRIBUTING.md:594-598) | | ST1, JV5 (`final var` approved) | **contradicts** → X1 |
| `@PostConstruct` banned in Boot main code (SB checkstyle.xml:27-35 `mainCodeIllegalImportCheck` illegalClasses `jakarta.annotation.PostConstruct`) — the file gives no reason | | SC18 allows narrow `@PostConstruct` | **contradicts / tightens** → X6, SP23. AP: 5 live uses, e.g. `aruvii-api/…/api/chat/ChatResponseSubscriber.java:44`, `aruvii-worker/…/worker/trigger/KafkaTriggerManager.java:59` |
| Nesting gates, not complexity: `NestedIfDepth` max 5 (SF checkstyle.xml:73-75) / max 3 (SJF spring-checkstyle.xml:60-62, used by Boot), `NestedForDepth` 3, `NestedTryDepth` 3 | | S-6 says "Checkstyle `CyclomaticComplexity`"; DS9 nesting is review-only | **sharpens** → SP22. AP `checkstyle.xml:22-70` has **neither** `CyclomaticComplexity` nor any `Nested*Depth` — S-6's "checked by" column is not true on master |
| No `System.out/err`, no `printStackTrace()` in main (SF checkstyle.xml:226-237) | | none (OBS rules cover logging) | **new gate** → SP19. AP `aruvii-tools/…/tools/rag/HashEmbeddingAdapter.java:35` `System.err.println`; `aruvii-platform/…/platform/tools/LicenseGenerator.java:20-45` (a CLI `main`, legitimate) |
| Utility class: `abstract`/`final`, private ctor, `*Utils` (SF CONTRIBUTING.md:572-587; `HideUtilityClassConstructor`, `FinalClass` SF checkstyle.xml:47-49) | | none | **new gate (minor)** → SP18. AP `aruvii-worker/…/worker/llm/AdapterHttpHelper.java:26,30` already `final` + private ctor |
| Import control: foundation packages may not import the root (SB import-control.xml, e.g. `<subpackage name="util"><disallow pkg="org.springframework.boot" exact-match="true"/>`) | Layering in the build | LY4 (ArchUnit) | confirms mechanism; no change |
| "A file should look like it was crafted by a single author, not like a history of changes" (SF CONTRIBUTING.md:450-453); member order (:297-315) | | DS7 (dead code) | adjacent; → SP24 (drop recommended) |

## 4. Seam guidance vs SEAM1 / S-1..S-7 (ADR17:208-225)

| S-rule | Fowler | Spring codebase | Net |
|---|---|---|---|
| S-1 one job, `Default*` package-private | `MF/RoleInterface` agrees on narrow consumer-shaped interfaces; `MF/InterfaceImplementationPair` **disagrees** with an interface per class | Interface + `final` `Default*` — but for *published* library APIs, the case Fowler exempts | Sharpen: `final`; interface only where LY2 allows (X3) |
| S-2 record in, sealed out | `MF/ValueObject` immutability; `MF/FlagArgument` (no boolean deciding a case) | Spring uses `boolean`/`@Nullable`, sealed only in new Boot 4 API | Ours is stricter; keep |
| S-3 decide or do | `MF/CommandQuerySeparation` (queries free of side effects) agrees; `MF/AnemicDomainModel` warns against all-logic-in-services | `RetryPolicy` = pure decision | Keep; add FW6 so records still own their own invariants (X5) |
| S-4 seams chain by exhaustive switch | Repeated Switches is a smell only when the *same* switch recurs | Spring chains by composition / ordered lists | Keep; state the Repeated Switches carve-out in DS11 |
| S-5 rule lists | — | `*Customizer` + `orderedStream()` is the same shape | confirms |
| S-6 Java 25, complexity ≤5 | `MF/FunctionLength`: ~6 lines; extract by intent | Gates nesting depth, not complexity | Sharpen: actually wire the gate (SP22) |
| S-7 earn the seam | `MF/Yagni`, Remove Middle Man | — | confirms; add the Hide-Delegate inverse note (FW8) |

## 5. Candidate rules

Ids: **FW** = Fowler. **SP** collides with approved testing rules SP1-SP12 (ledger :71-82), so Spring-codebase candidates
are numbered **SP13+** to keep the prefix the brief asked for without reusing an id (see D4).

| Id | Rule (imperative, ≤30 words) | Source | Our state (evidence) | Recommend |
|---|---|---|---|---|
| FW1 | A constructor taking more than 7 collaborators is a finding: split the class (Extract Class) or bundle travelling values (Introduce Parameter Object). | `MF-art/injection.html` §Constructor versus Setter Injection; `MF/DataClump` | `ChatOrchestrator.java:133` 32 params; `Tool.java:60` 29; 57 ctors ≥7 in AP main | ADOPT (threshold is ours — D1) → smells.md |
| FW2 | A boolean parameter that selects which operation runs is a finding: split into two named methods, or take a sealed/enum input. | `MF/FlagArgument` §Tangled Implementation, §Deriving the flag | `RagIngestionService.java:72,94` `forceReembed`; DS3 covers flows, not signatures | ADOPT → smells.md (beside DS3) |
| FW3 | A method that returns a value changes no observable state; a modifier returning its own outcome (CAS `Won`/`Lost`) or a fluent `this` is the stated exception. | `MF/CommandQuerySeparation`; `RC/separateQueryFromModifier`; `MF/FluentInterface` | NM3 covers names only | SHARPEN NM3 |
| FW4 | Change a published contract (stream payload, DB column, public API) by expand → migrate → contract across releases; in-repo-only APIs keep DS5 (one change). | `MF/ParallelChange` | DS5 forbids dual paths everywhere; no rule for wire/DB contracts | ADOPT as DS5 scope note (X4) |
| FW5 | Extract a fragment you must read to understand into a method named for what it does; a comment explaining *what* is the cue. | `MF/FunctionLength` ¶1-3 | No method-level rule; `ChatOrchestrator.java` 1405 lines | ADOPT → smells.md |
| FW6 | When callers read two or more fields of one record to compute or check something, move that logic onto the record as a method. | `MF/GetterEradicator` (Beck's rule); `MF/TellDontAsk`; `MF/AnemicDomainModel` | not measured; tension with S-3 (X5) | ADOPT, scoped to records/values (not entities) |
| FW7 | An interface declares only the methods its consumer calls; a port whose consumers each use a different subset is split into role interfaces. | `MF/RoleInterface`; `MF/HeaderInterface` | 5 ports with 8-9 methods, e.g. `aruvii-shared/…/shared/llm/InteractionPort.java`; consumer use not checked | ADOPT as SEAM1/S-1 sharpening |
| FW8 | Hide Delegate and Remove Middle Man are inverses: fix a chain or a pass-through by whichever removes coupling at real call sites; never add a wrapper then flag it. | `RC/removeMiddleMan` ("inverse of Hide Delegate"), `RC/hideDelegate` | `RK:19-20` list both, no note; AP: 0 three-getter chains in main | SHARPEN DS11/DS4 |
| FW9 | Add Long Function, Long Parameter List and Data Class to the review smell baseline; note it is a 12-smell subset of Refactoring 2e ch. 3. | §2.1 | SEAM1 + ADR17:221-225 cite `RK` as "the Fowler smells baseline" | SHARPEN SEAM1/DS11 text |
| SP13 | A seam's Spring implementation is `final` and package-private; callers get it as the interface; no `Impl` suffix. | SF `DefaultRestClient.java:86`, `DefaultRestClientBuilder.java:64`, `RestClient.java:84` | `DefaultAgentEvalPublisher.java:16` not final; `LlmAdapterRegistryImpl.java:15` public `Impl` | SHARPEN S-1/LY2 |
| SP14 | In a package-private class, a method is `public` only when it overrides; gate it with SJF `SpringMethodVisibilityCheck` or ArchUnit. | SJF `SpringMethodVisibilityCheck.java:53-67` | AP scan: 0 violations | ADOPT as gate (OQ3), low priority |
| SP15 | Every main package has `package-info.java` with `@NullMarked`; a nullable type says `@Nullable` (JSpecify); NullAway checks it. | SF CONTRIBUTING.md:494-560; FW null-safety §Defaults to non-null, §Configuration | 0 `package-info.java` / 1020 main files; 2 files import `org.jspecify` | HOLD — fold into the OQ-R27-6 spike (D3) |
| SP16 | When several modules must adjust one shared builder, each contributes a `@FunctionalInterface *Customizer` bean; the owner applies them via `orderedStream()`. | SB `RestClientCustomizer.java`, `RestClientAutoConfiguration.java:85`, `RestClientBuilderConfigurer.java:63-73` | 0 own customizers; no current need | HOLD (DS6: no pattern before pressure) |
| SP18 | A static-only class is `final` with a private constructor; gate `HideUtilityClassConstructor` + `FinalClass`. | SF CONTRIBUTING.md:572-587; SF checkstyle.xml:47-49 | `AdapterHttpHelper.java:26,30` already compliant | ADOPT as gate (OQ3) |
| SP19 | No `System.out`, `System.err` or `printStackTrace()` in main code, except a `main` method; gated by Checkstyle regex. | SF checkstyle.xml:226-237 | `HashEmbeddingAdapter.java:35` | ADOPT as gate |
| SP20 | A precondition message names the parameter first: `requireNonNull(sessionId, "sessionId must not be null")`. | SF CONTRIBUTING.md:470-492 | 4 `requireNonNull` without message; `RedisModelOverrideStoreAdapter.java:47` bare name | SHARPEN ER6 (optional) |
| SP21 | (proposed) Config-style objects use an immutable builder whose setters return a new instance. | SB `ThreadPoolTaskExecutorBuilder.java:110-111` | TY13 bans builders | DROP — TY13 stands (X2) |
| SP22 | Wire the S-6/DS9 gates: Checkstyle `CyclomaticComplexity` max 5 and `NestedIfDepth` set so DS9 (three levels) fails the build. | SF checkstyle.xml:70-78; SJF :57-65; ADR17:218 | AP `checkstyle.xml` has neither | ADOPT (S-6 claims a gate that does not exist) |
| SP23 | No `@PostConstruct` in main code; startup checks go in the constructor, start-up work in `ApplicationRunner`/`SmartLifecycle` (SC19, SC20). | SB checkstyle.xml:27-35 | 5 live uses (`ChatResponseSubscriber.java:44`, `RagIngestSubscriber.java:55`, `GlobalTrustStore.java:56`, `JdbcSslAdapter.java:36`, `KafkaTriggerManager.java:59`) | DECIDE (X6, D2) |
| SP24 | (proposed) Place a new member beside related ones; a file reads as written by one author, not as change history. | SF CONTRIBUTING.md:450-462 | — | DROP — taste, not checkable |

## 6. Contradictions with approved rules — flagged

| # | Approved rule | Source says | Recommendation |
|---|---|---|---|
| **X1** | ST1 / JV5: `final var` for locals | SF CONTRIBUTING.md:596: "`var` … is not permitted" in main code | **Keep ours.** Spring is a library read on GitHub without an IDE; ours is an app; JV5 already limits `var` to types visible on the right. Record the divergence |
| **X2** | TY13: no builder classes | Spring builds config objects with builders (SF `RestClient.java:231`, `RetryPolicy.java:123,148`; SB `ThreadPoolTaskExecutorBuilder.java`) | **Keep TY13** for our values; add one line: *using* a library's builder is fine, we don't write our own |
| **X3** | S-1 (each seam an interface + `Default*`) vs LY2 (interface only for a faked boundary or module boundary) | `MF/InterfaceImplementationPair`: dislikes one-impl interfaces in applications; Spring's pairs are published library APIs | **Reconcile in S-1 text:** pure decision seams (`RecoveryPolicy`) are `final` classes with no interface; I/O seams get the interface (they are faked). 57 of 67 AP `*Port` interfaces have exactly one main impl — allowed by LY2 as module boundaries |
| **X4** | DS5: migrate every caller and delete the old path in one change | `MF/ParallelChange`: expand/migrate/contract "still useful" even with control of all usages | **Scope DS5** to in-repo APIs; FW4 for published/persisted contracts |
| **X5** | S-3 decide-or-do (decisions in pure policy classes over records) | `MF/AnemicDomainModel`: behaviour-less domain objects are an anti-pattern; but `MF/GetterEradicator`: "Layering often trumps this" | **Tension, not conflict.** Keep S-3 for cross-object decisions; FW6 keeps single-record logic on the record |
| **X6** | SC18: `@PostConstruct` allowed for checks / in-memory setup | SB bans the import in its own main code (checkstyle.xml:27-35); no reason given in the file | Operator choice (D2) |

## 7. Open decisions

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | FW1 threshold | a) 5 · b) 7 · c) no number, review judgement | **b) 7** — no first-party number exists; 7 flags the 57 worst AP constructors and leaves ordinary services alone |
| D2 | `@PostConstruct` (X6) | a) keep SC18 · b) ban in main via Checkstyle, migrate 5 uses (#663-style ticket) | **b)** — SC18's allowed cases fit in a constructor; Boot itself gates it; SC19/SC20 already name the replacements |
| D3 | JSpecify (SP15) | a) adopt now · b) fold into OQ-R27-6 spike · c) drop | **b)** — the spike is already approved; add "`@NullMarked` package-info on the spiked module" to its scope |
| D4 | Id prefix for Spring-codebase rules | a) SP13+ (shares prefix with testing SP1-SP12) · b) new prefix `SX` | **a)** for this review; rename to `SX` if the operator wants prefixes to mean one file |
| D5 | Where FW rules live | a) smells.md (DS11 family) · b) design.md beside SEAM1 | **a)** FW1/2/5/6/8/9 → smells.md; FW3/FW7 → design.md (seam rules) |
