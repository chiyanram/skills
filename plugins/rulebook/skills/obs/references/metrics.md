# Metrics

Which meters a service records, how they are named and tagged, and which meter type fits which measurement. Read it
when you write or review a meter, a tag, a `Timer` or histogram setting, or the metrics of an endpoint, a dependency, a
pool, a queue or a job.

Contents: Rules · When X, use Y · Good / Bad (MX1, MXN1, MX3) · Decided edges · Review checks

## Rules

- **MX1** — Tag a meter only with bounded values (route template, enum, exception class, `NOT_FOUND`), never an id,
  email, raw URL or message, because each new value is a new time series.
- **MX5** — Give every endpoint and dependency rate, errors and duration (RED); every pool and queue utilisation,
  saturation and errors (USE), because overload otherwise stays invisible until users report it.
- **MX3** — Name meters dot-separated lower case with the outcome as a tag; never `*.success`/`*.failed` pairs or
  generated names, because split meters make the error ratio unqueryable.
- **MX2** — Time durations with `Timer` (`LongTaskTimer` for in-flight work), count only untimed events, gauge only a
  strongly held object, because a summary mis-scales time and a weak gauge reports NaN.
- **MXN1** — Publish latency as a percentile histogram, never only an average or client-side `publishPercentiles()`,
  because averages hide the slow tail and client percentiles can't be aggregated across instances.
- **MXN2** — Put no unit in a meter name; record a `Timer` with a `Duration`, set `baseUnit` on summaries, because the
  registry appends base units and a hand-written `ms` mixes units.
- **MXN3** — Give a scheduled or batch job a last-success epoch-seconds gauge plus a `LongTaskTimer` while it runs,
  because a stalled job emits nothing an alert can see.

## When X, use Y

| the measurement is | use | why |
|---|---|---|
| a tag value | a closed set: route template, enum, exception class, `NOT_FOUND` (MX1) | Prometheus naming "Do not use labels to store dimensions with high cardinality"; Micrometer naming, Observation · r47 :548-550 |
| an endpoint or an outbound dependency | rate, errors and duration (MX5) | Grafana dashboard best practices (RED, golden signals); Prometheus instrumentation · r47 :587-589 |
| a pool or a queue | utilisation, saturation (depth, wait) and errors (MX5) | Grafana dashboard best practices (USE); Prometheus instrumentation "the number of queued requests" · r47 :587-588 |
| success and failure of one operation | one meter with an `outcome` tag (MX3) | Micrometer naming; Prometheus instrumentation "create a single metric … with a `code` label"; OpenTelemetry recording errors · r47 :571-573 |
| how long a completed operation took | a `Timer` (MX2) | Micrometer timers "you should use a `Timer` rather than a `DistributionSummary`"; counters · r47 :555-556 |
| work still in progress | a `LongTaskTimer` (MX2) | Micrometer long task timers "A normal Timer only records the duration *after* the task is complete" · r47 :558 |
| a value that can go down | a gauge on a strongly held object (MX2) | Prometheus instrumentation "if the value can go down, it is a gauge"; Micrometer gauges · r47 :557, :559 |
| latency percentiles | `publishPercentileHistogram()` or SLO buckets (MXN1) | Micrometer histograms "aggregable (across dimensions)"; Prometheus histograms · r47 :564-565 |
| a unit | none in the name; a `Duration` for timers, `baseUnit` for summaries (MXN2) | OpenTelemetry metrics "SHOULD NOT include the units in the metric name"; Prometheus naming "base units" · r47 :580-582 |
| a scheduled or batch job | a gauge of the last success as epoch seconds, plus a `LongTaskTimer` (MXN3) | Prometheus instrumentation "the last time it succeeded", alerting; Micrometer long task timers · r47 :594-596 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file. Every rule has ≥2
independent sources, quoted there; none comes from one project's history (operator, 2026-10-31, agent-factory#34).
Grafana's page carries the Google SRE golden signals; the SRE book is not counted as a separate source.

## Good / Bad

### MX1 — Bounded tag values only

**Bad** (neutral)
```java
meterRegistry.counter(
        "invoices.sent",
        "customerId", customer.id().toString(),
        "path", request.getRequestURI())
    .increment();
```
Each customer and each raw path becomes a new time series.

**Good** (neutral)
```java
meterRegistry.counter(
        "invoices.sent",
        "channel", invoice.channel().name(),
        "outcome", outcome.name())
    .increment();
```
Both tags are closed sets. The customer id belongs in a log field or a span attribute.

### MXN1 — An aggregable histogram

**Bad** (neutral)
```java
final var timer = Timer.builder("payments.authorize")
    .publishPercentiles(0.5, 0.95, 0.99)
    .register(meterRegistry);
```
Each instance computes its own percentiles, and they cannot be combined across instances.

**Good** (neutral)
```java
final var timer = Timer.builder("payments.authorize")
    .publishPercentileHistogram()
    .register(meterRegistry);
```
The backend gets buckets it can aggregate into any percentile.

### MX3 — The outcome as a tag on one meter

**Bad** (neutral)
```java
meterRegistry.counter("orders.placed.success").increment();
meterRegistry.counter("orders.placed.failed").increment();
```
The error ratio needs two meters joined by hand.

**Good** (neutral)
```java
meterRegistry.counter(
        "orders.placed",
        "outcome", failed ? "failure" : "success")
    .increment();
```
One meter. The error ratio is a filter on the `outcome` tag.

## Decided edges

- **Skip when** an id is recorded on a span or a log line, not on a meter: ids are fine there (MX1; Micrometer
  Observation "High cardinality key values are not included in meters", r47 :634). — **Do not skip when** the same
  value is passed as a meter tag. — **Confidence** high

## Review checks

Walk every meter, tag and `Timer` or histogram setting added or changed in the diff, and every new endpoint, outbound
client, pool, queue and scheduled job.

- [ ] MX1 — For each tag, read where its value comes from. An id, email, raw URL, user input or exception message is
  a finding; an unknown value not mapped to a fixed one such as `NOT_FOUND` is a finding.
- [ ] MX5 — For each new endpoint and outbound client, find its rate, error and duration meters; for each new pool and
  queue, its utilisation, saturation and error meters. One missing is a finding.
- [ ] MX3 — `grep -n -E '"[a-z.]*\.(success|failed|failure|error)"'` in meter names. A paired or generated meter name,
  or one not dot-separated lower case, is a finding.
- [ ] MX2 — For each new meter, check its type against what it measures. A `Counter` or `DistributionSummary` for a
  duration, or a gauge on an object nothing else holds, is a finding.
- [ ] MXN1 — `grep -n -E "publishPercentiles\(|publishPercentileHistogram"` in each latency `Timer`. Client-side
  percentiles only, or an average only, is a finding.
- [ ] MXN2 — `grep -n -E '"[a-z.]*[._](ms|millis|seconds|bytes)"'` in meter names. A unit in the name, or a `Timer`
  recorded with a raw number, is a finding.
- [ ] MXN3 — For each new scheduled or batch job, find a gauge of its last success as epoch seconds and a
  `LongTaskTimer`. A job with either missing, or a "seconds since" gauge, is a finding.
