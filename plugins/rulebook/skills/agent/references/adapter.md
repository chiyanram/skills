# Model adapter

How the adapter behind your model port turns one provider's replies, errors, streams and usage into your own types,
and how fallback to another model wraps it. Read it when you write or review a model adapter, a stop reason, a model
error or retry policy, a streamed reply, a tool call's arguments, a usage record, an output-token cap or a fallback
model.

Contents: Rules · When X, use Y · Good / Bad (AE2, AE5, AEN2, AE10) · Decided edges · Review checks

## Rules

- **AE1** — Map each provider's stop reason onto one closed set (end, truncated, tool call, refused, context
  exceeded, paused, error) and switch on it exhaustively, because an unmapped refusal or truncation reads as success.
- **AE2** — Never run tool calls from a reply that stopped truncated or refused; end the turn with that typed
  outcome, because truncated arguments often parse as a valid partial object.
- **AE6** — Parse a tool call's complete arguments with a JSON library and validate them against the schema; send a
  malformed call back to the model as an error, because empty-argument fallbacks run the tool wrongly.
- **AE5** — Never retry a model call after its first streamed chunk reached a consumer; end it as a typed failure,
  because a retry replays text the user already saw.
- **AE3** — Have each adapter return one normalised error (status, retry-after, request id, timeout or network,
  response started), and let the retry policy above it decide, because retries inside adapters multiply attempts.
- **AEN2** — Treat a 429 or an explicit retry-after as back-pressure for the retry policy and rate limiter; count an
  overload toward the breaker only once retries give up, because throttling otherwise trips a healthy breaker.
- **AE8** — Treat an error event inside a stream as that request's failure even after a 200, and skip keep-alive and
  unknown event types, because providers fail mid-stream and add event types.
- **AE7** — Fold each provider's usage into one record (input including cache, cache read, cache write, output,
  reasoning) from the final cumulative value, because providers split and repeat these counts differently.
- **AE9** — Set every model call's output-token cap from agent or model configuration, sized as a backstop, never as
  an adapter default, because a hidden low cap truncates answers and wastes retries.
- **AE10** — Fall back to another model through a decorator over the model port with an explicit model mapping, and
  price usage on the model that served it, because the primary's name is wrong elsewhere.

## When X, use Y

