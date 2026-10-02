# R15 · plinth testing rules mapped onto our testing references

Ticket: `../issues/30-research-plinth-testing-mapping.md` · feeds G9a (`../issues/23`) Q3+ · shape per G5 (`../issues/13`)
· writing checklist R14 (`16-skill-writing-standards.md` §4a). Sources: the 9 files in `../refs/plinth-pinned/` (read in
full, 2026-10-01). `P130:46` = `refs/plinth-pinned/130-java-testing-strategies.md` line 46, and so on.
Stack facts checked against this worktree (`e0cc30e8`): `CLAUDE.md:4,190-191,220-233`, `.claude/rules/it-testing.md`,
`docs/adr/0009-integrationtest-source-root.md`, `aruvii-test-support/.../AruviiTestcontainersInitializer.java:15-29`.

## Summary (6 lines)

1. **130 is the keeper:** RIGHT-BICEP (6), A-TRIP (5), CORRECT (7) quoted verbatim in §4. They replace our coverage-design mnemonic, which is wrong.
2. **131 and 321 are mostly ADAPT:** the rules hold, but the idiom is JUnit/Mockito. In Spock: `where:` replaces `@CsvSource`, power asserts replace AssertJ, `Stub()`/`Mock()` replace `when`/`verify`.
3. **The Spring harness advice in 321/322/323 is mostly REJECT.** `@WebMvcTest`, `MockMvc(Tester)`, `@MockitoBean`, `TestRestTemplate`, `@ServiceConnection` + `@Container` and the Surefire/Failsafe naming all collide with our decisions or with `AruviiTestcontainersInitializer`.
4. **Plinth fills four of R13's missing rules:** M4 run existing tests first (P130:248), M5 boundaries trigger (P130:175-213, partial), M3 behaviour not defaults (P131:540 + P130:159, partial), and M1 tier choice (P322:57-58, partial). Plinth has nothing for M2 Mock vs Stub vs Fake, and nothing for M6 Prove-It.
5. **058 belongs to planning/acceptance-criteria and scenario-to-tests, not to testing.** Keep its step semantics. Drop the tag and `.feature` mechanics, because we have no Gherkin runtime. 706 is out of testing scope except for image pinning.
6. **Format:** borrow Safeguards → Review checks and Output-Format "CATEGORIZE" → the gap-matrix check. Drop Role/Tone and the Maven compile-gate boilerplate.

---

## 1 · Per plinth file

### P130 · java-testing-strategies (249 lines)

**Summary**
- It is a conceptual frameworks file, not a framework file. It has three mnemonics: RIGHT-BICEP (what to test), A-TRIP (test quality) and CORRECT (boundaries).
- Each mnemonic has one JUnit + AssertJ Good/Bad pair, using the Calculator, OrderProcessor and UserValidation classes.
- Its Output Format asks for findings to be categorised per letter, which works as a gap matrix.
- Its Safeguards require the existing tests to pass before you add new ones (`clean verify`).
- It covers only 3 of RIGHT-BICEP's 6 letters in code (R, B, C, E; Inverse and Performance have no example).

**Structure:** frontmatter 1-8 · Role 11-13 · Goal 15-23 · Constraints 25-33 (Maven compile gate) · Examples 35-234 (Ex1
RIGHT-BICEP 43-100 · Ex2 A-TRIP 102-162 · Ex3 CORRECT 164-234) · Output Format 236-243 · Safeguards 245-250.

| # | rule (≤15 words) | line |
|---|---|---|
| 130-1 | Before writing, ask "if the code ran correctly, how would I know?" | :46 |
| 130-2 | Ask "what else can go wrong?" and "could this happen elsewhere?" | :46 |
| 130-3 | Cover all six RIGHT-BICEP dimensions | :19, :46 |
| 130-4 | Boundary: test the identity value (zero) and the near-max value | :61-70 |
| 130-5 | Cross-check with an independent property (commutativity), not the same algorithm | :72-76 |
| 130-6 | Error: force the error; assert both exception type and message | :78-84 |
| 130-7 | Bad: a single happy-path test for a unit | :91-98 |
| 130-8 | Tests are Automatic, Thorough, Repeatable, Independent, Professional | :20, :105 |
| 130-9 | Fresh fixture per test; never shared static mutable state | :116-119, :145-146 |
| 130-10 | Weak assertion (`isGreaterThan(0)`) is Bad | :159 |
| 130-11 | Check the seven CORRECT boundary conditions | :21, :167 |
| 130-12 | Range: at the lower bound, at the upper bound, just below the lower bound | :175-189 |
| 130-13 | Conformance: valid AND invalid formats, both parameterised | :191-202 |
| 130-14 | Existence: null and empty input each have a test | :204-213 |
| 130-15 | Categorise findings by strategy letter (gap matrix) | :238-239 |
| 130-16 | Existing tests must pass before new test strategies are applied | :248 |
| 130-17 | Apply incrementally; validate after each modification | :250 |

### P131 · java-testing-unit-testing (711 lines)

**Summary**
- It covers framework-agnostic unit tests in JUnit 5 + AssertJ + Mockito, through 16 numbered examples.
- The core is G/W/T, descriptive names, one concept per test, independence, parameterisation and mocking collaborators.
- Its anti-pattern list at :540 is the densest rule block.
- It forbids reflection on private methods and asks you to assert exception messages.
- It says it does not apply to Spring Boot (:33), but our domain and application layers are framework-free, so it fits them.

**Structure:** frontmatter 1-8 · Role 11-13 · Goal 15-27 (5 principles) · Constraints 29-38 · Examples 40-690 (16 examples;
Ex9-14 are prose-only) · Output Format 692-700 · Safeguards 702-711.

