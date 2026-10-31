# Strategy

Which tier a test belongs in, what it may fake, and what it asserts. Read it when you choose where a new test goes,
when you fix a bug, or when you review the tier and the doubles of a changed test.

Contents: Rules · When X, use Y · Good / Bad (S1, S2, TM1, TM2, S3, S5) · Decided edges · Review checks

## Rules

- **S1** — Test pure logic in a unit spec, a real boundary (DB, Redis, HTTP, Spring wiring) in an IT, and a user
  journey in a smoke spec, because a Spring context makes plain service tests slow.
- **S2** — Assert observable behaviour, never a field default or the input you just passed in, because a test of a
  default or its own input cannot fail for a defect.
- **TM1** — At a boundary, make the IT the primary test and add unit specs only for branching it cannot reach cheaply,
  because a unit spec through a mock cannot see what the real boundary does.
- **TM2** — In ITs and smoke specs, fake only what others own (LLM: scripted model; third-party HTTP: WireMock at the
  wire, unless the vendor ships a container sandbox (IT5)), because faking our code leaves its query untested.
- **TM3** — Keep real-model tests in their own opt-in tier outside the gate, written to `llm-live-tests.md`, because a
  real model in the gate makes every run slow, paid and flaky.
- **AT1** — Prove an acceptance criterion with an IT (API) or a smoke spec (UI), never a separate acceptance tier,
  because a `.feature` tier with no Gherkin runtime left an orphan copy of an IT.
- **S3** — Before changing code, run the existing tests that touch it and note what was green, because a red test
  seen only after the change cannot be told from one already red.
- **S4** — Start a bug fix with a test that fails for the bug's reason, landed before the fix in the MR, because a
  regression test that never failed proves the mock, not the fix.

## When X, use Y

| situation | use | why |
|---|---|---|
| the behaviour is pure logic | a unit spec, with no Spring context | a Spring context makes a plain service test very slow (S1) · ledger :9 · plinth 321:47 |
| the behaviour crosses a real boundary: DB, Redis, HTTP, Spring wiring | an IT | the flow needs real collaborators (S1) · ledger :9 · plinth 322:57 |
| the behaviour is a user journey | a smoke spec | S1 · ledger :9 |
| the case is an error or unhappy path | the tier of what fails | an IT for a pure error branch starts Postgres yet reaches no boundary (S5) · ledger :13 · plinth 058:36 |
| a boundary the IT covers has branching it cannot reach cheaply: many input combinations, error mapping, edge values | a unit spec for that branching only | no unit test re-proves what the IT proves (TM1) · ledger :37 |
| an acceptance criterion is reached through the API | an IT | a `.feature` tier with no Gherkin runtime left an orphan copy of an IT (AT1) · ledger :35 |
| an acceptance criterion is reached through the UI | a smoke spec | AT1 · ledger :35 · tier choice: `scenario-to-tests.md` |
| an IT or smoke spec reaches the LLM | a scripted fake model | we do not own it (TM2) · ledger :38 |
| an IT or smoke spec reaches third-party HTTP | WireMock at the wire, or the vendor's container sandbox when it ships one (IT5) | we do not own it (TM2) · ledger :38 |
| an IT or smoke spec reaches our own service, repository or Redis consumer | the real one | a fake of our own code leaves its real query untested (TM2) · ledger :38 |

Ledger is `research/19-approved-rules.md` in this repo; plinth `321`, `322` and `058` are the pinned plinth-java-skills
files of those numbers; `:N` is a line.

## Good / Bad

Every rule's approved pair: [examples/strategy.md](examples/strategy.md).

### S1 — Pick the tier by what the behaviour depends on

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

### S2 — Assert observable behaviour

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

### TM1 — At a boundary the IT is the primary test

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

### TM2 — Fake only what we do not own

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

### S3 — Run the existing tests before changing code

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

### S5 — Pick the tier by what fails, not by the error path

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

## Decided edges

- **Skip when** an error case comes from pure logic: it stays a unit spec, not an IT (S5, ledger :13). — **Do not
  skip when** what fails is a real boundary: that case is an IT, by what fails (S1, S5, ledger :9, :13).
  — **Confidence** high
- **Skip when** the run is the gate: the real-model tier is opt-in and stays out of it (TM3). — **Do not skip
  when** prompt or provider code changes, or before a release: the real-model tier must pass then (TM3, ledger :39).
  — **Confidence** high

## Review checks

Walk every changed test file, and the MR that carries it.

- [ ] S1 — For each changed test, name what the behaviour depends on: pure logic, a real boundary (DB, Redis, HTTP,
  Spring wiring) or a user journey. A test in another tier is a finding. A Spring context around plain service logic
  is a finding (`grep -nE "SpringBootTest|ContextConfiguration|SpringExtension"`).
- [ ] S2 — For each assertion, name the observable behaviour it checks. An assertion that reads back a field default
  or the input the test passed in is a finding. A hand-copied list of enum members is V3 (`value-bar.md`).
- [ ] S5 — For each IT of an error or unhappy path, find the boundary the failure reaches. An error that comes from
  pure logic is a finding: it belongs in a unit spec.
- [ ] TM1 — For each unit spec beside an IT on the same boundary, check that it covers only branching the IT cannot
  reach cheaply. A unit spec that re-proves what the IT proves is a finding.
- [ ] TM2 — In each changed IT and smoke spec, list every fake. A fake is allowed only for the LLM (a scripted fake
  model) and for third-party HTTP (WireMock at the wire). Where the vendor ships a container sandbox, the IT uses it
  and WireMock is not required (IT5). A fake of our own service, repository or Redis consumer is a finding.
- [ ] TM3 — For each real-model test, check that it is opt-in and runs outside the gate. If the change touches prompt
  or provider code, or is a release, find the real-model tier's passing result. No such result is a finding. What a
  live test asserts and how its job runs are checked against `llm-live-tests.md`.
- [ ] AT1 — For each acceptance criterion, find the IT (API) or smoke spec (UI) that proves it. A `.feature` file
  or a separate acceptance harness is a finding.
- [ ] S3 — Find the note of the existing tests that touch the changed code, run before the change, and what was
  green. No note is a finding.
- [ ] S4 — For a bug fix, find the test that fails for the bug's reason, and check that it lands before the fix.
  A fix with no such test is a finding. Where that one test sits is V4 (`value-bar.md`).
