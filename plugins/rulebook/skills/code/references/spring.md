# Spring

How a Spring Boot application wires its beans, binds its settings, starts its work and crosses its proxies. Read it
when you write or review a bean, a configuration class, a settings record, a startup hook or a proxied method.

Contents: Rules · When X, use Y · Good / Bad (LY6, LY7, SC21) · Decided edges · Review checks

## Rules

- **LY6** (operator preference, 2026-10-31) — Take dependencies through one constructor; make an optional or
  zero-or-more collaborator an `ObjectProvider<T>` resolved at use, never a setter, a no-arg constructor or
  `@Autowired(required=false)`, because a setter-injected collaborator may be null at every use.
- **SC1** (operator preference, 2026-10-31) — Never use `@Autowired` in production code; give each bean exactly one
  constructor and no test-only second constructor, because a test-only constructor that accepts null hides a production
  wiring mistake.
- **SC2** (operator preference, 2026-10-31) — Cut a dependency cycle; if it cannot be cut, hold an `ObjectProvider<T>`
  field, resolve it at call time and name the cycle in a comment, because a constructor cycle fails startup with
  `BeanCurrentlyInCreationException`.
- **SC3** (operator preference, 2026-10-31) — Never put `@Lazy` on an `ObjectProvider` and never enable
  `spring.main.lazy-initialization`; let wiring fail at startup, because with laziness a missing bean fails at the first
  request instead.
- **SC4** (operator preference, 2026-10-31) — When only one implementation of an interface should run, select it with a
  config flag (`@ConditionalOnProperty`), never with `@Primary`, because `@Primary` builds both beans and leaves the
  choice in code, not configuration.
- **SC9** (operator preference, 2026-10-31) — Give every property-selected bean an `ApplicationContextRunner` spec
  proving each value picks the right bean and a missing value fails startup, because a wrong bean choice otherwise ships
  with no failing test.
- **SC5** (operator preference, 2026-10-31) — Write each configuration class `@Configuration(proxyBeanMethods = false)`
  and take collaborators as `@Bean` method parameters, never another `@Bean` method call, because without the CGLIB
  proxy a direct `@Bean` call builds a second instance of the bean.
- **SC6** (operator preference, 2026-10-31) — Declare a `@Bean` method's return type as the most specific type it
  builds, because before creation the container and type-based conditions see only the declared type.
- **SC8** — Put feature switches (`@EnableScheduling`, `@EnableAsync`, `@Enable*Auditing`) on a dedicated
  `@Configuration`, never on the `@SpringBootApplication` class, because every slice test loads the main class and so
  enables them.
- **LY7** — Bind grouped settings to one `@ConfigurationProperties` record that validates at startup, each key in one
  place; use `@Value` only for a single scalar no other class reads, because split reads give one key two defaults.
- **SC12** — Move a key read in two classes into the record that owns it, because each `@Value` read carries its own
  default, so two reads of one key can disagree.
- **SC11** — Register a properties record with `@EnableConfigurationProperties` on the module's configuration class,
  never also as `@Component` or `@Bean`, because constructor binding does not apply to a record created that way.
- **SC13** (operator preference, 2026-10-31) — Read configuration only through binding or the `Environment`, as
  kebab-case keys under the app's own prefix, never `System.getenv` or an env-var name in `@Value`, because
  `System.getenv` skips configtree secrets and tests cannot override it.
- **SC10** (operator preference, 2026-10-31) — Name a kebab-case key under the app's own prefix in
  `@ConditionalOnProperty`, and state `havingValue` and `matchIfMissing`, because an env-var name skips the bound
  configuration and tests cannot override it.
- **SC14** (operator preference, 2026-10-31) — Bind times and sizes as `Duration` or `DataSize` with a unit in the value
  (`2s`), never a `long` named `*-ms` or `*-seconds`, because a bare number hides its unit, so seconds bind silently as
  milliseconds.
- **SC15** — Make a settings record reject bad values at startup with a message naming the key, and prove it with a
  runner spec, because a missing key otherwise crashes with a bare NullPointerException naming nothing.
- **SC16** — Give a secret or a required endpoint no default: its absence fails startup or selects a named degraded mode
  that logs once at WARN, because a blank encryption-key default silently stores secrets unencrypted.
- **SC17** (operator preference, 2026-10-31) — Keep a secret out of every `@ConfigurationProperties` record, because the
  record's generated `toString` prints the secret.
