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
- **SC3** — Never enable global lazy initialization (`spring.main.lazy-initialization` or `setLazyInitialization`),
  because a misconfigured bean then fails only when it is first used, not at startup.
- **SC4** — When only one implementation of an interface should run, select it with a
  config flag (`@ConditionalOnProperty`), never with `@Primary`, because `@Primary` builds both beans and leaves the
  choice in code, not configuration.
- **SC9** — Give every property-selected bean an `ApplicationContextRunner` spec
  proving each value picks the right bean and a missing value fails startup, because a wrong bean choice otherwise ships
  with no failing test.
- **SC7** — Put `@ConditionalOnBean` and `@ConditionalOnMissingBean` only on auto-configuration classes, because these
  conditions see only the bean definitions processed so far, and only auto-configuration loads after every user bean.
- **SC5** — Declare each configuration class `@Configuration(proxyBeanMethods = false)` and pass collaborators as
  `@Bean` parameters, never by calling another `@Bean` method, because proxying adds a CGLIB subclass and,
  without it, a direct call builds a second instance.
- **SC6** — Declare a `@Bean` method's return type as the most specific type it
  builds, because before creation the container and type-based conditions see only the declared type.
- **SC8** — Put feature switches (`@EnableScheduling`, `@EnableAsync`, `@Enable*Auditing`) on a dedicated
  `@Configuration`, never on the `@SpringBootApplication` class, because every slice test loads the main class and so
  enables them.
- **LY7** — Bind related settings to one `@ConfigurationProperties` record, each key in one place; use `@Value` only
  for a lone scalar no other class reads, because scattered `@Value` reads each carry their own default and skip
  validation.
- **SC11** — Register a settings record with `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`, never
  as `@Component` or a `@Bean` method, because constructor binding does not apply to a record created that way.
- **SC13** — Read configuration only through binding or the `Environment`, as
  kebab-case keys under the app's own prefix, never `System.getenv` or an env-var name in `@Value`, because
  `System.getenv` skips configtree secrets and tests cannot override it.
- **SC10** — Name a kebab-case key under the app's own prefix in
  `@ConditionalOnProperty`, and state `havingValue` and `matchIfMissing`, because an env-var name skips the bound
  configuration and tests cannot override it.
- **SC14** — Bind times and sizes as `Duration` or `DataSize` with a unit in the value
  (`2s`), never a `long` named `*-ms` or `*-seconds`, because a bare number hides its unit, so seconds bind silently as
  milliseconds.
- **SC15** — Put `@Validated` and Jakarta constraints on each settings record, and prove with an
  `ApplicationContextRunner` that a missing or invalid value fails startup, because otherwise a bad value surfaces only
  when the code first reads it.
- **SC16** — Give a secret or required endpoint no default value, so its absence fails startup, because a shipped
  default credential or blank key silently runs production insecure.
- **SC17** — Never hold a secret as a plain `String` component of a settings record; wrap it in a type whose
  `toString` redacts it, because a record's generated `toString` prints every component value into logs.
- **X6** — Limit `@PostConstruct` to checking injected state; move I/O, calls to other beans and thread or container
  starts to an `ApplicationRunner` or `SmartLifecycle`, because `@PostConstruct` runs inside the singleton creation
  lock and can deadlock.
- **SC19** — Run startup work that must finish before traffic in an
  `ApplicationRunner`; hand later work to another thread from `@EventListener(ApplicationReadyEvent)`, which returns at
  once, because event listeners must not run lengthy tasks.
- **SC20** — Make a component that starts and stops background work (a listener
  container, a consumer loop) a Spring-managed `SmartLifecycle` bean, never `new`-ed and started by hand, because a
  hand-started container misses the context's shutdown phases.
- **SC21** — Call a method with a proxied annotation only from another bean; move it to a second bean, with no
  self-injection and no `AopContext`, because a `this` call bypasses the proxy, so the transaction never starts.
- **SC22** — Put `@Retryable` on the `@Transactional` method or on a caller with no open transaction, never inside an
  outer transaction, because each attempt then joins a transaction already marked rollback-only and repeats inside it.
- **SC23** — Put `@Transactional(readOnly = true)` on a service class whose methods mostly read, and plain
  `@Transactional` on each write method, because without the read-only default every query pays for dirty checking.
- **SX18** — Make a static-only class `final` with a private constructor, because Java
  adds a public constructor by default, which lets callers instantiate a class where an instance makes no sense.
- **SX19** — Write output through the logger, never `System.out`, `System.err` or
  `printStackTrace()` in main code, because console output bypasses the logger's level and context, so a failed run
  cannot be triaged from the logs.