| # | rule | line |
|---|---|---|
| 131-1 | JUnit 5 annotations, never JUnit 4 | :61-64 |
| 131-2 | AssertJ over JUnit `Assertions` and Hamcrest | :124-127 |
| 131-3 | `assertThatThrownBy` over `assertThrows`; assert the message | :151-153, :181-185 |
| 131-4 | Three separated phases: Given, When, Then | :190-193 |
| 131-5 | Names state scenario + outcome (`should_X_when_Y`) or `@DisplayName` | :238-241 |
| 131-6 | One logical concept per test method | :286-289 |
| 131-7 | Tests are independent, run in any order, and set up their own state | :322-325 |
| 131-8 | Parameterised test for the same logic over many inputs | :382-385 |
| 131-9 | Mock collaborators (DB, network, other classes) to isolate the SUT | :450-453 |
| 131-10 | Good example verifies the call plus `verifyNoMoreInteractions` | :493-494 |
| 131-11 | Coverage is a guide; a covered line is not a verified line | :522-525 |
| 131-12 | Test classes and methods are package-private | :527-530 |
| 131-13 | Small focused methods; helpers for duplicated setup | :532-535 |
| 131-14 | Avoid testing implementation details, complex test logic, ignored edges | :540 |
| 131-15 | Avoid hard-coded values; use constants or test data | :540 |
| 131-16 | Avoid over-reliance on mocks; never ignore failing tests | :540 |
| 131-17 | Isolated state per test; prefer immutable objects | :542-545 |
| 131-18 | Test graceful degradation when dependencies are unavailable | :547-550 |
| 131-19 | Use JSpecify nullness annotations in tests and the SUT | :552-555 |
| 131-20 | Never reflect into private methods; test the public API or extract | :604-607 |
| 131-21 | Existing tests pass (`clean verify`) before new test strategies | :705 |
| 131-22 | New tests introduce no inter-test dependency; keep runtime reasonable | :710-711 |

### P132 · java-testing-integration-testing (492 lines)

**Summary**
- It is framework-agnostic IT scaffolding, centred on WireMock for outbound HTTP.
- It is an interactive generator: inspect imports, ask topology questions one by one, then generate the `BaseIntegrationTest`.
- Its real rules: stub at the network level rather than with mocks, inject coordinates dynamically, register stubs per test, and keep bodies in mapping files.
- Most of the file is process for a generator agent, not standards.
- It is the only plinth source for "never Mockito an HTTP client in an IT".

**Structure:** frontmatter · Role 11-13 · Tone 15-17 · Goal + guiding principles 19-34 · Constraints 36-45 · Steps 47-165 (Q&A,
generate base, generate mappings) · Examples 168-471 (6) · Output Format 473-481 · Safeguards 483-492.

| # | rule | line |
|---|---|---|
| 132-1 | Start infrastructure from the test process; no shared pre-provisioned environment | :30 |
| 132-2 | Inject coordinates (URLs, ports) dynamically; never hardcode | :31, :129 |
| 132-3 | Infra lives in a shared base; concrete tests hold behaviour only | :32 |
| 132-4 | Stub outbound HTTP at the network level so the real client pipeline runs | :33, :491 |
| 132-5 | Given-When-Then in every test method | :34 |
| 132-6 | Read the code's imports for infra signals before asking or generating | :53-63, :486 |
| 132-7 | Include only the infrastructure the component actually needs | :130-131, :487 |
| 132-8 | Response bodies live in mapping files (`bodyFileName`), not inline strings | :260-271, :361 |
| 132-9 | A mapping has a `name` and matches on headers or body, not just URL | :320-324 |
| 132-10 | Programmatic stubs only for dynamic values or fault injection | :361, :377-383 |
| 132-11 | Register stubs inside each test, never in `@BeforeAll` | :406-409, :490 |
| 132-12 | Verify the outbound call was made (`verify(1, postRequestedFor…)`) | :252, :385-387 |
| 132-13 | Test-only dependencies stay test-scoped | :492 |
| 132-14 | Ask topology questions one at a time, in fixed order | :95-103 |

### P133 · java-testing-acceptance-tests (406 lines)

**Summary**
- It generates happy-path acceptance tests from a `.feature` file, for scenarios tagged `@acceptance` only.
- It boots the full app with Testcontainers (DB, Kafka) and WireMock (external REST), and uses RestAssured as the client.
- One test per scenario; Gherkin steps map literally onto G/W/T.
- It scopes tests to the happy path only and stops when the `.feature` file is missing.
- The file has no Output Format or Safeguards section; its Step Constraints play that role.

**Structure:** frontmatter · Role 11-13 · Tone 15-17 · Goal + principles 19-35 · Constraints 37-47 · Steps 49-168 (parse,
base, tests, deps) · Examples 171-405 (4).

| # | rule | line |
|---|---|---|
| 133-1 | A `.feature` file must be in context; stop otherwise | :41, :57 |
| 133-2 | Implement only scenarios tagged `@acceptance` / `@acceptance-tests` | :46, :73 |
| 133-3 | Happy path only; skip error paths unless asked | :47, :135 |
| 133-4 | Full app, dependencies simulated; no mocks of internal services | :30 |
| 133-5 | Testcontainers for DB/Kafka; WireMock for external REST | :31-32, :82-86 |
| 133-6 | Use RestAssured for the API under test, never MockMvc | :33, :133, :349-359 |
| 133-7 | One test per scenario; each step maps to Given / When / Then | :34-35, :120-124 |
| 133-8 | Propagate coordinates via `System.setProperty` in `@BeforeAll` | :103 |
| 133-9 | Confirm the scenario list with the user before generating code | :74 |
| 133-10 | Test libraries in test scope only | :400-405 |

### P321 · spring-boot-testing-unit-tests (862 lines)

**Summary**
- It covers Spring Boot unit tests: pure Mockito for services, plus `@WebMvcTest` / `@JsonTest` slices with `@MockitoBean`.
- Its best content is the time rule: inject `Clock`, use `Clock.fixed`, and inject suppliers for UUIDs and randomness.
- It also has the `@JsonTest` pitfall: `hasJsonPath*Value` checks existence, not value.
- Its naming example calls the `*Spec` suffix "silently skipped". That is a Maven fact, and it is false for our Gradle + Spock build.
- Its Safeguards include "do not add `@SpringBootTest` to make it work" and "over-mocking hides integration issues".

