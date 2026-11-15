# Concurrency

Read this when the change starts threads, submits async work, calls a remote service, retries, locks, builds a pool
or a cache, or handles a request or message that creates work. The general rules are in [SKILL.md](SKILL.md).

## Threads and async work

- Run blocking I/O fan-out on `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task. Never put
  virtual threads in a pool, because a pool caps concurrency at its size and blocked tasks queue behind it. On Java
  24 or later a `synchronized` block around a blocking call no longer pins the carrier; a blocking call inside a class
  initialiser still does.
- Give `supplyAsync` and `runAsync` a dedicated, named executor for blocking work, because the one-argument form runs
  on the common pool and blocking I/O starves it.
- Never call `join()`, `get()` or `block()` mid-flow on an event-loop or common-pool thread. Compose with
  `thenApply`, `thenCompose` and `allOf`, or run the flow on a virtual thread, because a blocked event-loop thread
  stalls every request it serves. A blocking call at the outer boundary of the flow, or inside a virtual-thread task,
  is fine.
- Pass request context (tenant, principal, depth) as a parameter or a `ScopedValue`, never a new `ThreadLocal`,
  because a `ThreadLocal` outlives the request on a reused thread and leaks into the next one. Across a
  `CompletableFuture` or executor hop, pass it as a parameter: a `ScopedValue` reaches another thread only through
  `StructuredTaskScope`, which is a preview API.

## Timeouts

- Give every remote client (HTTP, gRPC, JDBC, Redis) a connect and a read timeout, or a deadline, that ends the call
  itself. `orTimeout` only ends the caller's wait; the call keeps its thread and connection. `orTimeout` beside a
  client timeout is fine.
- Set each timeout from the call's measured p99 latency with headroom, and name that source where the value is set,
  because a guessed value cuts healthy calls or holds threads for calls that will fail. Give a call the caller can do
  without a short timeout and a fallback.
- Pass the caller's remaining deadline to each downstream call, and make no call once it has passed, because work for
  a caller who gave up wastes the capacity that recovery needs. The remaining deadline wins when it is shorter than
  the p99 timeout. A service that receives a request with no deadline starts the deadline with its own timeout.

**Bad**: the future completes after two seconds, but the blocking `send` inside `fetchRates` has no timeout and keeps
its thread on the socket.
```java
final var client = HttpClient.newHttpClient();
final var request = HttpRequest.newBuilder(ratesUri).GET().build();
return CompletableFuture
        .supplyAsync(() -> fetchRates(client, request), ioExecutor)
        .orTimeout(2, TimeUnit.SECONDS);
```
**Good**: the connect and request timeouts end the exchange, so a stuck provider frees the thread.
```java
// both timeouts come from the rates call's p99 with headroom
final var client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(1))
        .build();
final var request = HttpRequest.newBuilder(ratesUri)
        .timeout(Duration.ofSeconds(2))
        .GET()
        .build();
return client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
```

## Retries

- Retry only a transient failure of an idempotent call, with bounded attempts and jittered backoff, and only after a
  timeout exists, because retrying a non-idempotent call repeats its side effect. A non-idempotent command may be
  resent when it carries the initiator's idempotency key.
- Retry at one layer only, the one that sees the whole operation. The layers below fail fast and report the cause,
  because attempts multiply: three layers of three attempts send 27 requests. Check the callee and each caller of a
  retry you add, including a client whose own retries are on.
- Draw every retry from one client-wide retry budget of about 10% of requests, beside the per-call cap, and stop
  retrying while it is spent, because in an outage every call fails and per-call caps still multiply the load.
- Never retry a 4xx response unless it carries `Retry-After`, and then wait at least that long, because other 4xx
  responses fail the same way again.
- Put a circuit breaker on a retried remote dependency whose failures repeat, beside the timeout and the retry,
  because retrying a dependency that is down wastes threads and amplifies the outage.

## Side effects and idempotency

- Treat a side-effecting remote call that times out after it connected as unknown, not failed, because the effect may
  have applied. Only a failed connect is a failure. Resend an unknown call only with the key the initiator minted
  once; a key minted per attempt makes each resend a new effect.
- Require an idempotency key on every request or message that creates or triggers work, and reject one without it
  (400 over HTTP), because a repeated request otherwise repeats the work. A natural key that the handler claims
  atomically with its change is the idempotency key; new work with no natural key, such as a new charge, needs one.
- Claim each key atomically with a fingerprint of the request, and store the response. Replay the stored response on
  a repeat, answer 409 while the first request runs and 422 for the same key with another payload, because a bare
  "seen it" check repeats the effect or loses the result.

**Bad**: the charge mints its own key and counts a read timeout as failure. The provider may have taken the money,
so the caller's resend, under a new key, charges again.
```java
final var request = chargeRequest(order, UUID.randomUUID().toString());
try {
    return ChargeResult.fromStatus(http.send(request, discarding()).statusCode());
} catch (final HttpTimeoutException timedOut) {
    return ChargeResult.FAILED;
}
```
**Good**: the order mints the key once, inside `ChargeIntent`, and every resend reuses it. Anything after connect is
`Unknown`, for a reconciler to resolve.
```java
intents.recordPending(intent.idempotencyKey(), intent.orderId());
try {
    final HttpResponse<Void> response = http.send(chargeRequest(intent), discarding());
    return ChargeOutcome.fromStatus(intent.idempotencyKey(), response.statusCode());
} catch (final HttpConnectTimeoutException notSent) {
    return new ChargeOutcome.Failed(intent.idempotencyKey(), notSent.getClass().getSimpleName());
} catch (final IOException afterConnect) {
    return new ChargeOutcome.Unknown(intent.idempotencyKey(), afterConnect.getClass().getSimpleName());
} catch (final InterruptedException _) {
    Thread.currentThread().interrupt();
    return new ChargeOutcome.Unknown(intent.idempotencyKey(), "interrupted");
}
```

## Concurrent writes

- Give each concurrent writer its own key or file, merged where it is read, because shared writes race. When one
  shared target is real, acquire its locks in one documented global order, because opposite orders deadlock.
- Send a versioned resource's `@Version` as its `ETag`, and change it only under a matching `If-Match`: 412 on a
  mismatch, 428 when the header is missing, because without a precondition the last write silently wins.
- Map `OptimisticLockingFailureException` to 409 Conflict in the global handler, never 500, because the client lost a
  race and must reload, and a 500 reports a server fault.

## Pools and caches

- Give a thread pool a bounded queue and a stated rejection policy, because an unbounded queue never rejects; it grows
  memory until the process fails. `Executors.newFixedThreadPool` and `newScheduledThreadPool` look bounded but queue
  without limit: build a `ThreadPoolExecutor` with an `ArrayBlockingQueue` instead. `CallerRunsPolicy` slows the
  producer instead of growing memory.
- Give every in-process cache a maximum size or weight and an eviction policy, and every connection pool a maximum
  size and an acquire timeout, because an unbounded cache leaks memory and an untimed pool queues callers forever.