| situation | use | why |
|---|---|---|
| the provider returns a stop or finish reason | the closed `StopReason` set, mapped in the adapter; an unknown value maps to error | an unmapped refusal or truncation reads as success (AE1) · the switch form: TY2 (`code`'s `types`) |
| a reply holds tool calls | run them only when the stop reason is tool call | truncated arguments parse as a valid partial object (AE2) |
| a tool call's arguments arrive | a JSON library over the complete arguments, then the tool's schema | an empty-argument fallback runs the tool wrongly (AE6) · the check before a sink: SE10 (`code`'s `security`) |
| a call fails | one normalised error from the adapter, and one retry policy above it | retries inside adapters multiply attempts (AE3) · one layer retries: CC12 (`code`'s `concurrency`) |
| a streamed call fails | a retry only while no chunk has reached a consumer; after that, a typed failure | a retry replays text the user already saw (AE5) |
| the provider answers with a 429 or an explicit retry-after | back-pressure: the retry policy and the rate limiter, not the breaker | throttling otherwise trips a healthy breaker (AEN2) · the breaker itself: CC11 |
| the provider answers with an overload and no retry-after | the retry policy first; a breaker failure only once it gives up | one overload burst that a retry would ride out does not open the breaker (AEN2) |
| a stream sends an error event, a keep-alive or an event type you do not know | the error ends the request as failed; the other two are skipped | providers fail mid-stream after a 200, and add event types (AE8) |
| the provider reports token usage | one usage record, from the final cumulative value | providers split and repeat the counts differently (AE7) · its live test: LS16 (`testing`'s `llm-live-tests`) |
| a call needs an output-token cap | a value from agent or model configuration, sized as a backstop | a hidden low cap truncates answers and wastes retries (AE9) |
| a second model may answer when the first fails | a fallback decorator over the port, with an explicit model mapping | the primary's model name is wrong on another provider (AE10) · its test: LS9 (`testing`'s `llm-tests`) |

## Good / Bad

### AE2 — Tool calls run only on a tool-call stop

**Bad**
```java
final var reply = model.send(request);
if (!reply.toolCalls().isEmpty()) {
    return runTools(reply.toolCalls());
}
return Outcome.answer(reply.text());
```
A reply cut off by the token cap still holds a tool call, and its truncated arguments parse. The refund tool runs
with half an order.

**Good**
```java
final var reply = model.send(request);
return switch (reply.stopReason()) {
    case TOOL_CALL -> runTools(reply.toolCalls());
    case END -> Outcome.answer(reply.text());
    case PAUSED -> Outcome.paused(reply);
    case TRUNCATED, REFUSED, CONTEXT_EXCEEDED, ERROR -> Outcome.stopped(reply.stopReason());
};
```
Only a tool-call stop reaches the tools. The switch lists every case, so a new stop reason does not compile until
it is handled.

### AE5 — No retry after the first chunk reached the user

**Bad**
```java
RetryDecision decide(final ModelError error, final int attempt) {
    if (error.status() >= 500 && attempt < MAX_ATTEMPTS) {
        return RetryDecision.after(jitteredBackoff(attempt));
    }
    return RetryDecision.stop();
}
```
A 503 that arrives in the middle of a stream is retried. The user sees the first half of the answer twice.

**Good**
```java
RetryDecision decide(final ModelError error, final int attempt) {
    if (error.responseStarted()) {
        return RetryDecision.stop();
    }
    if (error.status() >= 500 && attempt < MAX_ATTEMPTS) {
        return RetryDecision.after(jitteredBackoff(attempt));
    }
    return RetryDecision.stop();
}
```
The adapter's normalised error says whether the response started (AE3). After the first chunk, the call ends as a
typed failure.

### AEN2 — A rate limit is back-pressure; an overload counts once retries give up

**Bad**
```java
} catch (final ModelError error) {
    breaker.recordFailure();
    throw error;
}
```
A burst of rate-limit responses opens the breaker. Every run then fails fast while the provider is healthy.

**Good**
```java
try {
    return retrying.send(request);
} catch (final ModelError error) {
    if (error.status() == 429 || error.retryAfter().isPresent()) {
        limiter.slowDown(error.retryAfter());
    } else {
        breaker.recordFailure();
    }
    throw error;
}
```
This code sits outside the retry policy, so an error reaches it only once retries gave up. Throttling slows the
caller down; an overload that outlasted the retries counts toward the breaker.

### AE10 — Fallback is a decorator with a model mapping

**Bad**
```java
try {
    return primaryClient.send(request);
} catch (final ModelUnavailable unavailable) {
    return secondClient.send(request);
}
```
The second provider gets the first provider's model name. The usage of the reply is priced as the primary model.

**Good**
```java
public ModelReply send(final ModelRequest request) {
    try {
        return primary.send(request);
    } catch (final ModelUnavailable unavailable) {
        return fallback.send(request.withModel(mapping.fallbackFor(request.model())));
    }
}
```
`FallbackModel` implements the model port and wraps two ports. The mapping names the fallback model, and each reply
carries the model that served it, so cost is priced on that model.

## Decided edges

- **Skip when** the code uses an agent library whose own types already hold a closed stop reason and one usage record:
  AE1 and AE7 apply to the mapping into your types, not to raw provider fields. — **Do not skip when** your code reads
  a raw provider field, such as a stop-reason string or a usage map. — **Confidence** medium
- **Skip when** a stream is still buffered inside the adapter and no chunk has gone to a user, a socket or a store: a
  retry is allowed (AE5). — **Do not skip when** any chunk was forwarded. — **Confidence** high
- **Skip when** a 429 says a quota or spend cap is used up and carries no retry-after: do not retry it (CC16), and
  stop the run with a typed reason; it is not a breaker failure (AEN2). — **Do not skip when** the response asks the
  caller to wait. — **Confidence** medium
- **Skip when** the output-token cap is a default in agent configuration that a model entry can override: that is
  configuration (AE9). — **Do not skip when** the value is a constant in the adapter. — **Confidence** high

## Review checks

Walk every changed model adapter, model port decorator, retry policy, stream handler and usage record.

- [ ] AE1 — Find where each provider stop or finish reason is read. A raw string compared outside the adapter, or a
  switch over the closed set with a `default`, is a finding.
  Applies when: code reads a stop or finish reason from a provider reply
  Evidence: the read or the switch at `file:line`
  Not a finding: a library's closed stop-reason type (decided edge)
  Severity: Act on
  Verify: re-open the mapping and every switch over its result
- [ ] AE2 — Find each path that runs tool calls from a reply. A path that does not first require the tool-call stop
  reason is a finding.
  Applies when: code runs tool calls from a model reply
  Evidence: the path at `file:line` and the condition it checks
  Not a finding: none
  Severity: Act on
  Verify: re-open the loop's step from reply to tool run
- [ ] AE6 — Find where tool-call arguments are parsed. Hand-built parsing, an empty-object fallback, or no schema
  check before the tool runs is a finding.
  Applies when: code parses tool-call arguments
  Evidence: the parse and the tool run at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the parse and the branch for a malformed call
- [ ] AE5 — Open the retry policy for streamed calls. A retry that does not check that no chunk reached a consumer is
  a finding.
  Applies when: a streamed model call can be retried
  Evidence: the retry condition at `file:line`
  Not a finding: a stream still buffered in the adapter (decided edge)
  Severity: Act on
  Verify: re-open where chunks are forwarded and where the retry decides
- [ ] AE3 — Find each retry loop around a model call. A retry inside an adapter, or an adapter error without status,
  retry-after, request id, timeout-or-network and response-started, is a finding.
  Applies when: an adapter or its caller handles a failed model call
  Evidence: the retry or the error type at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the error type and every caller that retries
- [ ] AEN2 — Find what the circuit breaker counts. A 429 or a response with retry-after counted as a breaker failure,
  or an overload counted before the retry policy gives up, is a finding.
  Applies when: a breaker wraps a model call
  Evidence: the record call, where it sits against the retry policy, and the errors that reach it, at `file:line`
  Not a finding: a used-up quota with no retry-after (decided edge)
  Severity: Act on
  Verify: re-open the breaker's failure predicate
- [ ] AE8 — Open the stream's event handler. An error event that does not fail the request, or an unknown or
  keep-alive event that throws or ends the stream, is a finding.
  Applies when: code reads a provider's event stream
  Evidence: the event branch at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the handler's branches and its fall-through
- [ ] AE7 — Open the usage mapping. Usage summed across stream events, or a cache or reasoning count dropped or
  counted twice, is a finding.
  Applies when: code reads provider usage
  Evidence: the mapping at `file:line`
  Not a finding: a library's own usage record (decided edge)
  Severity: Act on
  Verify: re-open the mapping against the record's fields
- [ ] AE9 — Find where each call's output-token cap is set. A literal in the adapter, or a call with no cap, is a
  finding.
  Applies when: code builds a model request
  Evidence: the cap's source at `file:line`
  Not a finding: a default in agent configuration (decided edge)
  Severity: Consider
  Verify: re-open the request builder and the configuration it reads
- [ ] AE10 — Find each fallback to another model. Fallback inside an adapter, no explicit model mapping, or cost priced
  on the primary model is a finding.
  Applies when: a second model can answer a failed call
  Evidence: the fallback and the pricing call at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the decorator and the cost calculation
