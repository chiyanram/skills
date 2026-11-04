# Errors

How a method reports a non-success, how it throws, catches and maps exceptions, which status an error gets, and where
it validates input. Read it when you write or review a `throw`, a `catch`, an exception handler, an error response or
request validation.

Contents: Rules · When X, use Y · Good / Bad (ER1, ER4, ER8, ER10) · Decided edges · Review checks

## Rules

- **ER1** — Return a foreseeable non-success (not found, already exists, over limit) as a case of a sealed return type;
  throw only faults, because a thrown expected case is invisible in the signature and callers skip it.
- **ER2** — Throw a fault as an unchecked exception carrying a code from the one error catalogue and give every
  error a body, because clients branch on a machine-readable code, not free text or an empty body.
- **ERN1** — Return 4xx for a client error and 500 with a generic body for an unforeseen fault; never a 2xx carrying an
  error, because clients and monitoring read the status.
- **ER7** — Do not use `Either` or VAVR; a domain-named sealed outcome carries the
  non-success case, because a domain-named sealed type says what failed; an `Either` left says only "left".
- **ER10** — Put only the catalogue message in an error body and log the detail server-side; never an exception's
  `getMessage()`, a stack trace or SQL, because they reveal framework versions, schema and data to an attacker.
- **ER11** — Map exceptions to error responses in one global `@RestControllerAdvice`; declare no `@ExceptionHandler` in
  a controller, because a local handler runs first and bypasses the shared, sanitised error shape.
- **ER3** — Pass the caught exception as a rethrow's cause; handle, rethrow or log every catch, or comment why it is
  empty, because a dropped cause loses the stack trace and a silent catch hides the failure.
- **ER4** — Catch the narrowest type; `catch (Exception)` only at a must-not-fail
  boundary, with a comment; never `Throwable`, because a broad catch hides failures; `Throwable` even swallows
  `OutOfMemoryError`.
- **ER5** — When you catch `InterruptedException`, rethrow it or call `Thread.currentThread().interrupt()`, because
  otherwise the interrupt request is lost and the thread can no longer be cancelled or shut down.
- **ERN2** — Leave state as it was when a method fails: validate and compute before you mutate, because a half-applied
  change corrupts data.
- **ER6** — Validate request input at the boundary with Bean Validation; inside, trust the types, because a service
  re-validating what the boundary checked is duplicated logic that drifts.
- **ER8** — A best-effort metric or audit call may catch, log at WARN with the exception (LG3) and continue; never an
  empty block, because a failure below WARN is invisible to production alerting.

## When X, use Y

| the code meets | use | why |
|---|---|---|
| a case the caller can foresee: not found, already exists, over limit | a case of a sealed return type (ER1), never an `Either` (ER7) | a thrown expected case is invisible in the signature, so callers skip it; a domain-named type says what failed |
| a fault: a non-success the caller cannot foresee | an unchecked exception carrying a code from the one error catalogue (ER2) | clients branch on a machine-readable code, not free text |
| an error response | a body every time (ER2), with a 4xx status for a client error and 500 for an unforeseen fault, never a 2xx (ERN1) | clients and monitoring read the status, and an empty body carries no code |
| an exception that must become an HTTP response | one global `@RestControllerAdvice` (ER11) | a local handler runs first and bypasses the shared, sanitised error shape |
| an error body | the catalogue message only; the detail goes to the server log (ER10) | an exception message, stack trace or SQL reveals framework versions, schema and data to an attacker |
| a caught exception that is rethrown | the caught exception passed as the cause (ER3) | a dropped cause loses the stack trace |
| a caught exception that is not rethrown | handle or log it; an empty block only with a comment saying why (ER3) | a silent catch hides the failure |
| a `catch` clause | the narrowest type the `try` can raise (ER4) | a broad catch hides failures; `Throwable` even swallows `OutOfMemoryError` |
| an `InterruptedException` | a rethrow, or `Thread.currentThread().interrupt()` (ER5) | otherwise the interrupt request is lost and the thread can no longer be cancelled or shut down |
| a method that changes state and can fail | every check and computation before the first change (ERN2) | a half-applied change corrupts data |
| request input | Bean Validation at the boundary, no second check inside (ER6) | a service re-validating what the boundary checked is duplicated logic that drifts |
| a best-effort metric or audit call that fails | catch, log at WARN with the exception (LG3, `../../obs/references/logging.md`), continue (ER8) | a failure below WARN is invisible to production alerting |

