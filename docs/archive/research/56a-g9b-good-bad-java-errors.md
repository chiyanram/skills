# 56a — G9b Good/Bad pairs: Java language + errors/comments/layers (#33, map #9)

Batches **G9b-GB1** (JV1 JV5 TY1 TY3 TY8 TY9 CC3 CC4 CC9) and **G9b-GB2** (ER1 ER4 ER8 ER10 CM3 CM4 CM7 LY1 LY2),
selected in `54-g9b-good-bad-selection.md`, written under `55-good-bad-v3-BRIEF.md` (GB2, SRC1, SEAM1).

- **Bad = our code**, agent-platform `origin/master` at **`772736bf`** (2026-10-03), cited `path:lines` (module and
  package prefix shortened to `…/` where the file name is unique).
- **Good = that Bad rewritten**, labelled `rewritten from path:lines`. Our code is never a Good as-is. Only when master
  has no Bad are both sides `adapted from <source:line>` (none needed in this file: every rule found a Bad).
- Every Good also obeys the approved rules in `19-approved-rules.md` (ST1/TY4 `final`, ST2, JV5, TY1, U4 `Clock`,
  NM1, LG1/LG3/LG8, CM3, SC1/LY6, ER2–ER4) and SEAM1 (S-1..S-7: one job, record in / sealed out, decide or do,
  exhaustive switch, earn the seam) plus the Fowler smells baseline (rameezk/skills
  `skills/code-review/martin-fowler-code-smells.md`). Names a Good introduces that master lacks are listed in its note.
- Every Good is **NEEDS COMPILE CHECK** (work item 1 compiles them).

---

## G9b-GB1 · Java language

### JV1 — Time is `Instant`/`Duration`; `Date`/zoned only at a library or display boundary

**Bad** (ours)
```java
long t0 = System.currentTimeMillis();
// …
AgentChatResponse resp;
try {
    resp = agentChatPort.chat(new AgentChatRequest(step.agentId(), null, resolvedInput, userId));
} catch (Exception e) {
    long ms = System.currentTimeMillis() - t0;
    // …
}
long ms = System.currentTimeMillis() - t0;
log.info("action=pipeline.step.ok pipelineId={} stepOrder={} agentId={} durationMs={}",
        pipelineId, step.stepOrder(), step.agentId(), ms);
```
`aruvii-agents/…/application/PipelineExecutionService.java:49,54-58,68,79-80` @ `772736bf` — elapsed time is raw `long`
subtraction read from the wall clock twice, so no test can pin it. also breaks: U4 (no `Clock`; `Instant.now()` at
`:41,63,74,83`), TY1 (`null` session id), ST1/TY4 (non-final locals), ST2 (wrapped log call), NM1 (`resp`, `ms`).

**Good** (rewritten from `PipelineExecutionService.java:49,54-58,68,79-80`) — NEEDS COMPILE CHECK
```java
final var stepStart = clock.instant();
final AgentChatResponse reply = agentChatPort.chat(stepRequest(step, resolvedInput, userId));
final var elapsed = Duration.between(stepStart, clock.instant());
log.info(
        "action=pipeline.step.ok pipelineId={} stepOrder={} agentId={} durationMs={}",
        pipelineId,
        step.stepOrder(),
        step.agentId(),
        elapsed.toMillis());
```
— the time is an `Instant` from an injected `Clock` (new constructor parameter), the span a `Duration`; it becomes a
`long` only where the log line and the `PipelineStepExecution.durationMs` column need a number. `stepRequest(…)` is new:
it builds the `AgentChatRequest` without the `null` session id. The step-failure `catch` keeps the same two lines.
Prevents the misreading "`long` millis is not `Date`, so it passes" — and the reverse: `Date.from(instant)` handed to
the JWT library is the allowed boundary, not a breach.

### JV5 — `final var` only when the right-hand side shows the type

**Bad** (ours)
```java
final var userId = principal != null ? tryParseUUID(principal.getName()) : null;
final var result = providerService.create(req, userId).orThrow(ErrorCode.PROVIDER_NAME_TAKEN);
audit.logProviderCreated(userId, result.id(), result.name(), servletReq.getRemoteAddr());
return ApiResponse.ok(result);
```
`aruvii-api/…/controller/ProviderController.java:58-61` @ `772736bf` — neither `create` nor `orThrow` tells the reader
the value is a `ProviderResponse`; `userId` hides that it may be `null`. also breaks: NM1 (`result`), TY1 (a `null`
user id reaches the audit row; `tryParseUUID` at `:197-199` swallows the parse error, ER3).

**Good** (rewritten from `ProviderController.java:55-61`) — NEEDS COMPILE CHECK
```java
public ApiResponse<ProviderResponse> create(
        @Valid @RequestBody final CreateProviderRequest req,
        final Principal principal,
        final HttpServletRequest servletReq) {
    final var userId = UUID.fromString(principal.getName());
    final ProviderResponse created = providerService.create(req, userId)
            .orThrow(ErrorCode.PROVIDER_NAME_TAKEN);
    audit.logProviderCreated(userId, created.id(), created.name(), servletReq.getRemoteAddr());
    return ApiResponse.ok(created);
}
```
— `UUID.fromString` is a factory, so `var` stays; `create(…).orThrow(…)` names actions, not a type, so the type is
written out. The principal is never `null` behind `@PreAuthorize`, and its name is the user UUID
(`JwtAuthentication.java:54-58`), so the `null` branch goes. Prevents the misreading "any method call shows the type".

