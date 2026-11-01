# Types

How Java types carry absence, closed sets, legal combinations, meaning, money and construction. Read it when you
write or review a field, a parameter, a return type, a record, an enum, a sealed type or a generic type.

Contents: Rules · When X, use Y · Good / Bad (TY1, TY3, TY8, TY9) · Decided edges · Review checks

## Rules

- **TY1** — Never let `null` decide a case; model absence as an `Optional`, a sealed interface with records, or an
  enum, because nullable fields let contradictory field combinations compile.
- **TY2** — Make a closed set of two or more cases sealed or an enum, and switch over it with no `default` arm,
  because a `default` arm lets a new case compile and be silently mishandled.
- **TY3** — Model forbidden combinations away with sealed variants first; let a record's compact constructor reject
  only the combinations the variants cannot exclude, because a record that admits forbidden combinations leaves
  every caller guessing which are legal.
- **TY7** — Return an empty collection, never `null`, from a method that returns a collection, because a `null`
  collection forces every caller to null-check and causes bugs.
- **TY9** — Strengthen a type only where partiality appears: a cast, a null check, a "never happens" throw; elsewhere
  keep the plain type, because only there is the type too weak to stop a runtime failure.
- **TY12** — Allow `null` only while mapping a wire DTO; turn it into an `Optional`, a sealed case or an enum in the
  adapter, because an escaped null becomes a runtime failure the compiler could stop.
- **TY8** — Wrap a primitive in a domain type when two same-typed values could swap places, or when it carries an
  invariant, because two same-typed ids can swap places at a call site and still compile.
- **TY4** — Mark fields `final` always; mark locals and parameters `final` in new code; never edit an old line only
  to add `final`, because final fields keep an object immutable and safe to share across threads.
- **TY5** — Type money, cost and price as `BigDecimal` with explicit scale and rounding, and use `double` only for
  latencies and scores, because `double` arithmetic adds binary rounding errors to money.
- **TY6** — Model a closed set of states, roles or modes as an enum, never a string
  literal, and persist it as `EnumType.STRING`, because an ordinal breaks when the enum is reordered.
- **TY11** — Make an `equals` between an enum and a `String` fail the build (ErrorProne
  `EqualsIncompatibleType` or an ArchUnit rule), never leave it to review, because an equality test between
  incompatible types always returns false.
- **TY10** — Write no raw generic types; put `@SuppressWarnings("unchecked")` on one statement with the reason it is
  safe, never on a method or class, because a raw type bypasses generic checks and throws `ClassCastException` at
  runtime.
- **TY13** — Build a value with its record constructor or a static
  factory; name a single implementation `Default<Name>`, never `<Name>Impl`, because a builder is a second
  construction API to maintain, and `Impl` names no role.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a value that may be absent | `Optional` as a return type (JV6, `java.md`), a sealed interface with records, or an enum (TY1) | a bag of optional fields lets contradictory combinations compile (pstack :15); `Optional` states absence explicitly (pl141 :206) |
| a closed set of two or more cases | a sealed interface or an enum, and a switch with no `default` arm (TY2) | the compiler must fail when a new variant is not handled (pstack :20, :29); the compiler confirms every permitted subclass is covered (JEP 409) |
| a record whose fields are legal only in some combinations | one record per legal shape under a sealed interface; the compact constructor for what the shapes cannot exclude (TY3) | a comment that explains when fields are valid means the type is too loose (pstack :15, :26); sealed classes restrict the subclasses to model the domain (JEP 409); the compact-constructor clause is operator preference |
| two parameters of one primitive type that mean different things | one wrapping record per meaning (TY8) | same-typed arguments that mean different things are branded (pstack :17, :27); give the concept its own small type (mattpocock `code-review/SKILL.md` :49); type-safe wrappers (pl122 Example 4) |
| a cast, a null check or a "never happens" throw | the check moved into the type, where the value is built (TY9) | that place marks a type too weak (pstack :22, :28) |
| an operation with an answer for every input | the plain type (TY9) | if nothing would otherwise fail, keep the plain type (pstack :22, :31) |
| a wire DTO with a missing field | `null` inside the mapping only; `Optional`, a sealed case or an enum out of the adapter (TY12) | external data is untyped until parsed at the boundary (pstack :18) |
| an amount of money | `BigDecimal` with a set scale and rounding mode (TY5) | floating point is never for precise values such as currency (Java Tutorial *Primitive Data Types*); `BigDecimal` for precision (pl122 :670-672) |
| a method that returns a collection | an empty collection for "none" (TY7) | never return `null` from a method that returns a collection (pl121m :231-233) |
| an unchecked warning | the generic type fixed; else `@SuppressWarnings("unchecked")` on one statement, with its reason (TY10); any other suppression is CM7, `comments.md` | raw types defer generic type checks to runtime (Java Tutorial *Raw Types*); suppress only provably safe operations, as narrowly as possible (pl128 :1504-1506) |
| a value to construct | its record constructor or a static factory (TY13) | prefer constructors, static factories and records first (pl123 :22; pl121c Example 2) |

