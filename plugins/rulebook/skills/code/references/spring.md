# Spring

How a Spring Boot application wires its beans, binds its settings, starts its work and crosses its proxies. Read it
when you write or review a bean, a configuration class, a settings record, a startup hook or a proxied method.

Contents: Rules · When X, use Y · Good / Bad (LY6, LY7, SC21) · Decided edges · Review checks

## Rules

- **LY6** — Take required dependencies through the constructor into `final` fields, never fields or setters; resolve
  an optional collaborator from an `ObjectProvider<T>` at use, because field or setter injection lets a bean start
  with a null dependency.
- **SC1** — Give each bean exactly one constructor, without `@Autowired`, and no second one for tests, because with
  several constructors the container picks by its own rules and tests exercise wiring production never uses.
- **SC2** — Cut every bean dependency cycle; where it cannot be cut, inject `ObjectProvider<T>` and resolve it at call
  time, because a constructor cycle fails startup with `BeanCurrentlyInCreationException` and an AOT context refuses it.
- **SCN1** — Never inject a prototype-, request- or session-scoped bean straight into a singleton; inject
  `ObjectProvider<T>` and resolve it per use, because the singleton keeps the first instance forever.
- **SC21** — Call a method with a proxied annotation only from another bean; move it to a second bean, with no
  self-injection and no `AopContext`, because a `this` call bypasses the proxy, so the transaction never starts.
- **SC22** — Put `@Retryable` on the `@Transactional` method or on a caller with no open transaction, never inside an
  outer transaction, because each attempt then joins a transaction already marked rollback-only and repeats inside it.
- **SC3** — Never enable global lazy initialization (`spring.main.lazy-initialization` or `setLazyInitialization`),
  because a misconfigured bean then fails only when it is first used, not at startup.
- **SC5** — Declare each configuration class `@Configuration(proxyBeanMethods = false)` and pass collaborators as
  `@Bean` parameters, never by calling another `@Bean` method, because proxying adds a CGLIB subclass and,
  without it, a direct call builds a second instance.
- **SC6** — Declare a `@Bean` method's return type as the most specific type it
  builds, because before creation the container and type-based conditions see only the declared type.
- **SC7** — Put `@ConditionalOnBean` and `@ConditionalOnMissingBean` only on auto-configuration classes, because these
  conditions see only the bean definitions processed so far, and only auto-configuration loads after every user bean.
- **SC8** — Put feature switches (`@EnableScheduling`, `@EnableAsync`, `@Enable*Auditing`) on a dedicated
  `@Configuration`, never on the `@SpringBootApplication` class, because every slice test loads the main class and so
  enables them.
- **LY7** — Bind related settings to one `@ConfigurationProperties` record, each key in one place; use `@Value` only
  for a lone scalar no other class reads, because scattered `@Value` reads each carry their own default and skip
  validation.
- **SC11** — Register a settings record with `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`, never
  as `@Component` or a `@Bean` method, because constructor binding does not apply to a record created that way.
- **SC15** — Put `@Validated` and Jakarta constraints on each settings record, and prove with an
  `ApplicationContextRunner` that a missing or invalid value fails startup, because otherwise a bad value surfaces only
  when the code first reads it.
- **SC16** — Give a secret or required endpoint no default value, so its absence fails startup, because a shipped
  default credential or blank key silently runs production insecure.
- **SC17** — Never hold a secret as a plain `String` component of a settings record; wrap it in a type whose
  `toString` redacts it, because a record's generated `toString` prints every component value into logs.
- **SC14** — Bind times and sizes as `Duration` or `DataSize` with a unit in the value
  (`2s`), never a `long` named `*-ms` or `*-seconds`, because a bare number hides its unit, so seconds bind silently as
  milliseconds.
- **X6** — Limit `@PostConstruct` to checking injected state; move I/O, calls to other beans and thread or container
  starts to an `ApplicationRunner` or `SmartLifecycle`, because `@PostConstruct` runs inside the singleton creation
  lock and can deadlock.
