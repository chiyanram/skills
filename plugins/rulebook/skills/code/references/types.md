# Types

How Java types carry absence, closed sets, legal combinations, meaning, money and construction. Read it when you
write or review a field, a parameter, a return type, a record, an enum, a sealed type or a generic type.

Contents: Rules · When X, use Y · Good / Bad (TY1, TY3, TY12, TY8) · Decided edges · Review checks

## Rules

- **TY1** — Return absence as an `Optional`; model a field that may be absent as a sealed case or an enum, never a
  nullable field that picks a branch, because a forgotten null check throws `NullPointerException`.
- **TY2** — Model a closed set as a sealed type or enum; switch over it arrow-form, listing every case, with no
  `default`, because a `default` lets a new case compile and be silently mishandled.
- **TY3** — Make forbidden field combinations unbuildable with sealed record variants; check in a compact constructor
  only the invariants the variants cannot exclude, because a record that admits forbidden combinations leaves every
  caller re-checking them.
- **TY12** — Parse external data (request bodies, rows, config) into domain types in the adapter, turning each
  nullable wire field into an `Optional`, sealed case or enum, because an unparsed null reaches logic and throws
  `NullPointerException`.
- **TY7** — Return an empty collection or array, never `null`, from a method whose type is a collection or array,
  because every caller must null-check and one that forgets throws `NullPointerException`.
- **TYN1** — Never return `null` from a method whose type is `Optional`, and never compare an `Optional` to `null`,
  because a null `Optional` throws `NullPointerException` where the caller expected empty.
- **TY8** — Wrap a primitive or `String` in a small record when two same-typed parameters could swap or the value
  carries an invariant, because swapped ids compile and corrupt data silently.
- **TY4** — Declare every field `final` unless it is reassigned after construction, because a mutable field makes an
  object unsafe to share across threads.
- **TY5** — Hold money as `BigDecimal` (built from a `String` or `valueOf`) or as a `long` of minor units, never
  `float` or `double`, because binary floating point cannot represent 0.10 exactly and totals drift.
- **TY6** — Model closed sets of states, roles or modes as enums, never `String` or `int` constants; persist by name,
  not ordinal, because a misspelt string compiles and a reordered enum remaps stored ordinals.
- **TY11** — Compare enum values with `==`, and turn on a compile-time check (Error Prone `EqualsIncompatibleType` or
  equivalent) that fails on `equals` between unrelated types, because such an `equals` compiles and is always false.
- **TY10** — Write no raw generic types; put `@SuppressWarnings("unchecked")` on the smallest declaration (one local
  variable), with a comment saying why the cast is safe, because a raw type turns a compile error into a runtime
  `ClassCastException`.
- **TY13** — Build a simple value with its record constructor or static factory; use a builder only for a type with
  many optional parts, because such a builder is a second construction API to maintain.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a method that may have no result | an `Optional` return type (TY1) | `Optional` is meant for a return type where `null` "is likely to cause errors" (OpenJDK `Optional` apiNote, r48 :117) |
| a field that may be absent and would pick a branch | a sealed case or an enum (TY1) | a boolean plus optionals lets contradictory states exist (pstack `typescript-best-practices` patterns.md :33, r48 :117) |
| a closed set of cases | a sealed type or an enum, switched over arrow-form with every case and no `default` (TY2) | removing the default lets Error Prone enforce that every case stays handled (Error Prone `UnnecessaryDefaultInEnumSwitch`, r48 :124); `default` over a sealed type is almost never necessary (OpenJDK amber exhaustiveness guide, r48 :124) |
| a record whose fields are legal only in some combinations | one record per legal shape under a sealed interface; the compact constructor for what the shapes cannot exclude (TY3) | build the shape so the illegal value cannot be constructed (pstack `typescript-best-practices` :16, r48 :131); invariants enforced by the constructor can be relied on (OpenJDK records-and-sealed note, r48 :131) |
| external data: a request body, a row, config | a parse into domain types in its adapter (TY12) | have a parse function at every boundary (pstack `principle-type-system-discipline`, r48 :149); validate external data at system boundaries before use in logic (addy `code-review-and-quality` :75, r48 :149) |
| a method whose type is a collection or an array | an empty one for "none", never `null` (TY7) | always return an empty array or collection instead (Effective Java Item 54, r48 :136); also Sonar S1168 (r48 :136) |
| a method whose type is `Optional` | `Optional.empty()` for "none", never `null` (TYN1) | a variable of type `Optional` should never itself be `null` (OpenJDK `Optional` apiNote, r48 :202); also Sonar S2789 (r48 :202) |
| two parameters of one primitive or `String` type that mean different things | one small wrapping record per meaning (TY8) | two arguments that share a primitive type but mean different things are branded (pstack `principle-type-system-discipline`, r48 :155); a primitive standing in for a domain concept gets its own small type (mattpocock `code-review` :49, r48 :155) |
| a field | `final`, unless it is reassigned after construction (TY4) | make all fields final (Effective Java Item 17, r48 :161); also Sonar S9438 (r48 :161) |
| an amount of money | `BigDecimal` built from a `String` or `valueOf`, or a `long` of minor units (TY5) | float and double are not suited for monetary calculations; use BigDecimal, int or long (Effective Java Item 60, r48 :169); `new BigDecimal(0.1)` is not exactly 0.1 (Error Prone `BigDecimalLiteralDouble`, r48 :169) |
| a closed set of states, roles or modes | an enum, persisted by name (TY6) | `int` constants for enum types are obsolete (Effective Java Item 34, r48 :176); an ordinal is not stable across builds (Error Prone `EnumOrdinal`, r48 :176) |
| an enum comparison | `==`, and a compile-time check on `equals` between unrelated types (TY11) | `equals` between incompatible types always returns false (Error Prone `EqualsIncompatibleType`, r48 :183); also Sonar S4551 (r48 :183) |
| an unchecked warning | the generic type fixed; else `@SuppressWarnings("unchecked")` on the smallest declaration, with a comment saying why it is safe (TY10); any other suppression is CM7, `comments.md` | raw types will probably fail at runtime (Effective Java Item 26, r48 :190); suppress as close to the declaration as possible and comment on why it is safe (Effective Java Item 27, r48 :190) |
| a simple value to construct | its record constructor or a static factory; a builder only for many optional parts (TY13) | static factories have names, and a builder suits a constructor with many arguments (Effective Java Items 1–2, r48 :197); also Sonar S6206 (r48 :197) |

