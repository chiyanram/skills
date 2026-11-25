# Observability examples

Good / Bad pairs for the rules in [SKILL.md](SKILL.md).

## Ids as fields, not in the text

From "Logging".

**Bad**
```java
log.info("order {} placed by customer {}", orderId, customerId);
```
The ids sit inside the text, so no query can select one order's lines without parsing every message.

**Good**
```java
// the trace id comes from the MDC
log.atInfo()
    .setMessage("order placed")
    .addKeyValue("orderId", orderId)
    .addKeyValue("customerId", customerId)
    .log();
```
The message is constant, and each id is a field the encoder writes beside it.

## Log once, where the failure is handled

From "Logging".

**Bad**
```java
try {
    paymentGateway.charge(invoice);
} catch (GatewayException e) {
    log.error("charge failed", e);
    throw new PaymentFailedException(invoice.id(), e);
}
```
The top-level handler logs the same failure again, so one failure counts twice.

**Good**
```java
try {
    paymentGateway.charge(invoice);
} catch (GatewayException e) {
    throw new PaymentFailedException(invoice.id(), e);
}
```
It wraps with the cause and logs nothing. The handler that decides the response logs it once.

## The exception as the last argument

From "Logging".

**Bad**
```java
log.warn("refund failed: {}", e.getMessage());
```
Only the message is kept. The type and the stack are lost.

**Good**
```java
// the payment id is in the MDC
log.warn("refund failed", e);
```
The throwable is the last argument, so the logger prints its type and stack.

## Bounded tag values only

From "Metrics".

**Bad**
```java
meterRegistry.counter(
        "invoices.sent",
        "customerId", customer.id().toString(),
        "path", request.getRequestURI())
    .increment();
```
Each customer and each raw path becomes a new time series.

**Good**
```java
meterRegistry.counter(
        "invoices.sent",
        "channel", invoice.channel().name(),
        "outcome", outcome.name())
    .increment();
```
Both tags are closed sets. The customer id belongs in a log field or a span attribute.

## An aggregable histogram

From "Metrics".

**Bad**
```java
final var timer = Timer.builder("payments.authorize")
    .publishPercentiles(0.5, 0.95, 0.99)
    .register(meterRegistry);
```
Each instance computes its own percentiles, and they cannot be combined across instances.

**Good**
```java
final var timer = Timer.builder("payments.authorize")
    .publishPercentileHistogram()
    .register(meterRegistry);
```
The backend gets buckets it can aggregate into any percentile.

## The outcome as a tag on one meter

From "Metrics".

**Bad**
```java
meterRegistry.counter("orders.placed.success").increment();
meterRegistry.counter("orders.placed.failed").increment();
```
The error ratio needs two meters joined by hand.

**Good**
```java
meterRegistry.counter(
        "orders.placed",
        "outcome", failed ? "failure" : "success")
    .increment();
```
One meter. The error ratio is a filter on the `outcome` tag.

## Propagate the context, not a copied field

From "Tracing".

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

## The facade, with no null check

From "Tracing".

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

## A span name for a class of operation

From "Tracing".

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

## End every span

From "Tracing".

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

## An error status only for a failed operation

From "Tracing".

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
} catch (final CacheMissException _) {
    observation.event(Observation.Event.of("cache.miss"));
    return repository.load(orderId);
}
```
The handled miss is an event, so the error rate counts only real failures.