### TY1 — No `null` decides a case; absence is `Optional`, a sealed type or an enum

**Bad** (ours)
```java
private NerPort tier2;

@Autowired(required = false)
void setTier2(NerPort tier2) { this.tier2 = tier2; }
// …
private Tier12 tier1And2(String input, boolean nerEnabled) {
    RedactionResult t1 = tier1.redact(InputNormaliser.normalise(input));
    // …
    if (nerEnabled && tier2 != null) {
        List<NerEntity> t2Entities = tier2.detectEntities(t1.redactedText());
        // … merge, return
    }
    return new Tier12(t1, List.of());
}
```
`aruvii-guardrails/…/application/GuardrailPipeline.java:35,43-44,113-114,123-124,132` @ `772736bf` — a `null` field and
a boolean together choose the redaction path; the third combination (flag on, no bean) silently skips NER.
also breaks: LY6/SC1 (setter `@Autowired(required=false)`), TY4 (non-final field), DS3 (a flag plus a `null` for one case).

**Good** (rewritten from `GuardrailPipeline.java:35,43-44,113-132`) — NEEDS COMPILE CHECK
```java
public enum NerMode { OFF, ON }

private final PiiRedactor tier1;
private final ObjectProvider<NerPort> tier2;

private Tier12 tier1And2(final String input, final NerMode nerMode) {
    final RedactionResult regexPass = tier1.redact(InputNormaliser.normalise(input));
    final List<NerEntity> nerEntities = switch (nerMode) {
        case OFF -> List.of();
        case ON -> tier2.getObject().detectEntities(regexPass.redactedText());
    };
    return withNerEntities(regexPass, nerEntities);
}
```
— the flag becomes an enum the switch must name; the optional bean is an `ObjectProvider` resolved at use (LY6), and
"ON but no NER bean" now fails loudly (`getObject()` throws) instead of skipping. `NerMode` and `withNerEntities`
(the old merge block) are new. Prevents the misreading "`!= null` on an optional collaborator is a guard, not a decision".

### TY3 — Sealed variants exclude forbidden combinations; the compact constructor checks only the rest

**Bad** (ours)
```java
if (req.pem() != null && !req.pem().isBlank()) {
    saved = service.addGlobalByPem(req.label(), req.pem(), req.notes(), userId);
} else if (req.uri() != null && req.sha256Fingerprint() != null) {
    saved = service.addGlobalByProbe(req.label(), parseUri(req.uri()), req.sha256Fingerprint(),
        req.notes(), userId);
} else {
    throw new IllegalArgumentException("Either 'pem' or both 'uri' + 'sha256Fingerprint' must be supplied");
}
```
`aruvii-api/…/controller/TrustedCertificateController.java:54-61` @ `772736bf`, over the record
`…/controller/dto/TrustedCertificateRequest.java:10-16` (three nullable fields) — every reader re-derives the two legal
shapes. also breaks: TY1 (`null` picks the path), LY1 (outcome branch in the controller), ER2 (`IllegalArgumentException`,
no `ErrorCode`), ST2 (wrapped call).

**Good** (rewritten from `TrustedCertificateRequest.java:10-16` + `TrustedCertificateController.java:54-61`) — NEEDS COMPILE CHECK
```java
@JsonTypeInfo(use = JsonTypeInfo.Id.DEDUCTION)
@JsonSubTypes({@JsonSubTypes.Type(Pem.class), @JsonSubTypes.Type(Probed.class)})
public sealed interface TrustedCertificateRequest {
    record Pem(
            @NotBlank @Size(max = 120) String label,
            @NotBlank String pem,
            @Size(max = 4000) String notes) implements TrustedCertificateRequest {}
    record Probed(
            @NotBlank @Size(max = 120) String label,
            @NotNull URI uri,
            @NotBlank String sha256Fingerprint,
            @Size(max = 4000) String notes) implements TrustedCertificateRequest {}
}
```
— "pem, or uri **and** fingerprint" is two records, so "uri without fingerprint" cannot be built. `DEDUCTION` picks the
record from the fields present, so the JSON on the wire is unchanged (`@JsonSubTypes` as in `shared/agents/Version.java:13-16`).
The controller becomes `service.addGlobal(req, userId)`, and the service switches over `Pem | Probed` with no `default`.
Nothing is left for a compact constructor: each record's fields are independent, and blanks are Bean Validation's job
at the boundary (ER6). Prevents the misreading "validate the either-or with `if/else`" — the type removes the combination.

### TY8 — Wrap a primitive when same-typed values could be swapped, or it carries an invariant

