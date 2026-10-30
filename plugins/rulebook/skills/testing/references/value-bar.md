# Value bar

Whether a test should exist at all. Read it before you add a test, when you fix a bug, and when you review or remove a
test.

Contents: Rules · When X, use Y · Good / Bad (V1–V5) · Decided edges · Review checks

## Rules

- **V1** — Before adding a test, write one line each for contract, regression, why uncovered and seam; add no test
  with a missing answer, because a test with no credible regression costs upkeep and protects nothing.
- **V2** — A test that breaks under a behaviour-preserving refactor asserts implementation: rewrite it at the boundary
  that owns the behaviour before landing, because it fails on a safe rename while the real output stays the same.
- **V3** — Add no test that matches a junk pattern unless it names the contract it independently guards, because a
  junk-pattern test cannot fail for a real defect.
- **V4** — Give a bug ONE regression test, at the boundary that owns the behaviour, never replayed at every layer it
  crosses, because copies at mocked layers cannot see the bug and only add upkeep.
- **V5** — Prove a test is junk before removing it, and keep every test a retention row names, because a test that
  looks like junk may be the only guard of a contract.

## When X, use Y

Each row maps what you see to the rule and the action. Openclaw is `openclaw/openclaw`
`.agents/skills/test-audit/SKILL.md`, the source of V1–V5; `:N` is its line.

| situation | use | why |
|---|---|---|
| you add a test | write one line each: 1 the behaviour or contract it protects · 2 the realistic regression that makes it fail · 3 why existing coverage does not catch it · 4 whether it needs a production seam no real caller needs (V1) | a missing answer means do not add it (openclaw :18-19) · questions: openclaw :21-29 |
| existing coverage already proves the contract (answer 3) | one primary test per contract, at its strongest boundary (V1); which tier that is: S1, TM1 (`strategy.md`) | each contract has one primary test owner at the strongest boundary (openclaw :23-24) |
| the test needs a production seam that no production caller needs (answer 4) | test at the real boundary instead (V1) | openclaw :28-29 |
| the test would fail under a behaviour-preserving refactor | rewrite it at the boundary that owns the behaviour before it lands (V2); for mock interactions: K4 (`spock.md`) | it asserts implementation, not behaviour (openclaw :33-35) |
| the new test matches a junk-pattern row below | name the contract it independently guards, or do not add it (V3) | openclaw :31-33 |
| you fix a bug | one regression test at the boundary that owns the behaviour (V4); failing first: S4 (`strategy.md`) | one regression at the owner boundary covers the bug (openclaw :39-40) |
| you would remove an existing test | keep it if a retention row below holds; otherwise prove it is junk first (V5) | a test that resembles implementation may still be the independent contract (openclaw :108-109) |

**Junk patterns (V3).** A new test matching one of these rows fails V3 unless it names the contract it guards. Each
row's why is V3's: it cannot fail for a real defect.

| the new test | use | why |
|---|---|---|
| has no assertion | junk pattern 1; Spock form: K19 (`spock.md`) | openclaw :47 |
| compares a value with itself or with a copy of itself | junk pattern 2 | openclaw :48 |
| checks a hand-copied list of enum or registry members | junk pattern 3 | openclaw :49 |
| greps source or exact strings instead of running the code | junk pattern 4 | openclaw :50 |
| takes its expected value from the code under test | junk pattern 5 | openclaw :56 |
| uses a mock that implements the asserted behaviour | junk pattern 6 | openclaw :57-58 |
| proves the same contract twice at different layers with no new risk | junk pattern 7; tier choice: GT5 (`scenario-to-tests.md`) | openclaw :52, :23-26 |
| has a name that promises more than its input exercises | junk pattern 8 | openclaw :65-66 |

**Retention rows (V5).** Keep an existing test when one of these rows holds.

| the existing test | use | why |
|---|---|---|
| independently guards a contract: API, protocol, config, migration, storage, security, a promised default, architecture | keep it (V5) | openclaw :96-98 |
| asserts order, and order is observable behaviour | keep it (V5); how to assert order: K13 (`spock.md`) | openclaw :100 |
| is a regression with a realistic failure mode | keep it (V5) | openclaw :101 |
| fails on master | treat it as a possible product bug: reproduce it, fix the owner, never delete it (V5) | openclaw :105-106 |
| is slow or static | keep it: slow or static is not a deletion reason (V5) | openclaw :108 |

## Good / Bad

### V1 — Answer the four questions before adding a test

**Bad** (neutral)
```groovy
    def "a refunded order has its own status"() {
        expect: "REFUNDED is named"
        OrderStatus.valueOf("REFUNDED") != null
    }
```
No realistic regression fails it. Removing a constant breaks compilation first, and nothing sets REFUNDED yet.

**Good** (neutral)
```groovy
/**
 * Q1 contract: OrderRepository stores OrderStatus.name() on each order row and /api/orders
 *    returns it as status.
 * Q2 regression: a renamed constant strands stored rows and every client that filters on the old name.
 * Q3 not covered: no test names the stored strings; compilation only proves a constant exists.
 * Q4 seam: none; the enum is what the repository writes.
 * REFUNDED gets its test when the refund flow sets it (#123); today Q2 has no answer.
 */
class OrderStatusSpec extends Specification {

    def "should still emit every status that stored order rows carry"() {
        expect: "a rename fails here, not as an empty order filter after an upgrade"
        OrderStatus.values()*.name().containsAll(STORED_ORDER_STATUSES)
    }
```
All four answers are written down. The constant with no answer to Q2 gets no test yet. (Real evidence: ledger row V1.)

