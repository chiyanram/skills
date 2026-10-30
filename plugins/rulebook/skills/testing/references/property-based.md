# Property-based

When a rule gets a property test, and how its generators, seeds and runs are set up. Read it when you write or review
a property test, a generator, or a requirement that says "for any input".

Contents: Rules · When X, use Y · Good / Bad (P1, P2, P3, P4, P6, P7, P8, P10) · Decided edges · Review checks

## Rules

- **P1** — Write a property when the requirement says "for any input" (invariant, round-trip, idempotence, oracle,
  metamorphic); otherwise write examples, because one example leaves a 'for any input' rule unchecked for other inputs.
- **P2** — Keep the CORRECT and just-inside/just-outside cases (B1–B3, `boundaries.md`) as example tests beside the
  property, which complements them, because its generators may never produce the named edge, such as null.
- **P3** — In every conditional property, count which branch each case hits and fail if a branch is never reached,
  because a conditional property passed 1000 runs without once reaching its branch.
- **P4** — Seed the random source per run and print the seed on failure; replay with it, never commit a fixed seed,
  never retry a failing property, because a fixed seed explores the same cases every run.
- **P6** — Make generators include edge cases (0, 1, min, max, empty) by default; turn them off only with a written
  reason, because random draws rarely hit edges; an empty string appears about 1 in 81.
- **P7** — Run a JVM property as a unit test: in the main unit-test target, counted toward coverage, never tagged out
  of the gate, because tagged-out properties left security invariants unrun by the main gate.
- **P8** — Build generators by mapping and combining, not filtering; filter only for rare rejects and never loosen the
  discard limit to pass, because a heavy filter discards most cases and the property passes vacuously.
- **P10** — Write UI properties with fast-check, the seed printed, `numRuns` explicit and no retries, because without
  the printed seed a failing run cannot be replayed.

## When X, use Y

| situation | use | why |
|---|---|---|
| the requirement states a rule for any input: invariant, round-trip, idempotence, oracle, metamorphic | a property (P1) | one example leaves the rule unchecked for other inputs (P1) · `19:98` |
| the requirement names a case: a CORRECT letter, or a value just inside or just outside an edge | an example test, also when a property covers the same input (P2) | the generators may never produce the named edge, such as null (P2) · `19:99` |
| the property asserts only inside a branch on the generated case | a count of the cases that reach each branch, and a failure when a count is 0 (P3) | a property can pass while it never reaches its branch (P3) · `19:100` |
| the generated value must have a shape, such as a format | a generator mapped or combined from smaller generators (P8) | a heavy filter discards most cases and the property passes vacuously (P8) · `19:104` |
| the property runs in the UI (TypeScript) | fast-check with `numRuns` explicit, the seed printed, no retries (P10) | without the printed seed a failing run cannot be replayed (P10) · `19:105` |

`19` is `research/19-approved-rules.md` (the ledger); `:N` is the line.

## Good / Bad

Each pair is copied from `research/68c-neutral-testing-mutation-property-scenarios.md`; `:N` is its heading line.

### P1 — Property when the requirement says "for any input"; otherwise examples (`68c:234`)

**Bad** (neutral)
```gherkin
Scenario: No discount makes an invoice total negative
  Given any order with any number of lines
  When the GOLD discount is applied
  Then the invoice total is zero or more
```
```groovy
    def "no discount makes an invoice total negative"() {
        expect: "a GOLD customer never gets money back"
        discountPolicy.discountedTotal(orderWithQuantity(Integer.MAX_VALUE), GOLD).amount() >= 0
    }
```
The requirement says "any order", but the test checks one value.

**Good** (neutral)
```groovy
def "should leave merged order lines unchanged when they are merged again"() {
    expect: "a second merge over any list of order lines returns the first merge unchanged"
    Property.forAll(Gen.orderLines()) { lines ->
        def once = orderService.mergeLines(lines)
        assert orderService.mergeLines(once) == once
    }
}
```
Idempotence is a law for any input, so a property states it under `expect:`. The harness injects edge cases (P6)
and prints a replayable seed (P4). (Real evidence: ledger row P1.)

### P2 — A property complements its examples; boundary cases stay beside it (`68c:265`)

**Bad** (n/a) — every property has example siblings to show.

**Good** (neutral)
```groovy
def "should give a zero total for absent order lines — #lines"() {
    expect: "absent lines yield a zero total, never an error"
    invoiceService.totalOf(lines).amount() == 0.00

    where:
    lines << [null, []]
}
```
CORRECT · Existence cases stay as examples beside the property, because its generators never produce `null`. (Real
evidence: ledger row P2.)

