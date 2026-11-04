# Coverage design

Which cases a test file needs for new logic, and how a case left untested is recorded. Read it when you write or
review tests for new logic, or a test of a call to an external dependency.

Contents: Rules · When X, use Y · Good / Bad (C1, C2, C3, C4) · Decided edges · Review checks

## Rules

- **C1** — Before testing new logic, decide its cases by RIGHT-BICEP (Right, Boundary, Inverse, Cross-check, Error,
  Performance); skip a dimension only with a one-line reason, because a reviewer cannot tell a skipped dimension from
  a forgotten one.
- **C2** — Test each external dependency's unavailable case (DB, Redis, LLM provider, HTTP tool): a predictable
  failure, a WARN or ERROR log, no hang, because an untested outage path can swallow the error without any log.
- **C3** — Write the expected value out, worked independently, never computed by the code under test or a copy of its
  logic, because an expected value from the code itself shares its defect and always passes.
- **C4** — Record each case you knowingly leave untested as one gap row in the MR description (dimension · missing ·
  risk), never left unsaid, because an unrecorded gap cannot be told from an oversight.

## When X, use Y

Each row maps what the new logic has to the RIGHT-BICEP dimension it triggers and the cases to write (C1).

| the logic | use | why |
|---|---|---|
| has a main result: a method, parser, mapper or domain rule | Right results: one explicit expected value, written out (C3) | the expected value is explicit and independently understandable |
| takes an input of a kind B2 names (`boundaries.md`) | Boundary conditions: the CORRECT cases of B1–B3 (`boundaries.md`) | when boundary analysis is the main task, CORRECT gives the detailed categories |
| has two operations that undo or preserve each other: encode and decode, add and remove, write and read | Inverse relationships: run both directions; assert meaningful equality, not only a non-null result | a reviewer cannot tell a skipped dimension from a forgotten one (C1) |
| has a result that is easy to compute wrongly, or a complex algorithm | Cross-checks: compare with an independent calculation, fixture, alternate implementation or property | the oracle must not reimplement the production algorithm with the same defect |
| can meet invalid input, illegal state, overflow, a missing resource or a denied operation | Error conditions: force the error directly; assert the exception type, and the message or error code when the contract names it | a reviewer cannot tell a skipped dimension from a forgotten one (C1) |
| calls an external dependency | Error conditions: the unavailable case (C2); which of WARN and ERROR, see LG3 (`obs/references/logging.md`) | test how the code degrades when a dependency is unavailable |
| has performance in its contract, or a known performance risk | Performance: a deterministic proxy — query count, batch count, call count — not a wall-clock threshold | a reviewer cannot tell a skipped dimension from a forgotten one (C1) |
| has a case you knowingly leave untested | a gap row in the MR description (C4) | missing boundary cases are recorded as explicit test gaps; a gap matrix names dimension, missing test and risk |

## Good / Bad

### C1 — Decide the cases with RIGHT-BICEP before writing

**Bad**
```groovy
    def "a new order entity starts as a draft"() {
        expect: "Hibernate writes the field on every INSERT, so a default of PLACED would override V12's column default"
        new OrderEntity().status == OrderStatus.DRAFT
    }
```
One Right case, and nothing shows which other dimensions were considered or why they were skipped.

**Good**
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
        def order = newOrder()

        when: "it is stored and the persistence context is cleared"
        def id = em.persistFlushFind(order).id
        em.clear()

        then: "Hibernate writes the field on every INSERT, so the stored row holds the entity's value"
        em.find(OrderEntity, id).status == OrderStatus.DRAFT
