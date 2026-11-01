# Java

How plain Java code handles time, streams, `toMap`, `BigDecimal` equality, `var`, `Optional`, strings, resources and
braces. Read it when you write or review Java production code.

Contents: Rules · When X, use Y · Good / Bad (U4, JV1, JV5) · Decided edges · Review checks

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

## When X, use Y

| situation | use | why |
|---|---|---|
| the logic reads the current time | an injected `Clock`, called as `now(clock)` (U4); the test's fixed clock is U1 ([unit-tests.md](../../testing/references/unit-tests.md)) | pass a `Clock` into any method that requires the current instant (OpenJDK `Clock` javadoc, r48 :215); also Sonar S8692 (r48 :215) |
| a point or a span of time | `Instant`, `Duration` or another `java.time` type; `Date` only at a library or display edge (JV1) | avoid `java.util.Date` and prefer the `java.time` APIs (Error Prone `JavaUtilDate`, r48 :221); also Sonar S2143 (r48 :221) |
| a stream in request- or queue-serving code | a sequential stream (JV2) | a task not submitted to a specified pool runs on the common pool (OpenJDK `ForkJoinPool`, r48 :227); parallelizing a pipeline is often no faster (Effective Java Item 48, r48 :227) |
| an I/O, logging or state-changing step in a stream | that step outside the pipeline (JV3) | side effects of behavioral parameters may not always be executed (OpenJDK `java.util.stream`, r48 :233); also Sonar S3864 (r48 :233) |
| a `toMap` | the three-argument form, with a merge function (JV4) | if the mapped keys might have duplicates, use the form with a merge function (OpenJDK `Collectors.toMap`, r48 :239) |
| two `BigDecimal` values to compare | `compareTo` (JVN1) | also Sonar S9351 (r48 :277); `equals` compares the scale as well as the value (Error Prone `BigDecimalEquals`, r48 :277) |
| a local variable | `var` when the initializer names the type; else the type written out; never `var` with `<>` (JV5) | consider `var` when the initializer gives the reader enough information (OpenJDK LVTI guide G3, r48 :245); `var` with a diamond infers `Object` (LVTI guide G6, r48 :245) |
| a value that can be absent | `Optional` as the return type only (JV6) | `Optional` is meant for method return types (OpenJDK `Optional` apiNote, r48 :123); also Sonar S3553 (r48 :251) |
| a multi-line SQL, JSON or HTML string | a text block (JV7) | use a text block for multi-line strings (OpenJDK text-blocks guide G1, r48 :257); also Sonar S6126 (r48 :257) |
| an I/O-backed `AutoCloseable` opened in a method | a try-with-resources header (JV8) | try-with-resources ensures prompt release and avoids resource exhaustion (OpenJDK `AutoCloseable`, r48 :262); always use try-with-resources (Effective Java Item 9, r48 :262) |
| an `if`, `else`, `for`, `do` or `while` body | braces, even for one statement (JV9) | braces are used even when the body is empty or one statement (Google Java Style §4.1.1, r48 :267); also Sonar S121 (r48 :267) |

`r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source, read at the
commit it names. JV4 rests on the JDK's own docs alone (vendor exception, r48 :39).

## Good / Bad

### U4 — Take an injected Clock; never call the wall clock directly

**Bad** (neutral)
```java
        if (invoice.dueDate().isBefore(LocalDate.now())) {
            invoiceRepository.save(invoice.withStatus(InvoiceStatus.OVERDUE));
        }
```
The due-date check reads the wall clock, so a test cannot pin "due exactly today" against "due yesterday".

**Good** (neutral)
```java
    public List<Invoice> overdueInvoices(final int graceDays) {
        log.info("action=invoice_overdue_scan graceDays={}", graceDays);
        final var today = LocalDate.now(clock);
        final LocalDate cutoff = today.minusDays(graceDays);
        return invoiceRepository.findOpen().stream()
                .filter(invoice -> invoice.dueDate().isBefore(cutoff))
                .toList();
    }
```
One date from the injected clock decides the cutoff, so a spec with `Clock.fixed(...)` pins the boundary exactly. (Pair:
research/68b § U4 — Production logic takes an injected Clock; never calls the wall clock directly. Real evidence: ledger
row U4.)

### JV1 — Time is a `java.time` type, never a raw `long`

**Bad** (neutral)
```java
final long chargeStartMillis = clock.millis();
final ChargeReply reply = paymentGateway.charge(chargeRequest(invoice, customerId));
final long elapsedMillis = clock.millis() - chargeStartMillis;
log.info(
        "action=invoice.charge.ok invoiceId={} orderId={} customerId={} durationMs={}",
        invoice.id(),
        invoice.orderId(),
        customerId,
        elapsedMillis);
```
Elapsed time is raw `long` subtraction of epoch millis, so the span is a bare number and not a `Duration`.

**Good** (neutral)
```java
final Instant chargeStart = clock.instant();
final ChargeReply reply = paymentGateway.charge(chargeRequest(invoice, customerId));
final var elapsed = Duration.between(chargeStart, clock.instant());
log.info(
        "action=invoice.charge.ok invoiceId={} orderId={} customerId={} durationMs={}",
        invoice.id(),
        invoice.orderId(),
        customerId,
        elapsed.toMillis());
```
The time is an `Instant` from an injected `Clock` and the span a `Duration`. It becomes a `long` only for the log line.
(Pair: research/68f § JV1 — Time is `Instant`/`Duration`; `Date`/zoned only at a library or display boundary. Real
evidence: ledger row JV1.)

### JV5 — `var` only when the initializer names the type

**Bad** (neutral)
```java
final var customerId = UUID.fromString(principal.getName());
final var placed = orderService.place(id, customerId).orThrow(ErrorCode.ORDER_NOT_FOUND);
return ApiResponse.ok(placed);
```
Neither `place` nor `orThrow` tells the reader the value is an `OrderResponse`.

**Good** (neutral)
```java
public ApiResponse<OrderResponse> place(
        @PathVariable final UUID id,
        final Principal principal) {
    final var customerId = UUID.fromString(principal.getName());
    final OrderResponse placed = orderService.place(id, customerId)
            .orThrow(ErrorCode.ORDER_NOT_FOUND);
    return ApiResponse.ok(placed);
}
```
`UUID.fromString` is a factory that names its type, so `var` stays. `place(…).orThrow(…)` names actions, not a type, so
the type is written out. (Pair: research/68f § JV5 — `final var` only when the right-hand side shows the type. Real
evidence: ledger row JV5.)

## Decided edges

- **Skip when** a framework's own style guide bans `var` (Spring Framework CONTRIBUTING.md:597, r48 :246): that ban
  serves a library read without an IDE, and JV5 already stops `var` from hiding a type. — **Do not skip when** the
  initializer does not name the type: write the type (JV5). — **Confidence** high
- **Skip when** the `AutoCloseable` is not backed by I/O, such as a `Stream` over a collection: try-with-resources is
  in general unnecessary there (OpenJDK `AutoCloseable`, r48 :262). — **Do not skip when** it holds a file, a socket
  or a connection: JV8 applies. — **Confidence** high

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