### P3 — A conditional property counts branch hits; fails if a branch is never reached (`68c:283`)

**Bad** (neutral)
```java
    @Test
    @DisplayName("an applied discount never exceeds ten percent, whatever the order")
    void shouldNeverDiscountMoreThanTenPercent() {
        Property.forAll(Gen.orders(), Gen.tiers(), (order, tier) -> {
            final Discount result = discountPolicy.decide(order, tier);

            if (result instanceof Discount.Applied applied) {
                assertThat(applied.saving().amount()).isLessThanOrEqualTo(tenPercentOf(order));
            }
        });
    }
```
If no case ever reaches `Discount.Applied`, the property passes having checked nothing.

**Good** (neutral)
```groovy
def "should keep an applied discount within ten percent of the order total"() {
    given: "a count of cases that reach each branch"
    def applied = 0
    def none = 0
    when: "any order is priced for any tier"
    Property.forAll(Gen.orders(), Gen.tiers()) { order, tier ->
        def result = discountPolicy.decide(order, tier)
        if (result instanceof Discount.Applied) {
            applied++
            assert result.saving().amount() <= order.total().amount() * 0.10
        } else {
            none++
        }
    }

    then: "both the Applied and the None branch were reached"
    applied > 0
    none > 0
}
```
Both branches are counted, so the feature fails when no case reached either one. The harness injects edge cases
(P6) and prints a replayable seed (P4). (Real evidence: ledger row P3.)

### P4 — Seed random per run, printed on failure, replayable; never fixed, never retried (`68c:327`)

**Bad** (neutral)
```ts
export function check<T>(
  gen: Gen<T>,
  predicate: (value: T) => boolean | void,
  opts: PropertyOptions = {},
): Counterexample<T> | null {
  const { runs = 200, seed = 0x5eed } = opts;
  const rng = rngFrom(seed);
```
The default seed is fixed, so every run explores the same 200 cases.

**Good** (neutral)
```ts
import fc from 'fast-check';

export function check<T>(
  arb: fc.Arbitrary<T>,
  predicate: (value: T) => boolean | void,
  opts: PropertyOptions = {},
): void {
  fc.assert(fc.property(arb, predicate), { seed: opts.seed, numRuns: opts.runs ?? 200 });
}
```
With no seed given, fast-check draws one per run and prints it on failure; passing it back replays the case. (Real
evidence: ledger row P4.)

### P6 — Generators include edge cases (0, 1, min, max, empty) by default (`68c:357`)

**Bad** (neutral)
```java
 * <p>What this gives up against a real framework: stateful/model-based testing, exhaustive
 * generation, edge-case injection, statistics.
```
```java
    private static Gen<String> strings(int maxLength, char from, char to) {
        return new Gen<>() {
            @Override public String generate(Random random) {
                final int length = random.nextInt(maxLength + 1);
                final StringBuilder out = new StringBuilder(length);
                for (int i = 0; i < length; i++) {
                    out.append((char) (from + random.nextInt(to - from + 1)));
                }
                return out.toString();
            }
```
The harness gives up edge-case injection, so an empty SKU or maximum length appears only by chance.

**Good** (neutral)
```ts
const SKU = fc.constantFrom('', '   ', 'SKU-BOOK-0001', 'SKU-FOOD-9999');
const QUANTITY = fc.constantFrom(0, 1, 2, 999);
const UNIT_PRICE_CENTS = fc.constantFrom(0, 1, 1999);
const STATUS = fc.constantFrom('', 'DRAFT', 'draft', 'PLACED', 'PAID', 'SHIPPED', 'CANCELLED');
const LINE = fc.record({ sku: SKU, quantity: QUANTITY, unitPriceCents: UNIT_PRICE_CENTS });
const LINES = fc.array(LINE, { maxLength: 10 });
```
Every alphabet starts with its edge value, which fast-check shrinks toward, and the array also draws length 0. (Real
evidence: ledger row P6.)

### P7 — A JVM property is a unit test: runs in the main unit-test target, counts toward coverage (`68c:391`)

**Bad** (n/a) — no property is tagged out of the gate to show.

