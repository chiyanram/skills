# Acceptance criteria

How a ticket's acceptance criteria are written in its spec as numbered AC-n lines: home, ids, outcomes, failure
paths, tables and words. Read it when you write or review the acceptance criteria of a spec.

Contents: Rules · When X, use Y · Good / Bad (GA2, GA4–GA6, AC7–AC9) · Decided edges · Review checks

## Rules

How each AC becomes its tests is owned by `testing/references/scenario-to-tests.md` (GT1, GT3–GT6).

- **GA1** — Write a ticket's ACs only in its spec's acceptance-criteria section, as numbered lines; a design, a test or
  a PR links to them, because a second copy drifts into a second source of truth.
- **GA2** — Number each AC on its own line (AC-1, AC-2, …) and never renumber one after approval, because a test or
  evidence row that cites AC-n then names the wrong criterion.
- **GA4** — Write an AC that holds for several inputs as one AC-n line and a table of input and expected result, one
  row per case, because a list of near-identical ACs hides the case that differs.
- **GA5** — Write each AC as one observable outcome that names no class or test level, and give each behaviour an AC
  for its failure or refusal, because an AC no test can fail proves nothing.
- **GA6** — Write each AC's text as a "should …" behaviour sentence, standard form "should X when Y", so the test
  name is that text verbatim (GT1), because a statement cannot become a test name without rewording.
- **AC7** — When a change alters stored data or a default, give one AC or more a pre-change starting state
  (an old row, an unset key), because new-row ACs test the default, not the migration.
- **AC8** — Move a GA4 table column whose value is the same on every row into the AC line, because a constant column
  is noise that is copied into every test table.
- **AC9** — Use terms from the glossary and related specs in AC text, and define a new noun in the spec first, because
  the AC text becomes the test name, so a wrong word reaches the code.
- **AC10** — Treat an edit to acceptance-criteria text after the approval gate as a spec change: record it on the change
  request and pass the gate again, because an approval covers only the text it saw.
- **AC12** — Write a bug's spec in three parts: current behaviour, expected behaviour and behaviour that must not
  change, because a fix that names no unchanged behaviour can break it unseen.

## When X, use Y

| the acceptance criteria have | use | why |
|---|---|---|
| a home | the spec's acceptance-criteria section; everything else links there (GA1) | the spec holds the testable success conditions |
| an AC | one line, `AC-n — should <outcome> when <trigger>`, numbered once and never renumbered after approval (GA2, GA6) | a test or evidence row cites the number, and the trigger has a place |
| an AC that holds for several inputs | one AC-n line and a table under it: input columns, then the expected result (GA4) | the case that differs shows as one row |
| a value that is the same in every row | that value in the AC line, not a column (AC8) | a constant column is copied into every test table |
| an outcome | what a user or caller can observe: a status, a response, a message, stored state (GA5) | an AC that no running test can check proves nothing |
| an AC with only a success path | one more AC for its failure or refusal path (GA5) | a behaviour tested only on success leaves its failure path unproven |
| a test level or a class name in an AC | the outcome instead; the test level is S1's call (`testing/strategy.md`) (GA5) | an AC that picks the test level decides it before the tests are written |
| an AC's text | a "should …" sentence about behaviour, in the standard form "should X when Y" (GA6) | the text becomes the test name |
| a change to stored data or a default | an AC that starts from state from before the change (AC7) | existing rows need a backfill |
| a noun in AC text | the glossary's word; a new noun defined in the spec first (AC9) | one shared, ubiquitous language; the AC text becomes the test name, so a wrong word reaches the code |
| an edit to approved acceptance-criteria text | a spec change that passes the approval gate again (AC10) | an approval covers only the text as it stood when it was approved |
| a bug | three parts: current, expected, and must not change (AC12) | the third part keeps the fix from breaking what works |

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### GA2 — One numbered line per AC, never renumbered

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
AC-1 is removed through a spec change (AC10), and AC-2 keeps its number. Each number stays where tests cite it.

### GA4 — Several inputs: one AC and a table

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

### GA5 — An observable outcome, and a failure AC

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

### GA6 — The AC text is a "should …" behaviour sentence

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

### AC7 — An AC that starts from state from before the change

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

### AC8 — A constant column moves into the AC line

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

### AC9 — Glossary words in AC text

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

## Decided edges