## Good / Bad

### ER1 — A foreseeable non-success is a sealed outcome; only faults throw

**Bad**
```java
public Order cancel(final OrderId id) {
    final Order order = orders.findById(id)
            .orElseThrow(() -> new ServiceException(ErrorCode.NOT_FOUND));
    if (order.isShipped()) {
        throw new ServiceException(ErrorCode.CONFLICT);
    }
    return orders.save(order.cancelled());
}
```
"No such order" and "already shipped" are normal answers. The signature promises an `Order`, so the caller learns of
the other two cases only at runtime.

**Good**
```java
public sealed interface CancelResult {
    record Cancelled(Order order) implements CancelResult {
        @Override
        public Optional<Order> changed() {
            return Optional.of(order);
        }
    }
    record NotFound(OrderId id) implements CancelResult {}
    record AlreadyShipped(OrderId id) implements CancelResult {}

    /** The order this outcome changed, for the caller to save; empty when nothing changed. */
    default Optional<Order> changed() {
        return Optional.empty();
    }
}
public CancelResult cancel(final OrderId id) {
    final CancelResult result = orders.findById(id)
            .map(OrderService::decideCancel)
            .orElseGet(() -> new CancelResult.NotFound(id));
    result.changed().ifPresent(orders::save);
    return result;
}
static CancelResult decideCancel(final Order order) {
    return order.isShipped()
            ? new CancelResult.AlreadyShipped(order.id())
            : new CancelResult.Cancelled(order.cancelled());
}
```
Each foreseeable case is in the return type, so the caller's `switch` must name all three. A database fault still
throws. `decideCancel` does no I/O, and `cancel` only reads and saves what the decision changed (SEAM1, `design.md`).

### ER4 — Catch the narrowest type

**Bad**
```java
try {
    insert(order);
} catch (Throwable failure) {
    log.error("order insert failed", failure);
}
```
`Throwable` also takes `OutOfMemoryError`, and the caller goes on as if the insert worked.

**Good**
```java
try {
    insert(order);
} catch (final SQLException failure) {
    throw new ServiceException(ErrorCode.INTERNAL_ERROR, failure);
}
```
Only the failure the `try` can raise is caught, and it is rethrown with its cause (ER3). A JVM error propagates.

### ER8 — A best-effort call logs at WARN with the exception

**Bad**
```java
private void audit(final OrderEvent event) {
    try {
        auditLog.record(event);
    } catch (RuntimeException e) {
        // audit is best effort
    }
}
```
Catching is allowed because the audit is best effort, but the block is silent, so a broken audit trail is invisible.

**Good**
```java
private void audit(final OrderEvent event) {
    try {
        auditLog.record(event);
    } catch (final RuntimeException failure) {
        // must-not-fail boundary: a lost audit row never blocks the order; the order id is in the MDC (LG1)
        log.warn("order audit failed", failure);
    }
}
```
The order still never blocks, and each lost audit row leaves one WARN line with the exception as the last argument
(LG3).

### ER10 — An error response carries the catalogue message only

**Bad**
```java
@RestControllerAdvice
public final class ApiExceptionHandler {
    @ExceptionHandler(DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleDataAccess(final DataAccessException failure) {
        return ApiError.of(ErrorCode.INTERNAL_ERROR, failure.getMessage());
    }
}
```
The client gets whatever the library wrote: SQL, table names, host names.

