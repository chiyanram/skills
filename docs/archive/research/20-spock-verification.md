# R16 — Spock best practices: verification against primary sources (2026-10-02)

Ticket: `issues/31-research-spock-best-practices.md`. Nothing here is approved. Rules in section 3 go to the operator one at a time.

**Sources**
- `DOC/x` = Spock docs at tag `spock-2.4`: `github.com/spockframework/spock/blob/spock-2.4/docs/x.adoc`, rendered at `spockframework.org/spock/docs/2.4/x.html`.
- `SK` = `/Users/chiyanram/.claude/skills/synced/408dc477-…/spock-best-practices`.
- `RULE` = `origin/master:.claude/rules/it-testing.md`.
- `PROBE` = a scratch spec run on this machine against `spock-core-2.4-groovy-5.0` and `groovy-5.0.8`, the jars this repo resolves. It lives in the session scratchpad, not in the repo.

## 1. Claims checked

### 1a. Our five rules (`RULE` lines 15-60)

| # | Claim | Verdict | Source | Note |
|---|---|---|---|---|
| R1 | A mock-argument closure checks only its last expression; use `assert` and end with `true` | **WRONG since Spock 1.3** | DOC/release_notes:946-993 · DOC/interaction_based_testing:249-250 · PROBE P1 | Every top-level line of a code constraint is an implicit assertion. In PROBE P1 the first line was false and the last true, and the run failed with `TooFewInvocationsError`. `assert` and `true` are harmless but not needed. What is still true: nested closures such as `.every{}` are not asserted (release_notes:557). |
| R2 | Every acceptance criterion maps to a file in the diff | N/A (process rule, not about Spock) | — | Belongs with the MR/DoD rules, not in spock.md. |
| R3 | "Every query" means count the queries | N/A (process rule) | — | Same as R2. |
| R4 | No bare `given:`/`when:`/`then:`/`expect:`, because the console report prints the description | **Rationale UNSUPPORTED** | DOC/spock_primer:791-830 · DOC/release_notes (2.0: `SpockReportingExtension` disabled) | Spock documents block texts as optional documentation. JUnit Platform display names do not include them. Keep the rule only on a readability reason. |
| R5a | Feature names read as sentences | CONFIRMED | DOC/spock_primer:134 | "By convention, feature methods are named with String literals." |
| R5b | No banner comments; keep CLAUDE.md consistent | N/A (house style) | — | — |

Two more findings outside the five rules:
- `origin/master:.claude/skills/it-testing/SKILL.md` has **no Spock content**. Its description covers `*IT.java` only.
- Spock ignores `junit.jupiter.execution.parallel.*`, the properties set in `build-logic/.../aruvii.test-conventions.gradle.kts:32-34`. The repo has no `SpockConfig.groovy`, so specs run sequentially inside the Spock engine (DOC/parallel_execution:11). CLAUDE.md's "unit tests are class-parallel" and its `@Isolated` advice are true for Jupiter only.

### 1b. Installed skill (`SK`)

