# Errors

How a method reports a non-success, how it throws, catches and maps exceptions, and where it validates input. Read it
when you write or review a `throw`, a `catch`, an exception handler or request validation.

Contents: Rules · When X, use Y · Good / Bad (ER1, ER4, ER8, ER10) · Decided edges · Review checks

## Rules

- **ER1** — A foreseeable non-success (not found, already exists, over limit) is a
  sealed outcome in the return type; only faults throw, because an expected case that is thrown lets callers ignore it
  until runtime.
- **ER2** — A fault throws one base exception type with a machine-readable error
  code; no checked exceptions; never a bare `ResponseEntity…build()`, because a bare `build()` returns an empty body
  with no error code.
- **ER7** — Do not use `Either` or VAVR; a domain-named sealed outcome carries the
  non-success case, because a domain-named sealed type says what failed; an `Either` left says only "left".
- **ER10** — An error response carries the error code's generic message only; never `getMessage()` from a library,
  driver or JDK exception, a stack, or SQL, because those expose internal details to the client.
- **ER11** — Map exceptions to responses only in the one central exception handler; a controller declares no
  `@ExceptionHandler`, because each extra handler is one more place that can return internal details to the client.
- **ER3** — A rethrow chains its cause; a caught exception is handled, rethrown or
  logged with its class name, never left empty, because a dropped cause ends the stack trace and an empty catch hides
  bugs.
- **ER4** — Catch the narrowest type; `catch (Exception)` only at a must-not-fail
  boundary, with a comment; never `Throwable`, because a broad catch hides failures; `Throwable` even swallows
  `OutOfMemoryError`.
- **ER5** — When you catch `InterruptedException`, restore the flag with
  `Thread.currentThread().interrupt()` or rethrow, because a swallowed interrupt causes a quiet hang.
- **ER6** — Validate request input at the boundary with Bean Validation; inside, trust the types, because a service
  re-validating what the boundary checked is duplicated logic that drifts.
- **ER8** — A best-effort metric or audit call may catch, log at WARN with the exception (LG3) and continue; never an
  empty block, because an empty catch hides the failure.

## When X, use Y

| the code meets | use | why |
|---|---|---|
| a case the caller can foresee: not found, already exists, over limit | a sealed outcome in the return type (ER1), never an `Either` (ER7) | operator preference; a case the types let you ignore becomes a runtime failure the compiler could have stopped (types :9) |
| a fault: a non-success the caller cannot foresee | throw the one base exception type with a machine-readable error code (ER2) | operator preference; every error response follows one shape with a machine-readable code (api :61-86) |
| an exception that must become an HTTP response | the one central exception handler (ER11), with the error code's generic message as the body (ER10) | translate at the boundary with centralized handlers (exc :32, :2184) · define a global error handler (OWASP) · never expose stack traces or internal error details (sec :73, :98) · log the detail, give users a generic message (exc :26) |
| a caught exception that is rethrown | the caught exception passed as the cause (ER3) | operator preference; chaining keeps the full error context (exc :27) |
| a caught exception that is not rethrown | handle it or log it, never an empty block (ER3) | an empty catch block hides the problem (exc :1948) · errors silently swallowed (rubric :10) |
| an `InterruptedException` | `Thread.currentThread().interrupt()`, or a rethrow (ER5) | operator preference; restore the interrupted status (exc :28) |
| a `catch` clause | the narrowest type the `try` can raise (ER4) | operator preference for the narrowest type and the must-not-fail boundary; specific types, not generic `Exception` (exc :23) · `Throwable` or `Error` can mask `OutOfMemoryError` (exc :2374); an `Error` is a problem a reasonable application should not try to catch (JDK `Error`) |
| a best-effort metric or audit call that fails | catch, log at WARN with the exception (LG3, `../../obs/references/logging.md`), continue (ER8) | WARN means degraded but handled (obs :75) · an empty catch block hides the problem (exc :1948) |
| request input | Bean Validation at the boundary, no second check inside (ER6) | validate at the boundary, trust the types inside (boundary :14-15, :24) · validate at system edges (api :90) · Bean Validation of web input (Spring Framework, Validation) |

