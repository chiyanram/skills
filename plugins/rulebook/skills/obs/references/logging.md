# Logging

How to write a log call: what it may hold, how it carries context and exceptions, and where the output goes. Read it
when you write or review a log call, a logger field, a `catch` block that logs, or the logging configuration.

Contents: Rules · When X, use Y · Good / Bad (LG1, LG2, LG3) · Decided edges · Review checks

Which level a log event gets is in `levels.md`.

## Rules

- **LG4** — Never log passwords, tokens, session ids, auth or cookie headers, keys, connection strings, card data or
  sensitive PII; log the id and allowlisted fields, never whole bodies, because logs leak data.
- **LG2** — Log a failure once, where it is handled; code that rethrows does not also log, because logging before a
  rethrow writes one failure once per layer and inflates error counts.
- **LG3** — Pass the exception as the last argument, never `e.getMessage()` or `printStackTrace()`, because a
  message-only log loses the type and stack, and `printStackTrace` bypasses the logger.
- **LG1** — Log a constant message with context as key-value fields (MDC or `addKeyValue`): trace id plus business
  ids, never ids pasted into text, because otherwise one request cannot be rebuilt from interleaved lines.
- **LG6** — Use a constant template with `{}` placeholders, never concatenation; pass an expensive argument as a
  `Supplier` or behind `isXEnabled()`, because concatenation runs while the level is off and lets input rewrite the
  template.
- **LG5** — Emit production logs with a structured (JSON) encoder; on a plain pattern layout, strip CR/LF from
  untrusted values, exception messages included, because a newline in input forges a log line.
- **LG8** — Create the logger with `LoggerFactory.getLogger(DeclaringClass.class)`, never a string or another class,
  because levels are configured by class-name hierarchy and a misnamed logger cannot be tuned.
- **LGN1** — Write logs to stdout; add no file appender, rotation or log path in app config, because the platform owns
  routing and storage, and a file in a container is lost or fills the disk.

## When X, use Y

| the log call or config holds | use | why |
|---|---|---|
| a secret, token, session id, credential header, key, connection string or card data | nothing: drop it (LG4) | OWASP Logging "should usually not be recorded directly in the logs"; Log4j API · r47 :502-503 |
| a request or response body | the id and allowlisted fields only (LG4) | OWASP Logging; OpenTelemetry HTTP "SHOULD be scrubbed" · r47 :502, :504 |
| a `catch` that rethrows or wraps with the cause | no log call; the handler that decides the outcome logs it (LG2) | OpenTelemetry recording errors "NOT RECOMMENDED to record the same exception more than once"; exceptions in logs · r47 :486-487 |
| an exception | the throwable as the last argument (LG3) | SLF4J FAQ "its stack trace will NOT be printed"; Log4j API "Don't use `Throwable#getMessage()`!" · r47 :494-495 |
| a trace id or a business id | a key-value field: MDC or `addKeyValue` (LG1) | OWASP Logging "Interaction identifier"; OpenTelemetry logs data model; Spring Boot logging, tracing · r47 :476-479 |
| any other variable value | a `{}` placeholder in a constant template (LG6) | SLF4J FAQ; Log4j API; OWASP Logging "Keep message templates constant" · r47 :517-519 |
| an argument that is costly to build | a `Supplier`, or a call behind `isXEnabled()` (LG6) | Log4j API "Use `Supplier`s"; SLF4J FAQ · r47 :517-518 |
| a production log layout | a structured (JSON) encoder (LG5) | OWASP Logging "Do not use unstructured text log formats"; Log4j security FAQ · r47 :511-512 |
| a logger field | `LoggerFactory.getLogger(DeclaringClass.class)` (LG8) | Log4j API; SLF4J FAQ · r47 :524-525 |
| an appender | the console (stdout) only (LGN1) | Twelve-Factor "writes its event stream, unbuffered, to stdout"; Kubernetes logging; Spring Boot logging · r47 :532-534 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file. Every rule has ≥2
sources, quoted there; none comes from one project's history (operator, 2026-10-31, agent-factory#34). LG2's two
sources are both OpenTelemetry documents; the operator kept it.

## Good / Bad

### LG1 — Ids as fields, not in the text

**Bad** (neutral)
```java
log.info("order {} placed by customer {}", orderId, customerId);
```
The ids sit inside the text, so no query can select one order's lines without parsing every message.

**Good** (neutral)
```java
// the trace id comes from the MDC
log.atInfo()
    .setMessage("order placed")
    .addKeyValue("orderId", orderId)
    .addKeyValue("customerId", customerId)
    .log();
```
The message is constant, and each id is a field the encoder writes beside it.

### LG2 — Log once, where the failure is handled

**Bad** (neutral)
```java
try {
    paymentGateway.charge(invoice);
} catch (GatewayException e) {
    log.error("charge failed", e);
    throw new PaymentFailedException(invoice.id(), e);
}
```
The top-level handler logs the same failure again, so one failure counts twice.

**Good** (neutral)
```java
try {
    paymentGateway.charge(invoice);
} catch (GatewayException e) {
    throw new PaymentFailedException(invoice.id(), e);
}
```
It wraps with the cause and logs nothing. The handler that decides the response logs it once.

### LG3 — The exception as the last argument

**Bad** (neutral)
```java
log.warn("refund failed: {}", e.getMessage());
```
Only the message is kept. The type and the stack are lost.

**Good** (neutral)
```java
// the payment id is in the MDC (LG1)
log.warn("refund failed", e);
```
The throwable is the last argument, so the logger prints its type and stack.

## Decided edges

- **Skip when** a value in a log message is not an id, such as a count, a duration or a status: a `{}` placeholder
  is right (LG6; SLF4J FAQ, Log4j API, r47 :517-518). — **Do not skip when** the value is a trace id or a business
  id: it is a field (LG1, r47 :476-479). — **Confidence** high
- **Skip when** the logger field is an instance field rather than `static`: both are allowed (LG8; SLF4J leaves
  static or instance "to the user", r47 :527). — **Do not skip when** the class passed is not the declaring class.
  — **Confidence** high

## Review checks

Walk every log call, logger field and `catch` block added or changed in the diff, and every changed logging
configuration file.

- [ ] LG4 — For each log call, read every argument and field. A secret, token, session id, credential header, key,
  connection string, card number, sensitive PII value or whole request or response body is a finding.
- [ ] LG2 — For each `catch` that logs, check that it does not rethrow or wrap. A log call followed by `throw` in the
  same block is a finding.
- [ ] LG3 — `grep -n -E "getMessage\(\)|printStackTrace\("` in each log call and `catch`. Either one, or a throwable
  that is not the last argument, is a finding.
- [ ] LG1 — For each log call, find every trace id and business id. One passed as a `{}` argument or joined into the
  message, not as an MDC entry or `addKeyValue` field, is a finding.
- [ ] LG6 — `grep -n -E 'log\.[a-z]+\(".*" *\+'` in each changed file. A concatenated message, or a costly argument
  built outside a `Supplier` or an `isXEnabled()` guard, is a finding.
- [ ] LG5 — In each changed logging configuration, find the production encoder. A pattern layout with no CR/LF
  stripping of untrusted values and exception text is a finding.
- [ ] LG8 — `grep -n "getLogger("`. A string argument, or a class other than the declaring class, is a finding.
- [ ] LGN1 — In each changed logging configuration, `grep -n -i -E "FileAppender|RollingFile|logging\.file"`. A file
  appender, a rotation policy or a log path is a finding.
