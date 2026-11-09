# Scenario to tests

How a Gherkin scenario becomes its tests: the name, the step text, the Outline table, the work-item link, the tier
and the MR row. Read it when you write or review a test for a scenario in a work item's acceptance criteria.

Contents: Rules · When X, use Y · Good / Bad (GT1–GT6, CV2) · Decided edges · Review checks

## Rules

The AC itself — its number (GA2), its text (GA6) and any table (GA4) — is owned by
`planning/references/acceptance-criteria.md`.

- **GT1** — Name each test with its scenario title verbatim, an Outline adding " — #placeholder"; a reworded name is
  a review finding, because a reworded name makes a search for the scenario title find no test.
- **GT2** — Repeat the scenario's Given/When/Then/And text in Spock block descriptions and in one Playwright
  `test.step` per step, because Given/When/Then kept in comments never appears in the test report.
- **GT3** — Turn a Scenario Outline into Spock `where:` or Jest `test.each` with the Examples column names unchanged;
  e2e takes one representative row, because a renamed column hid that the test fed counts, not the scenario's seconds.
- **GT4** — Put each scenario test's work item and AC id in `@Issue([...])` (Spock, CV2) or an `issue` annotation
  (Playwright), not in its name, because a javadoc mention gives no work-item number a search can find.
- **CV2** — Name a Spock test's work item and AC with `@Issue(["#NNN", "AC-n"])`, because a comment naming the AC
  is not reported by Spock and drifts.
- **GT5** — Give each scenario one owning tier by S1 (`strategy.md`); add a second tier only for a risk the first
  cannot see, because a second-tier copy re-asserts what the owner proves and catches nothing new.
- **GT6** — List every scenario's AC id → tier → test file:line in the MR description; review marks unlisted or
  unmatched ones "not done", because a scenario with no row lets an untested criterion merge as done.

## When X, use Y

Each row maps a part of the scenario to the test construct that carries it.

| the scenario has | use | why |
|---|---|---|
| a `Scenario:` title | the test name, equal to the title: the Spock feature method name, the Playwright `test()` title | a reworded name makes a search for the scenario title find no test (GT1) |
| a `Given`, `When`, `Then` or `And` step | Spock block descriptions with the step's text; one Playwright `test.step("Given …")` per step | Given/When/Then kept in comments never appears in the test report (GT2) |
| a `Scenario Outline` with `Examples` | Spock `where:` or Jest `test.each` with the Examples column names unchanged, ` — #placeholder` in the name; e2e one representative row | a renamed column hid what the test fed (GT3) |
| a work item and an AC id | Spock `@Issue(["#NNN", "AC-n"])`; a Playwright `issue` annotation | a javadoc mention gives no work-item number a search can find (GT4); Spock does not report a comment naming the AC (CV2) |

## Good / Bad

### GT1 — The test name is the scenario title verbatim

**Bad**
```gherkin
Scenario Outline: A GOLD customer gets ten percent off, a STANDARD customer gets nothing
```
```groovy
    def "the GOLD discount is ten percent, the STANDARD discount is zero"() {
```
The test rewords the title, so a search for the scenario title finds no test.

**Good**
```gherkin
Scenario: should mark an invoice overdue once its due date has passed
```
```groovy
@Issue(["#123", "AC-6"])
def "should mark an invoice overdue once its due date has passed"() {
```
The same string, byte for byte, so `grep -F` on the title finds the test.

### GT2 — Block descriptions and test steps repeat the scenario's steps

**Bad**
```groovy
@Issue(["#123", "AC-6"])
def "should mark an invoice overdue once its due date has passed"() {
    given: "an invoice nobody has paid"
    def invoice = invoiceRepository.save(openInvoiceDue(TODAY.minusDays(1)))

    when: "the job runs"
    overdueReminder.run()

    then: "an open invoice past due is the defect this REQ exists to prevent"
    invoiceRepository.findById(invoice.id()).orElseThrow().status() == InvoiceStatus.OVERDUE
}
```
The block texts paraphrase the scenario, so the test report does not read as the agreed steps.

**Good**
```groovy
@Issue(["#123", "AC-6"])
def "should mark an invoice overdue once its due date has passed"() {
    given: "an OPEN invoice due yesterday"
    def invoice = invoiceRepository.save(openInvoiceDue(TODAY.minusDays(1)))

    when: "the overdue reminder runs"
    overdueReminder.run()

    then: "the invoice is OVERDUE"
    invoiceRepository.findById(invoice.id()).orElseThrow().status() == InvoiceStatus.OVERDUE
}
```
Each block label is the scenario step word for word, so the report reads as the scenario.

### GT3 — An Outline keeps its Examples column names

**Bad**
```groovy
        where:
        level    | amount || expected
        GOLD     | 99.99  || 0.00
        GOLD     | 100.00 || 10.00
        STANDARD | 100.00 || 0.00
```
The columns `tier | total | discount` were renamed, so the table no longer reads against the scenario's Examples.

**Good**
```groovy
@Issue(["#123", "AC-5"])
def "should give ten percent off to a GOLD customer on orders of 100.00 EUR or more — #tier #total"() {
    when: "the discount is decided"
    def decision = discountPolicy.decide(customerOf(tier), orderTotalling(total))

    then: "the discount is <discount> EUR"
    decision.saving().amount() == discount

    where: "a <tier> customer with an order total of <total> EUR"
    tier     | total  || discount
    GOLD     | 99.99  || 0.00
    GOLD     | 100.00 || 10.00
    STANDARD | 100.00 || 0.00
}
```
The column names equal the Examples header, and the Given is the `where:` text because the table is the given.

### GT4 — Each scenario test links its work item and AC id