**Structure:** frontmatter · Role 11-13 · Goal 15-17 · Constraints 19-28 · Examples 30-844 (10) · Output Format 846-853 ·
Safeguards 855-862.

| # | rule | line |
|---|---|---|
| 321-1 | Plain service logic gets a Mockito unit test, never `@SpringBootTest` | :48, :115 |
| 321-2 | Omit `times(1)` in `verify`; it is the default | :48, :90 |
| 321-3 | Production code takes an injected `Clock`; never `Instant.now()` | :17, :136 |
| 321-4 | Same for `UUID.randomUUID`, random, `nanoTime`: inject a supplier or seeded source | :136 |
| 321-5 | Tests pass `Clock.fixed(…)`, or a mocked `Clock` for multiple instants | :136, :177-185 |
| 321-6 | Controllers: `@WebMvcTest` + MockMvc + mocked services | :218-221 |
| 321-7 | DTO JSON: `@JsonTest`; assert values with `extractingJsonPath*`, not `hasJsonPath*` | :290-293 |
| 321-8 | `@MockitoBean` replaces the removed `@MockBean` in Boot 4 | :631-634 |
| 321-9 | Copy-pasted variants become a parameterised test | :444-447 |
| 321-10 | Fixed `Clock` as `@Primary` bean in `@TestConfiguration` | :551-554 |
| 321-11 | Unit test class suffix `Test`; `*Spec` is silently skipped | :702-705, :762 |
| 321-12 | Test beans in `@TestConfiguration` under test sources; never `@Profile("test")` in main | :782-785 |
| 321-13 | Bad: `assertThat(result).isNotNull()` as the only check | :127 |
| 321-14 | Do not add `@SpringBootTest` just to "make it work" | :859 |
| 321-15 | Over-mocking hides integration issues; pair unit tests with ITs | :860 |
| 321-16 | Refactor one class or package at a time; stop on failure until understood | :861-862 |

### P322 · spring-boot-testing-integration-tests (922 lines)

**Summary**
- ITs prove wiring and contracts (HTTP, DB, brokers). They do not re-test the business branches the unit tests already cover.
- It recommends Testcontainers `static @Container` + `@ServiceConnection`, an abstract base, and `@DynamicPropertySource` only for extras.
- Its HTTP client is `TestRestTemplate` (status before body) or `MockMvcTester` + `@MockitoBean`.
- It uses the `@DataJpaTest` / `@DataJdbcTest` slice with `replace = NONE`, which is real Postgres, never H2.
- Its data isolation options are `@Transactional` rollback, `@Sql`, or truncate. It names tests by suffix: `*Test` / `*IT` / `*AT` via Surefire and Failsafe.

**Structure:** frontmatter · Role 11-13 · Goal 15-25 (wiring decision list 19-23) · Constraints 27-36 · Examples 38-904 (12) ·
Output Format 906-913 · Safeguards 915-922.

| # | rule | line |
|---|---|---|
| 322-1 | ITs verify wiring and contracts; never re-test unit-level business branches | :17, :57-58, :95-97 |
| 322-2 | Real containers, never shared developer databases | :17, :105 |
| 322-3 | `static @Container` + `@ServiceConnection` is the default wiring | :20, :105 |
| 322-4 | `@DynamicPropertySource` only for properties no ServiceConnection covers | :21 |
| 322-5 | Share containers via an abstract base or `@ImportTestcontainers`; never copy-paste | :22, :25 |
| 322-6 | Pin Docker image tags | :105 |
| 322-7 | `TestRestTemplate` on `RANDOM_PORT`; assert status before body | :171 |
| 322-8 | Never assert by substring match on raw JSON | :171, :255 |
| 322-9 | Status-only assertion is Bad; assert body and `Location` too | :221, :259-260 |
| 322-10 | Each test starts from a known state: rollback, `@Sql`, or truncate | :268 |
| 322-11 | Never pass IDs between tests via static fields | :268, :304 |
| 322-12 | One scenario per test; `@DisplayName`; optionally verify persistence | :321 |
| 322-13 | One container per class (static); never start per method | :370 |
| 322-14 | Persistence slice `@DataJpaTest` + `replace = NONE` against real DB, not H2 | :443 |
| 322-15 | `MockMvcTester` + `@MockitoBean` for HTTP slices | :523 |
| 322-16 | Suffix routes phase: `*Test` unit, `*IT` integration, `*AT` acceptance | :615 |
| 322-17 | Surefire includes `*Test`, Failsafe `*IT`/`*AT` | :711 |
| 322-18 | Never point tests at a production database | :920 |

### P323 · spring-boot-testing-acceptance-tests (486 lines)

**Summary**
- It is the Spring Boot twin of P133: a `.feature` file plus `@acceptance` tags, implemented on the happy path only.
- It boots the full app on `RANDOM_PORT`, uses `TestRestTemplate`, and puts the containers on `BaseAcceptanceTest`.
- It never mocks internal `@Service` beans and uses WireMock for outbound calls, with `resetAll()` before each test.
- It discusses context sharing against `@DirtiesContext` as a speed/correctness trade-off.
- `@DisplayName` mirrors the Gherkin scenario title for traceability, and class names use the `*AT` suffix.

**Structure:** frontmatter · Role · Tone · Goal 19-25 · Constraints 27-40 · Examples 42-465 (6) · Output Format 467-474 ·
Safeguards 476-486.

| # | rule | line |
|---|---|---|
| 323-1 | `.feature` in context and Spring Boot on classpath, else stop | :31-32, :478 |
| 323-2 | `@acceptance` scenarios only; happy path by default | :39-40, :481 |
| 323-3 | Full app on `RANDOM_PORT`; real HTTP via `TestRestTemplate` | :21, :89 |
| 323-4 | Never mock internal `@Service` beans; WireMock for outbound HTTP | :21, :89, :322-335 |
| 323-5 | Containers shared on base class with `@ServiceConnection` | :23 |
| 323-6 | Reset WireMock stubs before each test; keep context warm | :89, :139-142 |
| 323-7 | `@DirtiesContext` only when a test mutates shared context state | :89 |
| 323-8 | `@DisplayName` echoes the scenario title for traceability | :194, :215 |
| 323-9 | Register stubs in the Given phase, before the request | :256 |
| 323-10 | Verify the outbound stub was actually called | :307-308 |
| 323-11 | Never MockMvc for acceptance; real servlet/filter stack | :482 |
| 323-12 | Do not add RestAssured | :483 |
| 323-13 | No real API keys or production URLs in tests | :484 |
| 323-14 | Acceptance classes always end `AT` | :486 |

