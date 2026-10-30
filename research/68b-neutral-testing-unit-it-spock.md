# 68b — Neutral Good/Bad pairs: unit tests · integration tests · Spock (#99, map #9)

Source: research/31b-v2.md:1-617 (U1–U4, IT1–IT5, IT4b, SP1–SP11); research/47-good-rewrites.md (replaces the pair for IT2, IT4, SP2, SP11; replaces the Good only for SP3, SP5, whose Bad stays the 31b one because it shows the rule's own defect). Domain: ordering + billing (#99 brief). Stand-ins: `@EnableAruviiSpec` / `@EnableAruviiIT` → `@EnableSharedContainers` · `AruviiTestcontainersInitializer` → `SharedContainersInitializer` · `AruviiSpecResetInterceptor` → `SharedResetInterceptor`, `AruviiTestReset` → `TestReset` (SP3) · `PRESERVE` list kept as the reset's keep-list (SP3) · MiniStack S3 container of a non-Spring IT → PaymentGateway sandbox container (`SharedContainersInitializer.sharedGatewayUrl()`) (IT2) · owned settings port stubbed in an IT → `EmailSender` stubbed, replaced by `FakeEmailSender` (IT4) · audit port verified by Mock() → `InvoiceRepository.save` verified, writing the invoice IS the behaviour (U3) · provider rotation reminder → `OverdueReminder` on invoices past due (U1, U4) · password-reset expiry → invoice due-date check before payment (U4) · notification-config 400 per blank field → `/api/orders` 400 per blank field (IT1) · webhook controller over standalone MockMvc → order cancel endpoint (IT3) · agent-count-by-tool port and its SQL semantics → `PaymentGateway` and its idempotent charge (IT5) · connection-test port overridden by `@TestBean` → `ExchangeRateProvider`, a port the shared fakes do not hold (SP1) · pricing-override partial unique index → one invoice per order, `uq_invoice_order` (SP4) · SSRF allowlist resolved once → tax rates resolved once by `TaxCalculator` (SP6) · chat stream consumer → `BillingConsumer` on `orders.placed` (SP9) · sweepable-runs query → `findOverdue` (SP10) · chat test application → `OrdersTestApplication` (SP11). Added terms: `OverdueReminder.overdueInvoices(graceDays)` · `OrderController` · `OrderControllerIT`, `InvoiceControllerIT`, `PaymentGatewayIT` · `PaymentGatewayContract`, `FakePaymentGatewaySpec`, `PaymentGatewayAdapterIT` · `OrdersRepositoryIT` (repository-slice base, as in 68a), `OrdersTestApplication`, `OrdersServicesConfig` · `BillingConsumer` · `uq_invoice_order` · `invoices` / `payments` tables · `RestTestClient http`, `login(role)` helper · `payment.gateway.url` property · `PaymentGatewayAdapter` (real adapter, IT2/IT5) · `PaymentGateway.charge(payment)`, `chargesFor(invoiceId)` (IT5) · `Resettable` (fake reset hook, IT5) · `FakeEmailSender.sent()`, `OverdueReminder.remindOverdue()` (IT4) · `InvoiceRepository.findOpen()`, `findOverdue(date)`, `Invoice.withStatus(...)` (U4, SP10) · `AbstractIT` (JUnit IT base, SP3 Bad), `OrdersIT`, `TaxRateOverrideIT` · sandbox image `example/payment-sandbox` · packages `com.example.orders.repository` / `.billing.repository` / `.entity` (SP11) · `persistInvoice(...)`, `seedSandboxAccounts(...)` spec helpers · `ExchangeRateProvider`, `FakeExchangeRateProvider` (SP1) · `InvoiceRepository.markOverdue(date)` (SP10 Bad).
Skipped: IT4b — MERGED into IT4 (2026-10-04). (U2 is SUPERSEDED by U2a on naming only; its labelled-blocks clause stands, so the pair is kept and shows both.)
Stand-ins (Spock part): `@EnableSharedContainers` for the project's Spock IT annotation (K15) · `AbstractIT` kept as the generic JUnit IT base (K15) · trust/SSL port of K3 → `PaymentGateway` · lease + interaction row of K13 → gateway charge + `markPaid` · SQL analytics of K10 → `OverdueReminder` run · config parse of K6/K8 → `DiscountPolicy` / line quantity parse · logback logger kept as the global state (K14, K16) · Added terms: enum type names `CustomerTier`, `OrderStatus`, `InvoiceStatus` · `Quantity.Valid` / `Quantity.Invalid` (sealed parse result, K8) · `HttpPaymentGateway` (HTTP adapter of PaymentGateway, K9) · Hibernate `ConstraintViolationException` + constraint `invoices_order_id_key` (K19) · test helpers `eur()`, `line()`, `insertInvoice()` · Skipped: none (K1–K20, K2b all APPROVED)

### U1 — Every test is A-TRIP: automatic, thorough, repeatable, independent, professional

**Bad** (neutral)
```java
    private void await(java.util.function.BooleanSupplier cond) {
        long deadline = System.currentTimeMillis() + 60_000;
        while (System.currentTimeMillis() < deadline) {
            if (cond.getAsBoolean()) return;
            try { Thread.sleep(250); } catch (InterruptedException e) {
                Thread.currentThread().interrupt(); return;
            }
        }
        throw new AssertionError("invoice never became OVERDUE within 60s");
    }
```
What goes wrong: the result depends on wall-clock time and host speed, and an interrupt returns silently as if the condition held.

**Good** (neutral)
```groovy
    InvoiceRepository invoiceRepository = Stub()
    OverdueReminder reminder = new OverdueReminder(
        invoiceRepository,
        new FakeEmailSender(),
        Clock.fixed(NOW, ZoneOffset.UTC))

    def "should treat an invoice one day past due as overdue, and not one due today"() {
        given: "two open invoices, one due exactly today and one due yesterday"
        invoiceRepository.findOpen() >> [invoice("due-today", TODAY), invoice("due-yesterday", TODAY.minusDays(1))]
        when: "the reminder looks for overdue invoices"
        def overdue = reminder.overdueInvoices(0)

        then: "the due date itself is not yet overdue"
        overdue*.id() == ["due-yesterday"]
```
Why: a fixed clock, a fresh instance per feature and both sides of the boundary make the test repeatable and independent.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/modelswap/UiModelSwapE2EIT.java:600-609` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:31-52` (Good, adapted) · source 31b-v2.md:13 · fix from 31b-v2.md:14-32

### U2 — Labelled given:/when:/then: (expect:/where:); name is a "should …" behaviour sentence (U2a)

**Bad** (neutral)
```groovy
    def "shouldCarryTheLinesAnOrderIsPlacedWith"() {
        given:
        final first = new OrderLine("SKU-1", 2, money("10.00"))
        final second = new OrderLine("SKU-2", 1, money("5.00"))

        when:
        final order = Order.draft(CUSTOMER_ID, [first, second])

        then:
        order.lines() == [first, second]
    }
```
What goes wrong: a camelCase JUnit name in Spock, blocks with no description, `final` locals, and when:/then: for a pure construction.

**Good** (neutral)
```groovy
    def "should keep the lines a draft order is created with, in their order"() {
        given: "two lines for different products"
        def first = new OrderLine("SKU-1", 2, money("10.00"))
        def second = new OrderLine("SKU-2", 1, money("5.00"))

        expect: "the invoice later totals exactly these lines, so none may be dropped or reordered"
        Order.draft(CUSTOMER_ID, [first, second]).lines() == [first, second]
    }
```
Why: the name is a sentence starting with "should", each block says why, `def` locals, and `expect:` fits a pure construction.

Evidence: `aruvii-shared/src/test/groovy/ai/aruvii/shared/authz/CollectionScopeSpec.groovy:12-22` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:40-48` (Good, adapted; neutral Good is the Bad rewritten instead) · source 31b-v2.md:50 · fix from 31b-v2.md:51-63, U2a (19-approved-rules.md:132)

### U3 — Double only at a boundary; Stub() for returners, Mock() only when the call is the behaviour

**Bad** (neutral)
```groovy
    OrderRepository orderRepository = Mock()
    InvoiceRepository invoiceRepository = Mock()
    PaymentGateway paymentGateway = Mock()
    ...
            orderRepository.findById(ORDER_ID) >> Optional.of(placedOrder(ORDER_ID))
```
What goes wrong: every port is a `Mock()` that is only stubbed and never verified, so the spec hides which call is the behaviour.

**Good** (neutral)
```groovy
    OrderRepository orderRepository = Stub()
    InvoiceRepository invoiceRepository = Mock()
    InvoiceService service = new InvoiceService(
        orderRepository,
        invoiceRepository,
        new TaxCalculator(),
        Clock.fixed(NOW, ZoneOffset.UTC))
    ...
        then: "exactly one invoice is saved, open and for this order"
        1 * invoiceRepository.save({ Invoice i ->
            i.orderId() == ORDER_ID
            i.status() == InvoiceStatus.OPEN
        }) >> { Invoice i -> i }
```
Why: the lookup only returns, so it is a `Stub()`; saving the invoice is the behaviour, so only that call is a verified `Mock()`.

Evidence: `aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:31-33,67` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:24-27,50-51` (Good, adapted) · source 31b-v2.md:82 · fix from 31b-v2.md:83-96

### U4 — Production logic takes an injected Clock; never calls the wall clock directly

**Bad** (neutral)
```java
        if (invoice.status() == InvoiceStatus.PAID) {
            throw new OrderException(ErrorCode.INVOICE_ALREADY_PAID);
        }
        if (invoice.dueDate().isBefore(LocalDate.now())) {
            invoiceRepository.save(invoice.withStatus(InvoiceStatus.OVERDUE));
        }
```
What goes wrong: the due-date check reads the wall clock, so a test cannot pin "due exactly today" against "due yesterday".

**Good** (neutral)
```java
    public List<Invoice> overdueInvoices(final int graceDays) {
        log.info("action=invoice_overdue_scan graceDays={}", graceDays);
        final var today = LocalDate.now(clock);
        final var cutoff = today.minusDays(graceDays);
        return invoiceRepository.findOpen().stream()
                .filter(invoice -> invoice.dueDate().isBefore(cutoff))
                .toList();
    }
```
Why: one date from the injected clock decides the cutoff, so a spec with `Clock.fixed(...)` pins the boundary exactly.

Evidence: `aruvii-auth/src/main/java/ai/aruvii/auth/application/PasswordResetService.java:76-81` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-providers/src/main/java/ai/aruvii/providers/application/ProviderService.java:674-687` (Good, adapted; null-deciding filter dropped) · source 31b-v2.md:108 · fix from 31b-v2.md:109-126

### IT1 — An IT proves wiring and contracts; it does not re-test unit-owned business branches

**Bad** (neutral)
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
What goes wrong: one slow HTTP test per blank field re-runs validation branches that the order validator's unit spec already owns.

**Good** (neutral)
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
Why: one IT proves the refusal-to-400 mapping through the real stack; the field branches stay in the fast unit spec.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/NotificationConfigControllerIT.java:187-192,198-199` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-worker/src/integrationTest/groovy/ai/aruvii/worker/stream/ConsumerIdentityIT.groovy:48-67` (Good, adapted; neutral Good is the Bad rewritten instead) · source 31b-v2.md:142 · fix from 31b-v2.md:143-175

### IT2 — ITs get containers only from the singleton initializer; no @Testcontainers/@Container/@ServiceConnection

**Bad** (neutral)
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
What goes wrong: the class starts its own container and stops it when the class ends, outside the shared singleton every other IT uses.

**Good** (neutral)
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
Why: the container lives in the shared initializer beside Postgres, so no spec owns its lifecycle and every spec reuses it.

Evidence: `aruvii-tools/src/integrationTest/java/ai/aruvii/tools/infrastructure/handlers/FileToolHandlerS3IT.java:39-40,61-66` @772736bf (Bad, real) · source 31b-v2.md:178 · fix from research/47-good-rewrites.md:285-302 (replaces 31b-v2.md:179-205; CV5 exempts the old Bad)

### IT3 — ITs call the real server via RestTestClient (RANDOM_PORT); never MockMvc/TestRestTemplate

**Bad** (neutral)
```java
        OrderController ctrl = new OrderController(orderService, invoiceService, paymentGateway, clock);
        mockMvc = MockMvcBuilders.standaloneSetup(ctrl).build();
    ...
        mockMvc.perform(post("/api/orders/{orderId}/cancel", orderId)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"reason\":\"customer request\"}"))
            .andExpect(status().isAccepted());
