# Boundaries

Which boundary cases a test file needs for each input its logic takes. Read it when you write or review tests for
logic that takes a number, a collection, a formatted string, an enum or sealed set, a time value or an optional input.

Contents: Rules · When X, use Y · Good / Bad (B1, B2, B3) · Decided edges · Review checks

## Rules

- **B1** — For each input a piece of logic accepts, check every CORRECT boundary — Conformance, Ordering, Range,
  Reference, Existence, Cardinality, Time — because with only one item a correct and an inverted offset both pass.
- **B2** — In the test file, give each applicable CORRECT letter at least one case or a `skip: <letter> — <reason>`
  line, because 'consider boundaries' let -1, 1 and null inputs go untested past review.
- **B3** — For a Range, test just inside and just outside each edge, not only the edge (1..10 → 0, 1, 10, 11),
  because testing only one side of an edge lets an off-by-one comparison pass.

## When X, use Y

Each row maps an input to the letter it triggers and the cases to write. The first five rows are the B2 triggers:
logic that takes one of them gets a case or a skip line for each letter (B2).

| the logic takes | use | why |
|---|---|---|
| a number | Range: each bound, and just below and just above it | testing only one side of an edge lets an off-by-one comparison pass (B3) · plinth :94 |
| a collection | Cardinality: 0, 1 and many items · Ordering: sorted: assert exact order; unordered: assert without order | with only one item a correct and an inverted offset both pass (B1) · plinth :176 · ordering tests match the contract (plinth :67) |
| a string with a format, an enum or a sealed set | Conformance: one valid and one invalid value; assert the domain error | the assertion checks the domain error, not only a generic failure (plinth :42) |
| a time value | Time: before, at and after the cut-off, from a controllable time source | plinth :211 |
| an optional or nullable input | Existence: null, blank and empty; `Optional.empty()`; a missing record | null, blank and empty have distinct domain meanings (plinth :149) |
| an id it looks up, or a dependency it calls | Reference: the record is missing; for an unavailable dependency, see C2 (`coverage-design.md`) | the missing referenced entity is tested (plinth :119) |

Plinth is `130-java-testing-strategies-correct.md`, the CORRECT source of B1; `:N` is its line.

## Good / Bad

### B1 — Check every CORRECT boundary for each input

**Bad** (neutral)
```groovy
    def "should record the invoice's paid amount"() {
        when: "a payment of 30.00 EUR is allocated to one open invoice of 20.00 EUR"
        def paid = allocator.allocate(payment("30.00"), invoicesDue([5]))

        then: "the invoice is paid in full"
        paid*.amount() == [eur("20.00")]
    }
```
Cardinality 1 only. With one invoice the remainder always starts full, so oldest-first and newest-first both pass.

**Good** (neutral)
```groovy
    def "should pay the oldest invoices first when a payment covers #scenario"() {
        when: "a payment of 30.00 EUR is allocated across open invoices of 20.00 EUR each"
        def paid = allocator.allocate(payment("30.00"), invoicesDue(dueInDays))

        then: "each invoice gets what remains after the ones due sooner"
        paid*.amount() == expected.collect { eur(it) }

        where:
        scenario                 | dueInDays || expected
        "no invoice"             | []        || []
        "one invoice"            | [5]       || ["20.00"]
        "two, sooner one last"   | [9, 2]    || ["10.00", "20.00"]
        "three, the last unpaid" | [1, 2, 3] || ["20.00", "10.00", "0.00"]
    }
```
Cardinality 0, 1 and many, with Ordering reversed in one row, so a wrong allocation order fails. (Real evidence:
ledger row B1.)

### B2 — One case or one skip line per CORRECT letter

**Bad** (neutral)
```java
    void parse_valid_import_returns_lines() {
    void parse_null_returns_empty() {
    void parse_blank_returns_empty() {
    void parse_invalid_sku_throws() {
    void parse_non_numeric_quantity_throws() {
    void parse_exceeds_max_lines_throws() {
    void parse_quantity_exceeding_99_throws() {
    void parse_total_exceeds_10000_eur_throws() {
    void parse_invalid_currency_code_throws(String currency) {
```
Range is tried only from outside, and Cardinality only past the limit. No line says why Ordering, Reference and Time
are skipped.

**Good** (neutral)
```groovy
/**
 * CORRECT for parse: Conformance (SKU pattern, numeric quantity, ISO currency) · Range (quantity 1..99,
 * total ≤ 10 000 EUR) · Existence (null, blank) · Cardinality (0, 1, 50 lines accepted; 51 refused).
 * skip: Ordering — no rule reads line order · Reference, Time — no lookup and no clock.
 */
class OrderImportParserSpec extends Specification {

    def "should keep every line of an import carrying #count of them"() {
        expect: "up to the limit, nothing is dropped"
        OrderImportParser.parse(importOf(count)).size() == count

        where:
        count << [0, 1, 50]
    }
```
The header names every letter, covered or skipped with a reason. Cardinality runs 0, 1 and the edge 50. (Real
evidence: ledger row B2.)

### B3 — Test just inside and just outside each edge

**Bad** (neutral)
```java
    @Test
    void parse_quantity_exceeding_99_throws() {
        String header = "sku;quantity;unitPrice;currency";
        String row = "SKU-1;100;9.99;EUR";
        String csv  = header + "\n" + row;
        assertThatThrownBy(() -> OrderImportParser.parse(csv))
            .isInstanceOf(OrderException.class)
            .hasMessageContaining("99");
    }
```
Only 100 is tried. 99 is never shown to pass, so an off-by-one `>=` passes too.

**Good** (neutral)
```groovy
    def "should accept an import line with a quantity of exactly 99"() {
        expect: "the limit itself is inside the range"
        OrderImportParser.parse(importLine("SKU-1", 99)).first().quantity() == 99
    }

    def "should refuse an import line with a quantity of 100"() {
        when: "the quantity is one past the per-line limit"
        OrderImportParser.parse(importLine("SKU-1", 100))

        then: "the refusal names the limit it broke"
        def e = thrown(OrderException)
        e.message.contains("max 99 per line")
    }
```
The edge (99, accepted) and one past it (100, refused) each get a case, so `>` versus `>=` is decided. (Real
evidence: ledger row B3.)

## Decided edges

- **Skip when** the logic has no rule that reads the letter: no clock, no lookup, no rule on order. Write the
  `skip: <letter> — <reason>` line (B2). — **Do not skip when** the reason is left out: a bare skip cannot be told
  from a forgotten letter. — **Confidence** high
- **Do not skip when** a property test covers the same input: the CORRECT examples stay beside it (P2,
  `property-based.md`). — **Confidence** high

## Review checks

Walk every changed test file whose logic takes an input from the first five rows of When X, use Y.

- [ ] B1, B2 — For each such input, find a case or a `skip: <letter> — <reason>` line for each of the seven
  letters (`grep -n "skip:"`). The input's table row gives the minimum cases. A letter with neither, or a skip
  with no reason, is a finding.
- [ ] B3 — For each Range, find two values per edge: the last one inside and the first one outside. A Range tested
  from one side only is a finding.