- **X6** — Never use `@PostConstruct` in main code; put a startup check in the constructor and startup work in an
  `ApplicationRunner` or `SmartLifecycle`, because `@PostConstruct` runs inside the singleton creation lock and risks
  deadlock.
- **SC19** (operator preference, 2026-10-31) — Run startup work that must finish before traffic in an
  `ApplicationRunner`; hand later work to another thread from `@EventListener(ApplicationReadyEvent)`, which returns at
  once, because event listeners must not run lengthy tasks.
- **SC20** (operator preference, 2026-10-31) — Make a component that starts and stops background work (a listener
  container, a consumer loop) a Spring-managed `SmartLifecycle` bean, never `new`-ed and started by hand, because a
  hand-started container misses the context's shutdown phases.
- **SC21** — Call a method with a proxied annotation only from another bean; move it to a second bean, with no
  self-injection and no `AopContext`, because a `this` call bypasses the proxy, so the transaction never starts.
- **SC23** — Put `@Transactional(readOnly = true)` on a service class whose methods mostly read, and plain
  `@Transactional` on each write method, because without the read-only default every query pays for dirty checking.
- **SX18** — Make a static-only class `final` with a private constructor, because Java
  adds a public constructor by default, which lets callers instantiate a class where an instance makes no sense.
- **SX19** (operator preference, 2026-10-31) — Write output through the logger, never `System.out`, `System.err` or
  `printStackTrace()` in main code, because console output bypasses the logger's level and context, so a failed run
  cannot be triaged from the logs.
- **SX14** (operator preference, 2026-10-31) — In a package-private class, make a method `public` only when it
  overrides, because a public method there widens visibility by accident and exposes a method no caller should reach.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a collaborator that may be absent, or zero or more of one type | an `ObjectProvider<T>` field, resolved where it is used, with no `@Lazy` (LY6, SC3) | SF §Constructor-based or setter-based DI: with setter injection "not-null checks must be performed everywhere" · plinth 301 :713 · Jeffallan :189 · resolve at use, no `@Lazy`: operator preference |
| a dependency cycle that cannot be cut | an `ObjectProvider<T>` field resolved at call time, and a comment naming the cycle (SC2) | SF §Circular dependencies: a constructor cycle throws `BeanCurrentlyInCreationException` · the provider and comment: operator preference |
| several implementations of one type, and only one should run | one `@ConditionalOnProperty` value per implementation, exactly one matching, an unset flag failing startup (SC4) | plinth 301 :598-599 (Example 6) selects by `@ConditionalOnProperty` · never `@Primary`: operator preference |
| several settings that belong together | one `@ConfigurationProperties` record (LY7); `@Value` for one scalar no other class reads | SB §@ConfigurationProperties vs. @Value · plinth 301 :429 "avoid scattering many `@Value` fields" · Jeffallan :182 |
| a check on one settings field | a Jakarta constraint, with `@Validated` on the record (SC15) | SB §@ConfigurationProperties Validation · plinth 301 :1170 · a compact-constructor check alone crashes on a missing key with an unnamed NullPointerException |
| a rule across settings fields | a compact-constructor check, beside the field constraints (SC15) | operator preference |
| a startup check on injected state | the constructor (X6) | SF §Initialization Callbacks: `@PostConstruct` runs in the singleton creation lock, "a risk for an initialization deadlock" · plinth 301 :317 "avoid heavy work in `@PostConstruct`" |
| startup work that must finish before traffic | an `ApplicationRunner` (SC19) | SB §Application Events and Listeners: a runner finishes after context refresh, before the app accepts traffic |
| startup work that may finish later | a thread started from an `@EventListener(ApplicationReadyEvent)` that returns at once (SC19) | SB §Application Events and Listeners: "Event listeners should not run potentially lengthy tasks" |
| background work that starts and stops | a `SmartLifecycle` bean (SC20) | SF §Startup and Shutdown Callbacks: `SmartLifecycle` phases |
| a proxied method (such as `@Transactional`) called from its own class | the method on a second bean (SC21) | SF §Understanding AOP Proxies: "self invocation … will bypass the advice" · plinth 311 :1006 (Example 14) |
| a service whose methods mostly read | `@Transactional(readOnly = true)` on the class; plain `@Transactional` on each write method (SC23) | plinth 311 :665-668 (Example 10) · Jeffallan data.md :153 · Spring Data JPA §Transactionality: `SimpleJpaRepository` reads run read-only, so Hibernate skips dirty checks |