`pstack` is cursor-plugins pstack `skills/principle-type-system-discipline/SKILL.md`. `pl122` is plinth
`122-java-type-design.md`, `pl121m` is plinth `121-java-object-oriented-design-methods.md`, `pl128` is plinth
`128-java-generics.md`, `pl123` is plinth `123-java-design-patterns.md`, `pl141` is plinth
`141-java-refactoring-with-modern-features.md` and `pl121c` is plinth
`121-java-object-oriented-design-object-creation.md`. `:N` is the line.
TY4, TY6, TY7, TY9, TY11 and TY12 are operator preferences. TY7 follows pl121m :231-233, TY9 pstack :22, TY12
pstack :18, TY6 pl121-enums Example 2, and TY11 ErrorProne `EqualsIncompatibleType`.
TY3's sealed-variants part and TY13's constructor-or-factory part are industry; TY3's compact-constructor clause
and TY13's `Default<Name>` naming are operator preference.

Operator preference, 2026-10-31 (SRC2), in whole or in part: TY3, TY7, TY9, TY12, TY4, TY6, TY11 and TY13.

## Good / Bad

### TY1 — No `null` decides a case

**Bad** (neutral)
```java
private final FraudCheck fraudCheck;

OrderScreening(@Autowired(required = false) final FraudCheck fraudCheck) { this.fraudCheck = fraudCheck; }
// …
private Screening screen(final Order order, final boolean fraudCheckEnabled) {
    final RuleVerdict rules = orderRules.assess(order);
    // …
    if (fraudCheckEnabled && fraudCheck != null) {
        final List<FraudSignal> signals = fraudCheck.signalsFor(order);
        // … merge, return
    }
    return new Screening(rules, List.of());
}
```
A `null` field and a boolean together choose the path. With the flag on and no fraud-check bean, the check is skipped
in silence.

**Good** (neutral)
```java
public enum FraudCheckMode { OFF, ON }

private final OrderRules orderRules;
private final ObjectProvider<FraudCheck> fraudCheck;

private Screening screen(final Order order, final FraudCheckMode mode) {
    final RuleVerdict ruleVerdict = orderRules.assess(order);
    final List<FraudSignal> signals = switch (mode) {
        case OFF -> List.of();
        case ON -> fraudCheck.getObject().signalsFor(order);
    };
    return withSignals(ruleVerdict, signals);
}
```
The flag is an enum the switch must name. "ON but no fraud-check bean" now fails loudly instead of skipping. (Real
evidence: ledger row TY1.)

### TY3 — Sealed variants exclude forbidden combinations

**Bad** (neutral)
```java
if (request.pickupPointId() != null && !request.pickupPointId().isBlank()) {
    saved = service.shipToPickupPoint(request.orderId(), request.pickupPointId(), request.note(), userId);
} else if (request.street() != null && request.postcode() != null) {
    saved = service.shipToAddress(request.orderId(), request.street(), request.postcode(),
        request.note(), userId);
} else {
    throw new IllegalArgumentException("Either 'pickupPointId' or both 'street' + 'postcode' must be supplied");
}
```
The request record has nullable fields, so every reader works out the two legal shapes again. "Street without
postcode" still compiles.

**Good** (neutral)
```java
public sealed interface ShippingRequest {
    record Pickup(
            @NotNull UUID orderId,
            @NotBlank String pickupPointId,
            @Size(max = 500) String note) implements ShippingRequest {}
    record Address(
            @NotNull UUID orderId,
            @NotBlank String street,
            @NotBlank String postcode,
            @Size(max = 500) String note) implements ShippingRequest {}
}
```
"Pickup point, or street and postcode" is two records, so a forbidden mix cannot be built. The service switches over
both, with no `default`. (Real evidence: ledger row TY3.)

### TY8 — Wrap a primitive when same-typed values could swap

**Bad** (neutral)
```java
public Invoice issue(final long orderId, final long customerId, final long issuedBy,
                     final String note, final String notifyEmail) {
```
Three `long` ids and two `String`s in one signature. Any two ids can swap places at the caller, and the build stays
green.

**Good** (neutral)
```java
public record OrderId(long value) {}
public record CustomerId(long value) {}
public record UserId(long value) {}
public sealed interface NotifyTarget {
    record None() implements NotifyTarget {}
    record Email(String address) implements NotifyTarget {}
}
public Invoice issue(
        final OrderId orderId,
        final CustomerId customerId,
        final UserId issuedBy,
        final String note,
        final NotifyTarget notify) {
```
`issue(customerId, orderId, …)` no longer compiles. The id records check nothing, because the reason to wrap is the
swap. (Real evidence: ledger row TY8.)

