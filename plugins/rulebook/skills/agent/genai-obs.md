# GenAI observability

The spans, attributes, content capture and call records for model calls, tool calls and agent runs. Read it when you
write or review a span, metric or log for a model call, a tool call or an agent run, the capture of prompts and
completions, or the record kept for each model call.

## Rules

- Emit one client span per model call, named and attributed per the GenAI semantic conventions (provider, request
  and response model, finish reasons, usage, error type), because dashboards and alerts read those names. Spans go
  through the facade: `obs`, Tracing. A library's instrumentation that already follows the conventions needs only
  its configuration.
- Emit a tool span per tool call and an agent span per run, linked by call id, and mark a tool span errored when the
  tool returns an error result, because a returned error otherwise looks successful.
- Keep prompts, completions, system instructions and tool arguments out of spans and logs unless one deployment
  setting turns capture on, because they hold user data and are large. Secrets and bodies: `obs`, Logging and
  Tracing.
- Keep GenAI attribute and metric names in one constants file pinned to a dated semantic-conventions version, because
  the GenAI conventions are still in development and rename fields.
- Write a call record for every model call, failed, retried, resume, summariser and judge included, with request id,
  served model, retry count and final-attempt latency, because records of successes alone hide outages and cost.

## Good / Bad

### A returned tool error marks the span

**Bad**
```java
final var span = tracer.startToolSpan(call);
try (final var scope = span.makeCurrent()) {
    return tools.run(call);
} finally {
    span.end();
}
```
The tool returns `ToolResult.error(...)` without throwing. The span ends as a success, and the error rate shows
nothing.

**Good**
```java
final var span = tracer.startToolSpan(call);
try (final var scope = span.makeCurrent()) {
    final var result = tools.run(call);
    if (result.isError()) {
        span.setStatus(StatusCode.ERROR, result.errorType());
    }
    return result;
} finally {
    span.end();
}
```
An error result marks the span as errored, with a bounded error type and no exception text.

### Content stays out unless one setting turns it on

**Bad**
```java
span.setAttribute(GenAi.INPUT_MESSAGES, json.write(request.messages()));
log.info("model reply: {}", reply.text());
```
Every customer's messages and every answer go to the trace backend and the logs.

**Good**
```java
if (capture.contentEnabled()) {
    span.setAttribute(GenAi.INPUT_MESSAGES, json.write(request.messages()));
}
log.info("model call done requestId={} finishReason={}", reply.requestId(), reply.stopReason());
```
`capture.contentEnabled()` reads one deployment setting, off by default. The log holds ids and the stop reason only.

### A record for every call, not only the ones that worked

**Bad**
```java
final var reply = retrying.send(request);
callRecords.save(CallRecord.success(reply));
return reply;
```
A call that fails after three attempts leaves no record, and the retried attempts are not counted.

**Good**
```java
try {
    final var reply = retrying.send(request);
    callRecords.save(CallRecord.of(request, reply, retrying.stats()));
    return reply;
} catch (final ModelError error) {
    callRecords.save(CallRecord.failed(request, error, retrying.stats()));
    throw error;
}
```
Failed, retried, resume, summariser and judge calls all leave a record. It holds the purpose, request id, served
model, retry count and final-attempt latency.

## Review

Walk every model call, tool call and run, and every span, attribute and log call around them.

Each line is a finding, a blocker unless marked (warning).

- A model call with no client span, or a span name or attribute that differs from the GenAI semantic conventions.
- A missing tool or agent span, a span not linked by call id, or a tool span that stays OK on an error result.
- `grep -nE "INPUT_MESSAGES|OUTPUT_MESSAGES|SYSTEM_INSTRUCTIONS|TOOL_CALL_ARGUMENTS|prompt|completion"` in spans and
  log calls: a capture of content that the one deployment setting does not guard.
- (warning) A GenAI attribute or metric name as a string literal outside the one constants file, or a constants file
  with no pinned conventions version.
- A path that writes no call record on failure, or a record without request id, served model, retry count or
  final-attempt latency.
