# R33 · Spring core rules — beans, configuration, lifecycle (Boot 4.1.1 / Framework 7.0)

Ticket: `chiyanram/skills#77` (part of map #9 "One rulebook", feeds #33 G9b; re-checks approved LY6, LY7). Read 2026-10-03.
Inputs: R32 `research/50-spring-ai-sources.md` §1 (source ranking), `research/49-g9b-candidates.md` (format, LY6/LY7), `research/19-approved-rules.md` (ledger), `research/00-reference-format.md` (house rules).
Machine copy for the review page: `review/r33.json` (schema of `review/planning.json`). **Nothing here is approved.**

Abbrev: **AP** = agent-platform `origin/master` @ `772736bf` (2026-10-03 11:15 UTC), read with `git show`/`git grep` only ·
`…/` = `src/main/java/ai/aruvii/` inside a module · **BOOT** = docs.spring.io/spring-boot/reference (served version 4.1.1) ·
**FW** = docs.spring.io/spring-framework/reference (served 7.0.9) · **pl 301** = `REF/jabrena-plinth/skills/301-frameworks-spring-boot-core/references/301-frameworks-spring-boot-core.md` @ `5e338bb` ·
**SBS** = `rrezartprebreza/spring-boot-skills` @ `f0c06a0` (local clone `c43b0b6`; `configuration-properties/SKILL.md` byte-identical to origin head, checked with `gh api`).

## 0. What we do today (AP, `src/main` only, Java)

| Idiom | Count | Where / note |
|---|---|---|
| Field `@Autowired` | **0** | none in production code (316 hits are tests) |
| Setter / optional `@Autowired(required=false)` | 5 | `GuardrailPipeline.java:43-50` (3 setters), `PiiRedactor.java:46-57` (no-arg ctor + setter), `MockResultResolver.java:42-49` (on a ctor, plus a no-arg ctor) |
| `@Autowired` on one of two constructors | 5 | `RedisConsumerGroup.java:62`, `StreamBacklogJob.java:48`, `WebhookCallbackSender.java:35`, `LlmFakeGenerator.java:36`; `PresidioNerClient.java:37` (single ctor — redundant) |
| `ObjectProvider` | 29 | cycle-cut and multi-bean; `@Lazy ObjectProvider` twice (`AgentsAutoConfiguration.java:145`, `ToolsAutoConfiguration.java:194`) |
| `@Configuration` | 24 | **0** with `proxyBeanMethods = false`; **0** inter-bean method calls (script over all 24 files) |
| Classes named `*AutoConfiguration` | 8 | all plain `@Configuration`, **component-scanned** (both apps scan `ai.aruvii`, `AruviiApiApplication.java:7`, `AruviiWorkerApplication.java:9`); no `AutoConfiguration.imports` file anywhere |
| `@ConditionalOnMissingBean` | 15 | all on scanned `@Configuration` classes — the case BOOT warns about (SC7) |
| `@ConditionalOnProperty` | 4 | one on an env-var name: `PresidioNerClient.java:25` `("NER_SERVICE_URL")` |
| `@ConfigurationProperties` | 3 records | `PlatformConfigProperties.java:7`, `OllamaChatProperties.java:13`, `WorkerStreamsProperties.java:17`; 2 of 3 validate in the compact constructor; 0 use `@Validated` |
| `@Value` | 34 | groups split across classes (SC12); 4 `System.getenv` reads beside them (SC13) |
| `@Profile` / `application-*.yml` | **0 / 0** | environment differences come from env vars + `spring.config.import: optional:configtree:/run/secrets/` (`aruvii-*/src/main/resources/application.yml:20` worker, `:13` api) |
| `@PostConstruct` | 7 | 5 do I/O or start containers (SC18) |
| `ApplicationRunner` / `@EventListener(ApplicationReadyEvent)` | 2 / 5 | consumer loops start on ready (SC19) |
| `SmartLifecycle` | 0 | shutdown is `WorkerDrain` on `ContextClosedEvent`, deliberate (SC20 edge) |
| `@Transactional` | 93 | 1 real self-invocation (SC22) |
| Lazy init / overriding / circular refs | off / off / off | `allow-bean-definition-overriding=true` only in 7 worker ITs |
| Virtual threads / keep-alive | on / on (worker) | matches BOOT §Virtual threads advice |
| AOT / native | none | no `processAot`, no GraalVM plugin |

## 1. Sources — why each is strong, how it is built

### 1.1 Spring Boot reference 4.1.1 (primary)
**Built as** a user guide per feature, with Java + Kotlin listings for every claim and an explicit "we recommend" voice
(e.g. "We generally recommend using constructor injection", `using/spring-beans-and-dependency-injection.html`).
It **enforces nothing**, but it states *why* in the same paragraph, and its own listings are the de-facto standard: every
configuration class in the Boot docs is written `@Configuration(proxyBeanMethods = false)`.
**What makes it strong for us:** it is the only source that explains the *ordering* rules behind conditions
("we recommend using only `@ConditionalOnBean` and `@ConditionalOnMissingBean` annotations on auto-configuration classes
(since these are guaranteed to load after any user-defined bean definitions have been added)" — `features/developing-auto-configuration.html#…bean-conditions`),
the readiness contract of runners vs. `@PostConstruct` (`features/spring-application.html#…readiness-state`),
the record binding semantics (`@DefaultValue`, constructor binding needs `@EnableConfigurationProperties` or scanning,
"we recommend that `@ConfigurationProperties` only deal with the environment") and the `@Value` vs
`@ConfigurationProperties` comparison table (`features/external-config.html`). Its testing chapter adds the one
testing fact that changes a production rule: the `@SpringBootApplication` class is every slice test's configuration, so
area-specific `@Enable*` must not sit on it (`testing/spring-boot-applications.html#…user-configuration-and-slicing`).
Its internal style rules for property metadata ("Use `Duration` rather than `long`") are rare first-party conventions.

### 1.2 Spring Framework reference 7.0 (primary)
**Built as** a container specification: each mechanism (CGLIB config classes, "lite" mode, lifecycle callbacks,
proxying, AOT) is explained from how the container works, then the consequence. **Why it is strong:** it gives the
*mechanism*, so rules derived from it survive edge cases. Key passages:
- `core/beans/java/basic-concepts.html` — lite mode: `@Bean` methods "are not meant to declare inter-bean dependencies
  at all"; every call "can be expressed through a factory method argument instead". This is the basis for SC5.
- `core/beans/dependencies/factory-collaborators.html` — constructors for mandatory deps, setters only for optional deps
  "that can be assigned reasonable default values … Otherwise, not-null checks must be performed everywhere"; a large
  argument list "is a bad code smell"; circular constructor deps fail with `BeanCurrentlyInCreationException`.
- `core/beans/factory-nature.html` — `@PostConstruct` runs "within the container's singleton creation lock … only meant
  for validating the configuration state … Otherwise there is a risk for an initialization deadlock"; expensive work goes
  to `SmartInitializingSingleton`, `ContextRefreshedEvent` or `SmartLifecycle`.
- `core/aop/proxying.html` + `data-access/transaction/declarative/annotations.html` — self-invocation bypasses advice;
  "the best approach … is to refactor your code such that the self invocation does not happen"; `AopContext` "highly
  discouraged". Since 6.0, protected/package-private methods are transactional on class proxies.
- `core/aot.html#…best-practices` — avoid multiple constructors (flag the one with `@Autowired`), expose the most
  precise `@Bean` type, avoid circular dependencies (AOT context "will fail to start").
- `core/beans/annotation-config/autowired-primary.html` — `@Fallback` (6.2+): a default candidate that loses to any
  regular bean without ordering tricks. `core/beans/java/composing-configuration-classes.html` — `@Bean(bootstrap=BACKGROUND)`.

### 1.3 Spring team engineering record (primary context: *why* the docs say it)
- **spring-boot#9068** "Use `@Configuration(proxyBeanMethods=false)` wherever possible" — opened by **Phil Webb** (2017):
  CGLIB proxying of every config class "is potentially quite an expensive operation and is unnecessary". **Stéphane
  Nicoll** objected to the first design (`@Component` instead of `@Configuration` reads "very odd"), which produced the
  `proxyBeanMethods` attribute in Framework 5.2; **Andy Wilkinson** measured ~0.2–0.4 s startup gain on the WebFlux sample
  and listed the few Boot classes that still needed proxying because they call `@Bean` methods directly. Lesson: the
  attribute is safe exactly when no `@Bean` method calls another — which we measured is true of all 24 AP classes.
- **Josh Long**, "Bootiful Spring Boot 3.4: Spring Framework" (spring.io blog, 2024-11-24): `@Fallback` is the mirror of
  `@Primary` — Spring picks the fallback only "if Spring has no better choice". Basis for OQ-SC1 option (b).
- **Juergen Hoeller**, "Spring Framework 6.2 Core Container Revisited" (Spring I/O 2024 slides): `@Fallback`, background
  bootstrap — same features, from the project lead.
- **Sébastien Deleuze**, "Null Safety in Java with JSpecify and NullAway" (Spring I/O 2025): Framework 7 deprecates
  `org.springframework.lang` nullness for JSpecify. Not a new rule here — it is input to the open decision OQ-R27-6 (TY1 gate).
- Boot 4.0 migration guide (GitHub wiki): modular jars (`spring-boot-<tech>`, auto-config packages relocated — e.g.
  `org.springframework.boot.security.autoconfigure.UserDetailsServiceAutoConfiguration` as imported at
  `AruviiWorkerApplication.java:5`), `@MockBean` removed for `@MockitoBean`.

### 1.4 Industry blogs (secondary)
- **Oliver Drotbohm**, "Why field injection is evil" (odrotbohm.de, 2013; Spring Data lead). Argument structure: field
  injection lets callers build an object "in an invalid state"; it hides mandatory dependencies; the pain of a long
  constructor is a *feature* that signals too many responsibilities; constructor injection makes tests plain `new`.
  Setter injection only for optional deps. It is the origin of the community rule LY6 encodes. Baeldung not used —
  every claim here has a first-party source.

### 1.5 pl 301 `frameworks-spring-boot-core` (secondary, rule-shaped)
**Built as** 15 titled examples, each "Title / Description / Good / Bad", wrapped in a Maven-only compile gate
(`./mvnw compile` MANDATORY) and an ANALYZE→CATEGORIZE→APPLY output contract. **Strong because** every rule has a
Bad next to the Good, and it bundles traps agents actually hit (self-invocation in Ex 2, `@Enable*` off the main class in
Ex 1, `@Validated` records in Ex 11). **Weak where it disagrees with the reference:**
| pl 301 | Reference says | Our call |
|---|---|---|
| Ex 3 Good: heavy DB migration in `@EventListener(ApplicationReadyEvent)` | BOOT: "Event listeners should not run potentially lengthy tasks … Consider using application and command-line runners instead" | follow BOOT (SC19) |
| Ex 6 Good: `@ConditionalOnMissingBean` in a user `@Profile` config | BOOT: use bean conditions only on auto-configuration classes | follow BOOT (SC7) |
| Ex 4/6/15: `@Profile("!test")`, `@Profile("production")` configs | allowed, but Ex 15 itself warns profiles "leak test doubles" | we use no profiles (OQ-SC3) |
| Ex 12: set `server.shutdown: graceful` | BOOT 4.1: "Graceful shutdown is enabled by default" | stale; drop |
| Ex 13 Bad: a `ThreadPoolTaskExecutor` under virtual threads is "pool-within-pool" | BOOT: with virtual threads Boot-managed pool *properties* have no effect; an explicit pool is a deliberate bound | overstated; drop |
| Ex 15: "Prefer `@MockBean`" | removed in Boot 4.0 | stale |
| Targets Boot **4.0.x**, Maven | we run 4.1.1, Gradle | strip workflow |

### 1.6 SBS `spring-boot-4/configuration-properties`, `transactional-patterns`, `null-safety` (secondary, gotcha-shaped)
**Built as** short skills (59 lines for config-props) ending in a **Gotchas** list written as observed agent mistakes
("Agent defines a properties record but never registers it", "Agent adds a default credential"), plus "Official sources"
links and an `evaluations/cases.json` with graded criteria (e.g. case `configuration-properties`: "Reject missing URL,
non-positive timeout and excessive retries … Test context startup failure"). **Strong because** it is the only pack
written for Boot 4/Framework 7 and phrased as the failure an agent makes — the exact shape our review checks need.
Unique facts: record `toString` exposes a secret component; `@NotNull` does not reject a zero `Duration`; verify binding
with `ApplicationContextRunner`; Framework 7 `@Retryable` must sit on a caller bean outside `@Transactional`.
**Weak:** single author, no Bad from a real codebase, Maven/Lombok examples (`@RequiredArgsConstructor`).

### 1.7 Anthropic skill-authoring guidance (how to write these rules)
`platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` §"Concise is key": "Only add context Claude
doesn't already have"; §"Set appropriate degrees of freedom": low freedom (exact steps, scripts) where operations are
"fragile and error-prone". Applied here: we do **not** restate generic Spring knowledge (stereotypes, what a singleton
is, `@SpringBootApplication` basics — pl 301 Ex 1/2/5 dropped); we keep rules where the model's default is wrong *for
this repo* (scanned `*AutoConfiguration`, `@PostConstruct` containers, split `@Value` groups) and make the fragile ones
mechanical (SC5 grep, SC22 self-call script, SC10 runner test).

## 2. Candidate rules (prefix SC)

Kind: **rule** (reviewer judges) · **gated** (script/test decides) · **decision** · **drop**. Good/Bad are real AP code unless marked *adapted*.

### Group A — bean creation and wiring

| id | rule (≤30 words) | source (docs first) | our state | kind | recommend |
|---|---|---|---|---|---|
| **SC1** | Give a bean one constructor. When a test-only second constructor exists, put `@Autowired` on the one Spring uses; never on a single constructor. | FW `core/aot.html` §Avoid Multiple Constructors; BOOT `using/spring-beans-and-dependency-injection.html` ("If a bean has more than one constructor, you will need to mark the one…") | 4 correct (`RedisConsumerGroup.java:62`, `StreamBacklogJob.java:48`, `WebhookCallbackSender.java:35`, `LlmFakeGenerator.java:36`); 1 redundant (`PresidioNerClient.java:37`) | rule (NIT) | **fold into LY6** as its second sentence; no separate id |
| **SC2** | A dependency cycle is a design error: cut it. If it cannot be cut, hold an `ObjectProvider<T>` field, resolve it at call time, and name the cycle in a comment. | FW `factory-collaborators.html` §Circular dependencies; FW `core/aot.html` §Avoid Circular Dependencies; BOOT property `spring.main.allow-circular-references` default `false` | one cycle (ChatOrchestrator → ToolService → AgentToolHandler → AgentChatPort), cut correctly at `AgentToolHandler.java:32-43,122-125`; cut wrongly at `AgentsAutoConfiguration.java:143-148` (`@Lazy` on an `ObjectProvider`, resolved inside the factory, throwing stub on absence) | rule | adopt |
| **SC3** | Never put `@Lazy` on an `ObjectProvider`, and never enable `spring.main.lazy-initialization`; laziness hides wiring failures until first use. | BOOT `spring-application.html` §Lazy Initialization ("can delay the discovery of a problem"); FW `classpath-scanning.html` (`ObjectProvider` is the lazy form) | `@Lazy ObjectProvider` at `AgentsAutoConfiguration.java:145`, `ToolsAutoConfiguration.java:194`; global lazy init off | rule (NIT) | adopt, merged with SC2 as one rule if the operator prefers fewer ids |
| **SC4** | Two beans of one type: mark the real one `@Primary` only when both must exist; mark a stand-in default `@Fallback`. Never add `@Primary` to win a condition race. | FW `autowired-primary.html` (`@Primary`, `@Fallback` 6.2); Josh Long, spring.io blog 2024-11-24 | `@Primary` added to `GlobalTrustStore.java:38`, `JdbcSslAdapter.java:24` as the S5.6 fix for a stub "occasionally winning" (`.claude/SPRINTS.md:404`); `AgentsAutoConfiguration.java:78` `@Primary` vs `ToolsAutoConfiguration.java:91-95` default; `CompositeApprovalNotificationAdapter.java:17` legit composite | rule | adopt **if OQ-SC1 = (b)**; else drop |

**Good / Bad — SC2** (real)
```java
// Good — aruvii-tools/…/tools/infrastructure/handlers/AgentToolHandler.java:32-43,122-123
 * <p>Uses an {@link ObjectProvider} for {@link AgentChatPort} to break the circular
 * dependency: ChatOrchestrator → ToolService → AgentToolHandler → AgentChatPort
    private final ObjectProvider<AgentChatPort> chatPortProvider;
    public AgentToolHandler(ObjectProvider<AgentChatPort> chatPortProvider) {
        this.chatPortProvider = chatPortProvider;
    }
        AgentChatPort chatPort = chatPortProvider.getIfAvailable();   // at call time
```
```java
// Bad — aruvii-agents/…/agents/infrastructure/AgentsAutoConfiguration.java:142-148
    @Bean
    public PipelineExecutionService pipelineExecutionService(
            PipelineRepository pipelineRepository,
            @Lazy ObjectProvider<AgentChatPort> chatPortProvider) {      // @Lazy adds nothing
        AgentChatPort chatPort = chatPortProvider.getIfAvailable(          // resolved now, not at use
                () -> req -> { throw new UnsupportedOperationException("AgentChatPort not available in this context"); });
        return new PipelineExecutionService(pipelineRepository, chatPort);
```
Why: the provider is consumed during bean creation, so it does not cut the cycle, and a missing bean becomes a stub that fails at runtime instead of at startup. **This is LY6's currently cited Good** (§3).

### Group B — `@Configuration`, module wiring, conditions

| id | rule | source | our state | kind | recommend |
|---|---|---|---|---|---|
| **SC5** | Write every configuration class `@Configuration(proxyBeanMethods = false)`; take collaborators as `@Bean` method parameters; never call another `@Bean` method. | FW `basic-concepts.html` (lite mode), FW `configuration-annotation.html`; BOOT listings throughout; spring-boot#9068 (Webb, Nicoll, Wilkinson) | 24/24 classes proxied; **0** inter-bean calls → switch is behaviour-neutral | gated (grep: `@Configuration$` without the attribute) | adopt; sweep per OQ-SC6 |
| **SC6** | A `@Bean` method returns the most specific type it builds. | FW `core/aot.html` §Expose the Most Precise Bean Type; BOOT bean conditions ("provide as much type information as possible") | most `@Bean` methods return the port (`AgentsAutoConfiguration.java:53` returns `AgentRepository`, builds `AgentRepositoryAdapter`) | drop | **drop** — matters for AOT and for type-inferred conditions; we run no AOT and every condition names its port type explicitly; returning the port is our hexagonal contract (LY2) |
| **SC7** | A replaceable default bean (`@ConditionalOnMissingBean` stub) lives only where its evaluation order is guaranteed — see OQ-SC1 for the mechanism. | BOOT `developing-auto-configuration.html` §Bean Conditions ("You need to be very careful about the order … we recommend using only `@ConditionalOnBean` and `@ConditionalOnMissingBean` annotations on auto-configuration classes"); §Locating ("never the target of component scanning") | **15** `@ConditionalOnMissingBean` on scanned `@Configuration`; real incident S5.6 (`.claude/SPRINTS.md:404`: fallbacks "occasionally winning over the platform beans" → PKIX failures); safety of the provider-delete guard rests on it (`NoAgentCountAdapter.java:15-21`) | decision → rule | adopt after OQ-SC1 |
| **SC8** | Put feature switches (`@EnableScheduling`, `@EnableAsync`, `@Enable*Auditing`) on a dedicated `@Configuration`, never on the `@SpringBootApplication` class. | BOOT `testing/spring-boot-applications.html` §User Configuration and Slicing; pl 301 Ex 1 | Bad `AruviiWorkerApplication.java:9-11`; Good `JpaConfig.java:8-11`, `SecurityConfig.java:20-22`, `WorkerSchedulingConfig.java:13` | rule | adopt |
| **SC9** | Every conditional bean has an `ApplicationContextRunner` spec that proves both branches: it applies alone, and it backs off when the real bean is present. | BOOT `developing-auto-configuration.html` §Testing your Auto-configuration; SBS config-props §Verification | 2 runner specs exist (`WorkerStreamsStartupSpec.groovy:16-49`, `OllamaNumPredictStartupSpec.groovy`); **none** for the 15 defaults or 4 property conditions; one full-context guard (`ToolTrustStoreWiringIT`, per SPRINTS.md:404) | gated (test) — testing rule that changes production wiring | adopt |
| **SC10** | `@ConditionalOnProperty` names a kebab-case key under `aruvii.` and states `havingValue` and `matchIfMissing`. | BOOT `developing-auto-configuration.html` §Property Conditions, §Configuration keys ("use a unique namespace"); BOOT `external-config.html` (canonical form) | Good `SingaporePiiPolicy.java:21`, `ActivityClassifier.java:44`, `LitellmPricingRefreshJob.java:40`; Bad `PresidioNerClient.java:25` `@ConditionalOnProperty("NER_SERVICE_URL")` | rule (NIT) | adopt; merge into SC13 if fewer ids wanted |

**Good / Bad — SC8** (real)
```java
// Bad — aruvii-worker/…/AruviiWorkerApplication.java:9-12   (every slice test now enables scheduling + async)
@SpringBootApplication(exclude = {UserDetailsServiceAutoConfiguration.class})
@EnableScheduling
@EnableAsync
public class AruviiWorkerApplication {
```
```java
// Good — aruvii-infra/…/infra/config/JpaConfig.java:8-11
@Configuration
@EnableTransactionManagement
@EnableJpaAuditing
@EnableJpaRepositories(basePackages = {
```

**Bad — SC7** (real; Good waits for OQ-SC1)
```java
// aruvii-tools/…/tools/infrastructure/ToolsAutoConfiguration.java:91-95  — scanned config, default stub
    @Bean("agentCountByToolPortDefault")
    @ConditionalOnMissingBean(AgentCountByToolPort.class)
    public AgentCountByToolPort agentCountByToolPortDefault() {
        return toolId -> 0L;
    }
// …and the real bean needed @Primary to be sure it wins — AgentsAutoConfiguration.java:78-83
```
Whether the stub registers depends on which scanned config class is parsed first; S5.6 shipped a PKIX bug from exactly this.

### Group C — configuration properties and environment

| id | rule | source | our state | kind | recommend |
|---|---|---|---|---|---|
| **LY7′** | (sharpened LY7) Grouped settings bind to one `@ConfigurationProperties` record; a key is bound in one place, and other readers inject that record. | BOOT `external-config.html` §`@ConfigurationProperties` vs `@Value` ("If you define a set of configuration keys for your own components, we recommend you group them in a POJO annotated with `@ConfigurationProperties`") | see §3 | rule | replace LY7 text (operator re-approves) |
| **SC11** | Register a properties record with `@EnableConfigurationProperties` on the module's configuration class; never also as `@Component` or `@Bean`. | BOOT `external-config.html` §Constructor Binding ("You cannot use constructor binding with beans that are created by the regular Spring mechanisms"), §Enabling; SBS gotcha "never registers it" | Good `PlatformAutoConfiguration.java:14-15`, `OllamaChatConfig.java:6-7`, `WorkerStreamsConfig.java:28-29` | rule (NIT) | adopt as review check only (we already comply; the trap is agent-made) |
| **SC12** | A key read in two classes is a finding: move it into the owning record. | BOOT §`@ConfigurationProperties` vs `@Value`; BOOT §Default Values ("not reflected in the Environment") | `aruvii.activity.ollama.*` read in 3 classes with **two defaults for one key** (`timeout-ms`: 5000 at `AdminActivityClient.java:46`, 1500 at `OllamaActivityClient.java:45`); `aruvii.master-key` read 4 ways (`PlatformConfigProperties.java:9`, `ErasureConfig.java:16`, `ProvidersAutoConfiguration.java:32`, `ToolsAutoConfiguration.java:82`); `aruvii.eval.*` duplicated in api and worker `EvalTimeoutsConfig.java:19-22` | rule (review check) | adopt — this is the measurable core of LY7′ |
| **SC13** | Read configuration only through binding or the `Environment`: keys are kebab-case under `aruvii.`; never `System.getenv` or an env-var name in `@Value`. | BOOT `external-config.html` §Relaxed Binding, §Binding From Environment Variables, §Using Configuration Trees, `@Value` canonical-form note; BOOT §Configuration keys | Bad `System.getenv`: `SetupService.java:177,289`, `PlatformAutoConfiguration.java:31`, `WorkerLicenseBridgeConfig.java:41`; env names in `@Value`: `HealthController.java:45-46`, `NerSidecarHealthIndicator.java:26`, `PresidioNerClient.java:38` | rule | adopt — `System.getenv` skips the `configtree:/run/secrets/` import both apps declare, and tests cannot override it with properties |
| **SC14** | Times and sizes bind as `Duration`/`DataSize` with a unit in the value (`2s`), never a `long` named `*-ms`/`*-seconds`. | BOOT `external-config.html` §Converting Durations; BOOT internal key rules ("Use `Duration` rather than `long`"); SBS ("Use explicit units") | Good `WorkerStreamsProperties.java:22`, `EvalTimeoutsConfig.java:19-22`; Bad `OllamaActivityClient.java:45` `timeout-ms` long, `AdminActivityClient.java:46`, `RedisConsumerGroup.java:66` `idle-floor-seconds` long | rule (NIT) | adopt |
| **SC15** | A settings record rejects bad values at startup with a message naming the key, and a runner spec proves it. | BOOT §`@ConfigurationProperties` Validation; pl 301 Ex 11; SBS §Verification ("assert … startup failure on missing or invalid settings"; `@NotNull` does not reject zero `Duration`) | Good `WorkerStreamsProperties.java:26-35` + `WorkerStreamsStartupSpec.groovy:43-49`; `OllamaChatProperties.java:18-25` + `OllamaNumPredictStartupSpec`; none on `PlatformConfigProperties` | rule | adopt; style per OQ-SC5 |
| **SC16** | No default for a secret or a required endpoint: absence fails startup, or selects a named degraded mode that logs once at WARN. | SBS config-props ("missing credentials or required endpoints should fail startup"; gotcha "adds a default credential"); BOOT silent | `aruvii.master-key` defaults to empty (`application.yml:104` api, `:72` worker) → `CredentialEncryptor.java:22-25` switches to **plaintext passthrough** silently; datasource password default `ARUVII_internal` (`application.yml:25` worker, `:18` api) | rule | adopt; master-key behaviour is OQ-SC4 |
| **SC17** | Never make a secret a component of a `@ConfigurationProperties` record; record `toString` prints it. | SBS config-props ("generated toString can expose secrets") | Bad `PlatformConfigProperties.java:9` `masterKey` | rule (NIT) | adopt as review check; fix rides with SC12 |

**Good / Bad — SC12** (real)
```java
// Bad — one key, two defaults. aruvii-api/…/api/activity/AdminActivityClient.java:44-46
            @Value("${aruvii.activity.ollama.base-url:http://localhost:11434}") String baseUrl,
            @Value("${aruvii.activity.ollama.model:qwen3:1.7b}") String model,
            @Value("${aruvii.activity.ollama.timeout-ms:5000}") long timeoutMs) {
// aruvii-worker/…/worker/activity/OllamaActivityClient.java:43-45
            @Value("${aruvii.activity.ollama.timeout-ms:1500}") long timeoutMs) {
```
```java
// Good — aruvii-worker/…/worker/stream/WorkerStreamsProperties.java:17-30
@ConfigurationProperties(prefix = "aruvii.worker.streams")
public record WorkerStreamsProperties(Stream chat,
                                      Stream task,
                                      Stream eval,
                                      Stream promptTest,
                                      Duration drainTimeout) {
    public WorkerStreamsProperties {
        if (drainTimeout.isZero() || drainTimeout.isNegative()) {
            throw new IllegalArgumentException(
                PREFIX + "drain-timeout must be more than zero, but was " + drainTimeout
```

**Bad — SC13** (real)
```java
// aruvii-platform/…/platform/infrastructure/PlatformAutoConfiguration.java:29-33
    @Bean
    public LicenseValidator licenseValidator() {
        String key = System.getenv("ARUVII_LICENSE_PUBLIC_KEY");   // invisible to configtree, properties, tests
        return new LicenseValidator((key != null && !key.isBlank()) ? key : DEFAULT_PUBLIC_KEY);
    }
```

### Group D — lifecycle and startup

| id | rule | source | our state | kind | recommend |
|---|---|---|---|---|---|
| **SC18** | `@PostConstruct` only checks injected state or builds in-memory structures; no I/O, no calls into other beans, no thread or container start. | FW `factory-nature.html` §Initialization Callbacks (creation lock, "risk for an initialization deadlock"); FW tx annotations ("should not rely on this feature in your initialization code — for example, in a `@PostConstruct` method"); BOOT §Readiness ("instead of using Spring component lifecycle callbacks such as `@PostConstruct`") | Bad: `GlobalTrustStore.java:56-59` (DB read via repo port), `ChatResponseSubscriber.java:44-48` and `RagIngestSubscriber.java:55-59` (start Redis containers), `KafkaTriggerManager.java:59-62` (starts Kafka consumer), `JdbcSslAdapter.java:36-39` (sets a static global) | rule | adopt |
| **SC19** | Startup work that must finish before traffic runs in an `ApplicationRunner`; work that may finish later is handed to another thread from `@EventListener(ApplicationReadyEvent)`, which returns at once. | BOOT `spring-application.html` §Readiness State, §Application Events ("Event listeners should not run potentially lengthy tasks"), §Using the ApplicationRunner | Good `AdminAutoSeeder.java:15` (runner), `TrustUpgradeCheckJob.java:58-61` (virtual thread), `ChatStreamConsumer.java:63-68` (starts loops); contradicts pl 301 Ex 3 | rule | adopt |
| **SC20** | A component that starts and stops background work (listener container, consumer loop) is a Spring-managed `SmartLifecycle` bean, not `new`-ed and started in `@PostConstruct`. | FW `factory-nature.html` §Startup and Shutdown Callbacks (phases, 30 s per phase); BOOT `web/graceful-shutdown.html` (runs "in the earliest phase of stopping SmartLifecycle beans") | Bad `ChatResponseSubscriber.java:38-53` (`new RedisMessageListenerContainer()` — itself a `SmartLifecycle` — hidden from the context, driven by `@PostConstruct/@PreDestroy`); decided edge: `WorkerDrain.java:18-30` uses `ContextClosedEvent` on purpose (runs before any lifecycle stop, keeps pools alive) | rule + decided edge | adopt with the `WorkerDrain` edge written down |

**Good / Bad — SC18** (real)
```java
// Bad — aruvii-api/…/api/chat/ChatResponseSubscriber.java:38-48
    public ChatResponseSubscriber(RedisConnectionFactory connectionFactory, ObjectMapper mapper) {
        this.mapper = mapper;
        this.container = new RedisMessageListenerContainer();
        this.container.setConnectionFactory(connectionFactory);
    }

    @PostConstruct
    void start() {
        container.afterPropertiesSet();
        container.start();
    }
```
```java
// Good — aruvii-worker/…/worker/trust/TrustUpgradeCheckJob.java:58-61
    @EventListener(ApplicationReadyEvent.class)
    void onReady() {
        Thread.ofVirtual().name("trust-upgrade-check").start(this::run);
    }
```

### Group E — proxies (`@Transactional`, `@Async`, `@PreAuthorize`, `@Retryable`)

| id | rule | source | our state | kind | recommend |
|---|---|---|---|---|---|
| **SC21** | A proxied annotation works only on a call from another bean. Never call such a method through `this`; move it to a second bean. No self-injection, no `AopContext`. | FW `core/aop/proxying.html` §Understanding AOP Proxies; FW tx §Method visibility and `@Transactional` in proxy mode; FW `autowired.html` (self references "as a last resort only"); pl 301 Ex 2; SBS transactional-patterns | **Bad** `SetupService.java:174-179`: `getEffectiveSecretKey()` (no tx) calls `getOrGenerateSecretKey()` (`@Transactional` at `:165`), so the read-check-write of the signing key runs **without** a transaction on the path `JwtService.java:91` and `OidcController.java:80,106` use; harmless readOnly→readOnly self-calls in `PricingResolverAdapter.java:77-133` | rule + gated (self-call script over files with proxy annotations) | adopt |
| **SC22** | Put `@Retryable` on a caller bean around the `@Transactional` call, never on the same method or bean. | SBS transactional-patterns (Framework 7 `@EnableResilientMethods`); FW proxying | 0 `@Retryable` in AP | drop | **drop for now** — no use; CC8 (retry, group 12) owns retry; add when the first `@Retryable` lands |

**Good / Bad — SC21** (real Bad; Good *adapted*)
```java
// Bad — aruvii-api/…/api/service/SetupService.java:164-179
    @Transactional
    public String getOrGenerateSecretKey() {
        String stored = settings.get(KEY_SECRET);
        if (!stored.isBlank()) return decryptSafe(stored);
        String generated = generateSecureKey();
        settings.set(KEY_SECRET, encryptor.encrypt(generated));
        return generated;
    }
    @Override
    public String getEffectiveSecretKey() {
        String fromEnv = System.getenv("ARUVII_SECRET_KEY");
        if (fromEnv != null && !fromEnv.isBlank()) return fromEnv;
        return getOrGenerateSecretKey();          // this-call: the @Transactional above never applies
    }
```
*Adapted Good:* move `getOrGenerateSecretKey` into a `SecretKeyStore` bean and inject it into `SetupService`; the env lookup becomes a bound property (SC13).

### Dropped from the sources (with reason)

| from | item | reason |
|---|---|---|
| pl 301 Ex 1, 2, 5 | `@SpringBootApplication` alone; stereotype choice; default scanning | the model already does this (§1.7); our apps comply |
| pl 301 Ex 3 | explicit `@Scope` | singleton default; no prototype beans in AP |
| pl 301 Ex 9 | scheduler pool + `ErrorHandler` | belongs to concurrency group 12 (CC*) |
| pl 301 Ex 12, 13 | graceful shutdown yaml; virtual-thread pool warning | stale / overstated (§1.5) |
| pl 301 Ex 14 | jakarta vs javax | already gated by ArchUnit (LY4, `ArchitectureRulesTest` javax rule) |
| pl 301 Ex 15 / BOOT overriding | test bean overriding | test-only; 7 worker ITs set `allow-bean-definition-overriding=true` — a testing-group item, not a production rule |
| SBS null-safety | JSpecify `@NullMarked` | already open as OQ-R27-6 (types group 2); Framework 7 facts recorded in §1.3 for it |
| FW | `@Bean(bootstrap=BACKGROUND)` | no slow singleton measured; revisit with a startup profile |

## 3. Verdicts on approved LY6 and LY7

| id | verdict | why | proposed text |
|---|---|---|---|
| **LY6** | **Agree, sharpen** | FW and BOOT both recommend constructor injection; FW *permits* setters for optional deps "that can be assigned reasonable default values", so "never setter" is stricter than the docs — keep it, because our setter cases are exactly the "not-null checks everywhere" case FW warns about (`GuardrailPipeline.java:35-50` holds three nullable tiers). Two corrections: (1) **its Good is wrong** — `AgentsAutoConfiguration.java:145` is `@Lazy ObjectProvider` resolved in the factory method (SC2 Bad); replace with `AgentToolHandler.java:40-43,122-123`, or `ToolsAutoConfiguration.java:270-275` (`ObjectProvider<RagBackendPort>` → `backends.stream()`) for zero-or-more. (2) add the multi-constructor clause (SC1) and name the no-arg-constructor-plus-setter shape (`PiiRedactor.java:46-57`, `MockResultResolver.java:42-49`) in its Bad list. | "Spring beans take dependencies through one constructor; an optional or zero-or-more collaborator is an `ObjectProvider<T>` resolved at use, never a setter, a no-arg constructor or `@Autowired(required=false)`." (27 words) |
| **LY7** | **Agree, sharpen; raise from NIT** | BOOT says the same in nearly the same words (§`@ConfigurationProperties` vs `@Value`). NIT is too low: AP has one key with **two different defaults** (`timeout-ms` 5000 vs 1500) and the master key read four ways — split `@Value` groups have already produced two truths. The record style is right (BOOT §Constructor Binding: records need no `@ConstructorBinding`; `@DefaultValue` for defaults). Add: one owner per key (SC12), `Duration` types (SC14), startup validation (SC15). Its Good `PlatformConfigProperties.java:7-9` is weak — it holds a secret component (SC17); use `WorkerStreamsProperties.java:17-35`. | "Grouped settings bind to one `@ConfigurationProperties` record that validates at startup; each key is bound in one place; `@Value` only for a single scalar no other class reads." (27 words) |

Neither verdict contradicts the approval; both change the text and the cited Good, so both go back on the review page.

## 4. Open decisions for the operator

| id | decision | options (state now) | what changes | recommend |
|---|---|---|---|---|
| **OQ-SC1** | How a module supplies a default another module may replace | **(a)** real auto-configuration: `@AutoConfiguration` + `META-INF/spring/…AutoConfiguration.imports`, excluded from scanning — BOOT's documented mechanism; needs a scan exclusion because both apps scan `ai.aruvii` (8 classes). **(b)** keep scanned `@Configuration`; defaults become `@Fallback` beans (FW 6.2), conditions removed (15 sites). **(c)** status quo + `@Primary` on winners + context tests. Today: 15 order-dependent conditions, one shipped bug (S5.6). | (a) removes order-dependence and makes the `*AutoConfiguration` names true; larger change, touches packaging. (b) removes order-dependence with one annotation per site; the stub is still instantiated, so warn-on-construct stubs (`NoAgentCountAdapter.java:29-33`) must warn on first use instead. (c) keeps the race; SC4/SC9 only detect it. | **(b)** now: smallest change, order-free, first-party (Hoeller, Josh Long). Rename `*AutoConfiguration` → `*Config` in the same sweep so the name stops promising (a). SC9 tests either way. |
| **OQ-SC2** | Home of the SC rules | (a) new `.agents/skills/code/references/spring.md`, LY6/LY7 target moves there · (b) append to `services.md` + `layering.md` (group 10 today) | (b) mixes container mechanics into service shape; ~15 rules would double `services.md` | **(a)** |
| **OQ-SC3** | Profiles | (a) codify today: no `@Profile`, no `application-<profile>.yml`; environments differ by env vars/configtree; features by `@ConditionalOnProperty` · (b) allow profiles per pl 301 | AP has 0 profiles; pl 301 Ex 15 itself warns profiles leak test doubles | **(a)**, as a decided edge, not a rule |
| **OQ-SC4** | Empty `aruvii.master-key` → credentials stored in plaintext (`CredentialEncryptor.java:22-25`) | (a) intended dev mode — make it explicit (`aruvii.credentials.plaintext-allowed=true`) and fail startup otherwise · (b) always fail startup · (c) keep | security, not Spring core; SC16 cannot be approved cleanly until this is decided | **(a)**; route to security group 13 / #53 |
| **OQ-SC5** | How a settings record validates | (a) compact-constructor checks (AP's 2 records) · (b) `@Validated` + Jakarta constraints (BOOT, pl 301, SBS) · (c) either | (a) needs no validation provider, message names the key, tested by runner specs; (b) is what agents write by default | **(c) with (a) preferred** — SC15 governs the outcome, not the style |
| **OQ-SC6** | SC5 rollout | (a) new and touched classes only · (b) one sweep of 24 classes (behaviour-neutral, 0 inter-bean calls) | small startup gain; sweep is mechanical | **(b)** in the same MR as OQ-SC1 (b) — same files |

## 5. What was read

- **Online, 2026-10-03** (curl + text extraction, versions in page): BOOT 4.1.1 `using/spring-beans-and-dependency-injection`, `using/configuration-classes`, `using/auto-configuration`, `using/structuring-your-code`, `features/external-config` (full), `features/profiles`, `features/developing-auto-configuration` (full), `features/spring-application`, `web/graceful-shutdown`, `packaging/aot`, `testing/spring-boot-applications` §User Configuration and Slicing, appendix application-properties (`spring.main.*`, `spring.lifecycle.*`). FW 7.0.9 `core/beans/java/{basic-concepts,configuration-annotation,bean-annotation,composing-configuration-classes}`, `core/beans/dependencies/{factory-collaborators,factory-lazy-init}`, `core/beans/factory-nature`, `core/beans/factory-scopes`, `core/beans/annotation-config/{autowired,autowired-primary,autowired-qualifiers,postconstruct-and-predestroy-annotations}`, `core/beans/classpath-scanning`, `core/beans/environment`, `core/aop/proxying`, `core/aot`, `data-access/transaction/declarative/annotations`, `core/null-safety`. spring-boot#9068 + comments (`gh api`). Boot 4.0 migration guide (wiki). Josh Long blog 2024-11-24. Drotbohm 2013. Anthropic skill best-practices.
- **Local:** pl 301 SKILL.md + reference (1410 lines, full); SBS `configuration-properties` (SKILL + examples + agents), `transactional-patterns`, `null-safety`, `layered-architecture` head, `evaluations/cases.json` case; `research/45`, `research/44` (format, LY6/LY7 rows), `research/19` (LY rows), `research/00-reference-format.md`, `review/g9b.json` (overlap check: TY1, OQ-R27-6, PS2, LG4, ND-4).
- **AP @ `772736bf`:** `git grep` counts over `*/src/main/*.java` (and tests split out); full reads of `PlatformConfigProperties`, `PlatformAutoConfiguration`, `OllamaChatProperties`, `WorkerStreamsProperties`, `AgentsAutoConfiguration:40-160`, `ToolsAutoConfiguration:75-310`, `ProvidersAutoConfiguration`, `NoAgentCountAdapter`, `GuardrailPipeline:30-75`, `WorkerDrain:1-70`, `WorkerStreamsStartupSpec`, `CredentialEncryptor:1-40`, both `application.yml` heads, `AruviiWorkerApplication`, `JpaConfig`; excerpts of every other cited file; `.claude/SPRINTS.md:385-406`. Two scripts: inter-`@Bean` calls in all 24 `@Configuration` classes (0 found); `this`-calls to proxy-annotated methods (5 found, 1 real).
- **Not read:** Spring Boot 4.1 release notes (wiki page pruned; reference used instead); talk videos (slides/blog only).
