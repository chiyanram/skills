# Java

How plain Java code handles time, streams, `toMap`, `BigDecimal` equality, `var`, `Optional`, strings, resources,
braces and line length. Read it when you write or review Java production code.

Contents: Rules · When X, use Y · Good / Bad (U4, JV1, JV5, CV3) · Decided edges · Review checks

## Rules

- **U4** — When logic reads the current time, take an injected `Clock` and call `now(clock)`, never no-argument
  `now()`, because the wall clock cannot be fixed in a test, so the test flakes at midnight or across zones.
- **JV1** — Compute time in `java.time` types (`Instant`, `Duration`), never `Date`, `Calendar` or a raw `long` of
  millis; convert only at a library or display edge, because `Date` and its formatters are mutable and not
  thread-safe.
- **JV2** — Use sequential streams in request- or queue-serving code; never `parallelStream()` or `.parallel()`,
  because parallel streams run on the one JVM-wide common pool, so one blocking task stalls every other user of it.
- **JV3** — Keep `map`, `filter` and other stream lambdas free of I/O, logging and mutation, and do not use `peek` for
  work, because the stream may skip those calls, so the effect silently does not happen.
- **JV4** — Give every `toMap` a merge function, because `toMap` throws `IllegalStateException` at runtime on a
  duplicate key.
- **JVN1** — Compare `BigDecimal` values with `compareTo`, never `equals`, because `equals` treats 2.0 and 2.00 as
  different.
- **JV5** — Use `var` only when the initializer names the type (constructor, factory, literal); otherwise write the
  type, and never pair `var` with `<>`, because the reader cannot see the type and diamond infers `Object`.
- **JV6** — Use `Optional` only as a return type, never as a field, parameter or collection element, because an
  `Optional` parameter has three states (null, empty, present) and every callee must check all three.
- **JV7** — Write a multi-line SQL, JSON or HTML string as a text block, never as `+`-joined literals with `\n`,
  because escaped concatenation hides the text's shape and invites a missing newline.
- **JV8** — Open every I/O-backed `AutoCloseable` (stream, reader, connection) in a try-with-resources header, because
  a resource not closed when an exception fires leaks until the process runs out of handles.
- **JV9** — Put braces on every `if`, `else`, `for`, `do` and `while` body, because a line added under a brace-less
  body looks guarded but always runs.
- **CV3** — Let the formatter decide wrapping: the configured line length for Java
  and Groovy, Prettier for TypeScript, because a hand-wrapping rule that differs from the formatter fights its output.

## When X, use Y

| situation | use | why |
|---|---|---|
| the logic reads the current time | an injected `Clock`, called as `now(clock)` (U4); the test's fixed clock is U1 ([unit-tests.md](../../testing/references/unit-tests.md)) | a test cannot fix the wall clock, so a test that reads it flakes at midnight or across zones |
| a point or a span of time | `Instant`, `Duration` or another `java.time` type; `Date` only at a library or display edge (JV1) | `Date`, `Calendar` and their formatters are mutable and not thread-safe |
| a stream in request- or queue-serving code | a sequential stream (JV2) | a parallel stream runs on the JVM-wide common pool, so one blocking task stalls every user of it |
| an I/O, logging or state-changing step in a stream | that step outside the pipeline (JV3) | the stream may skip a lambda's call, so the effect silently does not happen |
| a `toMap` | the three-argument form, with a merge function (JV4) | a duplicate key throws `IllegalStateException` at runtime |
| two `BigDecimal` values to compare | `compareTo` (JVN1) | `equals` compares the scale as well as the value, so 2.0 and 2.00 differ |
| a local variable | `var` when the initializer names the type; else the type written out; never `var` with `<>` (JV5) | the reader cannot see a type the initializer hides, and `var` with a diamond infers `Object` |
| a value that can be absent | `Optional` as the return type only (JV6) | an `Optional` parameter has three states, and every callee must check all three |
| a multi-line SQL, JSON or HTML string | a text block (JV7) | escaped concatenation hides the text's shape and invites a missing newline |
| an I/O-backed `AutoCloseable` opened in a method | a try-with-resources header (JV8) | a resource not closed when an exception fires leaks until the process runs out of handles |
| an `if`, `else`, `for`, `do` or `while` body | braces, even for one statement (JV9) | a line added under a brace-less body looks guarded but always runs |
| a long Java, Groovy or TypeScript line | the formatter's wrapping (CV3) | a hand-wrapping rule that differs from the formatter fights its output |

## Good / Bad

### U4 — Take an injected Clock; never call the wall clock directly

**Bad**
```java
final class InvoiceSchedule {

    boolean isOverdue(final Instant dueAt) {
        return Instant.now().isAfter(dueAt);
    }
}
```
The check reads the wall clock. A test cannot pin "due one second ago" against "due in one second".

**Good**
```java
final class InvoiceSchedule {

    private final Clock clock;

    InvoiceSchedule(final Clock clock) {
        this.clock = clock;
    }

    boolean isOverdue(final Instant dueAt) {
        return Instant.now(clock).isAfter(dueAt);
    }
}
```
The clock comes in through the constructor. A test passes `Clock.fixed(...)` and pins the boundary exactly.