**Good**
```java
@RestControllerAdvice
public final class ApiExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleDataAccess(final DataAccessException failure) {
        // the trace id is in the MDC (LG1)
        log.error("data access failed", failure);
        return ApiError.of(ErrorCode.INTERNAL_ERROR);
    }
}
```
The body holds the error code, its catalogue message and the trace id. The driver text stays in the log. The method
lives in the one global exception handler (ER11).

## Decided edges

- **Skip when** the catch sits at a must-not-fail boundary, such as a best-effort metric or audit call: a broad catch
  that logs at WARN and continues is allowed there, with a comment (ER4, ER8). — **Do not skip when** the block is
  empty or logs below WARN (ER8), the broad catch has no comment (ER4), or the catch takes `Throwable` or `Error`
  (ER4). — **Confidence** high
- **Skip when** an empty catch carries a comment saying why doing nothing is safe (ER3). — **Do not skip when** the
  catch wraps a best-effort metric or audit call: it logs at WARN (ER8), or when it catches `InterruptedException`: it
  rethrows or restores the flag (ER5). — **Confidence** high

## Review checks

Walk every changed Java file that holds a `throw`, a `catch`, an `@ExceptionHandler`, an error response or a request
type (`grep -nE "throw |catch \(|@ExceptionHandler|ResponseEntity"`).

- [ ] ER1 — For each `throw`, the case is a fault. A throw for a not-found, already-exists or over-limit case is a
  finding.
- [ ] ER2 — Each fault throws an unchecked exception carrying a code from the one error catalogue. A new checked
  exception in a `throws` clause is a finding, and so is an error response with no body
  (`grep -nE "ResponseEntity\.(status|badRequest|notFound|unprocessableEntity|internalServerError)\(.*build\(\)"`).
- [ ] ERN1 — For each error response, the status is 4xx for a client error and 500 for an unforeseen fault. A 2xx that
  carries an error (`grep -nE "\.(ok|accepted)\(.*[Ee]rror"`), or a client error answered with a 5xx, is a finding.
- [ ] ER7 — `Either` or VAVR (`grep -nE "Either<|io\.vavr"`) is a finding.
- [ ] ER10 — For each `getMessage()` in an exception handler (`grep -n "getMessage()"`), the text goes to the log, not
  the body. A `getMessage()`, a stack trace or SQL text in the body is a finding.
- [ ] ER11 — Each `@ExceptionHandler` (`grep -rn "@ExceptionHandler"`) sits in the one `@RestControllerAdvice` class.
  One in a controller, or a second advice class, is a finding.
- [ ] ER3 — For each `catch` (`grep -nE -A1 "catch \("`), a rethrow passes the caught exception as its cause, and any
  other block handles it, logs it, or is empty with a comment saying why. A rethrow without the cause is a finding, and
  so is an empty block with no comment.
- [ ] ER4 — Each `catch` names the narrowest type its `try` can raise. A broad catch
  (`grep -nE "catch \((final )?([A-Za-z.]+ *\| *)*(Exception|RuntimeException|Throwable|Error)\b"`) away from a
  must-not-fail boundary or without a comment is a finding, and so is any catch of `Throwable` or `Error`.
- [ ] ER5 — Each catch of `InterruptedException` (`grep -n "InterruptedException"`) rethrows or calls
  `Thread.currentThread().interrupt()`. Neither is a finding.
- [ ] ERN2 — For each method that changes state and can fail, the checks and computation run before the first change.
  A check or a failing call after a partial change, with no rollback, is a finding.
- [ ] ER6 — Each request type carries Bean Validation at the boundary. A check inside the service that repeats a
  boundary check is a finding.
- [ ] ER8 — Each catch around a best-effort metric or audit call logs at WARN with the exception (LG3). An empty block,
  even one with a comment, or a log below WARN, is a finding.