**Bad**
```groovy
/**
 * #123 §Acceptance criteria. Every figure asserted here is the discount table's, and the
 * table cites where each one comes from.
 *
 * <p>The tier tables run against a policy with no seasonal offer. Seasonal offers are a separate
 * rule with their own features below.
 */
class DiscountPolicySpec extends Specification {
```
Traceability is free javadoc, so no search finds the work item or scenario id on any feature.

**Good**
```groovy
@Issue(["#123", "AC-6"])
def "should mark an invoice overdue once its due date has passed"() {
```
```ts
test(
  'should show "Payment declined" when the gateway declines the payment',
  { tag: '@billing', annotation: { type: 'issue', description: '#123 · AC-9' } },
  async ({ page, declinedInvoice }) => {
    await test.step('Given an OPEN invoice the gateway will decline', () =>
      page.goto(`/invoices/${declinedInvoice.id}`));
    await test.step('When the customer pays the invoice', () =>
      page.getByRole('button', { name: 'Pay invoice' }).click());
    await test.step('Then the page shows "Payment declined"', async () => {
      await expect(page.getByRole('alert')).toContainText('Payment declined');
    });
    await test.step('And no payment is recorded for the invoice', async () => {
      const payments = await page.request.get(`/api/invoices/${declinedInvoice.id}/payments`);
      expect(await payments.json()).toEqual([]);
    });
  },
);
```
Both tests carry a machine-readable link to `#123` and the scenario id; the Playwright test also checks that the
declined payment left no payment record.

### CV2 — One `@Issue` carries the work item and the AC id

**Bad**
```groovy
// AC-3 of #123
def "should refuse to pay an invoice that is already paid"() {
```
Spock does not report a comment, and the comment drifts from the scenario unnoticed.

**Good**
```groovy
@Issue(["#123", "AC-3"])
def "should refuse to pay an invoice that is already paid"() {
```
One annotation carries both links, and a search for `"AC-3"` finds the test.

### GT5 — One owning tier per scenario

**Bad**
```groovy
    @Issue(["#123", "AC-10"])
    def "should never make an invoice total negative with a discount"() {
        given: "one GOLD customer, each order saved to the real database"
        def customer = customerRepository.save(goldCustomer())
        200.times { i -> orderRepository.save(orderFor(customer, i)) }

        expect: "a GOLD customer never gets money back"
        orderRepository.findAll().every { invoiceService.issue(it.id()).total().amount() >= 0 }
    }
```
A unit spec already owns this rule; the IT repeats it against a real database and names no new risk.

**Good**
```groovy
@Issue(["#123", "AC-3"])
def "should refuse to pay an invoice that is already paid"() {
    given: "an invoice that is already PAID"
    def invoice = seedInvoice(InvoiceStatus.PAID)

    when: "the customer pays the invoice"
    def response = payInvoice(invoice.id())

    then: "the payment is refused with INVOICE_ALREADY_PAID"
    response.expectStatus().isEqualTo(409)
        .expectBody().jsonPath('$.type').isEqualTo("https://example.com/errors/INVOICE_ALREADY_PAID")
}
```
The scenario crosses HTTP and the database, so one IT owns it and no smoke spec replays it.

### GT6 — The MR lists every scenario's test

**Bad**
```text
- Take each acceptance criterion from the REQ — or from the work item body, where the change has
  no REQ.
- For each one, find the code that satisfies it and cite `file:line`. Not the test that covers
  it; the code that does it.
- A criterion you cannot cite is not met. Say which, and either implement it or say plainly on
  the MR why it is out of scope.
```
It maps criteria to code, never to tests, so a scenario with no test is invisible.

**Good**
```markdown
| AC | scenario | tier | test |
|---|---|---|---|
| AC-5 | should give ten percent off to a GOLD customer on orders of 100.00 EUR or more | unit | DiscountPolicySpec.groovy:25 |
| AC-3 | should refuse to pay an invoice that is already paid | IT | InvoiceControllerIT.groovy:41 |
| AC-8 | should keep the invoice open on every payment call when the PaymentGateway is unreachable | — | not done |
```
Every scenario has a row, so a missing test shows as "not done".

## Decided edges

- **Skip when** the owning tier already asserts the scenario's Then: write no second-tier copy of it (GT5). —
  **Do not skip when** the UI must show the refusal: add the smoke test beside the owning tier (GT5). —
  **Confidence** high

## Review checks

Walk every scenario in the work item's acceptance criteria, and every changed test that names one.

- [ ] GT1 — For each scenario, `grep -rnF "<title>"` the test tree. A scenario with no exact match, or an Outline
  test whose name lacks ` — #placeholder` after the title, is a finding.
- [ ] GT2 — For each scenario test, match every `Given`, `When`, `Then` and `And` step to a Spock block description
  or a Playwright `test.step` with the same text. A missing or paraphrased step is a finding.
- [ ] GT3 — For each Outline, compare the `where:` or `test.each` column names with the Examples header, and count
  the rows of an e2e test. A renamed column, or an e2e test with more than one row, is a finding.
- [ ] GT4, CV2 — For each scenario test, find the work item and the AC id in `@Issue([...])` (Spock,
  `grep -n "@Issue"`) or in an `issue` annotation (Playwright). Either one missing, or carried only in a comment,
  a javadoc or the name, is a finding.
- [ ] GT5 — For each scenario tested at two tiers, find the risk the second tier catches that the owner cannot see.
  A second tier with no such risk is a finding.
- [ ] GT6 — Find one MR-description row per scenario, and open each test `file:line` it cites. A scenario with no
  row, or with a row citing a test that is not its own, is marked "not done".