**Good** (neutral)
```groovy
/** No tag: a unit test, so `./gradlew test` runs it and coverage counts it (#123). */
class DiscountPolicyPropertySpec extends Specification {

    def discountPolicy = new DiscountPolicy()

    def "should never discount an order total below zero for any tier"() {
        expect: "a total of zero or more for every order and tier"
        Property.forAll(Gen.orders(), Gen.tiers()) { order, tier ->
            def total = discountPolicy.discountedTotal(order, tier)
            assert total.amount() >= 0
        }
    }
}
```
It carries no tag, so the main gate runs it and coverage counts it like any unit test. The harness injects edge
cases (P6) and prints a replayable seed (P4). (Real evidence: ledger row P7.)

### P8 — Build generators by mapping/combining, not filtering; never loosen discards to pass (`68c:415`)

**Bad** (neutral)
```groovy
Property.forAll(Gen.asciiStrings(14)) { String rawSku ->
    if (!rawSku.startsWith("SKU-") || !(rawSku ==~ /SKU-[A-Z]{4}-\d{4}/)) {
        return
    }
    assert skuFormat.accepts(rawSku)
}
```
Random ASCII almost never has the SKU shape, so nearly every case is discarded and the property passes vacuously.

**Good** (neutral)
```java
    private static Gen<String> skus() {
        final var families = Gen.oneOf("BOOK", "FOOD", "TOOL", "GIFT");
        final var numbers = Gen.integers(0, 9999);
        final var edges = Gen.oneOf(0, 9999);
        return new Gen<>() {
            @Override public String generate(final Random random) {
                final var number = random.nextInt(10) == 0 ? edges.generate(random) : numbers.generate(random);
                return sku(families.generate(random), number);
            }
            // shrink(...) unchanged
```
Each SKU is composed from family and number generators, with the 0 and 9999 edges mixed into one draw in ten. So
every case has the shape, the edges come up, and none is rejected. (Real evidence: ledger row P8.)

### P10 — UI properties: fast-check, seed printed, numRuns explicit, no retries (`68c:445`)

**Bad** (neutral)
```ts
  test('the order total and the sum of its line totals never disagree', () => {
    forAll('orderTotalCents === sumOf(lineTotalsCents)', LINES, lines =>
      orderTotalCents(lines) === sumOf(lineTotalsCents(lines)));
  });
```
The home-grown harness runs a default count with a fixed seed, so no run explores new cases.

**Good** (neutral)
```ts
test('should never let the order total and the sum of its line totals disagree', () => {
  fc.assert(
    fc.property(LINES, (lines) => orderTotalCents(lines) === sumOf(lineTotalsCents(lines))),
    { numRuns: 200 },
  );
});
```
`numRuns` is explicit, and with no seed passed fast-check draws one per run and prints it on failure. (Real evidence:
ledger row P10.)

## Decided edges

- **P4** · **Skip when** you pass the printed seed back to replay a failing case (`19:101`). — **Do not skip when**
  that seed would be committed: a committed seed explores the same cases every run. — **Confidence** high
- **P6** · **Skip when** a written reason turns the edge cases off (`19:102`). — **Do not skip when** the reason is
  left out. — **Confidence** high
- **P8** · **Skip when** a filter rejects only rare cases (`19:104`). — **Do not skip when** the filter
  discards most cases, or when the discard limit is loosened to make the property pass. — **Confidence** high

## Review checks

Walk every changed property test, every generator it uses, and every changed requirement that says "for any input".

- [ ] P1 — For each rule stated for any input, find a property. A rule of that kind checked only by examples is a
  finding.
- [ ] P2 — For each property, find example tests beside it for the input's CORRECT letters and just-inside/just-outside
  values (B1–B3, `boundaries.md`). A property with no example siblings is a finding.
- [ ] P3 — For each property that asserts inside a branch on the generated case, find a count for every branch and a
  failure when a count is 0. A branch with no count is a finding.
- [ ] P4 — For each property, find a seed drawn per run and printed on failure. A committed fixed seed (`grep -n
  "seed"`), or a retry of a failing property, is a finding.
- [ ] P6 — For each generator, find the edge cases 0, 1, min, max and empty that apply to its type, or a written reason
  for turning them off. A generator with neither is a finding.
- [ ] P7 — For each JVM property, confirm the main unit-test target runs it and coverage counts it. A tag or filter
  that takes it out of that target is a finding.
- [ ] P8 — For each filter or assumption in a generator or property, confirm it rejects only rare cases. A filter
  that discards most cases, or a raised discard limit, is a finding.
- [ ] P10 — For each UI property, find fast-check, an explicit `numRuns`, a printed seed and no retries. A property
  with any one missing is a finding.
