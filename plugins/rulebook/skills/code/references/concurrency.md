# Concurrency

How Java code runs work on other threads, calls remote services, retries, shares state and bounds its pools and
caches. Read it when you write or review code that starts threads, submits async work, calls a remote service, retries,
locks, or builds a pool or a cache.

Contents: Rules · When X, use Y · Good / Bad (CC3, CC4, CC9) · Decided edges · Review checks

## Rules

- **CC1** — Use virtual threads for blocking I/O fan-out, never pooled;
  `synchronized` is fine on Java 25; avoid blocking in a class initialiser or a callback from native or FFM code,
  because those still pin the carrier.
- **CC2** — Submit blocking async work to an explicit, named executor, never no-arg
  `supplyAsync`/`runAsync`, because no-arg `supplyAsync` puts blocking I/O on the common pool and starves it.
- **CC3** — Give every remote call a timeout that stops the work; `orTimeout` alone only abandons the future, because a
  call with no stopping timeout can hang forever and keep running.
- **CC9** — Treat a remote call as success, failure or unknown; record intent
  before it; the idempotency key comes from the initiator, never the retrying layer, because a timed-out effect may
  have applied; retries then duplicate it.
- **CC8** — Retry only a transient failure of an idempotent call, with bounded attempts and jittered backoff, and only
  after a timeout exists (CC3), because retrying a non-idempotent call repeats its side effect.
- **CC4** — Give a bounded pool a bounded queue and a stated rejection behaviour, because an unbounded queue never
  rejects; it grows memory until the process fails.
- **CC5** — Remove the shared write target (one key or file per actor) before
  locking; a lock still needed has one owner and one documented order, because shared writes race intermittently and
  opposite lock orders deadlock.
- **CC6** — Never call `join()`/`get()` mid-pipeline in request-serving code; compose
  with `thenApply`/`thenCompose`/`allOf`, because a mid-pipeline `join()` blocks a thread and undoes the reason for
  async.
- **CC7** — Carry request- or call-scoped context (depth, tenant, principal) in a `ScopedValue` or an explicit
  parameter, never a new `ThreadLocal`, because a `ThreadLocal` does not reach an async thread unless copied by hand.
- **CC10** — Bound each cache with an eviction policy and a memory ceiling, because an unbounded cache leaks memory
  until the process fails.

## When X, use Y

| the code has | use | why |
|---|---|---|
| many blocking I/O calls to run at once | `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task, never a pool of them (CC1) | avoid pooling virtual threads (pl125 :31) · there is never a need to pool them (JEP 444 §Do not pool virtual threads). The `synchronized` and pinning clauses are operator preference, read in JEP 491 (§Future Work, §Diagnosing remaining cases of pinning) |
| blocking work to run async | `supplyAsync(task, executor)` with a dedicated executor (CC2) | operator preference; avoid blocking I/O in the common pool; use a dedicated executor (pl125 :37) · the two-argument form (pl142 :854) |
| CPU-bound, short, side-effect-free work | ForkJoin or a parallel stream, outside request- or queue-serving code (CC2; JV2, `java.md`) | the common pool is reserved for that work (pl125 :37) |
| a client for a remote service | a connect and a read timeout on the client itself (CC3) | always bound remote calls with timeouts (pl125 :40) · cancel ongoing work on timeout (pl126 :34) · set a timeout on any remote call (AWS timeouts) |
| a remote call with a side effect | an intent record before the call, and three outcomes: success, failure, unknown (CC9) | operator preference; a timeout tells you nothing about whether the effect applied (addy api :213) |
| an idempotency key | one key per intent, minted by the initiator and reused on every retry (CC9) | never from the layer doing the retrying (addy api :163, :171) · the client generates the idempotency key (Stripe idempotent requests) |
| a failed remote call to retry | the timeout first, then bounded attempts with jitter, for transient failures of idempotent calls only (CC8) | bounded attempts and jitter (pl123cc :42-43) · retry only transient failures (pl123cc :95) · limit retries, add jitter, retry side effects only when idempotent (AWS timeouts) |
| a dependency that can exhaust shared threads, connections or queue capacity | a bulkhead: a bounded pool, a bounded queue and a rejection policy (CC4) | bounded queues and rejection policies (pl125 :35) · an unbounded work queue can grow without limit (JDK `ThreadPoolExecutor`) · a bounded queue and a fixed thread pool (Resilience4j bulkhead) |
| two actors that write the same state | each actor its own key or file, merged where it is read (CC5) | operator preference; eliminate the shared write target first (ps separate :15) |
| two locks held at once | one global acquisition order (CC5) | operator preference; establish global lock ordering (pl125 :36) |
| a `CompletableFuture` pipeline | `thenApply`/`thenCompose`/`allOf`; block only at the outer boundary (CC6) | operator preference; avoid premature `join()`/`get()` mid-flow (pl142 :839) |
| context that async tasks read | a `ScopedValue` (CC7) | `ScopedValue` over `ThreadLocal` across tasks (pl125 :33, :39) · scoped values may be a better alternative (JEP 444 §Thread-local variables; JEP 487 §Expensive inheritance) |
| a cache | an eviction policy and a memory ceiling (CC10) | eviction policy and memory ceiling set (addy perf :181) · size-based eviction with `maximumSize` (Caffeine Eviction §Size-based) |

Sources, all read at a pinned commit or at the URL named; `:N` is a line:

- pl125, pl126, pl142: jabrena/plinth `skills/<n>-<name>/references/<n>-<name>.md` for 125-java-concurrency,
  126-java-exception-handling and 142-java-functional-programming, @a46375a.
- pl123cc: jabrena/plinth `skills/123-java-design-patterns/references/123-cross-cutting-integration-patterns.md`,
  @a46375a.
- addy api, addy perf: addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md` and
  `references/performance-checklist.md`, @aeac41d.
