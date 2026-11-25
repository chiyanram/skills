---
name: obs
description: Use when you write or review a log call or its level, a logger, a meter or tag, a span or observation, or the logging, metrics or tracing configuration. Log levels, structured logging, meter types and tags, RED and USE, span names, propagation and sampling.
---

# Observability

Telemetry earns its place when someone on call can answer "what broke, where, and for whom" from it, without leaking
data. Everything below serves that. Bad and good code for the rules: [examples.md](examples.md). To review a diff,
walk [review.md](review.md).

## Logging

- Log a constant message, with the trace id and business ids as key-value fields (MDC or `addKeyValue`), because one
  request is rebuilt from interleaved lines only by its fields. Any other value, such as a count or a status, is a
  `{}` placeholder in that constant template.
- Build the message from a template with `{}` placeholders, and pass a costly argument as a `Supplier` or behind
  `isXEnabled()`, because concatenation runs while the level is off and lets input rewrite the message.
- Log a failure once, where it is handled. Code that rethrows or wraps with the cause logs nothing, because each layer
  that logs counts the same failure again.
- Pass the exception as the last argument, or with `setCause(e)` on the fluent builder, because `e.getMessage()` loses
  the type and the stack, and `printStackTrace()` goes around the logger.
- Log the id and allowlisted fields of a request or response, because logs leak data. Passwords, tokens, session
  ids, auth or cookie headers, keys, connection strings, card data and sensitive PII stay out of every log.
- Create each logger with `LoggerFactory.getLogger(DeclaringClass.class)`, static or instance, because levels are
  configured by class name and a misnamed logger cannot be tuned.
- Emit production logs through a structured (JSON) encoder. On a plain pattern layout, strip CR and LF from untrusted
  values and exception messages, because a newline in input forges a log line.
- Write logs to stdout only, with no file appender, rotation or log path in app config, because the platform owns
  routing and storage, and a file in a container is lost or fills the disk.

## Log levels

| the event | level |
|---|---|
| the process cannot go on (bad config at startup, out of memory) | ERROR, then exit |
| a failure no code handled: it reaches the top-level handler (5xx), or a consumer gives up on a message | ERROR, with the throwable |
| a dependency call failed and the code handled it (timeout, retries used up, fallback) | WARN, once, with the throwable |
| one attempt inside a retry loop | DEBUG; the final outcome gets the one WARN |
| a client error: validation (400) or authentication (401) fails | INFO or WARN, as the project chooses; it is the client's fault |
| authorization denied (403) | WARN or higher: it can be a probe |
| an exception that shows no real problem, such as a client cancelling | DEBUG |
| a business or lifecycle event (order placed, job finished, service started) | INFO |
| diagnostic detail for debugging | DEBUG |
| fine-grained flow (method entry and exit, loop iterations) | TRACE |

## Metrics

- Tag a meter only with values from a closed set: a route template, an enum, an exception class, or `NOT_FOUND` for
  an unknown, because each new value is a new time series. An id goes in a log field or a span attribute.
- Give every endpoint and outbound dependency rate, errors and duration (RED), and every pool and queue utilisation,
  saturation and errors (USE), because overload stays invisible otherwise until users report it. One `Timer` with an
  `outcome` tag gives all three of RED, and a meter the framework already records counts.
- Name a meter dot-separated in lower case, with success and failure as an `outcome` tag on one meter, because split
  `*.success` and `*.failed` meters make the error ratio a manual join.
- Time a completed operation with a `Timer`, work in progress with a `LongTaskTimer`, and count only events nothing
  times. Gauge only an object something else holds strongly, because a weakly held gauge reports NaN.
- Publish latency as a percentile histogram (`publishPercentileHistogram()` or SLO buckets), because an average hides
  the slow tail and client-side `publishPercentiles()` cannot be combined across instances.
- Leave units out of meter names: record a `Timer` with a `Duration`, and set `baseUnit` on a summary, because the
  registry appends the base unit and a hand-written `ms` mixes units.
- Give each scheduled or batch job a gauge of its last success in epoch seconds and a `LongTaskTimer` while it runs,
  because a stalled job emits nothing an alert can see.

## Tracing

- Instrument through the facade (`ObservationRegistry`, `Tracer`), with no null check, because the facade is a no-op
  without a backend and an SDK type ties business code to a vendor. Which bridge sits under it is a project choice.
- Wrap one operation in `observe(() -> …)`. Where a lambda cannot hold it, `start()`, keep the scope in
  try-with-resources and `stop()` in `finally`, because a span that never ends leaks memory and never reaches the
  backend.
- Name a span for a class of operation, such as `orders.place` or `GET /orders/{id}`, and put ids in high-cardinality
  attributes, because a name per id explodes cardinality.
- Carry trace context with the propagator: an instrumented producer that writes message headers, and a
  context-propagating executor for a thread hand-off, because a copied `traceId` field links no consumer span to the
  producer's trace.
- Mark a span as an error once, where the operation failed and is handled. A handled miss, a retry or a server-side
  4xx is an event, not an error, because false errors inflate error alerts.
- Keep secrets, tokens and sensitive PII out of span names, attributes, events and status text, because span data is
  exported and stored like logs. Ids are fine as attributes.
- Use a parent-based sampler, with the root ratio set in configuration per environment, because independent ratios
  per service leave traces with missing spans. A ratio of 1.0 in one environment's config is a cost choice.