- **SC20** — Make a component that starts and stops background work (a listener
  container, a consumer loop) a Spring-managed `SmartLifecycle` bean, never `new`-ed and started by hand, because a
  hand-started container misses the context's shutdown phases.
- **SC23** — Put `@Transactional(readOnly = true)` on a service class whose methods mostly read, and plain
  `@Transactional` on each write method, because without the read-only default every query pays for dirty checking.
- **SX18** — Make a static-only class `final` with a private constructor, because Java
  adds a public constructor by default, which lets callers instantiate a class where an instance makes no sense.
- **SX19** — Write output through the logger, never `System.out`, `System.err` or
  `printStackTrace()` in main code, because console output bypasses the logger's level and context, so a failed run
  cannot be triaged from the logs.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a required collaborator | a constructor parameter kept in a `final` field (LY6) | FW: constructor injection "ensures that required dependencies are not `null`" · SONAR S6813 (r48 :629) |
| a collaborator a bean must reach lazily | an `ObjectProvider<T>`, resolved where it is used (LY6) | FW aot: "use `@Lazy` injection points or `ObjectProvider` to lazily access" (r48 :630) |
| a bean with more than one constructor | one constructor, with no `@Autowired` (SC1) | FW aot "Avoid Multiple Constructors": "relying on that is not a best practice" · SONAR S6818 (r48 :635) |
| a dependency cycle | cut it; where it cannot be cut, an `ObjectProvider<T>` (SC2) | FW: the container "throws a `BeanCurrentlyInCreationException`"; an AOT context "will fail to start with explicit circular dependencies … you can use … `ObjectProvider`" · ADDY: "no circular dependencies" (r48 :641) |
| a prototype-, request- or session-scoped bean used by a singleton | an `ObjectProvider<T>` resolved per use (SCN1) | FW factory-scopes: "The prototype instance is the sole instance that is ever supplied to the singleton-scoped bean." · SONAR S6832 (r48 :755) |
| a proxied method (such as `@Transactional`) called from its own class | the method on a second bean (SC21) | FW proxying: "self invocation … will bypass the advice" · SONAR S6809 (r48 :733) |
| a retry around a transaction | `@Retryable` on the `@Transactional` method, or on a caller holding no transaction (SC22) | FW resilience: "Retry (OUTER) → Transaction (INNER) … Each retry attempt starts a fresh transaction" · SBS: "A retrying facade must not already hold a transaction that each attempt's `REQUIRED` method would join." (r48 :738) |
| the lazy-initialization switch | left at its default, off (SC3) | BOOT §Lazy Initialization: "lazy initialization is not enabled by default"; lazily, "a failure will no longer occur during startup" (r48 :1417, :1418) |
| a `@Bean` method that needs another bean | the other bean as a method parameter, in a `proxyBeanMethods = false` class (SC5) | FW: "every such call can be expressed through a factory method argument instead … no CGLIB subclassing" · SONAR S6838 (r48 :660) |
| a `@Bean` method that builds an implementation of an interface | the concrete class as its return type (SC6) | FW aot: "as precise as possible" · BOOT: "the bean method's return type should be the concrete class" (r48 :665) |
| a bean that backs off when the user defines one | `@ConditionalOnMissingBean` on an auto-configuration class (SC7) | BOOT §Bean Conditions: "we recommend using only `@ConditionalOnBean` and `@ConditionalOnMissingBean` annotations on auto-configuration classes" (r48 :1419) |
| an `@Enable*` feature switch | a dedicated `@Configuration` (SC8) | BOOT: "avoid adding configuration settings that are specific to a particular area on the main method's application class" · PL301: no `@Enable*` "should ever appear on the main class" (r48 :670) |
| several settings that belong together | one `@ConfigurationProperties` record (LY7) | BOOT: "group them in a POJO annotated with `@ConfigurationProperties`" · PL301: "avoid scattering many `@Value` fields" (r48 :675) |
| a settings record to register | `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan` (SC11) | BOOT: "You cannot use constructor binding with beans that are created by the regular Spring mechanisms" · SBS: "Register it with EnableConfigurationProperties or ConfigurationPropertiesScan" (r48 :684) |
| a check on a settings value | a Jakarta constraint, and an `ApplicationContextRunner` spec for the failure (SC15) | BOOT: "JSR-303 `jakarta.validation` constraint annotations directly on your configuration class" · SBS: "Use ApplicationContextRunner … to assert … startup failure on missing or invalid settings" (r48 :702) |
| a secret or a required endpoint | no default, so absence fails startup (SC16) | SBS: "missing credentials or required endpoints should fail startup" · ASVS 13.2.3: "not a default credential" (r48 :708) |
| a secret among the settings | a redacting value type, or resolution at the integration boundary (SC17) | SBS: "Resolve secrets at the integration boundary or use a redacting value type" · JDK `Record.toString`: it holds the "string representations of component values" (r48 :714) |
| startup work beyond checking injected state | an `ApplicationRunner`, or a `SmartLifecycle` bean (X6) | FW: `@PostConstruct` runs in "the container's singleton creation lock … only meant for validating the configuration state" (r48 :720) · BOOT: "Tasks expected to run during startup should be executed by `CommandLineRunner` and `ApplicationRunner`" (r48 :725) · FW: "consider implementing `SmartLifecycle`" (r48 :729) |
| a time or size setting | `Duration` or `DataSize` (SC14) | BOOT: "Use `Duration` rather than `long`" · SBS: "Use explicit units for durations and sizes" (r48 :697) |
| background work that starts and stops | a `SmartLifecycle` bean (SC20) | FW factory-nature: "consider implementing `SmartLifecycle`" (r48 :729) |
| a class with only static members | `final`, with a private constructor (SX18) | SONAR S1118, S2974 · CS: "forgetting to hide the default constructor" (r48 :743) |
| console output | a logger call (SX19) | SONAR S106 · PMD: "Avoid printStackTrace(); use a logger call instead." (r48 :747) |
| a service whose methods mostly read | `@Transactional(readOnly = true)` on the class; plain `@Transactional` on each write method (SC23) | plinth 311 :665-668 (Example 10) · Jeffallan data.md :153 · Spring Data JPA §Transactionality: `SimpleJpaRepository` reads run read-only, so Hibernate skips dirty checks |

