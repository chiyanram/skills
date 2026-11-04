# Modern Java

Which current-JDK language features and library calls Java code uses: records and collection copies, switch forms,
patterns, `Optional` unwrapping, overflow-checked arithmetic, obsolete APIs, preview features and the build's release
level. Read it when you write or review Java production code, a record, a `switch`, or a Maven or Gradle build file.

Contents: Rules · When X, use Y · Good / Bad (MJ2, MJ5, MJ4, MJ13, MJ10, MJ6) · Decided edges · Review checks

## Rules

- **MJ2** — In a record or class holding a collection, store `List.copyOf`/`Set.copyOf`/`Map.copyOf` of the argument,
  never the argument, a view or an array, because the caller keeps the original and can change the object later.
- **MJ5** — Write every `switch` arrow-form (`case X ->`), and make one that yields a value a switch expression,
  because a colon-form case without `break` falls through and a statement case can forget to assign.
- **MJ4** — Dispatch on a sealed type's subtypes with a pattern `switch`, never an `if`/`else if` chain of
  `instanceof` tests, because the chain has no exhaustiveness check, so a new subtype silently takes the last branch.
- **MJ9** — Never compile or run production code with `--enable-preview`; use only features final in the target JDK,
  because a preview feature may change or vanish next release, and its class files load only on that JDK.
- **MJ13** — Add, multiply or narrow counts and minor-unit money with `Math.addExact`, `multiplyExact` and
  `toIntExact`, never bare `+`, `*` or an `(int)` cast, because `int` and `long` overflow wraps silently to a wrong
  value.
- **MJ10** — Collect a stream with `toList()` when no one mutates the result, and with
  `Collectors.toCollection(ArrayList::new)` when the caller must; never mutate a `Collectors.toList()` result, because
  `toList()` throws on mutation and `Collectors.toList()` promises no mutability.
- **MJ12** — Unwrap an `Optional` with `map`, `orElse`, `orElseGet` or `orElseThrow`; never call `get()`, and never
  test `isPresent()` then `get()`, because `get()` hides that it throws `NoSuchElementException` when empty.
- **MJ1** — Declare an immutable data carrier as a record, never a class with hand-written accessors, `equals` and
  `hashCode`, because a field added later is easily left out of `equals` and `hashCode`.
- **MJ3** — Test and bind in one step with `x instanceof Type t`; never follow an `instanceof` test with a cast,
  because the repeated type name can drift from the test and the cast then throws `ClassCastException`.
- **MJ6** — Name an intentionally unused catch parameter, lambda parameter or pattern variable `_`, because a named
  unused variable reads as used and hides a forgotten use from the unused-variable check.
- **MJ16** — Never override `finalize()`; release a resource through `close()` under try-with-resources, or register a
  `Cleaner` as a safety net, because finalization is deprecated for removal and may run late or never.
- **MJ17** — Set the Java level with `--release` (Maven `maven.compiler.release` or `<release>`), never
  `-source`/`-target` or `maven.compiler.source`/`target`, because those compile against the build JDK's API and can
  emit classes that fail on the target JDK.
- **MJ14** — Use `ArrayList`, `HashMap`, `ArrayDeque` and `StringBuilder`, never `Vector`, `Hashtable`, `Stack` or
  `StringBuffer`; share state through a `java.util.concurrent` type, because the legacy classes synchronize every call
  and pay for locking nobody needs.
- **MJ15** — Box a primitive by autoboxing or `valueOf`, never `new Integer(..)`, `new Long(..)` or another wrapper
  constructor, because each constructor call allocates a fresh object that `==` and the value caches treat as
  distinct.
- **MJ8** — Write production code as named classes in a package; keep compact source files (no class header) to
  scripts outside `src/main`, because a compact source file cannot declare a package, so no class can import it.

## When X, use Y

