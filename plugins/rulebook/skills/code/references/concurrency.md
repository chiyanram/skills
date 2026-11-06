# Concurrency

How Java code runs work on other threads, calls remote services, retries, shares state and bounds its pools and
caches. Read it when you write or review code that starts threads, submits async work, calls a remote service, retries,
locks, or builds a pool or a cache.

Contents: Rules · When X, use Y · Good / Bad (CC3, CC9, CC12) · Decided edges · Review checks

## Rules

- **CC1** — Run blocking I/O fan-out on `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task,
  never a pool of virtual threads, because a pool caps concurrency at its size and blocked tasks then queue behind it.
- **CC2** — Submit blocking async work to an explicit, named executor, never no-arg `supplyAsync`/`runAsync`, because
  no-arg `supplyAsync` puts blocking I/O on the common pool and starves it.
- **CC3** — Give every remote call a client connect and read timeout (or deadline) that ends the call; `orTimeout`
  alone only stops the wait, because a call with no stopping timeout holds its thread and connection forever.
- **CC14** — Pass the caller's remaining deadline to each downstream call and stop once it has passed, never a fixed
  longer timeout, because work for a caller who gave up wastes the capacity recovery needs.
- **CC9** — Treat a side-effecting remote call that times out after connecting as unknown, not failed; resend it only
  with the initiator's idempotency key, because the effect may have applied and a new key duplicates it.
- **CC19** — Require an idempotency key header on every POST that creates or triggers work, and answer 400 when it is
  missing, because a client's retry of a keyless POST creates the work twice.
- **CC15** — Claim each idempotency key atomically with its request fingerprint, store the response; replay it on a
  repeat, answer 409 while the first runs and 422 for another payload, because otherwise a retry repeats the effect.
- **CC17** — Send a versioned resource's `@Version` as its `ETag` and change it only under a matching `If-Match`;
  answer 412 on a mismatch and 428 when it is missing, because otherwise the last write silently wins.
- **CC18** — Map an optimistic-lock failure (`OptimisticLockingFailureException`) to 409 Conflict in the global
  handler, never 500, because the client lost a race and must reload, and a 500 reports it as a server fault.
- **CC8** — Retry only a transient failure of an idempotent call, with bounded attempts and jittered backoff, and only
  after a timeout exists (CC3), because retrying a non-idempotent call repeats its side effect.
- **CC12** — Retry a failure at one layer only; the layers below fail fast and report the cause, because attempts
  multiply across layers: three layers of three attempts send 27 requests.
- **CC16** — Retry a 4xx response only when it carries `Retry-After`, and wait at least that long, because other 4xx
  responses fail the same way again and an early retry ignores the server's request to wait.
- **CC11** — Put a circuit breaker on a remote dependency whose failures repeat, beside the timeout and retry, because
  retrying a dependency that is down wastes threads and amplifies the outage.
- **CC4** — Give a bounded pool a bounded queue and a stated rejection behaviour, because an unbounded queue never
  rejects; it grows memory until the process fails.
- **CC5** — Give each concurrent writer its own key or file, merged where read; when one shared target is real,
  acquire its locks in one documented global order, because shared writes race and opposite lock orders deadlock.
- **CC6** — Never block with `join()`, `get()` or `block()` on an event-loop or common-pool thread; compose with
  `thenApply`/`thenCompose`/`allOf`, or run the flow on a virtual thread, because a blocked event-loop thread stalls
  every request it serves.
- **CC7** — Pass request-scoped context (tenant, principal, depth) as a parameter or a `ScopedValue`, never a new
  `ThreadLocal`, because a `ThreadLocal` outlives the request on a reused thread unless removed, leaking context into
  the next request.
- **CC10** — Give every in-process cache a maximum size or weight and an eviction policy, and every connection pool a
  maximum size and acquire timeout, because unbounded caches leak memory and untimed pools queue callers forever.

## When X, use Y

| the code has | use | why |
|---|---|---|
| many blocking I/O calls to run at once | `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task, never a pool of them (CC1) | a pool caps concurrency at its size, and blocked tasks queue behind it |
| blocking work to run async | `supplyAsync(task, executor)` with a dedicated executor (CC2) | without an executor the task runs on the common pool, and blocking I/O starves it |
| a client for a remote service | a connect and a read timeout, or a deadline, on the client itself (CC3) | a call with no stopping timeout holds its thread and connection forever |
| an `orTimeout` on a remote call | a client timeout beside it; `orTimeout` is only the caller's wait (CC3) | completing the future does not stop the running call |
| a downstream call made while serving a request that has a deadline | a timeout of the deadline's remaining time, and no call once it has passed (CC14) | a fixed longer timeout keeps working for a caller who has gone |
| a side-effecting remote call that timed out after connecting | the outcome unknown, not failed (CC9) | the effect may have applied |
| an idempotency key | one key minted by the initiator and reused on every resend (CC9) | a key minted per attempt makes each resend a new effect |
| a POST that creates or triggers work | a required idempotency key header, and 400 when it is missing (CC19) | a retry of a keyless POST creates the work twice |
| an update of a versioned resource over HTTP | its `@Version` as the `ETag`, and a matching `If-Match` required: 412 on a mismatch, 428 when missing (CC17) | without a precondition the last write silently wins |
| an `OptimisticLockingFailureException` | a 409 Conflict from the global handler (CC18) | the client lost a race and must reload; a 500 reports a server fault |
| an endpoint that accepts an idempotency key | an atomic claim of the key with a request fingerprint, the stored response replayed on a repeat, 409 while the first runs, 422 for another payload (CC15) | a bare "seen it" check repeats the effect or loses the result |
| a failed remote call to retry | the timeout first, then bounded attempts with jitter, for transient failures of idempotent calls only (CC8) | retrying a non-idempotent call repeats its side effect |
| a call chain in which more than one layer could retry | one retry, at the layer that sees the whole operation; the layers below fail fast (CC12) | attempts multiply across layers |
| a 4xx response | no retry, unless it carries `Retry-After`; then a wait of at least that long (CC16) | other 4xx responses fail the same way again |
| a remote dependency whose failures repeat | a circuit breaker beside the timeout and retry (CC11) | retrying a dependency that is down wastes threads and amplifies the outage |
| a bounded thread pool | a bounded queue and a stated rejection policy (CC4) | an unbounded queue never rejects; it grows memory until the process fails |
| `Executors.newFixedThreadPool` | a `ThreadPoolExecutor` with a bounded queue (CC4) | `newFixedThreadPool` queues on an unbounded `LinkedBlockingQueue` |
| two actors that write the same state | each actor its own key or file, merged where it is read (CC5) | shared writes race |
| two locks held at once | one documented global acquisition order (CC5) | opposite lock orders deadlock |
| a `CompletableFuture` flow on an event-loop or common-pool thread | `thenApply`/`thenCompose`/`allOf`; block only at the outer boundary (CC6) | a blocked event-loop thread stalls every request it serves |
| context that a request's code reads | a parameter or a `ScopedValue` (CC7) | a `ThreadLocal` outlives the request on a reused thread and leaks into the next one |
| an in-process cache | a maximum size or weight and an eviction policy (CC10) | an unbounded cache leaks memory |
| a connection pool | a maximum size and an acquire timeout (CC10) | an untimed pool queues callers forever |

