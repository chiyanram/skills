# Concurrency — Good / Bad examples

Every approved Good/Bad pair for the concurrency rules, one per rule that has one. The rules, the decision table and
the review checks are in [`../concurrency.md`](../concurrency.md).

Contents: CC3 · CC14 · CC4 · CC9 · CC15 · CC12

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

### CC14 — The caller's remaining deadline, not a fixed timeout

**Bad**
```java
// stock is built with a connect timeout (CC3)
Availability availability(final Order order) {
    return stock.check(order.items(), Duration.ofSeconds(20));
}
```
The caller waits two seconds for the order page, yet this call can hold its thread and connection for twenty.

**Good**
```java
// stock is built with a connect timeout (CC3)
Availability availability(final Order order, final Deadline deadline) {
    final Duration remaining = deadline.remaining();
    if (!remaining.isPositive()) {
        return Availability.unknown();
    }
    return stock.check(order.items(), remaining);
}
```
The call gets only the time its caller has left, and it is not made at all once that time has run out.

### CC4 — A bounded pool has a bounded queue and a stated rejection

**Bad**
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

**Good**
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

### CC15 — Claim the key with its fingerprint, and replay the stored response

**Bad**
```java
PaymentOutcome pay(final IdempotencyKey key, final PaymentRequest request) {
    if (keys.exists(key)) {
        return new PaymentOutcome.Duplicate(key);
    }
    keys.save(key);
    return payments.charge(request);
}
```
A client that retries after a lost response gets `Duplicate`, never the payment it made. Two concurrent requests can
both pass the check, and a different payload under the same key is never noticed.

**Good**
```java
PaymentOutcome pay(final IdempotencyKey key, final PaymentRequest request) {
    return switch (keys.claim(key, Fingerprint.of(request))) {
        case Claim.New claimed -> keys.completeOrRelease(claimed, () -> payments.charge(request));
        case Claim.Completed done -> done.outcome();
        case Claim.InFlight _ -> new PaymentOutcome.InProgress(key); // the controller answers 409
        case Claim.Mismatch _ -> new PaymentOutcome.KeyReused(key);  // the controller answers 422
    };
}
```
`claim` inserts the key and fingerprint under a unique constraint, so only one request is `New`. A repeat gets the
stored outcome. If the charge throws, `completeOrRelease` releases the claim, so a retry can run it again.

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