| situation | use | why |
|---|---|---|
| a record or class that takes a `List`, `Set` or `Map` | its `copyOf`, stored in the compact constructor or field (MJ2) | the caller keeps the original list and can still change it |
| a record that needs a sequence of values | a `List` component, copied (MJ2); never an array component | an array stays mutable, and two equal arrays are never `equals` |
| a `switch` statement or a value picked per case | an arrow-form switch; a switch expression when it yields a value (MJ5) | an arrow case cannot fall through, and an expression case cannot skip the assignment |
| a branch per subtype of a sealed type | a pattern `switch` with one `case` per subtype (MJ4) | the compiler fails the build when a new subtype has no case |
| a feature or API that is preview in the target JDK | the final alternative, or wait for the release that finalizes it (MJ9) | preview class files load only on the JDK that built them |
| a sum, product or narrowing of counts or minor-unit money | `Math.addExact`, `multiplyExact`, `toIntExact` (MJ13) | an overflow throws at once instead of saving a wrong total |
| a stream collected to a list nobody changes | `toList()` (MJ10) | the list is unmodifiable, so a change fails loudly |
| a stream collected to a list the caller changes | `Collectors.toCollection(ArrayList::new)` (MJ10) | `Collectors.toList()` promises no mutability |
| an `Optional` to unwrap | `map`, `orElse`, `orElseGet` or `orElseThrow` (MJ12) | the call names what happens when it is empty |
| an immutable carrier of named values | a record (MJ1) | the compiler derives `equals`, `hashCode` and `toString` from every component |
| a type test that the code then uses | `x instanceof Type t`, with the binding (MJ3) | the type is written once, so test and cast cannot disagree |
| a catch parameter, lambda parameter or pattern variable the body never reads | `_` (MJ6) | the name says the value is unused on purpose |
| a class that holds a resource | `AutoCloseable` used under try-with-resources; a `Cleaner` as a safety net (MJ16) | a finalizer may run late or never |
| the Java level in a build file | `--release`, `maven.compiler.release` or `<release>` (MJ17) | it compiles against the target JDK's own API |
| a list, map, stack or string buffer in one thread | `ArrayList`, `HashMap`, `ArrayDeque`, `StringBuilder` (MJ14) | the legacy classes lock on every call |
| a list or map shared between threads | a `java.util.concurrent` type, such as `ConcurrentHashMap` (MJ14) | it is built for concurrent access |
| a boxed primitive | autoboxing or `valueOf` (MJ15) | a wrapper constructor always allocates a new object |
| a single-file script or a spike | a compact source file outside `src/main` (MJ8) | it has no package, so production code cannot import it |

## Good / Bad

### MJ2 — Copy a collection into the record

**Bad**
```java
public record Invoice(InvoiceId id, List<InvoiceLine> lines) {}

final var lines = new ArrayList<InvoiceLine>(draftLines);
final var invoice = new Invoice(invoiceId, lines);
lines.clear();
```
The record keeps the caller's list. `lines.clear()` empties the issued invoice, and its hash code changes in any set.

**Good**
```java
public record Invoice(InvoiceId id, List<InvoiceLine> lines) {
    public Invoice {
        lines = List.copyOf(lines);
    }
}
```
The record holds its own unmodifiable copy, so no caller can change it after construction.

### MJ5 — Arrow-form; a switch that yields a value is an expression

**Bad**
```java
PaymentStatus status;
switch (responseCode) {
    case 200:
    case 201:
        status = PaymentStatus.ACCEPTED;
    case 402:
        status = PaymentStatus.DECLINED;
        break;
    default:
        status = PaymentStatus.RETRY;
}
```
The missing `break` lets 200 fall into 402, so an accepted payment reads as declined.

**Good**
```java
final PaymentStatus status = switch (responseCode) {
    case 200, 201 -> PaymentStatus.ACCEPTED;
    case 402 -> PaymentStatus.DECLINED;
    default -> PaymentStatus.RETRY;
};
```
No case can fall through, and the compiler rejects a case that yields nothing.

