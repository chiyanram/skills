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
| sends a message to another process | the propagator: an instrumented producer that writes trace headers (TR1) | a consumer span joins the producer's trace only through the propagated context |
| hands work to another thread | a context-propagating executor (TR1) | a bare executor drops the context, so the span on the new thread starts a new trace |
| measures one operation | `observation.observe(() -> …)` (TRN2) | an unended span leaks memory and never reaches the backend |
| starts a span it cannot wrap in a lambda | `start()`, the scope in try-with-resources, `stop()` in `finally` (TRN2) | the span must be ended and the scope closed, even when the work throws |
| needs a tracer or registry | the API or facade type, with no null check (TR2) | the API is a no-op without a backend, and SDK types tie code to a vendor |
| names a span | the class of operation: a constant such as `orders.place`, or `{method} {route template}` (TRN1) | per-id names explode cardinality |
| records an id | a high-cardinality key value (span attribute) (TRN1, TR3) | an id is a fine span attribute, and a high-cardinality key value never reaches a meter |
| catches a failure it handles, retries or turns into a 4xx | no error status (TRN3) | false errors inflate error alerts |
| sets the sampling ratio | a parent-based sampler, ratio in configuration (TR5) | a `ParentBased` sampler follows the root's decision, so no trace loses spans to independent per-service ratios |

Which tracer bridge sits under the facade is a project choice.

## Good / Bad

### TR1 — Propagate the context, not a copied field

**Bad**
```java
final var message = new OrderPlaced(
    order.id(),
    MDC.get("traceId"));
kafkaTemplate.send(
    "orders",
    message);
```
The copied field is a string, not a parent context, so it builds no link from the consumer's span to the producer's
trace.

**Good**
```java
// the template is built with observation enabled, so it writes the trace headers
kafkaTemplate.send(
    "orders",
    new OrderPlaced(order.id()));
```
The propagator injects the context into the message headers, and the consumer span joins the producer's trace.

### TR2 — The facade, with no null check

**Bad**
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

**Good**
```java
Observation.createNotStarted("orders.place", observationRegistry)
    .observe(() -> orderService.place(command));
```
The facade is a no-op when tracing is off, so no branch is needed.

### TRN1 — A span name for a class of operation

**Bad**
```java
Observation.createNotStarted("customers.load." + customerId, observationRegistry)
    .observe(() -> repository.load(customerId));
```
Each customer gets its own span name.

**Good**
```java
Observation.createNotStarted("customers.load", observationRegistry)
    .highCardinalityKeyValue("customer.id", customerId.toString())
    .observe(() -> repository.load(customerId));
```
The name is stable, and the id is a span attribute that never reaches a meter.

### TRN2 — End every span

**Bad**
```java
final var observation = Observation.start("invoices.render", observationRegistry);
renderer.render(invoice);
observation.stop();
```
An exception from `render` skips `stop()`, so the span leaks and is never exported.

**Good**
```java
Observation.createNotStarted("invoices.render", observationRegistry)
    .observe(() -> renderer.render(invoice));
```
One call opens the scope, records an error if the lambda throws, and stops the observation.

### TRN3 — An error status only for a failed operation

**Bad**
```java
try {
    return cache.get(orderId);
} catch (CacheMissException e) {
    observation.error(e);
    return repository.load(orderId);
}
```
The miss is handled and the order is returned, yet the span counts as an error.

**Good**
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
  (TR5). — **Do not skip when** the ratio or the sampler is set in code. — **Confidence** high
- **Skip when** an id is a span attribute: ids are fine on spans (TR3, TRN1). — **Do not skip when** the id is in
  the span name, or the value is a secret, token or sensitive PII. — **Confidence** high

## Review checks

Walk every span or observation, message producer and consumer, thread hand-off and tracing configuration added or
changed in the diff.

- [ ] TR1 — For each message sent to another process and each task handed to another thread, find the propagator or
  context-propagating executor. A `traceId` copied into a payload field, or a bare executor, is a finding.
- [ ] TRN2 — For each `start()`, find its `stop()` (`end()` on a `Span`) in a `finally` and its scope in
  try-with-resources, or an `observe(…)` instead. A path that skips the end is a finding.
- [ ] TR2 — `grep -n -i -E "io\.opentelemetry\.sdk|(tracer|tracing|observationregistry)[a-z]* *[!=]= *null|null *[!=]= *(tracer|tracing|observationregistry)|objects\.(nonnull|isnull)\((tracer|tracing|observationregistry)"`. An SDK type in application
  code, or a null check on a tracer or registry, is a finding.
- [ ] TR3 — For each span name, attribute, event and status description, read the value. A secret, token, credential
  or sensitive PII value is a finding.
- [ ] TRN1 — For each span or observation name, check it is a constant or a route template. An id or other unbounded
  value in the name is a finding; a name built only from bounded parts (method, route template) is not.
- [ ] TRN3 — For each `error(…)` or error status, check the operation failed. One in a `catch` that handles, retries or
  returns a 4xx is a finding, and so is the same failure marked by `error(…)` at more than one layer.
- [ ] TR5 — In each changed tracing configuration, find the sampler and its ratio. A sampler that ignores the parent,
  or a ratio set in code, is a finding.
