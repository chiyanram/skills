# Spring — Good / Bad examples

Every Good/Bad pair for the Spring rules, one per rule that has one. The rules, the decision table and the review
checks are in [`../spring.md`](../spring.md). Each pair is in one domain (a shop: orders, stock, payments).

Contents: LY6 · LY7 · SC6 · SC4 · SC15 · SC16 · SC19 · SC21

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

### SC6 — A `@Bean` method returns the most specific type it builds

**Bad**
```java
@Bean
PaymentService paymentService(final PaymentRepository payments) {
    return new CardPaymentService(payments);
}
```
The method builds a `CardPaymentService` but declares the interface. Before creation, the container and type-based
conditions see only `PaymentService`.

**Good**
```java
@Bean
CardPaymentService paymentService(final PaymentRepository payments) {
    return new CardPaymentService(payments);
}
```
The declared type is the built type. Callers still inject `PaymentService`, because Spring matches every type the bean
has.

### SC4 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup

**Bad**
```java
@Configuration(proxyBeanMethods = false)
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

**Good**
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

### SC15 — A settings record validates at startup; a runner spec proves a missing value fails it

**Bad**
```java
@ConfigurationProperties("shop.shipping")
public record ShippingProperties(URI baseUrl,
                                 Duration readTimeout) {
}
```
A missing `base-url` binds as null. The first shipment then fails with a NullPointerException that names no key.

**Good**
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

### SC16 — No default for a secret or required endpoint; its absence fails startup

**Bad**
```java
@Validated
@ConfigurationProperties("shop.payment-gateway")
public record PaymentGatewayProperties(@NotNull URI baseUrl,
                                       @NotNull Duration connectTimeout,
                                       @Min(1) int maxConnections,
                                       @DefaultValue("test-key") ApiKey apiKey) {
}
```
The default is a hard-coded credential: an unset key starts the shop with the test key, and no log says so.

**Good**
```java
@Validated
@ConfigurationProperties("shop.payment-gateway")
public record PaymentGatewayProperties(@NotNull URI baseUrl,
                                       @NotNull Duration connectTimeout,
                                       @Min(1) int maxConnections,
                                       @NotNull ApiKey apiKey) {
}

public record ApiKey(String value) {
    @Override
    public String toString() {
        return "ApiKey[***]";
    }
}
```
The key has no default. If it is unset, binding validation fails startup and names `apiKey`. The key sits in the
record with the rest of its group (LY7), and `ApiKey` keeps it out of the logs (SC17).

### SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a thread from ready

**Bad**
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
A long load runs inside an event listener, on the thread that publishes the event, and event listeners must not run
lengthy tasks.

**Good**
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