### MJ4 — Pattern `switch` over a sealed type

**Bad**
```java
String describe(final Payment payment) {
    if (payment instanceof Payment.Card card) {
        return "card ending " + card.last4();
    } else if (payment instanceof Payment.Transfer transfer) {
        return "transfer " + transfer.reference();
    }
    throw new IllegalStateException("unknown payment");
}
```
`Payment` is a sealed interface. A new subtype compiles and reaches the throw at runtime.

**Good**
```java
String describe(final Payment payment) {
    return switch (payment) {
        case Payment.Card card -> "card ending " + card.last4();
        case Payment.Transfer transfer -> "transfer " + transfer.reference();
    };
}
```
A new subtype fails the build at this switch, and the "never happens" throw is gone.

### MJ13 — Overflow-checked arithmetic on money

**Bad**
```java
long lineTotalMinor(final OrderLine line) {
    return line.unitPriceMinor() * line.quantity();
}
```
A large quantity wraps to a negative total, and no exception is thrown.

**Good**
```java
long lineTotalMinor(final OrderLine line) {
    return Math.multiplyExact(line.unitPriceMinor(), line.quantity());
}
```
An overflow throws `ArithmeticException` at the multiplication instead of saving a wrong invoice total.

### MJ10 — `toList()` is unmodifiable

**Bad**
```java
List<Invoice> overdueInvoices(final List<Invoice> invoices, final Instant now) {
    final List<Invoice> overdue = invoices.stream()
            .filter(invoice -> invoice.dueAt().isBefore(now))
            .toList();
    overdue.sort(Comparator.comparing(Invoice::dueAt));
    return overdue;
}
```
`sort` throws `UnsupportedOperationException`, because `toList()` is unmodifiable.

**Good**
```java
List<Invoice> overdueInvoices(final List<Invoice> invoices, final Instant now) {
    return invoices.stream()
            .filter(invoice -> invoice.dueAt().isBefore(now))
            .sorted(Comparator.comparing(Invoice::dueAt))
            .toList();
}
```
The sort happens inside the pipeline. A caller that must add to the result collects with
`Collectors.toCollection(ArrayList::new)`.

### MJ6 — `_` for a pattern variable the arm never reads

**Bad**
```java
Fee feeFor(final Payment payment) {
    return switch (payment) {
        case Payment.Card card -> Fee.CARD;
        case Payment.Transfer transfer -> Fee.NONE;
    };
}
```
The names `card` and `transfer` suggest that the arm reads the payment.

**Good**
```java
Fee feeFor(final Payment payment) {
    return switch (payment) {
        case Payment.Card _ -> Fee.CARD;
        case Payment.Transfer _ -> Fee.NONE;
    };
}
```
`_` states that only the type decides the fee.

## Decided edges

- **Skip when** the class is a JPA entity: the persistence provider needs a mutable, non-final class with a
  no-argument constructor (MJ1). — **Do not skip when** the class is a DTO, an event, a settings group or a value:
  declare it as a record. — **Confidence** high
- **Skip when** a switch over an `int` or a `String` ends in `default ->`: for such a selector, `default` is the only
  label that covers the unlisted values (MJ5). — **Do not skip when** the selector is a sealed type or an enum: list
  every case, with no `default` (TY2, `types.md`). — **Confidence** high
- **Skip when** `copyOf` or `Collectors.toUnmodifiableList()` throws `NullPointerException` on a `null` element: that
  is intended, because no domain collection holds `null` (TY12, `types.md`). — **Do not skip when** the fix would be a
  copy that admits `null`: parse the `null` away in the adapter instead (MJ2, MJ10). — **Confidence** high
- **Skip when** the project's target JDK is older than the release that made a feature final: write the form that
  JDK offers (MJ1–MJ17). — **Do not skip when** the target JDK has the feature: use it; a new project targets the
  newest JDK the team runs. — **Confidence** high