## Good / Bad

Every rule's approved pair: [examples/concurrency.md](examples/concurrency.md).

### CC3 — A timeout that stops the work, not only the wait

**Bad**
```java
final var client = HttpClient.newHttpClient();
final var request = HttpRequest.newBuilder(ratesUri).GET().build();
return CompletableFuture
        .supplyAsync(() -> fetchRates(client, request), ioExecutor)
        .orTimeout(2, TimeUnit.SECONDS);
```
After two seconds `orTimeout` completes the future. The blocking `send` inside `fetchRates` has no timeout, so it
keeps its thread on the socket.

**Good**
```java
final var client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(1))
        .build();
final var request = HttpRequest.newBuilder(ratesUri)
        .timeout(Duration.ofSeconds(2))
        .GET()
        .build();
return client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
```
The connect timeout and the request timeout end the exchange itself, so a stuck provider frees the thread.

### CC9 — A timeout after connect is unknown; a resend reuses the initiator's key

**Bad**
```java
final var request = chargeRequest(order, UUID.randomUUID().toString());
try {
    return ChargeResult.fromStatus(http.send(request, discarding()).statusCode());
} catch (final HttpTimeoutException timedOut) {
    return ChargeResult.FAILED;
}
```
The charge mints its own key, and a read timeout counts as a failure. The provider may have taken the money, so the
caller's resend, under a new key, charges again.