- ps separate: pstack `skills/principle-separate-before-serializing-shared-state/SKILL.md`, @f713f14.
- JEP 444, JEP 487, JEP 491: OpenJDK, https://openjdk.org/jeps/444, /487 and /491 (§Future Work, §Diagnosing remaining
  cases of pinning).
- AWS timeouts: Amazon Builders' Library, "Timeouts, retries, and backoff with jitter",
  https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/.
- JDK `ThreadPoolExecutor`: Java SE 25 Javadoc, `java.util.concurrent.ThreadPoolExecutor` §Queuing, §Rejected tasks.
- Resilience4j bulkhead: https://resilience4j.readme.io/docs/bulkhead.
- Stripe idempotent requests: https://docs.stripe.com/api/idempotent_requests.
- Caffeine Eviction: https://github.com/ben-manes/caffeine/wiki/Eviction §Size-based.

Operator preference, 2026-10-31 (SRC2), in whole or in part: CC1, CC2, CC9, CC5 and CC6.

## Good / Bad

### CC3 — A timeout that stops the work, not only the wait

**Bad** (neutral)
```java
final var client = HttpClient.newHttpClient();
final var request = HttpRequest.newBuilder(ratesUri).GET().build();
return CompletableFuture
        .supplyAsync(() -> fetchRates(client, request), ioExecutor)
        .orTimeout(2, TimeUnit.SECONDS);
```
After two seconds `orTimeout` completes the future. The blocking `send` inside `fetchRates` has no timeout, so it
keeps its thread on the socket.

**Good** (neutral)
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

### CC4 — A bounded pool has a bounded queue and a stated rejection

**Bad** (from jabrena/plinth `skills/125-java-concurrency/references/125-java-concurrency.md`:1596)
```java
final class ReceiptDispatcher {
    private final ExecutorService pool = Executors.newFixedThreadPool(8);

    void dispatch(final Runnable sendReceipt) {
        pool.submit(sendReceipt);
    }
}
```
Eight threads look bounded, but `newFixedThreadPool` queues on an unbounded `LinkedBlockingQueue`. A burst of
receipts is never rejected, and the heap grows.

**Good** (from jabrena/plinth `skills/125-java-concurrency/references/125-java-concurrency.md`:1562)
```java
final class ReceiptDispatcher {
    private final ThreadPoolExecutor pool = new ThreadPoolExecutor(
            4,
            8,
            60,
            TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(200),
            new ThreadPoolExecutor.CallerRunsPolicy());

    void dispatch(final Runnable sendReceipt) {
        pool.execute(sendReceipt);
    }
}
```
The queue holds 200 tasks. When it is full, the caller's thread runs the task, which slows the producer instead of
growing memory.

### CC9 — Success, failure or unknown; intent before the call; the initiator's key

