# Model adapter

How the adapter behind your model port turns one provider's replies, errors, streams and usage into your own types,
and how fallback to another model wraps it. Read it when you write or review a model adapter, a stop reason, a model
error or retry policy, a streamed reply, a tool call's arguments, a usage record, an output-token cap or a fallback
model.

## Rules

- Map each provider's stop reason onto one closed set (end, truncated, tool call, refused, context exceeded, paused,
  error), with an unknown value mapped to error, and switch on it exhaustively, because an unmapped refusal or
  truncation reads as success. When an agent library already gives you a closed stop reason and one usage record,
  this applies to the mapping into your types.
- Run tool calls only from a reply whose stop reason is tool call. A truncated or refused reply ends the turn with
  that typed outcome, because truncated arguments often parse as a valid partial object.
- Parse a tool call's complete arguments with a JSON library and validate them against the tool's schema. Send a
  malformed call back to the model as an error, because an empty-argument fallback runs the tool wrongly. The check
  before a sink is in `code`'s `security` notes, Outside input.
- Have each adapter return one normalised error (status, retry-after, request id, timeout or network, response
  started), and let one retry policy above it decide, because retries inside adapters multiply attempts.
- Retry a streamed call only while no chunk has reached a user, a socket or a store; after that, end it as a typed
  failure, because a retry replays text the user already saw.
- Treat a 429 or an explicit retry-after as back-pressure for the retry policy and the rate limiter. Count an
  overload toward the circuit breaker only once retries give up, because throttling otherwise trips a healthy
  breaker. A 429 that says a quota or spend cap is used up, with no retry-after, is not retried and not a breaker
  failure: stop the run with a typed reason.
- Treat an error event inside a stream as that request's failure, even after a 200, and skip keep-alive and unknown
  event types, because providers fail mid-stream and add event types.
- Fold each provider's usage into one record (input including cache, cache read, cache write, output, reasoning) from
  the final cumulative value, because providers split and repeat these counts differently.
- Set every call's output-token cap from agent or model configuration, sized as a backstop, because a hidden low cap
  in the adapter truncates answers and wastes retries. A default in agent configuration that a model entry
  overrides is configuration.
- Fall back to another model through a decorator over the model port, with an explicit model mapping, and price usage
  on the model that served it, because the primary's model name is wrong on another provider. Its test is in the
  `testing` skill's model-calls notes.

## Good / Bad

### Tool calls run only on a tool-call stop

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

### No retry after the first chunk reached the user

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
The adapter's normalised error says whether the response started. After the first chunk, the call ends as a
typed failure.

### A rate limit is back-pressure; an overload counts once retries give up

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

### Fallback is a decorator with a model mapping

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

## Review

Walk every changed model adapter, model port decorator, retry policy, stream handler and usage record.

Each line is a finding, a blocker unless marked (warning).

- A raw stop-reason string compared outside the adapter, or a switch over the closed set with a `default`.
- A path that runs tool calls without first requiring the tool-call stop reason.
- Hand-built argument parsing, an empty-object fallback, or no schema check before the tool runs.
- A retry inside an adapter, or an adapter error that lacks status, retry-after, request id, timeout-or-network or
  response-started.
- A retry of a streamed call that does not check that no chunk was forwarded.
- A breaker that counts a 429 or a retry-after response, or counts an overload before the retry policy gives up.
- A stream error event that does not fail the request, or a keep-alive or unknown event that throws or ends the stream.
- Usage summed across stream events, or a cache or reasoning count dropped or counted twice.
- (warning) An output-token cap that is a literal in the adapter, or a call with no cap.
- Fallback inside an adapter, no explicit model mapping, or cost priced on the primary model.
