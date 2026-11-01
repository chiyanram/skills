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
- **ER8** — A best-effort metric or audit call may catch, log at WARN with class and message (LG3) and continue; never
  an empty block, because a failure below WARN is invisible to production alerting.

## When X, use Y

| the code meets | use | why |
|---|---|---|
| a case the caller can foresee: not found, already exists, over limit | a case of a sealed return type (ER1) | return a `Result` when failure is expected (RUST) · never use exceptions for ordinary control flow (EJ §57) · exceptions as flow control obscure it (PMD ExceptionAsFlowControl) (r48 :396) |
| a fault: a non-success the caller cannot foresee | an exception carrying a code from the one error catalogue (ER2) | a problem detail carries machine-readable details; consumers use its `type` (RFC9457) · every error response has one shape with a machine-readable `code` (ADDY api) (r48 :402) · avoid unnecessary checked exceptions (EJ §59) (r48 :403) |
| an error response | a body every time (ER2), with a 4xx status for a client error and 500 for an unforeseen fault, never a 2xx (ERN1) | include details in the body of error responses (SPRING) (r48 :402) · 4xx for a client error, 5xx for an unforeseen bug (OWASP-EH) · 500 never exposes internal details (ADDY api) · the problem's status is the response's status (RFC9457) (r48 :443) |
| an exception that must become an HTTP response | one global `@RestControllerAdvice` (ER11) | configure a global error handler (OWASP-EH) · one error strategy everywhere (ADDY api) · global handlers apply after local ones (SPRING ann-advice) (r48 :414) |
| an error body | the catalogue message only; the detail goes to the server log (ER10) | a generic response; details logged server side (OWASP-EH) · no stack dump through the HTTP interface (RFC9457) · never expose stack traces or internal error details (ADDY security) (r48 :409) |
| a caught exception that is rethrown | the caught exception passed as the cause (ER3) | pass the lower-level exception to the higher-level one (EJ §61) · the original stack trace could be lost (PMD PreserveStackTrace) · log it or pass it forward (SONAR S1166) · the stack trace restarts at the current method (NET) (r48 :419) |
| a caught exception that is not rethrown | handle or log it; an empty block only with a comment saying why (ER3) | it is very rarely correct to do nothing (GJS §6.2) · don't ignore caught errors (CCJS) (r48 :419) · an empty catch explained in a comment is allowed (GJS §6.2, CS EmptyCatchBlock) (r48 :420) |
| a `catch` clause | the narrowest type the `try` can raise (ER4) | catching `Exception`, `Error` or `RuntimeException` is almost never acceptable (CS IllegalCatch) · a generic catch can hide real problems; `Throwable` includes `OutOfMemoryError` (PMD) · `Throwable` or `Error` also catches `OutOfMemoryError` (SONAR S1181) · an `Error` is not for an application to catch (JDK) (r48 :424) |
| an `InterruptedException` | a rethrow, or `Thread.currentThread().interrupt()` (ER5) | rethrow it or restore the interrupted status (JDK) · logging alone loses the interrupt (SONAR S2142) · interruption must be handled for correctness (GOOG EP) (r48 :429) |
| a method that changes state and can fail | every check and computation before the first change (ERN2) | a failed call leaves the object as it was (EJ §64) · callers assume no side effects when an exception is thrown (NET) (r48 :444) |
| request input | Bean Validation at the boundary, no second check inside (ER6) | trust the types inside; no re-validation (PS boundary-discipline) · validate at system edges, not between internal functions (ADDY api) · validate before processing or storage (OWASP-IV) (r48 :434) |
| a best-effort metric or audit call that fails | catch, log at WARN with class and message (LG3, `../../obs/references/logging.md`), continue (ER8) | WARN is degraded but handled (ADDY observability) · WARN is more important than an informational event (OTEL) · typical responses are to log it (GJS §6.2) (r48 :439) |

`r48` is agent-factory `research/48-industry-recheck-code.md` and `:N` its line, where the source is quoted with the
repository path it was read at. Source keys are those of r48's source table (r48 :363-383).

## Good / Bad

### ER1 — A foreseeable non-success is a sealed outcome; only faults throw

**Bad** (neutral)
```java
public Invoice issue(final UUID orderId, final IssueCommand command) {
    LOG.info("action=invoice_issue orderId={}", orderId);

    invoiceRepository.findByOrderId(orderId).ifPresent(existing -> {
        throw new OrderException(ErrorCode.INVOICE_ALREADY_ISSUED,
            "orderId=" + orderId + " invoiceId=" + existing.id());
    });

    final Invoice saved = invoiceRepository.save(Invoice.open(orderId, command.total(), command.dueDate()));
```
"This order already has an invoice" is a normal answer, yet it leaves as an exception from a lambda. The signature
promises an `Invoice`.

