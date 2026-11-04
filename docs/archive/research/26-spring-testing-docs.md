# R22 — Spring Framework 7 + Spring Boot 4.1 testing docs vs approved rules (2026-10-02)

Ticket: chiyanram/skills#8 · rules: `19-approved-rules.md` · sources: docs.spring.io only · repo facts from `agent-platform` `origin/master`.

Abbreviations: **SF** = `https://docs.spring.io/spring-framework/reference/testing/` · **SB** = `https://docs.spring.io/spring-boot/reference/testing/`

## 1 · Approved rules vs the docs

| rule | verdict | source | one line |
|---|---|---|---|
| S1 | CONFIRMED | SF `unit.html` | POJOs "testable … instantiated by using the `new` operator, without Spring". |
| S2–S5 | SILENT | — | Spring docs do not address assertion choice, pre-change runs, bug-first tests, or tier-by-error. |
| TM1 | NUANCE | SB `spring-boot-applications.html#testing.spring-boot-applications.with-mock-environment` | Boot offers a middle tier (slices / mock env, "faster") our IT-or-unit model has no slot for. |
| TM2 | NUANCE | SB `…#testing.spring-boot-applications.mocking-beans` | Boot's own example doubles a service with `@MockitoBean`; our "only what we do not own" is a house choice, not Spring's. |
| TM3, TM4 | SILENT | — | No real-LLM or fault-injection guidance. |
| U1 | NUANCE | SF `testcontext-framework/parallel-test-execution.html` | Supports Independent: tests that "change shared services or systems" must not run in parallel. |
| U2 | SILENT | — | Spock-specific. |
| U3 | CONFIRMED | SF `unit.html` | Endorses "stubbing or mocking DAO or repository interfaces" — doubles at a boundary. |
| U4 | SILENT | — | No Clock guidance in the testing chapter. |
| IT1 | SILENT | — | Consistent; docs do not define an IT's scope. |
| IT2 | CONFIRMED + NUANCE | SB `testcontainers.html#testing.testcontainers.junit-extension`, `#testing.testcontainers.service-connections`, `#testing.testcontainers.spring-beans` | `@Container` hazard confirmed: cached context may outlive a stopped container. `@ServiceConnection` = connection details only (matches "5 of 14"). But Boot's recommended fix is containers as `@Bean` / `@ImportTestcontainers`, not a static initializer — see §3. |
| IT3 | CONFIRMED + NUANCE | SB `…#testing.spring-boot-applications.with-running-server`; SB `test-utilities.html` | Boot documents RestTestClient on RANDOM_PORT. Mock env "cannot test lower-level servlet concerns" (error pages) — supports real server. `TestRestTemplate` is **not** deprecated; ban is a house choice. |
| IT4 / IT4b | CONFIRMED | SF `testcontext-framework/ctx-management/caching.html` | Cache key `contextCustomizers` "includes … bean overrides (`@TestBean`, `@MockitoBean`, `@MockitoSpyBean`)". |
| IT4b | NUANCE | SF `annotations/integration-spring/annotation-testbean.html` | Field **name** is part of the key: "name the field consistently to avoid creating unnecessary contexts". |
| IT5 | SILENT | — | No contract-test guidance. |
| K15 | CONFIRMED | SF `…/caching.html` | Any override changes the cache key → new context (Spock `@SpringBean` rides the same mechanism). |
| AT1 | SILENT | — | — |

