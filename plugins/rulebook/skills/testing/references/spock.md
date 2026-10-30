# Spock

How to write interactions, data tables, shared state, cleanup and assertions in a Spock specification. Read it when
you write or review a Spock spec, unit or integration.

Contents: Rules · When X, use Y · Good / Bad (K1, K2, K11, K13, K19) · Decided edges · Review checks

## Rules

- **K1** — In a mock-argument closure, write each check as its own top-level line, or `verifyAll(it, Type){…}` for
  many fields, because checks inside a nested closure such as `every{}` are never asserted.
- **K2** — When a call must return a value and be verified, write one interaction (`1 * repo.save(_) >> saved`),
  because a `given:` stub plus a `then:` count makes the call return null.
- **K2b** — Match a verified interaction's arguments by real value or by a constraint closure on the promised
  fields, because a wildcard argument lets a call with the wrong value pass.
- **K3** — Never give a `Stub()` a call count; use a `Mock()` when the call must be verified, because a Stub given a
  call count throws `InvalidSpecException`.
- **K4** — Mocks are lenient, so assert only the interactions the feature name promises, because asserting
  incidental calls breaks the test when someone adds a log line.
- **K5** — Count a call exactly (`N *`) only when N is the contract, and never count logging, metrics or retries,
  because a counted retry breaks the test when the retry policy changes.
- **K6** — Write a data-driven feature as a `where:` table (`|` between inputs, `||` before expected values) or a `<<`
  pipe for a single column, named with `#var`, no `@Unroll`, because otherwise iterations share one name.
- **K7** — In `where:`, read only `@Shared` or static fields; put a plain discriminator in the table and build mocks in
  `given:`, because Spock rejects a `where:` that reads an instance field or a mock.
- **K8** — Test one rule per data-driven feature: no `if` on a `where:` column, and throws-cases in another feature
  than returns-cases, because a branch on a column hides two rules and a failure names neither.
- **K9** — Use `@Shared` only for an expensive read-only resource, never for mocks or mutable state; use instance
  fields instead, because shared mutable state makes features pass alone and fail together.
- **K10** — Write interactions in the feature's own `given:` and `then:` blocks; a helper that asserts carries
  `@Verify`, `@VerifyAll` or `assert`, because a helper's hidden interaction makes an empty `then:` still assert.
- **K11** — Declare each variable an interaction uses before `when:` or inside `interaction{}`, never in `when:`,
  because `then:` interactions run before `when:`, so a variable set there is unset.
- **K12** — Check several fields of one result with `verifyAll(obj){…}`, never Groovy `obj.with{}`, because Groovy
  `obj.with{}` gives one opaque condition, not one check per field.
- **K13** — Assert call order only when order is the contract, and then with consecutive `then:` blocks, because
  `and:` imposes no order, so calls in the wrong order still pass.
- **K14** — Isolate a spec that touches global state with `@spock.lang.Isolated` or `@ResourceLock`, never Jupiter
  annotations, because Spock ignores Jupiter isolation, so a global-state spec runs unprotected.
- **K15** — In a Spring-context spec, use the shared fake ports (IT4, `integration-tests.md`) and `@SpringBean` only at
  an external boundary, because each `@SpringBean` forks a new uncached Spring context.
- **K16** — Free per-feature resources in `cleanup:` and write it defensively (`resource?.close()`), because
  `cleanup:` runs after any failure, when variables may still be null.
- **K17** — Never spy the class under test (`Spy()`, `@SpringSpy`, `Mockito.spy`); extract the method into an
  injected collaborator and double that, because a spied subject has its own methods faked and verified, not run.
- **K18** — Construct records and value objects with the values the test needs, never `Mock()` them, because a
  mocked value object can lie about `equals`, `hashCode` and `toString`.
- **K19** — Bind an expected exception as `def e = thrown(T)` and assert what matters; assert no exception with
  `noExceptionThrown()`, because an unbound `thrown()` passes for any exception, even an unrelated one.
- **K20** — Write a block description that says the scenario and the why, never the code restated, because a label
  that restates the code loses the one place the test can say why the case matters.

## When X, use Y

| the spec has | use | why |
|---|---|---|
| a mock argument with many fields to check | `verifyAll(it, Type){…}` inside the argument closure (K1) | every top-level line of a code constraint is asserted · notes :946 · ibt :253 |
| one result with many fields to check | `verifyAll(obj){…}` to see every failing field; Spock `with(obj){…}` when the first failure is enough (K12) | primer :606-691 · notes :62-64 |
| a call that returns a value and is counted | one interaction: `1 * x() >> v` (K2) | ibt :734-746 |
| a collaborator that only returns values | `Stub()`; it answers empty values (`""`, `[]`, `0`), not null (K3; the Stub or Mock choice is U3, `unit-tests.md`) | ibt :788-797 |
| "nothing else is called" as the promised behaviour | `0 * _` (K4) | ibt :290-306 |
| a data table | `\|` between inputs, `\|\|` before expected values, `#var` in the feature name, no `@Unroll` (K6) | `\|\|` is visual only (ddt :118) · unrolling is the default since Spock 2.0 (ddt :166) |
| a `where:` row that needs a mock | a plain discriminator in the table; the mock built in `given:` (K7) | only `@Shared` and static fields may be read from `where:` (ddt :100) |
| a helper method that asserts | `@Verify` or `@VerifyAll` on the helper, or an explicit `assert` (K10) | primer :581-591 |
| an interaction that reads the `when:` result | the value declared before `when:` or inside `interaction{}`; the result read in a plain condition (K11) | `then:` interactions are moved before `when:` (ibt :402-425) |
| a call order that is the contract | one `then:` block per step, in order (K13) | ibt :513-536 |
| a spec that changes process-wide state | `@spock.lang.Isolated` on the class, or `@ResourceLock` (K14) | Spock ignores `junit.jupiter.execution.parallel.*` (par :11-35) · `Isolated` targets a class only (Isolated.java:27) |
| an expected exception | `def e = thrown(T)`, then a condition on what matters (K19) | primer :340-380 |
| a block label | the scenario words and the why (K20); a scenario's own text is GT2, `scenario-to-tests.md` | labels are documentation, not report output (primer :791-830) |