**Good** (neutral)
```java
public InsertionResult<Invoice> issue(final UUID orderId, final IssueCommand command) {
    log.info("action=invoice_issue orderId={}", orderId);
    if (invoiceRepository.findByOrderId(orderId).isPresent()) {
        return new InsertionResult.Duplicate<>(orderId.toString());
    }
    final Invoice saved = invoiceRepository.save(Invoice.open(
            orderId,
            command.total(),
            command.dueDate()));
    log.info("action=invoice_issue_ok orderId={} invoiceId={}", orderId, saved.id());
    return new InsertionResult.Created<>(saved);
}
```
The duplicate is a case of the return type. The controller answers `.orThrow(ErrorCode.INVOICE_ALREADY_ISSUED)`, and
a database fault still throws. (Real evidence: ledger row ER1.)

### ER4 — Catch the narrowest type

**Bad** (neutral)
```java
try {
    JsonNode currencies = MAPPER.readTree(body).path("currencies");
    for (JsonNode currencyNode : currencies) {
        if (currency.equals(currencyNode.path("code").asString())) {
            currencySupported = true;
            break;
        }
    }
} catch (Exception failure) {
    log.warn(
            "action=gateway.health.status_unreadable cause={} message={}",
            failure.getClass().getSimpleName(),
            failure.getMessage());
}
```
Only the JSON parse can fail here, yet the catch takes every exception. A loop bug reads as "currency not supported".

**Good** (neutral)
```java
private boolean supportsCurrency(final String statusBody) {
    try {
        for (final JsonNode entry : MAPPER.readTree(statusBody).path("currencies")) {
            if (entry.path("code").asString().equals(currency)) {
                return true;
            }
        }
        return false;
    } catch (final JacksonException unexpectedShape) {
        log.warn(
                "action=gateway.health.status_unreadable cause={} message={}",
                unexpectedShape.getClass().getSimpleName(),
                unexpectedShape.getMessage());
        return false;
    }
}
```
`JacksonException` is the one failure the parse can raise, so it is the one caught and logged with its
class and message. Any other exception now surfaces. (Real evidence: ledger row ER4.)

### ER8 — A best-effort call logs at WARN with the exception class

**Bad** (neutral)
```java
private void logStatusChange(final OrderStatusChange change) {
    try {
        auditLog.record(OrderAuditEntry.of(change, clock.instant()));
    } catch (Exception ignored) { /* never block the order on audit failures */ }
}
```
Catching is allowed because the audit is best effort, but the block is silent, so a broken audit trail is invisible.

**Good** (neutral)
```java
private void logStatusChange(final OrderStatusChange change) {
    try {
        auditLog.record(OrderAuditEntry.of(change, clock.instant()));
    } catch (final RuntimeException auditFailure) {
        // best effort: a lost audit row must never block the order change
        log.warn(
                "action=order.status.audit_failed orderId={} statusAction={} cause={} message={}",
                change.orderId(),
                change.action(),
                auditFailure.getClass().getSimpleName(),
                auditFailure.getMessage());
    }
}
```
The order change still never blocks, but each lost audit row leaves one WARN line that names the exception class
and message, with no stack. The comment says why this broad catch sits at a must-not-fail boundary (ER4). (Real
evidence: ledger row ER8.)

### ER10 — An error response carries the catalogue message only

**Bad** (neutral)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(DataIntegrityViolationException violation) {
    return ApiResponse.error(
            ErrorCode.VALIDATION_FAILED.code(),
            "Invalid reference: " + violation.getMostSpecificCause().getMessage(),
            currentTraceId());
}
```
The body carries the catalogue code, but its message is the JDBC driver's: constraint names, column names, sometimes
the offending value.

**Good** (neutral)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(final DataIntegrityViolationException violation) {
    final String traceId = currentTraceId();
    log.warn(
            "action=api.data_integrity traceId={} cause={} message={}",
            traceId,
            violation.getMostSpecificCause().getClass().getSimpleName(),
            violation.getMostSpecificCause().getMessage());
    return ApiResponse.error(
            ErrorCode.VALIDATION_FAILED.code(),
            ErrorCode.VALIDATION_FAILED.defaultMessage(),
            traceId);
}
```
The body says only what the error catalogue says. The operator gets the trace id, the cause class and its message
in the log. The method lives in the one global exception handler (ER11). (Real evidence: ledger row ER10.)

## Decided edges

- **Skip when** the catch sits at a must-not-fail boundary, such as a best-effort metric or audit call: a broad catch
  that logs at WARN and continues is allowed there, with a comment (ER4, ER8; WARN is degraded but handled, r48 :439).
  — **Do not skip when** the block is empty or logs below WARN (ER8), the broad catch has no comment (ER4), or the
  catch takes `Throwable` or `Error` (ER4; r48 :424). — **Confidence** high
- **Skip when** an empty catch carries a comment saying why doing nothing is safe (ER3; GJS §6.2 and CS EmptyCatchBlock,
  r48 :420). — **Do not skip when** the catch wraps a best-effort metric or audit call: it logs at WARN (ER8), or when
  it catches `InterruptedException`: it rethrows or restores the flag (ER5). — **Confidence** high

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
- [ ] ER8 — Each catch around a best-effort metric or audit call logs at WARN with the exception's class and message
  (LG3). An empty block, even one with a comment, or a log below WARN, is a finding.
