# Spock — Good / Bad examples

Every approved Good/Bad pair for the Spock rules, one per rule. The rules, the decision table and the review checks
are in [`../spock.md`](../spock.md). Each pair is in one neutral domain (orders and invoices).

Contents: K1 · K2 · K2b · K3 · K4 · K5 · K6 · K7 · K8 · K9 · K10 · K11 · K12 · K13 · K14 · K15 · K16 · K17 · K18 · K19 · K20

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
The assert-then-true ritual stops at the first wrong field. One run never shows the other broken fields.

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
`verifyAll` checks each field of the argument and reports every failing one, with no `assert` and no trailing
`true`. (Real evidence: ledger row K1.)

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
The `then:` interaction replaces the `given:` stub. `save` returns null, and `saved.total` throws a
NullPointerException.

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
One interaction carries the count, the argument check and the return value, so nothing overrides the stub. (Real
evidence: ledger row K2.)

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
The order id is known, but the wildcard lets a delete of another order's lines pass.

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
The scope is the promise, so it is matched by its real value; the save belongs to another feature, so it is a stub in given:, never counted. (Real evidence: ledger row K2b.)

### K3 — A Stub() never gets a call count; a verified call needs a Mock()

**Bad** (neutral)
```groovy
    PaymentGateway paymentGateway = Stub()
    ...
        then: "the invoice is charged once"
        1 * paymentGateway.charge(invoiceId, amount) >> new Payment(paymentId, invoiceId, amount)
```
Spock rejects a call count on a Stub with InvalidSpecException when the spec runs.

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
The call is the behaviour under test, so the gateway is a Mock; a collaborator that only answers stays a Stub. (Real evidence: ledger row K3.)

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
The save is not what this feature promises, so a change to how the order is stored breaks an email test.

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
Only the promised interaction is counted; the save is stubbed for the flow and owned by its own feature. (Real evidence: ledger row K4.)

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
Reading the invoice twice harms nothing, so counting the read breaks the test on a harmless refactor.

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
The read is only stubbed; the count stays on the one email, because exactly one receipt is the contract. (Real evidence: ledger row K5.)

### K6 — Data tables: | inputs, || before expected; #var in the name; no @Unroll

**Bad** (neutral)
```groovy
    @Unroll
    def "should give a #tier customer #expected off an order of #subtotal"() {
```
`@Unroll` is the default since Spock 2.0, so the annotation is noise that copies spread.

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
`||` splits inputs from the expected value, and #var names each iteration without @Unroll. (Real evidence: ledger row K6.)

### K7 — where: reads only @Shared or static fields; build mocks in given:

**Bad** (neutral)
```groovy
    InvoiceRepository invoiceRepository = Mock()
    ...
        where: "each repository the guard might consult"
        repo << [invoiceRepository]
```
`where:` cannot read an instance field or a mock, so Spock rejects the spec.

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
The table reads only the static id and plain values; the mock stays an instance field, stubbed in given:. (Real evidence: ledger row K7.)

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
The branch on the valid column hides two rules in one feature, and a failure names neither.

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
Refused values get their own feature and accepted values another, so each failure names the one rule it broke. (Real evidence: ledger row K8.)

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
The class under test is shared by every feature, so state one feature leaves in it leaks into the next.

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
Only the expensive server is shared and reset per feature; the cheap subject is built fresh for each feature. (Real evidence: ledger row K9.)

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
The stubs the feature depends on are hidden in a helper, so the reader cannot see why the result holds.

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
Every stub, count and the fixed clock the feature relies on is visible in its own given: and then: blocks. (Real evidence: ledger row K10.)

### K11 — Variables an interaction uses are set before when:, never in when:

**Bad** (neutral)
```groovy
        when: "the customer places a draft order"
        def placed = orderService.place(draftOrderId)

        then: "the confirmation names the order just placed"
        1 * emailSender.sendConfirmation({ it.id == placed.id })
```
Spock moves `then:` interactions before `when:`, so `placed` is not set when the interaction is set up.

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
The interaction reads only values that exist before `when:`. The `when:` result is read in plain conditions. (Real
evidence: ledger row K11.)

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
Groovy .with{} returns one chained boolean, so a failure shows one opaque condition instead of the wrong field.

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
`verifyAll` asserts each line on its own and reports every field that is wrong. (Real evidence: ledger row K12.)

### K13 — Assert call order only when order is the contract, with consecutive then: blocks

**Bad** (neutral)
```groovy
        then: "the gateway is charged before the invoice is marked paid"
        1 * paymentGateway.charge(invoiceId, amount) >> payment

        and: "the invoice is marked paid"
        1 * invoiceRepository.markPaid(invoiceId, payment.id) >> true
```
`and:` imposes no order. Production code that marks the invoice paid first still passes.

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
Two consecutive `then:` blocks make Spock fail when the second call comes before the first. (Real evidence: ledger
row K13.)

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
The spec changes a process-wide logger with no isolation, so it breaks other specs once Spock runs in parallel.

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
Spock honours its own Isolated annotation; the Jupiter isolation annotations and parallel settings are ignored by Spock. (Real evidence: ledger row K14.)

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
The class overrides a port the shared OutboundFakesConfig already fakes, so it forks its own uncached Spring context.

**Good** (neutral)
```groovy
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
@Import(OutboundFakesConfig)
class InvoiceApiIT extends Specification {

    @Autowired
    FakeEmailSender emailSender
```
The shared config supplies the fake, so every IT with this setup reuses one cached context. (Real evidence: ledger row K15.)

### K16 — cleanup: frees per-feature resources defensively

**Bad** (neutral)
```groovy
    def cleanup() {
        logger.detachAppender(appender)
    }
```
If setup() failed before logger was set, cleanup throws and hides the real failure; the DEBUG level is never restored.

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
Null-safe calls survive a failed setup(), and the process-wide logger gets its old level back. (Real evidence: ledger row K16.)

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
The subject is partly faked and checks its own methods, so the test pins how OrderService is split, not what it does.

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
OrderService runs for real; the doubles sit at its outbound ports, which is where a charge or a receipt would leave. (Real evidence: ledger row K17.)

### K18 — Records and value objects are constructed, never doubled

**Bad** (neutral)
```groovy
        given: "the customer who owns the order"
        def owner = Spy(Customer)
        owner.getId() >> UUID.randomUUID()
```
A plain data holder is doubled to fake one getter, so its equals, hashCode and toString can lie.

**Good** (neutral)
```groovy
    def owner = customer()
    def stranger = customer()
    ...
    private Customer customer() {
        new Customer(UUID.randomUUID(), "customer@example.com", CustomerTier.STANDARD)
    }
```
A real Customer carries the one value the features read, and behaves like the production object. (Real evidence: ledger row K18.)

### K19 — Bind the expected exception and assert what matters

**Bad** (neutral)
```groovy
        when: "the same order is invoiced a second time"
        insertInvoice(orderId)
        em.flush()

        then: "invoices allows one row per order, so a customer is never billed twice"
        thrown(Exception)
```
Any exception passes, including one that has nothing to do with the one-invoice-per-order key.

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
The bound exception has the specific type, and its constraint name proves the key refused the row. (Real evidence:
ledger row K19.)

### K20 — A block description says the scenario and the why, never the code

**Bad** (neutral)
```groovy
        when: "it is stored"
        invoiceRepository.save(invoice)
```
The label repeats the method call, so it adds no fact the code does not already show.

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
The when: text names the scenario and the then: text says why the date matters, which the code cannot say. (Real evidence: ledger row K20.)

K20's reason comes from agent-factory research/31:21, approved by the operator; the ledger row has none.