Sources: `r48 :N` is a line of agent-factory `research/48-industry-recheck-code.md`, which records each quote with
the repository and commit it was read at. FW = Spring Framework reference and BOOT = Spring Boot reference (one
organisation; under the vendor exception, a rule about Spring's own behaviour may rest on it alone: SC3, SC6, SC7,
SC20); SONAR = SonarSource Java rules (cited by number only); PMD = PMD Java rules; CS = Checkstyle; ASVS = OWASP ASVS
5.0; JDK = OpenJDK `java.lang.Record`; SBS = rrezartprebreza/spring-boot-skills; PL301 = jabrena/plinth
`301-frameworks-spring-boot-core`; ADDY = addyosmani/agent-skills. SC23 was not part of the r48 re-check: plinth 311 =
jabrena/plinth `311-frameworks-spring-jdbc`, Jeffallan = Jeffallan claude-skills `spring-boot-engineer`. `68f § ID —
title` is a heading of `research/68f-neutral-code.md`.

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
The provider is resolved while the bean is built, so in an application with no EmailSender bean it bakes in a throwing
stub at startup.

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

- **Skip when** the static-only class is the `@SpringBootApplication` class: it is a full `@Configuration`, which
  Spring subclasses with CGLIB, and "`final` classes cannot be proxied" (FW, r48 :1420) (SX18). — **Do not skip when**
  any other class holds only static members (SX18). — **Confidence** high

## Review checks

Walk every changed main-code Java file, every changed `application*.yml` or `application*.properties` and every changed
configuration test.