**Bad** (from addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`:163)
```java
for (int attempt = 1; attempt <= 3; attempt++) {
    final var request = chargeRequest(order, UUID.randomUUID().toString());
    try {
        return ChargeResult.fromStatus(http.send(request, discarding()).statusCode());
    } catch (final HttpTimeoutException timedOut) {
        log.warn("Charge attempt {} failed: {}: {}",
                attempt,
                timedOut.getClass().getSimpleName(),
                timedOut.getMessage());
    }
}
return ChargeResult.FAILED;
```
Each attempt mints a new key, and a read timeout counts as a failure. The provider may have taken the money, so the
next attempt charges again.

**Good** (from addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`:167, :213)
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
    } catch (final InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        return new ChargeOutcome.Unknown(intent.idempotencyKey(), "interrupted");
    }
}
```
The order mints the key once, inside `ChargeIntent`, and every retry reuses it. The intent is recorded before the
call. A failed connect is `Failed`; anything after connect is `Unknown`, for a reconciler to resolve.

## Decided edges

- **Skip when** a `synchronized` block holds a blocking call on Java 24 or later: JEP 491 removed that pinning, and
  pl125 :38, which says otherwise, is stale (CC1). — **Do not skip when** the blocking call runs inside a class
  initialiser, or in Java code that native or FFM code calls back: that still pins (CC1; JEP 491). — **Confidence**
  high
- **Skip when** `orTimeout` sits beside a client timeout that stops the work: it is the caller's wait (CC3; the CC3 Good
  above). — **Do not skip when** `orTimeout` is the only timeout on the call. — **Confidence** high
- **Skip when** a non-idempotent command carries an idempotency key from its initiator: it may be retried (CC8; pl123cc
  :95). — **Do not skip when** the key is minted per attempt: every retry is then a new effect (addy api :163). —
  **Confidence** high
- **Skip when** one shared write target is a real invariant: serialize access structurally, with a lock, a
  single-writer actor or a compare-and-swap (CC5; ps separate :16). — **Do not skip when** the actors publish
  independent facts: give each its own target (ps separate :15). — **Confidence** high
- **Skip when** the `join()` sits at the outer boundary of the flow, such as a batch entry point (CC6; pl142 :839). —
  **Do not skip when** it sits mid-pipeline in request-serving code. — **Confidence** high

## Review checks

Walk every changed Java file that starts threads, submits async work, calls a remote service, retries, locks, or builds
a pool or a cache.

- [ ] CC1 — Blocking I/O fanned out on a platform-thread pool is a finding. A pool whose thread factory makes virtual
  threads (`grep -n "ofVirtual"`) is a finding. A blocking call inside a `static {}` block, a static field
  initialiser, or a Java callback from native or FFM code is flagged: CC1 says avoid, not never.
- [ ] CC2 — For each `supplyAsync` or `runAsync` (`grep -nE "(supply|run)Async\("`), find an executor argument. A
  one-argument call that does blocking work is a finding.
- [ ] CC3 — For each remote call (`RestClient`, `HttpClient`, `WebClient`, a JDBC or Redis client), find a timeout
  that stops the work, such as a connect and a read timeout on the client. A call whose only timeout is `orTimeout` is
  a finding.
- [ ] CC9 — For each remote call with a side effect, find the intent record before the call and an outcome that keeps
  unknown apart from failure. A timeout after connect handled as failure, or a key minted inside the retry, is a
  finding.
- [ ] CC8 — For each retry loop or retry policy, find bounded attempts, jittered backoff, a transient-only filter, an
  idempotent call (or an initiator's key) and a timeout. Any one missing is a finding.
- [ ] CC4 — For each bounded pool built (`grep -nE "new ThreadPoolExecutor|Executors\.newFixedThreadPool"`), find a
  bounded queue and a stated rejection behaviour. `newFixedThreadPool`, whose queue is unbounded, is a finding.
- [ ] CC5 — For each new lock, `synchronized` block or shared mutable field, ask whether each actor could own its
  own target. Shared state that could be separated is a finding. A lock with more than one owning class, or two locks
  held at once with no documented order, is a finding.
- [ ] CC6 — Each `.join()` or `.get()` on a future in request-serving code (`grep -nE "\.(join|get)\(\)"`) that is not
  at the outer boundary is a finding.
- [ ] CC7 — Each new `ThreadLocal` (`grep -n "ThreadLocal"`) is a finding.
- [ ] CC10 — For each cache, find an eviction policy and a maximum size. Either one missing is a finding.