| Claim (file:line) | Verdict | Source | Note |
|---|---|---|---|
| Spring Boot 4 removed Spock; no Groovy 5 support; stay on Boot 3 (SKILL:19-27) | **OUTDATED** | release_notes:13 (2.4 adds Groovy 5) · spring-boot #47650 (dropped in 4.0) · #48513 (back in 4.1.0-M1) | This repo runs Boot 4.1.1 with `2.4-groovy-5.0` (`gradle/libs.versions.toml:57`). |
| Mocks are lenient by default (SKILL:44-48) | CONFIRMED | interaction_based_testing:68-82 | — |
| `then:` interactions are moved before `when:`; three fixes (SKILL:61-73, interaction-testing:245-295) | CONFIRMED | interaction_based_testing:402-425 | — |
| `Stub()` has the same defaults as Mock, and its then-interactions are "silently ignored" (interaction-testing:11-14) | **WRONG** | interaction_based_testing:788-797 · PROBE P2/P3 | A Stub returns empty or dummy values (`""`, `[]`), not null. A cardinality on a Stub throws `InvalidSpecException`. |
| "Fine to use Mock() for everything" (interaction-testing:23) | Contradicts approved U3 | interaction_based_testing:785-786 | The docs: "Limiting a collaborator to a stub communicates its role." |
| Interface mocks use JDK proxies, class mocks use ByteBuddy/CGLIB (interaction-testing:9) | CONFIRMED | interaction_based_testing:29-33 | — |
| Final classes cannot be mocked (interaction-testing:378) | **OUTDATED** | extensions:1155-1158 | The 2.4 `mockito` mock maker can mock them. |
| A mocked class runs its constructor unless `constructorArgs` is given (interaction-testing:380) | **WRONG** | interaction_based_testing:549-556 | Objenesis skips the constructor. |
| Argument constraints `_`, `*_`, `!null`, `_ as T`, Hamcrest, code (interaction-testing:96-103) | CONFIRMED | interaction_based_testing:230-275 | — |
| `>>>` repeats the last element; `>>` returns a list as-is (anti-patterns:281-291) | CONFIRMED | interaction_based_testing:639-648 | — |
| Strict mode: `0 * _` as the last interaction (interaction-testing:187-203) | CONFIRMED | interaction_based_testing:290-306 | — |
| Interactions first, then conditions, "per the official docs" (anti-patterns:258) | CONFIRMED | interaction_based_testing:383-385 | The docs call it "customary". |
| A `then:` interaction outscopes a `setup()` one | CONFIRMED | interaction_based_testing:320-326 | — |
| Stubbing redefined in `then:` won't work because "the call already happened" (anti-patterns:313-319) | **WRONG** | interaction_based_testing:320-326 | `then:` interactions are hoisted and matched first. The real trap is missing: stubbing in `given:` plus a `1 *` in `then:` returns null (doc:744-746, PROBE P4). |
| Order is enforced only across `then:` blocks; `and:` adds no order (interaction-testing:351-372) | CONFIRMED | interaction_based_testing:513-536 | — |
| No mocks in `@Shared` or static fields; no interactions in `setupSpec` (blocks:217, interaction-testing:312) | CONFIRMED | interaction_based_testing:437-439 | — |
| Interactions in helper methods work (anti-patterns:227) | CONFIRMED | interaction_based_testing:316-318 | — |
| Unrolling is the default in 2.x (data-driven:102) | CONFIRMED | data_driven_testing:166 · PROBE P6 | — |
| `@Unroll` is what makes `#var` names work; `unrollByDefault true` is "recommended" (data-driven:104-160) | **OUTDATED** | data_driven_testing:199-234 · PROBE P6 | Placeholders work with no annotation, and `true` is already the default. |
| `$#income` in a feature name (data-driven:174-177) | **WRONG** | PROBE | It is a compile error. |
| `\|\|` separates expected values and is only visual (data-driven:27) | CONFIRMED | data_driven_testing:118 | — |
| Mocks or instance fields referenced in `where:` (data-driven:184-200, house:127-153) | **WRONG** | data_driven_testing:100 · PROBE P5 | Compile error: "Only @Shared and static fields may be accessed from here". |
| `0 * otherImpls.each{...}` (house:146) | **WRONG** | interaction_based_testing:330-336 | Not a valid interaction. |
| `creditCardRequest(amount: 250)` against a positional default parameter (house:313) | **WRONG** (Groovy semantics) | — | Passes a Map as the first argument. |
| Parallel execution is off by default; both mode defaults are CONCURRENT (parallel:7-32) | CONFIRMED | parallel_execution:11,31 | — |
| `@ResourceLock` modes; locks coarsen up to the spec (parallel:92-128) | CONFIRMED | parallel_execution:411-417 and § Lock coarsening | — |
| `@Isolated` shown on a feature (parallel:139-146) | **WRONG** | `spock/lang/Isolated.java:27` `@Target(TYPE)` | Class-level only. The skill contradicts itself at :150. |
| 2.4: global mocks need `@Isolated`/`@ResourceLock`; `tempdir.cleanup` rename; `.with{}` fix (parallel:152-220) | CONFIRMED | release_notes:47-58 | — |
| `@SpringBean` needs a strongly typed field assigned `Mock()`; replaces beans; initializer blocks (spring:38-122) | CONFIRMED | module_spring (Using `@SpringBean`) | — |
| `@SpringSpy`, `@StubBeans`, `DetachedMockFactory`, slices via `@BootstrapWith` (spring:72-162) | CONFIRMED | module_spring | **Omitted**: `@SpringBean` creates a unique, uncached ApplicationContext. |
| Detached mocks auto-attach when `@Autowired` (spring:160) | UNSUPPORTED | module_spring (Mocks NOTE) | The docs say only that the mocks must be attached. |
| `notThrown()` with no arguments (blocks:116) | CONFIRMED by PROBE | spock_primer:374 | The docs show `notThrown(Type)` and `noExceptionThrown()`. |
| `cleanup:` runs on failure (blocks:124-142) | CONFIRMED | spock_primer:466-475 | **Omitted**: write it defensively, because locals may still hold defaults. |
| `verifyAll` reports every failure (blocks:338-353) | CONFIRMED | spock_primer:648-691 | **Omitted (2.4)**: `@Verify`/`@VerifyAll` helpers and `verifyEach`. |
| Implicit assertions only in then/expect; helpers need explicit `assert` (blocks:334) | **OUTDATED** | spock_primer:581-591 | 2.4 adds `@Verify` helpers. |
| Lifecycle order and inheritance (blocks:177-229) | CONFIRMED | spock_primer:91-115 | — |
| `@Shared` only for read-only or expensive resources (anti-patterns:197-225) | ADAPTED | spock_primer:71-84 | The docs also allow sharing for interaction between features. The skill is stricter, and better for us. |
| `@DataJpaTest` brings an in-memory DB (spring:219) | Conflicts with house rule | CLAUDE.md "never H2" | — |