## Review checks

Walk every changed Java file under the production source tree and every changed build file. Where a build gate (for
example an Error Prone check) already enforces a rule, cite the gate and skip the manual check.

- [ ] MJ2 — `grep -nE 'record [A-Z][A-Za-z0-9]*(<[^>]*>)?\([^)]*((List|Set|Map|Collection)<[^)]*\) *\{ *\}|\[\])'`.
  Each hit is a finding: a collection component with no compact constructor, or an array component. For every other
  record and constructor that takes a collection, a collection stored without `copyOf` is a finding.
- [ ] MJ5 — `grep -nE '\b(case [^>]*|default)[[:space:]]*:([[:space:]]|$)'`. Each colon-form label is a finding.
  A gate such as Error Prone `StatementSwitchToExpressionSwitch` replaces this check.
- [ ] MJ4 — `grep -nE 'else if \(.*instanceof'`. A chain of two or more type tests on one sealed-typed variable is a
  finding.
- [ ] MJ9 — `grep -rnE --include=pom.xml --include='*.gradle' --include='*.kts' --include='*.properties' -e '--enable-preview|enablePreview' .`.
  Each hit outside a test-only or tooling module is a finding.
- [ ] MJ13 — `grep -nE '(Minor|[Qq]uantity|[Cc]ount)\b(\(\))? *[-+*]=? |[-+*]=? *[A-Za-z_.]*(Minor|[Qq]uantity|[Cc]ount)\b|\(int\) *[A-Za-z(]'`.
  A `+`, `*` or `(int)` cast on a count or a minor-unit amount, outside a `*Exact` call, is a finding.
- [ ] MJ10 — `grep -nE 'Collectors\.toList\(\)'`: each hit is a finding. For each mutating call
  (`grep -nE '\b[a-z][A-Za-z0-9]*\.(add|addAll|remove|removeIf|replaceAll|set|sort|clear)\('`), a receiver that came
  from `toList()` or `Collectors.toList()` is a finding.
- [ ] MJ12 — `grep -nE '\.isPresent\(\)|\.get\(\)'`. A `get()` on an `Optional` is a finding, and so is an
  `isPresent()` that guards a `get()`.
- [ ] MJ1 — `grep -nE 'public (boolean equals|int hashCode)\('`. A class whose fields are all `final` and whose methods
  are only accessors plus these is a finding.
- [ ] MJ3 — `grep -nE 'instanceof [A-Za-z_][A-Za-z0-9_.]*(<[^>]*>)?[[:space:]]*(\)|&&|\|\|)'`. A test with no binding
  that is followed by a cast of the same expression is a finding.
- [ ] MJ6 — A named pattern variable, catch parameter or lambda parameter that the body never reads is a finding. A
  gate such as Error Prone `UnusedVariable` replaces this check.
- [ ] MJ16 — `grep -nE 'void finalize\(\)|runFinalization'`. Each hit is a finding.
- [ ] MJ17 — `grep -nE 'maven\.compiler\.(source|target)\b|<(source|target)>|(^|[[:space:]])-(source|target)[[:space:]]'`
  over `pom.xml` and build scripts. Each hit is a finding.
- [ ] MJ14 — `grep -nE '\b(Vector|Hashtable|Stack|StringBuffer)\b'`. Each hit is a finding, unless a third-party API
  signature requires the type.
- [ ] MJ15 — `grep -nE 'new (Integer|Long|Short|Byte|Character|Boolean|Double|Float)\('`. Each hit is a finding.
- [ ] MJ8 — `grep -rLE '^[[:space:]]*((public|protected|private|abstract|final|sealed|non-sealed|static|strictfp)[[:space:]]+)*(class|interface|enum|record|@interface)[[:space:]]' --include='*.java' src/main`.
  Each file listed, other than `package-info.java` and `module-info.java`, is a finding.
