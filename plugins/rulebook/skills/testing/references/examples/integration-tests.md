# Integration tests — examples

Every Good/Bad pair for the rules in [../integration-tests.md](../integration-tests.md), one per rule id.
Read it when a rule's sentence leaves you unsure what the code looks like.

### IT1 — Prove the contract once; leave unit-owned branches to the unit spec

**Bad**
```java
    @DisplayName("POST with customerId blank → 400 naming customerId")
    void createOrder_blankCustomerId_returns400() {
        postOrder("""
                { "customerId": "", "lines": [ { "sku": "SKU-1", "quantity": 1 } ] }
                """)
                .expectStatus().isBadRequest()
    ...
    @DisplayName("POST with lines empty → 400 naming lines")
    void createOrder_emptyLines_returns400() {
```
One slow HTTP test per blank field re-runs validation branches that the order validator's unit spec already owns.

**Good**
```groovy
    def "should answer an order the validator refuses with a 400 problem"() {
        when: "a clerk posts an order the validator refuses; which fields it refuses is the unit spec's job"
        def result = http.post()
            .uri("/api/orders")
            .header(HttpHeaders.AUTHORIZATION, login("CLERK"))
            .contentType(MediaType.APPLICATION_JSON)
            .body('{ "customerId": "", "lines": [] }')
            .exchange()
            .returnResult()

        then: "the HTTP contract holds: status 400 as a problem document"
        result.status.value() == 400
        result.responseHeaders.contentType == MediaType.APPLICATION_PROBLEM_JSON
```
One IT proves the refusal-to-400 mapping through the real stack; the field branches stay in the fast unit spec.

### IT2 — Take every container from the singleton initializer

**Bad**
```java
@Testcontainers
class PaymentGatewayIT {
    ...
    @Container
    @SuppressWarnings("resource")
    static final GenericContainer<?> GATEWAY = new GenericContainer<>("example/payment-sandbox:1.4.0")
        .withExposedPorts(GATEWAY_PORT)
        .waitingFor(Wait.forListeningPort());
```
The class starts its own container and stops it when the class ends, outside the shared singleton every other IT uses.

**Good**
```groovy
/**
 * No Spring context, so no @EnableSharedContainers: the gateway sandbox comes from the singleton,
 * the way shared Postgres serves non-Spring ITs, and this spec never starts or stops it.
 */
class PaymentGatewayIT extends Specification {

    @Shared
    String gatewayUrl = SharedContainersInitializer.sharedGatewayUrl()

    PaymentGatewayAdapter gateway = new PaymentGatewayAdapter(gatewayUrl)

    def setupSpec() {
        seedSandboxAccounts(gatewayUrl)
    }
```
The container lives in the shared initializer beside Postgres, so no spec owns its lifecycle and every spec reuses it.

### IT3 — Call the running server with RestTestClient

**Bad**
```java
        OrderController ctrl = new OrderController(orderService, invoiceService, paymentGateway, clock);
        mockMvc = MockMvcBuilders.standaloneSetup(ctrl).build();
    ...
        mockMvc.perform(post("/api/orders/{orderId}/cancel", orderId)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"reason\":\"customer request\"}"))
            .andExpect(status().isAccepted());
```
HTTP-shaped assertions over standalone MockMvc skip the filter chain, security and error advice the real server applies.

**Good**
```groovy
    def "should cancel a placed order when a clerk asks over HTTP"() {
        given: "a placed order"
        def order = placedOrder(CUSTOMER_ID)

        when: "a signed-in clerk cancels it on the running server"
        def result = http.post()
            .uri("/api/orders/${order.id()}/cancel")
            .header(HttpHeaders.AUTHORIZATION, login("CLERK"))
            .exchange()
            .expectBody()
            .returnResult()

        then: "the request passed the real filter chain and the order is cancelled"
        result.status.value() == 202
        orderRepository.findById(order.id()).orElseThrow().status() == OrderStatus.CANCELLED
```
RestTestClient on RANDOM_PORT sends real HTTP through security and error handling, with a token from a real login.

### IT4 — Swap an outbound port for a fake, never a double

