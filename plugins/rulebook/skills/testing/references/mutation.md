# Mutation

How to configure PIT and how to read and answer its report. Read it when you change a PIT configuration, read a
mutation report, or write a test that answers a surviving mutant.

Contents: Rules · When X, use Y · Good / Bad (M1–M6, M8–M10) · Decided edges · Review checks

## Rules

- **M1** — Keep mutation testing a report, not a gate, and `mutationThreshold` at 0 until the operator picks one
  from a measured score, because gate minutes are paid every run and an unmeasured threshold is a guess.
- **M2** — Read a surviving mutant as a missing case: name the CORRECT or RIGHT-BICEP letter it breaks, then add that
  example test, because a test aimed at one mutant's line lets the next mutant there survive.
- **M3** — Report the mutation score and the test strength (killed ÷ (killed + survived)); read NO_COVERAGE as not
  reached and SURVIVED as not asserted, because one number mixes unreached code with unasserted code.
- **M4** — Exclude only code with no decision in it, such as wiring and config; never exclude code to raise the
  score, because excluding decision code hides its missing tests from the report.
- **M5** — After you change exclusions or `avoidCallsTo`, compare the per-class mutant counts before and after,
  because an over-matching glob looks exactly like a successful exclusion.
- **M6** — Keep PIT's DEFAULTS mutators and never set `ALL`, because non-default mutators are unstable and flood the
  report with equivalent mutants.
- **M8** — Mark a mutant equivalent only with a stated reason; when unsure, record it as a gap, because a mutant
  marked equivalent without a reason can hide a real gap.
- **M9** — Run a full analysis for a verdict you will trust, not `withHistory` incremental analysis, because PIT
  calls its assumption unproven and a stale history cache can silently report wrong results.
- **M10** — Prove a mutation-kill test with a temporary hand mutation, then revert it, not with a Red run, because a
  kill test passes on correct code and only a mutation shows it can fail.

## When X, use Y

| the report or the change shows | use | why |
|---|---|---|
| a NO_COVERAGE mutant | a test that runs the code | not reached by any test (M3) · 68c :64 |
| a SURVIVED mutant | the missing case: name its letter, add the example test | reached, not asserted (M2, M3) · 68c :65 |
| a SURVIVED Conditionals Boundary mutant | a just-inside and just-outside case (B3, `boundaries.md`) | M2's source pairs Conditionals Boundary with B3 · ledger :88 |
| a survivor whose letter you must name | CORRECT (B1, `boundaries.md`) or RIGHT-BICEP (C1, `coverage-design.md`) | M2 names these two lists · ledger :88 |
| a survivor you cannot prove equivalent | a gap with its risk (C4, `coverage-design.md`) | unsure means gap, not equivalent (M8) · 68c :172-173 |
| a new kill test that passes on its first run | a temporary hand mutation, then revert it | green on first run is expected (M10) · 68c :230 |

68c is `research/68c-neutral-testing-mutation-property-scenarios.md`; ledger is `research/19-approved-rules.md`.
`:N` is a line in that file.

## Good / Bad

### M1 — A report, not a gate; the threshold stays 0

**Bad** (n/a) — no gating threshold exists to show.

**Good** (neutral)
```kotlin
    // A report, never a gate (#123): a person reads the score, so the build never fails on it.
    // Raised only after a measured score exists and the operator picks a number.
    mutationThreshold.set(0)
```
The value and the condition for changing it sit in the file where someone would change it. (Real evidence: ledger
row M1.)
M1's reason comes from agent-factory research/31:23, approved by the operator; the ledger row has none.

### M2 — Read a survivor as a missing case and name its letter

**Bad** (neutral)
```groovy
def "kills mutant on line 88"() {
    expect:
    orderService.cancel(order.id()) != null
}
```
It names a line, not a case. It asserts only non-null, so the next mutant on that line survives too.

**Good** (neutral)
```groovy
/** Answers a survivor in OrderService.cancel (RIGHT-BICEP · Right: the gateway stays unconsulted). */
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
The survivor became a named case that asserts the missed decision. Its RIGHT-BICEP letter is on the page. (Real
evidence: ledger row M2.)

### M3 — Report score and test strength

**Bad** (neutral)
```text
mutation score 71% — good enough
```
One number mixes unreached code with unasserted code. The reader cannot tell which fix is needed.

**Good** (neutral)
```text
./gradlew pitest · billing · PIT DEFAULTS
mutation score 71% (142/200) · test strength 89% (142 killed ÷ 160 killed+survived)
NO_COVERAGE 40 → not reached by any test (coverage gap: add a test that runs it)
SURVIVED 18 → reached, not asserted (missing case: name its letter, add the example)
```
Both numbers are shown. The two kinds of non-kill read as two different defects. (Real evidence: ledger row M3.)

### M4 — Exclude only code with no decision in it

**Bad** (neutral)
```kotlin
excludedClasses.set(listOf("*Config", "*Properties", "*Policy"))
excludedMethods.set(listOf("get*", "is*"))
```
`DiscountPolicy` and `Invoice.isOverdue` are decisions. Excluding them hides their missing tests and lifts the score.

**Good** (neutral)
```kotlin
    // Wiring only: no class these globs match contains a decision.
    // Not get*/set*/is*: Invoice.isOverdue is a decision, and hiding it would raise the score.
    excludedClasses.set(listOf("*Config", "*Properties"))