Repo fact found on the way: `aruvii-test-support/…/AruviiTestClientConfig.java` javadoc says "Boot 4 has no auto-config for RestTestClient". **Contradicted** — SB `#testing.spring-boot-applications.with-running-server` shows `@AutoConfigureRestTestClient` on RANDOM_PORT. The custom `PerRequestJdkClientHttpRequestFactory` (#308) may still justify the hand-rolled bean; unverified whether the auto-config accepts a custom factory.

## 2 · Spring-documented practices our rules miss (candidates — NONE approved)

Put to the operator one by one.

| id | candidate rule (≤25 words) | source | rec | repo today |
|---|---|---|---|---|
| SP1 | Name a `@TestBean` field identically wherever the same bean is overridden; a different field name forks a new cached context. | SF `annotation-testbean.html` ("name the field consistently") | ADOPT | 31 `@TestBean` files, naming unchecked |
| SP2 | A `@TestBean` / fake replaces the bean bare: no `@Transactional`, `@Cacheable`, `@Retryable` or method security. Never override a bean whose advice the IT asserts. | SF `testcontext-framework/bean-overriding.html` §Bean Override and Spring AOP Proxies ("the override instance is a bare object") | ADOPT | — |
| SP3 | Never put `@Transactional` on a RANDOM_PORT IT expecting rollback; server work commits in another thread. Isolation comes from `DatabaseResetExtension`. | SB `…#testing.spring-boot-applications.with-running-server` ("Any transaction initiated on the server does not roll back") | ADOPT | 0 `@Transactional` ITs |
| SP4 | In `@DataJpaTest` specs (rolled back per test) call `em.flush()` before asserting a constraint or write; unflushed changes give false positives. | SB `…#testing.spring-boot-applications.autoconfigured-spring-data-jpa` ("transactional and roll back"); SF `testcontext-framework/tx.html` ("Failing to flush … can produce false positives") | ADOPT | 2 bases: `AgentsRepositoryIT.groovy:23`, `InfraRepositoryIT.groovy:28` |
| SP5 | A slice test (`@DataJpaTest`, `@JdbcTest`) always carries `@AutoConfigureTestDatabase(replace = NONE)` plus the singleton initializer; never the embedded default. | SB `…#testing.spring-boot-applications.autoconfigured-spring-data-jpa` ("prefer … a real database … `@AutoConfigureTestDatabase`") | ADOPT | both bases already comply |
| SP6 | No `@DirtiesContext` without a one-line reason; it closes the context and rebuilds it for every later test with that config. | SF `annotations/integration-spring/annotation-dirtiescontext.html` ("removed from the testing framework's cache and closed") | ADOPT | 0 uses |
| SP7 | When IT time or DB connections grow, log `org.springframework.test.context.cache` at DEBUG and count distinct contexts before raising limits. Cache max 32, LRU. | SF `…/caching.html` (DEBUG stats; "default maximum size of 32") | ADAPT | initializer comment cites ~23 contexts × Hikari 5 |
| SP8 | Shared IT properties go in the singleton initializer, never a per-class `@DynamicPropertySource`; each such method enters the cache key. | SF `…/caching.html` (`contextCustomizers` "includes `@DynamicPropertySource` methods") | ADAPT | 0 annotation uses (one in `it-testing/SKILL.md:112` text) |
| SP9 | Redis consumers, schedulers and other `SmartLifecycle` beans must stay pauseable (`isPauseable()` true) so idle cached contexts stop consuming during other classes' tests. | SF `ctx-management/context-pausing.html` (default `ON_CONTEXT_SWITCH`; `spring.test.context.cache.pause`) | ADAPT | unchecked |
| SP10 | No preemptive timeout (`assertTimeoutPreemptively`) in a transactional test; the body runs in another thread and commits. | SF `testcontext-framework/tx.html` §Preemptive Timeouts | ADOPT (small) | — |
| SP11 | No explicit `@ComponentScan` on a `@SpringBootApplication` used by slices; it disables slice exclude filters. | SB `…#testing.spring-boot-applications.user-configuration-and-slicing` | ADOPT if slices stay | unchecked |
| SP12 | Web-layer-only behaviour (validation, ProblemDetail mapping) may use `@WebMvcTest` instead of a full RANDOM_PORT IT. | SB `…#testing.spring-boot-applications.with-mock-environment` ("consider using `@WebMvcTest`") | ADAPT — **conflicts IT3** (MockMvc ban); operator decides | 0 uses |

Not raised as candidates: `@Bean` / `@ImportTestcontainers` containers (§3); `ContextHierarchy` (unused).

## 3 · What argues against IT2 and IT3

**IT2 (singleton initializer, no `@ServiceConnection`)**

| Spring says | applies to us? |
|---|---|
| Prefer "managing containers as Spring beans or importing container declarations" (SB `testcontainers.html#testing.testcontainers.lifecycle`) | Stated reason: context must stay usable while cached. Our static, never-stopped singleton meets that a different way. Bean containers would also be per-context; ours are shared across ~23 contexts per JVM. |
| `@ServiceConnection` details "take precedence over any connection-related configuration properties" (SB `#testing.testcontainers.service-connections`) | A convenience, not a correctness argument; 9 of our 14 properties still need an initializer. |
| Docs never show a static-field `ApplicationContextInitializer` for Testcontainers | Undocumented pattern, not a forbidden one: Framework documents initializers (SF `ctx-management/initializers.html`), and they are part of the cache key. |

**Plainly: the docs prefer a different mechanism; their stated reason does not hold against ours. No contradiction.**

**IT3 (RestTestClient on RANDOM_PORT, never MockMvc / TestRestTemplate)**

| Spring says | weight |
|---|---|
| Mock environment is faster; `@WebMvcTest` recommended for web-layer focus (SB `#testing.spring-boot-applications.with-mock-environment`) | Real: speed cost of full RANDOM_PORT for pure web-layer cases (SP12). |
| RANDOM_PORT loses test-transaction rollback (SB `#…with-running-server`) | Already paid; `DatabaseResetExtension` replaces it. |
| `TestRestTemplate` is active, not deprecated (SB `test-utilities.html`) | Ban stays a house choice, not a Spring one. |
| Boot ships `@AutoConfigureRestTestClient` | Against our **hand-rolled bean's javadoc**, not against IT3. |

**Plainly: nothing argues RestTestClient is wrong; Spring argues a faster slice tier exists, which IT3 deliberately excludes.**