`r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source, read at the
commit it names.

## Good / Bad

### TY1 — Absence is an `Optional`, a sealed case or an enum, never a nullable field that picks a branch

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
The flag is an enum the arrow-form switch must name in full. "ON but no fraud-check bean" now fails loudly instead of
skipping. (Real evidence: ledger row TY1.)

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

### TY12 — Parse external data into domain types in its adapter

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
An unparsed request value, an `Object`, stands in for "two due dates". The `instanceof`, the size check and `get(0)`
run deep in the SQL builder.

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
The filter value is parsed once into `BetweenBounds` where the request filter is read, so the builder needs no cast and
no size check. (Pair: research/68f § TY12. Real evidence: ledger row TY12.)

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

## Decided edges

- **Skip when** the code maps a wire DTO inside its adapter: a `null` check there is the parse (TY12). — **Do not skip
  when** the value has left the adapter: external data is untyped until it is parsed at the boundary (pstack
  `principle-type-system-discipline`, r48 :149), so TY1 applies. — **Confidence** high
- **Skip when** the switch is an old-style colon statement under a Checkstyle `MissingSwitchDefault` gate: that check
  asks for a `default` there and skips switch expressions (r48 :125). — **Do not skip when** the switch can be written
  arrow-form over a sealed type or an enum: write it so, with no `default` (TY2; Google Java Style §4.8.4.3 counts an
  enum switch that covers every value as exhaustive, r48 :125). — **Confidence** medium

## Review checks

Walk every changed Java file.

- [ ] TY1 — For each `return null;` (`grep -nE "return null;"`), a method that could return `Optional` is a finding.
  For each `null` comparison (`grep -nE "[!=]= null"`) outside a wire-DTO adapter, a nullable field that picks a
  branch, where a sealed case or an enum could, is a finding.
- [ ] TY2 — A closed set held as anything but a sealed type or an enum is a finding. A `default` in a switch over a
  sealed type or an enum (`grep -nE "default *(->|:)"`) is a finding, and so is such a switch that is not arrow-form
  or does not list every case.
- [ ] TY3 — A record whose fields are legal only in some combinations is a finding. A compact-constructor check that
  rejects a combination a sealed variant could exclude is a finding.
- [ ] TY12 — External data (a request body, a row, config) that reaches logic before its adapter parses it into domain
  types is a finding, and so is a nullable wire field that leaves the adapter as `null`.
- [ ] TY7 — `return null` in a method whose return type is a collection or an array is a finding.
- [ ] TYN1 — For each `return null;` and each `null` comparison (`grep -nE "return null;|[!=]= null"`), a method
  whose type is `Optional`, or an operand whose type is `Optional`, is a finding.
- [ ] TY8 — A method signature with two or more parameters of one primitive or `String` type that could swap at a
  call site is a finding, and so is an unwrapped primitive or `String` that carries an invariant.
- [ ] TY4 — A field without `final` that nothing reassigns after construction is a finding.
- [ ] TY5 — Money held in `float` or `double` is a finding. For each `BigDecimal` constructor whose argument is not a
  string literal (`grep -nE 'new BigDecimal\([^"]'`), a `double` argument is a finding.
- [ ] TY6 — A state, role or mode held or compared as a `String` or `int` constant is a finding. An enum persisted by
  ordinal (`grep -nE "@Enumerated *(\(EnumType\.ORDINAL\))?$|\.ordinal\(\)"`) is a finding.
- [ ] TY11 — An enum compared with `equals` instead of `==` is a finding. A build without Error Prone
  `EqualsIncompatibleType` or an equivalent compile-time check is a finding.
- [ ] TY10 — A raw generic type is a finding. `@SuppressWarnings("unchecked")`
  (`grep -nE '@SuppressWarnings\("unchecked"\)'`) on a method or a class, or with no comment saying why the cast is
  safe, is a finding.
- [ ] TY13 — A hand-written builder for a value with few or no optional parts is a finding.
