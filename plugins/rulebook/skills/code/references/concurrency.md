# Concurrency

How Java code runs work on other threads, calls remote services, retries, shares state and bounds its pools and
caches. Read it when you write or review code that starts threads, submits async work, calls a remote service, retries,
locks, or builds a pool or a cache.

Contents: Rules · When X, use Y · Good / Bad (CC3, CC4, CC9) · Decided edges · Review checks

## Rules

- **CC1** — Run blocking I/O fan-out on `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task,
  never a pool of virtual threads, because a pool caps concurrency at its size and blocked tasks then queue behind it.
- **CC2** — Submit blocking async work to an explicit, named executor, never no-arg `supplyAsync`/`runAsync`, because
  no-arg `supplyAsync` puts blocking I/O on the common pool and starves it.
- **CC3** — Give every remote call a client connect and read timeout (or deadline) that ends the call; `orTimeout`
  alone only stops the wait, because a call with no stopping timeout holds its thread and connection forever.
- **CC9** — Treat a side-effecting remote call that times out after connecting as unknown, not failed; resend it only
  with the initiator's idempotency key, because the effect may have applied and a new key duplicates it.
- **CC8** — Retry only a transient failure of an idempotent call, with bounded attempts and jittered backoff, and only
  after a timeout exists (CC3), because retrying a non-idempotent call repeats its side effect.
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
| many blocking I/O calls to run at once | `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task, never a pool of them (CC1) | "Avoid pooling virtual threads" (pl125 #8, r48 :1116) · virtual threads suit "tasks that spend most of the time blocked" (jdk-thread :108-110, r48 :1117) |
| blocking work to run async | `supplyAsync(task, executor)` with a dedicated executor (CC2) | async methods without an explicit executor run on the common pool (jdk-cf :72-74, r48 :1128) · for blocking I/O "use … a dedicated executor" (pl125 #12, r48 :1130) |
| a client for a remote service | a connect and a read timeout, or a deadline, on the client itself (CC3) | "always explicitly set a realistic deadline" (grpc-dl :24-26, r48 :1137) · "Set timeouts on every outbound call" (ms-tf :96, r48 :1138) |
| an `orTimeout` on a remote call | a client timeout beside it; `orTimeout` is only the caller's wait (CC3) | `cancel` does not interrupt the running work (jdk-cf :2545-2547, r48 :1140) |
| a side-effecting remote call that timed out after connecting | the outcome unknown, not failed (CC9) | "A timeout tells you nothing about whether the effect applied" (addy-api :215, r48 :1146) · after a timeout "the client is left uncertain about the status of the resource" (ietf-idem :53, r48 :1148) |
| an idempotency key | one key minted by the initiator and reused on every resend (CC9) | "never from the layer doing the retrying" (addy-api :171, r48 :1147) · the client generates it to "recognize subsequent retries of the same request" (ietf-idem :64, r48 :1149) |
| a failed remote call to retry | the timeout first, then bounded attempts with jitter, for transient failures of idempotent calls only (CC8) | "Retry tasks only when the faults are transient" and back off "with jitter"; non-idempotent retries cause inconsistencies (ms-tf :58, :82, :187, r48 :1157-1159) · "explicit timeouts before retries" (pl123cc :42, r48 :1139) · bounded attempts and jitter (pl123cc :42-43, r48 :1163) |
| a remote dependency whose failures repeat | a circuit breaker beside the timeout and retry (CC11) | stop "repeatedly trying to run an operation that's likely to fail" (ms-cb :29, r48 :1225) · "circuit breaker when repeated failures would waste resources" (pl123cc :22, :92-94, r48 :1227) |
| a bounded thread pool | a bounded queue and a stated rejection policy (CC4) | an unbounded queue admits "unbounded work queue growth" (jdk-tpe :170-180, r48 :1170) · an unbounded queue "can lead to `OutOfMemoryError`" (sf-sched :697-699, r48 :1172) · "bounded queues, appropriate rejection policies" (pl125 #10, r48 :1173) |
| `Executors.newFixedThreadPool` | a `ThreadPoolExecutor` with a bounded queue (CC4) | `newFixedThreadPool` builds an unbounded `LinkedBlockingQueue` (jdk-ex :88-91, r48 :1171) |
| two actors that write the same state | each actor its own key or file, merged where it is read (CC5) | "Give each actor its own owned file, key, branch" (ps-separate :15-16, r48 :1181) · "share memory by communicating" (go :2725-2726, r48 :1182) |
| two locks held at once | one documented global acquisition order (CC5) | acquire locks "in a consistent order" (pg :1546-1549, r48 :1183) · "Establish global lock ordering" (pl125 #11, r48 :1184) |
| a `CompletableFuture` flow on an event-loop or common-pool thread | `thenApply`/`thenCompose`/`allOf`; block only at the outer boundary (CC6) | non-blocking servers "use a small, fixed-size thread pool" (sf-webflux :218-219, r48 :1191) · "keep blocking at the outer boundary" (pl142 Ex. 19, r48 :1192) |
| context that a request's code reads | a parameter or a `ScopedValue` (CC7) | a `ThreadLocal` "continues to have a value after a method completes, unless explicitly removed" (jdk-sv :181-189, r48 :1203) · "`ScopedValue` instead of `ThreadLocal`" (pl125 #14, r48 :1204) |
| an in-process cache | a maximum size or weight and an eviction policy (CC10) | "an unbounded cache is a memory leak" (addy-perf :181, r48 :1214) · a cache evicts "to constrain its memory footprint" (guava :25-30, r48 :1215) · `Caffeine.maximumSize(long)` (caffeine :17, r48 :1216) |
| a connection pool | a maximum size and an acquire timeout (CC10) | exhaustion "fails fast instead of queueing forever" (addy-perf :116, r48 :1217) · `connectionTimeout` bounds the wait for a pooled connection (hikari :190-193, r48 :1218) |

Sources: `r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source; §5.1 of
that file names each key's repository and file. One key group is one organisation.

- jdk-thread, jdk-cf, jdk-fjp, jdk-tpe, jdk-ex, jdk-sv: openjdk/jdk `src/java.base/share/classes/java/` (`Thread`,
  `CompletableFuture`, `ForkJoinPool`, `ThreadPoolExecutor`, `Executors`, `ScopedValue`).
- sf-sched, sf-webflux: spring-projects/spring-framework `framework-docs` (scheduling, WebFlux).
- grpc-dl: grpc/grpc.io `content/en/docs/guides/deadlines.md`.
- ms-tf, ms-cb: MicrosoftDocs/architecture-center (transient faults, circuit breaker).
- ietf-idem: ietf-wg-httpapi/idempotency `draft-ietf-httpapi-idempotency-key-header.md`.
- pl125, pl142, pl123cc: jabrena/plinth `skills/` (125 concurrency, 142 functional programming, 123 cross-cutting
  integration patterns).
- addy-api, addy-perf: addyosmani/agent-skills (api-and-interface-design, performance checklist).
- ps-separate: cursor/plugins `pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md`.
- go: golang/website `_content/doc/effective_go.html` · pg: postgres/postgres `doc/src/sgml/mvcc.sgml`.
- guava: google/guava wiki `CachesExplained.md` · caffeine: ben-manes/caffeine wiki `Eviction.md` · hikari:
  brettwooldridge/HikariCP `README.md`.

## Good / Bad

### CC3 — A timeout that stops the work, not only the wait

**Bad** (neutral)
```java
@Bean
public HttpPaymentGateway paymentGateway(GatewayCredentials credentials) {
    RestClient restClient = RestClient.builder().build();
    return new HttpPaymentGateway(credentials, restClient);
}
// InvoiceService.pay:
return CompletableFuture.supplyAsync(() -> paymentGateway.charge(request), chargeExecutor)
    .orTimeout(limits.timeout().toMillis(), TimeUnit.MILLISECONDS)
```
The gateway `RestClient` has no connect or read timeout, so after `orTimeout` fires the charge request keeps running on
a pool thread.

**Good** (neutral)
```java
@Bean
public HttpPaymentGateway paymentGateway(
        final GatewayCredentials credentials,
        final GatewayHttpProperties gatewayHttp) {
    final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(gatewayHttp.connectTimeout())
            .build();
    final var requestFactory = new JdkClientHttpRequestFactory(httpClient);
    requestFactory.setReadTimeout(gatewayHttp.readTimeout());
    final RestClient restClient = RestClient.builder().requestFactory(requestFactory).build();
    return new HttpPaymentGateway(credentials, restClient);
}
```
The deadline is on the socket, so a stuck gateway read ends and frees its thread; `orTimeout` may stay as the caller's
wait. (Real evidence: ledger row CC3.)

### CC4 — A bounded pool has a bounded queue and a stated rejection

**Bad** (neutral)
```java
@Bean(destroyMethod = "shutdownNow")
ScheduledExecutorService orderStreamHeartbeatScheduler() {
    return Executors.newScheduledThreadPool(4,
        Thread.ofPlatform().name("order-stream-heartbeat-", 0).factory());
}
```
Four threads look bounded, but every open order-status stream adds its own periodic task, and nothing says what happens
past capacity.

**Good** (neutral)
```java
@Bean
SseHeartbeats sseHeartbeats(final SseProperties sseProperties) {
    return new SseHeartbeats(new ArrayBlockingQueue<>(sseProperties.maxOpenStreams()));
}

@Bean(destroyMethod = "shutdownNow")
ScheduledThreadPoolExecutor orderStreamHeartbeatTicker(final SseHeartbeats heartbeats) {
    final var ticker = new ScheduledThreadPoolExecutor(
            1,
            Thread.ofPlatform().name("order-stream-heartbeat").factory());
    ticker.scheduleAtFixedRate(heartbeats::sendToAll, HEARTBEAT_SECONDS, HEARTBEAT_SECONDS, TimeUnit.SECONDS);
    return ticker;
}
```
One thread runs one task over a queue of `maxOpenStreams`; `register` returns `Registered | Refused`, so the stream past
the cap is refused out loud. (Real evidence: ledger row CC4.)

### CC9 — A timeout after connect is unknown; a resend reuses the initiator's key

**Bad** (neutral)
```java
for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
        HttpRequest request = HttpRequest.newBuilder()
            // … gateway url, signature, Idempotency-Key = payment id, timeout(15 s), POST body …
            .build();
        HttpResponse<Void> response = HTTP.send(request, HttpResponse.BodyHandlers.discarding());
        int status = response.statusCode();
        // … 2xx → return; 4xx → return; 5xx → retry …
    } catch (IOException failure) {
        log.warn("PaymentGateway charge failed paymentId={} attempt={}: {}: {}",
            payment.id(), attempt + 1, failure.getClass().getSimpleName(), failure.getMessage());
    }
    // … sleep, next attempt …
}
```
A read timeout after the charge was sent is logged as "failed" and sent again, though the gateway may already have
taken the money.

**Good** (neutral)
```java
public ChargeOutcome charge(final Payment payment) {
    paymentLog.recordCharging(payment.id());
    try {
        final HttpResponse<Void> response = http.send(signedCharge(payment), discarding());
        return ChargeOutcome.fromStatus(payment.id(), response.statusCode());
    } catch (final HttpConnectTimeoutException | ConnectException notConnected) {
        return new ChargeOutcome.NotSent(payment.id(), notConnected.getClass().getSimpleName());
    } catch (final IOException afterConnect) {
        return new ChargeOutcome.Unknown(payment.id(), afterConnect.getClass().getSimpleName());
    } catch (final InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        return new ChargeOutcome.Unknown(payment.id(), "interrupted");
    }
}
```
Intent is recorded first; anything after connect is `Unknown`; the caller resends only `NotSent`, with the same
payment-id key. (Real evidence: ledger row CC9.)

## Decided edges

- **Skip when** a `synchronized` block holds a blocking call on a virtual thread on Java 24 or later: JEP 491 removed
  that pinning, and pl125 #13, which says otherwise, is stale (CC1; source unread: JEP 491, r48 :1120-1121). — **Do
  not skip when** the blocking call runs inside a class initialiser: that still pins its carrier (CC1; source unread:
  JEP 491, r48 :1120). — **Confidence** medium
- **Skip when** `orTimeout` sits beside a client timeout that stops the work: it is the caller's wait (CC3; jdk-cf
  :2545-2547, r48 :1140; the CC3 Good above). — **Do not skip when** `orTimeout` is the only timeout on the call. —
  **Confidence** high
- **Skip when** a non-idempotent command is resent with its initiator's idempotency key: the resource recognises the
  retry (CC8, CC9; ietf-idem :64, r48 :1149). — **Do not skip when** the key is minted per attempt: it comes from the
  retrying layer (addy-api :171, r48 :1147). — **Confidence** high
- **Skip when** the `join()` or `get()` sits at the outer boundary of the flow, or runs on a virtual thread (CC6; pl142
  Ex. 19, r48 :1192; jdk-thread :108-110, r48 :1117, :1196). — **Do not skip when** it blocks mid-flow on an
  event-loop or common-pool thread. — **Confidence** high
- **Skip when** request context crosses a `CompletableFuture` or executor hop as a parameter, not a `ScopedValue`: a
  `ScopedValue` reaches only threads forked in a `StructuredTaskScope` (CC7; jdk-sv :138-144, r48 :1207-1208). —
  **Do not skip when** it crosses in a `ThreadLocal`, copied by hand or not. — **Confidence** high

## Review checks

Walk every changed Java file that starts threads, submits async work, calls a remote service, retries, locks, or builds
a pool or a cache.

- [ ] CC1 — Blocking I/O fanned out on a platform-thread pool is a finding. For each virtual-thread factory
  (`grep -nE "ofVirtual\(\)"`), a factory passed to a `ThreadPoolExecutor` or a `new…ThreadPool(` is a finding.
- [ ] CC2 — For each `supplyAsync` or `runAsync` (`grep -nE "(supply|run)Async\("`), find an executor argument. A
  one-argument call that does blocking work is a finding.
- [ ] CC3 — For each remote call (`RestClient`, `HttpClient`, `WebClient`, a gRPC stub, a JDBC or Redis client), find a
  connect and a read timeout, or a deadline, on the client. A call whose only timeout is `orTimeout` is a finding.
- [ ] CC9 — For each side-effecting remote call, find an outcome that keeps a timeout after connect apart from failure.
  A timeout after connect handled as failure, or a resend whose idempotency key is minted inside the retry, is a
  finding.
- [ ] CC8 — For each retry loop or retry policy, find bounded attempts, jittered backoff, a transient-only filter, an
  idempotent call (or an initiator's key) and a timeout. Any one missing is a finding.
- [ ] CC11 — For each remote dependency the change retries (`grep -nE "@Retryable|RetryTemplate|Retry\.of|retryWhen"`),
  find a circuit breaker around it. A retried dependency with no circuit breaker is a finding.
- [ ] CC4 — For each pool built (`grep -nE "new ThreadPoolExecutor|Executors\.new(Fixed|Scheduled)ThreadPool"`), find a
  bounded queue and a stated rejection behaviour. `newFixedThreadPool` and `newScheduledThreadPool`, whose queues are
  unbounded, are findings.
- [ ] CC5 — For each new lock, `synchronized` block or shared mutable field, ask whether each writer could own its own
  key or file. Shared state that could be separated is a finding, and so are two locks held at once with no
  documented order.
- [ ] CC6 — Each `.join()`, `.get()` or `.block()` (`grep -nE "\.(join|get|block)\(\)"`) on an event-loop or
  common-pool thread that is not at the outer boundary is a finding. A hit inside a virtual-thread task is not.
- [ ] CC7 — Each new `ThreadLocal` (`grep -n "ThreadLocal"`) is a finding.
- [ ] CC10 — For each in-process cache, find a maximum size or weight and an eviction policy; for each connection
  pool, a maximum size and an acquire timeout. Any one missing is a finding.
