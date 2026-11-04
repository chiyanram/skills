# Strategy — examples

Every approved Good/Bad pair for the rules in [`../strategy.md`](../strategy.md), one per rule id, in one neutral
domain (ordering and billing).

## S1 — Pick the tier by what the behaviour depends on

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
A Spring context whose every bean is a mock wires plain logic, crosses no boundary, and only makes the test slow.

**Good** (neutral)
```groovy
    OrderRepository orderRepository = Stub()
    FakePaymentGateway paymentGateway = new FakePaymentGateway()
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
The service is built with `new`, only outbound ports are replaced (the gateway by its fake), our own TaxCalculator is real, and the clock is fixed. (Real evidence: ledger row S1.)

## S2 — Assert observable behaviour

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
Every line reads back the constructor argument, so it passes for any record and fails for no regression.

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
It asserts what OrderLine does with a bad quantity, not what the test handed in, so a missing guard fails it. (Real evidence: ledger row S2.)

## TM1 — At a boundary the IT is the primary test

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
It re-proves through a mock what the IT already proves on real rows; the SQL that does the filtering never runs.

**Good** (neutral)
```groovy
    def "should list only the requested status, and every invoice when no filter is given"() {
        given: "three invoices for one customer, two open and one paid"
        insertInvoice(customerId, InvoiceStatus.OPEN)
        insertInvoice(customerId, InvoiceStatus.OPEN)
        insertInvoice(customerId, InvoiceStatus.PAID)

        when: "the invoices are listed by each status and with no filter"
        def open = invoiceService.listByCustomer(customerId, InvoiceStatus.OPEN, 0, 10)
        def paid = invoiceService.listByCustomer(customerId, InvoiceStatus.PAID, 0, 10)
        def all = invoiceService.listByCustomer(customerId, null, 0, 10)

        then: "a filter that ignored the status would report every invoice as open"
        open.size() == 2
        paid.size() == 1
        all.size() == 3
    }
```
The filter lives in the SQL, so the IT against real Postgres is the primary proof, with `null` meaning unfiltered. (Real evidence: ledger row TM1.)

## TM2 — Fake only what we do not own

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
An IT fakes our own repository, which our database backs, so its real query is never exercised.

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
Only the payment gateway and the fraud-check service are faked, at the wire; our services, repositories and Postgres run for real. (Real evidence: ledger row TM2.)

## TM3 — Real-model tier: opt-in, outside the gate

**Bad** (neutral)
```groovy
    def "should summarise a placed order"() {
        given: "a placed order of two lines — no @Requires, so the real model runs inside ./gradlew check"
        def orderId = seedOrder(customerId, [line("SKU-1", 2), line("SKU-2", 1)])

        when: "the real model writes the order summary"
        def summary = orderSummariser.summarise(orderId)

        then: "the summary has the structure we need"
        summary.orderId() == orderId
        summary.lineCount() == 2
    }
```
Its assertions are fine, but with no opt-in it calls a real model inside the gate, so every run is slow, paid and flaky.

**Good** (neutral)
```groovy
    @Requires({ sys["model.real"] == "true" })
    def "should summarise a placed order with the real model"() {
        given: "a placed order of two lines"
        def orderId = seedOrder(customerId, [line("SKU-1", 2), line("SKU-2", 1)])

        when: "the real model writes the order summary"
        def summary = orderSummariser.summarise(orderId)

        then: "the summary has the structure we need — never the model's own wording"
        summary.orderId() == orderId
        summary.lineCount() == 2
        !summary.text().isBlank()
    }