- **SX14** — In a package-private class, make a method `public` only when it
  overrides, because a public method there widens visibility by accident and exposes a method no caller should reach.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a required collaborator | a constructor parameter kept in a `final` field (LY6) | a field- or setter-injected bean can start with a null dependency |
| a collaborator that may be absent | an `ObjectProvider<T>`, resolved where it is used (LY6) | its absence becomes a decision at the call, not a null |
| a bean with more than one constructor | one constructor, with no `@Autowired` (SC1) | with several, the container picks by its own rules and tests run wiring production never uses |
| a dependency cycle | cut it; where it cannot be cut, an `ObjectProvider<T>` resolved at call time (SC2) | a constructor cycle fails startup, and an AOT context refuses it |
| a prototype-, request- or session-scoped bean used by a singleton | an `ObjectProvider<T>` resolved per use (SCN1) | a plain injection keeps the first instance forever |
| the lazy-initialization switch | left at its default, off (SC3) | a misconfigured bean fails at startup, not at its first use |
| several implementations of one type, and only one should run | one `@ConditionalOnProperty` value per implementation, exactly one matching, an unset flag failing startup (SC4, SC10) | the choice lives in configuration, and only the chosen bean is built |
| a property-selected bean | an `ApplicationContextRunner` spec with a case per value and a missing-value case (SC9) | a wrong bean choice otherwise ships with no failing test |
| a bean that backs off when the user defines one | `@ConditionalOnMissingBean` on an auto-configuration class (SC7) | only auto-configuration loads after every user bean, so the condition sees them all |
| a `@Bean` method that needs another bean | the other bean as a method parameter, in a `proxyBeanMethods = false` class (SC5) | no CGLIB subclass, and no second instance from a direct call |
| a `@Bean` method that builds an implementation of an interface | the concrete class as its return type (SC6) | the container and type-based conditions see only the declared type before creation |
| an `@Enable*` feature switch | a dedicated `@Configuration` (SC8) | every slice test loads the main class |
| several settings that belong together | one `@ConfigurationProperties` record (LY7); `@Value` for one scalar no other class reads | one key, one default, validated once |
| a settings record to register | `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan` (SC11) | constructor binding does not apply to a `@Component` or `@Bean` record |
| a configuration value | binding or the `Environment`, kebab-case under the app's prefix (SC13) | `System.getenv` skips configtree secrets and tests cannot override it |
| a time or size setting | `Duration` or `DataSize` (SC14) | a bare number hides its unit |
| a check on a settings value | a Jakarta constraint with `@Validated`, and an `ApplicationContextRunner` spec for the failure (SC15) | a bad value fails startup instead of the first read |
| a secret or a required endpoint | no default, so absence fails startup (SC16) | a shipped default credential runs production insecure |
| a secret among the settings | a value type whose `toString` redacts it (SC17) | a record's `toString` prints every component |
| a startup check on injected state | the constructor or a `@PostConstruct` that only checks (X6) | it fails startup without work inside the creation lock |
| startup work beyond checking injected state | an `ApplicationRunner`, or a `SmartLifecycle` bean (X6) | `@PostConstruct` runs inside the singleton creation lock and can deadlock |
| startup work that must finish before traffic | an `ApplicationRunner` (SC19) | a runner finishes after context refresh, before the app accepts traffic |
| startup work that may finish later | a thread started from an `@EventListener(ApplicationReadyEvent)` that returns at once (SC19) | event listeners must not run lengthy tasks |
| background work that starts and stops | a `SmartLifecycle` bean (SC20) | it joins the context's start and shutdown phases |
| a proxied method (such as `@Transactional`) called from its own class | the method on a second bean (SC21) | a `this` call bypasses the proxy |
| a retry around a transaction | `@Retryable` on the `@Transactional` method, or on a caller holding no transaction (SC22) | each attempt then starts a fresh transaction instead of joining a doomed one |
| a service whose methods mostly read | `@Transactional(readOnly = true)` on the class; plain `@Transactional` on each write method (SC23) | read-only transactions skip dirty checking |
| a class with only static members | `final`, with a private constructor (SX18) | no caller can build an instance that makes no sense |
| console output | a logger call (SX19) | console output skips the logger's level and context |
| a method in a package-private class | `public` only on an override (SX14) | a public method there widens visibility by accident |

## Good / Bad

Every rule's approved pair: [examples/spring.md](examples/spring.md).

### LY6 — Required dependencies through the constructor; an optional one is an `ObjectProvider<T>` resolved at use

**Bad**
```java
@Service
class OrderService {
    private OrderRepository orders;
    private LoyaltyService loyalty;

    @Autowired
    void setOrders(OrderRepository orders) { this.orders = orders; }
    @Autowired(required = false)
    void setLoyalty(LoyaltyService loyalty) { this.loyalty = loyalty; }

    void place(Order order) {
        orders.save(order);
        loyalty.award(order);
    }
}
```
With no `LoyaltyService` bean, `loyalty` stays null, so every order fails after it is saved.