**Bad**
```groovy
    def "should send the overdue notice when the reminder runs"() {
        given: "a reminder whose email sender is a Spock double"
        EmailSender emailSender = Stub() {
            send(_) >> true
        }
        def reminder = new OverdueReminder(invoiceRepository, emailSender, clock)
```
The IT replaces an outbound port with a double that has no behaviour of its own, and repeats that stub per feature.

**Good**
```groovy
    @Autowired OverdueReminder reminder
    @Autowired FakeEmailSender emailSender // the EmailSender bean of OutboundFakesConfig

    @Issue(["#123", "AC-2"])
    def "should send one overdue notice when the reminder runs"() {
        given: "an invoice one day past due, and the wired reminder sending through the shared fake"
        saveInvoice(openInvoiceDue(TODAY.minusDays(1)))

        when: "the reminder runs"
        reminder.remindOverdue()

        then: "the fake holds exactly one notice, for this invoice's customer"
        emailSender.sent()*.to() == [CUSTOMER_EMAIL]
```
The subject is the wired bean, and the port is the shared in-memory fake from `OutboundFakesConfig`, with its own
contract spec (IT5), instead of one stub per feature.

### TM4 — One Toxiproxy IT per dependency the system must survive

**Good**
```groovy
    def "should pay nothing and warn while the gateway is cut, then pay once the link returns"() {
        given: "an open invoice stored in setup(), then the gateway link cut at the proxy"
        gatewayProxy.toxics().bandwidth("cut", ToxicDirection.DOWNSTREAM, 0)

        when: "the invoice is paid during the outage"
        def duringOutage = invoiceService.pay(invoiceId)

        then: "no payment is recorded, and the outage is logged at WARN"
        duringOutage.isEmpty()
        appender.list.any { it.level == Level.WARN && it.formattedMessage.contains("charge invoiceId=") }

        when: "the fault clears"
        gatewayProxy.toxics().get("cut").remove()
        then: "the same payment goes through"
        invoiceService.pay(invoiceId).map { it.invoiceId() } == Optional.of(invoiceId)
```
The real gateway sits behind a proxy; it asserts predictable failure, the WARN line, and recovery once the fault clears.
This is the cut, one of the three faults; latency and timeout get features of the same shape.

### IT5 — One contract spec for each fake and its real adapter

**Bad**
```java
public class FakePaymentGateway implements PaymentGateway, Resettable {

    private final List<Payment> charges = new ArrayList<>();

    @Override
    public void charge(final Payment payment) {
        charges.add(payment);
    }

    @Override
    public List<Payment> chargesFor(final UUID invoiceId) {
        return charges.stream().filter(p -> p.invoiceId().equals(invoiceId)).toList();
    }
```
No contract spec covers the fake, so it records a repeated payment twice while the real gateway is idempotent.

**Good**
```groovy
abstract class PaymentGatewayContract extends Specification {
    abstract PaymentGateway gateway()

    def "should charge an invoice once when the same payment is sent twice"() {
        given: "one payment for an open invoice"
        def payment = new Payment(PAYMENT_ID, INVOICE_ID, money("40.00"))

        when: "the same payment reaches the gateway twice"
        gateway().charge(payment)
        gateway().charge(payment)

        then: "a second charge would bill the customer twice"
        gateway().chargesFor(INVOICE_ID) == [payment]
    }
}
```
`FakePaymentGatewaySpec` and `PaymentGatewayAdapterIT` both extend one contract, so the fake cannot drift from the real
gateway unnoticed.

### SP1 — One field name for one overridden bean

**Good**
```groovy
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
class InvoiceControllerIT extends Specification {

    @Autowired ApplicationContext applicationContext

    @TestBean
    ExchangeRateProvider exchangeRateProvider

    static ExchangeRateProvider exchangeRateProvider() {
        new FakeExchangeRateProvider()
    }
```
Every IT that overrides `ExchangeRateProvider` names the field `exchangeRateProvider`, so they share one cached Spring
context; the shared fakes do not hold this port, so each class overrides it.

### SP2 — Override only a bean whose advice the IT does not assert

