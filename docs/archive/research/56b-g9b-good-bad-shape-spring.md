# 56b — G9b Good/Bad pairs: code shape, runtime, frameworks (#33, batches GB3 + GB4)

For **#33** (G9b — approving the code + observability rules) under map **#9** (One rulebook).
Written under `research/55-good-bad-v3-BRIEF.md` (GB2): **Bad = our real code; Good = that same Bad rewritten** to obey
its rule, every approved rule in `19-approved-rules.md` and house style. Our code is never a Good as-is. Where our code
has no Bad, both sides are `adapted from <source:line>` of a source opened for this file. Seams in a Good follow SEAM1
(ADR-0017 S-1..S-7, agent-platform `a73ba796:docs/adr/0017-turn-journal-and-replay.md:213-219`) and avoid the Fowler
smells baseline (rameezk/skills `skills/code-review/martin-fowler-code-smells.md`, fetched 2026-10-03).
Every Good is **NEEDS COMPILE CHECK** (work item 1 compiles them).

Rules (operator-approved selection, `54-g9b-good-bad-selection.md` §3): DS1 DS3 DS4 DS8 DS12 DS14 MS6 LG2 LG3 ·
LY6 LY7 SC6 SC7 SC15 SC16 SC19 SC21 NGB3.

Bads: agent-platform `origin/master` = **`772736bf`** (2026-10-03) unless a past commit is named; module prefixes are
dropped where the file name is unique. `…` inside a snippet marks lines left out, never changed.

---

## GB3 · Code shape and runtime

### DS1 — Look for a restructure that deletes branches, not one that moves them

**Bad** (ours, past commit `dffd26e5^1`; fixed by #349 — the retention rule written twice, so the preview could lie
about what gets deleted)
```java
// DataRetentionJob.java:69-74 — the job decodes the sentinel …
final int retentionDays = resolveRetentionDays(ws.retentionDays(), platformDefault);
if (retentionDays == 0) {
    log.debug("data_retention workspaceId={} keep_forever — skipped", ws.workspaceId());
    continue;
}
Instant cutoff = Instant.now(clock).minus(retentionDays, ChronoUnit.DAYS);
// DataErasureController.java:117-122 — … and the preview decodes it again
int retentionDays = resolveRetentionDays(ws.dataRetentionDays(), platformDefault);
if (retentionDays == 0) {
    return new RetentionPreviewEntry(ws.id(), ws.name(), 0, null, 0L);
}
Instant cutoff = Instant.now(clock).minus(retentionDays, ChronoUnit.DAYS);
```
— `resolveRetentionDays` is copied too (`DataRetentionJob.java:108-112`, `DataErasureController.java:127-131`); each
caller re-branches on `0` and repeats the cutoff arithmetic. #349's fix (`dffd26e5`) added `RetentionWindow` but each
caller still `switch`es on it — the branch moved, it was not deleted. also breaks: TY1 (`null` cutoff, :120), LY1
(preview decided in a controller), CM1 (banner at `DataErasureController.java:115`), TY4/ST1 (non-final locals).

**Good** (rewritten from `DataRetentionJob.java:69-74` + `DataErasureController.java:117-122` @ `dffd26e5^1`)
```java
public sealed interface RetentionWindow {
    record KeepForever() implements RetentionWindow {}
    record Days(int count) implements RetentionWindow {}   // compact ctor rejects count <= 0 (TY3), unchanged

    default Optional<Instant> purgeBefore(final Instant now) {
        return switch (this) {
            case KeepForever _ -> Optional.empty();
            case Days days -> Optional.of(now.minus(days.count(), ChronoUnit.DAYS));
        };
    }
}
// job:     window.purgeBefore(clock.instant()).ifPresent(cutoff -> purge(workspace.workspaceId(), cutoff));
// preview: final long rowCount = window.purgeBefore(clock.instant())
//                  .map(cutoff -> retentionPort.countExpiredData(workspace.id(), cutoff))
//                  .orElse(0L);
```
— the one decoder (`RetentionWindow.resolve`, as on master) and the one cutoff rule live on the type; both callers lose
their branch and their arithmetic, and the preview moves to a service (LY1). Misreading it prevents: "I removed the
duplication" when the `== 0` branch was only moved into a shared helper or a per-caller `switch` — count the branches
left in the callers; if it did not drop, the restructure was not found.

### DS3 — No one-off `if` or second boolean in a flow; model the case

**Bad** (ours) `ChatOrchestrator.java:201-206` @ `772736bf`
```java
private void recordToolCallSafely(UUID interactionId, ai.aruvii.agents.domain.Agent agent,
                                   UUID sessionId, UUID toolId, String toolType,
                                   String inputJson, String outputJson, long latencyMs,
                                   ToolCallStatus status, ToolErrorCode errorCode,
                                   boolean requiresApproval, UUID approvalId,
                                   String traceId, boolean mocked, String mockSource) {
```
— mock mode arrived as a boolean plus a string that only means something when the boolean is true;
`requiresApproval` + `approvalId` is the same shape a second time. also breaks: ST2 (several arguments per line), TY6
(`String toolType`), TY8 (five `UUID`s side by side), TY1 (`toolType == null`, `meters != null` at :211, :222), ER8
(`catch (Exception ignored)` at :228), U4 (`Instant.now()` at :213), Fowler Data Clumps / Long Parameter List.