### P058 · design-bdd (321 lines)

**Summary**
- It is a Gherkin syntax reference built on 7 Good/Bad examples. It is not a BDD workflow (:315).
- It covers keyword roles: Feature, Rule, Example, Background, Outline, Data Table, Doc String, tags, comments and localization.
- The quality rules that carry over: Given = context, When = one event, Then = observable outcome, and no implementation-coupled steps.
- It says valid Gherkin is not good BDD and does not require Cucumber (:38, :321), which matches our "no runtime" decision.
- It warns: do not infer a test tier (`@integration-test`) from a scenario being an error case.

**Structure:** frontmatter · Role 11-13 · Tone 15-17 · Goal 19-21 · Constraints 23-38 · Examples 40-301 (7) · Output Format
304-310 · Safeguards 313-321.

| # | rule | line |
|---|---|---|
| 058-1 | `Rule` groups examples that illustrate one business rule | :55, :63-68 |
| 058-2 | Given = context, When = one event, Then = observable outcome | :32, :88 |
| 058-3 | `And` / `But` only where they help readability | :32 |
| 058-4 | Bad: steps naming classes, requests, or "save invoked once" | :104-107, :320 |
| 058-5 | Background is short, at most one per scope | :114, :141-142 |
| 058-6 | Outline placeholders match the Examples header; one row per example | :149, :169-176 |
| 058-7 | A data table or doc string belongs to the step above it | :183 |
| 058-8 | Tags precede taggable elements; never on steps | :35, :217, :318 |
| 058-9 | Never infer a test tier from an error or alternative scenario | :36, :251, :318 |
| 058-10 | Behaviour tags only when trusted context supports them | :251 |
| 058-11 | Valid syntax does not prove good BDD or require Cucumber | :38, :321 |
| 058-12 | One Feature per file; colons only on structural keywords | :30, :55, :317 |

### P706 · containers-docker (67 lines)

**Summary**
- It is a router stub for Dockerfile and image quality: multi-stage, jlink, non-root, pinned base, JVM container flags, SBOM.
- It explicitly defers Testcontainers to "the matching testing skill" (:21, :33).
- Its body lives in a `references/706-…md` file that is NOT among the pinned refs. Only the SKILL shell was supplied.
- Testing relevance is close to zero. It feeds our deploy and compose content, not testing/.
- One overlap: pin image versions intentionally (:31), which is also P322-6 for test containers.

**Structure:** frontmatter · intro 9-21 · Constraints 23-36 · When to use 38-45 · Workflow 47-63 · Reference 65-67.

| # | rule | line |
|---|---|---|
| 706-1 | Testcontainers setup is the testing skill's, not this one's | :21, :33 |
| 706-2 | Never bake secrets into image layers, labels, args, or logs | :28 |
| 706-3 | Non-root, least privilege, no privileged containers | :18, :29 |
| 706-4 | Pin base images intentionally; document digest trade-offs | :31 |
| 706-5 | Set JVM flags for container memory/CPU limits | :32 |
| 706-6 | Verify with image build, scan, and smoke test before promoting | :63 |

---

## 2 · Mapping table

Targets come from G9a Q1: `strategy`, `value-bar`, `coverage-design`, `boundaries`, `unit-tests`, `spock`,
`integration-tests`, `smoke-specs`, workflows `write-a-test`, `scenario-to-tests`, `audit`, router `testing/SKILL.md`,
`rules/testing.md`, plus `planning/acceptance-criteria`.

Sections: **R** = Rules · **W** = When X, use Y · **G** = Good/Bad · **E** = Decided edges · **C** = Review checks.

### 2a · Strategy-level (P130 + scope rules)

| plinth | target · section | verdict | how / why |
|---|---|---|---|
| 130-1, 130-2 | write-a-test step 1 · R | ADOPT | the two opening questions become the first step before any test is written |
| 130-3 | coverage-design · R + C | ADOPT | six letters exactly (§4); C = "each changed unit has a RIGHT-BICEP gap row" |
| 130-4, 130-12 | boundaries · R + G | ADAPT | Spock `where:` row per bound; pin `RotationReminderBoundarySpec:42-71` (R13 §2) |
| 130-5 | coverage-design · R | ADOPT | "oracle independent of the implementation"; pairs with R13 M12 (system of record) |
| 130-6 | unit-tests · R; spock · G | ADAPT | Spock `thrown(X)` + `e.message`; Java legacy keeps `assertThatThrownBy` |
| 130-7 | coverage-design · G (Bad) | ADAPT | replace Calculator with a real Bad pin: `RunModeSpec:49-60` |
| 130-8 | unit-tests · R (A-TRIP block) | ADOPT | the letters already match `test-quality.md` (R13 §5); keep plinth wording |
| 130-9, 130-10 | unit-tests · R + G | ADAPT | Spock `setup()` / field init per feature; weak-assert Bad → `AlertTriggerTypeSpec:8-13` |
| 130-11 | boundaries · R | ADOPT | seven letters exactly (§4); keep our per-letter probes |
| 130-13, 130-14 | boundaries · G | ADAPT | Spock `where:`; existence pin `RotationReminderBoundarySpec:81-90` |
| 130-15 | coverage-design · C; workflows/audit | ADOPT | output a per-letter gap matrix; missing cases recorded as named gaps |
| 130-16, 131-21 | rules/testing.md · R; write-a-test step 0 | ADAPT | `./mvnw clean verify` → `make test-module MOD=… TEST=…` for touched tests first (M4) |
| 130-17 | write-a-test · R | ADOPT | one test, run it, then the next |
| 322-1 | strategy · R + W | ADOPT | "an IT owns wiring/contract; a unit owns the branch". Feeds the tier choice (M1) |
| 321-1, 321-14 | strategy · W | ADOPT | "plain service logic → unit spec; never a Spring context to make it work" |
| 321-15 | strategy · E | ADOPT | over-mocked unit → pair with an IT (Decided edge: when a second tier earns its place) |