**Bad** (ours)
```java
public AgentTask submit(UUID agentId, UUID workspaceId, UUID sessionId,
                         String prompt, String callbackUrl, UUID userId) {
```
`aruvii-agents/…/application/TaskService.java:29-30` @ `772736bf` — four `UUID`s and two `String`s in one signature; any
two can be transposed at the caller (`AgentTaskController.java:99-100`) and the build stays green. No swap incident
found — the risk is the signature. also breaks: TY1 (`callbackUrl` is `null` when there is no callback), ST2 (wrapped,
not one parameter per line), TY4 (non-final parameters), U4 (`:31` `Instant.now()`).

**Good** (rewritten from `TaskService.java:29-30`) — NEEDS COMPILE CHECK
```java
public record AgentId(UUID value) {}
public record WorkspaceId(UUID value) {}
public record SessionId(UUID value) {}
public record UserId(UUID value) {}
public sealed interface CallbackTarget {
    record None() implements CallbackTarget {}
    record Url(URI uri) implements CallbackTarget {}
}
public AgentTask submit(
        final AgentId agentId,
        final WorkspaceId workspaceId,
        final SessionId sessionId,
        final UserId submittedBy,
        final String prompt,
        final CallbackTarget callback) {
```
— `submit(workspaceId, agentId, …)` no longer compiles, and `prompt`/`callback` can no longer trade places. The id
records check nothing: the reason to wrap is the swap, not an invariant. All five types are new (none exist on master).
Prevents both misreadings: "wrap every id everywhere" (only where same-typed values meet one call) and "wrap only when
there is an invariant" (X4).

### TY9 — Strengthen a type only where partiality shows (a cast, a null check, a "never happens" throw)

**Bad** (ours)
```java
private int appendBetween(final List<String> whereParts,
                            final List<String> paramOrder,
                            final Map<String, Object> paramValues,
                            final int index,
                            final String quotedCol,
                            final Object value) {
    if (!(value instanceof List<?> bounds) || bounds.size() != 2) {
        throw new IllegalArgumentException(
            "BETWEEN operator on " + quotedCol + " requires a 2-tuple value");
    }
    // … two placeholder names, the BETWEEN fragment …
    paramValues.put(lo, bounds.get(0));
    paramValues.put(hi, bounds.get(1));
    return index + 2;
}
```
`aruvii-tools/…/infrastructure/compiler/PickerCompiler.java:260-277` @ `772736bf` — the `instanceof` + size check and
`get(0)`/`get(1)` are partiality: an `Object` is standing in for "two bounds". also breaks: ER2
(`IllegalArgumentException`, no `ErrorCode`), smell *Data Clumps* (`whereParts`, `paramOrder`, `paramValues` travel
together through every `append*`, `:209-217`), ST2 (parameters aligned, not indented once).

**Good** (rewritten from `PickerCompiler.java:260-277`) — NEEDS COMPILE CHECK
```java
record BetweenBounds(Object low, Object high) {}

private int appendBetween(
        final WhereClause where,
        final int index,
        final String quotedCol,
        final BetweenBounds bounds) {
    final String lowParam = FILTER_PARAM_PREFIX + index;
    final String highParam = FILTER_PARAM_PREFIX + (index + 1);
    where.add(quotedCol + " BETWEEN :" + lowParam + " AND :" + highParam);
    where.bind(lowParam, bounds.low());
    where.bind(highParam, bounds.high());
    return index + 2;
}
```
— the check moves up to where the filter is parsed (TY12 boundary), which builds `BetweenBounds` once; here the
`get(0)` has nothing left to guard. `WhereClause` (new) holds the three lists that always travelled together. And the
strengthening stops: `appendIn` keeps its plain list, because `IN` over any number of values is total. Prevents the
misreading "TY1/TY3/TY8 mean wrap everything" — strengthen the one place that was partial, nowhere else.

### CC3 — Every remote call has a timeout that stops the work; `orTimeout` alone only abandons

**Bad** (ours)
```java
@Bean
public ExchangeToolHandler exchangeToolHandler(ToolCredentialEncryptor encryptor) {
    RestClient restClient = RestClient.builder().build();
    return new ExchangeToolHandler(
        new GraphMailClient(encryptor, restClient),
        new EwsMailClient(encryptor, restClient)
    );
}
// ExchangeToolHandler.execute:
return CompletableFuture.supplyAsync(() -> doExecute(req))
    .orTimeout(limits.timeoutMs(), TimeUnit.MILLISECONDS)
```
`aruvii-tools/…/ToolsAutoConfiguration.java:211-218` + `aruvii-tools/…/handlers/ExchangeToolHandler.java:113-114`
@ `772736bf` — the Graph/EWS `RestClient` has no connect or read timeout, so after `orTimeout` fires the agent sees
"Timed out" while the HTTP call keeps running on a common-pool thread. The port contract tells every handler to do
this: `ToolHandlerPort.java:56` "timeout via `orTimeout`". also breaks: CC2 (no-executor `supplyAsync`), CM4 (that
javadoc claim is false), ST1 (non-final local).

