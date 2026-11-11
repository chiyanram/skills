# GenAI observability

The spans, attributes, content capture and call records for model calls, tool calls and agent runs. Read it when you
write or review a span, metric or log for a model call, a tool call or an agent run, the capture of prompts and
completions, or the record kept for each model call.

Contents: Rules · When X, use Y · Good / Bad (AE38, AE39, AE41) · Decided edges · Review checks

## Rules

- **AE37** — Emit one client span per model call, named and attributed per the GenAI semantic conventions (provider,
  request and response model, finish reasons, usage, error type), because tools and alerts read those names.
- **AE38** — Emit a tool span per tool call and an agent span per run, linked by call id, and mark a tool span
  errored when the tool returns an error, because returned errors otherwise look successful.
- **AE39** — Keep prompts, completions, system instructions and tool arguments out of spans and logs unless one
  deployment setting turns capture on, because they hold user data and are large.
- **AE40** — Keep GenAI attribute and metric names in one constants file pinned to a dated semantic-conventions
  version, because the GenAI conventions are still in development and rename fields.
- **AE41** — Write a call record for every model call (failed, retried, resume, summariser, judge) with request id,
  served model, retry count and final-attempt latency, because success-only records hide outages and cost.

## When X, use Y

| situation | use | why |
|---|---|---|
| code calls a model | one client span, named and attributed per the GenAI semantic conventions | dashboards and alerts read those names (AE37) · spans through the facade: TR2 (`obs`'s `tracing`) |
| code runs a tool or an agent run | a tool span per call and an agent span per run, linked by call id | a run's trace shows which call did what (AE38) |
| a tool returns an error result, not an exception | the tool span marked errored | a returned error otherwise looks successful (AE38) |
| a span or log could hold a prompt, completion, system instruction or tool argument | nothing, unless the one deployment setting turns capture on | that content holds user data and is large (AE39) · secrets and bodies: LG4, TR3 (`obs`) |
| code names a GenAI attribute or metric | a constant from the one file pinned to a dated conventions version | the conventions are still in development and rename fields (AE40) |
| a model call ends, in any way | a call record with request id, served model, retry count and final-attempt latency | success-only records hide outages and cost (AE41) |

## Good / Bad

### AE38 — A returned tool error marks the span

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

### AE39 — Content stays out unless one setting turns it on

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

### AE41 — A record for every call, not only the ones that worked

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

## Decided edges

- **Skip when** content capture is on through the one deployment setting in an environment with no user data, such as
  a local run: AE39 allows it. — **Do not skip when** capture is turned on in code, or per call. — **Confidence**
  high
- **Skip when** the code uses a library's GenAI instrumentation that already follows the conventions: AE37 and AE40
  apply to its configuration, not to new spans. — **Do not skip when** your code adds its own spans or attributes. —
  **Confidence** medium

## Review checks

Walk every changed span, metric, log call and call record around a model call, a tool call or an agent run.

- [ ] AE37 — For each model call, find its client span. No span, or a name or attribute that differs from the GenAI
  semantic conventions, is a finding.
  Applies when: code calls a model
  Evidence: the span and its attributes at `file:line`
  Not a finding: a library's conventions-based instrumentation (decided edge)
  Severity: blocker
  Verify: re-open the span and the constants it uses
- [ ] AE38 — For each tool call and run, find the tool span and the agent span. A missing span, a span not linked by
  call id, or a tool span that stays OK on an error result, is a finding.
  Applies when: code runs a tool or an agent run
  Evidence: the span code at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open the tool executor and its error branch
- [ ] AE39 — `grep -nE "INPUT_MESSAGES|OUTPUT_MESSAGES|SYSTEM_INSTRUCTIONS|TOOL_CALL_ARGUMENTS|prompt|completion"` in
  spans and log calls. A capture of content not guarded by the one deployment setting is a finding.
  Applies when: a span or log call is added near a model or tool call
  Evidence: the attribute or log call at `file:line`
  Not a finding: capture turned on by the deployment setting (decided edge)
  Severity: blocker
  Verify: re-open the setting and every use of it
- [ ] AE40 — Find each GenAI attribute or metric name. A string literal outside the one constants file, or a file
  with no pinned conventions version, is a finding.
  Applies when: code names a GenAI attribute or metric
  Evidence: the literal at `file:line`
  Not a finding: a library's conventions-based instrumentation (decided edge)
  Severity: warning
  Verify: re-open the constants file
- [ ] AE41 — List every path that calls a model. A path that writes no call record on failure, or a record without
  request id, served model, retry count or final-attempt latency, is a finding.
  Applies when: code calls a model
  Evidence: the record write, or its absence, at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open each call path and its error branch