**Good**
```java
/**
 * Shared fakes for outbound ports. Each replaced bean carries no @Transactional, @Cacheable,
 * @Retryable or method security, so replacing it bare removes no advice an IT could assert.
 */
@TestConfiguration
public class OutboundFakesConfig {

    @Bean
    @Primary
    PaymentGateway fakePaymentGateway() {
        return new FakePaymentGateway();
    }
```
The javadoc records the advice check beside the override, so a later advised bean is not replaced unnoticed.

### SP3 — Take isolation from the shared reset, never from @Transactional

**Bad**
```java
@Transactional
class InvoiceControllerIT extends AbstractIT {

    @Test
    void shouldPayInvoice() {
        http.post().uri("/api/invoices/{id}/payments", invoiceId).header(AUTHORIZATION, clerkAuth).exchange()
            .expectStatus().isCreated();
        // server thread already committed — this "rollback" undoes nothing it wrote
    }
```
The test's transaction is not the server's, so the payment rows the server committed leak into the next test.

**Good**
```groovy
/**
 * No @Transactional and no per-feature DELETE: @EnableSharedContainers resets the database before
 * every feature, and invoices and payments are not in its keep-list, so both start empty.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
class InvoiceControllerIT extends Specification {

    @Autowired
    ApplicationContext applicationContext

    @Autowired
    JdbcTemplate jdbc
```
One reset interceptor owns isolation and runs whatever thread the server committed on; the spec cleans up nothing by
hand.

### SP4 — Flush before asserting a constraint or a write

**Bad**
```groovy
    def "should refuse a second invoice for one order"() {
        given: "an invoice for an order"
        persistInvoice(ORDER_ID, "40.00")

        when: "a second invoice for the same order is persisted"
        persistInvoice(ORDER_ID, "45.00")

        then: "never thrown: the insert sits unflushed in the persistence context and is rolled back"
        def e = thrown(ConstraintViolationException)
        e.constraintName == "uq_invoice_order"
    }
```
Without a flush the second insert never reaches Postgres, so the unique index never runs and the expected exception never comes.

**Good**
```groovy
    def "should refuse a second invoice for one order"() {
        given: "an invoice for an order"
        persistInvoice(ORDER_ID, "40.00")

        when: "a second invoice for the same order reaches Postgres"
        persistInvoice(ORDER_ID, "45.00")
        em.flush()

        then: "the unique index refuses it, so one order is never billed twice"
        def e = thrown(ConstraintViolationException)
        e.constraintName == "uq_invoice_order"
    }
```
The flush inside `when:` sends the insert to the database, and the bound exception names the exact index.

### SP5 — Keep the real database in a slice test

**Bad**
```groovy
@DataJpaTest
abstract class OrdersRepositoryIT extends Specification {
```
Without `replace = NONE` Boot swaps in an embedded database unlike production Postgres, or fails when none is on the classpath.

**Good**
```groovy
/** replace = NONE keeps the singleton Postgres; without it Boot swaps in an embedded database. */
@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)
@ContextConfiguration(initializers = SharedContainersInitializer)
abstract class OrdersRepositoryIT extends Specification {

    @Autowired
    TestEntityManager em
```
Both halves of the rule sit on the slice base class, with the reason on one line.

### SP6 — A one-line reason beside every @DirtiesContext

**Good**
```groovy
// TaxCalculator resolves its rates once at construction; this spec changes them, so no later spec may reuse it.
@DirtiesContext
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
class TaxRateOverrideIT extends Specification {
```
The reason names what the spec changes and why reusing the context would give later specs wrong rates.

### SP7 — Count contexts before raising a limit

**Bad**
```java
    // configuration (~20 in orders-api alone — every @Import / @MockitoBean / @TestPropertySource
    // makes a new cache key), none are evicted below the cache's 32-entry default, and each holds a
    // fixed Hikari pool of application.yml's maximum-pool-size of 5. 20 x 5 = 100 idle connections
    ...
                    .withCommand("postgres", "-c", "max_connections=300");
```
The connection limit is raised on an estimated context count, and nothing measures how many contexts really exist.