- [ ] LY6 — For each bean, find its constructor. `@Autowired`, `@Inject` or `@Value` on a field or setter
  (`grep -rnE "@(Autowired|Inject|Value)\b"`, then read the next line) is a finding, and so is a required dependency
  kept in a non-`final` field. An `ObjectProvider` resolved (`getObject`, `getIfAvailable`) in a constructor or `@Bean`
  method is a finding.
- [ ] SC1 — A bean with more than one constructor, or `@Autowired` on a bean's constructor, is a finding.
- [ ] SC2 — For each changed constructor, follow its parameters' beans. A cycle back to the bean that is not cut and not
  held by an `ObjectProvider<T>` resolved at call time is a finding.
- [ ] SCN1 — For each prototype-, request- or session-scoped bean (`grep -rnE "@(RequestScope|SessionScope|Scope\()"`),
  find where it is injected. A singleton that takes it as a plain constructor parameter or field is a finding; an
  `ObjectProvider<T>` resolved per use is not.
- [ ] SC21 — For each method with a proxied annotation, find its callers. A call through `this`, a self-injected field,
  or `AopContext` is a finding.
- [ ] SC22 — For each `@Retryable` method (`grep -rn "@Retryable"`), find its callers. A caller that already runs inside
  a transaction, `@Transactional` on it or on a method up its call chain, is a finding.
- [ ] SC3 — `spring.main.lazy-initialization` set to true in any `application*` file, or `setLazyInitialization(true)`
  or `lazyInitialization(true)` in main code (`grep -rnE "lazy-initialization[:=] *true|azyInitialization\(true\)"`),
  is a finding.
- [ ] SC5 — A `@Configuration` without `proxyBeanMethods = false`, or a `@Bean` method that calls another `@Bean`
  method, is a finding.
- [ ] SC6 — A `@Bean` method whose declared return type is wider than the type it builds is a finding.
- [ ] SC7 — `@ConditionalOnBean` or `@ConditionalOnMissingBean` (`grep -rnE "@ConditionalOn(Missing)?Bean\b"`) in a
  class that is not an auto-configuration class (`@AutoConfiguration`, or listed in
  `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`) is a finding.
- [ ] SC8 — An `@Enable*` annotation on the `@SpringBootApplication` class is a finding.
- [ ] LY7 — Two or more related keys read through `@Value` is a finding. For each changed key, `grep -rn "<key>"
  src/main` across the modules; a key read in two classes is a finding.
- [ ] SC11 — A settings record annotated `@Component` or returned from a `@Bean` method is a finding, and so is one
  registered by neither `@EnableConfigurationProperties` nor `@ConfigurationPropertiesScan`.
- [ ] SC15 — A settings record without `@Validated`, or a field that must be present or bounded without its Jakarta
  constraint, is a finding. A record with no `ApplicationContextRunner` spec proving that a missing and an invalid
  value fail startup is a finding.
- [ ] SC16 — A default for a secret or a required endpoint (`${key:…}` in `@Value` or yml, `@DefaultValue`, or a
  fallback when the value is blank) is a finding.
- [ ] SC17 — A secret (key, password, token) held as a plain `String` component of a settings record is a finding; a
  component of a type whose `toString` redacts it is not.
- [ ] SC14 — A time or size setting bound as a number, or a key ending `-ms` or `-seconds`, is a finding.
- [ ] X6 — A `@PostConstruct` method (`grep -rn "@PostConstruct"`) that does I/O, calls another bean, or starts a
  thread or container is a finding; one that only checks injected state is not.
- [ ] SC20 — A listener container or consumer loop created with `new` and started by hand is a finding.
- [ ] SC23 — A service class whose methods mostly read without `@Transactional(readOnly = true)` at class level is a
  finding, and so is a write method in it without its own `@Transactional`.
- [ ] SX18 — Only where no gate enforces it (Checkstyle `HideUtilityClassConstructor` and `FinalClass`): a static-only
  class that is not `final` with a private constructor is a finding.
- [ ] SX19 — Only where no gate enforces it (Checkstyle `RegexpSinglelineJava`): `System.out`, `System.err` or
  `printStackTrace()` in main code is a finding.