```
Every RIGHT-BICEP letter is decided in the header. The case stores the order in `when:` and reads the stored row in
`then:`, instead of a field default.

### C2 — Test the unavailable case of every external dependency

**Bad**
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
It proves only silence. No WARN is asserted, so code that swallows the outage without a log still passes.

**Good**
```groovy
    @Timeout(14)
    def "should warn the mail service unreachable, within a bound, when it never answers"() {
        given: "an overdue invoice, behind a mail endpoint that holds every request for 15 s"
        wireMock.stubFor(post(urlEqualTo("/send")).willReturn(okJson("{}").withFixedDelay(15_000)))
        def invoiceId = seedOverdueInvoice(customerId)

        when: "the reminder job runs"
        overdueReminder.run()

        then: "it gave up before the endpoint would have answered, and named the invoice at WARN"
        def line = appender.list.find { it.formattedMessage.contains("status=unreachable invoiceId=$invoiceId") }
        line?.level == Level.WARN
    }
```
The dependency never answers. `@Timeout(14)` bounds the time with no wall-clock read, and the test asserts the logged
outcome and its WARN level.

### C3 — Write the expected value out, worked independently

**Bad**
```java
    @Test
    void emailNormalisation_ignoresCase() {
        // upper-case domain vs lower-case domain
        String typed = "Ann@Example.COM";   // as typed
        String stored = "ann@example.com";  // as stored
        assertThat(CustomerEmail.normalise(typed)).isEqualTo(CustomerEmail.normalise(stored));
    }
```
Both sides come from `normalise`, so a `normalise` that returns an empty string for every input still passes.

**Good**
```groovy
    def "should normalise an email typed in mixed case to lower case"() {
        expect: "the lower-case form is written out by hand, never produced by normalise itself"
        CustomerEmail.normalise("Ann@Example.COM") == "ann@example.com"
    }
```
The expected value is a literal worked out by hand, so a broken `normalise` cannot also produce it.

### C4 — One gap row per knowingly untested case

**Bad**
```markdown
## Verification

`./gradlew check`: 412 tests passed, smoke 88 passed / 0 failed / 0 skipped.

Each of the new assertions was mutation-tested rather than assumed: removing the
paid-invoice guard and letting a SHIPPED order cancel each turn the expected case red.
```
It lists what ran and nothing about what was not tested, so a decided gap looks like an oversight.

**Good**
```markdown
## Verification

`./gradlew check`: 412 tests passed, smoke 88 passed / 0 failed / 0 skipped.

## Not tested, by decision

| dimension | missing | risk |
|---|---|---|
| E — error | the cancellation email while `EmailSender` is down | the customer is not told the order was cancelled |
| B — boundary | cancelling a DRAFT order with no lines | an empty cancellation email is sent |
```
Each knowingly untested case is one `dimension · missing · risk` row, so a reviewer can tell a decision from an
oversight.

## Decided edges

- **Skip when** the logic has nothing the dimension reads: no two operations that undo each other, or
  no performance contract and no known performance risk. Write the one-line reason (C1). — **Do not
  skip when** the reason is left out: a bare skip cannot be told from a forgotten dimension. — **Confidence** high
- **Skip when** the only time bound is a hang guard (`@Timeout`) on an unavailable case (C2): a hang guard
  (`@Timeout`) is not a performance assertion, so it needs no Performance case. — **Do not skip when** the contract
  names a speed: decide Performance with a deterministic proxy, not a wall-clock threshold. — **Confidence** high

## Review checks

Walk every changed test file that covers new logic, and the MR description.

- [ ] C1 — For each piece of new logic, find each of the six dimensions — Right results, Boundary conditions,
  Inverse relationships, Cross-checks, Error conditions, Performance — decided: a case, or a skip with a one-line
  reason. A dimension with neither, or a skip with no reason, is a finding.
- [ ] C2 — For each external dependency the changed code calls (DB, Redis, LLM provider, HTTP tool), find a test of
  the unavailable case. It asserts a predictable failure, a WARN or ERROR log, and that the call returns instead of
  hanging. A dependency with no such test, or a test that asserts no log, is a finding.
- [ ] C3 — For each assertion, find where its expected value comes from. A value computed by calling the code under
  test, or by a copy of its logic, is a finding.
- [ ] C4 — For each case the change knowingly leaves untested, find one row in the MR description with dimension,
  missing and risk. An untested case with no row, or a row with a column empty, is a finding.
