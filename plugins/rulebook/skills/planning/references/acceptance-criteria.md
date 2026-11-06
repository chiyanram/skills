# Acceptance criteria

How a work item's acceptance criteria are written as Gherkin scenarios in its spec: home, ids, tags, titles, steps and
Outlines. Read it when you write or review the acceptance criteria of a spec as Gherkin scenarios.

Contents: Rules · When X, use Y · Good / Bad (GA3–GA6, CV1, AC7–AC9) · Decided edges · Review checks

## Rules

How each scenario becomes its tests is owned by `testing/references/scenario-to-tests.md` (GT1–GT6).

- **GA1** — Write a work item's acceptance criteria only in its spec's acceptance-criteria section; a plan, a test or a
  change request links to them, because a second copy drifts into a second source of truth.
- **GA2** — Give every scenario a stable id (AC-1, AC-2, …) and keep it unchanged once the spec is approved; a
  renumbering is a spec change, because a rewording breaks every reference to a title-only scenario.
- **GA3** — Tag a scenario by domain or concern (`@payments`, `@security`), never by test level (`@unit`, `@integration`,
  `@e2e`), because a test-level tag decides the test level before the writer of the tests can.
- **GA4** — Name exactly the Scenario Outline's `<placeholders>` in its Examples header, and write preconditions that
  several scenarios share once as `Background:`, because no Gherkin parser catches a header that misses a placeholder.
- **GA5** — Give every scenario at least one Then that states an observable outcome, and every acceptance criterion at
  least one failure or refusal scenario, because a Then that no running test can check proves nothing.
- **GA6** — Title every scenario as a plain behaviour sentence that starts with "should …", because the title becomes
  the test name, and a statement title cannot become a test name without rewording.
- **CV1** — Write a scenario's id as a `# AC-n` line directly above `Scenario:`, never a tag or title text,
  because an id tag breaks GA3 and an id in the title breaks the test name.
- **AC7** — When a change alters stored data or a default, give one scenario or more a Given with pre-change state (an old
  row, an unset key), because new-row scenarios test the default, not the migration.
- **AC8** — Move an Examples column whose value is the same on every row into `Background:` or the Given, because a
  constant column is noise that is copied into every test table.
- **AC9** — Use terms from the glossary and related specs in scenario text, and define a new noun in the spec first,
  because the title becomes the test name, so a wrong word reaches the code.
- **AC10** — Treat an edit to acceptance-criteria text after the approval gate as a spec change: record it on the change
  request and pass the gate again, because an approval covers only the text it saw.
- **AC12** — Write a bug's spec in three parts: current behaviour, expected behaviour and behaviour that must not
  change, because a fix that names no unchanged behaviour can break it unseen.

## When X, use Y

| the acceptance criteria have | use | why |
|---|---|---|
| a home | the spec's acceptance-criteria section; everything else links there (GA1) | the spec holds the testable success conditions |
| a scenario that needs an id | a `# AC-n` comment line above `Scenario:`, unchanged after approval (GA2, CV1) | each requirement carries a unique id; a Gherkin comment is a full line of its own |
| a scenario that needs a tag | a domain or concern tag, never a test level (GA3) | tags group related features; a test-level tag decides the test level before the writer of the tests can |
| a Given that several scenarios repeat | `Background:` (GA4) | `Background:` states shared preconditions once |
| a `Scenario Outline` | an Examples header that names exactly its placeholders (GA4); a constant column moved to the Given (AC8) | no Gherkin parser catches a header that misses a placeholder |
| a Then step | an outcome a user or caller can observe (GA5) | a Then that no running test can check proves nothing |
| an acceptance criterion with only success scenarios | one more scenario for its failure or refusal path (GA5) | a criterion tested only on success leaves its failure path unproven |
| a scenario title | a "should …" sentence about behaviour (GA6) | test names read as sentences; describe behaviour, not implementation |
| a change to stored data or a default | a Given with state from before the change (AC7) | existing rows need a backfill |
| a noun in scenario text | the glossary's word; a new noun defined in the spec first (AC9) | one shared, ubiquitous language; the title becomes the test name, so a wrong word reaches the code |
| an edit to approved acceptance-criteria text | a spec change that passes the approval gate again (AC10) | an approval covers only the text as it stood when it was approved |
| a bug | three parts: current, expected, and must not change (AC12) | the third part keeps the fix from breaking what works |

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### GA3 — Tag by domain or concern, never by test level

**Bad**
```gherkin
# AC-4
@integration-test @business-rule @error
Scenario: should keep a shipped order shipped when the customer tries to cancel it
  Given a customer has a shipped order
  When the customer tries to cancel the order
  Then the order remains shipped
```
The tag picks the test level inside the spec. The writer of the tests can no longer choose it.

**Good**
```gherkin
# AC-4
@orders
Scenario: should keep a shipped order shipped when the customer tries to cancel it
  Given a customer has a shipped order
  When the customer tries to cancel the order
  Then the order remains shipped
```
The tag names the domain. The test level stays open.

### GA4 — The Examples header names exactly the placeholders

**Bad**
```gherkin
# AC-2
@payments
Scenario Outline: should set the order status from the payment result
  Given an order total of <amount>
  When the payment result is <result>
  Then the order status is <status>

  Examples:
    | total | result   |
    | 25.00 | approved |
```
`<amount>` and `<status>` have no column. No parser reports it.

**Good**
```gherkin
# AC-2
@payments
Scenario Outline: should set the order status from the payment result
  Given an order total of <total>
  When the payment result is <result>
  Then the order status is <status>

  Examples:
    | total | result   | status    |
    | 25.00 | approved | confirmed |
    | 25.00 | declined | unpaid    |
    |  0.00 | skipped  | confirmed |
```