Sources: SF = Spring Framework reference, SB = Spring Boot reference (docs.spring.io; one vendor, one source); plinth
301 / 311 = jabrena-plinth `skills/301-frameworks-spring-boot-core` and `311-frameworks-spring-jdbc` references;
Jeffallan = Jeffallan claude-skills `spring-boot-engineer/SKILL.md`. Rules without a row: SC1 one constructor (SF
§Constructor-based DI, plinth 301 :713), the rest operator preference; SC5 SF §Java-based Configuration (CGLIB
subclass); SC6 SF §Using the @Bean Annotation "declare the most specific return type"; SC8 SB §Detecting Test
Configuration, plinth 301 :53; SC11 SB §Constructor Binding, plinth 301 :429, :1170; SC12 as LY7; SC13 and SC10 SB
§Property Placeholders and §Relaxed Binding (kebab-case is canonical); SC14 SB §Converting Durations (a bare `long`
binds as milliseconds); SC15 the runner spec: rrezartprebreza/spring-boot-skills
`spring-boot-4/configuration-properties/SKILL.md:44-46`, giuseppe-trisciuoglio/developer-kit
`unit-test-config-properties/SKILL.md:31,34`; SC16 plinth 301 :1407 "Do not commit secrets", Jeffallan :194 "Hardcode … credentials" (MUST
NOT); SC17 JDK `java.lang.Record#toString` (the implicit string holds each component's name and value); SX18 Checkstyle
`HideUtilityClassConstructor` and `FinalClass`, github/awesome-copilot `instructions/springboot.instructions.md:33`;
SC9, SX14 and SX19 operator preference. `68f § ID — title` is a heading of
`research/68f-neutral-code.md`.

## Good / Bad

Every rule's approved pair: [examples/spring.md](examples/spring.md).

### LY6 — One constructor; an optional collaborator is an `ObjectProvider<T>` resolved at use

**Bad** (neutral)
```java
@Bean
public OverdueReminder overdueReminder(
        InvoiceRepository invoiceRepository,
        ObjectProvider<EmailSender> emailSenderProvider) {
    EmailSender emailSender = emailSenderProvider.getIfAvailable(
            () -> email -> { throw new UnsupportedOperationException("EmailSender not available in this context"); });
    return new OverdueReminder(invoiceRepository, emailSender);
}
```
The provider is resolved while the bean is built, so in orders-api (no EmailSender) it bakes in a throwing stub at
startup.

**Good** (neutral)
```java
@Bean
OverdueReminder overdueReminder(final InvoiceRepository invoiceRepository,
                                final ObjectProvider<EmailSender> emailSenders) {
    return new OverdueReminder(invoiceRepository, emailSenders);
}

// OverdueReminder — resolved where a reminder is sent
private void send(final ReminderEmail email) {
    emailSenders.getObject().send(email);
}
```
The bean holds the provider and resolves it per send, so a missing EmailSender fails at that call, naming the type.
(Pair: 68f § LY6 — One constructor; an optional collaborator is an `ObjectProvider<T>` resolved at use. Real evidence:
ledger row LY6.)

### LY7 — Grouped settings in one validated record; each key bound in one place

**Bad** (neutral)
```java
// orders-api — CheckoutFraudClient
public CheckoutFraudClient(
        @Value("${example.fraud-check.base-url}") String baseUrl,
        @Value("${example.fraud-check.ruleset:default}") String ruleset,
        @Value("${example.fraud-check.timeout:5s}") Duration timeout) {
// billing — PaymentFraudClient
public PaymentFraudClient(
        @Value("${example.fraud-check.base-url}") String baseUrl,
        @Value("${example.fraud-check.ruleset:default}") String ruleset,
        @Value("${example.fraud-check.timeout:1500ms}") Duration timeout) {
```
One key has two defaults, 5000 and 1500 ms, so unset, the two modules run "the same" setting differently.

**Good** (neutral)
```java
@Validated
@ConfigurationProperties("example.fraud-check")
public record FraudCheckProperties(@NotNull URI baseUrl,
                                   @NotBlank String ruleset,
                                   @NotNull Duration connectTimeout,
                                   @NotNull Duration checkoutTimeout,
                                   @NotNull Duration paymentTimeout) {
}

public CheckoutFraudClient(final FraudCheckProperties fraudCheck) {
    this.http = restClient(fraudCheck.baseUrl(), fraudCheck.connectTimeout(), fraudCheck.checkoutTimeout());
}
```
One record is bound once and read by both clients; two real timeouts are two named keys, not one key with two defaults.
(Pair: 68f § LY7 — Grouped settings in one validated record; each key bound in one place. Real evidence: ledger row
LY7.)

### SC21 — A proxied annotation works only on a call from another bean; never through `this`

**Bad** (neutral)
```java
@Transactional
public String getOrGenerateWebhookSecret() {
    String stored = settings.get(KEY_WEBHOOK_SECRET);
    if (!stored.isBlank()) {
        return decryptSafe(stored);
    }
    String generated = generateSecureKey();
    settings.set(KEY_WEBHOOK_SECRET, encryptor.encrypt(generated));
    return generated;
}

/** WebhookSecretPort implementation — env var takes precedence over DB. */
@Override
public String getEffectiveWebhookSecret() {
    String fromEnvironment = environment.getProperty("example.webhook-secret");
    if (fromEnvironment != null && !fromEnvironment.isBlank()) {
        return fromEnvironment;
    }
    return getOrGenerateWebhookSecret();
```
The port method reaches the `@Transactional` method through `this`, so the proxy is bypassed and the read-then-write has
no transaction.

**Good** (neutral)
```java
@Component
class WebhookSecretStore {
    … // one constructor: BillingSettingsPort settings, CredentialEncryptor encryptor
    @Transactional
    String loadOrCreate() {
        final String stored = settings.get(KEY_WEBHOOK_SECRET);
        return stored.isBlank() ? create() : decryptSafe(stored);
    }
}
// BillingSettingsService implements WebhookSecretPort
@Override
public String loadOrCreateWebhookSecret() {
    return Optional.ofNullable(environment.getProperty("example.webhook-secret"))
            .filter(not(String::isBlank))
            .orElseGet(webhookSecretStore::loadOrCreate);
```
The transactional method lives on a second bean, so the call crosses the proxy, with no self-injection and no
`AopContext`. (Pair: 68f § SC21 — A proxied annotation works only on a call from another bean; never through `this`.
Real evidence: ledger row SC21.)

## Decided edges

- **Skip when** the code is a test, including a shared test-support module: tests may use `@Autowired` (SC1). — **Do
  not skip when** the class is production code, including a second constructor only a test calls (SC1). —
  **Confidence** high
- **Skip when** both implementations must exist at once and callers pick one: `@Primary` for the default or
  `@Qualifier` at the injection point (plinth 301 :1072-1074, Example 10). — **Do not skip when** only one of them
  should run; then a config flag selects it (SC4). — **Confidence** high
- **Skip when** both implementations must exist at once (the edge above). — **Do not skip when** a
  `@Fallback` bean or a `@ConditionalOnMissingBean` stub stands in for the one that should run: each hides the choice
  as `@Primary` does, and a stub resolved by load order once beat the real bean (SC4, operator preference). —
  **Confidence** high
- **Skip when** a named degraded mode is chosen on purpose: its switch property is set only in test or local
  configuration (SC16). — **Do not skip when** the switch is set in the shipped `application.yml`, or the mode starts
  without its one WARN (SC16). — **Confidence** high
- **Skip when** the settings are for tests: they live in `src/test/resources/application.yml`, and local overrides
  come from environment variables or an untracked file outside the repo (operator preference). — **Do not skip when**
  an environment needs other settings or another bean: no `@Profile` and no `application-<profile>.yml`; settings
  differ by environment variables or a config tree, features by `@ConditionalOnProperty` (SC4), because profile
  configuration leaks test doubles (operator preference). The industry allows `@Profile`: plinth prefers it over
  `if (env == "prod")` branches in code (301:598-599), and so does this rule. — **Confidence** high
- **Skip when** the static-only class is the `@SpringBootApplication` class: the gate ignores classes annotated with
  it (SX18). — **Do not skip when** any other class holds only static members (SX18). — **Confidence** high
- **Skip when** the console output sits in a `main` method (SX19). — **Do not skip when** it sits in any other
  main-code method (SX19). — **Confidence** high

## Review checks

Walk every changed main-code Java file, every changed `application*.yml` and every changed configuration test.

- [ ] LY6 — For each bean, find one constructor. A setter or field injection, a no-arg constructor beside setters, or
  `@Autowired(required=false)` is a finding. An `ObjectProvider` resolved in a constructor or `@Bean` method is a
  finding.
- [ ] SC1 — A second constructor only a test calls is a finding. Only where no gate enforces it (Checkstyle
  `IllegalImport`): `@Autowired` in production code is a finding.
- [ ] SC2 — An `ObjectProvider` field that breaks a cycle without a comment naming the cycle is a finding.
- [ ] SC3 — `@Lazy` on an `ObjectProvider` (`grep -rn "@Lazy"`), or `spring.main.lazy-initialization` set to true in any
  `application*.yml`, is a finding.
- [ ] SC4 — `@Primary`, `@Fallback` or a `@ConditionalOnMissingBean` stub in main code
  (`grep -rnE "@(Primary|Fallback|ConditionalOnMissingBean)"`) on one of several implementations where only one should run
  is a finding. For each such type, each implementation carries `@ConditionalOnProperty` for its own value, exactly one
  matches, and an unset flag fails startup; a gap is a finding.
- [ ] SC9 — For each property-selected bean, find an `ApplicationContextRunner` spec with a case per value and a case
  for the missing value. A value or the missing case without one is a finding.
- [ ] SC5 — A `@Configuration` without `proxyBeanMethods = false`, or a `@Bean` method that calls another `@Bean`
  method, is a finding.
- [ ] SC6 — A `@Bean` method whose declared return type is wider than the type it builds is a finding.
- [ ] SC8 — An `@Enable*` annotation on the `@SpringBootApplication` class is a finding.
- [ ] LY7 — Two or more related keys read through `@Value`, or a `@Value` key that another class also reads, is a
  finding. A record without startup validation is a finding (SC15).
- [ ] SC12 — For each changed key, `grep -rn "<key>" src/main` across the modules. A key read in two classes is a
  finding.
- [ ] SC11 — A properties record also annotated `@Component` or returned from a `@Bean` method is a finding, and so is a
  record not registered with `@EnableConfigurationProperties`.
- [ ] SC13 — `System.getenv` in main code (`grep -rn "System.getenv"`), an upper-case env-var name in `@Value`, or a key
  that is not kebab-case under the app's own prefix, is a finding.
- [ ] SC10 — An `@ConditionalOnProperty` whose key is not kebab-case under the app's own prefix, or that does not state
  both `havingValue` and `matchIfMissing`, is a finding.
- [ ] SC14 — A time or size setting bound as a number, or a key ending `-ms` or `-seconds`, is a finding.
- [ ] SC15 — For each settings record, a bad and a missing value fail startup with a message naming the key, and a
  runner spec proves both. Either one unproven is a finding.
- [ ] SC16 — A default for a secret or a required endpoint (`${…:}` or `@DefaultValue`) is a finding. A degraded mode
  with no name or no WARN at startup is a finding.
- [ ] SC17 — A secret (key, password, token) as a component of a `@ConfigurationProperties` record is a finding.
- [ ] X6 — Only where no gate enforces it (Checkstyle `IllegalImport`): `@PostConstruct` in main code is a finding.
- [ ] SC19 — Startup work that must finish before traffic outside an `ApplicationRunner` is a finding, and so is an
  `ApplicationReadyEvent` listener that runs the work itself instead of handing it to another thread.
- [ ] SC20 — A listener container or consumer loop created with `new` and started by hand is a finding.
- [ ] SC21 — For each method with a proxied annotation, find its callers. A call through `this`, a self-injected field,
  or `AopContext` is a finding.
- [ ] SC23 — A service class whose methods mostly read without `@Transactional(readOnly = true)` at class level is a
  finding, and so is a write method in it without its own `@Transactional`.
- [ ] SX18 — Only where no gate enforces it (Checkstyle `HideUtilityClassConstructor` and `FinalClass`): a static-only
  class that is not `final` with a private constructor is a finding.
- [ ] SX19 — Only where no gate enforces it (Checkstyle `RegexpSinglelineJava`): `System.out`, `System.err` or
  `printStackTrace()` in main code is a finding.
- [ ] SX14 — In a package-private class, a `public` method without `@Override` is a finding.