- **Skip when** an AC names a second visible effect of the same event ("keep the order unpaid and offer another
  payment method"): it is still one outcome (GA5). — **Do not skip when** any part names a method, a class, a table
  or a test level. — **Confidence** high
- **Skip when** the failure path of a behaviour is in a sibling AC (GA5). — **Do not skip when** no AC of the
  behaviour covers a failure or a refusal. — **Confidence** medium
- **Skip the table when** the cases differ in more than input and expected result, such as a refusal with its own
  message: write separate ACs. — **Do not skip when** the ACs differ only in values (GA4). — **Confidence** medium
- **Skip when** the change adds a new table with no rows before the change: AC7 has no old state. — **Do not skip
  when** the change adds a column, changes a default or changes a stored value. — **Confidence** high
- **Skip when** an edit after the approval gate changes only whitespace or a typo that keeps the meaning. — **Do not
  skip when** the edit changes a value, a table row, the text or a number (AC10, GA2). — **Confidence** medium

## Review checks

Walk every AC in the spec's acceptance-criteria section that the change adds or edits.

- [ ] GA1 — Acceptance criteria written outside the spec (a design, a change request, a `.feature` file) are a
  finding.
  Applies when: the change adds or edits acceptance criteria.
  Evidence: the file and line where the criteria are written outside the spec.
  Not a finding: none
  Severity: blocker
  Verify: re-open that file and confirm it holds the criterion text, not a link.
- [ ] GA2 — An AC that is not its own `AC-n` line, or an approved number that changed or was reused, is a finding.
  Applies when: the change adds or edits an AC.
  Evidence: the AC line, and the old and new number when a number changed.
  Not a finding: none
  Severity: blocker
  Verify: re-open the AC, and the approved spec for a changed number.
- [ ] GA4 — Two ACs or more that differ only in values, or a table with no expected-result column, are a finding.
  Applies when: the change adds or edits two ACs or more with the same text apart from values, or a table under an AC.
  Evidence: the ACs side by side, or the table header.
  Not a finding: cases that differ in more than input and expected result (decided edge).
  Severity: blocker
  Verify: re-open the ACs or the table.
- [ ] GA5 — An AC with no observable outcome, or one that names a class or a test level, is a finding, and so is a
  behaviour with no failure or refusal AC.
  Applies when: the change adds or edits an AC.
  Evidence: the AC line, quoted, or the behaviour and its list of ACs.
  Not a finding: a second visible effect of the same event; a failure path in a sibling AC (decided edges).
  Severity: blocker
  Verify: re-open every AC of the behaviour, siblings included.
- [ ] GA6 — AC text that does not start with "should" or that names no behaviour is a finding.
  Applies when: the change adds or edits AC text.
  Evidence: the AC line, quoted.
  Not a finding: none
  Severity: blocker
  Verify: re-open the AC line.
- [ ] AC7 — Open the change. When it alters stored data or a default, an AC set with no pre-change starting state is a
  finding.
  Applies when: the change alters stored data or a default.
  Evidence: the stored data or default that changes, and the ACs' starting states.
  Not a finding: a new table with no rows before the change (decided edge).
  Severity: blocker
  Verify: re-open the change to the data or default, and the ACs.
- [ ] AC8 — A table column with one value on every row is a finding.
  Applies when: the change adds or edits a table under an AC.
  Evidence: the column header and its one value.
  Not a finding: none
  Severity: blocker
  Verify: re-open the table.
- [ ] AC9 — A noun not in the glossary, a related spec or this spec's own definitions is a finding.
  Applies when: the change adds or edits AC text.
  Evidence: the noun, the AC line, and where you looked for it.
  Not a finding: none
  Severity: blocker
  Verify: search the glossary, the related specs and this spec for the noun again.
- [ ] AC10 — Compare the acceptance-criteria text with the approved version. A changed text with no new approval is a
  finding.
  Applies when: the spec has passed the approval gate.
  Evidence: the old and new text, and the change request with no new approval.
  Not a finding: a whitespace or typo edit that keeps the meaning (decided edge).
  Severity: blocker
  Verify: re-open the approved version and the change request.
- [ ] AC12 — For a bug, find the current, expected and must-not-change behaviour. Each part missing is a finding.
  Applies when: the ticket is a bug.
  Evidence: the spec's sections, and which part is missing.
  Not a finding: none
  Severity: blocker
  Verify: re-open the bug spec.
