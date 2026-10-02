# R20 · Fakes vs mocks in ITs — does industry back IT4?

Ticket: `issues/35-research-fakes-vs-mocks.md` · Informs: G9a · Researched 2026-10-02.

Rule under test (IT4): *"In an IT swap a collaborator only at an outbound port with a fake port bean
(real in-memory implementation); never @MockitoBean."*

## 0. Premise correction — repo state on `origin/master`

```
@MockitoBean as an annotation      0 files   (git grep '^[[:space:]]*@MockitoBean' origin/master)
"@MockitoBean" in a comment       14 files   (7 ITs + 7 support/Fake* javadocs: "no @MockitoBean")
@TestBean field override          28 files   aruvii-api/src/integrationTest/**
shared @Import(FakePortsConfig)    e.g. AgentEvalControllerIT
```

The "14 ITs still use @MockitoBean" in the brief is a grep of the string, not the annotation. The
live cost question on master is **`@TestBean`**, which the Spring docs put in the cache key exactly
like `@MockitoBean` (see §2). `FakePortsConfig.java:9-12` already says so.

## 1. Sources

| source | position | key reason | URL |
|---|---|---|---|
| SWE at Google ch.13 *Test Doubles* | prefer real, then fakes | "Our first choice for tests is to use the real implementations" · "the best option is often to use a fake" | https://abseil.io/resources/swe-book/html/ch13.html |
| same | fakes, owner-maintained | "The team that owns the real implementation should write and maintain a fake" · "A fake must have its own tests" | same |
| same | stubbing/mocking: limited | "Overuse of stubbing can result in major losses in productivity" · "Stubbing leaks implementation details of your code into your test" | same |
| same | interaction testing: allowed, narrow | "Perform interaction testing only for state-changing functions" | same |
| Google TotT *Don't Overuse Mocks* (Trenk, 2013) | prefer real/fakes | "there may better options than using mocks" when real dep is slow/networked | https://testing.googleblog.com/2013/05/testing-on-toilet-dont-overuse-mocks.html |
| Google TotT *Know Your Test Doubles* (2013) | taxonomy only | body not retrievable by fetch — **unverified**, not cited for a position | https://testing.googleblog.com/2013/07/testing-on-toilet-know-your-test-doubles.html |
| Fowler *Mocks Aren't Stubs* | prefer real; double "if awkward" | classicists "use real objects if possible and a double if it's awkward" · mockist tests "more coupled to the implementation" | https://martinfowler.com/articles/mocksArentStubs.html |
| Fowler *TestDouble* (bliki) | definitional | fakes "have working implementations, but usually take some shortcut" (InMemoryTestDatabase) | https://martinfowler.com/bliki/TestDouble.html |
| Spring Framework ref, *Context Caching* | neutral; states cost | key includes "bean overrides (such as `@TestBean`, `@MockitoBean`, `@MockitoSpyBean` etc.)" | https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/ctx-management/caching.html |
| Spring Framework ref, `@MockitoBean` | mocks fine; mind the key | "make sure to name the fields consistently to avoid creating unnecessary contexts" | https://docs.spring.io/spring-framework/reference/testing/annotations/integration-spring/annotation-mockitobean.html |
| same | prefers a real substitute bean for infra | suggests "Overriding the `CacheManager` bean with a `NoOpCacheManager`" via `@TestBean` | same |
| Spring Boot ref, *Testing Spring Boot Applications* | mocks fine (slice tests) | `@WebMvcTest` "used in combination with `@MockitoBean`" for collaborators | https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html |
| Testcontainers *Introducing Testcontainers* | real deps over in-memory | "In-memory services may not have all the features of your production service" | https://testcontainers.com/guides/introducing-testcontainers/ |
| Testcontainers *WireMock* guide | fake at the wire, not the client | "better to mock the external API interactions at HTTP protocol level" | https://testcontainers.com/guides/testing-rest-api-integrations-using-wiremock/ |