## 2. Idioms missing from both (or wrong in one)

| Idiom | Ours | Skill | Source |
|---|---|---|---|
| Code constraints are implicit assertions; use `verifyAll(it, T){}` for many fields | wrong (R1) | right | interaction_based_testing:245-252 |
| Stub plus verify in **one** interaction: `1 * x() >> v` | missing | missing (wrong reason) | interaction_based_testing:734-746 |
| A Stub cannot take a cardinality; it returns empty/dummy values | missing | wrong | interaction_based_testing:785-797 |
| `where:` sees only `@Shared`/static fields; pass a discriminator, not a mock | missing | wrong examples | data_driven_testing:98-100 |
| `#var` names with no `@Unroll`; `#featureName`, `#iterationIndex` | missing | outdated | data_driven_testing:503-575 |
| `filter:` block and `combined:` cartesian product (2.4) | missing | missing | data_driven_testing:321-348, 481-491 |
| `@Verify`/`@VerifyAll` helpers; `verifyEach` (2.4) | missing | missing | spock_primer:581-691, 743 |
| Spock `with(obj){}` instead of `obj.with{}` (2.4 behaviour change) | missing | partly | release_notes:55-58 |
| `@SpringBean` costs context caching, so prefer fakes in ITs | fake ports rule exists | missing | module_spring CAUTION |
| Spock parallelism is configured by SpockConfig, not Jupiter properties; `spock.lang.Isolated` is class-only | missing | partly wrong | parallel_execution:11-35 · Isolated.java:27 |
| `cleanup:` written defensively (`?.`) | missing | partly | spock_primer:466-475 |
| `thrown(T)` bound to a typed variable; `noExceptionThrown()` | missing | right | spock_primer:340-380 |

Real-world use, per GitHub code-search file counts: gradle/gradle has `verifyAll` in 99 files, `Stub()` in 45 and `@Unroll` in 28 (the `@Unroll` files predate 2.0). spockframework/spock has `@SpringBean` in 24. The repo's own specs have 93 `Mock(`, 6 `Stub(`, 93 `where:` and 6 `@Shared`.

## 3. Candidate rules for `testing/references/spock.md` (none approved)

