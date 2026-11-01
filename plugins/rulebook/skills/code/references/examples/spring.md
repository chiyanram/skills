# Spring — Good / Bad examples

Every approved Good/Bad pair for the Spring rules, one per rule that has one. The rules, the decision table and the
review checks are in [`../spring.md`](../spring.md). Each pair is in one neutral domain (a shop: orders, stock,
payments). Labels use the source names of `../spring.md`: plinth 301 / 311 = jabrena-plinth
`skills/301-frameworks-spring-boot-core/references/301-frameworks-spring-boot-core.md` and
`skills/311-frameworks-spring-jdbc/references/311-frameworks-spring-jdbc.md`; SF / SB = the Spring Framework / Spring
Boot reference.

Contents: LY6 · LY7 · SC6 · SC4 · SC15 · SC16 · SC19 · SC21

### LY6 — One constructor; an optional collaborator is an `ObjectProvider<T>` resolved at use

**Bad** (from plinth 301 :791, Example 7)
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
With no `LoyaltyService` bean, `loyalty` stays null, so every order fails after it is saved. SF §Constructor-based or
setter-based DI: with setters, not-null checks must be done everywhere.

**Good** (neutral)
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

### LY7 — Grouped settings in one validated record; each key bound in one place

**Bad** (from plinth 301 :486, Example 4)
```java
@Configuration
class PaymentGatewayConfig {
    @Value("${shop.payment-gateway.base-url}")
    private String baseUrl;
    @Value("${shop.payment-gateway.connect-timeout:5s}")
    private Duration connectTimeout;
    @Value("${shop.payment-gateway.max-connections:10}")
    private int maxConnections;

    @Bean
    PaymentGatewayClient paymentGatewayClient() {
        return new PaymentGatewayClient(baseUrl, connectTimeout, maxConnections);
    }
}
```
Three related keys are read one by one, each with its own default. A second class that reads one of them can choose a
different default, and no value is checked at startup.

**Good** (from plinth 301 :462, Example 4)
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

### SC6 — A `@Bean` method returns the most specific type it builds

**Bad** (from SF §Using the @Bean Annotation, Declaring a Bean)
```java
@Bean
PaymentService paymentService(final PaymentRepository payments) {
    return new CardPaymentService(payments);
}
```
The method builds a `CardPaymentService` but declares the interface. Before creation, the container and type-based
conditions see only `PaymentService`.

**Good** (from SF §Using the @Bean Annotation, "declare the most specific return type possible")
```java
@Bean
CardPaymentService paymentService(final PaymentRepository payments) {
    return new CardPaymentService(payments);
}
```
The declared type is the built type. Callers still inject `PaymentService`, because Spring matches every type the bean
has.

### SC4 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup

**Bad** (from plinth 301 :1091, Example 10)
```java
@Configuration
class OrderNotifierConfig {
    @Bean
    @Primary
    EmailOrderNotifier emailOrderNotifier() {
        return new EmailOrderNotifier();
    }

    @Bean
    SmsOrderNotifier smsOrderNotifier() {
        return new SmsOrderNotifier();
    }
}
```
Every start builds both notifiers, and `@Primary` puts the choice of email in code. A move to SMS needs a release, not
a setting.

**Good** (from plinth 301 :645, Example 6)
```java
@Configuration(proxyBeanMethods = false)
class OrderNotifierConfig {
    @Bean
    @ConditionalOnProperty(name = "shop.notifier.channel", havingValue = "email", matchIfMissing = false)
    EmailOrderNotifier emailOrderNotifier() {
        return new EmailOrderNotifier();
    }

    @Bean
    @ConditionalOnProperty(name = "shop.notifier.channel", havingValue = "sms", matchIfMissing = false)
    SmsOrderNotifier smsOrderNotifier() {
        return new SmsOrderNotifier();
    }
}
```
Each value builds exactly one notifier. An unset channel builds none, so the bean that needs an `OrderNotifier` fails
startup.

### SC15 — A settings record rejects bad values at startup, naming the key; a runner spec proves it

**Bad** (from plinth 301 :1212, Example 11)
```java
@ConfigurationProperties("shop.shipping")
public record ShippingProperties(URI baseUrl,
                                 Duration readTimeout) {
}
```
A missing `base-url` binds as null. The first shipment then fails with a NullPointerException that names no key.

**Good** (record from plinth 301 :1188, Example 11; spec from rrezartprebreza/spring-boot-skills
`spring-boot-4/configuration-properties/SKILL.md:44-46`)
```java
@Validated
@ConfigurationProperties("shop.shipping")
public record ShippingProperties(@NotNull URI baseUrl,
                                 @NotNull Duration readTimeout) {
}
```
```groovy
def "should fail startup naming baseUrl when base-url is missing"() {
    expect:
    runner.withPropertyValues("shop.shipping.read-timeout=2s")
            .run { context ->
                assert getRootCause(context.startupFailure).message.contains("baseUrl")
            }
}
```
Each field carries its own constraint, so the bind-validation failure names the field. The runner spec proves the
missing case.

### SC16 — No default for a secret or required endpoint; fail, or a named degraded mode at WARN

**Bad** (from plinth 301 :510, Example 4)
```java
@Bean
PaymentGatewayClient paymentGatewayClient(
        final PaymentGatewayProperties gateway,
        @Value("${shop.payment-gateway.api-key:test-key}") final String apiKey) {
    return new PaymentGatewayClient(gateway, apiKey);
}
```
The source hard-codes the password. This default does the same behind a placeholder: an unset key starts the shop with
the test key, and no log says so.

**Good** (neutral)
```java
@Bean
PaymentGatewayClient paymentGatewayClient(
        final PaymentGatewayProperties gateway,
        @Value("${shop.payment-gateway.api-key}") final String apiKey) {
    return new PaymentGatewayClient(gateway, apiKey);
}
```
The key has no default. If it is unset, startup fails with "Could not resolve placeholder
'shop.payment-gateway.api-key'".

### SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a thread from ready

**Bad** (from plinth 301 :366, Example 3)
```java
@Component
class PriceCatalogueLoader {
    … // one constructor: PriceCatalogue catalogue

    @EventListener
    void onApplicationReady(final ApplicationReadyEvent event) {
        catalogue.loadAll();
    }
}
```
A long load runs inside an event listener, on the thread that publishes the event. SB §Application Events and Listeners:
listeners should not run lengthy tasks.

**Good** (from SB §Using the ApplicationRunner or CommandLineRunner)
```java
@Component
class PriceCatalogueLoader implements ApplicationRunner {
    private final PriceCatalogue catalogue;

    PriceCatalogueLoader(final PriceCatalogue catalogue) {
        this.catalogue = catalogue;
    }

    @Override
    public void run(final ApplicationArguments arguments) {
        catalogue.loadAll();
    }
}
```
Orders need prices before the first request. A runner finishes after context refresh, before the app accepts traffic.

### SC21 — A proxied annotation works only on a call from another bean; never through `this`

**Bad** (from plinth 311 :1073, Example 14)
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

**Good** (from plinth 311 :1049, Example 14)
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