```
It runs only on request, outside the gate. How a live test asserts, structure and never wording, is LT15 in [`../llm-live-tests.md`](../llm-live-tests.md). (Real evidence: ledger row TM3.)

## AT1 — No separate acceptance tier

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
A separate `.feature` tier with its own Node runtime duplicates an IT and is left orphaned when the feature file goes.

**Good** (neutral)
```groovy
    @Issue(["#123", "AC-1"])
    def "should refuse to cancel an order whose invoice is already paid"() {
        given: "a placed order whose invoice the customer has paid"
        def orderId = seedOrder(customerId, OrderStatus.PLACED)
        payInvoiceOf(orderId)

        when: "the customer cancels it through the API"
        def response = client.post().uri("/api/orders/{id}/cancel", orderId)
            .header(HttpHeaders.AUTHORIZATION, login("CUSTOMER"))
            .exchange()

        then: "the API refuses with the problem type, and the order is not cancelled"
        response.expectStatus().isEqualTo(409)
        response.expectBody().jsonPath('$.type').isEqualTo("https://example.com/errors/INVOICE_ALREADY_PAID")
        orderRepository.findById(orderId).get().status() != OrderStatus.CANCELLED
    }
```
The AC of the order-cancellation story is an ordinary IT on the real API, called with a customer's token; its name reads as the scenario. (Real evidence: ledger row AT1.)

## S3 — Run the existing tests before changing code

**Bad** (neutral)
```text
./mvnw -pl orders-api -am -Dtest='InvoiceServiceTest+OrderServiceTest' ... test
→ [INFO] BUILD SUCCESS
→ zero tests executed
```
A hand-rolled baseline run whose filter matched nothing; nothing ran, yet "green" was noted before editing.

**Good** (neutral)
```text
./gradlew :orders-api:test --tests '*InvoiceServiceTest*'
./gradlew :orders-api:test --tests '*OrderServiceTest*'

Baseline before editing InvoiceService, at main <sha>:
  InvoiceServiceTest   <n> tests, 0 failed
  OrderServiceTest     <n> tests, 0 failed
```
It goes through the build's own test task, one pattern per run so an empty match fails, and the note records counts proving tests ran. (Real evidence: ledger row S3.)
S3's reason comes from agent-factory research/31:19, approved by the operator; the ledger row has none.

## S4 — A bug fix starts with a test that fails for the bug's reason

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
Bug #123 (every consumer shared `consumer-1`) makes this fail on the old code for exactly the bug's reason, read from Redis. (Real evidence: ledger row S4.)

## S6 — Run the failing test locally, and paste its output

**Bad** (neutral)
```text
git commit -m "test: rounding of a discounted total"   # the test was never run
git push
CI job prove-red ...................................... 12 min, failed (expected)
Pull request body: "Red run: <link to the CI job>"
```
The red state is proved by a 12-minute CI job, and the pull request holds only a link, not the failure.

**Good** (neutral)
```text
./gradlew test --tests '*PriceRoundingTest*'
  PriceRoundingTest > should round a discounted total half-up FAILED
    expected 10.05 but was 10.04                           4 s
Pull request body:
  Baseline at main <sha>: PriceRoundingTest <n> tests, 0 failed.
  Red run, local, at a1b2c3d (test only): the command and the failure above.
  Green run at d4e5f6a (the fix): same command, passed.
```
The red run takes seconds locally, before the push, and the pull request carries its command and failure. (Real
evidence: ledger row S6.)

## S5 — Pick the tier by what fails, not by the error path

**Bad** (neutral)
```groovy
    def "a quantity outside the allowed range is refused"() {
        when: "a quantity the database would not accept is added"
        orderService.addLine(orderId, "SKU-1", quantity)

        then: "the service guard fires before the CHECK constraint does, with a readable message"
        def e = thrown(IllegalArgumentException)
        e.message.contains("quantity must be")

        and: "and nothing is written"
        orderService.lineCount(orderId) == 0L

        where:
        quantity << [0, -1, 100]
    }
```
A pure `if` guard boots Postgres in an IT; the CHECK constraint it names is never reached, so no boundary is added.

**Good** (neutral)
```groovy
    OrderRepository orderRepository = Mock()

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
The error comes from pure logic, so it is a unit spec; `0 *` on the `Mock()` repository is the behaviour here because nothing may be reached. (Real evidence: ledger row S5.)