**Good** (rewritten from `ToolsAutoConfiguration.java:211-218`) — NEEDS COMPILE CHECK
```java
@Bean
public ExchangeToolHandler exchangeToolHandler(
        final ToolCredentialEncryptor encryptor,
        final ExchangeHttpProperties exchangeHttp) {
    final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(exchangeHttp.connectTimeout())
            .build();
    final var requestFactory = new JdkClientHttpRequestFactory(httpClient);
    requestFactory.setReadTimeout(exchangeHttp.readTimeout());
    final RestClient restClient = RestClient.builder().requestFactory(requestFactory).build();
    return new ExchangeToolHandler(
            new GraphMailClient(encryptor, restClient),
            new EwsMailClient(encryptor, restClient));
}
```
— the deadline is on the socket, so a stuck Graph/EWS read ends and frees its thread. `ExchangeHttpProperties` is a new
validated `@ConfigurationProperties` record (LY7). `orTimeout` may stay as the per-call wait, because the work under it
now stops on its own; the `ToolHandlerPort.java:56` javadoc is corrected to say so. Prevents the misreading
"`orTimeout` is a timeout" — it only stops *waiting*.

### CC4 — A bounded pool has a bounded queue and a stated rejection behaviour

**Bad** (ours)
```java
@Bean(destroyMethod = "shutdownNow")
ScheduledExecutorService sseHeartbeatScheduler() {
    return Executors.newScheduledThreadPool(4,
        Thread.ofVirtual().name("sse-heartbeat-", 0).factory());
}
```
`aruvii-api/…/config/SseHeartbeatConfig.java:12-16` @ `772736bf` — four threads look bounded, but the delay queue is
not: every open SSE stream adds its own periodic task (`SessionMessageController.java:239-242`), and nothing says what
happens past capacity. Intent not verified (open streams may be capped elsewhere). also breaks: CC1 (pools virtual
threads), ST2 (wrapped call), SC6 (returns the interface, not the concrete type).

**Good** (rewritten from `SseHeartbeatConfig.java:12-16` + `SessionMessageController.java:239-242`) — NEEDS COMPILE CHECK
```java
@Bean
SseHeartbeats sseHeartbeats(final SseProperties sse) {
    return new SseHeartbeats(new ArrayBlockingQueue<>(sse.maxOpenStreams()));
}

@Bean(destroyMethod = "shutdownNow")
ScheduledThreadPoolExecutor sseHeartbeatTicker(final SseHeartbeats heartbeats) {
    final var ticker = new ScheduledThreadPoolExecutor(
            1,
            Thread.ofPlatform().name("sse-heartbeat").factory());
    ticker.scheduleAtFixedRate(heartbeats::sendToAll, HEARTBEAT_SECONDS, HEARTBEAT_SECONDS, TimeUnit.SECONDS);
    return ticker;
}
```
— one platform thread runs one task; the open streams sit in a queue of `maxOpenStreams`. `SseHeartbeats.register(emitter)`
is `open.offer(emitter)` and returns a sealed `Registered | Refused`; the controller turns `Refused` into an
`ErrorCode` response, so the 1 001st stream is refused out loud. `SseHeartbeats`, `SseProperties` and the error code are
new. Prevents the misreading "`Executors.newScheduledThreadPool(4)` / `newFixedThreadPool(8)` is bounded" — the
threads are, the queue is not.

### CC9 — A remote call ends as success, failure or unknown; intent before the call; key from the initiator

**Bad** (ours)
```java
for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
        HttpRequest request = HttpRequest.newBuilder()
            // … url, signature, X-aruvii-JobId, timeout(15 s), POST body …
            .build();
        HttpResponse<Void> resp = HTTP.send(request, HttpResponse.BodyHandlers.discarding());
        int status = resp.statusCode();
        // … 2xx → return; 4xx → return; 5xx → retry …
    } catch (Exception e) {
        log.warn("WebhookCallbackSender request failed jobId={} attempt={}: {}",
            job.id(), attempt + 1, e.getMessage());
    }
    // … sleep, next attempt …
}
```
`aruvii-worker/…/webhook/WebhookCallbackSender.java:69-97` @ `772736bf` — a read timeout after the POST was sent is
logged as "request failed" and sent again, though the receiver may already have it; nothing records that a delivery
started, and `send` returns `void`, so no caller learns the outcome. The job-id header (`:75`) is the right key, from
the initiator. also breaks: ER4 (`catch (Exception)`), U4 (`:60` `Instant.now()`), TY1 (`:48` `null` callback URL).