**Good**
```yaml
# orders-api/src/test/resources/application-it.yml — temporary, while diagnosing
logging:
  level:
    org.springframework.test.context.cache: DEBUG
```
The cache logger prints size, hits and misses, so the context count is measured before any limit changes.

### SP8 — Shared properties in the singleton initializer

**Bad**
```java
    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url",      postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
        r.add("spring.data.redis.host",     redis::getHost);
    }
```
Per-class properties enter the context cache key, so this class forks its own Spring context.

**Good**
```java
    @Override
    public void initialize(final ConfigurableApplicationContext ctx) {
        TestPropertyValues.of(
                "spring.datasource.url=" + POSTGRES.getJdbcUrl(),
                "spring.datasource.username=" + POSTGRES.getUsername(),
                "spring.datasource.password=" + POSTGRES.getPassword(),
                "spring.data.redis.host=" + REDIS.getHost(),
                "spring.data.redis.port=" + REDIS.getMappedPort(REDIS_PORT),
                "payment.gateway.url=" + sharedGatewayUrl())
                .applyTo(ctx);
    }
```
One property set in the shared initializer serves every IT, so all of them share one cache key.

### SP9 — Keep lifecycle beans pauseable

**Bad**
```java
    @EventListener(ApplicationReadyEvent.class)
    void start() {
        ensureGroup();
        running.set(true);
        loopThread = Thread.ofPlatform().name("billing-consumer").daemon(false).start(this::loop);
        log.info("Started billing consumer on stream={} group={}", STREAM_KEY, CONSUMER_GROUP);
    }

    @PreDestroy
    void stop() {
```
The consumer is not a lifecycle bean, so every cached test context keeps reading `orders.placed` until the JVM exits.

**Good**
```java
@Component
public class BillingConsumer implements SmartLifecycle {
    @Override
    public void start() {
        ensureGroup();
        running.set(true);
        loopThread = Thread.ofPlatform().name("billing-consumer").start(this::loop);
        log.info("action=billing_consumer_start stream={} group={}", STREAM_KEY, CONSUMER_GROUP);
    }

    @Override
    public void stop() {
        running.set(false);
        loopThread.interrupt();
    }
```
A `SmartLifecycle` bean is pauseable by default, so Spring stops the loop while its context waits in the test cache.

### SP10 — No preemptive timeout in a transactional test

**Bad**
```java
    @Test
    void shouldMarkOverdueInvoices() {
        assertTimeoutPreemptively(Duration.ofSeconds(10), () -> repo.markOverdue(today)); // new thread: no tx, no rollback
    }
```
The timed body runs on another thread outside the test transaction, so its writes commit and never roll back.

**Good**
```groovy
    @Timeout(10)
    def "should find only invoices past their due date"() {
        given: "one invoice due yesterday and one due today"
        persistInvoice(ORDER_ID, TODAY.minusDays(1))
        persistInvoice(OTHER_ORDER_ID, TODAY)
        em.flush()
        em.clear()

        when: "the overdue invoices are looked up"
        def overdue = repo.findOverdue(TODAY)

        then: "an invoice due today is not overdue yet, so it must not be reminded"
        overdue*.orderId() == [ORDER_ID]
    }
```
Spock's `@Timeout` keeps the feature on the test thread, so the slice transaction stays bound and still rolls back.

### SP11 — Keep the component scan off the class a slice finds

**Bad**
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan("com.example.orders")
@EnableJpaRepositories(["com.example.orders.repository",
                        "com.example.orders.billing.repository"])
@EntityScan(["com.example.orders.entity", "com.example.orders.billing.entity"])
class OrdersTestApplication {
```
Any `@DataJpaTest` that finds this class also scans and loads every service, because an explicit scan disables slice filters.

**Good**
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@EnableJpaRepositories([
    "com.example.orders.repository",
    "com.example.orders.billing.repository"])
class OrdersTestApplication {
}

/** The services OrdersIT calls. Only OrdersIT imports it, so a slice that finds OrdersTestApplication loads none. */
@Configuration(proxyBeanMethods = false)
@ComponentScan("com.example.orders")
class OrdersServicesConfig {
}
```
The scan moves off the class a slice searches for; only the full `@SpringBootTest` imports the services config.
