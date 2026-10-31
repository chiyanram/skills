# Tracing

How code starts, names, ends and propagates spans, what a span may hold, and how traces are sampled. Read it when you
write or review an `Observation`, a span, a message producer or consumer, a hand-off between threads, or the tracing
configuration.

Contents: Rules · When X, use Y · Good / Bad (TR1, TR2, TRN1, TRN2, TRN3) · Decided edges · Review checks

## Rules

- **TR1** — Carry trace context with the propagator (message headers, a context-propagating executor), never a
  hand-copied `traceId` field, because consumer spans then can't join the producer's trace.
- **TRN2** — End every span you start: `observe(() -> …)`, or `stop()` in `finally` with the scope in
  try-with-resources, because an unended span leaks memory and never reaches the backend.
- **TR2** — Instrument through the API or facade (`ObservationRegistry`, `Tracer`), never SDK types, and never
  null-check tracing, because the API is a no-op without a backend and SDK types tie code to a vendor.
- **TR3** — Put no secrets, tokens or sensitive PII in span names, attributes, events or status text (ids are fine),
  because span data is exported and stored like logs.
- **TRN1** — Name a span for a class of operation (`orders.place`, `GET /orders/{id}`), with ids in attributes, never
  in the name, because per-id names explode cardinality.
- **TRN3** — Mark a span as an error only when its operation failed, once, where handled; never a handled or retried
  failure or a server-side 4xx, because false errors inflate error alerts.
- **TR5** — Use a parent-based sampler and set the root ratio in config per environment, never in code, because
  independent per-service ratios leave traces with missing spans.

## When X, use Y

| the code | use | why |
|---|---|---|
| sends a message to another process | the propagator: an instrumented producer that writes trace headers (TR1) | OpenTelemetry messaging "A producer SHOULD attach a message creation context"; propagators API; Spring Boot tracing · r47 :611-613 |
| hands work to another thread | a context-propagating executor (TR1) | OpenTelemetry propagators API; Micrometer Tracing "continue a span in a new thread" · r47 :612, :614 |
| measures one operation | `observation.observe(() -> …)` (TRN2) | OpenTelemetry Trace API "Any span that is created MUST also be ended"; Micrometer Observation · r47 :646-647 |
| starts a span it cannot wrap in a lambda | `start()`, the scope in try-with-resources, `stop()` in `finally` (TRN2) | OpenTelemetry Trace API; Micrometer Observation "The Scope must be closed" · r47 :646-647 |
| needs a tracer or registry | the API or facade type, with no null check (TR2) | OpenTelemetry library guidelines "the API calls should be no-ops"; Trace API; Micrometer Tracing "without vendor lock-in" · r47 :621-623 |
| names a span | the class of operation: a verb on a resource, or `{method} {route template}` (TRN1) | OpenTelemetry Trace API "the most general string"; HTTP spans; Micrometer Observation · r47 :639-641 |
| records an id | a high-cardinality key value (span attribute) (TRN1, TR3) | OpenTelemetry Trace API "account_id=42 would make a nice Span attribute"; Micrometer Observation · r47 :634 |
| catches a failure it handles, retries or turns into a 4xx | no error status; an event if it is worth recording (TRN3) | OpenTelemetry Trace API, recording errors "SHOULD NOT be recorded on spans", HTTP spans · r47 :652-654 |
| sets the sampling ratio | a parent-based sampler, ratio in configuration (TR5) | OpenTelemetry Trace SDK `ParentBased`; Spring Boot `management.tracing.sampling.probability` · r47 :661-662 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file. TRN3's sources are all
OpenTelemetry documents. Which tracer bridge sits under the facade is a project choice (r47 :666-672).

## Good / Bad

### TR1 — Propagate the context, not a copied field

**Bad** (neutral)
```java
final var message = new OrderPlaced(
    order.id(),
    MDC.get("traceId"));
kafkaTemplate.send(
    "orders",
    message);
```
The consumer reads a string, not a parent context, so it starts an unrelated trace.

