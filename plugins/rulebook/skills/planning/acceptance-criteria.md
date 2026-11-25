# Acceptance criteria

How a ticket's acceptance criteria are written in its spec as numbered AC-n lines: home, numbers, outcomes, failure
paths, tables and words. Read it when you write or review the acceptance criteria of a spec. How each AC becomes its
tests is owned by the `testing` skill.

## Rules

- Write a ticket's ACs only in its spec's acceptance-criteria section, as numbered lines. A design, a test or a PR
  links to them, because a second copy drifts into a second source of truth.
- Put each AC on its own line, `AC-n — should <outcome> when <trigger>`, and keep its number after approval: a removed
  AC leaves its number unused, because a test or evidence row that cites AC-n would then name the wrong criterion.
- Write an AC that holds for several inputs as one AC-n line and a table under it, input columns then the expected
  result, one row per case, because a list of near-identical ACs hides the case that differs. Cases that differ in
  more than input and result, such as a refusal with its own message, are separate ACs.
- Move a table column whose value is the same on every row into the AC line, because a constant column is copied into
  every test table.
- Write each AC as one outcome a user or caller can observe (a status, a response, a message, stored state), naming no
  class, method, table or test level, because an AC no test can fail proves nothing. A second visible effect of the
  same event ("keep the order unpaid and offer another payment method") is still one outcome.
- Give each behaviour an AC for its failure or refusal, in its own line or a sibling's, because a behaviour tested only
  on success leaves its failure path unproven.
- Write each AC's text as a "should …" behaviour sentence, "should X when Y", so the test name is that text word for
  word, because a statement cannot become a test name without rewording.
- When a change alters stored data or a default, start at least one AC from a state before the change (an old row, an
  unset key), because ACs on new rows test the default, not the migration. A new table with no rows has no old state.
- Use the glossary's words and those of related specs in AC text, and define a new noun in the spec first, because the
  AC text becomes the test name, so a wrong word reaches the code.
- Treat an edit to AC text after approval as a spec change: record it on the change request and pass the approval
  again, because an approval covers only the text it saw. A whitespace or typo edit that keeps the meaning is not one.
- Write a bug's spec in three parts: current behaviour, expected behaviour, and behaviour that must not change,
  because a fix that names no unchanged behaviour can break it unseen.
- End a feature or one-way-door spec with "How we will know it worked: <lever>, read at <where>, on <when>", or
  "none: <why>", because a feature with no read-back point is never checked. A lever is a product metric, adoption, a
  benchmark, an error-rate or latency target, or a person's read on the date. Other lanes leave the line out, because
  a lever made up for a small change is read as a promise.

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### One numbered line per AC, never renumbered

**Bad**
```text
Approved:     AC-1 — should cancel an unpaid order on request
              AC-2 — should keep a shipped order shipped when the customer tries to cancel it
After review: AC-1 — should keep a shipped order shipped when the customer tries to cancel it
```
An approved AC was removed and the next one took its number. The test and evidence row for AC-1 now name the wrong
criterion.

**Good**
```text
AC-2 — should keep a shipped order shipped when the customer tries to cancel it
```
AC-1 is removed through a spec change, and AC-2 keeps its number. Each number stays where tests cite it.

### Several inputs: one AC and a table

**Bad**
```text
AC-2 — should confirm an order of 25.00 when the payment is approved
AC-3 — should keep an order of 25.00 unpaid when the payment is declined
AC-4 — should confirm an order of 0.00 when the payment is skipped
```
Three lines differ only in values. A reader must diff them to see which case differs.

**Good**
```text
AC-2 — should set the order status from the payment result
  | total | result   | status    |
  | 25.00 | approved | confirmed |
  | 25.00 | declined | unpaid    |
  |  0.00 | skipped  | confirmed |
```
One AC, one row per case. The declined row stands out.

### An observable outcome, and a failure AC

**Bad**
```text
AC-3 — should call PaymentServiceImpl, which calls OrderRepository.save once (integration test)
```
It names classes and a test level, not an outcome. No customer can see it, and the payment has no failure AC.

**Good**
```text
AC-3 — should confirm the order when the card payment is approved
AC-4 — should keep the order unpaid and offer another payment method when the card is declined
```
Each AC is an outcome the customer sees. AC-4 is the refusal path of the payment.

### The AC text is a "should …" behaviour sentence

**Bad**
```text
AC-9 — Refund calculation for partial returns
```
A topic, not a behaviour. The test name must reword it.

**Good**
```text
AC-9 — should refund only the returned items when the customer returns part of an order
```
The text is the test name, word for word. The "when" part names the trigger.

### An AC that starts from state from before the change

**Bad**
```text
AC-6 — should give a new order the default delivery window of 3 days
```
Only new orders. The orders that existed before the new column are never checked.

**Good**
```text
AC-7 — should give an order stored before the delivery window existed the default delivery window of 3 days
```
The starting state is an old row, so the migration's default is tested.

### A constant column moves into the AC line

**Bad**
```text
AC-8 — should charge a card fee that grows with the order total
  | currency | total  | fee  |
  | EUR      | 10.00  | 0.50 |
  | EUR      | 100.00 | 1.00 |
```
`currency` is the same on every row. It is copied into every test table.

**Good**
```text
AC-8 — should charge a card fee in EUR that grows with the order total
  | total  | fee  |
  | 10.00  | 0.50 |
  | 100.00 | 1.00 |
```
The currency sits in the AC line once, and the table holds only what changes.

### Glossary words in AC text

**Bad**
```text
AC-10 — should void the basket when the shopper bails at checkout
```
The glossary says "order" and "customer". "Basket", "shopper" and "void" reach the test name.

**Good**
```text
AC-10 — should cancel the order when the customer leaves the checkout
```
Every noun is the glossary's, so the test name uses the project's words.

## Review

Walk every AC in the spec's acceptance-criteria section that the change adds or edits.

Each line is a finding, a blocker unless marked (warning).

- Acceptance criteria written outside the spec: a design, a change request, a `.feature` file.
- An AC that is not its own `AC-n` line, or an approved number that changed or was reused.
- Two ACs or more that differ only in values, or a table with no expected-result column.
- A table column with one value on every row.
- An AC with no observable outcome, or one that names a class, method, table or test level.
- A behaviour with no failure or refusal AC among its ACs.
- AC text that does not start with "should" or names no behaviour.
- A change to stored data or a default whose ACs all start from new state.
- A noun not in the glossary, a related spec or this spec's own definitions.
- AC text changed after approval with no new approval.
- A bug spec missing its current, expected or must-not-change part.
- (warning) A feature or one-way-door spec with no "How we will know it worked" line, or a lever with no place or no
  date to read it.