### GA5 — An observable Then, and a failure scenario

**Bad**
```gherkin
# AC-3
@payments
Scenario: should keep the order unpaid when the card is declined
  Given: the controller receives request 42
  When: PaymentServiceImpl calls the gateway
  Then: OrderRepository.save is invoked once
```
Each step names code, not an outcome. No customer can see it.

**Good**
```gherkin
# AC-3
@payments
Scenario: should keep the order unpaid when the card is declined
  Given a customer has an unpaid order
  And the selected card will be declined
  When the customer submits the payment
  Then the order remains unpaid
  But the customer can choose another payment method
```
This is the refusal scenario of the payment criterion. Each Then is an outcome the customer sees.

### GA6 — The title is a "should …" behaviour sentence

**Bad**
```gherkin
# AC-9
@returns
Scenario: Refund calculation for partial returns
  Given a customer returns 1 of the 3 items of an order
  When the return is accepted
  Then the customer gets the price of 1 item back
```
A topic, not a behaviour. The test name must reword it.

**Good**
```gherkin
# AC-9
@returns
Scenario: should refund only the returned items of a partial return
  Given a customer returns 1 of the 3 items of an order
  When the return is accepted
  Then the customer gets the price of 1 item back
```

### CV1 — The id is a comment line above the scenario

**Bad**
```gherkin
@AC-5 @orders
Scenario: AC-5 should cancel an unpaid order on request
```
The id tag breaks GA3. The id in the title changes the test name.

**Good**
```gherkin
# AC-5
@orders
Scenario: should cancel an unpaid order on request
  Given a customer has an unpaid order
  When the customer cancels the order
  Then the order status is cancelled
```

### AC7 — A Given with state from before the change

**Bad**
```gherkin
# AC-6
@orders
Scenario: should give a new order the default delivery window of 3 days
  Given the customer places an order today
  Then the order has a delivery window of 3 days
```
Only new orders. The orders that existed before the new column are never checked.

**Good**
```gherkin
# AC-7
@orders
Scenario: should give an order placed before the change the default delivery window of 3 days
  Given an order that was stored before the delivery window existed
  When the customer opens the order
  Then the order has a delivery window of 3 days
```

### AC8 — A constant column moves to the Given

**Bad**
```gherkin
  Examples:
    | currency | total  | fee  |
    | EUR      | 10.00  | 0.50 |
    | EUR      | 100.00 | 1.00 |
```
`currency` is the same on every row. It is copied into every test table.

**Good**
```gherkin
# AC-8
@payments
Scenario Outline: should charge a card fee that grows with the order total
  Given the shop currency is EUR
  When an order of <total> is paid by card
  Then the card fee is <fee>

  Examples:
    | total  | fee  |
    | 10.00  | 0.50 |
    | 100.00 | 1.00 |
```

### AC9 — Glossary words in scenario text

**Bad**
```gherkin
# AC-10
@orders
Scenario: should void the basket when the shopper bails at checkout
  Given a shopper has a basket at checkout
  When the shopper leaves the checkout
  Then the basket is void
```
The glossary says "order" and "customer". "Basket", "shopper" and "void" reach the test name.

**Good**
```gherkin
# AC-10
@orders
Scenario: should cancel the order when the customer leaves the checkout
  Given a customer has an order at checkout
  When the customer leaves the checkout
  Then the order status is cancelled
```

## Decided edges

- **Skip when** a scenario has no tag at all: GA3 asks for no tag. — **Do not skip when** a tag names a test level,
  even when an outside guide tags test levels. — **Confidence** high
- **Skip when** a Then has an And or a But: GA5 asks for at least one observable Then, not exactly one. — **Do not
  skip when** any Then names a method, a class or a table instead of an outcome. — **Confidence** high
- **Skip when** the failure path of an acceptance criterion is in a sibling scenario under the same criterion (GA5). —
  **Do not skip when** no scenario of the criterion covers a failure or a refusal. — **Confidence** medium
- **Skip when** the change adds a new table with no rows before the change: AC7 has no old state. — **Do not skip
  when** the change adds a column, changes a default or changes a stored value. — **Confidence** high
- **Skip when** an edit after the approval gate changes only whitespace or a typo that keeps the meaning. — **Do not
  skip when** the edit changes a value, a step, a title or an id (AC10, GA2). — **Confidence** medium

## Review checks

Walk every scenario in the spec's acceptance-criteria section that the change adds or edits.

- [ ] GA1 — Acceptance criteria written outside the spec (a plan, a change request, a `.feature` file) are a finding.
- [ ] GA2 — A scenario without an id, or an approved id that changed, is a finding.
- [ ] GA3 — A tag that names a test level is a finding.
- [ ] GA4 — Compare each Outline's placeholders with its Examples header. A difference is a finding, and so is a Given
  repeated in several scenarios outside `Background:`.
- [ ] GA5 — A scenario with no observable Then is a finding, and so is an acceptance criterion with no failure or
  refusal scenario.
- [ ] GA6 — A title that does not start with "should" or that names no behaviour is a finding.
- [ ] CV1 — An id that is not a `# AC-n` line directly above `Scenario:` is a finding.
- [ ] AC7 — Open the change. When it alters stored data or a default, a criterion with no pre-change Given is a finding.
- [ ] AC8 — An Examples column with one value on every row is a finding.
- [ ] AC9 — A noun not in the glossary, a related spec or this spec's own definitions is a finding.
- [ ] AC10 — Compare the acceptance-criteria text with the approved version. A changed text with no new approval is a
  finding.
- [ ] AC12 — For a bug, find the current, expected and must-not-change behaviour. Each part missing is a finding.
