# Unit tests

How a unit test is built: what makes it trustworthy, how a Spock feature is laid out, and which collaborators get a
test double. Read it when you write or review a unit test or a Spock spec.

Contents: Rules · When X, use Y · Good / Bad (U1, U3, U2) · Decided edges · Review checks

## Rules

- **U1** — Write every test A-TRIP (Automatic, Thorough, Repeatable, Independent, Professional): a fixed clock, no
  shared state, no order dependence, because a test tied to clock, order or shared state fails without a defect.
- **U3** — Double only at boundaries: `Stub()` what only returns, `Mock()` only a call that is the behaviour, an
  existing fake port over both, because mocking your own classes breaks tests on refactors that keep behaviour.
- **U2** — Write every Spock feature in labelled blocks (`given:`/`when:`/`then:`; `expect:` for a pure function;
  `where:` for a table), named as a plain behaviour sentence, not shouldXxx, because the labels tell Spock which lines
  are assertions.

## When X, use Y

| situation | use | why |
|---|---|---|
| the feature tests a pure function with no collaborators | `expect:`, no doubles; `where:` for several inputs (U2) | `expect:` collapses `when:` + `then:` for a pure expression |
| the feature asserts a state change on the subject | `given:` / `when:` / `then:` with conditions only (U2) | the labels tell Spock which lines are assertions |
| a collaborator only returns a value to the subject | `Stub()` with `>>` (U3); a call count on a stub is K3 (`spock.md`) | the call is not the behaviour, so nothing about it is verified |
| the subject's call to a collaborator is the behaviour | `Mock()` and its interaction in `then:` (U3); which interactions to assert is K4 (`spock.md`) | the call is the behaviour, so it is what the test verifies |
| the collaborator is your own class or module | the real class (U3) | mocking your own classes breaks tests on refactors that keep behaviour |
| a fake of the port already exists | the fake, not a `Stub()` or `Mock()` (U3) | a fake ranks above a stub and a mock |
| the logic reads the clock or a random value | a fixed clock (U1); how production code takes it is U4 (`code/references/java.md`) | time and randomness are system boundaries |

## Good / Bad

### U1 — Every test is A-TRIP

**Bad**
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
The result depends on wall-clock time and host speed, and an interrupt returns silently as if the condition held.

**Good**
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
A fixed clock, a fresh instance per feature and both sides of the boundary make the test repeatable and independent.

### U3 — Double only at boundaries

**Bad**
```groovy
    OrderRepository orderRepository = Mock()
    InvoiceRepository invoiceRepository = Mock()
    PaymentGateway paymentGateway = Mock()
    ...
            orderRepository.findById(ORDER_ID) >> Optional.of(placedOrder(ORDER_ID))
```
Every port is a `Mock()` that is only stubbed and never verified, so the spec hides which call is the behaviour.

**Good**
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
The lookup only returns, so it is a `Stub()`. Saving the invoice is the behaviour, so only that call is a verified
`Mock()`.

### U2 — Labelled blocks and a plain behaviour sentence as the name

**Bad**
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
The name is camelCase, and `when:`/`then:` wrap a pure construction.

**Good**
```groovy
    def "should keep the lines a draft order is created with, in their order"() {
        given: "two lines for different products"
        def first = new OrderLine("SKU-1", 2, money("10.00"))
        def second = new OrderLine("SKU-2", 1, money("5.00"))

        expect: "the invoice later totals exactly these lines, so none may be dropped or reordered"
        Order.draft(CUSTOMER_ID, [first, second]).lines() == [first, second]
    }
```
The name is a plain behaviour sentence, and `expect:` fits a pure construction.

## Decided edges

- **Skip when** an existing JUnit test is left unchanged: it keeps its name and layout (U2). — **Do not skip when**
  the change adds a Spock feature. — **Confidence** high
- **Skip when** a `@Shared` field holds an expensive read-only resource: it is not shared state under U1 (K9,
  `spock.md`). — **Do not skip when** a `@Shared` field holds a mock or mutable state: features then pass alone and
  fail together (K9). — **Confidence** high

## Review checks

Walk every changed test file.

- [ ] U1 — For each changed test, check all five letters. Automatic: it runs and decides with no human step.
  Thorough: run the C1 (`coverage-design.md`) and B1 (`boundaries.md`) checks. Repeatable: a fixed clock, no shared
  state, no order dependence (`grep -nE "now\(\)|currentTimeMillis"` finds wall-clock reads). Independent: it runs
  alone and in any order. Professional: it is named and kept like production code. A letter not met is a finding.
- [ ] U2 — For each new or changed Spock feature, find every statement under `given:`, `when:`, `then:`, `expect:`
  or `where:`, and a name that is a plain behaviour sentence. An unlabelled statement or a camelCase shouldXxx name is
  a finding. Block descriptions are K20 (`spock.md`); a name tied to an AC is GT1 (`scenario-to-tests.md`).
- [ ] U3 — For each `Mock()`, `Stub()` and `Spy(` in a changed spec (`grep -nE "Mock\(|Stub\(|Spy\("`): the doubled
  type is a boundary (outbound port, clock, randomness, external API), never your own class; a collaborator that only
  returns is a `Stub()`; a `Mock()` has its call verified in `then:`; where a fake of the port exists, the fake is
  used. A double that fails one of these is a finding. Which interactions a `Mock()` asserts is K4, and a spy of the
  subject is K17 (both `spock.md`).