### V2 — Assert what the owner emits, not how the code is built

**Bad** (neutral)
```groovy
    def "the declined-payment code carries its problem type"() {
        expect: "the member found by its Java name"
        ErrorCode.valueOf('PAYMENT_DECLINED').problemType() == "https://example.com/errors/PAYMENT_DECLINED"
    }
```
It reaches the problem type through a Java enum member name. Renaming the member breaks it while every problem type a
client sees stays the same.

**Good** (neutral)
```groovy
    def "should still produce every problem type clients already handle after the refactor"() {
        expect: "nothing a client already switches on has been lost"
        (PUBLISHED_PROBLEM_TYPES - ErrorCode.values()*.problemType()).isEmpty()
    }
```
It asserts the problem-type strings clients see. A rename that keeps them passes, and a lost one is named. (Real
evidence: ledger row V2.)

### V3 — A junk pattern names the contract it guards, or it does not land

**Bad** (neutral)
```groovy
        OrderStatus.valueOf("REFUNDED") != null
        ["DRAFT", "PLACED", "PAID", "SHIPPED", "CANCELLED"]
                .every { OrderStatus.valueOf(it) != null }
```
Junk pattern 3, a hand-copied list of enum members, with no stored or emitted form named as its contract.

**Good** (neutral)
```groovy
    /**
     * The statuses order rows already store and /api/orders returns, verbatim.
     * Hand-copied on purpose (junk pattern 3, contract named): never derive this list from the enum.
     */
    static final List<String> STORED_ORDER_STATUSES = [
        "DRAFT",
        "PLACED",
        "PAID",
        "SHIPPED",
        "CANCELLED",
    ]
```
Still pattern 3, but it names the storage and API contract it guards and says why it must not be derived. (Real
evidence: ledger row V3.)

### V4 — One regression test, at the owning boundary

**Bad** (neutral)
```groovy
// BillingConsumerSpec — unit, StreamOperations mocked
    def "should not read as consumer-1"() {
        when: "the consumer polls once"
        consumer.poll()

        then: "the read names a consumer other than the old shared literal"
        1 * streamOps.read({ Consumer c -> c.name != "consumer-1" }, _, _)
    }
// …the same feature again in NotificationsConsumerSpec and a smoke spec
```
The same bug is replayed at every consumer and layer. The mocked copies cannot see Redis merge two names.

**Good** (neutral)
```groovy
    @Issue("#123")
    def "should register the injected identity on #group"() {
        // given: / when: as in S4 Good
        then: "the group holds this process's identity"
        names.contains(consumerIdentity.name())

        and: "and never the literal every consumer used to share"
        !names.contains("consumer-1")

        where:
        group << [BillingConsumer.GROUP, NotificationsConsumer.GROUP]
    }
```
The regression lives once, in Redis where the bug shows, with one row per consumer group. (Evidence: ledger row V4,
adapted.)

### V5 — Keep a test that guards a promised default

**Bad** (n/a) — no deletion of a contract-guarding test without proof was found; recent deletions were replacements
that name their successor.

**Good** (neutral)
```groovy
/** #123 AC-2 — an order created through the app starts as a draft. */
class OrderEntityStatusSpec extends Specification {

    @Issue(["#123", "AC-2"])
    def "should start a new order entity as a draft"() {
        expect: "Hibernate writes it on every INSERT, so a default of PLACED would override V12's column default"
        new OrderEntity().status == OrderStatus.DRAFT
    }
}
```
It looks like field-default junk but guards a promised default tied to migration V12, so it is kept. (Evidence: ledger
row V5.)

## Decided edges

- **Skip when** a junk-pattern test names the contract it independently guards, as a hand-copied list that names the
  stored form and says why it must not be derived (V3 Good). — **Do not skip when** no contract is named: the match
  fails V3. — **Confidence** high
- **Skip when** a test that asserts a field default guards a promised default, such as one a migration relies on: keep
  it (V5 Good) over S2 (`strategy.md`). — **Do not skip when** nothing promises the default: S2 applies.
  — **Confidence** high
- **Skip when** an existing test must change for a behaviour-preserving reorganisation: it is suspect, not
  automatically deletable; V5 decides (openclaw :71-73). — **Do not skip when** the test is new: V2 rejects it before
  it lands. — **Confidence** high
- **Skip when** a second layer has its own distinct risk the owner cannot reach, such as a transport or lifecycle
  failure: it gets its own test (openclaw :24-26, GT5 `scenario-to-tests.md`). — **Do not skip when** it re-asserts
  what the owner proves: that is junk pattern 7 and a V4 replay. — **Confidence** high

## Review checks

Walk every test the change adds, changes or removes.

- [ ] V1 — For each added test, find a one-line answer to each of the four questions: contract, realistic regression,
  why existing coverage misses it, production seam. A missing answer, or a seam no production caller uses, is a
  finding.
- [ ] V2 — For each added test, ask whether a rename or move that keeps the output would break it. A test that would
  break is a finding.
- [ ] V3 — Check each added test against all eight junk-pattern rows. A match that names no contract it guards is a
  finding.
- [ ] V4 — For each bug fix, list the tests that replay the bug's scenario. More than one, without a distinct risk per
  extra layer, is a finding.
- [ ] V5 — For each removed test (`git diff --diff-filter=D`, and removed features), check all five retention rows. A
  removal where a row holds, a removal with no proof of junk, or a removal because the test is slow or static, is a
  finding.