**Good** (rewritten from `ChatOrchestrator.java:201-206`)
```java
sealed interface ToolRun {
    record Live() implements ToolRun {}
    record Mocked(MockSource source) implements ToolRun {}
}

sealed interface ApprovalGate {
    record NotRequired() implements ApprovalGate {}
    record Required(UUID approvalId) implements ApprovalGate {}
}

record ToolCallRecord(ToolCallIds ids, ToolType toolType, ToolCallPayload payload, ToolCallStatus status,
                      ApprovalGate approval, ToolRun run) {
}

private void recordToolCall(final ToolCallRecord call) {
```
— each mode is a sealed case carrying only its own data, so `mockSource` cannot exist without "mocked" and an
`approvalId` cannot exist without an approval; the eleven loose parameters become one record (S-2 record in). The
persistence adapter maps `ToolRun` to its two columns with an exhaustive `switch` (S-4, TY2). Misreading it prevents:
"one more flag is cheaper than a type" — every boolean pair is a combination someone must keep in sync by hand.

### DS4 — Remove pass-throughs and single-caller wrappers; apply the deletion test

**Bad** (ours) `TriggerService.java:135-147` @ `772736bf`
```java
/** Returns all triggers that are due to fire right now. */
public List<TriggerConfig> findDueScheduledTriggers() {
    return triggerRepository.findDueScheduledTriggers();
}

/**
 * Atomic optimistic-lock claim. Advances next_run_at only when the expected value still matches.
 *
 * @return true if this instance won the race and should fire the trigger
 */
public boolean claimAndAdvance(UUID agentId, Instant expectedNextRunAt, Instant newNextRunAt) {
    return triggerRepository.claimAndAdvance(agentId, expectedNextRunAt, newNextRunAt);
}
```
— two one-line forwards whose only production caller is `ScheduledTriggerJob.java:83,127` (its other two calls,
`resetRunAsFailures` :167 and `recordRunAsFailure` :189, are forwards too, the latter plus one INFO line). also breaks:
CM2/CM5 (Javadoc restating the port), TY8 (two `Instant`s side by side), SEAM1 S-2 (`boolean` decides won/lost).

**Good** (rewritten from `TriggerService.java:135-147` + `ScheduledTriggerJob.java:59,83,127`)
```java
@Component
class ScheduledTriggerJob {

    private final TriggerRepository triggers;
    // … other collaborators unchanged

    FireOutcome processTrigger(final TriggerConfig trigger, final ClaimWindow window) {
        return switch (triggers.claimAndAdvance(trigger.agentId(), window)) {
            case TriggerClaim.Won _ -> fire(trigger);
            case TriggerClaim.Lost _ -> FireOutcome.NOT_CLAIMED;
        };
    }
}
```
— the job depends on the port that does the work; the forwarding methods are deleted (S-7 earn the seam; Fowler Middle
Man), and the claim returns a sealed `Won`/`Lost` (S-2, the CAS example S-3 names) over a `ClaimWindow(expected,
next)` record (TY8). `findDueScheduledTriggers` is called on `triggers` the same way. Misreading it prevents (the LY2
collision): deleting a *translating* module-boundary adapter because "it only calls the repository" — e.g.
`AgentTriggerRepositoryAdapter` maps JPA rows to `TriggerConfig` and fails the deletion test (the mapping would reappear
in every caller). Delete a forwarder; keep a translator.

### DS8 — No null check or try/catch to silence a failure on a trusted path

**Bad** (ours) `OpenApiSpecImporter.java:86-90,197-199` @ `772736bf`
```java
/** Back-compat constructor (pre-V80 callers without tool group support). */
public OpenApiSpecImporter(ToolPort toolPort, ToolCredentialEncryptor encryptor,
                           ObjectMapper mapper) {
    this(toolPort, encryptor, mapper, null, null);
}
…
private void applyDestination(ImportOperationsRequest req, List<ToolResponse> created, UUID createdBy) {
    ToolGroupDestination dest = req.destination();
    if (dest == null || toolGroupService == null) return;
```
— a second constructor passes `null` for two final fields; its only user is `OpenApiSpecImporterTest.java:177`. The
trusted path grew `toolGroupService == null` so that test passes, and in production a wiring mistake would make group
placement silently do nothing. also breaks: SC1 (test-only second constructor), TY1 (`dest == null` decides the case;
`ToolGroupDestination.type` is a `String`, TY6), JV9 (unbraced `if`), CM1 (banner at :92).

**Good** (rewritten from `OpenApiSpecImporter.java:76-90,197-199`)
```java
OpenApiSpecImporter(final ToolPort toolPort,
                    final ToolCredentialEncryptor encryptor,
                    final ObjectMapper mapper,
                    final ToolGroupService toolGroupService,
                    final ToolInputSchemaResolver inputSchemaResolver) {
    // … assignments unchanged; the back-compat constructor is deleted
}

private void applyDestination(final GroupPlacement placement, final List<UUID> toolIds, final UUID createdBy) {
    switch (placement) {
        case GroupPlacement.None _ -> { }
        case GroupPlacement.NewGroup group -> toolGroupService.create(group.toRequest(toolIds), createdBy);
        case GroupPlacement.ExistingGroup group -> toolIds.forEach(toolId -> toolGroupService.addTool(group.id(), toolId));
    }
}
```
— one constructor (SC1), no `null` guard: the collaborator is constructor-injected and final, so it is never `null` in
production; the wire `ToolGroupDestination` is decoded to a sealed `GroupPlacement` at the request boundary (TY12), and
the test builds the importer with `Stub(ToolGroupService)`. Misreading it prevents: "a guard is defensive, so it is
safe" — the guard hid a half-wired object; fix the test, delete the constructor, then grep for `== null` on other
injected fields.