```
It names what is excluded and why it holds no decision. It also names the tempting exclusion it refuses. (Real
evidence: ledger row M4.)

### M5 — Compare per-class mutant counts after changing exclusions

**Bad** (neutral)
```kotlin
// Added org.springframework: survivors fell 18 → 4, so the change is safe (#123).
avoidCallsTo.set(listOf("org.slf4j", "org.springframework"))
```
Only the total was read, and no per-class counts were compared. So nobody sees that the gateway's RestClient calls
stopped being mutated.

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
It records the measured count change and why the broader glob was rejected. (Real evidence: ledger row M5.)

### M6 — Keep the DEFAULTS mutators

**Bad** (neutral)
```kotlin
mutators.set(listOf("ALL"))
```
It adds unstable non-default operators and floods the report with equivalent mutants.

**Good** (neutral)
```kotlin
extensions.configure<PitestPluginExtension>("pitest") {
    junit5PluginVersion.set(version("pitestJunit5"))
    pitestVersion.set(version("pitest"))

    // No `mutators`: PIT's DEFAULTS group. ALL adds unstable operators and equivalent mutants.
    failWhenNoMutations.set(true)
```
The rule is an absence, so a one-line comment makes it visible to the next editor. (Real evidence: ledger row M6.)

### M8 — Equivalent only with a stated reason

**Bad** (neutral)
```text
18 survivors — all equivalent, ignore.
```
No mutant has a reason, so eighteen possible missing cases become silence.

**Good** (neutral)
```text
Gap · DiscountPolicy:42 CONDITIONALS_BOUNDARY survived (`quantity > 0` → `quantity >= 0`)
equivalent? unsure — the two differ only for a zero-quantity line; not proven unreachable.
recorded as gap, not as equivalent; risk: a zero-quantity line could earn a GOLD discount.
```
It names the mutant and the reason. It records the doubt as a gap with its risk. (Real evidence: ledger row M8.)

### M9 — A full analysis for a verdict you trust

**Bad** (neutral)
```kotlin
withHistory.set(true)
```
Incremental reuse rests on an assumption PIT calls unproven, so a stale kill can be reported.

**Good** (neutral)
```kotlin
    // No withHistory: every run is a full analysis. PIT calls incremental reuse unproven,
    // and a verdict we act on must not rest on a stale kill.
    timestampedReports.set(false)
    outputFormats.set(listOf("HTML", "XML"))
```
The deliberate absence is written down beside the report settings. (Real evidence: ledger row M9.)

### M10 — Prove a kill test with a temporary hand mutation

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
The kill test was green on its first run, and nothing shows it was ever made to fail.

**Good** (neutral)
```groovy
/**
 * Kills the survivor in Order.withStatus that dropped placedAt (RIGHT-BICEP · Right).
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
Green on the first run is expected. The recorded hand mutation proves the test can fail. (Real evidence: ledger
row M10.)

## Decided edges

- **Skip when** a class holds only wiring or config, such as `*Config` and `*Properties`: exclude it (M4). —
  **Do not skip when** a getter or an `is*` method decides something: it stays measured (M4; ledger :90).
  — **Confidence** high
- **Skip when** a test answers a surviving mutant in correct code: prove it with a hand mutation, not a Red run
  (M10). — **Do not skip when** the change is a bug fix: the failing test comes first (S4, `strategy.md`; ledger
  :96; ADR-0007). — **Confidence** high

## Review checks

Walk every changed PIT configuration, every mutation report or survivor list in the MR, and every test added to
answer a survivor.

- [ ] M1 — `grep -n "mutationThreshold"` in each changed PIT configuration. A value other than 0 with no operator
  decision from a measured score, or a gate that fails on the score, is a finding.
- [ ] M2 — For each test added to answer a survivor, find the CORRECT or RIGHT-BICEP letter named for it and a case
  that asserts the missed decision. A test aimed at a line, or with no letter named, is a finding.
- [ ] M3 — In each mutation report in the MR, find the mutation score, the test strength, the NO_COVERAGE count and
  the SURVIVED count, each reported apart. A missing one is a finding.
- [ ] M4 — For each new glob in an exclusion list, open the classes and methods it matches. A match that contains a
  decision, or an exclusion whose effect is only a higher score, is a finding.
- [ ] M5 — For each change to an exclusion list or `avoidCallsTo`, find the per-class mutant counts before and after
  the change. A change with no comparison is a finding.
- [ ] M6 — `grep -n "mutators"` in each changed PIT configuration. `ALL`, or any group other than DEFAULTS, is a
  finding.
- [ ] M8 — For each mutant called equivalent, find its stated reason. An equivalent claim with no reason, or an
  unsure one not recorded as a gap, is a finding.
- [ ] M9 — `grep -n "withHistory"` in each changed PIT configuration. Incremental analysis on the run whose verdict
  the MR relies on is a finding.
- [ ] M10 — For each kill test, find the hand mutation that made it fail, and check the diff keeps no left-over
  mutation. A kill test with no shown failure, or an unreverted edit, is a finding.