```
What goes wrong: HTTP-shaped assertions over standalone MockMvc skip the filter chain, security and error advice the real server applies.

**Good** (neutral)
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
Why: RestTestClient on RANDOM_PORT sends real HTTP through security and error handling, with a token from a real login.

Evidence: `aruvii-api/src/test/java/ai/aruvii/api/controller/WebhookControllerRunContextTest.java:63-65,87-90` @origin/master 2026-10-02, no sha in source (Bad, real) · `aruvii-api/src/integrationTest/groovy/ai/aruvii/api/controller/WorkspaceCallerRoleIT.groovy:88-102` (Good, adapted) · source 31b-v2.md:207 · fix from 31b-v2.md:208-227

### IT4 — Swap a collaborator only at an outbound port with a fake bean; never a mock

**Bad** (neutral)
```groovy
    def "should send the overdue notice when the reminder runs"() {
        given: "a reminder whose email sender is a Spock double"
        EmailSender emailSender = Stub() {
            send(_) >> true
        }
        def reminder = new OverdueReminder(invoiceRepository, emailSender, clock)
```
What goes wrong: the IT replaces an outbound port with a double that has no behaviour of its own, and repeats that stub per feature.

**Good** (neutral)
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
Why: the subject is the wired bean, and the port is the shared in-memory fake from `OutboundFakesConfig`, with its own contract spec (IT5), instead of one stub per feature.

Evidence: `aruvii-worker/src/integrationTest/groovy/ai/aruvii/worker/webhook/KafkaCallbackPublisherDrainIT.groovy:39-44` @772736bf (Bad, real) · source 31b-v2.md:243 · fix from research/47-good-rewrites.md:317-335 (replaces 31b-v2.md:244-274)

### IT5 — Every fake port has a contract spec run against both fake and real adapter

**Bad** (neutral)
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
What goes wrong: no contract spec covers the fake, so it records a repeated payment twice while the real gateway is idempotent.

**Good** (neutral)
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
Why: `FakePaymentGatewaySpec` and `PaymentGatewayAdapterIT` both extend one contract, so the fake cannot drift from the real gateway unnoticed.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakeAgentCountByToolPort.java:17-29` @origin/master 2026-10-02, no sha in source (Bad, real) · langchain4j `Abstract*IT` (R19) over `AgentCountByToolQueryIT.groovy:28-38` (Good, adapted) · source 31b-v2.md:307 · fix from 31b-v2.md:308-327

### SP1 — A bean overridden with @TestBean in several classes uses the identical field name

**Bad** (n/a) — the source found no `@TestBean` that overrides one type under two field names.

**Good** (neutral)
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
Why: every IT that overrides `ExchangeRateProvider` names the field `exchangeRateProvider`, so they share one cached Spring context; the shared fakes do not hold this port, so each class overrides it.

Evidence: no Bad (n/a, 31b-v2.md:364) · `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/ProviderTagsIT.java:20-27` @origin/master 2026-10-02, no sha in source (Good, adapted) · source 31b-v2.md:346 · fix from 31b-v2.md:347-362

### SP2 — A @TestBean/fake replaces the bean bare; never override a bean whose advice the IT asserts

**Bad** (n/a) — no real Bad: no bean the ITs override carries `@Transactional`, `@Cacheable`, `@Retryable`, method security or `@Async`.

**Good** (neutral)
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
Why: the javadoc records the advice check beside the override, so a later advised bean is not replaced unnoticed.

Evidence: no Bad (n/a, research/47-good-rewrites.md:339) · `aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakePortsConfig.java:8-24` @772736bf (Good, rewritten) · source 31b-v2.md:366 · fix from research/47-good-rewrites.md:341-356

### SP3 — Never @Transactional on a RANDOM_PORT IT; isolation comes from the shared reset

**Bad** (neutral)
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
What goes wrong: the test's transaction is not the server's, so the payment rows the server committed leak into the next test.

**Good** (neutral)
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
Why: one reset interceptor owns isolation and runs whatever thread the server committed on; the spec cleans up nothing by hand.

Evidence: Bad adapted from Spring Boot §with-running-server (R22), no Aruvii path (31b-v2.md:401-413); nearest real case `aruvii-api/src/integrationTest/java/ai/aruvii/api/dashboard/DashboardControllerIT.java:26,34-43` @772736bf (hand DELETE isolation) · `aruvii-test-support/src/main/java/ai/aruvii/testsupport/spock/AruviiSpecResetInterceptor.java:24-36` (old Good, real) · source 31b-v2.md:382 · fix from research/47-good-rewrites.md:377-393 (javadoc also names @Transactional, so it fixes the 31b Bad)

### SP4 — In @DataJpaTest specs call em.flush() before asserting a constraint or write

**Bad** (neutral)
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
What goes wrong: without a flush the second insert never reaches Postgres, so the unique index never runs and the expected exception never comes.

**Good** (neutral)
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
Why: the flush inside `when:` sends the insert to the database, and the bound exception names the exact index.

Evidence: Bad adapted from Spring Boot §data-jpa (R22), no Aruvii path (31b-v2.md:433-446) · `aruvii-infra/src/integrationTest/groovy/ai/aruvii/infra/repository/PricingOverrideRepositoryIT.groovy:96-106` @origin/master 2026-10-02, no sha in source (Good, adapted) · source 31b-v2.md:415 · fix from 31b-v2.md:416-431

### SP5 — Slice tests use @AutoConfigureTestDatabase(replace = NONE) plus the singleton initializer

**Bad** (neutral)
```groovy
@DataJpaTest
abstract class OrdersRepositoryIT extends Specification {
```
What goes wrong: without `replace = NONE` Boot swaps in an embedded database unlike production Postgres, or fails when none is on the classpath.

**Good** (neutral)
```groovy
/** replace = NONE keeps the singleton Postgres; without it Boot swaps in an embedded database. */
@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)
@ContextConfiguration(initializers = SharedContainersInitializer)
abstract class OrdersRepositoryIT extends Specification {

    @Autowired
    TestEntityManager em
```
Why: both halves of the rule sit on the slice base class, with the reason on one line.

Evidence: Bad adapted from Spring Boot §data-jpa (R22), no Aruvii path (31b-v2.md:461-466; 47:397 finds no real Bad) · `aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentsRepositoryIT.groovy:16-29` @772736bf (Good, rewritten) · source 31b-v2.md:448 · fix from research/47-good-rewrites.md:399-410

### SP6 — No @DirtiesContext without a one-line reason

**Bad** (n/a) — the source found no `@DirtiesContext` in any test source.

**Good** (neutral)
```groovy
// TaxCalculator resolves its rates once at construction; this spec changes them, so no later spec may reuse it.
@DirtiesContext
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
class TaxRateOverrideIT extends Specification {
```
Why: the reason names what the spec changes and why reusing the context would give later specs wrong rates.

Evidence: no Bad (n/a, 31b-v2.md:479) · Spring `@DirtiesContext` docs (R22) onto `NotificationTestSsrfAllowlistIT` (Good, adapted) · source 31b-v2.md:468 · fix from 31b-v2.md:469-477

### SP7 — When ITs slow or connections grow, log the context cache at DEBUG and count first

**Bad** (neutral)
```java
    // configuration (~20 in orders-api alone — every @Import / @MockitoBean / @TestPropertySource
    // makes a new cache key), none are evicted below the cache's 32-entry default, and each holds a
    // Hikari pool that idles at application.yml's minimum-idle of 5. 20 x 5 = 100 idle connections
    ...
                    .withCommand("postgres", "-c", "max_connections=300");
```
What goes wrong: the connection limit is raised on an estimated context count, and nothing measures how many contexts really exist.

**Good** (neutral)
```yaml
# orders-api/src/test/resources/application-it.yml — temporary, while diagnosing
logging:
  level:
    org.springframework.test.context.cache: DEBUG
```
Why: the cache logger prints size, hits and misses, so the context count is measured before any limit changes.

Evidence: `aruvii-test-support/src/main/java/ai/aruvii/testsupport/AruviiTestcontainersInitializer.java:43-45,54` @origin/master 2026-10-02, no sha in source (Bad, real) · Spring caching.html (R22) (Good, adapted) · source 31b-v2.md:481 · fix from 31b-v2.md:482-489

### SP8 — Shared IT properties go in the singleton initializer, never per-class @DynamicPropertySource

**Bad** (neutral)
```java
    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url",      postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
        r.add("spring.data.redis.host",     redis::getHost);
    }
```
What goes wrong: per-class properties enter the context cache key, so this class forks its own Spring context.

**Good** (neutral)
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
Why: one property set in the shared initializer serves every IT, so all of them share one cache key.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:60-66` @origin/master 2026-10-02, no sha in source (Bad, real; CV5 bootstrap exception, shown for the pattern) · `aruvii-test-support/src/main/java/ai/aruvii/testsupport/AruviiTestcontainersInitializer.java:75-82` (Good, adapted; tail of the call completed) · source 31b-v2.md:501 · fix from 31b-v2.md:502-513

### SP9 — Stream consumers, schedulers and other lifecycle beans stay pauseable

**Bad** (neutral)
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
What goes wrong: the consumer is not a lifecycle bean, so every cached test context keeps reading `orders.placed` until the JVM exits.

**Good** (neutral)
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
Why: a `SmartLifecycle` bean is pauseable by default, so Spring stops the loop while its context waits in the test cache.

Evidence: `aruvii-worker/src/main/java/ai/aruvii/worker/chat/ChatStreamConsumer.java:73-82` @origin/master 2026-10-02, no sha in source (Bad, real) · Spring context-pausing.html (R22) onto `ChatStreamConsumer.java:73-85` (Good, adapted) · source 31b-v2.md:528 · fix from 31b-v2.md:529-548

### SP10 — No preemptive timeout (assertTimeoutPreemptively) in a transactional test

**Bad** (neutral)
```java
    @Test
    void shouldMarkOverdueInvoices() {
        assertTimeoutPreemptively(Duration.ofSeconds(10), () -> repo.markOverdue(today)); // new thread: no tx, no rollback
    }
```
What goes wrong: the timed body runs on another thread outside the test transaction, so its writes commit and never roll back.

**Good** (neutral)
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
Why: Spock's `@Timeout` keeps the feature on the test thread, so the slice transaction stays bound and still rolls back.

Evidence: Bad adapted, no Aruvii path (31b-v2.md:584-592) · Spring tx.html §preemptive timeouts (R22) onto `aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:28-38` @origin/master 2026-10-02, no sha in source (Good, adapted) · source 31b-v2.md:566 · fix from 31b-v2.md:567-582

### SP11 — No explicit @ComponentScan on the @SpringBootApplication/configuration slices find

**Bad** (neutral)
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan("com.example.orders")
@EnableJpaRepositories(["com.example.orders.repository",
                        "com.example.orders.billing.repository"])
@EntityScan(["com.example.orders.entity", "com.example.orders.billing.entity"])
class OrdersTestApplication {
```
What goes wrong: any `@DataJpaTest` that finds this class also scans and loads every service, because an explicit scan disables slice filters.

**Good** (neutral)
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
Why: the scan moves off the class a slice searches for; only the full `@SpringBootTest` imports the services config.

Evidence: `aruvii-chat/src/integrationTest/groovy/ai/aruvii/chat/ChatTestApplication.groovy:38-44` @772736bf (Bad, real, latent) · source 31b-v2.md:594 · fix from research/47-good-rewrites.md:426-442 (replaces 31b-v2.md:595-605)

### K1 — Mock-argument closure: plain lines, or verifyAll(it, Type) for many fields

**Bad** (neutral)
```groovy
        then: "the invoice is saved for the placed order"
        1 * invoiceRepository.save({ Invoice i ->
            assert i.orderId == orderId
            assert i.total == eur("42.00")
            assert i.dueDate == LocalDate.parse("2026-12-01")
            assert i.status == InvoiceStatus.OPEN
            true
        }) >> { Invoice i -> i }
```
What goes wrong: the old assert-then-true ritual stops at the first wrong field, so one run never shows the other broken fields.

**Good** (neutral)
```groovy
    def "should save an open invoice for the placed order"() {
        when: "a placed order is invoiced"
        invoiceService.invoice(placedOrder)

        then: "every field a reminder or a payment reads later is in place"
        1 * invoiceRepository.save({
            verifyAll(it, Invoice) {
                orderId == placedOrder.id
                total == eur("42.00")
                dueDate == LocalDate.parse("2026-12-01")
                status == InvoiceStatus.OPEN
            }
        }) >> { Invoice i -> i }
    }
```
Why: verifyAll checks each field of the argument and reports every failing one, with no assert keyword and no trailing true.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:63-70` @master 2026-10-02, no sha in source (Bad, real) · `aruvii-infra/src/test/groovy/ai/aruvii/infra/adapter/PricingSyncAdapterSpec.groovy:34-47` (Good, adapted) · source research/31b-v2.md:620 · fix from research/31b-v2.md:640 (verifyAll(it, Type) remark)

### K2 — Return-and-verify is one interaction: 1 * repo.save(…) >> saved

**Bad** (neutral)
```groovy
    def "should keep the invoice total when the invoice is stored"() {
        given: "the repository hands back what it is given"
        invoiceRepository.save(_) >> { Invoice i -> i }

        when: "the invoice for a two-line order is stored"
        def saved = invoiceService.store(invoice)

        then: "it is saved once and the total survives"
        1 * invoiceRepository.save({ it.total == eur("42.00") })
        saved.total == eur("42.00")
    }
```
What goes wrong: the then: interaction replaces the given: stub, so save returns null and saved.total throws a NullPointerException.

**Good** (neutral)
```groovy
    def "should keep the invoice total when the invoice is stored"() {
        when: "the invoice for a two-line order is stored"
        def saved = invoiceService.store(invoice)

        then: "a lost total would bill the customer nothing"
        1 * invoiceRepository.save({ Invoice i ->
            i.total == eur("42.00")
        }) >> { Invoice i -> i }

        and: "the invoice handed back carries the same total"
        saved.total == eur("42.00")
    }
```
Why: one interaction carries the count, the argument check and the return value, so nothing overrides the stub.

Evidence: none on master (Bad, adapted from Spock interaction_based_testing.adoc:734-746) · `aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/AgentEvalRepositoryAdapterSpec.groovy:89-110` @master 2026-10-02 (Good, adapted) · source research/31b-v2.md:651 · fix from research/31b-v2.md:653-668

### K2b — Verified interactions match real values or a field constraint; _ only when not promised

**Bad** (neutral)
```groovy
    def "should replace the lines of this order only"() {
        when: "the clerk replaces the lines of a draft order"
        orderService.replaceLines(orderId, [line("SKU-1", 2), line("SKU-2", 1)])

        then: "the old lines go and the new ones are saved"
        1 * orderRepository.deleteLinesOf(_)
        1 * orderRepository.save(_) >> { Order o -> o }
    }
```
What goes wrong: the order id is known, but the wildcard lets a delete of another order's lines pass.

**Good** (neutral)
```groovy
    def "should replace the lines of this order only"() {
        given: "a repository that hands back the order it stores"
        orderRepository.save(_) >> { Order o -> o }

        when: "the clerk replaces the lines of a draft order"
        orderService.replaceLines(orderId, [line("SKU-1", 2), line("SKU-2", 1)])

        then: "a delete scoped to any other order would empty a customer's cart"
        1 * orderRepository.deleteLinesOf(orderId)
    }
```
Why: the scope is the promise, so it is matched by its real value; the save belongs to another feature, so it is a stub in given:, never counted.

Evidence: `aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/PipelineRepositoryAdapterSpec.groovy:154-157` @master 2026-10-02 (Bad, real) · `aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:48-55` (Good, adapted) · source research/31b-v2.md:688 · fix from research/31b-v2.md:709 ("the id is known, so pipelineId")

### K3 — A Stub() never gets a call count; a verified call needs a Mock()

**Bad** (neutral)
```groovy
    PaymentGateway paymentGateway = Stub()
    ...
        then: "the invoice is charged once"
        1 * paymentGateway.charge(invoiceId, amount) >> new Payment(paymentId, invoiceId, amount)
```
What goes wrong: Spock rejects a call count on a Stub with InvalidSpecException when the spec runs.

**Good** (neutral)
```groovy
    def "should charge the gateway once for an open invoice"() {
        given: "a gateway whose calls are the assertion"
        PaymentGateway paymentGateway = Mock()
        def service = new InvoiceService(invoiceRepository, paymentGateway, clock)
        invoiceRepository.findById(invoiceId) >> Optional.of(openInvoice)

        when: "the customer pays the invoice"
        service.pay(invoiceId)

        then: "a second charge would bill the customer twice"
        1 * paymentGateway.charge(invoiceId, amount) >> new Payment(paymentId, invoiceId, amount)
    }
```
Why: the call is the behaviour under test, so the gateway is a Mock; a collaborator that only answers stays a Stub.

Evidence: none on master (Bad, adapted from Spock interaction_based_testing.adoc:785-788) · `aruvii-worker/src/test/groovy/ai/aruvii/worker/llm/AdapterHttpHelperSpec.groovy:57-70,74-77` @master 2026-10-02 (Good, adapted) · source research/31b-v2.md:712 · fix from research/31b-v2.md:714-728

### K4 — Assert only the interactions the feature promises

**Bad** (neutral)
```groovy
    def "should send the order confirmation to the customer's email"() {
        when: "the customer places a draft order"
        orderService.place(orderId)

        then: "the order is saved"
        1 * orderRepository.save(_) >> { Order o -> o }

        and: "the confirmation goes to the address on file"
        1 * emailSender.sendConfirmation(customer.email, _)
    }
```
What goes wrong: the save is not what this feature promises, so a change to how the order is stored breaks an email test.

**Good** (neutral)
```groovy
    def "should send the order confirmation to the customer's email"() {
        given: "a repository that hands back the order it stores"
        orderRepository.save(_) >> { Order o -> o }

        when: "the customer places a draft order"
        orderService.place(orderId)

        then: "a confirmation sent to any other address shows the order to a stranger"
        1 * emailSender.sendConfirmation(customer.email, _)
    }
```
Why: only the promised interaction is counted; the save is stubbed for the flow and owned by its own feature.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:57-62` @master 2026-10-02 (Bad, real) · `aruvii-agents/src/test/groovy/ai/aruvii/agents/application/AgentEvalServiceSpec.groovy:42-66` (Good, adapted) · source research/31b-v2.md:740 · fix from research/31b-v2.md:769 (the delete belongs to another feature)

### K5 — Exact count only when N is the contract; never count a read

**Bad** (neutral)
```groovy
    def "should email exactly one receipt when an invoice is paid"() {
        when: "the customer pays an open invoice"
        invoiceService.pay(invoiceId)

        then: "the invoice is looked up and the receipt goes out"
        1 * invoiceRepository.findById(invoiceId) >> Optional.of(openInvoice)
        1 * emailSender.sendReceipt(customer.email, _)
    }
```
What goes wrong: reading the invoice twice harms nothing, so counting the read breaks the test on a harmless refactor.

**Good** (neutral)
```groovy
    def "should email exactly one receipt when an invoice is paid"() {
        given: "an open invoice the service can find"
        invoiceRepository.findById(invoiceId) >> Optional.of(openInvoice)

        when: "the customer pays it"
        invoiceService.pay(invoiceId)

        then: "a second receipt tells the customer they paid twice"
        1 * emailSender.sendReceipt(customer.email, _)
    }
```
Why: the read is only stubbed; the count stays on the one email, because exactly one receipt is the contract.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:67-68` @master 2026-10-02 (Bad, real) · `aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:80-87` (Good, adapted) · source research/31b-v2.md:772 · fix from research/31b-v2.md:794 ("a stub suffices")

### K6 — Data tables: | inputs, || before expected; #var in the name; no @Unroll

**Bad** (neutral)
```groovy
    @Unroll
    def "should give a #tier customer #expected off an order of #subtotal"() {
```
What goes wrong: @Unroll is the default since Spock 2.0, so the annotation is noise that copies spread.

**Good** (neutral)
```groovy
    def "should give a #tier customer #expected off an order of #subtotal"() {
        expect: "only a gold customer at or above the threshold earns a discount"
        discountPolicy.discountFor(tier, subtotal) == expected

        where: "the threshold is 100.00 EUR"
        tier                  | subtotal      || expected
        CustomerTier.STANDARD | eur("150.00") || eur("0.00")
        CustomerTier.GOLD     | eur("99.99")  || eur("0.00")
        CustomerTier.GOLD     | eur("100.00") || eur("10.00")
    }
```
Why: || splits inputs from the expected value, and #var names each iteration without @Unroll.

Evidence: `aruvii-api/src/test/groovy/ai/aruvii/api/security/ApiKeyScopeInterceptorSpec.groovy:54-55` @master 2026-10-02 (Bad, real) · `aruvii-tools/src/test/groovy/ai/aruvii/tools/domain/RagToolConfigSpec.groovy:23-37` (Good, adapted) · source research/31b-v2.md:798 · fix from research/31b-v2.md:800-818

### K7 — where: reads only @Shared or static fields; build mocks in given:

**Bad** (neutral)
```groovy
    InvoiceRepository invoiceRepository = Mock()
    ...
        where: "each repository the guard might consult"
        repo << [invoiceRepository]
```
What goes wrong: where: cannot read an instance field or a mock, so Spock rejects the spec.

**Good** (neutral)
```groovy
    static final UUID INVOICE_ID = UUID.fromString("3f2a9c4e-7b1d-4e8a-9f60-2c5d8e1b7a43")
    def "should refuse #entryPoint on an invoice that is already paid"() {
        given: "the invoice on file is paid"
        invoiceRepository.findById(INVOICE_ID) >> Optional.of(paidInvoice)

        when: "the entry point is called"
        call(invoiceService)

        then: "acting on a paid invoice would charge or remind a customer who owes nothing"
        def e = thrown(OrderException)
        e.errorCode() == ErrorCode.INVOICE_ALREADY_PAID

        where: "every method that guards on the invoice status"
        entryPoint << ["pay", "remind"]
        call << [{ it.pay(INVOICE_ID) }, { it.remind(INVOICE_ID) }]
```
Why: the table reads only the static id and plain values; the mock stays an instance field, stubbed in given:.

Evidence: none on master — 47 records the Bad as n/a, Spock refuses it at run time (Bad, adapted from Spock data_driven_testing.adoc:100, kept from source) · `aruvii-agents/src/test/groovy/ai/aruvii/agents/application/AgentEvalServiceSpec.groovy:35-66` @772736bf (Good, rewritten) · source research/31b-v2.md:827 · fix from research/47-good-rewrites.md:444

### K8 — A data-driven feature tests one rule: no branch on a where: column

**Bad** (neutral)
```groovy
    def "should read a line quantity of #quantity"() {
        when: "the clerk's quantity is read"
        def parsed = OrderLine.parseQuantity(quantity)

        then: "valid quantities are kept and invalid ones refused"
        valid ? parsed == new Quantity.Valid(quantity) : parsed instanceof Quantity.Invalid

        where: "a mix of accepted and refused values"
        quantity | valid
        3        | true
        0        | false
    }
```
What goes wrong: the branch on the valid column hides two rules in one feature, and a failure names neither.

**Good** (neutral)
```groovy
    def "should refuse a line quantity of #quantity, never round it"() {
        when: "a value outside a whole number 1-999 is read"
        def parsed = OrderLine.parseQuantity(quantity)

        then: "the field is named, so the API and the orders page report the same thing"
        parsed == new Quantity.Invalid("quantity")

        where: "the refused rows from AC-2 and AC-3"
        quantity << [0, 1000, -1, 2.5, "3", true]
    }
```
Why: refused values get their own feature and accepted values another, so each failure names the one rule it broke.

Evidence: none on master (Bad, adapted from spock-best-practices data-driven :205-255) · `aruvii-tools/src/test/groovy/ai/aruvii/tools/domain/RagToolConfigSpec.groovy:39-48` @master 2026-10-02 (Good, adapted) · source research/31b-v2.md:851 · fix from research/31b-v2.md:853-866

### K9 — @Shared only for expensive read-only resources, never the subject

**Bad** (neutral)
```groovy
    @Shared
    HttpPaymentGateway gateway

    def setupSpec() {
        wireMock.start()
        gateway = new HttpPaymentGateway(restClient(),
            Duration.ofSeconds(2))
    }
```
What goes wrong: the class under test is shared by every feature, so state one feature leaves in it leaks into the next.

**Good** (neutral)
```groovy
    @Shared
    @AutoCleanup("stop")
    WireMockServer wireMock = new WireMockServer(options().dynamicPort())

    HttpPaymentGateway gateway = new HttpPaymentGateway(
        restClient(),
        Duration.ofSeconds(2))

    def setupSpec() {
        wireMock.start()
    }

    def setup() {
        wireMock.resetAll()
    }
```
Why: only the expensive server is shared and reset per feature; the cheap subject is built fresh for each feature.

Evidence: `aruvii-guardrails/src/test/groovy/ai/aruvii/guardrails/infrastructure/CustomPiiEndpointClientSpec.groovy:42-49` @772736bf (Bad, real) · `CustomPiiEndpointClientSpec.groovy:38-53` (Good, rewritten) · source research/31b-v2.md:884 · fix from research/47-good-rewrites.md:468

### K10 — Interactions live in the feature's own blocks, never in helpers

**Bad** (neutral)
```groovy
    def "should remind only the invoice that is overdue on the clock's date"() {
        given: "two open invoices, one due yesterday and one due tomorrow"
        stubTheInvoices()
    ...
    private void stubTheInvoices() {
        clock.instant() >> Instant.parse("2026-11-01T09:00:00Z")
        invoiceRepository.findOpen() >> [dueYesterday, dueTomorrow]
    }
```
What goes wrong: the stubs the feature depends on are hidden in a helper, so the reader cannot see why the result holds.

**Good** (neutral)
```groovy
    def "should remind only the invoice that is overdue on the clock's date"() {
        given: "two open invoices, one due yesterday and one due tomorrow, and a clock fixed on the day"
        def overdueReminder = new OverdueReminder(
            invoiceRepository, emailSender, Clock.fixed(Instant.parse("2026-11-01T09:00:00Z"), ZoneOffset.UTC))
        invoiceRepository.findOpen() >> [dueYesterday, dueTomorrow]

        when: "the morning reminder run starts"
        overdueReminder.run()

        then: "a reminder before the due date tells a customer they are late when they are not"
        1 * emailSender.sendReminder(dueYesterday)
        0 * emailSender.sendReminder(dueTomorrow)
    }
```
Why: every stub, count and the fixed clock the feature relies on is visible in its own given: and then: blocks.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/ConversationAnalyticsWindowSpec.groovy:47-49,85-89` @master 2026-10-02 (Bad, real) · `aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/ConversationAnalyticsAdapterSpec.groovy:63-76` (Good, adapted) · source research/31b-v2.md:918 · fix from research/31b-v2.md:920-935

### K11 — Variables an interaction uses are set before when:, never in when:

**Bad** (neutral)
```groovy
        when: "the customer places a draft order"
        def placed = orderService.place(draftOrderId)

        then: "the confirmation names the order just placed"
        1 * emailSender.sendConfirmation({ it.id == placed.id })
```
What goes wrong: Spock moves then: interactions before when:, so placed is not set yet when the interaction is set up.

**Good** (neutral)
```groovy
    def "should send one confirmation for the order just placed"() {
        given: "a place to capture the order the confirmation is about"
        Order confirmed = null

        when: "the customer places a draft order"
        def placed = orderService.place(draftOrderId)

        then: "the email sender receives one confirmation, for this order"
        1 * emailSender.sendConfirmation({ it.id == draftOrderId }) >> { Order o -> confirmed = o }

        and: "the email shows the placed order, not the draft"
        confirmed.status == OrderStatus.PLACED
        confirmed == placed
    }
```
Why: the interaction reads only values that exist before when:; the when: result is read in plain conditions.

Evidence: none on master (Bad, adapted from Spock interaction_based_testing.adoc:402-425) · `aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:43-66` @master 2026-10-02 (Good, adapted) · source research/31b-v2.md:953 · fix from research/31b-v2.md:955-972

### K12 — Several fields of one result: verifyAll(obj){…}, never Groovy .with{}

**Bad** (neutral)
```groovy
    def "should bill a placed order in euro, due 30 days after it was placed"() {
        expect: "the invoice for a two-line order placed on 1 November"
        invoiceService.invoiceFor(placedOrder).with {
            orderId == placedOrder.id && total == eur("42.00") && dueDate == LocalDate.parse("2026-12-01")
        }
    }
```
What goes wrong: Groovy .with{} returns one chained boolean, so a failure shows one opaque condition instead of the wrong field.

**Good** (neutral)
```groovy
    def "should bill a placed order in euro, due 30 days after it was placed"() {
        when: "a two-line order placed on 1 November is invoiced"
        def invoice = invoiceService.invoiceFor(placedOrder)

        then: "every wrong field is reported, not only the first"
        verifyAll(invoice) {
            orderId == placedOrder.id
            total == eur("42.00")
            dueDate == LocalDate.parse("2026-12-01")
        }
    }
```
Why: verifyAll asserts each line on its own and reports every field that is wrong.

Evidence: `aruvii-shared/src/test/groovy/ai/aruvii/shared/llm/TokenUsageSpec.groovy:29-34` @master 2026-10-02 (Bad, real) · `aruvii-infra/src/test/groovy/ai/aruvii/infra/adapter/AgentDailyStatsAdapterSpec.groovy:56-70` (Good, adapted) · source research/31b-v2.md:984 · fix from research/31b-v2.md:1013 ("verifyAll(new TokenUsage(…)) { … } per field")

### K13 — Assert call order only when order is the contract, with consecutive then: blocks

**Bad** (neutral)
```groovy
        then: "the gateway is charged before the invoice is marked paid"
        1 * paymentGateway.charge(invoiceId, amount) >> payment

        and: "the invoice is marked paid"
        1 * invoiceRepository.markPaid(invoiceId, payment.id) >> true
```
What goes wrong: and: imposes no order, so production code that marks the invoice paid first still passes.

**Good** (neutral)
```groovy
    def "should charge the gateway before the invoice is marked paid"() {
        when: "the customer pays an open invoice"
        invoiceService.pay(invoiceId)

        then: """the order is the contract: an invoice marked paid before a declined charge
                 shows a debt as settled."""
        1 * paymentGateway.charge(invoiceId, amount) >> payment

        then: "only then is the invoice marked paid, with that payment"
        1 * invoiceRepository.markPaid(invoiceId, payment.id) >> true
    }
```
Why: two consecutive then: blocks make Spock fail when the second call comes before the first.

Evidence: none on master (Bad, adapted from Spock interaction_based_testing.adoc:513-536) · `aruvii-worker/src/test/groovy/ai/aruvii/worker/chat/TurnRunnerFinalizeSpec.groovy:159-169` @master 2026-10-02 (Good, adapted) · source research/31b-v2.md:1017 · fix from research/31b-v2.md:1019-1031

### K14 — Isolate a spec that touches global state with @spock.lang.Isolated

**Bad** (neutral)
```groovy
class OrderServiceSpec extends Specification {
    ...
    def setup() {
        logger = LoggerFactory.getLogger(OrderService) as Logger
        appender = new ListAppender<>()
        appender.start()
        logger.addAppender(appender)
        logger.level = Level.DEBUG
    }
```
What goes wrong: the spec changes a process-wide logger with no isolation, so it breaks other specs once Spock runs in parallel.

**Good** (neutral)
```groovy
@spock.lang.Isolated("attaches an appender to OrderService's logback logger and changes its level")
class OrderServiceSpec extends Specification {
    ...
    def setup() {
        logger = LoggerFactory.getLogger(OrderService) as Logger
        appender = new ListAppender<>()
        appender.start()
        logger.addAppender(appender)
        logger.level = Level.DEBUG
    }
```
Why: Spock honours its own Isolated annotation; the Jupiter isolation annotations and parallel settings are ignored by Spock.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:36,51-57` @master 2026-10-02 (Bad, real, latent) · none (Good, adapted from Spock parallel_execution docs) · source research/31b-v2.md:1044 · fix from research/31b-v2.md:1046-1050

### K15 — Spring-context specs use the shared fake ports; no per-class override of an owned port

**Bad** (neutral)
```java
class InvoiceApiIT extends AbstractIT {
    ...
    @TestBean
    EmailSender emailSender;

    static EmailSender emailSender() {
        return new FakeEmailSender();
    }
```
What goes wrong: the class overrides a port the shared OutboundFakesConfig already fakes, so it forks its own uncached Spring context.

**Good** (neutral)
```groovy
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
@Import(OutboundFakesConfig)
class InvoiceApiIT extends Specification {

    @Autowired
    FakeEmailSender emailSender
```
Why: the shared config supplies the fake, so every IT with this setup reuses one cached context.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/security/SecurityIT.java:37,57-62` @772736bf (Bad, real) · `SecurityIT.java:37-62` (Good, rewritten; `ApiKeyPrivilegeContainmentIT.groovy:37-40` was the old real Good) · source research/31b-v2.md:1067 · fix from research/47-good-rewrites.md:503

### K16 — cleanup: frees per-feature resources defensively

**Bad** (neutral)
```groovy
    def cleanup() {
        logger.detachAppender(appender)
    }
```
What goes wrong: if setup() failed before logger was set, cleanup throws and hides the real failure; the DEBUG level is never restored.

**Good** (neutral)
```groovy
@spock.lang.Isolated("attaches an appender to OrderService's logback logger and changes its level")
class OrderServiceSpec extends Specification {
    ...
    def setup() {
        logger = LoggerFactory.getLogger(OrderService) as Logger
        previousLevel = logger.level
        appender = new ListAppender<ILoggingEvent>().tap { start() }
        logger.addAppender(appender)
        logger.level = Level.DEBUG
    }

    def cleanup() {
        logger?.detachAppender(appender)
        logger?.setLevel(previousLevel)
    }
```
Why: null-safe calls survive a failed setup(), and the process-wide logger gets its old level back.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:59-61` @772736bf (Bad, real) · `SessionServiceSpec.groovy:36,51-61` (Good, rewritten) · source research/31b-v2.md:1086 · fix from research/47-good-rewrites.md:537

### K17 — Never spy the class under test; double its outbound port instead

**Bad** (neutral)
```java
    @Test
    @DisplayName("quote never charges the customer or sends a receipt — AC-4")
    void shouldQuoteWithoutCharging() {
        // given
        final var spy = spy(orderService);

        // when
        spy.quote(orderId);

        // then
        verify(spy, never()).chargeFor(orderId);
        verify(spy, never()).sendReceipt(orderId);
    }
```
What goes wrong: the subject is partly faked and checks its own methods, so the test pins how OrderService is split, not what it does.

**Good** (neutral)
```groovy
    PaymentGateway paymentGateway = Mock()
    EmailSender emailSender = Mock()

    @Issue(["#123", "AC-4"])
    def "should quote an order total without charging the customer"() {
        given: "a draft order the service can find"
        orderRepository.findById(orderId) >> Optional.of(draftOrder)

        when: "the customer asks for a quote on the orders page"
        orderService.quote(orderId)

        then: "a quote that charges or sends a receipt bills a customer who only asked"
        0 * paymentGateway.charge(*_)
        0 * emailSender.sendReceipt(*_)
    }
```
Why: OrderService runs for real; the doubles sit at its outbound ports, which is where a charge or a receipt would leave.

Evidence: `aruvii-api/src/test/java/ai/aruvii/api/service/SetupServiceTest.java:357-369` @772736bf (Bad, real) · same lines (Good, rewritten; old real Good was `TurnRunnerFinalizeSpec.groovy:23-27`) · source research/31b-v2.md:1107 · fix from research/47-good-rewrites.md:567

### K18 — Records and value objects are constructed, never doubled

**Bad** (neutral)
```groovy
        given: "the customer who owns the order"
        def owner = Spy(Customer)
        owner.getId() >> UUID.randomUUID()
```
What goes wrong: a plain data holder is doubled to fake one getter, so its equals, hashCode and toString can lie.

**Good** (neutral)
```groovy
    def owner = customer()
    def stranger = customer()
    ...
    private Customer customer() {
        new Customer(UUID.randomUUID(), "customer@example.com", CustomerTier.STANDARD)
    }
```
Why: a real Customer carries the one value the features read, and behaves like the production object.

Evidence: `aruvii-auth/src/test/groovy/ai/aruvii/auth/application/WorkspaceCallerRoleSpec.groovy:56-60` @772736bf (Bad, real) · `WorkspaceCallerRoleSpec.groovy:25-27,56-60` (Good, rewritten) · source research/31b-v2.md:1137 · fix from research/47-good-rewrites.md:607

### K19 — Bind the expected exception and assert what matters

**Bad** (neutral)
```groovy
        when: "the same order is invoiced a second time"
        insertInvoice(orderId)
        em.flush()

        then: "invoices allows one row per order, so a customer is never billed twice"
        thrown(Exception)
```
What goes wrong: any exception passes, including one that has nothing to do with the one-invoice-per-order key.

**Good** (neutral)
```groovy
    def "should refuse a second invoice for the same order"() {
        given: "an order that already has an invoice"
        insertInvoice(orderId)
        em.flush()

        when: "the same order is invoiced a second time"
        insertInvoice(orderId)
        em.flush()

        then: "one invoice per order is what stops a customer being billed twice"
        def e = thrown(ConstraintViolationException)
        e.constraintName == "invoices_order_id_key"
    }
```
Why: the bound exception is the specific type, and its constraint name proves the key, not some other failure, refused the row.

Evidence: `aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:68-73` @master 2026-10-02 (Bad, real) · `aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:68-78` (Good, adapted, different feature) · source research/31b-v2.md:1158 · fix from research/31b-v2.md:1186 ("bind ConstraintViolationException and check agent_tool_links_pkey")

### K20 — A block description says the scenario and the why, never the code

**Bad** (neutral)
```groovy
        when: "it is stored"
        invoiceRepository.save(invoice)
```
What goes wrong: the label repeats the method call, so it adds no fact the code does not already show.

**Good** (neutral)
```groovy
    def "should keep the due date of an invoice stored late in the evening"() {
        when: "the invoice for an order placed at 23:30 Berlin time is stored and read back"
        invoiceRepository.save(invoice)
        def stored = invoiceRepository.findById(invoice.id).orElseThrow()

        then: "a due date shifted by the UTC offset would mark the invoice overdue a day early"
        stored.dueDate == invoice.dueDate
    }
```
Why: the when: text names the scenario and the then: text says why the date matters, which the code cannot say.

Evidence: `aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/AgentEvalRepositoryAdapterSpec.groovy:120-121` @master 2026-10-02 (Bad, real) · `aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:50-60` (Good, adapted) · source research/31b-v2.md:1190 · fix from research/31b-v2.md:1192-1205
