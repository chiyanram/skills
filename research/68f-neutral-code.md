# 68f — Neutral Good/Bad pairs: code (G9b — Java, errors, layers, shape, Spring, API, security) (#99, map #9)

Source: research/56a, 56b, 56c (selection research/54). Domain: ordering + billing (#99 brief). research/47 covers none of these ids.
- Stand-ins (56a): `AgentChatPort.chat` (LLM call, JV1) → `PaymentGateway.charge` · optional NER bean `NerPort` (TY1) → optional fraud-check HTTP service `FraudCheck` · trusted-certificate request pem | uri+fingerprint (TY3) → `ShippingRequest` pickup point | street+postcode · agent task `submit` (TY8) → `InvoiceService.issue` · picker SQL compiler (TY9) → invoice search filter builder · Exchange/Graph mail `RestClient` (CC3) → `HttpPaymentGateway` `RestClient` · chat-session SSE heartbeats (CC4, CM4) → order-status event stream · webhook callback sender + `X-aruvii-JobId` (CC9) → gateway charge + `Idempotency-Key` = payment id · DB-connection create / NAME_TAKEN (ER1) → invoice issue / `INVOICE_ALREADY_ISSUED` · Ollama `/api/tags` model check (ER4) → gateway `/status` currency check · agent lifecycle audit (ER8) → order status audit · tool-call metric (CM3) → `payment.charge.duration` · session send-message + cap claim (LY1) → invoice pay + gateway charge · `@wsAuth` → `@invoiceAuth` · `LlmAdapterRegistry` / `LlmAdapterPort` (LY2) → `PaymentGatewayRegistry` / `PaymentGateway` · `AruviiException` → `OrderException` · Added terms: `ChargeRequest`, `ChargeReply`, `ChargeOutcome` (NotSent | Unknown | …), `ChargeDecision.Declined`, `ChargeStatus`, `PaymentMethod` enum, `paymentLog`, `signedCharge`, `HttpPaymentGateway`, `GatewayCredentials`, `GatewayHttpProperties`, `OrderResponse`, `PaymentResponse`, `PayInvoiceRequest`, `PayOutcome` (Paid | AlreadyPaid | Declined), `invoicePayer`, `ApiResponse`, `FraudCheck`, `FraudSignal`, `FraudCheckMode`, `OrderRules`, `RuleVerdict`, `Screening`, `ShippingRequest` (Pickup | Address), `OrderId`/`CustomerId`/`UserId`, `NotifyTarget` (None | Email), `IssueCommand`, `InsertionResult` (Created | Duplicate), `BetweenBounds`, `WhereClause`, `SseHeartbeats`, `SseProperties`, `SseHeaders`, `OrderStatusChange`, `OrderAuditEntry`, `auditLog`, `PaymentGatewayRegistry`, `UnsupportedPaymentMethodException`, `ConfirmService` entries, ErrorCode `INVOICE_ALREADY_ISSUED`, `VALIDATION_FAILED` · Skipped: none (all 18 APPROVED).
- Stand-ins (56b): `aruvii.` property prefix → `example.` · retention sentinel `0` = keep forever (DS1) → grace days `0` = never overdue · LLM tool call with mock mode + approval (DS3) → PaymentGateway call in sandbox mode + manual review · scheduled trigger claim (DS4) → overdue-reminder claim on an invoice · OpenAPI tool import into a tool group (DS8) → CSV order import onto an invoice · smoke sessions/tools/providers/workspaces (DS12) → smoke orders/invoices/customers · PII endpoint + Ollama RestClients (DS14) → tax-rate service + PaymentGateway clients · user erasure (MS6) → order cancellation · notification config update (LG2) → invoice reschedule · chat SSE stream (LG3) → order-status SSE stream · `AgentChatPort` absent from the api app (LY6) → `EmailSender` absent from orders-api · Ollama activity clients (LY7) → fraud-check HTTP service clients in orders-api and billing · agent repository (SC6) → order repository · ONNX vs hash embeddings (SC7) → rate-table vs flat-rate `TaxCalculator` · worker streams chat/task/eval/promptTest (SC15) → notifications streams ordersPlaced/invoicesOverdue/paymentsReceived · provider credentials under `master-key` (SC16) → stored PaymentGateway credentials · TLS trust store (SC19) → `TaxRateTable` · JWT secret key (SC21) → PaymentGateway webhook signing secret · pipeline builder workspace → agents (NGB3) → record-payment form customer → open invoices · Added terms: Customer.graceDays, Customer.name, `GracePeriod` (NeverOverdue | Days), `OverduePreview`, `PaymentAttempt`, `PaymentIds`, `PaymentMethod`, `PaymentStatus`, `GatewayExchange`, `GatewayRun` (Live | Sandbox), `SandboxSource`, `ReviewGate` (NotRequired | Required), `ReminderClaim` (Won | Lost), `ClaimWindow`, `ReminderOutcome`, `OrderImporter`, `ImportOrdersRequest`, `InvoiceDestination`, `InvoiceTarget` (None | New | Existing), Order.reference, Invoice.reference, `TaxRateClient`, `TaxServiceProperties`, `PaymentGatewayClient`, `PaymentGatewayProperties`, `OrderCancellation`, `CancelRequest`, `CancelOutcome` (AlreadyCancelled | …), `OrderAlreadyCancelledException`, `OrderStatusEvent`, `OrderStatusSubscriber`, `ReminderEmail`, `CheckoutFraudClient`, `PaymentFraudClient`, `FraudCheckProperties`, `OrderJpaRepository`, `OrderRepositoryAdapter`, `RateTableTaxCalculator`, `FlatRateTaxCalculator`, `TaxProperties`, `TaxMode`, `RateTableFiles`, `NotificationStreamsProperties`, `NotificationStream`, streams invoices.overdue / payments.received, `CredentialEncryptor`, `CredentialProperties`, `TaxRateTable`, `WebhookSecretPort`, `WebhookSecretStore`, `BillingSettingsService`, `BillingSettingsPort`, `InvoiceResponse`, payment allocations · Skipped: none.
- Stand-ins (56c): tool PATCH/DELETE → order PATCH/DELETE on `/api/orders/{id}` · workspace A/B ownership → customer A/B owns the order · `@wsAuth` → `@orderAuth` · setup wizard `/api/setup/complete` kept (generic first-admin setup) · LLM tool input schema (TT2) → JSON schema of the public `POST /api/invoices/{id}/send` request · OIDC discovery / token endpoint (SE1, SE5) → PaymentGateway discovery document and its `refund_endpoint` · `SsrfGuard` → `UrlGuard` · file tool (SE4) → `InvoicePdfStore` reading a stored PDF by relative path · `AruviiException` → `OrderException` · Added terms: `UrlGuard`, `UrlDecision` (Blocked | Permitted), `CheckedUrl`, `GatewayDiscovery`, `RefundReply`, `InvoicePdfStore`, `PathCheck` (Inside | Outside | NotFound), ErrorCode `GATEWAY_URL_BLOCKED`, `GATEWAY_DISCOVERY_FAILED`, `ApiKeyCandidate` · Skipped: none.

### JV1 — Time is `Instant`/`Duration`; `Date`/zoned only at a library or display boundary

**Bad** (neutral)
```java
final long chargeStartMillis = clock.millis();
final ChargeReply reply = paymentGateway.charge(chargeRequest(invoice, customerId));
final long elapsedMillis = clock.millis() - chargeStartMillis;
log.info(
        "action=invoice.charge.ok invoiceId={} orderId={} customerId={} durationMs={}",
        invoice.id(),
        invoice.orderId(),
        customerId,
        elapsedMillis);
```
What goes wrong: elapsed time is raw `long` subtraction of epoch millis, so the span is a bare number and not a `Duration`.

**Good** (neutral)
```java
final var chargeStart = clock.instant();
final ChargeReply reply = paymentGateway.charge(chargeRequest(invoice, customerId));
final var elapsed = Duration.between(chargeStart, clock.instant());
log.info(
        "action=invoice.charge.ok invoiceId={} orderId={} customerId={} durationMs={}",
        invoice.id(),
        invoice.orderId(),
        customerId,
        elapsed.toMillis());
```
Why: the time is an `Instant` from an injected `Clock` and the span a `Duration`; it becomes a `long` only for the log line.

Evidence: `aruvii-agents/…/application/PipelineExecutionService.java:49,54-58,68,79-80` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:20-57 · fix from 56a:41-57

### JV5 — `final var` only when the right-hand side shows the type

**Bad** (neutral)
```java
final var customerId = UUID.fromString(principal.getName());
final var placed = orderService.place(id, customerId).orThrow(ErrorCode.ORDER_NOT_FOUND);
return ApiResponse.ok(placed);
```
What goes wrong: neither `place` nor `orThrow` tells the reader the value is an `OrderResponse`, so `var` hides the type.

**Good** (neutral)
```java
public ApiResponse<OrderResponse> place(
        @PathVariable final UUID id,
        final Principal principal) {
    final var customerId = UUID.fromString(principal.getName());
    final OrderResponse placed = orderService.place(id, customerId)
            .orThrow(ErrorCode.ORDER_NOT_FOUND);
    return ApiResponse.ok(placed);
}
```
Why: `UUID.fromString` is a factory, so `var` stays; `place(…).orThrow(…)` names actions, not a type, so the type is written out.

Evidence: `aruvii-api/…/controller/ProviderController.java:58-61` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:59-87 · fix from 56a:72-87

### TY1 — No `null` decides a case; absence is `Optional`, a sealed type or an enum

**Bad** (neutral)
```java
private final FraudCheck fraudCheck;

OrderScreening(@Autowired(required = false) final FraudCheck fraudCheck) { this.fraudCheck = fraudCheck; }
// …
private Screening screen(final Order order, final boolean fraudCheckEnabled) {
    final RuleVerdict rules = orderRules.assess(order);
    // …
    if (fraudCheckEnabled && fraudCheck != null) {
        final List<FraudSignal> signals = fraudCheck.signalsFor(order);
        // … merge, return
    }
    return new Screening(rules, List.of());
}
```
What goes wrong: a `null` field and a boolean together choose the path; flag on with no fraud-check bean silently skips the check.

**Good** (neutral)
```java
public enum FraudCheckMode { OFF, ON }

private final OrderRules orderRules;
private final ObjectProvider<FraudCheck> fraudCheck;

private Screening screen(final Order order, final FraudCheckMode mode) {
    final RuleVerdict ruleVerdict = orderRules.assess(order);
    final List<FraudSignal> signals = switch (mode) {
        case OFF -> List.of();
        case ON -> fraudCheck.getObject().signalsFor(order);
    };
    return withSignals(ruleVerdict, signals);
}
```
Why: the flag becomes an enum the switch must name, and "ON but no fraud-check bean" now fails loudly instead of skipping.

Evidence: `aruvii-guardrails/…/application/GuardrailPipeline.java:35,43-44,113-114,123-124,132` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:89-130 · fix from 56a:112-130

### TY3 — Sealed variants exclude forbidden combinations; the compact constructor checks only the rest

**Bad** (neutral)
```java
if (request.pickupPointId() != null && !request.pickupPointId().isBlank()) {
    saved = service.shipToPickupPoint(request.orderId(), request.pickupPointId(), request.note(), userId);
} else if (request.street() != null && request.postcode() != null) {
    saved = service.shipToAddress(request.orderId(), request.street(), request.postcode(),
        request.note(), userId);
} else {
    throw new IllegalArgumentException("Either 'pickupPointId' or both 'street' + 'postcode' must be supplied");
}
```
What goes wrong: the request record has nullable fields, so every reader re-derives the two legal shapes and "street without postcode" still compiles.

**Good** (neutral)
```java
public sealed interface ShippingRequest {
    record Pickup(
            @NotNull UUID orderId,
            @NotBlank String pickupPointId,
            @Size(max = 500) String note) implements ShippingRequest {}
    record Address(
            @NotNull UUID orderId,
            @NotBlank String street,
            @NotBlank String postcode,
            @Size(max = 500) String note) implements ShippingRequest {}
}
```
Why: "pickup point, or street and postcode" is two records, so a forbidden mix cannot be built; the service switches over both, no `default`.

Evidence: `aruvii-api/…/controller/TrustedCertificateController.java:54-61` @772736bf over `…/controller/dto/TrustedCertificateRequest.java:10-16` (Bad, real) · source 56a-g9b-good-bad-java-errors.md:132-170 · fix from 56a:150-170

### TY8 — Wrap a primitive when same-typed values could be swapped, or it carries an invariant

**Bad** (neutral)
```java
public Invoice issue(final long orderId, final long customerId, final long issuedBy,
                     final String note, final String notifyEmail) {
```
What goes wrong: three `long` ids and two `String`s in one signature; any two ids can be swapped at the caller and the build stays green.

**Good** (neutral)
```java
public record OrderId(long value) {}
public record CustomerId(long value) {}
public record UserId(long value) {}
public sealed interface NotifyTarget {
    record None() implements NotifyTarget {}
    record Email(String address) implements NotifyTarget {}
}
public Invoice issue(
        final OrderId orderId,
        final CustomerId customerId,
        final UserId issuedBy,
        final String note,
        final NotifyTarget notify) {
```
Why: `issue(customerId, orderId, …)` no longer compiles; the id records check nothing, because the reason to wrap is the swap.

Evidence: `aruvii-agents/…/application/TaskService.java:29-30` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:172-205 · fix from 56a:184-205

### TY9 — Strengthen a type only where partiality shows (a cast, a null check, a "never happens" throw)

**Bad** (neutral)
```java
private int appendBetween(final List<String> whereParts,
                            final List<String> placeholderOrder,
                            final Map<String, Object> placeholderValues,
                            final int index,
                            final String quotedColumn,
                            final Object value) {
    if (!(value instanceof List<?> bounds) || bounds.size() != 2) {
        throw new IllegalArgumentException(
            "BETWEEN operator on " + quotedColumn + " requires a 2-tuple value");
    }
    // … two placeholder names, the BETWEEN fragment …
    placeholderValues.put(lowPlaceholder, bounds.get(0));
    placeholderValues.put(highPlaceholder, bounds.get(1));
    return index + 2;
}
```
What goes wrong: in the invoice search builder an `Object` stands in for "two due dates"; the `instanceof`, size check and `get(0)` are partiality.

**Good** (neutral)
```java
record BetweenBounds(Object low, Object high) {}

private int appendBetween(
        final WhereClause where,
        final int index,
        final String quotedColumn,
        final BetweenBounds bounds) {
    final String lowPlaceholder = FILTER_PLACEHOLDER_PREFIX + index;
    final String highPlaceholder = FILTER_PLACEHOLDER_PREFIX + (index + 1);
    where.add(quotedColumn + " BETWEEN :" + lowPlaceholder + " AND :" + highPlaceholder);
    where.bind(lowPlaceholder, bounds.low());
    where.bind(highPlaceholder, bounds.high());
    return index + 2;
}
```
Why: the check moves to where the filter is parsed, which builds `BetweenBounds` once; `appendIn` keeps its plain list, being total.

Evidence: `aruvii-tools/…/infrastructure/compiler/PickerCompiler.java:260-277` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:207-252 · fix from 56a:232-252

### CC3 — Every remote call has a timeout that stops the work; `orTimeout` alone only abandons

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
What goes wrong: the gateway `RestClient` has no connect or read timeout, so after `orTimeout` fires the charge request keeps running on a pool thread.

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
Why: the deadline is on the socket, so a stuck gateway read ends and frees its thread; `orTimeout` may stay as the caller's wait.

Evidence: `aruvii-tools/…/ToolsAutoConfiguration.java:211-218` + `aruvii-tools/…/handlers/ExchangeToolHandler.java:113-114` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:254-296 · fix from 56a:276-296

### CC4 — A bounded pool has a bounded queue and a stated rejection behaviour

**Bad** (neutral)
```java
@Bean(destroyMethod = "shutdownNow")
ScheduledExecutorService orderStreamHeartbeatScheduler() {
    return Executors.newScheduledThreadPool(4,
        Thread.ofPlatform().name("order-stream-heartbeat-", 0).factory());
}
```
What goes wrong: four threads look bounded, but every open order-status stream adds its own periodic task, and nothing says what happens past capacity.

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
Why: one thread runs one task over a queue of `maxOpenStreams`; `register` returns `Registered | Refused`, so the stream past the cap is refused out loud.

Evidence: `aruvii-api/…/config/SseHeartbeatConfig.java:12-16` @772736bf (Bad, real; per-stream task `SessionMessageController.java:239-242`) · source 56a-g9b-good-bad-java-errors.md:298-333 · fix from 56a:313-333

### CC9 — A remote call ends as success, failure or unknown; intent before the call; key from the initiator

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
What goes wrong: a read timeout after the charge was sent is logged as "failed" and sent again, though the gateway may already have taken the money.

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
Why: intent is recorded first; anything after connect is `Unknown`; the caller resends only `NotSent`, with the same payment-id key.

Evidence: `aruvii-worker/…/webhook/WebhookCallbackSender.java:69-97` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:335-382 · fix from 56a:359-382

### ER1 — A foreseeable non-success is a sealed outcome; only faults throw

**Bad** (neutral)
```java
public Invoice issue(final UUID orderId, final IssueCommand command) {
    LOG.info("action=invoice_issue orderId={}", orderId);

    invoiceRepository.findByOrderId(orderId).ifPresent(existing -> {
        throw new OrderException(ErrorCode.INVOICE_ALREADY_ISSUED,
            "orderId=" + orderId + " invoiceId=" + existing.id());
    });

    final Invoice saved = invoiceRepository.save(Invoice.open(orderId, command.total(), command.dueDate()));
```
What goes wrong: "this order already has an invoice" is a normal answer, yet it leaves as an exception from a lambda; the signature promises an `Invoice`.

**Good** (neutral)
```java
public InsertionResult<Invoice> issue(final UUID orderId, final IssueCommand command) {
    log.info("action=invoice_issue orderId={}", orderId);
    if (invoiceRepository.findByOrderId(orderId).isPresent()) {
        return new InsertionResult.Duplicate<>(orderId.toString());
    }
    final Invoice saved = invoiceRepository.save(Invoice.open(
            orderId,
            command.total(),
            command.dueDate()));
    log.info("action=invoice_issue_ok orderId={} invoiceId={}", orderId, saved.id());
    return new InsertionResult.Created<>(saved);
}
```
Why: the duplicate is a case of the return type; the controller answers `.orThrow(ErrorCode.INVOICE_ALREADY_ISSUED)`, and a database fault still throws.

Evidence: `aruvii-tools/…/application/DbConnectionService.java:69-85` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:386-428 · fix from 56a:410-428

### ER4 — Catch the narrowest type; `catch (Exception)` only at a must-not-fail boundary, commented

**Bad** (neutral)
```java
try {
    JsonNode root = MAPPER.readTree(body);
    JsonNode currencies = root.path("currencies");
    if (currencies.isArray()) {
        for (JsonNode currencyNode : currencies) {
            String code = currencyNode.path("code").asString();
            if (currency.equals(code)) {
                currencySupported = true;
                break;
            }
        }
    }
} catch (Exception failure) {
    log.warn(
            "action=gateway.health.status_unreadable cause={} message={}",
            failure.getClass().getSimpleName(),
            failure.getMessage());
}
```
What goes wrong: only the JSON parse can fail here, yet the catch takes every exception; a loop bug reads as "currency not supported".

**Good** (neutral)
```java
private boolean supportsCurrency(final String statusBody) {
    try {
        for (final JsonNode entry : MAPPER.readTree(statusBody).path("currencies")) {
            if (entry.path("code").asString().equals(currency)) {
                return true;
            }
        }
        return false;
    } catch (final JacksonException unexpectedShape) {
        log.warn(
                "action=gateway.health.status_unreadable cause={} message={}",
                unexpectedShape.getClass().getSimpleName(),
                unexpectedShape.getMessage());
        return false;
    }
}
```
Why: `JacksonException` is the one failure the parse can raise, so it is the one caught, and logged with class and message; any other exception now surfaces.

Evidence: `aruvii-api/…/activity/AdminActivityClient.java:74-88` @772736bf (Bad, real; flag declared `:73`) · source 56a-g9b-good-bad-java-errors.md:430-474 · fix from 56a:454-474

### ER8 — A best-effort metric or audit call may catch and continue; WARN with the exception class and message

**Bad** (neutral)
```java
private void logStatusChange(final OrderStatusChange change) {
    try {
        auditLog.record(OrderAuditEntry.of(change, clock.instant()));
    } catch (Exception ignored) { /* never block the order on audit failures */ }
}
```
What goes wrong: catching is allowed because audit is best effort, but the block is silent, so a broken audit trail is invisible.

**Good** (neutral)
```java
private void logStatusChange(final OrderStatusChange change) {
    try {
        auditLog.record(OrderAuditEntry.of(change, clock.instant()));
    } catch (final RuntimeException auditFailure) {
        log.warn(
                "action=order.status.audit_failed orderId={} statusAction={} cause={} message={}",
                change.orderId(),
                change.action(),
                auditFailure.getClass().getSimpleName(),
                auditFailure.getMessage());
    }
}
```
Why: the order change still never blocks, but each lost audit row leaves one WARN line naming the exception class and message, with no stack.

Evidence: `aruvii-agents/…/application/AgentService.java:62-70` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:476-511 · fix from 56a:494-511

### ER10 — An error response carries the `ErrorCode` message only

**Bad** (neutral)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(DataIntegrityViolationException violation) {
    return ApiResponse.error("Invalid reference: " + violation.getMostSpecificCause().getMessage());
}
```
What goes wrong: the handler sends the JDBC driver's message to the client: constraint names, column names, sometimes the offending value.

**Good** (neutral)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(final DataIntegrityViolationException violation) {
    final String traceId = currentTraceId();
    log.warn(
            "action=api.data_integrity traceId={} cause={} message={}",
            traceId,
            violation.getMostSpecificCause().getClass().getSimpleName(),
            violation.getMostSpecificCause().getMessage());
    return ApiResponse.error(
            ErrorCode.VALIDATION_FAILED.code(),
            ErrorCode.VALIDATION_FAILED.defaultMessage(),
            traceId);
}
```
Why: the body says only what the error catalogue says; the operator gets trace id, cause class and message in the log; it lives in the one central exception handler (ER11).

Evidence: `aruvii-api/…/controller/AgentController.java:186-190` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:513-545 · fix from 56a:527-545

### CM3 — A comment survives only for a constraint the code cannot show

**Bad** (neutral)
```java
// Metric: payment.charge.duration tagged by method + status. Bounded cardinality —
// payment methods are an enum, statuses are a small fixed set. Operators get a graph
// of "is the gateway getting slower?" and "is the PAID rate dropping?"
try {
    meters.timer("payment.charge.duration",
        "method", method,
        "status", status.toString())
        .record(latency);
} catch (RuntimeException meterFailure) {
    log.warn(
            "action=payment.charge.metric_failed cause={} message={}",
            meterFailure.getClass().getSimpleName(),
            meterFailure.getMessage());
}
```
What goes wrong: the comment defends our own tag choice instead of the code showing it, and it is false: `method` is a `String`.

**Good** (neutral)
```java
private void recordChargeDuration(
        final PaymentMethod method,
        final ChargeStatus status,
        final Duration latency) {
    try {
        meters.timer("payment.charge.duration", "method", method.name(), "status", status.name())
                .record(latency);
    } catch (final RuntimeException meterFailure) {
        log.warn(
                "action=payment.charge.metric_failed method={} cause={} message={}",
                method,
                meterFailure.getClass().getSimpleName(),
                meterFailure.getMessage());
    }
}
```
Why: two enum parameters now show the bounded cardinality, so the comment has nothing left to say; operator questions belong in the metrics docs.

Evidence: `aruvii-worker/…/chat/ChatOrchestrator.java:219-229` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:547-587 · fix from 56a:568-587

### CM4 — Check a comment's factual claim; encode "keep in sync" as a type, test or lint

**Bad** (neutral)
```java
// Mandatory anti-buffering headers — without these, nginx + corporate proxies stall
// SSE responses for 30s+ at a time. Stays in sync with docs/architecture.md §Streaming.
response.setHeader("Cache-Control",     "no-cache, no-transform");
response.setHeader("X-Accel-Buffering", "no");
```
What goes wrong: the doc section has no header text, so the claim is false, and the same two headers are hand-copied into two other stream endpoints.

**Good** (neutral)
```java
final class SseHeaders {
    private SseHeaders() {
    }

    // nginx and corporate proxies hold text/event-stream frames unless these two headers are set
    static void disableProxyBuffering(final HttpServletResponse response) {
        response.setHeader(HttpHeaders.CACHE_CONTROL, "no-cache, no-transform");
        response.setHeader("X-Accel-Buffering", "no");
    }
}
```
```groovy
def "should tell proxies not to buffer the order event stream"() {
    given: "a response for an order event stream, before any frame is written"
    def response = new MockHttpServletResponse()
    when: "the endpoint prepares the stream"
    SseHeaders.disableProxyBuffering(response)
    then: "nginx and caching proxies pass each frame on at once instead of holding it"
    response.getHeader("X-Accel-Buffering") == "no"
    response.getHeader(HttpHeaders.CACHE_CONTROL) == "no-cache, no-transform"
}
```
Why: every stream endpoint calls one helper and a spec pins the headers, so the sync note goes; the proxy sentence stays, an outside constraint.

Evidence: `aruvii-api/…/controller/SessionMessageController.java:230-233` @772736bf (Bad, real; copies `PromptBuilderController.java:162`, `WebhookController.java:140`) · source 56a-g9b-good-bad-java-errors.md:589-626 · fix from 56a:603-626

### CM7 — Never suppress a lint or compiler rule that protects correctness; fix the type

**Bad** (neutral)
```ts
interface ConfirmEntry {
  id: string;
  options: ConfirmOptions;
  mode: 'confirm' | 'prompt';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  resolve: (value: any) => void;
}
// … "Pay invoice" asks before charging …
ask(options: ConfirmOptions): Promise<boolean> {
  return this.enqueue(options, 'confirm') as Promise<boolean>;
}
```
What goes wrong: silencing `no-explicit-any` lets `accept()` hand a string to the "Pay invoice" confirm, and the cast hides it.

**Good** (neutral)
```ts
type ConfirmEntry =
  | { id: string; options: ConfirmOptions; mode: 'confirm'; resolve: (accepted: boolean) => void }
  | { id: string; options: ConfirmOptions; mode: 'prompt'; resolve: (input: string | null) => void };

ask(options: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => this.enqueue({ id: newId(), options, mode: 'confirm', resolve }));
}

accept(inputValue = ''): void {
  const entry = this._current();
  if (entry?.mode === 'confirm') entry.resolve(true);
  if (entry?.mode === 'prompt') entry.resolve(inputValue);
  this._current.set(this.queue.shift() ?? null);
}
```
Why: the union ties each `mode` to its `resolve` type, so suppression and casts go; style rules may be suppressed, type rules fixed.

Evidence: `aruvii-ui/src/app/core/confirm.service.ts:13-19,27-29` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:628-667 · fix from 56a:648-667

### LY1 — A controller binds, delegates and shapes; a branch that chooses an outcome lives in a service

**Bad** (neutral)
```java
Invoice invoice = invoiceService.get(id);
// … caller id, trace id, 6 comment lines on ordering …
if (invoice.status() != InvoiceStatus.OPEN) {
    throw new OrderException(ErrorCode.INVOICE_ALREADY_PAID,
        "invoice " + invoice.id() + " is " + invoice.status());
}
// … 4 comment lines on charging before recording …
if (paymentGateway.charge(invoice.id(), invoice.total())
        instanceof ChargeDecision.Declined declined) {
    throw new OrderException(ErrorCode.PAYMENT_DECLINED,
        "gateway declined: " + declined.reason());
}
paymentService.record(invoice.id(), invoice.total());
```
What goes wrong: the controller decides whether an invoice may be paid and in what order, so that contract lives where no service test reaches.

**Good** (neutral)
```java
@PostMapping("/{id}/payments")
@PreAuthorize("@invoiceAuth.canPay(#id)")
public ApiResponse<PaymentResponse> pay(
        @PathVariable final UUID id,
        @RequestBody final PayInvoiceRequest request,
        final Authentication authentication) {
    final PayOutcome outcome = invoicePayer.pay(id, callerOf(authentication), request);
    return switch (outcome) {
        case PayOutcome.Paid paid -> ApiResponse.ok(PaymentResponse.of(paid));
        case PayOutcome.AlreadyPaid already ->
                throw new OrderException(ErrorCode.INVOICE_ALREADY_PAID, already.detail());
        case PayOutcome.Declined declined ->
                throw new OrderException(ErrorCode.PAYMENT_DECLINED, declined.detail());
    };
}
```
Why: the service checks status, charges and records in order, returning a sealed outcome; an exhaustive switch over it is shaping, which is allowed.

Evidence: `aruvii-api/…/controller/SessionMessageController.java:142,155-173` @772736bf (Bad, real) · source 56a-g9b-good-bad-java-errors.md:669-712 · fix from 56a:692-712

### LY2 — An interface only for a faked boundary or a module boundary; its one implementation is `Default<Name>`

**Bad** (neutral)
```java
@Service
public class PaymentGatewayRegistryImpl implements PaymentGatewayRegistry {
    private final List<PaymentGateway> gateways;

    public PaymentGatewayRegistryImpl(List<PaymentGateway> gateways) {
        this.gateways = gateways;
    }

    @Override
    public PaymentGateway forMethod(String method) {
        for (PaymentGateway gateway : gateways) {
            if (gateway.supports(method)) {
                return gateway;
            }
        }
        throw new UnsupportedPaymentMethodException(method);
    }
```
What goes wrong: a public `*Impl` behind an interface in a shared module, though every caller is in billing and the real boundary is `PaymentGateway`.

**Good** (neutral)
```java
@Service
public class PaymentGatewayRegistry {

    private final List<PaymentGateway> gateways;

    public PaymentGatewayRegistry(final List<PaymentGateway> gateways) {
        this.gateways = List.copyOf(gateways);
    }

    public PaymentGateway forMethod(final String method) {
        return gateways.stream()
                .filter(gateway -> gateway.supports(method))
                .findFirst()
                .orElseThrow(() -> new UnsupportedPaymentMethodException(method));
    }
```
Why: one concrete class in billing; tests build it with `FakePaymentGateway`s instead of mocking the selection logic.

Evidence: `aruvii-worker/…/llm/LlmAdapterRegistryImpl.java:14-29` @772736bf, interface `aruvii-shared/…/llm/LlmAdapterRegistry.java:9-16` (Bad, real) · source 56a-g9b-good-bad-java-errors.md:714-764 · fix from 56a:740-764

### DS1 — Look for a restructure that deletes branches, not one that moves them

**Bad** (neutral)
```java
// OverdueReminder.java — the job decodes the sentinel …
final int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    log.debug("overdue_reminder customerId={} never_overdue — skipped", customer.id());
    continue;
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
// InvoicePreviewController.java — … and the preview decodes it again
int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    return new OverduePreview(customer.id(), 0, null, 0L);
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
```
What goes wrong: the "0 means never overdue" rule and the cutoff arithmetic are written twice, so the preview can disagree with the job.

**Good** (neutral)
```java
public sealed interface GracePeriod {
    record NeverOverdue() implements GracePeriod {}
    record Days(int count) implements GracePeriod {}   // compact ctor rejects count <= 0, unchanged

    default Optional<Instant> overdueBefore(final Instant now) {
        return switch (this) {
            case NeverOverdue _ -> Optional.empty();
            case Days days -> Optional.of(now.minus(days.count(), ChronoUnit.DAYS));
        };
    }
}
// job:     period.overdueBefore(clock.instant()).ifPresent(cutoff -> remind(customer.id(), cutoff));
// preview: final long invoiceCount = period.overdueBefore(clock.instant())
//                  .map(cutoff -> invoiceRepository.countOpenDueBefore(customer.id(), cutoff))
//                  .orElse(0L);
```
Why: the one cutoff rule lives on the type, so both callers lose their branch instead of each switching on it.

Evidence: `DataRetentionJob.java:69-74` + `DataErasureController.java:117-122` @dffd26e5^1 (Bad, real; fixed by #349) · source 56b-g9b-good-bad-shape-spring.md:21-66 · fix from 56b:45-62

### DS3 — No one-off `if` or second boolean in a flow; model the case

**Bad** (neutral)
```java
private void recordPaymentSafely(PaymentIds ids, GatewayExchange exchange, PaymentStatus status,
                                 boolean requiresReview, UUID reviewId,
                                 boolean sandbox, String sandboxSource) {
```
What goes wrong: sandbox mode arrived as a boolean plus a string that only means something when it is true; review repeats that shape.

**Good** (neutral)
```java
sealed interface GatewayRun {
    record Live() implements GatewayRun {}
    record Sandbox(SandboxSource source) implements GatewayRun {}
}

sealed interface ReviewGate {
    record NotRequired() implements ReviewGate {}
    record Required(UUID reviewId) implements ReviewGate {}
}

record PaymentAttempt(PaymentIds ids, PaymentMethod method, GatewayExchange exchange, PaymentStatus status,
                      ReviewGate review, GatewayRun run) {
}

private void recordPaymentAttempt(final PaymentAttempt attempt) {
```
Why: each mode is a sealed case carrying only its own data, so a sandbox source or review id cannot exist without its mode.

Evidence: `ChatOrchestrator.java:201-206` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:68-105 · fix from 56b:84-101

### DS4 — Remove pass-throughs and single-caller wrappers; apply the deletion test

**Bad** (neutral)
```java
public List<Invoice> findDueReminders() {
    return invoiceRepository.findDueReminders();
}

public boolean claimAndAdvance(UUID invoiceId, Instant expectedNextReminderAt, Instant newNextReminderAt) {
    return invoiceRepository.claimAndAdvance(invoiceId, expectedNextReminderAt, newNextReminderAt);
}
```
What goes wrong: two one-line forwards in InvoiceService whose only caller is OverdueReminder add a layer to trace and hide nothing.

**Good** (neutral)
```java
@Component
class OverdueReminder {

    private final InvoiceRepository invoices;
    // … other collaborators unchanged

    ReminderOutcome remind(final Invoice invoice, final ClaimWindow window) {
        return switch (invoices.claimAndAdvance(invoice.id(), window)) {
            case ReminderClaim.Won _ -> send(invoice);
            case ReminderClaim.Lost _ -> ReminderOutcome.NOT_CLAIMED;
        };
    }
}
```
Why: the job depends on the port that does the work; the forwarders are deleted and the claim returns a sealed Won or Lost.

Evidence: `TriggerService.java:135-147` @772736bf (Bad, real; caller `ScheduledTriggerJob.java:83,127`) · source 56b-g9b-good-bad-shape-spring.md:107-150 · fix from 56b:129-144

### DS8 — No null check or try/catch to silence a failure on a trusted path

**Bad** (neutral)
```java
private void applyInvoicing(ImportOrdersRequest request, List<Order> created, UUID createdBy) {
    InvoiceDestination destination = request.invoicing();
    if (destination == null || invoiceService == null) {
        return;
    }
```
What goes wrong: `invoiceService` is a constructor-injected final field that a test-only constructor sets to null, so the trusted path grows a null guard, and a wiring mistake silently skips invoicing.

**Good** (neutral)
```java
OrderImporter(final OrderRepository orderRepository,
              final TaxCalculator taxCalculator,
              final ObjectMapper mapper,
              final InvoiceService invoiceService,
              final DiscountPolicy discountPolicy) {
    // … assignments unchanged; the back-compat constructor is deleted
}

private void applyInvoicing(final InvoiceTarget placement, final List<UUID> orderIds, final UUID createdBy) {
    switch (placement) {
        case InvoiceTarget.None _ -> { }
        case InvoiceTarget.New target -> invoiceService.create(target.toRequest(orderIds), createdBy);
        case InvoiceTarget.Existing target -> orderIds.forEach(orderId -> invoiceService.attach(target.id(), orderId));
    }
}
```
Why: one constructor and an injected final collaborator mean no null guard; the request decodes to a sealed target at the boundary.

Evidence: `OpenApiSpecImporter.java:86-90,197-199` @772736bf (Bad, real; only user `OpenApiSpecImporterTest.java:177`) · source 56b-g9b-good-bad-shape-spring.md:152-193 · fix from 56b:171-188

### DS12 — A rule-encoding predicate or literal is defined once, called everywhere

**Bad** (neutral)
```ts
const smokeOrders = orders.filter(order => order.reference?.startsWith('smoke-') || order.reference?.startsWith('rate-limit-smoke-'));
const staleInvoices = invoices.filter(invoice => invoice.reference.startsWith('smoke-'));
const smoke = customers.filter(customer => (customer.email ?? '').startsWith('smoke-') || (customer.name ?? '').startsWith('smoke-'));
```
What goes wrong: "what counts as smoke data" lives in three lambdas that already disagree, so numbered prefixes like `smoke77-` leak every run.

**Good** (neutral)
```ts
// playwright/support/smoke-name.ts
const SMOKE_NAME = /^(rate-limit-)?smoke\d*[-_]/;

export function isSmokeName(name: string | null | undefined): boolean {
  return SMOKE_NAME.test(name ?? '');
}

// playwright/global-setup.ts — every purge site calls the one predicate
const smokeOrders = orders.filter((order) => isSmokeName(order.reference));
const smokeInvoices = invoices.filter((invoice) => isSmokeName(invoice.reference));
const smokeCustomers = customers.filter(
  (customer) => isSmokeName(customer.email) || isSmokeName(customer.name),
);
```
Why: the rule has one home, so a new prefix is one edit and every purge site learns it.

Evidence: `aruvii-ui/playwright/global-setup.ts:52,85,100,117` @8f7bf163 (Bad, real; fixed by #636) · source 56b-g9b-good-bad-shape-spring.md:195-227 · fix from 56b:208-224

### DS14 — Do not extract a helper for 2–3 similar lines with no shared rule

**Bad** (neutral)
```java
static RestClient restClient(final String kind, final Duration timeout, final String baseUrl) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    if ("tax".equals(kind)) {
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);
        return RestClient.builder().requestFactory(requestFactory).build();
    }
    requestFactory.setConnectTimeout(Duration.ofSeconds(1));
    requestFactory.setReadTimeout(timeout);
    return RestClient.builder().baseUrl(baseUrl).requestFactory(requestFactory).build();
}
```
What goes wrong: one "shared" factory serves two callers that share no rule, so it needs a mode argument at once and grows one per caller.

**Good** (neutral)
```java
// TaxRateClient — its own setting, its own policy
static RestClient restClient(final TaxServiceProperties tax) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(tax.timeout());
    requestFactory.setReadTimeout(tax.timeout());
    return RestClient.builder().requestFactory(requestFactory).build();
}

// PaymentGatewayClient — looks alike, answers to a different setting
static RestClient restClient(final PaymentGatewayProperties gateway) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(gateway.connectTimeout());
    requestFactory.setReadTimeout(gateway.chargeTimeout());
    return RestClient.builder().baseUrl(gateway.baseUrl().toString()).requestFactory(requestFactory).build();
}
```
Why: the two builders stay apart because each timeout belongs to its own settings record and changes for a different reason.

Evidence: no Bad in Aruvii code @772736bf; both sides adapted from https://refactoring.com/catalog/removeFlagArgument.html:137-146 (Bad) and :170-171 (Good), placed on `CustomPiiEndpointClient.java:46-51` + `LlmFakeGenerator.java:42-45` · source 56b-g9b-good-bad-shape-spring.md:229-274 · fix from 56b:253-270

### MS6 — Answer "runs twice / crashed halfway"; reconcile when leftovers matter

**Bad** (neutral)
```java
@Override
@Transactional
public CancelOutcome cancel(final UUID orderId, final UUID requestedBy, final String reason) {

    final Optional<OrderCancellation> completed = cancellationPort.findCompletedByOrderId(orderId);
    if (completed.isPresent()) {
        return new CancelOutcome.AlreadyCancelled(completed.orElseThrow());
    }
    … // PENDING cancellation row, audit row, void the invoice, order CANCELLED, row COMPLETED
    } catch (RuntimeException failure) {
        log.error("order_cancel FAILED orderId={} cancellationId={}: {}: {}", …, failure);
        cancellationEntity.setStatus(CancellationStatus.FAILED);
        cancellationRepository.save(cancellationEntity);
        throw failure;
    }
```
What goes wrong: two concurrent cancels both pass the check-then-act guard, and the FAILED row is rolled back with the transaction it lives in.

**Good** (neutral)
```java
@Override
@Transactional
public CancelOutcome cancel(final CancelRequest request) {
    lockOrder(request.orderId());
    return cancellationPort.findCompletedByOrderId(request.orderId())
            .<CancelOutcome>map(CancelOutcome.AlreadyCancelled::new)
            .orElseGet(() -> cancelLocked(request));
}

private void lockOrder(final UUID orderId) {
    jdbc.queryForObject("SELECT id FROM orders WHERE id = ? FOR UPDATE", UUID.class, orderId);
}
```
Why: the row lock makes a second run wait and then see COMPLETED; one transaction means a crash leaves nothing to reconcile.

Evidence: `UserErasureAdapter.java:56-63,163-170` @772736bf (Bad, real; lead found by reading, no incident) · source 56b-g9b-good-bad-shape-spring.md:276-321 · fix from 56b:302-316

### LG2 — Log a failure once, where it is handled

**Bad** (neutral)
```java
try {
    final Invoice updated = new Invoice(
            … // the merged fields, ending in Instant.now()
    );
    final Invoice saved = invoiceRepository.save(updated);
    log.info("InvoiceService.reschedule complete invoiceId={}", saved.id());
    return toView(saved);
} catch (Exception e) {
    log.warn("InvoiceService.reschedule failed: {} {}", e.getClass().getSimpleName(), e.getMessage());
    throw e;
}
```
What goes wrong: the service logs and rethrows, then the global exception handler logs the same failure again, so one failure is two lines.

**Good** (neutral)
```java
final Invoice updated = new Invoice(
        … // the merged fields as before
        clock.instant());
final Invoice saved = invoiceRepository.save(updated);
log.info("action=invoice.reschedule invoiceId={}", saved.id());
return toView(saved);
```
Why: with no `try`, the exception travels to the one handler that handles it and logs it once.

Evidence: `NotificationConfigService.java:114,137-143` @772736bf (Bad, real; second log `GlobalExceptionHandler.java:179-183`) · source 56b-g9b-good-bad-shape-spring.md:323-354 · fix from 56b:343-351

### LG3 — WARN = handled, class and message, no stack; ERROR = investigate, throwable last

**Bad** (neutral)
```java
private void sendOrClose(SseEmitter emitter, OrderStatusEvent event) {
    try {
        … // send; IllegalStateException and IOException handled at DEBUG
    } catch (Exception e) {
        log.warn("Unexpected order-status stream failure: {}", e.toString(), e);
        emitter.completeWithError(e);
    }
}
```
What goes wrong: "unexpected" means someone must look, yet it logs at WARN, and passing `e` last prints a stack at WARN.

**Good** (neutral)
```java
    } catch (RuntimeException e) {
        // Must not fail: runs inside the OrderStatusSubscriber callback shared by every open stream (ER4).
        log.error("action=sse.send outcome=failed orderId={} event={}", orderId, eventName(event), e);
        emitter.completeWithError(e);
    }
```
Why: an unexpected failure is ERROR with the throwable last, so its stack prints once; the catch names its boundary.

Evidence: `SessionMessageController.java:302-303,318-321` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:356-385 · fix from 56b:372-379

### LY6 — One constructor; an optional collaborator is an `ObjectProvider<T>` resolved at use

**Bad** (neutral)
```java
@Bean
public OverdueReminder overdueReminder(
        InvoiceRepository invoiceRepository,
        ObjectProvider<EmailSender> emailSenderProvider) {
    EmailSender emailSender = emailSenderProvider.getIfAvailable(
            () -> email -> { throw new UnsupportedOperationException("EmailSender not available in this context"); });
    return new OverdueReminder(invoiceRepository, emailSender);
}
```
What goes wrong: the provider is resolved while the bean is built, so in orders-api (no EmailSender) it bakes in a throwing stub at startup.

**Good** (neutral)
```java
@Bean
OverdueReminder overdueReminder(final InvoiceRepository invoiceRepository,
                                final ObjectProvider<EmailSender> emailSenders) {
    return new OverdueReminder(invoiceRepository, emailSenders);
}

// OverdueReminder — resolved where a reminder is sent
private void send(final ReminderEmail email) {
    emailSenders.getObject().send(email);
}
```
Why: the bean holds the provider and resolves it per send, so a missing EmailSender fails at that call, naming the type.

Evidence: `AgentsAutoConfiguration.java:142-149` @772736bf (Bad, real; resolved use `PipelineExecutionService.java:27-31,56`) · source 56b-g9b-good-bad-shape-spring.md:391-425 · fix from 56b:408-420

### LY7 — Grouped settings in one validated record; each key bound in one place

**Bad** (neutral)
```java
// orders-api — CheckoutFraudClient
public CheckoutFraudClient(
        @Value("${example.fraud-check.base-url}") String baseUrl,
        @Value("${example.fraud-check.ruleset:default}") String ruleset,
        @Value("${example.fraud-check.timeout:5s}") Duration timeout) {
// billing — PaymentFraudClient
public PaymentFraudClient(
        @Value("${example.fraud-check.base-url}") String baseUrl,
        @Value("${example.fraud-check.ruleset:default}") String ruleset,
        @Value("${example.fraud-check.timeout:1500ms}") Duration timeout) {
```
What goes wrong: one key has two defaults, 5000 and 1500 ms, so unset, the two modules run "the same" setting differently.

**Good** (neutral)
```java
@Validated
@ConfigurationProperties("example.fraud-check")
public record FraudCheckProperties(@NotNull URI baseUrl,
                                   @NotBlank String ruleset,
                                   @NotNull Duration connectTimeout,
                                   @NotNull Duration checkoutTimeout,
                                   @NotNull Duration paymentTimeout) {
}

public CheckoutFraudClient(final FraudCheckProperties fraudCheck) {
    this.http = restClient(fraudCheck.baseUrl(), fraudCheck.connectTimeout(), fraudCheck.checkoutTimeout());
}
```
Why: one record is bound once and read by both clients; two real timeouts are two named keys, not one key with two defaults.

Evidence: `AdminActivityClient.java:43-46` + `OllamaActivityClient.java:42-45` @772736bf (Bad, real; third reader `LlmFakeGenerator.java:38-39`) · source 56b-g9b-good-bad-shape-spring.md:427-467 · fix from 56b:447-462

### SC6 — A `@Bean` method returns the most specific type it builds

**Bad** (neutral)
```java
@Bean
public OrderRepository orderRepository(OrderJpaRepository jpaRepository) {
    return new OrderRepositoryAdapter(jpaRepository);
}
```
What goes wrong: the method builds the adapter but declares the port, so before creation the container and type conditions see only the port.

**Good** (neutral)
```java
@Bean
OrderRepositoryAdapter orderRepository(final OrderJpaRepository jpaRepository) {
    return new OrderRepositoryAdapter(jpaRepository);
}
```
Why: the declared type is what is built; callers still inject `OrderRepository`, because Spring matches every type the bean has.

Evidence: `AgentsAutoConfiguration.java:52-55` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:469-492 · fix from 56b:482-488

### SC7 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup

**Bad** (neutral)
```java
@Bean
@ConditionalOnMissingBean(TaxCalculator.class)
public TaxCalculator taxCalculator(TaxProperties tax) {
    Path ratesPath = Path.of(tax.rateTable().ratesPath());
    Path regionsPath = Path.of(tax.rateTable().regionsPath());
    if (Files.exists(ratesPath) && Files.exists(regionsPath)) {
        … // load RateTableTaxCalculator
        } catch (Exception failure) {
            log.warn("rate table init failed ({}: {}), falling back to a flat rate",
                    failure.getClass().getSimpleName(), failure.getMessage());
        }
    } … // else: WARN "using flat-rate tax"
    return new FlatRateTaxCalculator();
}
```
What goes wrong: a file's existence picks between two real implementations, any failure falls back silently, and the stub depends on load order.

**Good** (neutral)
```java
@Bean
@ConditionalOnProperty(name = "example.tax.mode", havingValue = "rate-table", matchIfMissing = false)
RateTableTaxCalculator rateTableTax(final TaxProperties tax) {
    return RateTableTaxCalculator.load(tax.rateTable().ratesPath(), tax.rateTable().regionsPath());
}

@Bean
@ConditionalOnProperty(name = "example.tax.mode", havingValue = "flat", matchIfMissing = false)
FlatRateTaxCalculator flatRateTax() {
    log.warn("action=tax.mode mode=flat accuracy=low key=example.tax.mode");
    return new FlatRateTaxCalculator();
}

@Validated @ConfigurationProperties("example.tax")
record TaxProperties(@NotNull TaxMode mode, @Valid RateTableFiles rateTable) {}
```
Why: each implementation carries its own value, exactly one matches, and an unset mode fails startup naming the key.

Evidence: `ToolsAutoConfiguration.java:220-227,234-242` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:494-544 · fix from 56b:520-537

### SC15 — A settings record rejects bad values at startup, naming the key; a runner spec proves it

**Bad** (neutral)
```java
@ConfigurationProperties(prefix = "example.notifications.streams")
public record NotificationStreamsProperties(Stream ordersPlaced,
                                            Stream invoicesOverdue,
                                            Stream paymentsReceived,
                                            Duration drainTimeout) {

    public NotificationStreamsProperties {
        if (drainTimeout.isZero() || drainTimeout.isNegative()) {
            throw new IllegalArgumentException(PREFIX + "drain-timeout must be more than zero, but was " + …);
        }
        for (final NotificationStream stream : NotificationStream.values()) {
            requireCap(capOf(stream, ordersPlaced, invoicesOverdue, paymentsReceived), stream);
        }
    }
```
What goes wrong: a wrong value is rejected, but a missing one makes the constructor dereference null: a bare NullPointerException naming no key.

**Good** (neutral)
```java
@Validated
@ConfigurationProperties("example.notifications.streams")
public record NotificationStreamsProperties(@NotNull @Valid Stream ordersPlaced,
                                            @NotNull @Valid Stream invoicesOverdue,
                                            @NotNull @Valid Stream paymentsReceived,
                                            @NotNull @DurationMin(millis = 1) Duration drainTimeout) {

    public record Stream(@Min(1) int maxInFlight) {
    }
}
```
Why: each field carries its own constraint, so Boot's bind-validation failure names the property; the runner spec adds the missing case.

Evidence: `WorkerStreamsProperties.java:17-35` @772736bf (Bad, real; spec `WorkerStreamsStartupSpec.groovy:43-49`) · source 56b-g9b-good-bad-shape-spring.md:546-592 · fix from 56b:572-585

### SC16 — No default for a secret or required endpoint; fail, or a named degraded mode at WARN

**Bad** (neutral)
```java
@Bean
public CredentialEncryptor credentialEncryptor(@Value("${example.master-key:}") String masterKey) {
    return new CredentialEncryptor(masterKey);
}
// CredentialEncryptor
public CredentialEncryptor(String secretKey) {
    if (secretKey == null || secretKey.isBlank()) {
        this.keyBytes    = null;
        this.passthrough = true;
        return;
    }
```
```yaml
example:
  master-key: ${EXAMPLE_MASTER_KEY:${master_key:}}
```
What goes wrong: a missing master key defaults to `""` twice, which silently stores every PaymentGateway credential in plaintext, with no failure or log.

**Good** (neutral)
```java
@Bean
CredentialEncryptor credentialEncryptor(final Environment environment, final CredentialProperties credentials) {
    return Optional.ofNullable(environment.getProperty("example.master-key"))
            .filter(not(String::isBlank))
            .<CredentialEncryptor>map(AesGcmCredentialEncryptor::new)
            .orElseGet(() -> plaintextIfAllowed(credentials));
}

private static CredentialEncryptor plaintextIfAllowed(final CredentialProperties credentials) {
    if (!credentials.plaintextAllowed()) {
        throw new InvalidConfigurationPropertyValueException("example.master-key", "", "required for credentials");
    }
    log.warn("action=credentials.mode mode=plaintext key=example.credentials.plaintext-allowed");
    return new PlaintextCredentialEncryptor();
}
```
Why: absence fails startup naming the key; plaintext is only a named mode, set outside the shipped yml, that warns once.

Evidence: `ProvidersAutoConfiguration.java:31-33` + `CredentialEncryptor.java:21-26` + `application.yml:104` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:594-643 · fix from 56b:619-636

### SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a thread from ready

**Bad** (neutral)
```java
@Service
public class TaxRateTable implements TaxCalculator {
    …
    @PostConstruct
    void initialise() {
        reload();
    }
```
What goes wrong: `reload()` reads every tax rate row while the bean is created, so a database outage fails startup inside unrelated bean construction.

**Good** (neutral)
```java
@Service
public class TaxRateTable implements TaxCalculator, ApplicationRunner {
    … // fields and the one constructor unchanged

    @Override
    public void run(final ApplicationArguments arguments) {
        reload();
    }
```
Why: rates must be loaded before any order is priced, and a runner finishes after context refresh but before the app accepts traffic.

Evidence: `GlobalTrustStore.java:37-39,56-59` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:645-679 · fix from 56b:663-673

### SC21 — A proxied annotation works only on a call from another bean; never through `this`

**Bad** (neutral)
```java
@Transactional
public String getOrGenerateWebhookSecret() {
    String stored = settings.get(KEY_WEBHOOK_SECRET);
    if (!stored.isBlank()) {
        return decryptSafe(stored);
    }
    String generated = generateSecureKey();
    settings.set(KEY_WEBHOOK_SECRET, encryptor.encrypt(generated));
    return generated;
}

/** WebhookSecretPort implementation — env var takes precedence over DB. */
@Override
public String getEffectiveWebhookSecret() {
    String fromEnvironment = environment.getProperty("example.webhook-secret");
    if (fromEnvironment != null && !fromEnvironment.isBlank()) {
        return fromEnvironment;
    }
    return getOrGenerateWebhookSecret();
```
What goes wrong: the port method reaches the `@Transactional` method through `this`, so the proxy is bypassed and the read-then-write has no transaction.

**Good** (neutral)
```java
@Component
class WebhookSecretStore {
    … // one constructor: BillingSettingsPort settings, CredentialEncryptor encryptor
    @Transactional
    String loadOrCreate() {
        final String stored = settings.get(KEY_WEBHOOK_SECRET);
        return stored.isBlank() ? create() : decryptSafe(stored);
    }
}
// BillingSettingsService implements WebhookSecretPort
@Override
public String loadOrCreateWebhookSecret() {
    return Optional.ofNullable(environment.getProperty("example.webhook-secret"))
            .filter(not(String::isBlank))
            .orElseGet(webhookSecretStore::loadOrCreate);
```
Why: the transactional method lives on a second bean, so the call crosses the proxy, with no self-injection and no `AopContext`.

Evidence: `SetupService.java:165-180` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:681-728 · fix from 56b:706-723

### NGB3 — State in `signal()`, derived state in `computed()`; `effect()` never copies

**Bad** (neutral)
```ts
customerId = '';
allInvoices = signal<InvoiceResponse[]>([]);
customerInvoices = signal<InvoiceResponse[]>([]);
…
        this.customerId = payment.customerId;
        this.filterInvoices(payment.customerId);
…
onCustomerChange(customerId: string) {
  this.filterInvoices(customerId);
  this.allocations.update((allocations) => allocations.map((allocation) => ({ ...allocation, invoiceId: '' })));
}

private filterInvoices(customerId: string) {
  this.customerInvoices.set(this.allInvoices().filter((invoice) => invoice.customerId === customerId && invoice.status === 'OPEN'));
}
```
What goes wrong: the open-invoice list is a hand-synced copy; if the payment loads before the invoices, it filters an empty list and stays empty.

**Good** (neutral)
```ts
readonly customerId = signal('');
readonly allInvoices = signal<InvoiceResponse[]>([]);
readonly customerInvoices = computed(() =>
  this.allInvoices().filter(
    (invoice) => invoice.customerId === this.customerId() && invoice.status === 'OPEN',
  ),
);
// on load: this.customerId.set(payment.customerId);  — nothing to re-filter

onCustomerChange(customerId: string): void {
  this.customerId.set(customerId);
  this.allocations.update((allocations) =>
    allocations.map((allocation) => ({ ...allocation, invoiceId: '' })),
  );
}
```
Why: the filtered list is derived from both signals, so it is right whichever request lands first, and `filterInvoices` is deleted.

Evidence: `aruvii-ui/src/app/features/pipelines/pipeline-builder.component.ts:222,225-226,242-243,258-265` @772736bf (Bad, real) · source 56b-g9b-good-bad-shape-spring.md:730-773 · fix from 56b:755-769

### AP3a — A role rule is proven by a caller × endpoint matrix IT

**Bad** (neutral)
```java
@Test
@DisplayName("PATCH /api/orders/{id} updates the delivery note")
void updateOrder_changesNote() {
    final String id = createOrderAs(adminToken);
    http.patch().uri("/api/orders/" + id)
            .header(HttpHeaders.AUTHORIZATION, adminToken)
            .contentType(MediaType.APPLICATION_JSON)
            .body("""{ "deliveryNote": "Leave at the door" }""")
            .exchange()
            .expectStatus().isOk();
}
```
What goes wrong: the endpoint is guarded by role, yet the only caller ever sent is the admin, so another customer editing this order is never tried.

**Good** (neutral)
```groovy
def "should answer #caller with #expected when it edits an order of customer A"() {
    given: "an order of customer A, and the caller signed in through the real filter chain"
    def order = orderOf(CUSTOMER_A)
    when: "the caller changes its delivery note"
    def status = patchAs(bearerFor(caller), "/api/orders/${order.id()}", [deliveryNote: "Leave at the door"])
    then: "the status is the matrix's, and a refusal left the order as it was"
    status == expected
    expected == 200 || orderRepository.findById(order.id()).get() == order
    where:
    caller        || expected
    ANONYMOUS     || 401
    CUSTOMER_A    || 200
    CUSTOMER_B    || 403
    API_KEY_OF_B  || 403
}
```
Why: every caller kind gets a row; CUSTOMER_B holds the same role as CUSTOMER_A, so only this row catches an ownership hole.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/ToolControllerIT.java:328-354` @772736bf (Bad, real; `adminToken` at :49-53) · source 56c-g9b-good-bad-api-security.md:20-64 · fix from 56c:42-58

### AP4a — A `PUBLIC_PATHS` entry has an IT proving its replacement check refuses; no secret in a URL

**Bad** (neutral)
```java
@Test
@DisplayName("POST /api/setup/complete → sets setupComplete to true")
void shouldSetSetupCompleteOnComplete() {
    // given / when / then
    http.post().uri("/api/setup/complete")
        .exchange()
        .expectStatus().isOk()
        .expectBody()
        .jsonPath("$.data.setupComplete").isEqualTo(true);
}
```
What goes wrong: the path needs no token, and the only IT is the happy path, so nobody sees that the "setup not done yet" check is missing.

**Good** (neutral)
```groovy
def "should refuse an anonymous caller who completes setup on a completed install"() {
    given: "an install whose setup is already complete"
    completeSetup()

    when: "a caller with no token posts to the public complete endpoint"
    def reply = http.post().uri("/api/setup/complete").exchange()

    then: "the check that replaces the token refuses it"
    reply.expectStatus().isBadRequest()
        .expectBody()
        .jsonPath('$.success').isEqualTo(false)
        .jsonPath('$.code').isNotEmpty()
}
```
Why: the IT sends the caller the public path lets in and proves the replacement check refuses it.

Evidence: `aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:271-280` @772736bf (Bad, real; unguarded `SetupController.java:140-144`) · source 56c:68-108 · fix from 56c:87-101

### TT2 — Read a request's required arguments off its handler; the schema is never stricter

**Bad** (neutral)
```java
@Override
public RequestContract sendInvoiceContract() {
    return new RequestContract.Declared("""
        {"type":"object",
         "properties":{
           "to":{"type":"string"},
           "subject":{"type":"string"},
           "message":{"type":"string"}},
         "required":["to","subject","message"]}
        """);
}
```
What goes wrong: written from what an email "obviously" needs; the handler takes a list of recipients and no message, so working calls are refused.

**Good** (neutral)
```java
@Override
public RequestContract sendInvoiceContract() {
    return new RequestContract.Declared("""
        {"type":"object",
         "properties":{
           "to":{"anyOf":[{"type":"string"},{"type":"array","items":{"type":"string"}}]},
           "subject":{"type":"string","description":"Must not be empty."},
           "message":{"type":"string","description":"Sent empty if omitted."}},
         "required":["to","subject"]}
        """);
}
```
Why: `to` takes what the handler takes, and `required` lists exactly what the handler refuses without.

Evidence: no Bad in our code (both sides adapted) · handler facts `EmailToolHandler.java:116-127` @772736bf; counterexample in prose `CLAUDE.md:423-427` @772736bf · source 56c:110-151 · fix from pstack `principle-type-system-discipline/SKILL.md:21`

### SE1 — A URL not in code is fetched only through the checked fetch

**Bad** (neutral)
```java
private RefundReply requestRefund(final GatewayDiscovery discovery, final RefundRequest request) {
    final RefundReply reply = restClient.post()
            .uri(discovery.refundEndpoint())
            .contentType(MediaType.APPLICATION_JSON)
            .header("X-Api-Secret", gatewaySecret)
            .body(request)
            .retrieve()
            .body(RefundReply.class);
    return reply;
}
```
What goes wrong: the discovery document was fetched through the URL check, but the endpoint it returned is called unchecked, carrying the secret.

**Good** (neutral)
```java
private RefundReply requestRefund(final GatewayDiscovery discovery, final RefundRequest request) {
    final CheckedUrl refundEndpoint = switch (urlGuard.check(discovery.refundEndpoint())) {
        case UrlDecision.Blocked blocked -> throw new OrderException(
                ErrorCode.GATEWAY_URL_BLOCKED,
                blocked.host());
        case UrlDecision.Permitted permitted -> permitted.target();
    };
    return noRedirectRestClient.post()
            .uri(refundEndpoint.value())
            .contentType(MediaType.APPLICATION_JSON)
            .header("X-Api-Secret", gatewaySecret)
            .body(request)
            .retrieve()
            .body(RefundReply.class);
}
```
Why: every URL the remote side names passes the same check, on a client with redirects off.

Evidence: `aruvii-api/src/main/java/ai/aruvii/api/controller/OidcController.java:163-183` @772736bf (Bad, real; discovery checked at `OidcSettingsService.java:91-102`) · source 56c:153-202 · fix from 56c:179-195

### SE4 — Resolve a user-supplied path with `toRealPath()`, then check `startsWith(base)`

**Bad** (neutral)
```java
public Path locate(final Path basePath, final String relativePath) {
    if (relativePath.contains("..")) {
        throw new OrderException(ErrorCode.PDF_PATH_BLOCKED, relativePath);
    }
    final Path base = basePath.toAbsolutePath().normalize();
    final Path resolved = base.resolve(relativePath).normalize();
    if (!resolved.startsWith(base)) {
        throw new OrderException(ErrorCode.PDF_PATH_BLOCKED, relativePath);
    }
    return resolved;
}
```
What goes wrong: both checks are lexical; a symlink inside the base that points at `/etc` passes them.

**Good** (neutral)
```java
PathCheck resolveInside(final Path realBase, final String requested) {
    final Path candidate = realBase.resolve(requested).normalize();
    if (!candidate.startsWith(realBase)) {
        return new PathCheck.Outside();
    }
    try {
        final Path real = candidate.toRealPath();
        return real.startsWith(realBase) ? new PathCheck.Inside(real) : new PathCheck.Outside();
    } catch (final IOException missingOrUnreadable) {
        return new PathCheck.NotFound();
    }
}
```
Why: the deciding check runs on the real path with symlinks followed, and the caller opens exactly the path that was checked.

Evidence: `aruvii-tools/src/main/java/ai/aruvii/tools/infrastructure/handlers/FileToolHandler.java:50-63` @772736bf (Bad, real) · source 56c:204-249 · fix from 56c:228-242 · added ErrorCode `PDF_PATH_BLOCKED`

### SE5 — Untrusted JSON binds to a fixed record; no `Map<String,Object>` past the adapter

**Bad** (neutral)
```java
final Map<String, Object> body = noRedirectRestClient.get()
        .uri(checked.value())
        .retrieve()
        .body(Map.class);
if (body == null) {
    throw new IllegalStateException("Empty gateway discovery from " + checked.value());
}
return new GatewayDiscovery(
        (String) body.get("charge_endpoint"),
        (String) body.get("refund_endpoint"));
// …
public record GatewayDiscovery(String chargeEndpoint, String refundEndpoint) {}
```
What goes wrong: a typed record exists, yet the reply is cast field by field; a missing key becomes a `null` URL that fails three calls later.

**Good** (neutral)
```java
final GatewayDiscovery discovery = noRedirectRestClient.get()
        .uri(checked.value())
        .retrieve()
        .body(GatewayDiscovery.class);
return Optional.ofNullable(discovery)
        .orElseThrow(() -> new OrderException(ErrorCode.GATEWAY_DISCOVERY_FAILED));
// …
public record GatewayDiscovery(
        @JsonProperty("charge_endpoint") String chargeEndpoint,
        @JsonProperty("refund_endpoint") String refundEndpoint) {
    public GatewayDiscovery {
        requireUrls(chargeEndpoint, refundEndpoint);
    }
}
```
Why: the reply binds straight to the record, and its constructor refuses a bad document at the boundary with one error.

Evidence: `aruvii-api/src/main/java/ai/aruvii/api/service/OidcSettingsService.java:105-114,121-123` @772736bf (Bad, real) · source 56c:251-297 · fix from 56c:275-291

### SS13 — A resource guard asks the ownership check; `hasRole` names platform roles only

**Bad** (neutral)
```java
@PatchMapping("/{id}")
@PreAuthorize("hasAnyRole('ADMIN','CLERK','CUSTOMER')")
public ApiResponse<OrderResponse> update(@PathVariable UUID id,
                                         @RequestBody UpdateOrderRequest req) {
    return ApiResponse.ok(orderService.update(id, req));
}

@DeleteMapping("/{id}")
@ResponseStatus(HttpStatus.NO_CONTENT)
@PreAuthorize("hasAnyRole('ADMIN','CUSTOMER')")
public void delete(@PathVariable UUID id) {
    orderService.delete(id);
}
```
What goes wrong: CUSTOMER says what the caller is, not whose order it is, so customer B may edit or delete customer A's order.

**Good** (neutral)
```java
@PatchMapping("/{id}")
@PreAuthorize("@orderAuth.canEdit(#id)")
public ApiResponse<OrderResponse> update(
        @PathVariable final UUID id,
        @RequestBody @Valid final UpdateOrderRequest request) {
    return ApiResponse.ok(orderService.update(id, request));
}

@DeleteMapping("/{id}")
@ResponseStatus(HttpStatus.NO_CONTENT)
@PreAuthorize("@orderAuth.canDelete(#id)")
public void delete(@PathVariable final UUID id) {
    orderService.delete(id);
}
```
Why: each guard asks about this order's owner; admins pass inside the check, so no role name is needed.

Evidence: `aruvii-api/src/main/java/ai/aruvii/api/controller/ToolController.java:69-81` @772736bf (Bad, real; unused `@wsAuth.canEditTool` at `WorkspaceAuthorization.java:97-103`) · source 56c:299-344 · fix from 56c:323-339

### SS21 — Passwords via `DelegatingPasswordEncoder`; machine secrets via HMAC-SHA-256; never the encoder per request

**Bad** (neutral)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
}
// ApiKeyService — runs on every request that carries an API key
ApiKeyEntity found = null;
if (rawKey != null && rawKey.startsWith("ok_")) {
    String prefix = rawKey.substring(0, Math.min(8, rawKey.length()));
    found = apiKeyRepository.findByKeyPrefix(prefix).stream()
        .filter(ApiKeyEntity::isValid)
        .filter(key -> passwordEncoder.matches(rawKey, key.getKeyHash()))
        .findFirst()
        .orElse(null);
}
```
What goes wrong: one slow password hash also checks API keys, so every API-key request pays a deliberately slow hash per candidate row.

**Good** (neutral)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}
// ApiKeyService
public Optional<ApiKeyEntity> authenticateKey(final ApiKeyCandidate candidate) {
    final byte[] presented = apiKeyMac.digest(candidate.rawKey());
    return apiKeyRepository.findByKeyPrefix(candidate.prefix()).stream()
            .filter(ApiKeyEntity::isValid)
            .filter(key -> MessageDigest.isEqual(presented, key.getKeyHmac()))
            .findFirst();
}
```
Why: passwords keep an adaptive hash; a random 128-bit key needs only a keyed HMAC, compared in constant time.

Evidence: `aruvii-auth/src/main/java/ai/aruvii/auth/infrastructure/AuthAutoConfiguration.java:16-19` + `aruvii-auth/src/main/java/ai/aruvii/auth/application/ApiKeyService.java:239-248` @772736bf (Bad, real) · source 56c:346-396 · fix from 56c:372-386