**Good** (rewritten from `WebhookCallbackSender.java:47-97`) — NEEDS COMPILE CHECK
```java
public CallbackDelivery send(final URI callbackUrl, final WebhookJob job) {
    deliveryLog.recordSending(job.id());
    try {
        final HttpResponse<Void> response = http.send(signedPost(callbackUrl, job), discarding());
        return CallbackDelivery.fromStatus(job.id(), response.statusCode());
    } catch (final HttpConnectTimeoutException | ConnectException notConnected) {
        return new CallbackDelivery.NotDelivered(job.id(), notConnected.getClass().getSimpleName());
    } catch (final IOException afterConnect) {
        return new CallbackDelivery.Unknown(job.id(), afterConnect.getClass().getSimpleName());
    } catch (final InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        return new CallbackDelivery.Unknown(job.id(), "interrupted");
    }
}
```
— intent is written first; a refused connection is a failure, but anything after connect (a read timeout included) is
`Unknown`, never a silent retry. The retry loop moves to the caller, which switches over the sealed `CallbackDelivery`
and resends only `NotDelivered` — with the same `X-aruvii-JobId`, so the receiver can drop a duplicate. `deliveryLog`,
`signedPost` and `CallbackDelivery` are new (`discarding` is a static import of `HttpResponse.BodyHandlers`); this I/O seam decides nothing beyond its own result (SEAM1 S-3).
Prevents the misreadings "a timeout is a failure, so retry" and "the retrying layer mints the key".

---

## G9b-GB2 · Errors, comments, layers

### ER1 — A foreseeable non-success is a sealed outcome; only faults throw

**Bad** (ours)
```java
public DbConnection create(final UUID workspaceId, final CreateCommand cmd) {
    final long start = System.currentTimeMillis();
    LOG.info("action=dbconnection_create workspaceId={}", workspaceId);

    port.findByWorkspaceIdAndName(workspaceId, cmd.name()).ifPresent(existing -> {
        throw new AruviiException(ErrorCode.DB_CONNECTION_NAME_TAKEN,
            "workspaceId=" + workspaceId + " name=" + cmd.name());
    });

    final DbConnection toSave = new DbConnection(
        null, workspaceId, cmd.name(),
        // … engine, urls, username, password, tls, pool …
        cmd.createdBy(), null, null, null);
    final DbConnection saved = port.save(toSave);
```
`aruvii-tools/…/application/DbConnectionService.java:69-85` @ `772736bf` — "a connection with that name already exists"
is a normal answer to "create", yet it leaves as an exception thrown from inside a lambda; the signature says it
always returns a `DbConnection`. also breaks: JV1/U4 (`long` millis from the wall clock, `:70,88`), TY1 (`null`s in
the constructor), LG8 (`LOG`, not `log`).