`ibt` is the Spock 2.4 doc `interaction_based_testing.adoc`, `primer` is `spock_primer.adoc`, `ddt` is
`data_driven_testing.adoc`, `par` is `parallel_execution.adoc` and `notes` is `release_notes.adoc`; `:N` is the line.

## Good / Bad

Every rule's approved pair: [examples/spock.md](examples/spock.md).

### K1 — Plain lines in a mock-argument closure, or verifyAll(it, Type)

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

### K2 — Return-and-verify is one interaction

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

### K11 — Variables an interaction uses exist before when:

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

### K13 — Call order with consecutive then: blocks

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

## Decided edges

- **Skip when** the argument is not part of what the feature promises, or cannot be known in the test (a generated
  id, a timestamp): use `_` or `*_` (K2b). — **Do not skip when** part of the argument is known: constrain what you
  can. — **Confidence** medium
- **Skip when** "nothing else is called" is itself the behaviour: assert it with `0 * _` (K4). — **Do not skip when**
  the extra call is incidental, such as a log line, a metric or a retry (K5). — **Confidence** high
- **Skip when** the double sits at an external boundary: `@SpringBean` is allowed there (K15). — **Do not skip when**
  the port is one the shared fake set already replaces (IT4, `integration-tests.md`). — **Confidence** high
- **Skip when** the spy sits in code the change does not touch. — **Do not skip when** the change touches that code:
  refactor the spy away in the same change; there is no legacy exception (K17). — **Confidence** high

## Review checks

Walk every changed Spock spec, unit and integration (`grep -l "extends Specification"`).

- [ ] K1 — Open each argument closure. A check nested in `every{}` or another inner closure is a finding.
- [ ] K2 — For each `N *` interaction, look for a `given:` stub of the same call. Both present is a finding.
- [ ] K2b — For each `_` or `*_` in an `N *` interaction, the argument is not promised or not knowable (Decided edges).
  A promised, known argument matched by `_` is a finding.
- [ ] K3 — For each `Stub()`, look for an `N *` on it. One found is a finding.
- [ ] K4 — For each counted interaction, the feature name promises it. A count on an incidental call is a finding.
- [ ] K5 — An `N *` on a logging, metrics or retry call is a finding, and so is an exact count where N is not the
  contract.
- [ ] K6 — For each `where:` block, find a table with `|` between inputs and `||` before expected values, or a `<<`
  pipe for a single column, and `#var` in the name. `@Unroll` (`grep -n "@Unroll"`) is a finding.
- [ ] K7 — A `where:` that reads an instance field or a mock is a finding.
- [ ] K8 — An `if` on a `where:` column, or throws-cases and returns-cases in one feature, is a finding.
- [ ] K9 — For each `@Shared` field (`grep -n "@Shared"`), it is expensive and read-only. A mock or mutable state is
  a finding.
- [ ] K10 — An interaction (`N *` or `>>`) inside a helper method is a finding. A helper with conditions but no
  `@Verify`, `@VerifyAll` or `assert` is a finding.
- [ ] K11 — For each interaction, every variable it reads is declared before `when:` or inside `interaction{}`. A
  variable assigned in `when:` is a finding.
- [ ] K12 — Groovy `.with{` used as an assertion (`grep -nE "\.with ?\{"`) is a finding.
- [ ] K13 — For each order-dependent claim in a feature name or block label, the calls sit in consecutive `then:`
  blocks. Order asserted through `and:`, or asserted where order is not the contract, is a finding.
- [ ] K14 — For each spec that changes process-wide state (a logger level, a global mock), find
  `@spock.lang.Isolated` or `@ResourceLock`. A Jupiter annotation or none is a finding.
- [ ] K15 — For each `@SpringBean` (`grep -n "@SpringBean"`), it doubles an external boundary. A port the shared
  fake set covers is a finding.
- [ ] K16 — A per-feature resource opened and never freed in `cleanup:` or `cleanup()` is a finding. In cleanup, a
  call on a field or variable without `?.` is a finding.
- [ ] K17 — `Spy(`, `@SpringSpy` or `spy(` on the class under test (`grep -nE "Spy\(|@SpringSpy|spy\("`) is a finding.
- [ ] K18 — `Mock(`, `Stub(` or `Spy(` of a record or value object is a finding.
- [ ] K19 — A `thrown(...)` not bound to a variable, a bound exception with no condition on it, a "no exception"
  case without `noExceptionThrown()`, or a `then:` with no condition is a finding.
- [ ] K20 — A block description that restates the code below it is a finding.