`types` is pstack `skills/principle-type-system-discipline/SKILL.md`, `boundary` is pstack
`skills/principle-boundary-discipline/SKILL.md`, `rubric` is pstack `skills/interrogate/references/rubric.md`, `exc` is
plinth `126-java-exception-handling.md`, `api` is addy `skills/api-and-interface-design/SKILL.md`, `sec` is addy
`skills/security-and-hardening/SKILL.md` and `obs` is addy `skills/observability-and-instrumentation/SKILL.md`; `:N`
is the line. OWASP is the Error Handling Cheat Sheet,
https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html. JDK `Error` is the Java SE Javadoc of
`java.lang.Error`. Spring Framework, Validation is
https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html.

Operator preference, 2026-10-31 (SRC2), in whole or in part: ER1, ER2, ER7, ER3, ER4 and ER5.

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
    JsonNode root = MAPPER.readTree(body);
    JsonNode currencies = root.path("currencies");
    if (currencies.isArray()) {
        for (JsonNode currencyNode : currencies) {
            String code = currencyNode.path("code").asString();
            if (currency.equals(code)) {
                currencySupported = true;
                break;
            }
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
and message, with no stack. (Real evidence: ledger row ER8.)

### ER10 — An error response carries the `ErrorCode` message only

**Bad** (neutral)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(DataIntegrityViolationException violation) {
    return ApiResponse.error("Invalid reference: " + violation.getMostSpecificCause().getMessage());
}
```
The handler sends the JDBC driver's message to the client: constraint names, column names, sometimes the offending
value.

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
in the log. The method lives in the one central exception handler (ER11). (Real evidence: ledger row ER10.)

## Decided edges

- **Skip when** the catch sits at a must-not-fail boundary, such as a best-effort metric or audit call: a broad catch
  that continues is allowed there, with a comment (ER4, ER8; WARN means degraded but handled, obs :75). — **Do not
  skip when** the block is empty or logs below WARN (ER8), the broad catch has no comment (ER4), or the catch takes
  `Throwable` or `Error` (ER4; exc :2374). —
  **Confidence** high

## Review checks

Walk every changed Java file that holds a `throw`, a `catch`, an `@ExceptionHandler`, an error response or a request
type (`grep -nE "throw |catch \(|@ExceptionHandler|ResponseEntity"`).

- [ ] ER1 — For each `throw`, the case is a fault. A throw for a not-found, already-exists or over-limit case is a
  finding.
- [ ] ER2 — Each fault throws the one base exception type with a machine-readable error code. A new checked exception in a
  `throws` clause is a finding, and so is a `ResponseEntity…build()` with no body (`grep -n "build()"`).
- [ ] ER7 — `Either` or VAVR (`grep -nE "Either<|io\.vavr"`) is a finding.
- [ ] ER10 — For each error response, the body message is the error code's generic message. A `getMessage()` of a library,
  driver or JDK exception, a stack trace or SQL text in the body is a finding.
- [ ] ER11 — An `@ExceptionHandler` outside the one central exception handler (`grep -n "@ExceptionHandler"`) is a
  finding.
- [ ] ER3 — For each `catch`, a rethrow passes the caught exception as its cause, and any other block handles it or
  logs its class name. A rethrow without the cause is a finding, and so is an empty block, even one that holds a
  comment (operator preference).
- [ ] ER4 — Each `catch` names the narrowest type its `try` can raise. A `catch (Exception)` away from a must-not-fail
  boundary or without a comment is a finding, and so is any catch of `Throwable` or `Error`.
- [ ] ER5 — Each catch of `InterruptedException` calls `Thread.currentThread().interrupt()` or rethrows. Neither is a
  finding.
- [ ] ER6 — Each request type carries Bean Validation at the boundary. A check inside the service that repeats a
  boundary check is a finding.
- [ ] ER8 — Each catch around a best-effort metric or audit call logs at WARN with the exception (LG3). An empty
  block, or a log below WARN, is a finding.