**Good**
```java
@Service
class OrderService {
    private final OrderRepository orders;
    private final ObjectProvider<LoyaltyService> loyalty;
    OrderService(final OrderRepository orders,
                 final ObjectProvider<LoyaltyService> loyalty) {
        this.orders = orders;
        this.loyalty = loyalty;
    }

    void place(final Order order) {
        orders.save(order);
        loyalty.ifAvailable(service -> service.award(order));
    }
}
```
One constructor takes every collaborator. The optional one is resolved where it is used, so its absence is a decision
in the code, not a null.

### LY7 — Related settings in one validated record; each key bound in one place

**Bad**
```java
@Configuration(proxyBeanMethods = false)
class PaymentGatewayConfig {
    @Bean
    PaymentGatewayClient paymentGatewayClient(
            @Value("${shop.payment-gateway.base-url}") final String baseUrl,
            @Value("${shop.payment-gateway.connect-timeout:5s}") final Duration connectTimeout,
            @Value("${shop.payment-gateway.max-connections:10}") final int maxConnections) {
        return new PaymentGatewayClient(baseUrl, connectTimeout, maxConnections);
    }
}
```
Three related keys are read one by one, each with its own default. A second class that reads one of them can choose a
different default, and no value is checked at startup.

**Good**
```java
@Validated
@ConfigurationProperties("shop.payment-gateway")
public record PaymentGatewayProperties(@NotNull URI baseUrl,
                                       @NotNull Duration connectTimeout,
                                       @Min(1) int maxConnections) {
}

@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties(PaymentGatewayProperties.class)
class PaymentGatewayConfig {
    @Bean
    PaymentGatewayClient paymentGatewayClient(final PaymentGatewayProperties gateway) {
        return new PaymentGatewayClient(gateway);
    }
}
```
One record binds the group once and validates it at startup. Every class that needs a key reads it from the record.

### SC21 — A proxied annotation works only on a call from another bean; never through `this`

**Bad**
```java
@Service
class OrderService {
    … // one constructor: JdbcClient jdbc

    void placeOrder(final long productId) {
        this.reserveStock(productId);
    }

    @Transactional
    void reserveStock(final long productId) {
        jdbc.sql("UPDATE stock SET on_hand = on_hand - 1 WHERE product_id = ?").param(productId).update();
        jdbc.sql("INSERT INTO reservations (product_id) VALUES (?)").param(productId).update();
    }
}
```
The call goes through `this`, not the proxy, so no transaction starts. A failed insert leaves the stock reduced.

**Good**
```java
@Service
class OrderService {
    private final StockService stock;

    OrderService(final StockService stock) {
        this.stock = stock;
    }

    void placeOrder(final long productId) {
        stock.reserve(productId);
    }
}
// StockService: a second @Service; its @Transactional reserve(productId) holds both writes
```
The transactional method lives on a second bean, so the call crosses the proxy. No self-injection, no `AopContext`.

## Decided edges

- **Skip when** the code is a test, including a shared test-support module: tests may use `@Autowired` (SC1). — **Do
  not skip when** the class is production code, including a second constructor only a test calls (SC1). —
  **Confidence** high
- **Skip when** both implementations must exist at once and callers pick one: `@Primary` for the default or
  `@Qualifier` at the injection point (SC4). — **Do not skip when** only one of them should run; then a config flag
  selects it (SC4). — **Confidence** high
- **Skip when** both implementations must exist at once (the edge above), or the default is a
  `@ConditionalOnMissingBean` bean on an auto-configuration class that backs off when the user defines one (SC7). —
  **Do not skip when** a `@Fallback` bean or a `@ConditionalOnMissingBean` stub outside auto-configuration stands in
  for the one that should run: each hides the choice as `@Primary` does, and a stub resolved by load order can beat the
  real bean (SC4, SC7). — **Confidence** high
- **Skip when** the settings are for tests: they live in `src/test/resources/application.yml`, and local overrides
  come from environment variables or an untracked file outside the repo. — **Do not skip when** an environment needs
  other settings or another bean: no `@Profile` and no `application-<profile>.yml`; settings differ by environment
  variables or a config tree, features by `@ConditionalOnProperty` (SC4), because profile configuration leaks test
  doubles. — **Confidence** high
- **Skip when** the static-only class is the `@SpringBootApplication` class: the context builds it as a configuration
  bean, so an instance makes sense (SX18); SC5 still applies to it, so it takes `proxyBeanMethods = false`. — **Do
  not skip when** any other class holds only static members (SX18). — **Confidence** high
