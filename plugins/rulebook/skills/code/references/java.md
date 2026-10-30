# Java

How plain Java code handles time, ids, `var`, streams, `Optional`, strings, resources and line length. Read it when
you write or review Java production code.

Contents: Rules · When X, use Y · Good / Bad (U4, JV1, JV5, CV3) · Decided edges · Review checks

## Rules

- **U4** — In logic a test must pin, take an injected `Clock` (and a `Supplier<UUID>` where an id matters), never
  `Instant.now()`, `LocalDate.now()` or `UUID.randomUUID()`, because a direct `Instant.now()` call cannot be
  stubbed and makes tests flaky.
- **JV1** — Compute time as an `Instant` or a `Duration`; convert to `Date` or a zoned type only at a library or
  display boundary, because a shared `SimpleDateFormat` corrupts dates under concurrent use.
- **JV2** — Use sequential streams in request- or queue-serving code, never `parallelStream()` or `.parallel()`,
  because a blocking call in a parallel stream parks a JVM-wide shared thread.
- **JV3** — Let a stream only compute; do I/O, logging and mutation outside `map` and `filter`, and never log with
  `peek`, because an effect inside `map` or `filter` makes the pipeline hard to test.
- **JV4** — Give `toMap` a merge function unless a database constraint makes the keys unique and a comment names that
  constraint, because `toMap` throws `IllegalStateException` at runtime on a duplicate key.
- **JV5** — Write `final var` only when the right-hand side shows the type (constructor, factory, literal, or a method
  named for it); otherwise write the type, because the reader cannot see it, and `new ArrayList<>()` infers
  `ArrayList<Object>`.
- **JV6** — Use `Optional` only as a return type, never as a field, parameter or collection element, because an
  `Optional` parameter still accepts `null` and an `Optional` field cannot serialise.
- **JV7** — Write multi-line SQL, JSON or HTML in Java as a text block, because escaped multi-line strings hide the
  shape, and a one-line edit touches three lines.
- **JV8** — Close every `AutoCloseable` a method opens with try-with-resources, because a resource that is not closed
  when an exception fires leaks.
- **JV9** — Put braces on every `if`, `else`, `for` and `while` body, because agents copy nearby code, and a
  brace-less `if` sat in a 'copy this' example.
- **CV3** — Wrap Java and Groovy at the line length the project's formatter config sets, and leave TypeScript wrapping
  to Prettier, because a Java wrapping rule forced onto TypeScript fights Prettier's own output.

## When X, use Y

| situation | use | why |
|---|---|---|
| the logic reads the current time or makes a new id | an injected `Clock` (`Instant.now(clock)`, `LocalDate.now(clock)`) or a `Supplier<UUID>` (U4); the test's fixed clock is U1 ([unit-tests.md](../../testing/references/unit-tests.md)) | `Instant.now()` is a static call on a final type, so a test cannot stub it (plinth 321 :136) |
| a point in time or a span of time | `Instant` for the point, `Duration` for the span (JV1) | `Instant` is machine time and `Duration` a time-based amount (pl 141 R:294) |
| a local variable whose right-hand side is a method call | the type written out, unless the method's name states the type (JV5) | `var result = processData(data)` hides the return type (pl 141 R:507-508) |
| a `toMap` whose keys may collide | a merge function (JV4) | pl 142 R:772 |
| a value that can be absent | `Optional` as the return type only (JV6) | fields, parameters and `Optional<List>` are the Bad cases (pl 121 methods:354-365) |
| an I/O, logging or state-changing step in a stream | that step outside the pipeline (JV3) | isolate side effects at the edges (pl 142 R:740) |
| a multi-line SQL, JSON or HTML string | a text block (JV7) | pl 141 R:914 |
| an `AutoCloseable` opened in a method | a try-with-resources header (JV8) | resources close even when exceptions occur (pl 126 R:195) |

`pl NNN` is a plinth-java-skills skill (`R` = its main reference, `methods` = the 121 methods reference), and plinth
321 is `321-frameworks-spring-boot-testing-unit-tests.md`; `:N` is the line. CV3's reason is reworded from the ledger
row, which named a dropped rule (ST2), and is approved by the operator (agent-factory#32 D9).

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

### JV1 — Time is an `Instant` or a `Duration`

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
final var chargeStart = clock.instant();
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

### JV5 — `final var` only when the right-hand side shows the type

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
`UUID.fromString` is a factory, so `var` stays. `place(…).orThrow(…)` names actions, not a type, so the type is written
out. (Pair: research/68f § JV5 — `final var` only when the right-hand side shows the type. Real evidence: ledger row
JV5.)

### CV3 — TypeScript wrapping is Prettier's

**Bad** (n/a) — the conflict is between two formatting rules, not in code.

**Good** (neutral)
```ts
await expect(
  page.getByRole('row', { name: invoiceId }),
).toBeVisible();
```
This is Prettier's own output. A Java wrapping rule forced onto it would fight the formatter. (Pair: research/68c
§ CV3 — Wrapping: ST2 applies to Java/Groovy (120); TypeScript follows Prettier (110). Real evidence: ledger row CV3.)

## Decided edges

- **Skip when** a framework's own style guide bans `var` (Spring Framework CONTRIBUTING.md:596): that ban serves a
  library read without an IDE, and JV5 already stops `var` from hiding a type (ledger X1). — **Do not skip when** the
  right-hand side does not show the type: write the type (JV5). — **Confidence** high

## Review checks

Walk every changed Java file under the production source tree. A Checkstyle gate owns JV2, JV6 and JV9 (ledger OQ3);
run their checks only where that gate does not run.

- [ ] U4 — `grep -nE "Instant\.now\(\)|LocalDate\.now\(\)|UUID\.randomUUID\(\)"`. A hit in logic a test must pin is a
  finding; the call belongs behind an injected `Clock` or `Supplier<UUID>`.
- [ ] JV1 — `grep -nE "java\.util\.Date|Calendar|SimpleDateFormat|ZonedDateTime|currentTimeMillis|\.millis\(\)"`. A
  `Date` or zoned type away from a library or display boundary is a finding, and so is time arithmetic on a `long`.
- [ ] JV2 — Only where no gate enforces it (Checkstyle `RegexpSinglelineJava`): `parallelStream()` or `.parallel()`
  in request- or queue-serving code is a finding.
- [ ] JV3 — Open each `map`, `filter` and `peek` lambda. An I/O call, a log call or a mutation inside it is a finding.
- [ ] JV4 — `grep -n "toMap("`. A `toMap` with no merge function and no comment naming the database constraint that
  keeps its keys unique is a finding.
- [ ] JV5 — `grep -n "var "`. A right-hand side that is not a constructor, a factory, a literal or a method named for
  its type is a finding.
- [ ] JV6 — Only where no gate enforces it (Checkstyle `IllegalType`): an `Optional` field, parameter or collection
  element is a finding.
- [ ] JV7 — A multi-line SQL, JSON or HTML string built with `+` and `\n` is a finding (a nit).
- [ ] JV8 — For each `AutoCloseable` a changed method opens, find it in a try-with-resources header. One opened
  anywhere else is a finding.
- [ ] JV9 — Only where no gate enforces it (Checkstyle `NeedBraces`): an `if`, `else`, `for` or `while` body without
  braces is a finding.
- [ ] CV3 — A Java or Groovy line longer than the project's configured length is a finding. A TypeScript file that
  Prettier's check would reformat is a finding.