**Good**
```java
public ChargeOutcome charge(final ChargeIntent intent) {
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
}
```
The order mints the key once, inside `ChargeIntent`, and every resend reuses it. A failed connect is `Failed`;
anything after connect is `Unknown`, for a reconciler to resolve.

### CC12 — One layer retries; the layers below fail fast

**Bad**
```java
// RatesClient
Rates fetch(final Currency base) {
    return Decorators.ofSupplier(() -> http.getRates(base))
            .withCircuitBreaker(ratesBreaker)
            .withRetry(ratesRetry)
            .get();
}

// QuoteService
Quote quote(final Order order) {
    return Decorators.ofSupplier(() -> pricing.price(order, ratesClient.fetch(order.currency())))
            .withRetry(quoteRetry)
            .get();
}
```
Both layers make three attempts, so one failing quote sends nine requests to the rates provider.

**Good**
```java
// RatesClient: client timeouts (CC3) and a breaker (CC11), no retry
Rates fetch(final Currency base) {
    return ratesBreaker.executeSupplier(() -> http.getRates(base));
}

// QuoteService: the one retry (CC8)
Quote quote(final Order order) {
    return quoteRetry.executeSupplier(() -> pricing.price(order, ratesClient.fetch(order.currency())));
}
```
The client fails fast, and an open breaker fails it at once. The service retries the whole quote, so one failure
costs at most three requests.

## Decided edges

- **Skip when** a `synchronized` block holds a blocking call on a virtual thread on Java 24 or later: that pinning is
  gone (CC1). — **Do not skip when** the blocking call runs inside a class initialiser: that still pins its carrier
  (CC1). — **Confidence** medium
- **Skip when** `orTimeout` sits beside a client timeout that stops the work: it is the caller's wait (CC3; the CC3
  Good above). — **Do not skip when** `orTimeout` is the only timeout on the call. — **Confidence** high
- **Skip when** a non-idempotent command is resent with its initiator's idempotency key: the resource recognises the
  retry (CC8, CC9). — **Do not skip when** the key is minted per attempt: it comes from the retrying layer. —
  **Confidence** high
- **Skip when** the service is the first to receive the request and no deadline came with it: its own timeout starts
  the deadline (CC14, CC3). — **Do not skip when** the inbound request carries a deadline or a timeout header: each
  downstream call gets what is left of it. — **Confidence** high
- **Skip when** the `join()` or `get()` sits at the outer boundary of the flow, or runs on a virtual thread (CC6). —
  **Do not skip when** it blocks mid-flow on an event-loop or common-pool thread. — **Confidence** high
- **Skip when** request context crosses a `CompletableFuture` or executor hop as a parameter, not a `ScopedValue`: a
  `ScopedValue` reaches no other thread without `--enable-preview`, because `StructuredTaskScope` is a preview API
  (CC7). — **Do not skip when** it crosses in a `ThreadLocal`, copied by hand or not. — **Confidence** high

## Review checks

Walk every changed Java file that starts threads, submits async work, calls a remote service, retries, locks, or builds
a pool or a cache.

- [ ] CC1 — Blocking I/O fanned out on a platform-thread pool is a finding. For each virtual-thread factory
  (`grep -nE "ofVirtual\(\)"`), a factory passed to a `ThreadPoolExecutor` or a `new…ThreadPool(` is a finding.