### DS12 — A rule-encoding predicate or literal is defined once, called everywhere

**Bad** (ours, past commit `8f7bf163`; fixed by #636 — smoke cleanup missed `smoke77-` resources)
`aruvii-ui/playwright/global-setup.ts:52,85,100,117`
```ts
const smokeSessions = sessions.filter(s => s.title?.startsWith('smoke-') || s.title?.startsWith('rate-limit-smoke-'));
const staleTools = tools.filter(t => t.name.startsWith('smoke-'));
const smokeProviders = providers.filter(p => p.name.startsWith('smoke-'));
const smoke = workspaces.filter(w => (w.slug ?? '').startsWith('smoke-') || (w.name ?? '').startsWith('smoke-'));
```
— "what counts as smoke data" lives in four lambdas that already disagree (only sessions know `rate-limit-smoke-`);
numbered prefixes leaked every run until #636. also breaks: NM1 (`s`, `t`, `p`, `w`, `smoke`), CV3 (over 110 chars).

**Good** (rewritten from `global-setup.ts:52,85,100,117` @ `8f7bf163`)
```ts
// playwright/support/smoke-name.ts
const SMOKE_NAME = /^(rate-limit-)?smoke\d*[-_]/;

export function isSmokeName(name: string | null | undefined): boolean {
  return SMOKE_NAME.test(name ?? '');
}

// playwright/global-setup.ts — every purge site calls the one predicate
const smokeSessions = sessions.filter((session) => isSmokeName(session.title));
const smokeTools = tools.filter((tool) => isSmokeName(tool.name));
const smokeProviders = providers.filter((provider) => isSmokeName(provider.name));
const smokeWorkspaces = workspaces.filter(
  (workspace) => isSmokeName(workspace.slug) || isSmokeName(workspace.name),
);
```
— the rule has one home; a new prefix is one edit and every site learns it. (#636's `917df5ea` added the same
predicate; the `rate-limit-` arm is kept here because the sessions site matched it.) Misreading it prevents: "four
`startsWith('smoke-')` calls are trivial, not duplication" — a literal that encodes a rule is exactly what DS12 means.

### DS14 — Do not extract a helper for 2–3 similar lines with no shared rule

No Bad in our code on `772736bf` (the misreading's result was not found), so both sides are adapted from Fowler's
catalogue entry *Remove Flag Argument*, https://refactoring.com/catalog/removeFlagArgument.html (page source lines
137-146 the merged `setDimension(name, value)`, 170-171 the split `setHeight`/`setWidth`), moved onto the two
`RestClient` builders that look alike on master (`CustomPiiEndpointClient.java:46-51`, `LlmFakeGenerator.java:42-45`).

**Bad** (adapted from removeFlagArgument.html:137-146)
```java
static RestClient restClient(final String kind, final Duration timeout, final String baseUrl) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    if ("pii".equals(kind)) {
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);
        return RestClient.builder().requestFactory(requestFactory).build();
    }
    requestFactory.setConnectTimeout(Duration.ofSeconds(1));
    requestFactory.setReadTimeout(timeout);
    return RestClient.builder().baseUrl(baseUrl).requestFactory(requestFactory).build();
}
```
— one "shared" factory for two callers that share no rule; it needs a mode argument at once, and every new caller adds
another arm. also breaks: DS3 (a mode string into a flow), TY6 (`String kind`).

**Good** (adapted from removeFlagArgument.html:170-171)
```java
// CustomPiiEndpointClient — its own setting, its own policy
static RestClient restClient(final CustomPiiProperties pii) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(pii.timeout());
    requestFactory.setReadTimeout(pii.timeout());
    return RestClient.builder().requestFactory(requestFactory).build();
}

// LlmFakeGenerator — looks alike, answers to a different setting
static RestClient restClient(final OllamaActivityProperties ollama) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(ollama.connectTimeout());
    requestFactory.setReadTimeout(ollama.generateTimeout());
    return RestClient.builder().baseUrl(ollama.baseUrl().toString()).requestFactory(requestFactory).build();
}
```
— two four-line builders stay apart: each timeout belongs to its own settings record (LY7, SC14), and they will change
for different reasons. Misreading it prevents: DS12 over-applied — "similar lines are duplication" builds a factory that
grows a flag per caller. Extract only when the repeated thing is a rule (a prefix, a limit, a status). The two comment
lines label the sites for this page; they are not code.

### MS6 — Answer "runs twice / crashed halfway"; reconcile when leftovers matter

**Bad** (ours) `UserErasureAdapter.java:56-63,163-170` @ `772736bf`
```java
@Override
@Transactional
public UserErasureLog erase(UUID subjectUserId, UUID requestedBy, String subjectEmail) {

    // 409 guard — idempotency
    logPort.findCompletedBySubjectUserId(subjectUserId).ifPresent(existing -> {
        throw new AlreadyErasedException(subjectUserId);
    });
    … // :68-161 PENDING log row, audit row, the deletes, COMPLETED
    } catch (Exception ex) {
        log.error("user_erasure FAILED subjectUserId={} logId={}: {}: {}", …, ex);
        logEntity.setStatus("FAILED");
        logRepo.save(logEntity);
        throw ex;
    }
```
— "runs twice": two concurrent erasures both pass a check that looks only for a COMPLETED row (check-then-act), and
each writes its own log and audit row. "Crashed halfway": the FAILED row is saved inside the transaction the rethrow
rolls back, so it never lands — the comment says "idempotency" but neither question was answered. Lead found by
reading; no incident filed. also breaks: ER1 (foreseeable "already erased" thrown), LG2 (`log.error` then `throw ex`),
TY6 (status as `String`), CM1 (step banners :68-152), U4 (`Instant.now()` :154).

**Good** (rewritten from `UserErasureAdapter.java:56-63,163-170`)
```java
@Override
@Transactional
public ErasureOutcome erase(final ErasureRequest request) {
    lockSubject(request.subjectUserId());
    return logPort.findCompletedBySubjectUserId(request.subjectUserId())
            .<ErasureOutcome>map(ErasureOutcome.AlreadyErased::new)
            .orElseGet(() -> eraseLocked(request));
}

private void lockSubject(final UUID subjectUserId) {
    jdbc.queryForObject("SELECT id FROM users WHERE id = ? FOR UPDATE", UUID.class, subjectUserId);
}
```
— runs twice: the row lock makes the second run wait, then see COMPLETED and return a sealed outcome (ER1); crashed
halfway: the whole erasure is one transaction, so nothing is left behind and a rerun starts clean — no reconcile step
is needed, and the `catch` that wrote a FAILED row nobody could read is deleted (the failure is logged once by the
handler, LG2). Misreading it prevents: "it's idempotent because there is a guard" — a read-then-act guard answers
neither question; name the lock or key that makes the second run see the first.

### LG2 — Log a failure once, where it is handled

**Bad** (ours) `NotificationConfigService.java:114,137-143` @ `772736bf`
```java
try {
    final NotificationConfig updated = new NotificationConfig(
            … // :116-134 the merged fields, ending in Instant.now()
    );
    final NotificationConfig saved = configPort.save(updated);
    log.info("NotificationConfigService.update complete configId={}", saved.id());
    return maskPassword(saved);
} catch (Exception e) {
    log.warn("NotificationConfigService.update failed: {} {}", e.getClass().getSimpleName(), e.getMessage());
    throw e;
}
```
— the service logs and rethrows; `GlobalExceptionHandler.java:179-183` (or `logAtSeverity`, :192) logs the same failure
again with the stack, so one failure is two lines at two levels. also breaks: ER4 (`catch (Exception)` not at a
boundary), U4 (`Instant.now()` :134), LG1 (entry line not `action=…`).

**Good** (rewritten from `NotificationConfigService.java:114-143`)
```java
final NotificationConfig updated = new NotificationConfig(
        … // the merged fields as before
        clock.instant());
final NotificationConfig saved = configPort.save(updated);
log.info("action=notification_config.update configId={}", saved.id());
return maskPassword(saved);
```
— no `try`: the exception travels to `GlobalExceptionHandler`, the one place that handles it and logs it once.
Misreading it prevents: "log context before rethrow is helpful" — if context is needed, put it in the exception (a
catalogue `ErrorCode` and a chained cause, ER2/ER3), not in a second log line.

### LG3 — WARN = handled, class and message, no stack; ERROR = investigate, throwable last

**Bad** (ours) `SessionMessageController.java:302-303,318-321` @ `772736bf`
```java
private void sendOrClose(SseEmitter emitter, ChatResponseEvent event) {
    try {
        … // :304-317 send; IllegalStateException and IOException handled at DEBUG
    } catch (Exception e) {
        log.warn("Unexpected SSE failure: {}", e.toString(), e);
        emitter.completeWithError(e);
    }
}
```
— "unexpected" means someone must look, yet it logs at WARN; and passing `e` last prints a stack at WARN. Either reading
breaks LG3. also breaks: ER4 (`catch (Exception)` with no boundary comment), LG1 (no `action=`/ids).

**Good** (rewritten from `SessionMessageController.java:318-321`)
```java
    } catch (RuntimeException e) {
        // Must not fail: runs inside the ChatResponseSubscriber callback shared by every session (ER4).
        log.error("action=sse.send outcome=failed sessionId={} event={}", sessionId, eventName(event), e);
        emitter.completeWithError(e);
    }
```
— an unexpected failure is ERROR with the throwable last, so the stack prints once; the expected cases above it stay
handled (the `IOException` arm, a dropped browser, would be WARN with `e.getClass().getSimpleName()` and no stack if
it were logged above DEBUG). The catch narrows to `RuntimeException` (the checked `IOException` is already caught) and
names its boundary (ER4, CM3: the subscriber callback at :236-237 is an outside constraint); `sendOrClose` gains a
`sessionId` parameter for the log line (LG1). Misreading it prevents: `log.warn(msg,
e)` — "it's only a warning" while it prints a full stack and pages nobody.

---

## GB4 · Frameworks

### LY6 — One constructor; an optional collaborator is an `ObjectProvider<T>` resolved at use

**Bad** (ours) `AgentsAutoConfiguration.java:142-149` @ `772736bf`
```java
@Bean
public PipelineExecutionService pipelineExecutionService(
        PipelineRepository pipelineRepository,
        @Lazy ObjectProvider<AgentChatPort> chatPortProvider) {
    AgentChatPort chatPort = chatPortProvider.getIfAvailable(
            () -> req -> { throw new UnsupportedOperationException("AgentChatPort not available in this context"); });
    return new PipelineExecutionService(pipelineRepository, chatPort);
}
```
— the provider is resolved while the bean is created, so it decides once, at the wrong time: in the api context (only
`aruvii-worker`'s `AgentChatAdapter` implements the port) it bakes in a throwing stub. also breaks: SC3 (`@Lazy` on an
`ObjectProvider`), SC5 (no `proxyBeanMethods = false` on the class, :49), TY4 (non-final parameters and local).

**Good** (rewritten from `AgentsAutoConfiguration.java:142-149` + `PipelineExecutionService.java:27-31,56`)
```java
@Bean
PipelineExecutionService pipelineExecutionService(final PipelineRepository pipelineRepository,
                                                  final ObjectProvider<AgentChatPort> chatPorts) {
    return new PipelineExecutionService(pipelineRepository, chatPorts);
}

// PipelineExecutionService — resolved where a step runs
private AgentChatResponse runStep(final AgentChatRequest request) {
    return chatPorts.getObject().chat(request);
}
```
— the bean holds the provider and resolves it per step; where no `AgentChatPort` exists, `getObject()` fails at that
call with Spring's `NoSuchBeanDefinitionException` naming the type, instead of a stub chosen at startup. No `@Lazy`
(SC3). If the `@Lazy` was there to break a cycle, SC2 applies: cut it, or keep the provider and name the cycle in a
comment. Misreading it prevents: "I took an `ObjectProvider`, so LY6 is met" — taking one and resolving it in the
factory is the same as injecting the bean, plus a stub.

### LY7 — Grouped settings in one validated record; each key bound in one place

**Bad** (ours) `AdminActivityClient.java:43-46` + `OllamaActivityClient.java:42-45` @ `772736bf`
```java
// aruvii-api — AdminActivityClient
public AdminActivityClient(
        @Value("${aruvii.activity.ollama.base-url:http://localhost:11434}") String baseUrl,
        @Value("${aruvii.activity.ollama.model:qwen3:1.7b}") String model,
        @Value("${aruvii.activity.ollama.timeout-ms:5000}") long timeoutMs) {
// aruvii-worker — OllamaActivityClient
public OllamaActivityClient(
        @Value("${aruvii.activity.ollama.base-url:http://localhost:11434}") String baseUrl,
        @Value("${aruvii.activity.ollama.model:qwen3:1.7b}") String model,
        @Value("${aruvii.activity.ollama.timeout-ms:1500}") long timeoutMs) {
```
— one key, two defaults (`timeout-ms` 5000 vs 1500); the same base-url and model are also read in
`LlmFakeGenerator.java:38-39`. Unset, the api and the worker run with different timeouts for "the same" setting. also
breaks: SC12 (key read in three classes), SC14 (`long … -ms`), SC1 (`@Autowired` on `LlmFakeGenerator.java:36`),
CM3 (comment at `AdminActivityClient.java:49-50` explains the drift instead of removing it).

**Good** (rewritten from `AdminActivityClient.java:43-55` + `OllamaActivityClient.java:42-52`)
```java
@Validated
@ConfigurationProperties("aruvii.activity.ollama")
public record OllamaActivityProperties(@NotNull URI baseUrl,
                                       @NotBlank String model,
                                       @NotNull Duration connectTimeout,
                                       @NotNull Duration probeTimeout,
                                       @NotNull Duration classifyTimeout,
                                       @NotNull Duration generateTimeout) {
}

public AdminActivityClient(final OllamaActivityProperties ollama) {
    this.http = restClient(ollama.baseUrl(), ollama.connectTimeout(), ollama.probeTimeout());
}
```
— one record bound once (registered by `@EnableConfigurationProperties` on the module's configuration class, SC11),
read by all three clients; values live in the shipped `application.yml`, not in Java defaults. Where two callers
really need different timeouts, they are two named keys (`probe-timeout`, `classify-timeout`), not one key with two
defaults (SC14 `Duration`). The record sits in a module both apps import, not `aruvii-shared` (LY4). Misreading it
prevents: "`@Value` per class is local and fine" — two `@Value`s for one key is two truths.

### SC6 — A `@Bean` method returns the most specific type it builds

**Bad** (ours) `AgentsAutoConfiguration.java:52-55` @ `772736bf`
```java
@Bean
public AgentRepository agentRepository(AgentJpaRepository repo) {
    return new AgentRepositoryAdapter(repo);
}
```
— the method builds an `AgentRepositoryAdapter` but declares the port; before the bean is created, the container (and
AOT, and any type-based condition) sees only `AgentRepository`. also breaks: SC5 (proxied configuration class, :49),
TY4 (non-final parameter).

**Good** (rewritten from `AgentsAutoConfiguration.java:52-55`)
```java
@Bean
AgentRepositoryAdapter agentRepository(final AgentJpaRepository repo) {
    return new AgentRepositoryAdapter(repo);
}
```
— the declared type is what is built; callers still inject `AgentRepository` (Spring matches by every type the bean
has), so the hexagonal boundary is unchanged. Source: FW `core/aot.html` §Expose the Most Precise Bean Type
(`51-spring-core-rules.md:171`). Misreading it prevents: "return the port, that's hexagonal" — the port is what
*consumers* depend on; the factory's return type is container metadata and should be exact.

### SC7 — Several implementations: `@ConditionalOnProperty` per value, exactly one matches, missing fails startup

**Bad** (ours) `ToolsAutoConfiguration.java:220-227,234-242` @ `772736bf`
```java
@Bean
@ConditionalOnMissingBean(EmbeddingPort.class)
public EmbeddingPort embeddingPort(
        @Value("${aruvii.rag.onnx.model-path:/models/bge-small-en-v1.5.onnx}") String modelPath,
        @Value("${aruvii.rag.onnx.vocab-path:/models/vocab.txt}") String vocabPath) {
    Path mPath = Path.of(modelPath);
    Path vPath = Path.of(vocabPath);
    if (Files.exists(mPath) && Files.exists(vPath)) {
        … // :228-233 load OnnxEmbeddingAdapter
        } catch (Exception e) {
            log.warn("ONNX embedding init failed ({}), falling back to hash embeddings", e.getMessage());
        }
    } … // :238-241 else: WARN "using hash-based embeddings"
    return new HashEmbeddingAdapter();
}
```
— two real implementations (`OnnxEmbeddingAdapter`, `HashEmbeddingAdapter`) chosen by whether a file exists, a silent
fallback on any failure, and a `@ConditionalOnMissingBean` on a scanned `@Configuration` whose outcome depends on parse
order (BOOT `developing-auto-configuration.html` §Bean Conditions; the S5.6 PKIX incident, `.claude/SPRINTS.md:404`).
The same shape elsewhere: `ToolsAutoConfiguration.java:91-95` stub + `AgentsAutoConfiguration.java:78-83` `@Primary`.
also breaks: SC6, SC16 (silent degraded mode), ER4, LY7/SC13 (`@Value` pair), SC4 (the `@Primary` pair).

**Good** (rewritten from `ToolsAutoConfiguration.java:220-243`)
```java
@Bean
@ConditionalOnProperty(name = "aruvii.rag.embedding", havingValue = "onnx", matchIfMissing = false)
OnnxEmbeddingAdapter onnxEmbeddings(final RagProperties rag) {
    return OnnxEmbeddingAdapter.load(rag.onnx().modelPath(), rag.onnx().vocabPath());
}

@Bean
@ConditionalOnProperty(name = "aruvii.rag.embedding", havingValue = "hash", matchIfMissing = false)
HashEmbeddingAdapter hashEmbeddings() {
    log.warn("action=rag.embedding mode=hash quality=low key=aruvii.rag.embedding");
    return new HashEmbeddingAdapter();
}

@Validated @ConfigurationProperties("aruvii.rag")
record RagProperties(@NotNull EmbeddingMode embedding, @Valid OnnxFiles onnx) {}
```
— each implementation carries its own value (SC10 form), exactly one matches, and an unset `aruvii.rag.embedding`
fails startup through the `@NotNull` enum, naming the key (OQ-SC1 d). The ONNX bean fails startup if its files are
missing instead of falling back; hash is a named degraded mode that WARNs once (SC16). An `ApplicationContextRunner`
spec proves each value and the missing case (SC9). Misreading it prevents: "`@ConditionalOnMissingBean` / `@Primary`
is the Spring way to pick one" — on a scanned class it picks by load order (BOOT), and `@Primary` is banned (SC4).
Before adding a property, check there really are two implementations: the `AgentCountByToolPort` stub has no
production context where it applies, so its Good is deleting the stub and the `@Primary` (DS6), not a property.

### SC15 — A settings record rejects bad values at startup, naming the key; a runner spec proves it

**Bad** (ours) `WorkerStreamsProperties.java:17-35` @ `772736bf`
```java
@ConfigurationProperties(prefix = "aruvii.worker.streams")
public record WorkerStreamsProperties(Stream chat,
                                      Stream task,
                                      Stream eval,
                                      Stream promptTest,
                                      Duration drainTimeout) {

    public WorkerStreamsProperties {
        if (drainTimeout.isZero() || drainTimeout.isNegative()) {
            throw new IllegalArgumentException(PREFIX + "drain-timeout must be more than zero, but was " + …);
        }
        for (final WorkerStream stream : WorkerStream.values()) {
            requireCap(capOf(stream, chat, task, eval, promptTest), stream);
        }
    }
```
— the checks are good for a *wrong* value but not for a *missing* one: with `drain-timeout` or a stream block unset,
the compact constructor dereferences `null` and startup fails with a bare `NullPointerException` that names no key.
The Jakarta half of OQ-SC5 is absent (no `@Validated`). The spec proves only the zero case
(`WorkerStreamsStartupSpec.groovy:43-49`), and its feature names are camelCase (U2a/CV6). (The selection's Bad,
`PlatformConfigProperties.java:7-11`, has no bad value to reject but the secret, which is SC16/SC17.)

**Good** (rewritten from `WorkerStreamsProperties.java:17-39,64-70`)
```java
@Validated
@ConfigurationProperties("aruvii.worker.streams")
public record WorkerStreamsProperties(@NotNull @Valid Stream chat,
                                      @NotNull @Valid Stream task,
                                      @NotNull @Valid Stream eval,
                                      @NotNull @Valid Stream promptTest,
                                      @NotNull @DurationMin(millis = 1) Duration drainTimeout) {

    public record Stream(@Min(1) int maxInFlight) {
    }
}
```
— each field carries its own constraint and Boot's bind-validation failure names the property; the per-field checks
leave the compact constructor. OQ-SC5 keeps the compact constructor for *cross-field* rules only — this record has
none, so it has none. Order matters: the constructor runs **before** `@Validated`, so a compact-constructor check must
never dereference a field the annotations guard. `@DurationMin` is Hibernate Validator's (Jakarta has no `Duration`
constraint). The runner spec gains `def "should refuse to start when drain-timeout is missing"()` beside the zero case.
Misreading it prevents: "either style is fine" (OQ-SC5 says both) and "my compact constructor validates" when it only
validates values that are present.

### SC16 — No default for a secret or required endpoint; fail, or a named degraded mode at WARN

**Bad** (ours) `ProvidersAutoConfiguration.java:31-33` + `CredentialEncryptor.java:21-26` + `application.yml:104` @ `772736bf`
```java
@Bean
public CredentialEncryptor credentialEncryptor(@Value("${aruvii.master-key:}") String masterKey) {
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
aruvii:
  master-key: ${ARUVII_MASTER_KEY:${master_key:}}
```
— a missing master key is defaulted to `""` twice (yml and `@Value`), and `""` silently switches every provider
credential to plaintext storage — no failure, no log. also breaks: SC12 (`aruvii.master-key` read in four classes:
also `ToolsAutoConfiguration.java:82`, `ErasureConfig.java:16`), SC13 (env-var name in config), TY1/SEAM1 S-2
(`boolean passthrough` decides the mode).

**Good** (rewritten from `ProvidersAutoConfiguration.java:31-33` + `CredentialEncryptor.java:21-26`)
```java
@Bean
CredentialEncryptor credentialEncryptor(final Environment environment, final CredentialProperties credentials) {
    return Optional.ofNullable(environment.getProperty("aruvii.master-key"))
            .filter(not(String::isBlank))
            .<CredentialEncryptor>map(AesGcmCredentialEncryptor::new)
            .orElseGet(() -> plaintextIfAllowed(credentials));
}

private static CredentialEncryptor plaintextIfAllowed(final CredentialProperties credentials) {
    if (!credentials.plaintextAllowed()) {
        throw new InvalidConfigurationPropertyValueException("aruvii.master-key", "", "required to encrypt credentials");
    }
    log.warn("action=credentials.mode mode=plaintext key=aruvii.credentials.plaintext-allowed");
    return new PlaintextCredentialEncryptor();
}
```
— absence fails startup with Boot's own exception, whose failure analyzer names the key; plaintext exists only as a
named mode that `aruvii.credentials.plaintext-allowed=true` selects and that logs once at WARN (OQ-SC4). That property
is set in `src/test/resources/application.yml` or a local override, never the shipped file; `application.yml:104` is
deleted (relaxed binding reads `ARUVII_MASTER_KEY`). The key is read through the `Environment`, never stored in a
properties record (SC17); the mode is a type, not a boolean (S-2). The other three readers take this bean's key
holder (SC12). Misreading it prevents: "`:` with an empty default is harmless" and "the plaintext flag is fine in the
shipped yml" (OQ-SC4 forbids it).

### SC19 — Work that must finish before traffic runs in an `ApplicationRunner`; later work goes to a thread from ready

**Bad** (ours) `GlobalTrustStore.java:37-39,56-59` @ `772736bf`
```java
@Service
@Primary
public class GlobalTrustStore implements TrustedCertificatesPort {
    …
    @PostConstruct
    void initialise() {
        rebuild();
    }
```
— `rebuild()` reads every certificate row from the database while the bean is still being created: a DB outage or a
missing table fails context refresh from inside an unrelated bean's construction, and every bean that injects the
store waits on that I/O. also breaks: SC18 (I/O in `@PostConstruct`), SC4 (`@Primary`), ER4 (`catch (Exception
ignored)` in `refreshIfStale`, :92).

**Good** (rewritten from `GlobalTrustStore.java:37-39,56-59`)
```java
@Service
public class GlobalTrustStore implements TrustedCertificatesPort, ApplicationRunner {
    … // fields and the one constructor unchanged

    @Override
    public void run(final ApplicationArguments arguments) {
        rebuild();
    }
```
— TLS trust must be loaded before a tool or provider call goes out, so it is "must finish before traffic": an
`ApplicationRunner` runs after the context is refreshed and before Boot publishes `ReadinessState.ACCEPTING_TRAFFIC`
(BOOT `spring-application.html` §Using the ApplicationRunner, §Readiness State). `@Primary` goes (SC4). Misreading it
prevents: "`@PostConstruct` and an `ApplicationReadyEvent` listener both run at startup" — the first does I/O inside
bean creation (SC18), the second runs *after* readiness, so traffic can arrive first; a ready listener is only for work
that may finish later, handed to another thread.

### SC21 — A proxied annotation works only on a call from another bean; never through `this`

**Bad** (ours) `SetupService.java:165-180` @ `772736bf`
```java
@Transactional
public String getOrGenerateSecretKey() {
    String stored = settings.get(KEY_SECRET);
    if (!stored.isBlank()) return decryptSafe(stored);
    String generated = generateSecureKey();
    settings.set(KEY_SECRET, encryptor.encrypt(generated));
    return generated;
}

/** SecretKeyPort implementation — env var takes precedence over DB. */
@Override
public String getEffectiveSecretKey() {
    String fromEnv = System.getenv("ARUVII_SECRET_KEY");
    if (fromEnv != null && !fromEnv.isBlank()) return fromEnv;
    return getOrGenerateSecretKey();
```
— the port method (what `JwtService`, `OidcController` and `AuthAutoConfiguration` call) reaches the `@Transactional`
method through `this`, so the proxy is bypassed and the read-then-write runs with no transaction. also breaks: SC13
(`System.getenv`), NM3 (`get…` names that write), TY1 (`fromEnv != null`), JV9 (unbraced `if`), CM2 (Javadoc
restating the code).

**Good** (rewritten from `SetupService.java:165-180`)
```java
@Component
class SecretKeyStore {
    … // one constructor: PlatformSettingsPort settings, CredentialEncryptor encryptor
    @Transactional
    String loadOrCreate() {
        final String stored = settings.get(KEY_SECRET);
        return stored.isBlank() ? create() : decryptSafe(stored);
    }
}
// SetupService implements SecretKeyPort
@Override
public String loadOrCreateSecretKey() {
    return Optional.ofNullable(environment.getProperty("aruvii.secret-key"))
            .filter(not(String::isBlank))
            .orElseGet(secretKeyStore::loadOrCreate);
```
— the transactional method lives on a second bean, so the call crosses the proxy; no self-injection, no `AopContext`.
`create()` generates and stores the key; the override binds `aruvii.secret-key` (relaxed binding reads
`ARUVII_SECRET_KEY`, SC13); names say they may write (NM3, port renamed with its callers). Runs twice: the api is a
single replica (ADR-0016), so two first calls cannot race across instances. Misreading it prevents: "the annotation is
on the method, so it applies" — it applies only when the call comes from outside the bean.

### NGB3 — State in `signal()`, derived state in `computed()`; `effect()` never copies

**Bad** (ours) `aruvii-ui/src/app/features/pipelines/pipeline-builder.component.ts:222,225-226,242-243,258-265` @ `772736bf`
```ts
workspaceId = '';
allAgents = signal<AgentResponse[]>([]);
workspaceAgents = signal<AgentResponse[]>([]);
…
        this.workspaceId = p.workspaceId;
        this.filterAgents(p.workspaceId);
…
onWorkspaceChange(wsId: string) {
  this.filterAgents(wsId);
  this.steps.update((ss) => ss.map((s) => ({ ...s, agentId: '' })));
}

private filterAgents(wsId: string) {
  this.workspaceAgents.set(this.allAgents().filter((a) => a.workspaceId === wsId && a.status === 'ACTIVE'));
}
```
— `workspaceAgents` is a copy, refreshed only when someone remembers to call `filterAgents`. In edit mode the pipeline
and the agent list load in parallel (:235, :238); if the pipeline answers first, the filter runs on an empty list and
the step dropdowns stay empty until the user changes workspace. also breaks: NGC4 (`error: () => {}` at :234-235),
NM1 (`wsId`, `ss`, `s`, `a`, `p`).

**Good** (rewritten from `pipeline-builder.component.ts:222,225-226,242-243,258-265`)
```ts
readonly workspaceId = signal('');
readonly allAgents = signal<AgentResponse[]>([]);
readonly workspaceAgents = computed(() =>
  this.allAgents().filter((agent) => agent.workspaceId === this.workspaceId() && agent.status === 'ACTIVE'),
);

// on load: this.workspaceId.set(pipeline.workspaceId);  — nothing to re-filter

onWorkspaceChange(workspaceId: string): void {
  this.workspaceId.set(workspaceId);
  this.steps.update((steps) => steps.map((step) => ({ ...step, agentId: '' })));
}
```
— the filtered list is derived, so it is right whichever request lands first; `filterAgents` is deleted. The template
binds `[ngModel]="workspaceId()" (ngModelChange)="onWorkspaceChange($event)"`, and the two `error: () => {}` become
`toast.error(…)` (NGC4). Misreading it prevents: "`.set(filter(…))` in a handler is normal state" — a value computed
from other signals is a `computed()`, not a second signal kept in sync by hand (and not an `effect()` that copies).

---

## Counts

| | n | rules |
|---|---|---|
| Bad = our real code (`772736bf` or a named past commit) | 17 | DS1 DS3 DS4 DS8 DS12 MS6 LG2 LG3 LY6 LY7 SC6 SC7 SC15 SC16 SC19 SC21 NGB3 |
| Good = that Bad rewritten (`rewritten from path:lines`) | 17 | same |
| Both sides adapted from an opened source (no Bad in our code) | 1 | DS14 (refactoring.com Remove Flag Argument) |
| Goods taken from our code as-is | 0 | — |
| Total pairs | 18 | all `NEEDS COMPILE CHECK` |

Changes against `54-g9b-good-bad-selection.md` §1 (BAD column): **MS6** has a real Bad (`UserErasureAdapter.java`, the
selection's "lead to check"); **SC7** Bad is the `EmbeddingPort` fallback (`ToolsAutoConfiguration.java:220-243`, two
real implementations) — the selection's `AgentCountByToolPort` stub has no second production case, so its fix is
deletion (DS6); **SC15** Bad is `WorkerStreamsProperties.java:17-35` (missing value → bare NPE) — the selection's
`PlatformConfigProperties.java:7-11` has no bad value except the secret (SC16/SC17); **LG3** lines are :318-321.
