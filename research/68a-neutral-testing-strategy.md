# 68a — Neutral Good/Bad pairs: strategy · coverage-design · boundaries · value-bar (#99, map #9)

Source: research/31a-v2.md; research/47-good-rewrites.md (replaces the pair for S2, S3, C1, C4, B2, B3, V1, V3). Domain: ordering + billing (#99 brief). Stand-ins: `make test-module MOD=<m> TEST=<p>` → `./gradlew :<m>:test --tests '<p>'` (S3) · real-LLM opt-in tier (local Ollama, `-Dollama.it=true`) → PaymentGateway sandbox, `-Dgateway.sandbox=true`; exact model wording → gateway `receiptText` (TM3) · scripted fake LLM provider turns → PaymentGateway HTTP API stubbed at the wire with a WireMock scenario; third-party HTTP tool → fraud-check HTTP service (TM2) · Redis-backed store behind Toxiproxy → PaymentGateway HTTP behind Toxiproxy, `gatewayProxy` supplied by the shared container initializer (`@EnableSharedContainers`, IT2) (TM4) · provider startup check that never gets an answer → OverdueReminder job against a mail HTTP endpoint behind EmailSender (C2) · tool-output injection REQ scenario → order-cancellation AC on `/api/orders` (AT1) · stream consumer-group identity bug → same bug on stream `orders.placed`, groups of the billing and notifications modules (S4, V4) · entity version default tied to a migration → OrderEntity status default tied to migration V12 (C1, V5) · alert trigger enum → OrderStatus (V1, V3) · legacy exit-status strings → ErrorCode problem types (V2) · forwarded-header parser → OrderImportParser (B2, B3) · redaction offsets → payment allocation across invoices (B1) · Unicode NFC normaliser → CustomerEmail.normalise (C3). Added terms: OrderEntity (JPA entity of Order) · migration V12 · OrdersRepositoryIT (repository-slice base class) · OrderStatus.REFUNDED (new constant, V1 Bad only) · OrderImportParser (CSV of order lines) · PaymentAllocator · CustomerEmail.normalise · FakeInvoiceRepository + Resettable (own-code fake, TM2 Bad only) · BillingConsumer / NotificationsConsumer (consumers of `orders.placed`) · ErrorCode.problemType() + PUBLISHED_PROBLEM_TYPES · OrderCancellationHarness (AT1 Bad only) · gateway `receiptText`.
Skipped: none.

### S1 — Pick the tier by dependency; never start Spring to test plain service logic

**Bad** (neutral)
```java
@ExtendWith(SpringExtension.class)
@ContextConfiguration(classes = OrderTotalTest.TestConfig.class)
class OrderTotalTest {

    static final String CUSTOMER_EMAIL = "ann@example.com";

    @TestConfiguration
    static class TestConfig {

        @Bean OrderRepository orderRepository() { return mock(OrderRepository.class); }

        @Bean TaxCalculator taxCalculator() { return mock(TaxCalculator.class); }

        @Bean EmailSender emailSender() { return mock(EmailSender.class); }
```
What goes wrong: a Spring context whose every bean is a mock wires plain logic, crosses no boundary, and only makes the test slow.

**Good** (neutral)
```groovy
    OrderRepository orderRepository = Stub()
    PaymentGateway paymentGateway = Stub()
    OrderService service

    def setup() {
        service = new OrderService(
            orderRepository,
            paymentGateway,
            new FakeEmailSender(),
            new TaxCalculator(),
            Clock.fixed(NOW, ZoneOffset.UTC))
    }
```
Why: the service is built with `new`, only outbound ports are doubled, our own TaxCalculator is real, and the clock is fixed.

Evidence: `aruvii-worker/src/test/java/ai/aruvii/worker/chat/HistoryCompressionTest.java:45-56` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:8 · fix from 31a-v2.md:10-26

### S2 — Assert observable behaviour, never a field default or the input passed in

**Bad** (neutral)
```groovy
    def "the order line variants carry what they are given"() {
        given: "a unit price"
        def price = new Money(new BigDecimal("9.99"), "EUR")

        expect: "the quantity and price are present, and the status is named"
        new OrderLine("SKU-1", 2, price).quantity() == 2
        new OrderLine("SKU-1", 2, price).unitPrice() == price
        new Order(orderId, customerId, [], status, null).status() == status

        where:
        status << OrderStatus.values().toList()
    }
```
What goes wrong: every line reads back the constructor argument, so it passes for any record and fails for no regression.

**Good** (neutral)
```groovy
    def "should refuse an order line with quantity #quantity, because a line orders at least one item"() {
        given: "the unit price a line would carry"
        def price = new Money(new BigDecimal("9.99"), "EUR")

        when: "a line names that quantity"
        new OrderLine("SKU-1", quantity, price)

        then: "the line type refuses it, so no invoice can bill an item nobody ordered"
        def e = thrown(IllegalArgumentException)
        e.message == "A quantity starts at 1, but was $quantity"

        where:
        quantity << [0, -1]
    }
```
Why: it asserts what OrderLine does with a bad quantity, not what the test handed in, so a missing guard fails it.

Evidence: `aruvii-agents/src/test/groovy/ai/aruvii/agents/domain/RunModeSpec.groovy:49-60` @772736bf (Bad, real) · source 31a-v2.md:46 · fix from research/47-good-rewrites.md:36-54

### S3 — Before changing code, run the existing tests touching it; note what was green

**Bad** (neutral)
```text
./mvnw -pl orders-api -am -Dtest='InvoiceServiceTest+OrderServiceTest' ... test
→ [INFO] BUILD SUCCESS
→ zero tests executed
```
What goes wrong: a hand-rolled baseline run whose filter matched nothing; nothing ran, yet "green" was noted before editing.

**Good** (neutral)
```text
./gradlew :orders-api:test --tests '*InvoiceServiceTest*'
./gradlew :orders-api:test --tests '*OrderServiceTest*'

Baseline before editing InvoiceService, at main <sha>:
  InvoiceServiceTest   <n> tests, 0 failed
  OrderServiceTest     <n> tests, 0 failed
```
Why: it goes through the build's own test task, one pattern per run so an empty match fails, and the note records counts proving tests ran.

Evidence: `.claude/skills/aruvii-standards/references/verification.md:27-31` @772736bf (Bad, real) · source 31a-v2.md:81 (31a's own Bad, adapted, was replaced by 47's pair) · fix from research/47-good-rewrites.md:66-75

### S4 — A bug fix starts with a test failing for the bug's reason, landed before the fix

**Bad** (n/a) — a squash-merged main shows one commit per MR, so test-before-fix order is invisible there; no "fix with no test" exists to cite.

**Good** (neutral)
```groovy
    @Issue("#123")
    def "should register the injected identity on #group"() {
        given: "an entry for the running consumer to read — its loop registers it on that read"
        ensureGroup("orders.placed", group)
        redis.opsForStream().add(StreamRecords.mapBacked(["orderId": "42"]).withStreamKey("orders.placed"))

        when: "the consumer the service started has read at least once"
        def names = awaitConsumerNames("orders.placed", group)

        then: "the group holds this process's identity"
        names.contains(consumerIdentity.name())

        and: "and never the literal every consumer used to share"
        !names.contains("consumer-1")
```
Why: bug #123 (every consumer shared `consumer-1`) makes this fail on the old code for exactly the bug's reason, read from Redis.

Evidence: `none` (Bad, n/a — master squash-merged; 12 sampled fix commits all carry tests) · source 31a-v2.md:105 · fix from 31a-v2.md:107-124

### S5 — Do not pick a tier because the case is an error path; pick by what fails

**Bad** (neutral)
```groovy
    def "a quantity outside the allowed range is refused"() {
        when: "a quantity the database would not accept is added"
        orderService.addLine(orderId, "SKU-1", quantity)

        then: "the service guard fires before the CHECK constraint does, with a readable message"
        thrown(IllegalArgumentException)

        and: "and nothing is written"
        orderService.lineCount(orderId) == 0L

        where:
        quantity << [0, -1, 100]
    }
```
What goes wrong: a pure `if` guard boots Postgres in an IT; the CHECK constraint it names is never reached, so no boundary is added.

**Good** (neutral)
```groovy
    def "should refuse quantity #quantity before anything is written"() {
        when: "a quantity the column would reject is added"
        service.addLine(orderId, "SKU-1", quantity)

        then: "the guard fires first, so the clerk gets a sentence rather than a constraint violation"
        def e = thrown(IllegalArgumentException)
        e.message.contains("quantity must be")

        and: "and the repository is never even reached"
        0 * orderRepository._

        where:
        quantity << [0, -1, 100, Integer.MIN_VALUE]
    }
```
Why: the error comes from pure logic, so it is a unit spec; `0 *` is the behaviour here because nothing may be reached.

Evidence: `aruvii-chat/src/integrationTest/groovy/ai/aruvii/chat/FeedbackServiceIT.groovy:62-74` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:128 · fix from 31a-v2.md:130-148

### TM1 — At a boundary the IT is primary; unit specs only cover what the IT cannot cheaply reach

**Bad** (neutral)
```groovy
    def "the status filter is passed through as given, null included"() {
        when: "invoices are listed with and without a filter"
        service.listByCustomer(customerId, InvoiceStatus.OPEN, 0, 25)
        service.listByCustomer(customerId, null, 0, 10)

        then: "substituting a default for null would silently filter an unfiltered list"
        1 * invoiceRepository.findByCustomerId(customerId, InvoiceStatus.OPEN, 0, 25) >> []
        1 * invoiceRepository.findByCustomerId(customerId, null, 0, 10) >> []
    }
```
What goes wrong: it re-proves through a mock what the IT already proves on real rows; the SQL that does the filtering never runs.

**Good** (neutral)
```groovy
    def "should list only the requested status, and every invoice when no filter is given"() {
        given: "three invoices for one customer, two open and one paid"
        insertInvoice(customerId, InvoiceStatus.OPEN)
        insertInvoice(customerId, InvoiceStatus.OPEN)
        insertInvoice(customerId, InvoiceStatus.PAID)

        expect: "a filter that ignored the status would report every invoice as open"
        invoiceService.listByCustomer(customerId, InvoiceStatus.OPEN, 0, 10).size() == 2
        invoiceService.listByCustomer(customerId, InvoiceStatus.PAID, 0, 10).size() == 1
        invoiceService.listByCustomer(customerId, null, 0, 10).size() == 3
    }
```
Why: the filter lives in the SQL, so the IT against real Postgres is the primary proof, with `null` meaning unfiltered.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/application/FeedbackServiceSpec.groovy:99-107` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:169 · fix from 31a-v2.md:171-187

### TM2 — In ITs/smoke replace only what we don't own; fake third-party HTTP at the wire

**Bad** (neutral)
```java
public class FakeInvoiceRepository implements InvoiceRepository, Resettable {

    private final Map<UUID, Invoice> invoices = new HashMap<>();

    /** Programs the invoice the repository returns for one id. */
    public void put(final Invoice invoice) {
        invoices.put(invoice.id(), invoice);
    }

    @Override
    public Optional<Invoice> findById(final UUID id) {
        return Optional.ofNullable(invoices.get(id));
    }
```
What goes wrong: an IT fakes our own repository, which our database backs, so its real query is never exercised.

**Good** (neutral)
```groovy
    private void stubFraudCheck(String body) {
        wireMock.resetAll()
        wireMock.stubFor(get(urlEqualTo("/fraud-check")).willReturn(okJson(body)))
    }

    /** Call 1 leaves the charge pending, call 2 captures it; the WireMock scenario carries the call. */
    private void stubGatewayCapturesOnRetry() {
        wireMock.stubFor(post(urlEqualTo(CHARGES))
            .inScenario("charge").whenScenarioStateIs(Scenario.STARTED)
            .willSetStateTo("pending")
            .willReturn(okJson(PENDING)))
        wireMock.stubFor(post(urlEqualTo(CHARGES))
            .inScenario("charge").whenScenarioStateIs("pending")
            .willReturn(okJson(CAPTURED)))
    }
```
Why: only the payment gateway and the fraud-check service are faked, at the wire; our services, repositories and Postgres run for real.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakeActiveSessionCountPort.java:17-29` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:204 · fix from 31a-v2.md:206-224

### TM3 — Opt-in tier against a real external service, structural assertions only, never in the gate

**Bad** (neutral)
```groovy
    def "should pay an open invoice"() {
        given: "an open invoice on the gateway sandbox — no @Requires, so it runs inside ./gradlew check"
        def customerId = seedCustomer("sandbox-pay", CustomerTier.STANDARD)
        def invoiceId = seedInvoice(customerId, new Money(new BigDecimal("25.50"), "EUR"))
        def events = subscribePayments(invoiceId)

        when: "the clerk pays it"
        invoiceService.pay(invoiceId)
        await().atMost(Duration.ofSeconds(60)).until { events.completed() }

        then: "the gateway's receipt is word-for-word what we expect"
        events.firstPayment().receiptText() == "Approved: 25.50 EUR charged to card ending 4242."
    }
```
What goes wrong: it calls a real external service inside the gate and asserts wording the service is free to change.

**Good** (neutral)
```groovy
    @Requires({ sys["gateway.sandbox"] == "true" })
    def "should record a payment for an open invoice against the gateway sandbox"() {
        given: "an open invoice of 25.50 EUR for a fresh customer"
        def customerId = seedCustomer("sandbox-pay", CustomerTier.STANDARD)
        def invoiceId = seedInvoice(customerId, new Money(new BigDecimal("25.50"), "EUR"))
        def events = subscribePayments(invoiceId)

        when: "the clerk pays it and the gateway answers"
        invoiceService.pay(invoiceId)
        await().atMost(Duration.ofSeconds(60)).until { events.paymentCount() >= 1 }

        then: "a payment of the amount we sent was recorded — never the gateway's own wording"
        events.firstPayment().amount() == new Money(new BigDecimal("25.50"), "EUR")
        invoiceRepository.findById(invoiceId).get().status() == InvoiceStatus.PAID
    }
```
Why: it runs only on request, outside the gate, and asserts the shape of the outcome, not the external service's text.

Evidence: `aruvii-worker/src/integrationTest/java/ai/aruvii/worker/chat/AllToolTypesIT.java:694-712` @origin/master 2026-10-02, no sha in source (Bad, adapted — no real exact-wording Bad found) · source 31a-v2.md:245 · fix from 31a-v2.md:247-265

### TM4 — One Toxiproxy IT per survived dependency: latency, timeout, cut, recovery

**Bad** (n/a) — no fault-injection IT exists, so there is nothing to cite.

**Good** (neutral)
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
Why: the real gateway sits behind a proxy; it asserts predictable failure, the WARN line, and recovery once the fault clears.

Evidence: `none` (Bad, n/a — `git grep -i toxiproxy` empty on master) · source 31a-v2.md:285 · fix from 31a-v2.md:287-305

### C2 — Test every external dependency's unavailable case: predictable failure, WARN/ERROR, no hang

**Bad** (neutral)
```groovy
    def "reminder sends and tolerates an outage"() {
        when: "the overdue reminder runs"
        reminder.run()

        then: "the mail service is unreachable"
        1 * emailSender.send(_) >> { throw new RuntimeException("connection refused") }

        and:
        noExceptionThrown()
    }
```
What goes wrong: it proves only silence; no WARN is asserted, so code that swallows the outage without a log still passes.

**Good** (neutral)
```groovy
    def "should warn the mail service unreachable, within a bound, when it never answers"() {
        given: "an overdue invoice, behind a mail endpoint that holds every request for 15 s"
        wireMock.stubFor(post(urlEqualTo("/send")).willReturn(okJson("{}").withFixedDelay(15_000)))
        def invoiceId = seedOverdueInvoice(customerId)

        when: "the reminder job runs"
        def start = System.currentTimeMillis()
        overdueReminder.run()
        def elapsedMs = System.currentTimeMillis() - start

        then: "it gave up before the endpoint would have answered, and named the invoice at WARN"
        elapsedMs < 14_000L
        def line = appender.list.find { it.formattedMessage.contains("status=unreachable invoiceId=$invoiceId") }
        line?.level == Level.WARN
    }
```
Why: the dependency never answers; the test asserts a bounded time, the logged outcome, and its WARN level.

Evidence: `aruvii-infra/src/test/groovy/ai/aruvii/infra/adapter/RedisModelOverrideStoreAdapterSpec.groovy:125-134` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:309 · fix from 31a-v2.md:311-329

### AT1 — No separate acceptance tier; an AC is proven by an IT (API) or a smoke spec (UI)

**Bad** (neutral)
```java
/**
 * Acceptance harness for {@code features/order-cancellation.feature}.
 *
 * <p>The acceptance runtime is Node; the behaviour under test is a Java order service. This is the
 * adapter between them: one JSON command on argv, the observed values as JSON on stdout. It
 * drives the <em>real</em> {@link OrderService} and the real {@link InvoiceService} — only the
 * edges they talk to (payment gateway, email sender, repositories) are faked, so nothing about
 * the cancellation rule under test is reimplemented here.
 *
 * <pre>
 *   java -cp … OrderCancellationHarness '{"order":"PLACED","invoice":"PAID"}'
 * </pre>
 */
public final class OrderCancellationHarness {
```
What goes wrong: a separate `.feature` tier with its own Node runtime duplicates an IT and is left orphaned when the feature file goes.

**Good** (neutral)
```groovy
    @Issue(["#123", "AC-1"])
    def "should refuse to cancel an order whose invoice is already paid"() {
        given: "a placed order whose invoice the customer has paid"
        def orderId = seedOrder(customerId, OrderStatus.PLACED)
        payInvoiceOf(orderId)

        when: "the customer cancels it through the API"
        def response = client.post().uri("/api/orders/{id}/cancel", orderId).exchange()

        then: "the API refuses with the problem type, and the order is not cancelled"
        response.expectStatus().isEqualTo(409)
        response.expectBody().jsonPath('$.type').isEqualTo("https://example.com/errors/INVOICE_ALREADY_PAID")
        orderRepository.findById(orderId).get().status() == OrderStatus.PAID
    }
```
Why: the AC of issue #123 is an ordinary IT on the real API; its name reads as the scenario.

Evidence: `aruvii-worker/src/test/java/ai/aruvii/worker/acceptance/ToolOutputSplitHarness.java:92-106` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:347 · fix from 31a-v2.md:349-367

### C1 — Decide cases with RIGHT-BICEP before writing; skip a dimension only with a reason

**Bad** (neutral)
```groovy
    def "a new order entity starts as a draft"() {
        expect: "Hibernate writes the field on every INSERT, so a default of PLACED would override V12's column default"
        new OrderEntity().status == OrderStatus.DRAFT
    }
```
What goes wrong: one Right case, and nothing shows which other dimensions were considered or why they were skipped.

**Good** (neutral)
```groovy
/**
 * #123 AC-2: an order created through the app starts as a draft.
 * R: a saved new order reads back DRAFT. B: DRAFT is the first status — nothing comes before it.
 * I, C, E, P: skip — no inverse operation, no second source, no error path, one INSERT.
 */
class OrderEntityStatusIT extends OrdersRepositoryIT {

    @Issue(["#123", "AC-2"])
    def "should store a newly created order as a draft"() {
        given: "an order built the way the app builds one, its status never set"
        def id = em.persistFlushFind(newOrder()).id
        em.clear()

        expect: "Hibernate writes the field on every INSERT, so the stored row holds the entity's value"
        em.find(OrderEntity, id).status == OrderStatus.DRAFT
```
Why: every RIGHT-BICEP letter is decided in the header, and the case reads the stored row instead of a field default.

Evidence: `aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/entity/AgentEntityVersionSpec.groovy:8-11` @772736bf (Bad, real) · source 31a-v2.md:389 · fix from research/47-good-rewrites.md:88-106

### C3 — Expected value written out, worked independently, never computed by the code under test

**Bad** (neutral)
```java
    @Test
    void emailNormalisation_ignoresCase() {
        // upper-case domain vs lower-case domain
        String typed = "Ann@Example.COM";   // as typed
        String stored = "ann@example.com";  // as stored
        assertThat(CustomerEmail.normalise(typed)).isEqualTo(CustomerEmail.normalise(stored));
    }
```
What goes wrong: both sides come from `normalise`, so a `normalise` that returns an empty string for every input still passes.

**Good** (neutral)
```groovy
    def "should store an email typed in mixed case in lower case"() {
        expect: "the stored form is written out by hand, never produced by normalise itself"
        CustomerEmail.normalise("Ann@Example.COM") == "ann@example.com"
    }
```
Why: the expected value is a literal worked out by hand, so a broken `normalise` cannot also produce it.

Evidence: `aruvii-guardrails/src/test/java/ai/aruvii/guardrails/pii/InputNormaliserTest.java:57-63` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:420 · fix from 31a-v2.md:422-436 (literal expected value) and 31a-v2.md:448 ("expected should be the literal")

### C4 — A knowingly untested case is one gap row in the MR description, never unsaid

**Bad** (neutral)
```markdown
## Verification

`./gradlew check`: 412 tests passed, smoke 88 passed / 0 failed / 0 skipped.

Each of the new assertions was mutation-tested rather than assumed: removing the
paid-invoice guard and letting a SHIPPED order cancel each turn the expected case red.
```
What goes wrong: it lists what ran and nothing about what was not tested, so a decided gap looks like an oversight.

**Good** (neutral)
```markdown
## Verification

`./gradlew check`: 412 tests passed, smoke 88 passed / 0 failed / 0 skipped.

## Not tested, by decision

| dimension | missing | risk |
|---|---|---|
| E — error | the cancellation email while `EmailSender` is down | the customer is not told the order was cancelled |
| B — boundary | cancelling a DRAFT order with no lines | an empty cancellation email is sent |
```
Why: each knowingly untested case is one `dimension · missing · risk` row, so a reviewer can tell a decision from an oversight.

Evidence: `git log -1 527ae415` body lines 68-75 @772736bf (Bad, real) · source 31a-v2.md:452 (31a's own Bad, adapted, was replaced by 47's pair) · fix from research/47-good-rewrites.md:123-137

### B1 — Check CORRECT boundaries for each input: Conformance, Ordering, Range, Reference, Existence, Cardinality, Time

**Bad** (neutral)
```groovy
    def "should record the invoice's paid amount"() {
        when: "a payment of 30.00 EUR is allocated to one open invoice of 20.00 EUR"
        def paid = allocator.allocate(payment("30.00"), invoicesDue([5]))

        then: "the invoice is paid in full"
        paid*.amount() == [eur("20.00")]
    }
```
What goes wrong: Cardinality 1 only; with one invoice the remainder always starts full, so oldest-first and newest-first both pass.

**Good** (neutral)
```groovy
    def "should pay the oldest invoices first when a payment covers #scenario"() {
        when: "a payment of 30.00 EUR is allocated across open invoices of 20.00 EUR each"
        def paid = allocator.allocate(payment("30.00"), invoicesDue(dueInDays))

        then: "each invoice gets what remains after the ones due sooner"
        paid*.amount() == expected.collect { eur(it) }

        where:
        scenario                 | dueInDays || expected
        "no invoice"             | []        || []
        "one invoice"            | [5]       || ["20.00"]
        "two, sooner one last"   | [9, 2]    || ["10.00", "20.00"]
        "three, the last unpaid" | [1, 2, 3] || ["20.00", "10.00", "0.00"]
    }
```
Why: Cardinality 0, 1 and many, with Ordering reversed in one row, so a wrong allocation order fails.

Evidence: `aruvii-guardrails/src/test/groovy/ai/aruvii/guardrails/infrastructure/CustomPiiResponseSpec.groovy:11-13` @origin/master 2026-10-02, no sha in source (Bad, adapted — the file's own doc names this trap) · source 31a-v2.md:470 · fix from 31a-v2.md:472-489 (one row per broken edge; Cardinality 1/2/3 in the same file)

### B2 — Logic taking number/collection/format/enum/time/optional gets ≥1 case per CORRECT letter or a skip line

**Bad** (neutral)
```java
    void parse_valid_import_returns_lines() {
    void parse_null_returns_empty() {
    void parse_blank_returns_empty() {
    void parse_invalid_sku_throws() {
    void parse_non_numeric_quantity_throws() {
    void parse_exceeds_max_lines_throws() {
    void parse_quantity_exceeding_99_throws() {
    void parse_total_exceeds_10000_eur_throws() {
    void parse_invalid_currency_code_throws(String currency) {
```
What goes wrong: Range is tried only from outside, Cardinality only past the limit, and no line says why Ordering, Reference and Time are skipped.

**Good** (neutral)
```groovy
/**
 * CORRECT for parse: Conformance (SKU pattern, numeric quantity, ISO currency) · Range (quantity 1..99,
 * total ≤ 10 000 EUR) · Existence (null, blank) · Cardinality (0, 1, 50 lines accepted; 51 refused).
 * skip: Ordering — no rule reads line order · Reference, Time — no lookup and no clock.
 */
class OrderImportParserSpec extends Specification {

    def "should keep every line of an import carrying #count of them"() {
        expect: "up to the limit, nothing is dropped"
        OrderImportParser.parse(importOf(count)).size() == count

        where:
        count << [0, 1, 50]
    }
```
Why: the header names every letter, covered or skipped with a reason; Cardinality runs 0, 1 and the edge 50.

Evidence: `aruvii-platform/src/test/java/ai/aruvii/platform/application/ForwardContextParserTest.java:17,26,31,36,43,51,65,75,92` @772736bf (Bad, real) · source 31a-v2.md:503 · fix from research/47-good-rewrites.md:155-172

### B3 — Range: test just inside and just outside the edge, not only the edge

**Bad** (neutral)
```java
    @Test
    void parse_quantity_exceeding_99_throws() {
        String header = "sku;quantity;unitPrice;currency";
        String row = "SKU-1;100;9.99;EUR";
        String csv  = header + "\n" + row;
        assertThatThrownBy(() -> OrderImportParser.parse(csv))
            .isInstanceOf(OrderException.class)
            .hasMessageContaining("99");
    }
```
What goes wrong: only 100 is tried; 99 is never shown to pass, so an off-by-one `>=` passes too.

**Good** (neutral)
```groovy
    def "should accept an import line with a quantity of exactly 99"() {
        expect: "the limit itself is inside the range"
        OrderImportParser.parse(importLine("SKU-1", 99)).first().quantity() == 99
    }

    def "should refuse an import line with a quantity of 100"() {
        when: "the quantity is one past the per-line limit"
        OrderImportParser.parse(importLine("SKU-1", 100))

        then: "the refusal names the limit it broke"
        def e = thrown(OrderException)
        e.message.contains("max 99 per line")
    }
```
Why: the edge (99, accepted) and one past it (100, refused) each get a case, so `>` versus `>=` is decided.

Evidence: `aruvii-platform/src/test/java/ai/aruvii/platform/application/ForwardContextParserTest.java:64-72` @772736bf (Bad, real) · source 31a-v2.md:532 · fix from research/47-good-rewrites.md:190-206

### V1 — Before adding a test answer: contract · realistic regression · why not covered · needs a fake seam?

**Bad** (neutral)
```groovy
    def "a refunded order has its own status"() {
        expect: "REFUNDED is named, and the existing five are unchanged"
        OrderStatus.valueOf("REFUNDED") != null
        ["DRAFT", "PLACED", "PAID", "SHIPPED", "CANCELLED"]
                .every { OrderStatus.valueOf(it) != null }
    }
```
What goes wrong: no realistic regression fails it; removing a constant breaks compilation first, and nothing sets REFUNDED yet.

**Good** (neutral)
```groovy
/**
 * Q1 contract: OrderRepository stores OrderStatus.name() on each order row and /api/orders
 *    returns it as status.
 * Q2 regression: a renamed constant strands stored rows and every client that filters on the old name.
 * Q3 not covered: no test names the stored strings; compilation only proves a constant exists.
 * Q4 seam: none; the enum is what the repository writes.
 * REFUNDED gets its test when the refund flow sets it (#123); today Q2 has no answer.
 */
class OrderStatusSpec extends Specification {

    def "should still emit every status that stored order rows carry"() {
        expect: "a rename fails here, not as an empty order filter after an upgrade"
        OrderStatus.values()*.name().containsAll(STORED_ORDER_STATUSES)
    }
```
Why: all four answers are written down, and the constant with no answer to Q2 gets no test yet.

Evidence: `aruvii-platform/src/test/groovy/ai/aruvii/platform/domain/AlertTriggerTypeSpec.groovy:8-13` @772736bf (Bad, real) · source 31a-v2.md:565 · fix from research/47-good-rewrites.md:221-238

### V2 — A test that breaks under a behaviour-preserving refactor asserts implementation; move it to the owner

**Bad** (neutral)
```groovy
    def "the error codes are the three the order API lists"() {
        expect: "no more and no fewer"
        ErrorCode.values()*.name() as Set == [
            'ORDER_NOT_FOUND',
            'INVOICE_ALREADY_PAID',
            'PAYMENT_DECLINED',
        ] as Set
    }
```
What goes wrong: it pins Java enum member names; renaming a member breaks it while every problem type a client sees stays the same.

**Good** (neutral)
```groovy
    def "should still produce every problem type clients already handle after the refactor"() {
        when: "the problem types the error codes produce are collected"
        def producible = ErrorCode.values()*.problemType() as Set

        then: "nothing a client already switches on has been lost"
        (PUBLISHED_PROBLEM_TYPES - producible).isEmpty()
    }
```
Why: it asserts the problem-type strings clients see, so a rename that keeps them passes and a lost one is named.

Evidence: `aruvii-worker/src/test/groovy/ai/aruvii/worker/chat/RefusalReasonSpec.groovy:44-51` @origin/master 2026-10-02, no sha in source (Bad, real) · source 31a-v2.md:589 · fix from 31a-v2.md:591-608

### V3 — Junk-pattern test fails the gate unless it names the contract it independently guards

**Bad** (neutral)
```groovy
        OrderStatus.valueOf("REFUNDED") != null
        ["DRAFT", "PLACED", "PAID", "SHIPPED", "CANCELLED"]
                .every { OrderStatus.valueOf(it) != null }
```
What goes wrong: junk pattern 3, a hand-copied list of enum members, with no stored or emitted form named as its contract.

**Good** (neutral)
```groovy
    /**
     * The statuses order rows already store and /api/orders returns, verbatim.
     * Hand-copied on purpose (junk pattern 3, contract named): never derive this list from the enum.
     */
    static final List<String> STORED_ORDER_STATUSES = [
        "DRAFT",
        "PLACED",
        "PAID",
        "SHIPPED",
        "CANCELLED",
    ]
```
Why: still pattern 3, but it names the storage and API contract it guards and says why it must not be derived.

Evidence: `aruvii-platform/src/test/groovy/ai/aruvii/platform/domain/AlertTriggerTypeSpec.groovy:10-12` @772736bf (Bad, real) · source 31a-v2.md:624 · fix from research/47-good-rewrites.md:250-263

### V4 — A bug gets ONE regression test at the owning boundary; don't replay it per layer

**Bad** (neutral)
```groovy
// BillingConsumerSpec — unit, StreamOperations mocked
    def "should not read as consumer-1"() {
        when: "the consumer polls once"
        consumer.poll()

        then: "the read names a consumer other than the old shared literal"
        1 * streamOps.read({ Consumer c -> c.name != "consumer-1" }, _, _)
    }
// …the same feature again in NotificationsConsumerSpec and a smoke spec
```
What goes wrong: the same bug is replayed at every consumer and layer; the mocked copies cannot see Redis merge two names.

**Good** (neutral)
```groovy
    @Issue("#123")
    def "should register the injected identity on #group"() {
        // given: / when: as in S4 Good
        then: "the group holds this process's identity"
        names.contains(consumerIdentity.name())

        and: "and never the literal every consumer used to share"
        !names.contains("consumer-1")

        where:
        group << [BillingConsumer.GROUP, NotificationsConsumer.GROUP]
    }
```
Why: the regression lives once, in Redis where the bug shows, with one row per consumer group.

Evidence: `none` (Bad, adapted from the #521 tests — no real replay found on master) · source 31a-v2.md:646 · fix from 31a-v2.md:648-665

### V5 — Keep a test that guards a contract, promised default, order, or real regression; prove junk before deleting

**Bad** (n/a) — no deletion of a contract-guarding test without proof was found; recent deletions were replacements that name their successor.

**Good** (neutral)
```groovy
/** #123 AC-2 — an order created through the app starts as a draft. */
class OrderEntityStatusSpec extends Specification {

    @Issue(["#123", "AC-2"])
    def "should start a new order entity as a draft"() {
        expect: "Hibernate writes it on every INSERT, so a default of PLACED would override V12's column default"
        new OrderEntity().status == OrderStatus.DRAFT
    }
}
```
Why: it looks like field-default junk but guards a promised default tied to migration V12, so it is kept.

Evidence: `none` (Bad, n/a — `git log --diff-filter=D` deletions are JUnit→Spock replacements) · source 31a-v2.md:681 · fix from 31a-v2.md:683-695
