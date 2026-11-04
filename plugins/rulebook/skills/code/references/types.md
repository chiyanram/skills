# Types

How Java types carry absence, closed sets, legal combinations, meaning, money and construction. Read it when you
write or review a field, a parameter, a return type, a record, an enum, a sealed type or a generic type.

Contents: Rules · When X, use Y · Good / Bad (TY1, TY3, TY9, TY8) · Decided edges · Review checks

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
- **TY9** — Strengthen a type only where partiality appears: a cast, a null check, a "never happens" throw; elsewhere
  keep the plain type, because only there is the type too weak to stop a runtime failure.
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
| a method that may have no result | an `Optional` return type (TY1) | a `null` return is a check the caller can forget, and the forgotten check throws `NullPointerException` |
| a field that may be absent and would pick a branch | a sealed case or an enum (TY1) | a boolean plus nullable fields lets contradictory states exist |
| a closed set of cases | a sealed type or an enum, switched over arrow-form with every case and no `default` (TY2) | without a `default`, the compiler fails when a new case is not handled |
| a record whose fields are legal only in some combinations | one record per legal shape under a sealed interface; the compact constructor for what the shapes cannot exclude (TY3) | a shape that cannot be built needs no check in any caller |
| external data: a request body, a row, config | a parse into domain types in its adapter (TY12) | data is untyped until it is parsed, and an unparsed null throws deep in the logic |
| a cast, a null check or a "never happens" throw | the check moved into the type, where the value is built (TY9) | that place marks a type too weak to stop a runtime failure |
| an operation with an answer for every input | the plain type (TY9) | nothing there can fail, so a stronger type adds nothing |
| a method whose type is a collection or an array | an empty one for "none", never `null` (TY7) | every caller must null-check a `null` collection, and one that forgets throws |
| a method whose type is `Optional` | `Optional.empty()` for "none", never `null` (TYN1) | a caller of an `Optional` expects empty, not `null`, and throws on it |
| two parameters of one primitive or `String` type that mean different things | one small wrapping record per meaning (TY8) | swapped same-typed arguments compile and corrupt data silently |
| a field | `final`, unless it is reassigned after construction (TY4) | a mutable field makes the object unsafe to share across threads |
| an amount of money | `BigDecimal` built from a `String` or `valueOf`, or a `long` of minor units (TY5) | binary floating point cannot hold 0.10 exactly, so totals drift |
| a closed set of states, roles or modes | an enum, persisted by name (TY6) | a misspelt string compiles, and a reordered enum remaps stored ordinals |
| an enum comparison | `==`, and a compile-time check on `equals` between unrelated types (TY11) | `equals` between unrelated types compiles and is always false |
| an unchecked warning | the generic type fixed; else `@SuppressWarnings("unchecked")` on the smallest declaration, with a comment saying why it is safe (TY10); any other suppression is CM7, `comments.md` | a raw type turns a compile error into a runtime `ClassCastException` |
| a simple value to construct | its record constructor or a static factory; a builder only for many optional parts (TY13) | a builder for a simple value is a second construction API to keep in step |

## Good / Bad

### TY1 — Return absence as an `Optional`

**Bad**
```java
public Address findShippingAddress(final String customerId) {
    return addressesByCustomer.get(customerId);
}

final Address address = addressBook.findShippingAddress(customerId);
if (address == null) {
    return Label.pickUpInStore();
}
return Label.shipTo(address);
```
The `null` return chooses the path. A caller that forgets the check compiles and fails at runtime.

**Good**
```java
public Optional<Address> findShippingAddress(final String customerId) {
    return Optional.ofNullable(addressesByCustomer.get(customerId));
}

return addressBook.findShippingAddress(customerId)
        .map(Label::shipTo)
        .orElseGet(Label::pickUpInStore);
```
The return type states that the address can be absent. The caller must handle both cases to get a `Label`.

### TY3 — Sealed variants exclude forbidden combinations

**Bad**
```java
public record Delivery(boolean delivered, Instant deliveredAt) {}

final var delivery = new Delivery(true, null);
```
"Delivered, but at no time" compiles. Every reader must work out again which combinations are legal.

**Good**
```java
public sealed interface Delivery {
    record Pending() implements Delivery {}
    record Delivered(Instant at) implements Delivery {}
}

static String describe(final Delivery delivery) {
    return switch (delivery) {
        case Delivery.Pending pending -> "on its way";
        case Delivery.Delivered delivered -> "delivered at " + delivered.at();
    };
}
```
Each legal shape is its own record, so the forbidden mix cannot be built. The switch names both cases, with no
`default`.

### TY9 — Strengthen a type only where partiality shows

**Bad**
```java
public LineItem firstItem(final List<LineItem> items) {
    if (items.isEmpty()) {
        throw new IllegalStateException("an order always has an item");
    }
    return items.get(0);
}
```
The "never happens" throw marks partiality: the plain list is too weak for this operation.

**Good**
```java
public record NonEmptyItems(LineItem first, List<LineItem> rest) {}

public LineItem firstItem(final NonEmptyItems items) {
    return items.first();
}

public BigDecimal total(final List<LineItem> items) {
    return items.stream()
            .map(LineItem::price)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
}
```
A non-empty list is a first item plus the rest, so `firstItem` cannot fail. `total` has an answer for an empty list,
so it keeps the plain list.

### TY8 — Wrap a primitive when same-typed values could swap

**Bad**
```java
public void cancel(final String customerId, final String orderId) {
    // …
}

orders.cancel(orderId, customerId);
```
Both ids are a `String`. The swapped call compiles, and the build stays green.

**Good**
```java
public record CustomerId(String value) {}
public record OrderId(String value) {}

public void cancel(
        final CustomerId customerId,
        final OrderId orderId) {
    // …
}
```
`orders.cancel(orderId, customerId)` no longer compiles. The records check nothing, because the reason to wrap is the
swap.

## Decided edges

- **Skip when** the code maps a wire DTO inside its adapter: a `null` check there is the parse (TY12). — **Do not skip
  when** the value has left the adapter: external data is untyped until it is parsed at the boundary, so TY1
  applies. — **Confidence** high
- **Skip when** the operation has an answer for every input: keep the plain type (TY9). — **Do not skip when** the
  code needs a cast, a null check or a "never happens" throw to work. — **Confidence** high
- **Skip when** the switch is an old-style colon statement under a Checkstyle `MissingSwitchDefault` gate: that check
  asks for a `default` there and skips switch expressions. — **Do not skip when** the switch can be written
  arrow-form over a sealed type or an enum: write it so, with no `default` (TY2; Google Java Style §4.8.4.3 counts an
  enum switch that covers every value as exhaustive). — **Confidence** medium

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
- [ ] TY9 — For each cast, null check or "never happens" throw, the type is strengthened where the value is built,
  or it is a finding. A stronger type added where no such check existed is a finding.
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
