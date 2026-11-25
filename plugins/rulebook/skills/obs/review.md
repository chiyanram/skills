# Observability review

Walk every log call, logger field, `catch` block that logs, meter, tag, span, message producer and consumer,
thread hand-off, and logging, metrics or tracing configuration added or changed in the diff. Each line is a finding
when it holds. The rules behind each line are in [SKILL.md](SKILL.md).

## Log levels

- [ ] For each log call, find its row in the level table in SKILL.md. A level that differs from its row is a finding, such as an
  ERROR for a handled dependency failure or a WARN per retry attempt. A process-ending event that does not exit after
  its log call is a finding. "Once" and "with the throwable" are checked under Logging.
- [ ] For each 400 or 401 log call, an ERROR is a finding. When the project's docs name INFO or WARN, a level that
  differs from that choice is a finding.

## Logging

- [ ] **No secrets in logs**: For each log call, read every argument and field. A password, token, session id, auth or cookie header,
  key, connection string, card data, sensitive PII value or whole request or response body is a finding.
- [ ] **Log once**: For each `catch` that logs, check that it does not rethrow or wrap. A log call followed by `throw` in the
  same block is a finding.
- [ ] **The exception**: `grep -n -E "getMessage\(\)|printStackTrace\("`. A `getMessage()` inside a log call's arguments, any
  `printStackTrace(` call, or a throwable that is neither the last argument nor set with `setCause`, is a finding.
- [ ] **Ids as fields**: For each log call, find every trace id and business id. One passed as a `{}` argument or joined into the
  message, not as an MDC entry or `addKeyValue` field, is a finding.
- [ ] **Templates**: `grep -n -E '(log|logger|LOG|LOGGER)\.[a-zA-Z]+\(.*(" *\+|\+ *")|setMessage\(.*(" *\+|\+ *")'` in each
  changed file, and read multi-line calls by eye. A concatenated message, or a costly argument built outside a
  `Supplier` or an `isXEnabled()` guard, is a finding.
- [ ] **Structured output**: In each changed logging configuration, find the production encoder. One that is not a structured (JSON)
  encoder is a finding. On any pattern layout, a message or exception converter without CR/LF stripping (Logback
  `%replace`, Log4j2 `%enc{}{CRLF}`) is a finding.
- [ ] **Logger name**: `grep -n "getLogger("`. A string argument, or a class other than the declaring class, is a finding.
- [ ] **Stdout only**: In each changed logging configuration,
  `grep -n -i -E 'FileAppender|<(Rolling)?(RandomAccess)?File[ >]|MemoryMappedFile|type *= *(Rolling)?(RandomAccess)?File|logging\.file|^\s+file:|rollingpolicy|file-appender'`.
  A file appender, a rotation policy or a log path is a finding.

## Metrics

- [ ] **Bounded tags**: For each tag and each `lowCardinalityKeyValue`, read where its value comes from. An id, email, raw URL, user input or exception message is
  a finding; an unknown value not mapped to a fixed one such as `NOT_FOUND` is a finding.
- [ ] **RED and USE**: For each new endpoint and outbound client, find its rate, error and duration meters; for each new pool and
  queue, its utilisation, saturation and error meters. One missing is a finding. One `Timer` with an `outcome` tag
  gives all three, and a meter the framework records for it (an HTTP server or client timer, an executor or pool
  binder) counts.
- [ ] **One meter, outcome tag**: `grep -n -E '"[a-z0-9._]*[._](success|succeeded|ok|failed|failure|failures|error|errors)[._"]'` and
  `grep -n -E '(counter|timer|builder)\("[^"]*" *\+'` in meter names. A paired or generated meter name,
  or one not dot-separated lower case, is a finding.
- [ ] **Meter types**: For each new meter, check its type against what it measures. A `Counter` or `DistributionSummary` for a
  duration, a `Counter` for an event a `Timer` already records, in-flight work with no `LongTaskTimer`, or a gauge on
  an object nothing else holds, is a finding.
- [ ] **Histograms**: `grep -n -E "publishPercentiles\(|publishPercentileHistogram|serviceLevelObjectives\(|histogram *= *true|percentiles-histogram"`
  across code and config, for each latency `Timer`. Client-side percentiles only, or an average only, is a finding.
- [ ] **No units in names**: `grep -n -E '"[a-zA-Z0-9._]*([._](ms|millis|milliseconds|nanos|micros|seconds|secs|bytes|kb|mb)|[a-z](Ms|Millis|Nanos|Seconds|Bytes))[._"]'`
  in meter names. A unit in the name, a `Timer` recorded with a raw number, or a `DistributionSummary` of a quantity
  with a unit and no `baseUnit`, is a finding.
- [ ] **Job health**: For each new scheduled or batch job, find a gauge of its last success as epoch seconds and a
  `LongTaskTimer`. A job with either missing, or a "seconds since" gauge, is a finding.

## Tracing

- [ ] **Propagation**: For each message sent to another process and each task handed to another thread, find the propagator or
  context-propagating executor. A `traceId` copied into a payload field, or a bare executor, is a finding.
- [ ] **End every span**: For each `start()`, find its `stop()` (`end()` on a `Span`) in a `finally` and its scope in
  try-with-resources, or an `observe(…)` instead. A path that skips the end is a finding.
- [ ] **The facade**: `grep -n -i -E "io\.opentelemetry\.sdk|(tracer|tracing|observationregistry)[a-z]* *[!=]= *null|null *[!=]= *(tracer|tracing|observationregistry)|objects\.(nonnull|isnull)\((tracer|tracing|observationregistry)"`. An SDK type in application
  code, or a null check on a tracer or registry, is a finding.
- [ ] **No secrets in spans**: For each span name, attribute, event and status description, read the value. A secret, token, credential
  or sensitive PII value is a finding.
- [ ] **Span names**: For each span or observation name, check it is a constant or a route template. An id or other unbounded
  value in the name is a finding; a name built only from bounded parts (method, route template) is not.
- [ ] **Error status**: For each `error(…)` or error status, check the operation failed. One in a `catch` that handles, retries or
  returns a 4xx is a finding, and so is the same failure marked by `error(…)` at more than one layer.
- [ ] **Sampling**: In each changed tracing configuration, find the sampler and its ratio. A sampler that ignores the parent,
  or a ratio set in code, is a finding.