**Good** (neutral)
```java
// the template is built with observation enabled, so it writes the trace headers
kafkaTemplate.send(
    "orders",
    new OrderPlaced(order.id()));
```
The propagator injects the context into the message headers, and the consumer span joins the producer's trace.

### TR2 — The facade, with no null check

**Bad** (neutral)
```java
private final SdkTracerProvider tracerProvider;

if (tracerProvider != null) {
    final var span = tracerProvider.get("orders").spanBuilder("orders.place").startSpan();
    try {
        orderService.place(command);
    } finally {
        span.end();
    }
}
```
An SDK type sits in business code, and a null branch guards it.

**Good** (neutral)
```java
Observation.createNotStarted("orders.place", observationRegistry)
    .observe(() -> orderService.place(command));
```
The facade is a no-op when tracing is off, so no branch is needed.

### TRN1 — A span name for a class of operation

**Bad** (neutral)
```java
Observation.createNotStarted("customers.load." + customerId, observationRegistry)
    .observe(() -> repository.load(customerId));
```
Each customer gets its own span name.

**Good** (neutral)
```java
Observation.createNotStarted("customers.load", observationRegistry)
    .highCardinalityKeyValue("customer.id", customerId.toString())
    .observe(() -> repository.load(customerId));
```
The name is stable, and the id is a span attribute that never reaches a meter.

### TRN2 — End every span

**Bad** (neutral)
```java
final var observation = Observation.start("invoices.render", observationRegistry);
renderer.render(invoice);
observation.stop();
```
An exception from `render` skips `stop()`, so the span leaks and is never exported.

**Good** (neutral)
```java
Observation.createNotStarted("invoices.render", observationRegistry)
    .observe(() -> renderer.render(invoice));
```
One call opens the scope, records an error, and stops the observation.

### TRN3 — An error status only for a failed operation

**Bad** (neutral)
```java
try {
    return cache.get(orderId);
} catch (CacheMissException e) {
    observation.error(e);
    return repository.load(orderId);
}
```
The miss is handled and the order is returned, yet the span counts as an error.

**Good** (neutral)
```java
try {
    return cache.get(orderId);
} catch (CacheMissException e) {
    observation.event(Observation.Event.of("cache.miss"));
    return repository.load(orderId);
}
```
The handled miss is an event, so the error rate counts only real failures.

## Decided edges

- **Skip when** an environment sets its ratio to 1.0 in configuration: the ratio is a cost choice per environment
  (TR5; OpenTelemetry Trace SDK, Spring Boot tracing, r47 :661-662). — **Do not skip when** the ratio or the sampler
  is set in code. — **Confidence** high
- **Skip when** an id is a span attribute: ids are fine on spans (TR3, TRN1; OpenTelemetry Trace API, Micrometer
  Observation, r47 :634). — **Do not skip when** the id is in the span name, or the value is a secret, token or
  sensitive PII. — **Confidence** high

## Review checks

Walk every span or observation, message producer and consumer, thread hand-off and tracing configuration added or
changed in the diff.

- [ ] TR1 — For each message sent to another process and each task handed to another thread, find the propagator or
  context-propagating executor. A `traceId` copied into a payload field, or a bare executor, is a finding.
- [ ] TRN2 — For each `start()`, find its `stop()` in a `finally` and its scope in try-with-resources, or an
  `observe(…)` instead. A path that skips `stop()` is a finding.
- [ ] TR2 — `grep -n -E "io\.opentelemetry\.sdk|Tracer.*!= *null|Registry.*!= *null"`. An SDK type in application
  code, or a null check on a tracer or registry, is a finding.
- [ ] TR3 — For each span name, attribute, event and status description, read the value. A secret, token, credential
  or sensitive PII value is a finding.
- [ ] TRN1 — For each span or observation name, check it is a constant or a route template. An id, or any value
  concatenated into the name, is a finding.
- [ ] TRN3 — For each `error(…)` or error status, check the operation failed. One in a `catch` that handles, retries or
  returns a 4xx is a finding.
- [ ] TR5 — In each changed tracing configuration, find the sampler and its ratio. A sampler that ignores the parent,
  or a ratio set in code, is a finding.