**Good** (rewritten from `DbConnectionService.java:69-90`) — NEEDS COMPILE CHECK
```java
public InsertionResult<DbConnection> create(final UUID workspaceId, final CreateCommand cmd) {
    log.info("action=dbconnection_create workspaceId={}", workspaceId);
    if (port.findByWorkspaceIdAndName(workspaceId, cmd.name()).isPresent()) {
        return new InsertionResult.Duplicate<>(cmd.name());
    }
    final DbConnection saved = port.save(DbConnection.unchecked(
            workspaceId,
            cmd,
            encryptor.encrypt(cmd.plainPassword())));
    log.info("action=dbconnection_create_ok workspaceId={} connectionId={}", workspaceId, saved.id());
    return new InsertionResult.Created<>(saved);
}
```
— the duplicate is a case of the return type, using the shared outcome `InsertionResult` (`shared/outcome/InsertionResult.java:20-29`,
#514); the controller answers with `.orThrow(ErrorCode.DB_CONNECTION_NAME_TAKEN)`. A database fault still throws.
`DbConnection.unchecked(…)` (new) replaces the 17-argument constructor call and its `null`s. Prevents the misreading
"name taken feels exceptional, so the service throws".

### ER4 — Catch the narrowest type; `catch (Exception)` only at a must-not-fail boundary, commented

**Bad** (ours)
```java
try {
    JsonNode root = MAPPER.readTree(body);
    JsonNode models = root.path("models");
    if (models.isArray()) {
        for (JsonNode m : models) {
            String name = m.path("name").asString();
            if (model.equals(name) || name.startsWith(model + ":")) {
                modelPulled = true;
                break;
            }
        }
    }
} catch (Exception ignored) {
    // /api/tags returned but JSON unexpected — still reachable, just downgrade detail.
}
```
`aruvii-api/…/activity/AdminActivityClient.java:74-88` @ `772736bf` (flag declared `:73`) — the only thing that can fail here is JSON
parsing, yet the catch takes every exception and drops it; a bug in the loop would read as "model not pulled".
also breaks: ER3 (empty block, nothing logged), ST1 (non-final locals), NM1 (`m`).

**Good** (rewritten from `AdminActivityClient.java:73-88`) — NEEDS COMPILE CHECK
```java
private boolean listsConfiguredModel(final String tagsBody) {
    try {
        for (final JsonNode entry : MAPPER.readTree(tagsBody).path("models")) {
            final String name = entry.path("name").asString();
            if (name.equals(model) || name.startsWith(model + ":")) {
                return true;
            }
        }
        return false;
    } catch (final JacksonException unexpectedShape) {
        log.warn("action=activity.health.tags_unreadable cause={}", unexpectedShape.getClass().getSimpleName());
        return false;
    }
}
```
— `tools.jackson.core.JacksonException` is the one failure the parse can raise, so it is the one caught; any other
exception now surfaces. The outcome for unreadable JSON is unchanged (model reported missing), but it is logged. The
`isArray` check goes: a missing `models` node iterates as empty. Prevents the misreading "best-effort code is a boundary,
so `catch (Exception)` is fine" — this is a parse, not a boundary.

### ER8 — A best-effort metric or audit call may catch and continue; WARN with the exception class

**Bad** (ours)
```java
private void logLifecycle(String action, UUID agentId, Integer fromVersion, Integer toVersion,
                           String fromStatus, String toStatus, UUID actorUserId, String reason) {
    if (lifecycleLog == null) return;  // graceful degradation if no port wired
    try {
        lifecycleLog.record(new AgentLifecycleLog(
            null, agentId, fromVersion, toVersion, fromStatus, toStatus,
            actorUserId, action, reason, Instant.now(), null));
    } catch (Exception ignored) { /* never block the main flow on audit failures */ }
}
```
`aruvii-agents/…/application/AgentService.java:62-70` @ `772736bf` — catching is allowed here (audit is best effort),
but the block is silent, so a broken audit trail is invisible. also breaks: ER3 (empty block), ER4 (`Exception`),
TY1 (`null` port decides "skip"; `null` id), U4 (`Instant.now()`), smell *Data Clumps* (eight parameters), ST2.

**Good** (rewritten from `AgentService.java:62-70`) — NEEDS COMPILE CHECK
```java
private void logLifecycle(final AgentLifecycleChange change) {
    try {
        lifecycleLog.record(AgentLifecycleLog.of(change, clock.instant()));
    } catch (final RuntimeException auditFailure) {
        log.warn(
                "action=agent.lifecycle.audit_failed agentId={} lifecycleAction={} cause={}",
                change.agentId(),
                change.action(),
                auditFailure.getClass().getSimpleName());
    }
}
```
— the call still never blocks the agent change, but each lost audit row leaves one WARN line with the class and no
stack (LG3). The port is a required constructor argument, so the `null` guard goes. `AgentLifecycleChange` (new record)
carries the eight values; `AgentLifecycleLog.of` (new) stamps the time from the injected `Clock`. Prevents the
misreading "best effort means it may be silent" — that is ER3's empty block.

### ER10 — An error response carries the `ErrorCode` message only

**Bad** (ours)
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(DataIntegrityViolationException ex) {
    return ApiResponse.error("Invalid reference: " + ex.getMostSpecificCause().getMessage());
}
```
`aruvii-api/…/controller/AgentController.java:186-190` @ `772736bf` — `getMostSpecificCause()` is the JDBC driver's
exception, so the client receives Postgres text: constraint names, column names, sometimes the offending value.
also breaks: ER11 (a controller declares `@ExceptionHandler`), ER2 (no `ErrorCode`, no trace id).

**Good** (rewritten from `AgentController.java:186-190`, moved to `GlobalExceptionHandler`) — NEEDS COMPILE CHECK
```java
@ExceptionHandler(DataIntegrityViolationException.class)
@ResponseStatus(HttpStatus.BAD_REQUEST)
public ApiResponse<Void> handleDataIntegrity(final DataIntegrityViolationException violation) {
    final String traceId = currentTraceId();
    log.warn(
            "action=api.data_integrity traceId={} cause={}",
            traceId,
            violation.getMostSpecificCause().getClass().getSimpleName());
    return ApiResponse.error(
            ErrorCode.VALIDATION_FAILED.code(),
            ErrorCode.VALIDATION_FAILED.defaultMessage(),
            traceId);
}
```
— the body says only what the catalogue says (`ErrorCode.java:80`); the operator gets the trace id and the cause's class
in the log, and the driver text goes nowhere. The handler lives in `GlobalExceptionHandler` (ER11) and the controller's
copy is deleted. Prevents the misreading "the driver's `getMessage()` is useful detail for the client".

### CM3 — A comment survives only for a constraint the code cannot show

**Bad** (ours)
```java
// Metric: tool.call.duration tagged by toolType + status. Bounded cardinality —
// tool types are an enum, statuses are a small fixed set. Operators get a graph
// of "are HTTP tools getting slower?" and "is the SUCCESS rate dropping?"
if (meters != null) {
    try {
        meters.timer("tool.call.duration",
            "toolType", toolType == null ? "UNKNOWN" : toolType,
            "status",   status   == null ? "UNKNOWN" : status.toString())
            .record(java.time.Duration.ofMillis(Math.max(0L, latencyMs)));
    } catch (Exception ignored) { /* metric failure must never affect chat */ }
}
```
`aruvii-worker/…/chat/ChatOrchestrator.java:219-229` @ `772736bf` — the comment defends our own tag choice ("bounded
cardinality") instead of the code showing it; and it is false: `toolType` is a `String` (`:202`). also breaks: CM4
(unchecked claim), TY1 (`null` → `"UNKNOWN"`, `null` registry), TY6 (tool type as a string), ER3/ER4 (`catch (Exception
ignored)`).

**Good** (rewritten from `ChatOrchestrator.java:219-229`) — NEEDS COMPILE CHECK
```java
private void recordToolCallDuration(
        final ToolType toolType,
        final ToolCallStatus status,
        final Duration latency) {
    try {
        meters.timer("tool.call.duration", "toolType", toolType.name(), "status", status.name())
                .record(latency);
    } catch (final RuntimeException meterFailure) {
        log.warn(
                "action=tool.call.metric_failed toolType={} cause={}",
                toolType,
                meterFailure.getClass().getSimpleName());
    }
}
```
— the two enum parameters (`tools/domain/ToolType`, `shared/tool/ToolCallStatus`) now say "bounded cardinality", so the
comment has nothing left to say; the operator questions it answered belong in the metrics reference, not here. Prevents
the misreading "a *why* comment about our own code is always allowed" (X1) — CM3 keeps only outside constraints.

### CM4 — Check a comment's factual claim; encode "keep in sync" as a type, test or lint

**Bad** (ours)
```java
// Mandatory anti-buffering headers — without these, nginx + corporate proxies stall
// SSE responses for 30s+ at a time. Stays in sync with docs/architecture/ARCHITECTURE.md §Streaming.
response.setHeader("Cache-Control",     "no-cache, no-transform");
response.setHeader("X-Accel-Buffering", "no");
```
`aruvii-api/…/controller/SessionMessageController.java:230-233` @ `772736bf` — the claim is false:
`ARCHITECTURE.md` has no header text in its streaming section (no `X-Accel-Buffering` anywhere under `docs/architecture/`
@ `772736bf`). The same two headers are copied by hand into `PromptBuilderController.java:162` and
`WebhookController.java:140`, which nothing keeps in sync. also breaks: DS12 (rule-encoding literals in three places).

**Good** (rewritten from `SessionMessageController.java:230-233`) — NEEDS COMPILE CHECK
```java
final class SseHeaders {
    // nginx and corporate proxies hold text/event-stream frames unless these two headers are set
    static void disableProxyBuffering(final HttpServletResponse response) {
        response.setHeader(HttpHeaders.CACHE_CONTROL, "no-cache, no-transform");
        response.setHeader("X-Accel-Buffering", "no");
    }
}
```
```groovy
def "should tell proxies not to buffer the event stream"() {
    given: "a servlet response"
    def response = new MockHttpServletResponse()
    when: "the stream headers are applied"
    SseHeaders.disableProxyBuffering(response)
    then: "nginx and HTTP caches pass each frame straight through"
    response.getHeader("X-Accel-Buffering") == "no"
}
```
— the three streaming endpoints call one helper, and a spec holds the headers, so the "stays in sync" line is
deleted. The proxy sentence stays: it is an outside constraint (CM3). `SseHeaders` and its spec are new.
Prevents the misreading "a sync note is enough" — a note does not fail when the copies drift; a shared method and a
test do.

### CM7 — Never suppress a lint or compiler rule that protects correctness; fix the type

**Bad** (ours)
```ts
interface ConfirmEntry {
  id: string;
  options: ConfirmOptions;
  mode: 'confirm' | 'prompt';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  resolve: (value: any) => void;
}
// …
ask(options: ConfirmOptions): Promise<boolean> {
  return this.enqueue(options, 'confirm') as Promise<boolean>;
}
```
`aruvii-ui/src/app/core/confirm.service.ts:13-19,27-29` @ `772736bf` — `no-explicit-any` is a correctness rule;
silencing it lets `accept()` hand a string to a `confirm` caller, and the `as Promise<boolean>` casts (`:28,:32`) hide
it. also breaks: TY10 by analogy (a cast stands in for a type).

**Good** (rewritten from `confirm.service.ts:13-19,27-29,43-47`) — NEEDS COMPILE CHECK
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
— the union ties each `mode` to its `resolve` type, so the suppression, both casts and the `unknown` in `resolveEntry`
go. `enqueue` now takes a built entry; `cancel()` mirrors `accept()` with `false`/`null`. Prevents the misreading "a
suppression with a reason is fine" (X6) — a style rule may be suppressed; a type rule is fixed.

### LY1 — A controller binds, delegates and shapes; a branch that chooses an outcome lives in a service

**Bad** (ours)
```java
ChatSession session = sessionService.get(id);
// … ids, trace id, 7 comment lines on ordering …
if (session.status() != SessionStatus.ACTIVE) {
    throw new AruviiException(ErrorCode.SESSION_ARCHIVED,
        "session " + session.id() + " is " + session.status());
}
// … 4 comment lines on slot ownership …
if (sessionCapService.claimSlot(session.userId(), session.workspaceId(), session.id())
        instanceof SessionCapDecision.Refused refused) {
    throw new AruviiException(ErrorCode.SESSION_LIMIT_EXCEEDED,
        "already using " + refused.current() + " of " + refused.cap()
            + " concurrent sessions in this workspace");
}
messageService.saveUserMessage(session.id(), req.userMessage());
```
`aruvii-api/…/controller/SessionMessageController.java:142,155-173` @ `772736bf` — the controller decides whether a
message may be sent (session state, cap claim) and in what order, so the REQ-007 ordering contract lives in a web
class no service test reaches. also breaks: CM3 (long justification comments `:148-154,160-163`), ST1 (non-final locals).

**Good** (rewritten from `SessionMessageController.java:136-189`) — NEEDS COMPILE CHECK
```java
@PostMapping("/messages")
@PreAuthorize("@wsAuth.canEditSession(#id)")
public ApiResponse<SendMessageResponse> sendMessage(
        @PathVariable final UUID id,
        @RequestBody final SendMessageRequest req,
        final Authentication auth,
        final HttpServletRequest httpRequest) {
    final SendOutcome outcome = messageSender.send(id, callerOf(auth, httpRequest), req);
    return switch (outcome) {
        case SendOutcome.Accepted accepted -> ApiResponse.ok(SendMessageResponse.of(accepted));
        case SendOutcome.SessionEnded ended -> throw new AruviiException(ErrorCode.SESSION_ARCHIVED, ended.detail());
        case SendOutcome.AtCap atCap -> throw new AruviiException(ErrorCode.SESSION_LIMIT_EXCEEDED, atCap.detail());
    };
}
```
— the service (`messageSender`, new) checks the state, claims the slot, saves and publishes in that order and returns
the sealed `SendOutcome` (new); the controller only maps each case to a response. Prevents the misreading "mapping an
outcome to a status is a branch too, so it must move" — an exhaustive switch over the service's answer is shaping,
which LY1 allows.

### LY2 — An interface only for a faked boundary or a module boundary; its one implementation is `Default<Name>`

**Bad** (ours)
```java
@Service
public class LlmAdapterRegistryImpl implements LlmAdapterRegistry {
    private final List<LlmAdapterPort> adapters;

    public LlmAdapterRegistryImpl(List<LlmAdapterPort> adapters) {
        this.adapters = adapters;
    }

    @Override
    public LlmAdapterPort forProviderType(String providerType) {
        for (LlmAdapterPort a : adapters) {
            if (a.supports(providerType)) return a;
        }
        throw new UnsupportedProviderException(providerType);
    }
```
`aruvii-worker/…/llm/LlmAdapterRegistryImpl.java:14-29` @ `772736bf`, interface `aruvii-shared/…/llm/LlmAdapterRegistry.java:9-16`
— a public `*Impl` behind an interface in `aruvii-shared`, though every caller is in `aruvii-worker`
(`ChatOrchestrator`, `DefaultLlmSummarizer`, `OllamaActivityClient`, `LlmMockAdapter`, `PromptBuilderTestHandler`) and
the I/O boundary is `LlmAdapterPort`, one level down. The interface exists so tests can `mock` it
(`ChatOrchestratorFixture.java:82`). also breaks: TY13 (`Impl` suffix), JV9 (no braces), NM1 (`a`).

**Good** (rewritten from `LlmAdapterRegistryImpl.java:14-29`; the `aruvii-shared` interface is deleted) — NEEDS COMPILE CHECK
```java
@Service
public class LlmAdapterRegistry {

    private final List<LlmAdapterPort> adapters;

    public LlmAdapterRegistry(final List<LlmAdapterPort> adapters) {
        this.adapters = List.copyOf(adapters);
    }

    public LlmAdapterPort forProviderType(final String providerType) {
        return adapters.stream()
                .filter(adapter -> adapter.supports(providerType))
                .findFirst()
                .orElseThrow(() -> new UnsupportedProviderException(providerType));
    }
```
— one concrete class in `aruvii-worker`; tests build the real registry with fake `LlmAdapterPort`s (the boundary)
instead of mocking the selection logic. Had a second module needed it, the interface would stay and this class would be
package-private `DefaultLlmAdapterRegistry`. `providerType` stays a `String` because `LlmAdapterPort.supports` takes one
(`shared/llm/LlmAdapterPort.java:24`); turning it into an enum is TY6's change, not this one. Prevents the misreading
"every service gets an interface" (the old services.md §1).

---

## Counts

| | n | rules |
|---|---|---|
| rewritten from ours | 18 | JV1 JV5 TY1 TY3 TY8 TY9 CC3 CC4 CC9 ER1 ER4 ER8 ER10 CM3 CM4 CM7 LY1 LY2 |
| adapted from source (no Bad on master) | 0 | — |

Bads changed from `54-g9b-good-bad-selection.md`: TY9 now has a real Bad (`PickerCompiler.java:260-277`, partiality not
pushed into the type), CC9 too (`WebhookCallbackSender.java:69-97`); CC3 uses `ExchangeToolHandler` + its `RestClient`
bean instead of `HttpToolHandler` (which does set `HttpRequest.timeout` at `:335`, so it is not a clean Bad); ER8 uses
`AgentService.java:62-70` so that `ChatOrchestrator.java:219-229` serves CM3 alone.

## Operator review (2026-10-03)

- JV1: ok
- JV5: ok
- TY1: ok
- TY3: ok (+ SE5 decided edge: Jackson DEDUCTION over a closed @JsonSubTypes set is allowed — it only chooses among listed records, never a class named in the payload)
- TY8: ok
- TY9: ok
- CC3: ok
