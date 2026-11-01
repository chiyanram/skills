# Spring — Good / Bad examples

Every approved Good/Bad pair for the Spring rules, one per rule that has one. The rules, the decision table and the
review checks are in [`../spring.md`](../spring.md). Each pair is in one neutral domain (orders and billing); `68f § ID
— title` is a heading of `research/68f-neutral-code.md`.

Contents: LY6 · LY7 · SC6 · SC4 · SC15 · SC16 · SC19 · SC21

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

### SC6 — A `@Bean` method returns the most specific type it builds

**Bad** (neutral)
```java
@Bean
public OrderRepository orderRepository(OrderJpaRepository jpaRepository) {
    return new OrderRepositoryAdapter(jpaRepository);
}
```
The method builds the adapter but declares the port, so before creation the container and type conditions see only the
port.

**Good** (neutral)
```java
@Bean
OrderRepositoryAdapter orderRepository(final OrderJpaRepository jpaRepository) {
    return new OrderRepositoryAdapter(jpaRepository);
}
```
The declared type is what is built; callers still inject `OrderRepository`, because Spring matches every type the bean
has. (Pair: 68f § SC6 — A `@Bean` method returns the most specific type it builds. Real evidence: ledger row SC6.)

### SC4 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup

**Bad** (neutral)
```java
@Bean
@ConditionalOnMissingBean(TaxCalculator.class)
public TaxCalculator taxCalculator(TaxProperties tax) {
    Path ratesPath = Path.of(tax.rateTable().ratesPath());
    Path regionsPath = Path.of(tax.rateTable().regionsPath());
    if (Files.exists(ratesPath) && Files.exists(regionsPath)) {
        … // load RateTableTaxCalculator
        } catch (Exception failure) {
            log.warn("rate table init failed ({}: {}), falling back to a flat rate",
                    failure.getClass().getSimpleName(), failure.getMessage());
        }
    } … // else: WARN "using flat-rate tax"
    return new FlatRateTaxCalculator();
}
```
A file's existence picks between two real implementations, any failure falls back silently, and the stub depends on load
order.

**Good** (neutral)
```java
@Bean
@ConditionalOnProperty(name = "example.tax.mode", havingValue = "rate-table", matchIfMissing = false)
RateTableTaxCalculator rateTableTax(final TaxProperties tax) {
    return RateTableTaxCalculator.load(tax.rateTable().ratesPath(), tax.rateTable().regionsPath());
}

@Bean
@ConditionalOnProperty(name = "example.tax.mode", havingValue = "flat", matchIfMissing = false)
FlatRateTaxCalculator flatRateTax() {
    log.warn("action=tax.mode mode=flat accuracy=low key=example.tax.mode");
    return new FlatRateTaxCalculator();
}

@Validated @ConfigurationProperties("example.tax")
record TaxProperties(@NotNull TaxMode mode, @Valid RateTableFiles rateTable) {}
```
Each implementation carries its own value, exactly one matches, and an unset mode fails startup naming the key. (Pair:
68f § SC7 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup.
Real evidence: ledger row SC7.)

### SC15 — A settings record rejects bad values at startup, naming the key; a runner spec proves it

**Bad** (neutral)
```java
@ConfigurationProperties(prefix = "example.notifications.streams")
public record NotificationStreamsProperties(Stream ordersPlaced,
                                            Stream invoicesOverdue,
                                            Stream paymentsReceived,
                                            Duration drainTimeout) {

    public NotificationStreamsProperties {
        if (drainTimeout.isZero() || drainTimeout.isNegative()) {
            throw new IllegalArgumentException(PREFIX + "drain-timeout must be more than zero, but was " + …);
        }
        for (final NotificationStream stream : NotificationStream.values()) {
            requireCap(capOf(stream, ordersPlaced, invoicesOverdue, paymentsReceived), stream);
        }
    }
```
A wrong value is rejected, but a missing one makes the constructor dereference null: a bare NullPointerException naming
no key.

**Good** (neutral)
```java
@Validated
@ConfigurationProperties("example.notifications.streams")
public record NotificationStreamsProperties(@NotNull @Valid Stream ordersPlaced,
                                            @NotNull @Valid Stream invoicesOverdue,
                                            @NotNull @Valid Stream paymentsReceived,
                                            @NotNull @DurationMin(millis = 1) Duration drainTimeout) {

    public record Stream(@Min(1) int maxInFlight) {
    }
}
```
Each field carries its own constraint, so Boot's bind-validation failure names the property; the runner spec adds the
missing case. (Pair: 68f § SC15 — A settings record rejects bad values at startup, naming the key; a runner spec proves
it. Real evidence: ledger row SC15.)

### SC16 — No default for a secret or required endpoint; fail, or a named degraded mode at WARN

**Bad** (neutral)
```java
@Bean
public CredentialEncryptor credentialEncryptor(@Value("${example.master-key:}") String masterKey) {
    return new CredentialEncryptor(masterKey);
}
// CredentialEncryptor
public CredentialEncryptor(String secretKey) {
    if (secretKey == null || secretKey.isBlank()) {
        this.keyBytes    = null;
        this.passthrough = true;
        return;
    }
```
```yaml
example:
  master-key: ${EXAMPLE_MASTER_KEY:${master_key:}}
```
A missing master key defaults to `""` twice, which silently stores every PaymentGateway credential in plaintext, with no
failure or log.

**Good** (neutral)
```java
@Bean
CredentialEncryptor credentialEncryptor(final Environment environment, final CredentialProperties credentials) {
    return Optional.ofNullable(environment.getProperty("example.master-key"))
            .filter(not(String::isBlank))
            .<CredentialEncryptor>map(AesGcmCredentialEncryptor::new)
            .orElseGet(() -> plaintextIfAllowed(credentials));
}

private static CredentialEncryptor plaintextIfAllowed(final CredentialProperties credentials) {
    if (!credentials.plaintextAllowed()) {
        throw new InvalidConfigurationPropertyValueException("example.master-key", "", "required for credentials");
    }
    log.warn("action=credentials.mode mode=plaintext key=example.credentials.plaintext-allowed");
    return new PlaintextCredentialEncryptor();
}
```
Absence fails startup naming the key; plaintext is only a named mode, set outside the shipped yml, that warns once.
(Pair: 68f § SC16 — No default for a secret or required endpoint; fail, or a named degraded mode at WARN. Real evidence:
ledger row SC16.)

### SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a thread from ready

**Bad** (neutral)
```java
@Service
public class TaxRateTable implements TaxCalculator {
    …
    @PostConstruct
    void initialise() {
        reload();
    }
```
`reload()` reads every tax rate row while the bean is created, so a database outage fails startup inside unrelated bean
construction.

**Good** (neutral)
```java
@Service
public class TaxRateTable implements TaxCalculator, ApplicationRunner {
    … // fields and the one constructor unchanged

    @Override
    public void run(final ApplicationArguments arguments) {
        reload();
    }
```
Rates must be loaded before any order is priced, and a runner finishes after context refresh but before the app accepts
traffic. (Pair: 68f § SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a
thread from ready. Real evidence: ledger row SC19.)

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