| id | Rule (≤25 words) | Source | Rec |
|---|---|---|---|
| K1 | Write a mock-argument closure's checks as plain lines, since each is asserted; nested closures (`every{}`) are not. For many fields use `verifyAll(it, T){}`. | release_notes:946 · interaction_based_testing:245 · PROBE P1 | ADOPT (replaces RULE 1) |
| K2 | When a call is both stubbed and verified, write one interaction (`1 * repo.save(_) >> saved`), never a stub in `given:` plus a count in `then:`. | interaction_based_testing:734-746 · PROBE P4 | ADOPT |
| K3 | A `Stub()` never takes a cardinality (it throws `InvalidSpecException`). If the call must be verified, it is a `Mock()`. | interaction_based_testing:785-788 · PROBE P2 | ADOPT |
| K4 | Assert only the interactions the feature name promises. Use `0 * _` only when "nothing else is called" is itself the behaviour. | interaction_based_testing:68-82, 290-306 | ADOPT |
| K5 | Use an exact count `N *` only when N is the contract; use `0 *` to assert absence; never count logging, metrics or retries. | SK anti-patterns:93-114 · interaction_based_testing:142 | ADAPT |
| K6 | Data-driven features use a `where:` table (`\|` for inputs, `\|\|` for expected values) and name iterations with `#var`. No `@Unroll`, which is the default since 2.0. | data_driven_testing:118, 166, 503-575 | ADOPT |
| K7 | `where:` reads only `@Shared`/static fields. Put a discriminator in the table and build mocks in `given:`. | data_driven_testing:100 · PROBE P5 | ADOPT |
| K8 | One rule per data-driven feature: no `if` on a `where:` column. Split throws-cases and returns-cases into separate features. | SK data-driven:205-255 | ADOPT |
| K9 | `@Shared` only for expensive read-only resources. Never put mocks or mutable state in it; instance fields are fresh per feature. | spock_primer:63-84 · interaction_based_testing:437-439 | ADOPT |
| K10 | Interactions go in `given:`/`then:`, never hidden in helpers. Helpers that assert use `@Verify`/`@VerifyAll` or an explicit `assert`. | interaction_based_testing:316 · spock_primer:581-591 | ADAPT |
| K11 | Declare variables an interaction uses before `when:` or inside `interaction{}`, because `then:` interactions are hoisted above `when:`. | interaction_based_testing:402-425 | ADOPT |
| K12 | Group field checks with `verifyAll(obj){}` (reports every failure) or Spock's `with(obj){}`, never Groovy's `obj.with{}`. | spock_primer:606-691 · release_notes:55-58 | ADOPT |
| K13 | Assert call order only with consecutive `then:` blocks, and only when order is the contract; `and:` imposes no order. | interaction_based_testing:513-536 | ADOPT |
| K14 | Spock ignores `junit.jupiter.*` parallel properties. Isolate a spec with `spock.lang.Isolated` (class-only) or `@ResourceLock`, not the Jupiter annotations. | parallel_execution:11-35 · Isolated.java:27 | ADAPT |
| K15 | In Spring specs prefer fake ports. `@SpringBean` (typed field assigned `Mock()`) only at an external boundary, because it forks an uncached context. | module_spring CAUTION · CLAUDE.md fakes | ADAPT |
| K16 | `cleanup:` frees per-feature resources and is written defensively (`?.`), because it runs after any failure with locals possibly unset. | spock_primer:466-475 | ADOPT |
| K17 | Never `Spy()` the class under test. Extract the overridden method into an injected collaborator. Spy only legacy code. | SK anti-patterns:166-195 | ADOPT |
| K18 | Construct records and value objects; never `Mock()` them. | SK anti-patterns:44-64 | ADOPT |
| K19 | Bind expected exceptions as `def e = thrown(T)` and assert the message. Assert "no exception" with `noExceptionThrown()`, never a conditionless `then:`. | spock_primer:340-380 | ADOPT |
| K20 | Block descriptions (`given: "…"`) are written when the code does not say why; they document, not report. | spock_primer:791-830 | ADAPT (replaces RULE 4's rationale) |

Side note, unverified: `libs.versions.toml:54` says the Boot BOM does not manage Spock. Boot 4.1.0-M1 reinstated Spock support (#48513). Re-read the BOM before relying on that comment.