### JV1 — Time is an `Instant` or a `Duration`

**Bad**
```java
private static final SimpleDateFormat FORMAT = new SimpleDateFormat("yyyy-MM-dd");

String reminderDate(final Date issuedAt) {
    final Calendar calendar = Calendar.getInstance();
    calendar.setTime(issuedAt);
    calendar.add(Calendar.DAY_OF_MONTH, 30);
    return FORMAT.format(calendar.getTime());
}
```
The arithmetic runs on a mutable `Calendar`. The shared `SimpleDateFormat` is not synchronized, so two threads can
corrupt each other's output.

**Good**
```java
private static final Duration PAYMENT_TERM = Duration.ofDays(30);
private static final DateTimeFormatter FORMAT = DateTimeFormatter.ISO_LOCAL_DATE
        .withZone(ZoneOffset.UTC);

String reminderDate(final Instant issuedAt) {
    final Instant remindAt = issuedAt.plus(PAYMENT_TERM);
    return FORMAT.format(remindAt);
}
```
The point is an `Instant` and the span a `Duration`. A zone enters only in the formatter, at the display boundary.

### JV5 — `var` only when the initializer names the type

**Bad**
```java
final var pending = new ArrayList<>();
final var summary = summarise(pending);
```
The diamond infers `ArrayList<Object>`. The name `summarise` does not tell the reader what type comes back.

**Good**
```java
final var pending = new ArrayList<Invoice>();
final var dueDate = LocalDate.parse(dueDateText);
final InvoiceSummary summary = summarise(pending);
```
A constructor and a factory show the type, so `var` stays. `summarise` names an action, not a type, so the type is
written out.

### CV3 — TypeScript wrapping is Prettier's

**Bad**
```ts
const overdue = invoices.filter((invoice) => invoice.dueAt < today &&
    invoice.status === "open");
```
The line is wrapped by hand, in a Java style. `prettier --check` flags the file, and the next format run rewrites it.

**Good**
```ts
const overdue = invoices.filter(
  (invoice) => invoice.dueAt < today && invoice.status === "open",
);
```
This is the shape Prettier prints. Nobody wraps TypeScript by hand, so the formatter and the reviewer never disagree.

## Decided edges

- **Skip when** a framework's own style guide bans `var` (for example Spring Framework's): that ban serves a library
  read without an IDE, and JV5 already stops `var` from hiding a type. — **Do not skip when** the initializer does
  not name the type: write the type (JV5). — **Confidence** high
- **Skip when** the `AutoCloseable` is not backed by I/O, such as a `Stream` over a collection: try-with-resources is
  in general unnecessary there. — **Do not skip when** it holds a file, a socket or a connection: JV8 applies. —
  **Confidence** high

## Review checks

Walk every changed Java file under the production source tree. Where a build gate (for example Checkstyle) already
enforces JV2, JV6 or JV9, cite the gate and skip the manual check.

- [ ] U4 — `grep -nE "\.now\(\)"`. A no-argument `now()` in logic is a finding; it takes an injected `Clock` and calls
  `now(clock)`.
- [ ] JV1 — `grep -nE "java\.util\.Date|Calendar|SimpleDateFormat|currentTimeMillis|\.millis\(\)"`. A `Date` or a
  `Calendar` away from a library or display edge is a finding, and so is time arithmetic on a raw `long` of millis.
- [ ] JV2 — Only where no gate enforces it (Checkstyle `RegexpSinglelineJava`): `parallelStream()` or `.parallel()`
  in request- or queue-serving code is a finding.
- [ ] JV3 — Open each `map`, `filter` and other stream lambda. An I/O call, a log call or a mutation inside it is a
  finding, and so is a `peek` that does work.
- [ ] JV4 — `grep -nE "toMap\("`. A `toMap` with no merge function is a finding.
- [ ] JVN1 — For each `equals` call (`grep -nE "\.equals\("`), one between two `BigDecimal` values is a finding.
- [ ] JV5 — `grep -nE "\bvar "`. A `var` whose initializer does not name its type (a constructor, a factory, a
  literal) is a finding, and so is `var` with `<>`.
- [ ] JV6 — Only where no gate enforces it (Checkstyle `IllegalType`): an `Optional` field, parameter or collection
  element is a finding.
- [ ] JV7 — A multi-line SQL, JSON or HTML string built with `+` and `\n` is a finding (a nit).
- [ ] JV8 — For each I/O-backed `AutoCloseable` a changed method opens, find it in a try-with-resources header. One
  opened anywhere else is a finding.
- [ ] JV9 — Only where no gate enforces it (Checkstyle `NeedBraces`): an `if`, `else`, `for`, `do` or `while` body
  without braces is a finding.
- [ ] CV3 — A Java or Groovy line longer than the project's configured length is a finding. A TypeScript file that
  Prettier's check would reformat is a finding.