No primary Spring-team blog post on `@MockBean` deprecation/cache was found; secondary posts were
excluded. Kent Beck / Uncle Bob: not researched (no primary source fetched).

## 2. Measurable cost claim — does `@MockitoBean` fragment the context cache?

**Yes, by distinct override set — not per class, and not unique to Mockito.**

```
cache key = MergedContextConfiguration
  ├ classes, locations, initializers, profiles, property sources, loader, parent
  └ contextCustomizers  ← @DynamicPropertySource, @TestBean, @MockitoBean, @MockitoSpyBean
          per override: bean type + qualifiers + FIELD NAME
default max size 32, LRU eviction closes the evicted context
```

- Key component: *Context Caching* page, list item `contextCustomizers` (URL above).
- Field name matters: "Qualifiers, including the name of the field, are used to determine if a
  separate `ApplicationContext` needs to be created" — identical wording on both the `@MockitoBean`
  and `@TestBean` pages.
- Size/eviction: "default maximum size of 32" · "least recently used (LRU) eviction policy".
- Mitigation Spring itself documents: type-level `@MockitoBean(types = …)` in a composed
  annotation (`@SharedMocks`) "to support reuse of mock configuration" — one key for every class
  that carries it.

Implication for IT4: the cost argument is against **per-class overrides of any kind**. A per-class
`@TestBean` fake fragments exactly like a per-class `@MockitoBean`. Only a shared, identical
override set (repo: `@Import(FakePortsConfig)`; Spring: `@SharedMocks`) keeps one context.
Number of contexts actually created on master: **not measured here** — needs a run with
`logging.level.org.springframework.test.context.cache=DEBUG`.

## 3. Where industry disagrees with IT4 — candidate *Decided edges*

Put to the operator one at a time.

| # | edge (≤25 words) | source |
|---|---|---|
| E1 | Third-party HTTP clients: fake at the wire (WireMock/MockServer container), not a port bean — catches marshalling and latency that a port fake skips. | Testcontainers WireMock guide |
| E2 | Error/state injection a fake cannot reach cheaply (timeouts, partial failures): a stub is acceptable to "get the system under test into a certain state". | SWE@Google ch.13, *Stubbing* |
| E3 | Side-effect verification (email sent, message published once): interaction testing is endorsed "only for state-changing functions" — a recording fake satisfies it; a mock is not banned. | SWE@Google ch.13 |
| E4 | Slice tests (`@WebMvcTest`) — Spring Boot's own documented pattern pairs them with `@MockitoBean`; IT4 should say it scopes to full-context ITs only. | Spring Boot testing ref |
| E5 | Cost rule is about override *sets*, not Mockito: a shared `@MockitoBean(types=…)` meta-annotation is cache-neutral; per-class `@TestBean` is not. Reword "why" accordingly. | Spring `@MockitoBean`, *Context Caching* |
| E6 | Fakes need owners and their own contract tests; an untested fake drifts like a mock. IT4 has no such clause. | SWE@Google ch.13 |
| E7 | Spy on a real bean (`@MockitoSpyBean`, WRAP) to assert one call on real behaviour — no fake equivalent; decide allow or ban. | Spring `@MockitoBean` page |

## 4. Verdict — **partly backed**

| IT4 clause | backed? | by |
|---|---|---|
| prefer a real in-memory fake over a mock | **backed** | SWE@Google ch.13, Fowler, TotT |
| swap only at an outbound port | **backed in spirit** (replace awkward/remote collaborators only) | Fowler classicist, TotT |
| "never `@MockitoBean`" (absolute) | **not backed** — Google allows stubs/interaction tests narrowly; Spring Boot documents `@MockitoBean` for slices | ch.13, Boot ref |
| implied cache-cost reason | **backed, but mis-aimed** — applies equally to `@TestBean`; the fix is a shared override set | Spring *Context Caching*, `@TestBean` page |