### TY9 — Strengthen a type only where partiality shows

**Bad** (neutral)
```java
private int appendBetween(final List<String> whereParts,
                            final List<String> placeholderOrder,
                            final Map<String, Object> placeholderValues,
                            final int index,
                            final String quotedColumn,
                            final Object value) {
    if (!(value instanceof List<?> bounds) || bounds.size() != 2) {
        throw new IllegalArgumentException(
            "BETWEEN operator on " + quotedColumn + " requires a 2-tuple value");
    }
    // … two placeholder names, the BETWEEN fragment …
    placeholderValues.put(lowPlaceholder, bounds.get(0));
    placeholderValues.put(highPlaceholder, bounds.get(1));
    return index + 2;
}
```
An `Object` stands in for "two due dates". The `instanceof`, the size check and `get(0)` are partiality.

**Good** (neutral)
```java
record BetweenBounds(Object low, Object high) {}

private int appendBetween(
        final WhereClause where,
        final int index,
        final String quotedColumn,
        final BetweenBounds bounds) {
    final String lowPlaceholder = FILTER_PLACEHOLDER_PREFIX + index;
    final String highPlaceholder = FILTER_PLACEHOLDER_PREFIX + (index + 1);
    where.add(quotedColumn + " BETWEEN :" + lowPlaceholder + " AND :" + highPlaceholder);
    where.bind(lowPlaceholder, bounds.low());
    where.bind(highPlaceholder, bounds.high());
    return index + 2;
}
```
The check moves to where the filter is parsed, which builds `BetweenBounds` once. An operation that takes any list
keeps its plain list, because it is total. (Real evidence: ledger row TY9.)

## Decided edges

- **Skip when** a parameter or local sits on an old line that the change does not otherwise edit: leave it without
  `final` (TY4; a final-parameters gate would flag every existing signature). —
  **Do not skip when** the line is new, or the declaration is a field: fields are `final` always. — **Confidence**
  high
- **Skip when** the code maps a wire DTO inside its adapter: a `null` check there is allowed (TY12). — **Do not skip
  when** the value has left the adapter: TY1 applies. — **Confidence** high
- **Skip when** the operation has an answer for every input: keep the plain type (TY9, pstack :22). — **Do not skip
  when** the code needs a cast, a null check or a "never happens" throw to work. — **Confidence** high
- **Skip when** a large record really needs a builder, because many of its parameters are optional (pl121c
  Example 3): expose one builder (TY13, operator preference). — **Do not skip when** a constructor or a static
  factory reads clearly: TY13 applies. — **Confidence** medium

## Review checks

Walk every changed Java file.

- [ ] TY1 — Each `null` comparison or `return null` (`grep -nE "[!=]= null|return null"`) outside wire-DTO mapping
  is a finding. A `null` that chooses a path, where an `Optional`, a sealed type or an enum could, is a finding.
- [ ] TY2 — Each closed set of two or more cases is sealed or an enum. A `default` arm in a switch over a sealed type
  or an enum (`grep -nE "default ->|default:"`) is a finding.
- [ ] TY3 — A record whose fields are legal only in some combinations is a finding. A compact-constructor check that
  rejects a combination a sealed variant could exclude is a finding.
- [ ] TY7 — `return null` in a method whose return type is a collection is a finding.
- [ ] TY9 — For each cast, null check or "never happens" throw, the type is strengthened where the value is built,
  or it is a finding. A stronger type added where no such check existed is a finding.
- [ ] TY12 — A field, parameter or return value that can hold `null` outside a wire-DTO adapter is a finding.
- [ ] TY8 — A method with two or more parameters of one primitive type that could swap places at a call site is a
  finding, and so is an unwrapped primitive that carries an invariant.
- [ ] TY4 — A field without `final` is a finding. A new parameter without `final` is a finding. A changed line whose
  only change is an added `final` is a finding. Only where no gate enforces it (Checkstyle
  `FinalLocalVariable`): a new local without `final` is a finding.
- [ ] TY5 — Money, cost or price held in `double` or `float` is a finding. A `BigDecimal` division or rescale with no
  explicit scale and `RoundingMode` is a finding.
- [ ] TY6 — A state, role or mode held or compared as a string literal is a finding. `@Enumerated` without
  `EnumType.STRING` is a finding.
- [ ] TY11 — The build carries ErrorProne `EqualsIncompatibleType` or an ArchUnit rule for enum-to-`String`
  `equals`. A build with neither is a finding.
- [ ] TY10 — A raw generic type is a finding. `@SuppressWarnings("unchecked")` on a method or class, or with no
  reason beside it, is a finding.
- [ ] TY13 — A builder on a value that a constructor or a static factory serves is a finding. A single
  implementation named `<Name>Impl` is a finding.