- [ ] CC2 — For each `supplyAsync` or `runAsync` (`grep -nE "(supply|run)Async\("`), find an executor argument. A
  one-argument call that does blocking work is a finding.
- [ ] CC3 — For each remote call (`RestClient`, `HttpClient`, `WebClient`, a gRPC stub, a JDBC or Redis client), find
  a connect and a read timeout, or a deadline, on the client. A call whose only timeout is `orTimeout` is a finding.
- [ ] CC14 — `grep -rnE "timeout\(Duration\.of|withDeadlineAfter|Timeout\(Duration\.of"`, and for each downstream
  call made while serving a request, find where its timeout comes from. A fixed timeout, when the inbound request
  carries a deadline, is a finding; gRPC Java propagates the deadline itself.
- [ ] CC9 — For each side-effecting remote call, find an outcome that keeps a timeout after connect apart from
  failure. A timeout after connect handled as failure, or a resend whose idempotency key is minted inside the retry, is
  a finding.
- [ ] CC19 — For each `@PostMapping` that creates or starts work (`grep -rn "@PostMapping"`), find a required
  idempotency key header and a 400 when it is missing. Either one missing is a finding.
- [ ] CC17 — For each PUT, PATCH or DELETE of an entity with `@Version` (`grep -rln "@Version" src/main`), find the
  `ETag` on its GET and an `If-Match` check before the change. Either one missing, or a status other than 412 for a
  mismatch or 428 for a missing header, is a finding.
- [ ] CC18 — `grep -rnE "OptimisticLock(ing)?(Failure)?Exception"` in the global handler. No mapping, or a mapping
  to a status other than 409, is a finding.
- [ ] CC15 — For each endpoint that reads an idempotency key (`grep -rn -i "idempotency"`), find an atomic claim of
  the key with a request fingerprint, a stored response replayed on a repeat, a 409 while the first runs and a 422
  for another payload. Any one missing is a finding.
- [ ] CC8 — For each retry loop or retry policy, find bounded attempts, jittered backoff, a transient-only filter, an
  idempotent call (or an initiator's key) and a timeout. Any one missing is a finding.
- [ ] CC12 — `grep -rnE "@Retryable|RetryTemplate|Retry\.of|retryWhen|withRetry|executeSupplier|retryOnResult"`. For
  each retry the change adds, follow the call it wraps and each caller of the method. A callee or caller that also
  retries (one of those hits, or a client whose own retries are on) is a finding.
- [ ] CC16 — `grep -rnE "Retry-After|retryOnResult|\b4[0-9]{2}\b"` beside each retry policy. A 4xx retried without
  `Retry-After`, or a retry sooner than the `Retry-After` delay, is a finding.
- [ ] CC11 — For each remote dependency the change retries
  (`grep -nE "@Retryable|RetryTemplate|Retry\.of|retryWhen"`), find a circuit breaker around it. A retried dependency
  with no circuit breaker is a finding.
- [ ] CC4 — For each pool built (`grep -nE "new ThreadPoolExecutor|Executors\.new(Fixed|Scheduled)ThreadPool"`), find
  a bounded queue and a stated rejection behaviour. `newFixedThreadPool` and `newScheduledThreadPool`, whose queues are
  unbounded, are findings.
- [ ] CC5 — For each new lock, `synchronized` block or shared mutable field, ask whether each writer could own its own
  key or file. Shared state that could be separated is a finding, and so are two locks held at once with no
  documented order.
- [ ] CC6 — Each `.join()`, `.get()` or `.block()` (`grep -nE "\.(join|get|block)\(\)"`) on an event-loop or
  common-pool thread that is not at the outer boundary is a finding. A hit inside a virtual-thread task is not.
- [ ] CC7 — Each new `ThreadLocal` (`grep -n "ThreadLocal"`) is a finding.
- [ ] CC10 — For each in-process cache, find a maximum size or weight and an eviction policy; for each connection
  pool, a maximum size and an acquire timeout. Any one missing is a finding.
