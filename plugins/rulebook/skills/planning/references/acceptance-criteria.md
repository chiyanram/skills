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

## When X, use Y

| the acceptance criteria have | use | why |
|---|---|---|
| a home | the spec's acceptance-criteria section; everything else links there (GA1) | the spec holds the testable success conditions (addy-sdd :143; spec-kit §User Scenarios & Testing; humanlayer-plan :225) |
| a scenario that needs an id | a `# AC-n` comment line above `Scenario:`, unchanged after approval (GA2, CV1) | each requirement carries a unique id (spec-kit §Functional Requirements; sysml); a comment is a full line of its own (cucumber-ref §Comments) |
| a scenario that needs a tag | a domain or concern tag, never a test level (GA3) | tags group related features (cucumber-ref §Tags); plinth-bdd :266 tags a test level, and this rulebook overrides it |
| a Given that several scenarios repeat | `Background:` (GA4) | cucumber-ref §Background |
| a `Scenario Outline` | an Examples header that names exactly its placeholders (GA4); a constant column moved to the Given (AC8) | plinth-bdd :149; cucumber-ref §Scenario Outline |
| a Then step | an outcome a user or caller can observe (GA5) | cucumber-ref §Steps; plinth-bdd :32 |
| an acceptance criterion with only success scenarios | one more scenario for its failure or refusal path (GA5) | spec-kit §Edge Cases; plinth-unit :25 |
| a scenario title | a "should …" sentence about behaviour (GA6) | test names read as sentences (north §agiledox); describe behaviour, not implementation (better-gherkin §Declarative) |
| a change to stored data or a default | a Given with state from before the change (AC7) | existing rows need a backfill (addy-migration :179) |
| a noun in scenario text | the glossary's word; a new noun defined in the spec first (AC9) | to-spec :13; a ubiquitous language (north §BDD for analysis) |
| an edit to approved acceptance-criteria text | a spec change that passes the approval gate again (AC10) | update the spec first, then implement (addy-sdd :214) |

`addy-sdd` is addyosmani `skills/spec-driven-development/SKILL.md` and `addy-migration` is addyosmani
`skills/deprecation-and-migration/SKILL.md`. `humanlayer-plan` is humanlayer `.claude/commands/create_plan.md`.
`to-spec` is mattpocock `skills/engineering/to-spec/SKILL.md`. `plinth-bdd` is jabrena plinth
`skills/058-design-bdd/references/058-design-bdd.md` and `plinth-unit` is its `131-java-testing-unit-testing.md`.
`spec-kit` is github/spec-kit `templates/spec-template.md`. `cucumber-ref` is cucumber.io/docs/gherkin/reference and
`better-gherkin` is cucumber.io/docs/bdd/better-gherkin. `north` is Dan North, "Introducing BDD"
(dannorth.net/blog/introducing-bdd). `sysml` is OMG issue SYSML16-204, which quotes "The unique Id of the requirement"
from SysML 1.6. `:N` is the line.

Operator preference, 2026-10-31 (SRC2), in whole or in part: GA2, GA3, GA6, CV1, AC7, AC8, AC9 and AC10.

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### GA3 — Tag by domain or concern, never by test level

**Bad** (adapted from plinth-bdd :266-270)
```gherkin
# AC-4
@integration-test @business-rule @error
Scenario: should keep a shipped order shipped when the customer tries to cancel it
  Given a customer has a shipped order
  When the customer tries to cancel the order
  Then the order remains shipped
```
The tag picks the test level inside the spec. The writer of the tests can no longer choose it.

**Good** (neutral)
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

**Bad** (adapted from plinth-bdd :169-176)
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

**Good** (neutral, adapted from plinth-bdd :154-164)
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

**Bad** (adapted from plinth-bdd :104-107)
```gherkin
# AC-3
@payments
Scenario: should keep the order unpaid when the card is declined
  Given: the controller receives request 42
  When: PaymentServiceImpl calls the gateway
  Then: OrderRepository.save is invoked once
```
Each step names code, not an outcome. No customer can see it.

**Good** (neutral, adapted from plinth-bdd :93-99)
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

**Bad** (neutral)
```gherkin
# AC-9
@returns
Scenario: Refund calculation for partial returns
  Given a customer returns 1 of the 3 items of an order
  When the return is accepted
  Then the customer gets the price of 1 item back
```
A topic, not a behaviour. The test name must reword it.

**Good** (neutral)
```gherkin
# AC-9
@returns
Scenario: should refund only the returned items of a partial return
  Given a customer returns 1 of the 3 items of an order
  When the return is accepted
  Then the customer gets the price of 1 item back
```

### CV1 — The id is a comment line above the scenario

**Bad** (neutral)
```gherkin
@AC-5 @orders
Scenario: AC-5 should cancel an unpaid order on request
```
The id tag breaks GA3. The id in the title changes the test name.

**Good** (neutral)
```gherkin
# AC-5
@orders
Scenario: should cancel an unpaid order on request
  Given a customer has an unpaid order
  When the customer cancels the order
  Then the order status is cancelled
```

### AC7 — A Given with state from before the change

**Bad** (neutral)
```gherkin
# AC-6
@orders
Scenario: should give a new order the default delivery window of 3 days
  Given the customer places an order today
  Then the order has a delivery window of 3 days
```
Only new orders. The orders that existed before the new column are never checked.

**Good** (neutral)
```gherkin
# AC-7
@orders
Scenario: should give an order placed before the change the default delivery window of 3 days
  Given an order that was stored before the delivery window existed
  When the customer opens the order
  Then the order has a delivery window of 3 days
```

### AC8 — A constant column moves to the Given

**Bad** (neutral)
```gherkin
  Examples:
    | currency | total  | fee  |
    | EUR      | 10.00  | 0.50 |
    | EUR      | 100.00 | 1.00 |
```
`currency` is the same on every row. It is copied into every test table.

**Good** (neutral)
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

**Bad** (neutral)
```gherkin
# AC-10
@orders
Scenario: should void the basket when the shopper bails at checkout
  Given a shopper has a basket at checkout
  When the shopper leaves the checkout
  Then the basket is void
```
The glossary says "order" and "customer". "Basket", "shopper" and "void" reach the test name.

**Good** (neutral)
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
  even when an outside source tags test levels (plinth-bdd :266). — **Confidence** high
- **Skip when** a Then has an And or a But: GA5 asks for at least one observable Then, not exactly one (plinth-bdd
  :93-99). — **Do not skip when** any Then names a method, a class or a table instead of an outcome. — **Confidence**
  high
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