- **Skip when** the console output sits in a `main` method (SX19). — **Do not skip when** it sits in any other
  main-code method (SX19). — **Confidence** high

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
- [ ] SC3 — `spring.main.lazy-initialization` set to true in any `application*` file, or `setLazyInitialization(true)`
  or `lazyInitialization(true)` in main code (`grep -rnE "lazy-initialization[:=] *true|azyInitialization\(true\)"`),
  is a finding.
- [ ] SC4 — `@Primary`, `@Fallback` or a `@ConditionalOnMissingBean` stub in main code
  (`grep -rnE "@(Primary|Fallback|ConditionalOnMissingBean)"`) on one of several implementations where only one should
  run is a finding, except a `@ConditionalOnMissingBean` default on an auto-configuration class (SC7). For each such
  type, each implementation carries `@ConditionalOnProperty` for its own value, exactly one matches, and an unset flag
  fails startup; a gap is a finding.
- [ ] SC9 — For each property-selected bean, find an `ApplicationContextRunner` spec with a case per value and a case
  for the missing value. A value or the missing case without one is a finding.
- [ ] SC7 — `@ConditionalOnBean` or `@ConditionalOnMissingBean` (`grep -rnE "@ConditionalOn(Missing)?Bean\b"`) in a
  class that is not an auto-configuration class (`@AutoConfiguration`, or listed in
  `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`) is a finding.
- [ ] SC5 — A `@Configuration` without `proxyBeanMethods = false`, or a `@Bean` method that calls another `@Bean`
  method, is a finding.
- [ ] SC6 — A `@Bean` method whose declared return type is wider than the type it builds is a finding.
- [ ] SC8 — An `@Enable*` annotation on the `@SpringBootApplication` class is a finding.
- [ ] LY7 — Two or more related keys read through `@Value` is a finding. For each changed key, `grep -rn "<key>"
  src/main` across the modules; a key read in two classes is a finding.
- [ ] SC11 — A settings record annotated `@Component` or returned from a `@Bean` method is a finding, and so is one
  registered by neither `@EnableConfigurationProperties` nor `@ConfigurationPropertiesScan`.
- [ ] SC13 — `System.getenv` in main code (`grep -rn "System.getenv"`), an upper-case env-var name in `@Value`, or a key
  that is not kebab-case under the app's own prefix, is a finding.
- [ ] SC10 — An `@ConditionalOnProperty` whose key is not kebab-case under the app's own prefix, or that does not state
  both `havingValue` and `matchIfMissing`, is a finding.
- [ ] SC14 — A time or size setting bound as a number, or a key ending `-ms` or `-seconds`, is a finding.
- [ ] SC15 — A settings record without `@Validated`, or a field that must be present or bounded without its Jakarta
  constraint, is a finding. A record with no `ApplicationContextRunner` spec proving that a missing and an invalid
  value fail startup is a finding.
- [ ] SC16 — A default for a secret or a required endpoint (`${key:…}` in `@Value` or yml, `@DefaultValue`, or a
  fallback when the value is blank) is a finding.
- [ ] SC17 — A secret (key, password, token) held as a plain `String` component of a settings record is a finding; a
  component of a type whose `toString` redacts it is not.
- [ ] X6 — A `@PostConstruct` method (`grep -rn "@PostConstruct"`) that does I/O, calls another bean, or starts a
  thread or container is a finding; one that only checks injected state is not.
- [ ] SC19 — Startup work that must finish before traffic outside an `ApplicationRunner` is a finding, and so is an
  `ApplicationReadyEvent` listener that runs the work itself instead of handing it to another thread.
- [ ] SC20 — A listener container or consumer loop created with `new` and started by hand is a finding.
- [ ] SC21 — For each method with a proxied annotation, find its callers. A call through `this`, a self-injected field,
  or `AopContext` is a finding.
- [ ] SC22 — For each `@Retryable` method (`grep -rn "@Retryable"`), find its callers. A caller that already runs inside
  a transaction, `@Transactional` on it or on a method up its call chain, is a finding.
- [ ] SC23 — A service class whose methods mostly read without `@Transactional(readOnly = true)` at class level is a
  finding, and so is a write method in it without its own `@Transactional`.
- [ ] SX18 — Only where no gate enforces it (Checkstyle `HideUtilityClassConstructor` and `FinalClass`): a static-only
  class that is not `final` with a private constructor is a finding.
- [ ] SX19 — Only where no gate enforces it (Checkstyle `RegexpSinglelineJava`): `System.out`, `System.err` or
  `printStackTrace()` in main code is a finding.
- [ ] SX14 — In a package-private class, a `public` method without `@Override` is a finding.
