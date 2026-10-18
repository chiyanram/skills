# 68c — Neutral Good/Bad pairs: mutation, property, acceptance criteria, scenario → tests, conventions (#99, map #9)

Source: research/31c-v2.md (M1–M10, P1–P4, P6–P8, P10, GA1–GA6, GT1–GT6), research/31e-conventions.md (CV1–CV5); Goods for M1, M4, M6, M9, P4, P7, CV5 from research/47-good-rewrites.md. Domain: ordering + billing (#99 brief). Stand-ins: `billing` = the one module wired for PIT (was the guardrails module, M7); `FirstAdminSetupIT` = the one IT allowed its own container (was the setup-wizard controller IT, CV5); `TestClientConfig` = the project's test HTTP client config (CV5); the unconsulted NER sidecar (M2) → `FakePaymentGateway` never asked for a refund; the tool-output sanitizer properties (P1, P3, P7, P8) → `OrderService.mergeLines`, `DiscountPolicy`, a SKU generator; the chat-history properties (P6, P10) → order lines and totals; the chat-message copy that lost its tool-call id (M10) → `Order.withStatus` losing `placedAt`; the RestClient call inside the guard (M5) → the RestClient call inside the `PaymentGateway` adapter; Redis unreachable (GA5) → `PaymentGateway` unreachable; the login-throttle REQ (GA*, GT*) → REQ-123-order-cancellation with discount, refund and overdue scenarios. Added terms: `Discount` (sealed result of `DiscountPolicy.decide`: `Discount.Applied` · `Discount.None`); `SkuFormat` (pure decision: does a SKU string parse); `OrderService.mergeLines` (merges lines with the same SKU); `PaymentGateway.refund` / `FakePaymentGateway.refunds()`; Playwright fixture `declinedInvoice`; test helpers named in each Good (`draftOrder`, `placedOrderAt`, `openInvoiceDue`, `seedInvoice`, `payInvoice`).
Skipped: CV6 — MERGED into U2a (2026-10-04).

### M1 — Mutation testing is a report, never a gate; threshold stays 0

**Bad** (n/a) — no gating threshold exists to show.

**Good** (neutral)
```kotlin
    // A report, never a gate (#123): a person reads the score, so the build never fails on it.
    // Raised only after a measured score exists and the operator picks a number.
    mutationThreshold.set(0)
```
Why: the value and the condition for changing it sit in the file where someone would change it.

Evidence: Bad n/a (`Makefile:236-243`, `make mutation` outside every gate) · `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:15-17` @772736bf (Good, real) · source 31c-v2.md:16 · fix from research/47-good-rewrites.md:635

### M2 — Read a surviving mutant as a missing case; name its CORRECT/RIGHT-BICEP letter

**Bad** (neutral)
```groovy
def "kills mutant on line 88"() {
    expect:
    orderService.cancel(order.id()) != null
}
```
What goes wrong: it names a line, not a case, and asserts non-null, so the next mutant on that line survives too.

**Good** (neutral)
```groovy
/** Answers a survivor in OrderService.cancel (RIGHT-BICEP · Cross-check: the gateway stays unconsulted). */
def "should cancel a draft order without asking the payment gateway for a refund"() {
    given: "a draft order the gateway has never charged"
    def order = orderRepository.save(draftOrder())

    when: "the order is cancelled"
    def cancelled = orderService.cancel(order.id())

    then: "the gateway was never asked for a refund"
    gateway.refunds().isEmpty()

    and: "the order is cancelled"
    cancelled.status() == OrderStatus.CANCELLED
}
```
Why: the survivor became a named case that asserts the missed decision, and its RIGHT-BICEP letter is on the page.

Evidence: `aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerHardeningTest.java:41-51` @master-2026-10-02 (sha not recorded) (Bad, adapted) · source 31c-v2.md:27 · fix from 31c-v2.md:28-45

### M3 — Report score and test strength; NO_COVERAGE = not reached, survived = not asserted

**Bad** (neutral)
```text
mutation score 71% — good enough
```
What goes wrong: one number mixes unreached code with unasserted code, so the reader cannot tell which fix is needed.

**Good** (neutral)
```text
make mutation · billing · PIT DEFAULTS
mutation score 71% (142/200) · test strength 89% (142 killed ÷ 160 killed+survived)
NO_COVERAGE 40 → not reached by any test (coverage gap: add a test that runs it)
SURVIVED 18 → reached, not asserted (missing case: name its letter, add the example)
```
Why: both numbers are shown, and the two kinds of non-kill read as two different defects.

Evidence: Bad adapted (no mutation report committed on master; pitest.org report fields) · source 31c-v2.md:56 · fix from 31c-v2.md:57-64

### M4 — Exclude only code with no decision in it; never to raise the number

**Bad** (neutral)
```kotlin
excludedClasses.set(listOf("*Config", "*Properties", "*Policy", "get*", "is*"))
```
What goes wrong: `DiscountPolicy` and `Invoice.isOverdue` are decisions; excluding them hides their missing tests and lifts the score.

**Good** (neutral)
```kotlin
    // Wiring only: no class these globs match contains a decision.
    // Not get*/set*/is*: Invoice.isOverdue is a decision, and hiding it would raise the score.
    excludedClasses.set(listOf("*Config", "*Properties"))
```
Why: it names what is excluded, why it holds no decision, and the tempting exclusion that is refused.

Evidence: Bad adapted (no real Bad on master or in history, research/47:649) · `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:22-25` @772736bf (Good, real) · source 31c-v2.md:72 · fix from research/47-good-rewrites.md:647

### M5 — After changing exclusions/avoidCallsTo, compare per-class mutant counts before and after

**Bad** (neutral)
```kotlin
avoidCallsTo.set(listOf("org.slf4j", "org.springframework"))
```
What goes wrong: the glob over-matches; survivors fall, which looks like success, while the gateway's RestClient calls stop being mutated.

**Good** (neutral)
```kotlin
    // avoidCallsTo REPLACES pitest's defaults rather than adding to them, so the four logging
    // packages must be repeated here. Omitting them made every `log.warn(...)` mutable and
    // added 14 survivors in one run (measured, #123).
    avoidCallsTo.set(listOf(
        "java.util.logging",
        "org.apache.log4j",
        "org.slf4j",
        "org.apache.commons.logging",
        "org.springframework.http.client"))
    // Not "org.springframework.web.client": it would also suppress the RestClient call inside
    // the PaymentGateway adapter's charge(), which is real behaviour. One wiring mutant in the
    // adapter's client builder stays uncovered as a result, the cheaper of the two mistakes.
```
Why: it records the measured count change and why the broader glob was rejected.

Evidence: Bad adapted · `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:31-43` @master-2026-10-02 (sha not recorded) (Good, real base; ST2 paren moved) · source 31c-v2.md:88 · fix from 31c-v2.md:89-104

### M6 — Keep PIT DEFAULTS mutators; never ALL

**Bad** (neutral)
```kotlin
mutators.set(listOf("ALL"))
```
What goes wrong: it adds unstable non-default operators and floods the report with equivalent mutants.

**Good** (neutral)
```kotlin
extensions.configure<PitestPluginExtension>("pitest") {
    junit5PluginVersion.set(version("pitestJunit5"))
    pitestVersion.set(version("pitest"))

    // No `mutators`: PIT's DEFAULTS group. ALL adds unstable operators and equivalent mutants.
    failWhenNoMutations.set(true)
```
Why: the rule is an absence, so a one-line comment makes it visible to the next editor.

Evidence: Bad adapted (no `mutators` ever committed, research/47:661) · `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:9-13` @772736bf (Good, real) · source 31c-v2.md:112 · fix from research/47-good-rewrites.md:659

### M7 — Run make mutation after branching logic in the wired module; other modules: wire in, say so

**Bad** (neutral)
```text
`make mutation` runs PIT against `billing` (`gradlew :billing:pitest`) — a report, not a gate,
because a mutation score needs a human reading it, not a threshold. It exists for one failure: a
unit test that passes today but would still pass if the logic it covers were deleted. Run it on
any module you've added meaningful branching logic to, even outside `billing` — wiring a second
module in is a `build.gradle.kts` change away, not a redesign.
```
What goes wrong: "run it on any module" reads as if `make mutation` covers them, but it only runs `billing`.

**Good** (neutral)
```text
6. **Mutation-test what you just wrote.** `make mutation` runs PIT against `billing` only.
   If you added real branching logic to another module, wire it in there first (a `build.gradle.kts`
   change, not a redesign), run it, and say in the MR description that you wired it in.
```
Why: it names the one wired module, the wiring step, and the sentence the MR must carry.

Evidence: `.claude/skills/gherkin-to-test/SKILL.md:66-71` @master-2026-10-02 (sha not recorded) (Bad, real) · `docs/agents/personas/developer.md:58-60` (Good base, MR sentence added) · source 31c-v2.md:129 · fix from 31c-v2.md:130-136

### M8 — Mutant is equivalent only with a stated reason; unsure = recorded gap

**Bad** (neutral)
```text
18 survivors — all equivalent, ignore.
```
What goes wrong: no mutant has a reason, so eighteen possible missing cases become silence.

**Good** (neutral)
```text
Gap · DiscountPolicy:42 CONDITIONALS_BOUNDARY survived (`quantity > 0` → `quantity >= 0`)
equivalent? unsure — the two differ only for a zero-quantity line; not proven unreachable.
recorded as gap, not as equivalent; risk: a zero-quantity line could earn a GOLD discount.
```
Why: it names the mutant and the reason, and records doubt as a gap with its risk.

Evidence: Bad adapted (no equivalence claim on master; pitest.org basic concepts) · source 31c-v2.md:149 · fix from 31c-v2.md:150-156

### M9 — Do not rely on withHistory for a verdict you will trust

**Bad** (neutral)
```kotlin
withHistory.set(true)
```
What goes wrong: incremental reuse rests on an assumption PIT calls unproven, so a stale kill can be reported.

**Good** (neutral)
```kotlin
    // No withHistory: every run is a full analysis. PIT calls incremental reuse unproven,
    // and a verdict we act on must not rest on a stale kill.
    timestampedReports.set(false)
    outputFormats.set(listOf("HTML", "XML"))
```
Why: the deliberate absence is written down beside the report settings.

Evidence: Bad adapted (no `withHistory` ever committed, research/47:676) · `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:45-49` @772736bf (Good, real) · source 31c-v2.md:164 · fix from research/47-good-rewrites.md:674

### M10 — Mutation-kill test passes first run; prove with a temporary hand mutation, then revert

**Bad** (neutral)
```groovy
/**
 * #123 — withStatus replaces the status and nothing else.
 *
 * <p>Answers the one mutation site this change added to the record, which no other test in this
 * module covers. A copy that quietly lost placedAt would break overdue reminders, and one that
 * lost customerId would invoice the wrong customer. This pins that the copy is otherwise faithful.
 */
def "withStatus replaces the status and nothing else"() {
```
What goes wrong: the kill test was green on first run and nothing shows it was ever made to fail.

**Good** (neutral)
```groovy
/**
 * Kills the survivor in Order.withStatus that dropped placedAt (CORRECT · Reference).
 * Proved: withStatus hand-edited to pass a null placedAt → this feature failed; edit reverted.
 */
def "should keep the placed time when an order is marked paid"() {
    given: "an order placed at nine o'clock"
    def order = placedOrderAt(NINE_AM)

    when: "the order is marked paid"
    def paid = order.withStatus(OrderStatus.PAID)

    then: "the placed time survives"
    paid.placedAt() == NINE_AM
}
```
Why: green on first run is expected; the recorded hand mutation is what proves the test can fail.

Evidence: `aruvii-chat/src/test/groovy/ai/aruvii/chat/domain/ChatMessageHardeningSpec.groovy:7-15` @master-2026-10-02 (sha not recorded) (Bad, real, partial) · source 31c-v2.md:181 · fix from 31c-v2.md:182-199

### P1 — Property when the requirement says "for any input"; otherwise examples

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
What goes wrong: the requirement says "any order", but the test checks one value.

**Good** (neutral)
```groovy
def "should leave merged order lines unchanged when they are merged again"() {
    when: "merging runs twice over any list of order lines"
    Property.forAll(Gen.orderLines()) { lines ->
        def once = orderService.mergeLines(lines)
        assert orderService.mergeLines(once) == once
    }

    then: "every second merge returned the first merge unchanged"
    noExceptionThrown()
}
```
Why: idempotence is a law for any input, so a property states it; the check is an explicit `assert`.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:331-335` + `aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:43-46` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:221 · fix from 31c-v2.md:222-235

### P2 — A property never replaces examples; boundary cases stay as examples beside it

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
Why: CORRECT · Existence cases stay as examples beside the property, because its generators never produce `null`.

Evidence: Bad n/a (`ToolOutputSanitizerTest.java`, `aruvii-ui/playwright/unit/history.spec.ts` already siblings) · source 31c-v2.md:254 · fix from 31c-v2.md:255-265

### P3 — A conditional property counts branch hits; fails if a branch is never reached

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
What goes wrong: if no case ever reaches `Discount.Applied`, the property passes having checked nothing.

**Good** (neutral)
```groovy
def "should keep an applied discount within ten percent of the order total"() {
    given: "a count of cases that reach the Applied branch"
    def applied = 0
    when: "any order is priced for any tier"
    Property.forAll(Gen.orders(), Gen.tiers()) { order, tier ->
        def result = discountPolicy.decide(order, tier)
        if (result instanceof Discount.Applied) {
            applied++
            assert result.saving().amount() <= order.total().amount() * 0.10
        }
    }

    then: "the Applied branch was reached at least once"
    applied > 0
}
```
Why: the branch is counted, so the feature fails when no case reached it.

Evidence: `aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java:67-77` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:269 · fix from 31c-v2.md:270-288

### P4 — Seed random per run, printed on failure, replayable; never fixed, never retried

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
What goes wrong: the default seed is fixed, so every run explores the same 200 cases.

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
Why: with no seed given, fast-check draws one per run and prints it on failure; passing it back replays the case.

Evidence: `aruvii-ui/playwright/support/property.ts:114-120` @772736bf (Bad, real) · source 31c-v2.md:306 · fix from research/47-good-rewrites.md:687

### P6 — Generators include edge cases (0, 1, min, max, empty) by default

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
What goes wrong: the harness gives up edge-case injection, so an empty SKU or maximum length appears only by chance.

**Good** (neutral)
```ts
const SKU = fc.constantFrom('', '   ', 'SKU-BOOK-0001', 'SKU-FOOD-9999');
const QUANTITY = fc.constantFrom(0, 1, 2, 999);
const UNIT_PRICE_CENTS = fc.constantFrom(0, 1, 1999);
const STATUS = fc.constantFrom('', 'DRAFT', 'draft', 'PLACED', 'PAID', 'SHIPPED', 'CANCELLED');
const LINE = fc.record({ sku: SKU, quantity: QUANTITY, unitPriceCents: UNIT_PRICE_CENTS });
const LINES = fc.array(LINE, { maxLength: 10 });
```
Why: every alphabet starts with its edge value, which fast-check shrinks toward, and the array also draws length 0.

Evidence: `aruvii-guardrails/src/test/java/ai/aruvii/guardrails/property/Property.java:25-27` + `.../property/Gen.java:66-75` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:333 · fix from 31c-v2.md:334-342

### P7 — A JVM property is a unit test: runs in make test, counts toward coverage

**Bad** (n/a) — no property is tagged out of the gate to show.

**Good** (neutral)
```groovy
/** No tag: a unit test, so `make test` runs it and coverage counts it (#123). */
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
Why: it carries no tag, so the main gate runs it and coverage counts it like any unit test.

Evidence: Bad n/a in source (research/47:717 has a real one: `ToolOutputSanitizerPropertyTest.java:29-31,43-44` @613429ec, `@Tag("property")`) · source 31c-v2.md:365 · fix from research/47-good-rewrites.md:715

### P8 — Build generators by mapping/combining, not filtering; never loosen discards to pass

**Bad** (neutral)
```groovy
Property.forAll(Gen.asciiStrings(14)) { String rawSku ->
    if (!rawSku.startsWith("SKU-") || !(rawSku ==~ /SKU-[A-Z]{4}-\d{4}/)) {
        return
    }
    assert skuFormat.accepts(rawSku)
}
```
What goes wrong: random ASCII almost never has the SKU shape, so nearly every case is discarded and the property passes vacuously.

**Good** (neutral)
```java
    private static Gen<String> skus() {
        final var families = Gen.oneOf("BOOK", "FOOD", "TOOL", "GIFT");
        final var numbers = Gen.integers(0, 9999);
        return new Gen<>() {
            @Override public String generate(final Random random) {
                return sku(families.generate(random), numbers.generate(random));
            }
            // shrink(...) unchanged
```
Why: each SKU is composed from family and number generators, so every case has the shape and none is rejected.

Evidence: Bad adapted from `aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java` @master-2026-10-02 (sha not recorded) · `ToolOutputSanitizerPropertyTest.java:194-202` (Good base, ST1 applied) · source 31c-v2.md:387 · fix from 31c-v2.md:388-400

### P10 — UI properties: fast-check, seed printed, numRuns explicit, no retries

**Bad** (neutral)
```ts
  test('the order total and the sum of its line totals never disagree', () => {
    forAll('orderTotalCents === sumOf(lineTotalsCents)', LINES, lines =>
      orderTotalCents(lines) === sumOf(lineTotalsCents(lines)));
  });
```
What goes wrong: the home-grown harness runs a default count with a fixed seed, so no run explores new cases.

**Good** (neutral)
```ts
test('should never let the order total and the sum of its line totals disagree', () => {
  fc.assert(
    fc.property(LINES, (lines) => orderTotalCents(lines) === sumOf(lineTotalsCents(lines))),
    { numRuns: 200 },
  );
});
```
Why: `numRuns` is explicit, and with no seed passed fast-check draws one per run and prints it on failure.

Evidence: `aruvii-ui/playwright/property/history.property.spec.ts:53-56` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:413 · fix from 31c-v2.md:414-425

### GA1 — Scenarios live in the REQ AC section as one fenced gherkin block

**Bad** (neutral)
~~~~text
```
AC-1  Given order O is PAID with one payment of 40.00 EUR
      When  the customer cancels O
      Then  the payment is refunded; the invoice is closed; an email
            tells the customer the order id and the refund amount
```
~~~~
What goes wrong: Given/When/Then sit as prose in an untyped fence, so it is not Gherkin and cannot take Examples.

**Good** (neutral)
~~~~gherkin
```gherkin
# AC-1 · CORRECT · Existence — the defect this REQ exists for: a paid order cancelled with no refund
@billing
Scenario: should refund the payment when a paid order is cancelled
  Given a PAID order with one payment of 40.00 EUR
  When the customer cancels the order
  Then the PaymentGateway receives a refund of 40.00 EUR
```
~~~~
Why: one gherkin block inside the REQ's acceptance criteria, with one checkable Then and no `.feature` file.

Evidence: `docs/spec/REQ-075-certification-execution-gate.md:699-704` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:441 · fix from 31c-v2.md:442-452

### GA2 — Every scenario has a stable analyst-assigned id (AC-1…), fixed once approved

**Bad** (neutral)
```gherkin
@domain @orders
Scenario: A cancelled order always sends the customer one email
  Given a PLACED order for customer c@example.com
  When the clerk cancels the order
  Then the EmailSender sends one email to c@example.com
```
What goes wrong: the title is the only handle, so rewording it breaks every MR and test that refers to it.

**Good** (neutral)
~~~~gherkin
```gherkin
# AC-2
@orders
Scenario: should send the customer one email when an order is cancelled
  Given a PLACED order for customer c@example.com
  When the clerk cancels the order
  Then the EmailSender sends one email to c@example.com
```
~~~~
Why: `AC-2` is a stable handle for the MR and the test's `@Issue`; rewording the title does not move it.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:303-307` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:464 · fix from 31c-v2.md:465-475

### GA3 — Tags name the domain/concern, never the tier

**Bad** (neutral)
```gherkin
# Shipped goods cannot be recalled by a cancellation
@api @orders
Scenario: A shipped order cannot be cancelled
  Given a SHIPPED order
  When the customer cancels the order
  Then the order stays SHIPPED
```
What goes wrong: `@api` decides the test tier before the developer has looked at what the behaviour depends on.

**Good** (neutral)
~~~~gherkin
```gherkin
# AC-4 · shipped goods cannot be recalled by a cancellation
@orders
Scenario: should keep a shipped order shipped when the customer cancels it
  Given a SHIPPED order
  When the customer cancels the order
  Then the order stays SHIPPED
```
~~~~
Why: the tag names only the concern; the developer picks unit, IT or smoke by what the behaviour depends on.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:352-357` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:487 · fix from 31c-v2.md:488-498

### GA4 — Examples header names exactly the <placeholders>; shared preconditions once as Background

**Bad** (neutral)
~~~~gherkin
```gherkin
# AC-5
@billing
Scenario Outline: should give ten percent off to a GOLD customer on orders of 100.00 EUR or more
  Given a <tier> customer with an order total of <total> EUR
  When the discount is decided
  Then the discount is <discount> EUR

  Examples:
    | level | amount | expected |
    | GOLD  | 100.00 | 10.00    |
```
~~~~
What goes wrong: the header names no placeholder, and with no Gherkin parser nothing catches the mismatch.

**Good** (neutral)
~~~~gherkin
```gherkin
Background:
  Given the order is PLACED and not yet invoiced
# AC-5 · CORRECT · Range — just below and at the 100.00 EUR edge
@billing
Scenario Outline: should give ten percent off to a GOLD customer on orders of 100.00 EUR or more
  Given a <tier> customer with an order total of <total> EUR
  When the discount is decided
  Then the discount is <discount> EUR
  Examples:
    | tier     | total  | discount |
    | GOLD     | 99.99  | 0.00     |
    | GOLD     | 100.00 | 10.00    |
    | STANDARD | 100.00 | 0.00     |
```
~~~~
Why: the header equals the three placeholders, and the shared precondition is written once as `Background:`.

Evidence: Bad adapted from `docs/spec/REQ-500-login-throttle-progressive-delay.md:376-386` @master-2026-10-02 (sha not recorded) (no real mismatch on master) · `REQ-500:337-350`, `REQ-075:692-695` (Good base) · source 31c-v2.md:511 · fix from 31c-v2.md:512-535

### GA5 — One checkable Then per scenario; every AC has a failure/refusal scenario

**Bad** (neutral)
```gherkin
@api @billing
Scenario Outline: A declined payment path no longer exists
  Given the invoice endpoint
  When <condition>
  Then no PaymentDeclinedException path is reachable

  Examples:
    | condition                         |
    | the card is declined              |
    | the PaymentGateway is unreachable |
```
What goes wrong: the Then is a claim about code structure, so no test can check it by running the scenario.

**Good** (neutral)
~~~~gherkin
```gherkin
# AC-8 · the gateway-down contract
@billing @resilience
Scenario Outline: should keep the invoice open on every payment call when the PaymentGateway is unreachable
  Given the PaymentGateway is unreachable
  When <operation>
  Then the invoice stays OPEN

  Examples:
    | operation                                 |
    | the customer pays the invoice             |
    | the clerk retries the payment             |
    | the overdue reminder charges the invoice  |
```
~~~~
Why: the gateway-down failure path has one observable Then that a running test can check.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:394-403` @master-2026-10-02 (sha not recorded) (Bad, real) · `REQ-500:428-439` (Good base) · source 31c-v2.md:553 · fix from 31c-v2.md:554-570

### GA6 — Scenario titles are behaviour starting with "should …"

**Bad** (neutral)
```gherkin
@domain @billing
Scenario: An invoice past its due date becomes overdue
```
What goes wrong: a statement title cannot become the test name without rewording, so the title and test drift apart.

**Good** (neutral)
~~~~gherkin
```gherkin
# AC-6 · CORRECT · Time — an invoice is overdue only after its due date
@billing
Scenario: should mark an invoice overdue once its due date has passed
  Given an OPEN invoice due yesterday
  When the overdue reminder runs
  Then the invoice is OVERDUE
```
~~~~
Why: the title is already a valid "should …" test name, so the test copies it verbatim.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:454-455` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:587 · fix from 31c-v2.md:588-598

### GT1 — Test name is the scenario title verbatim (Outline adds " — #placeholder")

**Bad** (neutral)
```gherkin
Scenario Outline: A GOLD customer gets ten percent off, a STANDARD customer gets nothing
```
```groovy
    def "the GOLD discount is ten percent, the STANDARD discount is zero"() {
```
What goes wrong: the test rewords the title, so a search for the scenario title finds no test.

**Good** (neutral)
```gherkin
Scenario: should mark an invoice overdue once its due date has passed
```
```groovy
@Issue(["#123", "AC-6"])
def "should mark an invoice overdue once its due date has passed"() {
```
Why: the same string, byte for byte, so `grep -F` on the title finds the test.

Evidence: `docs/spec/REQ-500-login-throttle-progressive-delay.md:311` + `aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:25` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:612 · fix from 31c-v2.md:613-621

### GT2 — Spock block texts repeat the Given/When/Then; Playwright one test.step per step

**Bad** (neutral)
```groovy
    def "D4 — an invoice past its due date can never stay open"() {
        given: "an invoice nobody has paid"
        def invoice = invoiceRepository.save(openInvoiceDue(TODAY.minusDays(1)))

        when: "the job runs"
        overdueReminder.run()

        then: "an open invoice past due is the defect this REQ exists to prevent"
        invoiceRepository.findById(invoice.id()).orElseThrow().status() == InvoiceStatus.OVERDUE
    }
```
What goes wrong: the block texts paraphrase the scenario, so the test report does not read as the agreed steps.

**Good** (neutral)
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
Why: each block label is the scenario step word for word, so the report reads as the scenario.

Evidence: `aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/LoginThrottleServiceIT.groovy:56-65` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:633 · fix from 31c-v2.md:634-651

### GT3 — Outline → Spock where: / test.each with Examples columns unchanged; e2e one row

**Bad** (neutral)
```groovy
        where:
        level    | amount || expected
        GOLD     | 99.99  || 0.00
        GOLD     | 100.00 || 10.00
        STANDARD | 100.00 || 0.00
```
What goes wrong: the columns `tier | total | discount` were renamed, so the table no longer reads against the scenario's Examples.

**Good** (neutral)
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
Why: the column names equal the Examples header, and the Given is the `where:` text because the table is the given.

Evidence: `aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:29-33` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:668 · fix from 31c-v2.md:669-687

### GT4 — Each scenario test carries @Issue("#NNN") / Playwright issue annotation + AC id

**Bad** (neutral)
```groovy
/**
 * REQ-123 §Acceptance criteria. Every figure asserted here is the discount table's, and the
 * table cites where each one comes from.
 *
 * <p>The tier tables run against a policy with no seasonal offer. Seasonal offers are a separate
 * rule with their own features below.
 */
class DiscountPolicySpec extends Specification {
```
What goes wrong: traceability is free javadoc, so no search finds the work item or scenario id on any feature.

**Good** (neutral)
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
  },
);
```
Why: both tests carry a machine-readable link to `#123` and the scenario id.

Evidence: `aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:8-17` @master-2026-10-02 (sha not recorded) (Bad, real) · `aruvii-ui/playwright/e2e/smoke/smoke-01-auth.spec.ts:13-24` (Good base) · source 31c-v2.md:699 · fix from 31c-v2.md:700-720

### GT5 — One owning tier per scenario by S1; second tier only for a risk the first cannot see

**Bad** (neutral)
```groovy
    def "D1 — no discount makes an invoice total negative"() {
        given: "one GOLD customer, each order saved to the real database"
        def customer = customerRepository.save(goldCustomer())
        200.times { i -> orderRepository.save(orderFor(customer, i)) }

        expect: "a GOLD customer never gets money back"
        orderRepository.findAll().every { invoiceService.issue(it.id()).total().amount() >= 0 }
    }
```
What goes wrong: a unit spec already owns this rule; the IT repeats it against a real database and names no new risk.

**Good** (neutral)
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
Why: the scenario crosses HTTP and the database, so one IT owns it and no smoke spec replays it.

Evidence: `aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/LoginThrottleServiceIT.groovy:67-75` @master-2026-10-02 (sha not recorded) (Bad, real, judgement) · `aruvii-api/src/integrationTest/java/ai/aruvii/api/security/LoginThrottleIT.java:130-140` (Good base) · source 31c-v2.md:737 · fix from 31c-v2.md:738-753

### GT6 — MR lists every AC-id → tier → test file:line; unlisted = "not done"

**Bad** (neutral)
```text
- Take each acceptance criterion from the REQ — or from the work item body, where the change has
  no REQ.
- For each one, find the code that satisfies it and cite `file:line`. Not the test that covers
  it; the code that does it.
- A criterion you cannot cite is not met. Say which, and either implement it or say plainly on
  the MR why it is out of scope.
```
What goes wrong: it maps criteria to code, never to tests, so a scenario with no test is invisible.

**Good** (neutral)
```markdown
| AC | scenario | tier | test |
|---|---|---|---|
| AC-5 | should give ten percent off to a GOLD customer on orders of 100.00 EUR or more | unit | DiscountPolicySpec.groovy:25 |
| AC-3 | should refuse to pay an invoice that is already paid | IT | InvoiceControllerIT.groovy:41 |
| AC-8 | should keep the invoice open on every payment call when the PaymentGateway is unreachable | — | not done |
```
Why: every scenario has a row, so a missing test shows as "not done".

Evidence: `.claude/commands/crq.md:388-393` @master-2026-10-02 (sha not recorded) (Bad, real) · source 31c-v2.md:769 · fix from 31c-v2.md:770-778

### CV1 — AC id in Gherkin is a `# AC-n` comment line above `Scenario:`

**Bad** (neutral)
```gherkin
@AC-3 @billing
Scenario: AC-3 should refuse to pay an invoice that is already paid
```
What goes wrong: the id as a tag breaks the concern-only tag rule; the id in the title breaks name-equals-title.

**Good** (neutral)
```gherkin
# AC-3
@billing
Scenario: should refuse to pay an invoice that is already paid
  Given an invoice that is already PAID
  When the customer pays the invoice
  Then the payment is refused with INVOICE_ALREADY_PAID
```
Why: the comment carries the id, the tag names a concern, and the title stays equal to the test name.

Evidence: Bad adapted (pattern) · `docs/spec/REQ-500-login-throttle-progressive-delay.md:303-307` (Good base) @master-2026-10-02 (sha not recorded) · source 31e-conventions.md:3 · fix from 31e-conventions.md:4-12

### CV2 — A Spock test names its work item and AC with `@Issue(["#NNN", "AC-n"])`

**Bad** (neutral)
```groovy
// AC-3 of #123
def "should refuse to pay an invoice that is already paid"() {
```
What goes wrong: Spock does not report a comment, and the comment drifts from the scenario unnoticed.

**Good** (neutral)
```groovy
@Issue(["#123", "AC-3"])
def "should refuse to pay an invoice that is already paid"() {
```
Why: one annotation carries both links, and a search for `"AC-3"` finds the test.

Evidence: Bad adapted (pattern) · source 31e-conventions.md:22 · fix from 31e-conventions.md:23-28

### CV3 — Wrapping: ST2 applies to Java/Groovy (120); TypeScript follows Prettier (110)

**Bad** (n/a) — the conflict is between two rules, not in code.

**Good** (neutral)
```ts
await expect(
  page.getByRole('row', { name: invoiceId }),
).toBeVisible();
```
Why: this is Prettier's own output; forcing the Java closing-paren rule onto it would fight the formatter.

Evidence: Bad n/a · `aruvii-ui/.prettierrc.json` (Good, Prettier output, adapted) · source 31e-conventions.md:37 · fix from 31e-conventions.md:38-44

### CV4 — Property tests written in Spock use an explicit `assert` inside the `Property.forAll` closure

**Bad** (neutral)
```groovy
Property.forAll(Gen.orders()) { order ->
    taxCalculator.totalWithTax(order).amount() >= order.total().amount()
}
```
What goes wrong: Spock does not assert lines in this closure, so the boolean is discarded and the property always passes.

**Good** (neutral)
```groovy
Property.forAll(Gen.orders()) { order ->
    def withTax = taxCalculator.totalWithTax(order)
    assert withTax.amount() >= order.total().amount()
}
```
Why: the explicit `assert` makes a false case fail the property.

Evidence: Bad adapted from `aruvii-guardrails` ToolOutputSanitizerPropertyTest @master-2026-10-02 (sha not recorded) · source 31e-conventions.md:46 · fix from 31e-conventions.md:47-54

### CV5 — The shared-container rule has one documented exception: the first-run setup IT

**Bad** (n/a) — any other IT doing this breaks the shared-container rule.

**Good** (neutral)
```java
/** The one shared-container exception: first-run setup needs a database no seeder has touched. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Import(TestClientConfig.class)
class FirstAdminSetupIT {

    @Container
    static final PostgreSQLContainer POSTGRES = new PostgreSQLContainer(TestConstants.POSTGRES_IMAGE)
        .withDatabaseName(TestConstants.DB_NAME)
        .withUsername(TestConstants.DB_USERNAME)
        .withPassword(TestConstants.DB_PASSWORD);
```
Why: the exception is named once, the container is `final`, and the values come from shared constants.

Evidence: Bad n/a in source (research/47:775 has a real one: `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:50-58` @772736bf) · `SetupControllerIT.java:44-58` (Good base) · source 31e-conventions.md:63 · fix from research/47-good-rewrites.md:773