### 2b · Unit tests and Spock (P131, P321)

| plinth | target · section | verdict | how / why |
|---|---|---|---|
| 131-1 | — | REJECT | our rule is Spock for every new test (`rules/it-testing.md:62`); JUnit 4/5 choice is moot |
| 131-2 | spock · R; unit-tests · E | ADAPT | Groovy: power assert, not AssertJ (`rules/it-testing.md:99-101`); AssertJ stays for legacy Java |
| 131-3 | spock · R | ADAPT | `thrown(T)` + assert the message; matches `CLAUDE.md:190` "assertThrows banned" in Java |
| 131-4 | spock · R + C | ADAPT | Spock `given:/when:/then:` with descriptions; no bare labels (`rules/it-testing.md:51-52`) |
| 131-5 | rules/testing.md · R | ADAPT | Spock: sentence feature names (G9a default); `should_X_when_Y` only in legacy JUnit |
| 131-6 | unit-tests · R + C | ADOPT | one behaviour per feature method; `where:` rows count as one behaviour |
| 131-7, 131-17 | unit-tests · R | ADOPT | no `@Shared` mutable state; fresh fixture per feature |
| 131-8, 321-9 | spock · W | ADAPT | "same logic, many inputs → `where:` table" (not `@ParameterizedTest`/`@CsvSource`) |
| 131-9 | unit-tests · W | ADAPT | DB/network → port Fake or `Stub()`; own pure classes → real object (G9a doubles default) |
| 131-10 | — | REJECT | `verifyNoMoreInteractions` over-specifies. Our default is `Stub()` for returns and `Mock()` only when the interaction IS the behaviour |
| 131-11 | unit-tests · E | ADOPT | coverage floors in `gradle.properties` are the gate; "covered ≠ verified" is the edge |
| 131-12 | — | REJECT (N/A) | Groovy classes are public by default; Spock specs gain nothing. Java legacy: no new rule |
| 131-13 | unit-tests · R | ADOPT | small features; helpers last (CLAUDE.md:191 "helpers last") |
| 131-14 | value-bar · R; unit-tests · C | ADOPT | "test behaviour not implementation; no conditionals/loops computing the expected value" |
| 131-15 | — | REJECT | "avoid hard-coded values" contradicts our Good pin `RefusalReasonSpec:19-26`: a literal wire string is the independent oracle (130-5) |
| 131-16 | unit-tests · R; rules/testing.md | ADOPT | never ignore a failing test. Our edge: `@Disabled` debt (R13 M10) needs a named ticket |
| 131-18 | coverage-design · R (Error) | ADOPT | "graceful degradation when a dependency is down" sits under E of RIGHT-BICEP |
| 131-19 | — | REJECT | JSpecify is not in our stack; we use `Optional`/sealed types to avoid null cases (CLAUDE.md:190-191) |
| 131-20 | unit-tests · R + G | ADOPT | Bad pin `ToolTrustStoreWiringIT.java:55-56,77-78` (reflection seam) |
| 131-22 | unit-tests · C | ADOPT | new spec adds no ordering dependency |
| 321-2 | spock · R | ADAPT | Spock: `1 * port.save(_)` only when the call is the contract; never as noise |
| 321-3, 321-4, 321-5 | unit-tests · R + G | ADOPT | `Clock` injected; Good pin `RotationReminderBoundarySpec:16-24` (#512 javadoc) |
| 321-6 | — | REJECT | `@WebMvcTest`/MockMvc: never MockMvc (CLAUDE.md:233); 0 uses in repo |
| 321-7 | — | REJECT (N/A) | `@JsonTest` has 0 uses; JSON is asserted through `RestTestClient` in ITs. Keep the "existence ≠ value" lesson as a value-bar junk item |
| 321-8 | — | REJECT | `@MockitoBean` is banned in ITs (CLAUDE.md:233). Unit specs need no Spring beans |
| 321-10, 321-12 | integration-tests · W | ADAPT | test beans → `@TestConfiguration` / `FakePortsConfig` (`@TestBean`); no `@Profile("test")` in main |
| 321-11 | — | REJECT | Gradle + Spock: `*Spec` runs. The claim is Maven-only and false here |
| 321-13 | value-bar · G (junk) | ADOPT | lone `isNotNull()` / `!= null` check = junk; pin `AlertTriggerTypeSpec:8-13` |
| 321-16 | workflows/audit · R | ADOPT | one class or package at a time (matches G9a Q1 "audit one class/package") |

### 2c · Integration tests (P132, P322, P706)

| plinth | target · section | verdict | how / why |
|---|---|---|---|
| 132-1, 322-2 | integration-tests · R | ADOPT | already ours: Testcontainers, never H2 / shared DB |
| 132-2 | integration-tests · R | ADAPT | coordinates via `AruviiTestcontainersInitializer` (singleton). WireMock URL via `@DynamicPropertySource` (5 files use it) |
| 132-3, 322-5 | integration-tests · W | ADAPT | "need the platform stack → `@EnableAruviiIT` / `@EnableAruviiSpec`"; never a new base class |
| 132-4 | integration-tests · R | ADOPT | never Mockito/`@MockitoBean` an HTTP client in an IT; WireMock (in use in 18 files) |
| 132-5 | spock · R | ADAPT | Spock blocks with descriptions |
| 132-6, 132-7 | integration-tests · E | ADOPT | start only what the IT needs (e.g. Ollama off unless `OLLAMA=true`) |
| 132-8, 132-9 | integration-tests · E | ADAPT | inline `stubFor` is our norm. Mapping files are an edge (Skip when: body < N lines). Open Q4 |
| 132-10 | integration-tests · W | ADOPT | fault injection (503, delay) → programmatic stub |
| 132-11 | integration-tests · R + C | ADOPT | stubs registered per test; R13 already lists this gap (§7c) |
| 132-12, 323-10 | integration-tests · R | ADOPT | verify the outbound call when the call is the behaviour (same as the `Mock()` rule) |
| 132-13 | — | REJECT (gated) | Gradle test configs already scope it; no rule needed (R14 checklist #4) |
| 132-14 | — | REJECT | an interactive generator process; our refs are standards, not Q&A scripts |
| 322-1 | integration-tests · R; strategy · W | ADOPT | IT owns transport / lifecycle / SQL; not unit branches (R13 §7c, oc `:23-27`) |
| 322-3, 322-13 | — | REJECT | `@Container`/`@Testcontainers` stops containers per class. Our singleton is deliberate: 14 properties, ServiceConnection covers 5 (`AruviiTestcontainersInitializer.java:15-29`) |
| 322-4 | integration-tests · E | ADAPT | `@DynamicPropertySource` only for WireMock or other extras; never datasource/Redis |
| 322-6, 706-4 | integration-tests · R | ADOPT | images pinned once in `TestConstants.java:14-15`; never inline a tag |
| 322-7 | integration-tests · R | ADAPT | `RestTestClient` not `TestRestTemplate` (0 uses); keep "status before body" |
| 322-8, 322-9 | integration-tests · G | ADOPT | parse JSONB / body; never substring; assert more than status |
| 322-10 | integration-tests · W | ADAPT | full-stack → `AruviiTestReset` truncate (PRESERVE list); `@DataJpaTest` bases → rollback. Not `@Sql` |
| 322-11 | integration-tests · R | ADOPT | no static IDs between tests |
| 322-12 | integration-tests · R | ADOPT | one scenario per feature; DB-row assertion allowed when persistence is the behaviour (G9a default) |
| 322-14 | integration-tests · W + G | ADOPT | `@DataJpaTest @AutoConfigureTestDatabase(replace = NONE)`; pin `InfraRepositoryIT.groovy` |
| 322-15 | — | REJECT | MockMvcTester + `@MockitoBean` are both banned |
| 322-16, 322-17 | — | REJECT | Gradle source root decides phase (ADR-0009), not suffix; Surefire/Failsafe gone |
| 322-18, 323-13 | integration-tests · R | ADOPT (one line) | never a real key or prod URL; already true via `TestConstants` |
| 706-1 | — | ADOPT (boundary) | confirms Testcontainers belongs in integration-tests, not a docker ref |
| 706-2, 706-3, 706-5, 706-6 | — (delivery/ or deploy ref) | OUT OF SCOPE | not testing; route to the deploy/compose content (`docker-compose.yml:114,171,270` mem limits) |

### 2d · Acceptance, BDD, scenarios (P133, P323, P058)

| plinth | target · section | verdict | how / why |
|---|---|---|---|
| 133-1, 323-1 | — | REJECT | no `.feature` files; G/W/T prose in the REQ (`to-spec/SKILL.md:46`) |
| 133-2, 323-2 | — | REJECT | no `@acceptance` tags; every AC is in scope |
| 133-3, 323-2 (happy only) | — | REJECT | contradicts CLAUDE.md:221 "happy path and failure/edge" (G9a default) |
| 133-4, 323-4 | integration-tests · R; smoke-specs · R | ADOPT | no fake for an internal service in an IT; fakes only at the external port |
| 133-5 | integration-tests · W | ADOPT | DB → Testcontainers; outbound REST → WireMock (Kafka N/A; Redis instead) |
| 133-6, 323-3, 323-11 | — | REJECT (client) / ADOPT (intent) | RestAssured, `TestRestTemplate` → `RestTestClient` over `RANDOM_PORT`; "real HTTP stack, never MockMvc" ADOPT |
| 133-7 | scenario-to-tests · R | ADAPT | each AC step → Spock `given:/when:/then:` description; tier per scenario (M1), not "one per scenario" blindly |
| 133-8 | — | REJECT | `System.setProperty` is for apps without Spring; we use the initializer |
| 133-9 | — | REJECT | `/crq` stage 6 is AFK after `/approved`; the scenarios come from the approved REQ |
| 323-6 | integration-tests · R | ADOPT | WireMock reset per test (`resetAll()` in `setup()`/`@BeforeEach`) |
| 323-7 | integration-tests · E | ADAPT | `@DirtiesContext` has 0 uses; edge = "use only when a test mutates singleton state; say why" |
| 323-8 | scenario-to-tests · R + C | ADAPT | feature name or `@DisplayName` cites the AC id (`REQ-075 R1` style, R13 §12) |
| 323-9 | spock · R | ADOPT | stubs in `given:` |
| 323-12, 323-14 | — | REJECT | no RestAssured to add; no `*AT` tier (smoke = Playwright is our acceptance tier) |
| 058-1 | planning/acceptance-criteria · R | ADOPT | ACs grouped under the business rule they illustrate |
| 058-2 | planning/acceptance-criteria · R + C; scenario-to-tests · R | ADOPT | Given = context, When = one event, Then = observable outcome |
| 058-3, 058-5, 058-6, 058-7 | planning/acceptance-criteria · G | ADAPT | prose rules: short shared preconditions, outline table matches placeholders. Pin `REQ-500:298-370` |
| 058-4 | planning/acceptance-criteria · G (Bad) | ADOPT | no class names or call counts in an AC. Fills R13 "assert behaviour, not a default" for ACs |
| 058-8, 058-10, 058-12 | — | REJECT | tag, colon and file syntax only matter to a parser we do not run |
| 058-9 | strategy · E | ADOPT | tier is never inferred from "it's an error case"; scenario-to-tests picks the tier from the risk |
| 058-11 | scenario-to-tests · E | ADOPT | confirms "no Gherkin runtime by design" |

---

## 3 · R13 missing rules: which plinth line covers each

| R13 # | missing rule | plinth coverage | verdict |
|---|---|---|---|
| M1 | tier choice | P322:57-58 (IT = wiring, not branches) · P321:48, :859 (no context for service logic) · P058:251 (never infer tier from error case) | **partial**: gives the split, not "lowest tier that can prove it". Addy TDD `:144-186` stays primary |
| M2 | unit-level doubles (Mock/Stub/Fake) | P131:450-453 says "mock collaborators", which contradicts our default · P321:860 warns about over-mocking · P321:782-785 `@TestConfiguration` fakes | **not covered**: plinth is Mockito-everything. Keep the G9a default (`Stub()` returns, `Mock()` only for interaction) |
| M3 | assert behaviour not defaults / no change detectors | P131:540 "testing implementation details" · P130:159 weak assertion · P321:127 lone `isNotNull` · P322:259-260 status-only | **partial**: covers weak and implementation asserts, not "constant / enum-list change detector". Superpowers `:41-63` stays primary |
| M4 | run existing tests first | P130:248 · P131:705 · P321:862 "stop if tests fail until understood" | **covered**: ADOPT with `make test-module … TEST=` |
| M5 | boundaries trigger | P130:175-213 (at / at upper / just below; valid + invalid; null + empty) · P130:238-239 (categorise gaps per letter) | **partial**: gives the probes and the gap matrix. No trigger predicate ("a diff adding a comparison, collection, clock, or external ref") |
| M6 | Prove-It for bug fixes | none in the 9 files | **not covered**: addy `:96-142`, superpowers `SKILL.md:113-128` |
| (M7) | verify Red for the right reason | none | not covered |
| (M8) | mental mutation check | none (P131:525 "covered line not verified" is the motive only) | not covered |
| (M10) | test-debt edges | P131:540 "never ignore failing tests" | partial: motive only |
| (M12) | assert from system of record | P130:72-76 cross-check via independent means · P132:252 verify at the network | partial: supports the rule |

---

## 4 · The three mnemonics exactly as P130 states them

The Goal lines (P130:19-21) quoted verbatim:

> 1. **RIGHT-BICEP**: Key questions and dimensions to guide comprehensive test creation — Right results, Boundary
> conditions, Inverse relationships, Cross-checks, Error conditions, Performance.
> 2. **A-TRIP**: Characteristics of good tests — Automatic, Thorough, Repeatable, Independent, Professional.
> 3. **CORRECT**: Boundary condition verification — Conformance, Ordering, Range, Reference, Existence, Cardinality, Time.

**RIGHT-BICEP**, the question form, verbatim from P130:46:

| letter | P130:46 |
|---|---|
| Right | "Are the results **Right**?" |
| B | "Are all the **Boundary** conditions CORRECT?" |
| I | "Can you check **Inverse** relationships?" |
| C | "Can you **Cross-check** results using other means?" |
| E | "Can you force **Error** conditions to happen?" |
| P | "Are **Performance** characteristics within bounds?" |

The lead-in questions on the same line: "If the code ran correctly, how would I know?", "How am I going to test this?",
"What else can go wrong?" and "Could this same kind of problem happen anywhere else?"
Note: "RIGHT" is the word *Right*, not five letters. That makes 6 dimensions, not the 9 in our `coverage-design.md:3,17-52`.

**A-TRIP**, verbatim from P130:105:

| letter | P130:105 |
|---|---|
| A | "**Automatic**: Tests should run without human intervention." |
| T | "**Thorough**: Test everything that could break; cover edge cases." |
| R | "**Repeatable**: Tests should produce the same results every time, in any environment." |
| I | "**Independent**: Tests should not rely on each other or on the order of execution." |
| P | "**Professional**: Test code is real code; keep it clean, maintainable, and well-documented." |

**CORRECT**, verbatim from P130:167:

| letter | P130:167 |
|---|---|
| C | "**Conformance**: Does the value conform to an expected format?" |
| O | "**Ordering**: Is the set of values ordered or unordered as appropriate?" |
| R | "**Range**: Is the value within reasonable minimum and maximum values?" |
| R | "**Reference**: Does the code reference anything external that isn't under direct control?" |
| E | "**Existence**: Does the value exist? (e.g., is non-null, non-zero, present in a set)" |
| C | "**Cardinality**: Are there exactly enough values?" |
| T | "**Time**: Is everything happening in order? At the right time? In time?" |

Caveat: the pinned P130 has no examples for Inverse or Performance, and no prose on "independent expected value" or
"record gaps". R13 cited those from the corpus extraction (`plinth-java-testing-strategies…md:192, :219-236`), which is
longer than this pinned file. Before coverage-design cites those lines, confirm the extraction is the same version (`@c4276f64`).

---

## 5 · Format mapping: plinth sections → G5 five sections

| plinth section | what it holds | → our section | borrow? |
|---|---|---|---|
| frontmatter `description` | "Use when…" triggers + scope | router SKILL description only (R14 §3: refs carry none) | borrow the trigger list form for `testing/SKILL.md` |
| Role / Tone | persona sentence | — | **drop**: no-op test (R14 #15) |
| Goal | principles prose + mnemonic definitions | **Rules** (principles as checkable sentences) | borrow; split prose into one rule per line |
| Goal "guiding principles" (P132:28-34, P133:28-35) | 5-6 imperative bullets | **Rules** | closest to our Rules; copy the shape |
| Goal decision lists (P322:19-23 "Choosing wiring") | if-this-then-that | **When X, use Y** | **best borrow**: observable predicate → choice |
| Constraints (Maven compile gate, PRECONDITION) | blocking preconditions | **Decided edges** (Skip when / Do not skip when) | borrow the PRECONDITION idea only; drop the Maven boilerplate (`make` is the gate) |
| Steps (P132, P133) | interactive generator procedure | **workflows/** (`write-a-test`, `scenario-to-tests`) | borrow the step shape, drop the user Q&A (stage 6 is AFK) |
| Examples Good/Bad | invented domain classes (Calculator, OrderService) | **Good/Bad** | keep the *pair* shape and the inline "why" comment. **Reject invented code**: R14 #6 requires a pinned file:line in this repo |
| Output Format ANALYZE / CATEGORIZE | how to report findings | **Review checks** (report shape) | borrow CATEGORIZE → "gap matrix per letter" check (P130:238-239) |
| Safeguards | "never X" / "always run Y" | **Review checks** + rules/testing.md MUSTs | **borrow**: each Safeguard → one check with evidence (e.g. P132:490 → "every stub registered inside the feature: grep `stubFor` outside `given:`/setup") |
| "When to use this skill" (P706:38-45) | trigger phrases | router SKILL only | — |
| Table of contents (every Examples block) | per-example index | contents line (R14 #1, >100 lines) | borrow |

Net: plinth has no **Decided edges** section. Its exceptions live inline ("unless explicitly requested", P133:47), which
breaks R14 #9. It also has no **Review checks** with evidence; its Safeguards are checks without a grep or file:line. Those
are the two places our shape is stronger.

---

## 6 · Conflicts and open questions

### 6a · Conflicts (plinth vs our stack or decisions)

| # | plinth says | ours | evidence |
|---|---|---|---|
| X1 | JUnit 5 + AssertJ + Mockito everywhere (P131:17, P321) | Spock for every new test; power asserts in Groovy | `rules/it-testing.md:62,99-101`; CLAUDE.md:4 |
| X2 | `@WebMvcTest` / MockMvc / `MockMvcTester` (P321:218, P322:523) | never MockMvc; `RestTestClient` | CLAUDE.md:233; 0 uses of `@WebMvcTest`/`MockMvcTester` |
| X3 | `@MockitoBean` is the standard (P321:631, P322:523) | fake ports, never `@MockitoBean` | CLAUDE.md:233 (14 ITs still use it: debt, R13 §7) |
| X4 | `static @Container` + `@ServiceConnection` default (P322:20) | singleton `ApplicationContextInitializer`, no `@Container` | `AruviiTestcontainersInitializer.java:15-29` (containers stopped per class; 14 vs 5 properties) |
| X5 | `TestRestTemplate` / RestAssured (P322:171, P323:483, P133:33) | `RestTestClient` (29 files), 0 `TestRestTemplate` | grep |
| X6 | suffix routes phase; `*Spec` silently skipped (P321:705,762; P322:615,711) | source root routes phase (ADR-0009); Gradle runs `*Spec` | ADR-0009; `rules/it-testing.md:12` |
| X7 | happy path only (P133:47, P323:40) | happy path AND failure/edge | CLAUDE.md:221; G9a default |
| X8 | `.feature` + `@acceptance` tags required (P133:41, P323:31) | prose G/W/T in the REQ; no Gherkin runtime | `to-spec/SKILL.md:46` |
| X9 | mock every collaborator + `verifyNoMoreInteractions` (P131:450-494) | `Stub()` for returns, `Mock()` only when the interaction is the behaviour | G9a defaults (`../issues/23:29-30`) |
| X10 | avoid hard-coded values (P131:540) | a literal is the independent oracle | Good pin `RefusalReasonSpec:19-26` (R13 §1) |
| X11 | names `should_X_when_Y` / `@DisplayName` (P131:241) | Spock sentence names; `shouldXxx` legacy JUnit only | G9a default; CLAUDE.md:191 still says `shouldXxx` |
| X12 | Maven compile/verify as blocking gate (every file) | `make` is the front door; no CI | CLAUDE.md "make is the front door" |
| X13 | `@Transactional`/`@Sql` isolation (P322:268) | `AruviiTestReset` truncate + PRESERVE; rollback only in `@DataJpaTest` bases | R13 §5, §7 |
| X14 | confirm with the user before generating (P132:103, P133:74) | `/crq` stage 6 is AFK after `/approved` | R13 §13 |
| X15 | WireMock bodies in mapping files (P132:260-271) | inline `stubFor` in 16 files; 0 use `bodyFileName`/`withBodyFile`/`usingFilesUnderClasspath` | grep; see Q4 |

### 6b · Open questions for the operator (not decided here)

| # | question | why it matters | options |
|---|---|---|---|
| Q1 | Is P130's pinned text the authority, or the longer corpus extraction R13 cited (`…extraction.md:192, :219-236`)? | coverage-design's "independent expected value" and "record gaps as explicit gaps" rules exist only in the extraction | pinned only · extraction (re-pin its version) |
| Q2 | Add "graceful degradation when a dependency is down" (P131:550) as an explicit E-dimension rule? | customer is on-call; failure paths are the triage surface | yes, under coverage-design E · no |
| Q3 | Adopt the inject-`Clock`/`Supplier<UUID>` rule (P321:136) as a production-code rule in code/ refs, or keep it only in unit-tests? | it is a design rule that makes tests possible; #512 was this bug | code/ ref + unit-tests pointer · unit-tests only |
| Q4 | WireMock bodies: inline `stubFor` (our norm) or mapping files + `bodyFileName` (P132)? | X15; affects the integration-tests Good pin | keep inline · files for >N-line bodies · files always |
| Q5 | Adopt "stubs registered per test, never in base/`@BeforeAll`" (P132:490) as a MUST in `rules/testing.md`, or a Review check only? | insertion-order flakiness; nobody checks today | MUST · check only |
| Q6 | P058 tags carry no meaning without a runtime, but its "do not infer the tier from an error case" (:251) is a tier-choice rule. Put it in `strategy.md`'s edges? | a cross-domain borrow from a planning source | strategy edge · scenario-to-tests only |
| Q7 | P706's body (`references/706-…md`) was not supplied. Should the container rules go to a delivery/deploy ref (G9 another domain)? | otherwise 706 maps to nothing | route to delivery/ · drop |
| Q8 | `@DirtiesContext` (P323:89) has 0 uses. Write an edge forbidding it unless justified, or leave it unmentioned? | R14 #15 no-op test | edge · omit |
