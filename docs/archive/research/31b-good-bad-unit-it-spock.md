# 31b — Good/Bad examples: unit-tests.md · integration-tests.md · spock.md

Source: agent-platform `origin/master` (fetched 2026-10-02). Rules from `19-approved-rules.md`, ids U1–U4, IT1–IT5, IT4b, SP1–SP11, K1–K20, K2b.

## unit-tests.md

### U1 — Every test is A-TRIP: automatic, thorough, repeatable, independent, professional
**Good** (real)
```groovy
    static final Instant NOW = Instant.parse("2026-09-20T12:00:00Z")
    ...
    def setup() {
        service = new ProviderService(providerPort, connectionTestPort, agentCountPort,
            new CredentialEncryptor("test-secret-key-that-is-32chars!"),
            Clock.fixed(NOW, ZoneOffset.UTC))
    }

    def "should report a provider older than the threshold, and not one exactly at it"() {
        given: "two providers, one sitting exactly on the threshold and one a second past it"
            providerPort.findAll() >> [provider("exactly-at-threshold", NOW.minus(90, ChronoUnit.DAYS)),
                                       provider("one-second-older", NOW.minus(90, ChronoUnit.DAYS).minusSeconds(1))]
```
`aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:28,36-45` — fixed clock, fresh instance per feature, both sides of the boundary: repeatable and thorough.

**Bad** (real)
```java
    private void await(java.util.function.BooleanSupplier cond) {
        long deadline = System.currentTimeMillis() + 60_000;
        while (System.currentTimeMillis() < deadline) {
            if (cond.getAsBoolean()) return;
            try { Thread.sleep(250); } catch (InterruptedException e) {
                Thread.currentThread().interrupt(); return;
            }
        }
        throw new AssertionError("condition never satisfied within 60s");
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/modelswap/UiModelSwapE2EIT.java:600-609` — wall-clock sleep-poll; outcome depends on host speed (not Repeatable), and an interrupt silently returns as success.

### U2 — Spock features use labelled blocks and a plain-sentence name, not shouldXxx
**Good** (real)
```groovy
    def "a tool nothing uses counts zero, which is what permits the delete"() {
        given: "an agent that uses no tool at all"
        insertAgent(workspaceId, "unwired")
        em.flush()
        em.clear()

        expect: "the join yields no rows rather than counting every agent"
        repo.countAgentsByToolId(toolId) == 0L
    }
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:40-48` — name reads as a behaviour sentence; given:/expect: labelled.

**Bad** (real)
```groovy
    def "shouldCarryTheWorkspacesACallerIsRestrictedTo"() {
        given:
        final workspaceA = UUID.randomUUID()
        final workspaceB = UUID.randomUUID()

        when:
        final scope = new CollectionScope.Only(Set.of(workspaceA, workspaceB))

        then:
        scope.workspaceIds() == Set.of(workspaceA, workspaceB)
    }
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/authz/CollectionScopeSpec.groovy:12-22` — JUnit camelCase name ported into Spock; also a pure construction that wants `expect:`.

### U3 — Double only at a boundary; Stub() for returners, Mock() only when the call is the behaviour
**Good** (real)
```groovy
    ApiKeyRepository apiKeyRepo = Mock()
    UserRepository userRepo = Stub()
    WorkspaceMemberRepository memberRepo = Stub()
    AuditLogPort audit = Mock()
    ...
        then: "the audit port receives exactly one entry"
        1 * audit.save(_) >> { AuditLogEntry e -> written = e; e }
```
`aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:24-27,50-51` — lookups are Stub(); the audit port is Mock() because writing the audit row IS the behaviour; encoder is the real class.

**Bad** (real)
```groovy
    LlmProviderPort providerPort = Mock()
    ConnectionTestPort connectionTestPort = Mock()
    AgentCountByProviderPort agentCountPort = Mock()
    ...
            providerPort.findAll() >> [provider("aged-89-days", NOW.minus(89, ChronoUnit.DAYS))]
```
`aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:31-33,67` — every port is Mock() yet only ever stubbed, never verified; should be Stub(). (Same spec is the U1/U4 Good — the clock half is right.)

### U4 — Production logic takes an injected Clock; never calls Instant.now() directly
**Good** (real)
```java
    public List<RotationReminderRecord> staleProviders(int thresholdDays) {
        log.info("action=provider_stale_providers thresholdDays={}", thresholdDays);
        final Instant now = clock.instant();
        final Instant cutoff = now.minus(thresholdDays, ChronoUnit.DAYS);
        return providerPort.findAll().stream()
                .filter(p ->
                        !p.archived() && p.createdAt() != null && p.createdAt().isBefore(cutoff))
```
`aruvii-providers/src/main/java/ai/aruvii/providers/application/ProviderService.java:674-680` — one instant from the injected clock serves cutoff and day count, so the spec pins the boundary exactly.

**Bad** (real)
```java
        if (token.isUsed()) {
            throw new ResetTokenException("Reset token has already been used");
        }
        if (token.getExpiresAt().isBefore(Instant.now())) {
            throw new ResetTokenException("Reset token has expired");
        }
```
`aruvii-auth/src/main/java/ai/aruvii/auth/application/PasswordResetService.java:76-81` — expiry rule reads the wall clock; a test cannot pin "expires exactly now".

## integration-tests.md

### IT1 — An IT proves wiring and contracts; it does not re-test unit-owned business branches
**Good** (real)
```groovy
    def "shouldRegisterTheInjectedIdentityOn#group"() {
        given: "an entry for the running consumer to read — its loop registers it on that read"
        ensureGroup(stream, group)
        redis.opsForStream().add(StreamRecords.mapBacked(["payload": "{}"]).withStreamKey(stream))

        when: "the consumer the worker started has read at least once"
        def names = awaitConsumerNames(stream, group)

        then: "the group holds this process's identity"
        names.contains(consumerIdentity.name())
```
`aruvii-worker/src/integrationTest/groovy/ai/aruvii/worker/stream/ConsumerIdentityIT.groovy:48-57` — asserts what only real Redis + the started app can show (XINFO CONSUMERS); no business branching.

**Bad** (real)
```java
    @DisplayName("PUT smtpEnabled=true with smtpRecipients blank → 400 naming smtpRecipients")
    void updateConfig_enabledWithBlankRecipients_returns400() {
        putConfig("""
                { "smtpEnabled": true, "smtpHost": "localhost", "smtpFrom": "from@x.com", "smtpRecipients": "" }
                """)
                .expectStatus().isBadRequest()
    ...
    @DisplayName("PUT smtpEnabled=true with smtpFrom blank → 400 naming smtpFrom")
    void updateConfig_enabledWithBlankFrom_returns400() {
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/NotificationConfigControllerIT.java:187-192,198-199` — one HTTP IT per missing field (lines 164-206, 4 variants); `NotificationConfigServiceTest.java:183-250` already owns those branches. One 400-mapping IT is the contract.

### IT2 — ITs get containers only from the singleton initializer; no @Testcontainers/@Container/@ServiceConnection
**Good** (real)
```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
@EnableAruviiIT
public abstract class AbstractIT {

    @Autowired
    protected RestTestClient http;
```
`aruvii-test-support/src/main/java/ai/aruvii/testsupport/AbstractIT.java:22-27` — containers arrive via `@EnableAruviiIT` → `AruviiTestcontainersInitializer` (javadoc `:15-29` explains why not `@Container`/`@ServiceConnection`). Spock twin: `@EnableAruviiSpec` at `ConsumerIdentityIT.groovy:31-33`.

**Bad** (real)
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@Import(AruviiTestClientConfig.class)
@ExtendWith({RedisFlushExtension.class, RedisReachabilityCheck.class})
class SetupControllerIT {
    ...
    @Container
    static PostgreSQLContainer postgres = new PostgreSQLContainer(TestConstants.POSTGRES_IMAGE)
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:44-48,54-55` — per-class container, stopped at class end. Documented bootstrap exception (needs an unseeded DB) that the rule as approved does not carry; same pattern in `FileToolHandlerS3IT.java:37`.

### IT3 — ITs call the real server via RestTestClient (RANDOM_PORT); never MockMvc/TestRestTemplate
**Good** (real)
```java
    private RestTestClient.ResponseSpec putConfig(String json) {
        return http.put().uri("/api/platform/notifications/config")
                .header(HttpHeaders.AUTHORIZATION, adminToken)
                .contentType(MediaType.APPLICATION_JSON)
                .body(json)
                .exchange();
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/NotificationConfigControllerIT.java:570-576` — real HTTP through the security filter chain, JWT and all (`http` from `AbstractIT:27`).

**Bad** (real)
```java
        WebhookController ctrl = new WebhookController(
            triggerService, sessionService, publisher, subscriber, webhookJobPort, tracerProvider, mapper);
        mockMvc = MockMvcBuilders.standaloneSetup(ctrl).build();
    ...
        mockMvc.perform(post("/api/webhooks/{agentId}/{secret}", agentId, validSecret)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"message\":\"hello\"}"))
            .andExpect(status().isAccepted());
```
`aruvii-api/src/test/java/ai/aruvii/api/controller/WebhookControllerRunContextTest.java:63-65,87-90` — HTTP-shaped assertions over standalone MockMvc: no filter chain, no security, no error advice; the only MockMvc left on master (a unit test, so rule letter not broken, spirit is).

### IT4 — Swap a collaborator only at an outbound port with a fake bean; never @MockitoBean
**Good** (real)
```java
public class FakeActiveSessionCountPort implements ActiveSessionCountPort, Resettable {

    private final Map<UUID, Integer> counts = new HashMap<>();

    public void setCount(final UUID agentId, final int count) {
        counts.put(agentId, count);
    }

    @Override
    public int countActiveSessions(final UUID agentId) {
        return counts.getOrDefault(agentId, 0);
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakeActiveSessionCountPort.java:17-29` — real in-memory implementation of an outbound port, resettable between tests.

**Bad** (adapted from CLAUDE.md "never @MockitoBean"; `NEEDS COMPILE CHECK`)
```java
class AgentEvalControllerIT extends AbstractIT {

    @MockitoBean
    ActiveSessionCountPort activeSessionCountPort;

    @BeforeEach
    void stubSessions() {
        when(activeSessionCountPort.countActiveSessions(any())).thenReturn(0);
    }
```
— a Mockito double with no behaviour of its own, and a new context-cache key per class. Master has 0 `@MockitoBean` annotation uses (javadoc mentions only).

### IT4b — Swap via the shared FakePortsConfig (or @TestBean returning a fake); prefer shared to per-class
**Good** (real)
```java
@Import(ai.aruvii.api.support.FakePortsConfig.class)
class AgentEvalControllerIT extends AbstractIT {

    private String adminAuth;
    private UUID agentId;
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/AgentEvalControllerIT.java:23-27` — shared `@Primary` fakes from `FakePortsConfig.java:17-36`; every importer reuses one cached context.

**Bad** (real)
```java
class AgentControllerIT extends AbstractIT {

    private static final FakeActiveSessionCountPort ACTIVE_SESSION_COUNT_PORT = new FakeActiveSessionCountPort();

    @TestBean
    ActiveSessionCountPort activeSessionCountPort;

    static ActiveSessionCountPort activeSessionCountPort() {
        return ACTIVE_SESSION_COUNT_PORT;
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/AgentControllerIT.java:29-38` — per-class `@TestBean` for a port `FakePortsConfig` already supplies; forks a context. Same in `PromptBuilderControllerIT:34`, `SecurityIT:58`, `AgentSnapshotLimitIT:39`.

### IT5 — Every fake port has a contract spec run against both fake and real adapter
**Good** (adapted from langchain4j `Abstract*IT` pattern (R19); `NEEDS COMPILE CHECK`)
```groovy
abstract class AgentCountByToolPortContract extends Specification {
    abstract AgentCountByToolPort port()
    abstract void linkAgent(UUID toolId)

    def "a tool nothing uses counts zero"() {
        expect: port().countByToolId(UUID.randomUUID()) == 0L
    }

    def "every agent wired to the tool is counted"() {
        given: def toolId = UUID.randomUUID(); linkAgent(toolId); linkAgent(toolId)
        expect: port().countByToolId(toolId) == 2L
    }
}
// FakeAgentCountByToolPortSpec extends it (unit); AgentCountByToolAdapterIT extends it on Testcontainers
```
— one behaviour list, two implementations; the fake cannot drift from SQL semantics unnoticed.

**Bad** (real)
```java
public class FakeAgentCountByToolPort implements AgentCountByToolPort, Resettable {

    private final Map<UUID, Long> counts = new HashMap<>();

    public void setCount(final UUID toolId, final long count) {
        counts.put(toolId, count);
    }

    @Override
    public long countByToolId(final UUID toolId) {
        return counts.getOrDefault(toolId, 0L);
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakeAgentCountByToolPort.java:17-29` — no contract spec; the real adapter's soft-delete and join semantics (`AgentCountByToolQueryIT.groovy:50-60`) are proven only for the real side.

### SP1 — A bean overridden with @TestBean in several classes uses the identical field name
**Good** (real)
```java
class ProviderTagsIT extends AbstractIT {

    @TestBean
    ConnectionTestPort connectionTestPort;

    static ConnectionTestPort connectionTestPort() {
        return new FakeConnectionTestPort();
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/ProviderTagsIT.java:20-27` — same field name `connectionTestPort` as `LlmProviderControllerIT.java:33-34`, `ProviderFallbackIT:26`, `SecurityIT:40`; all 31 `@TestBean` files use one name per port type (checked).

**Bad** (n/a) — no `@TestBean` on master overrides the same type under two field names.

### SP2 — A @TestBean/fake replaces the bean bare; never override a bean whose advice the IT asserts
**Good** (real)
```java
@TestConfiguration
public class FakePortsConfig {

    @Bean
    @Primary
    ActiveSessionCountPort fakeActiveSessionCountPort() {
        return new FakeActiveSessionCountPort();
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/support/FakePortsConfig.java:17-24` — plain outbound-port fakes; the replaced real beans (`AgentCountByToolAdapter`, `AgentCountByProviderAdapter`, `HttpConnectionTester`) carry no `@Transactional/@Cacheable/@Retryable/@PreAuthorize` (checked), so no advice is lost.

**Bad** (n/a) — no override of an advised bean found on master.

### SP3 — Never @Transactional on a RANDOM_PORT IT; isolation comes from DatabaseResetExtension
**Good** (real)
```java
public class DatabaseResetExtension implements BeforeEachCallback {

    @Override
    public void beforeEach(final ExtensionContext ctx) {
        AruviiTestReset.resetDatabase(SpringExtension.getApplicationContext(ctx));
    }
}
```
`aruvii-test-support/src/main/java/ai/aruvii/testsupport/DatabaseResetExtension.java:26-32` — restores a snapshot before each method, which works whatever thread the server committed on. 0 `@Transactional` in any `src/integrationTest` on master.

**Bad** (adapted from Spring Boot §with-running-server (R22); `NEEDS COMPILE CHECK`)
```java
@Transactional
class AgentEvalControllerIT extends AbstractIT {

    @Test
    void shouldCreateRun() {
        http.post().uri("/api/agents/{id}/evals", agentId).header(AUTHORIZATION, adminAuth).exchange();
        // server thread already committed — this "rollback" undoes nothing it wrote
    }
```
— the test's transaction is not the server's; rows leak into the next test.

### SP4 — In @DataJpaTest specs call em.flush() before asserting a constraint or write
**Good** (real)
```groovy
    def "the same agent cannot hold the tool twice, so the link count is an agent count"() {
        given: "an agent already wired to the tool"
        def agentId = insertAgent(workspaceId, "double")
        link(agentId, toolId)
        em.flush()

        when: "the same pair is inserted again"
        link(agentId, toolId)
        em.flush()

        then: "agent_tool_links is keyed on (agent_id, tool_id) — the query needs no DISTINCT"
        thrown(Exception)
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:62-73` — the flush inside `when:` is what makes Postgres see the duplicate. (Unbound `thrown(Exception)` is a K19 Bad.)

**Bad** (adapted from Spring Boot §data-jpa (R22); `NEEDS COMPILE CHECK`)
```groovy
    def "a second platform-wide row for the same model is refused"() {
        given: persist(null, "gpt-5", "1.00")
        when:  persist(null, "gpt-5", "2.00")
        then:  thrown(Exception)   // never thrown: the insert sits in the persistence context, rolled back unflushed
    }
```
— master's real version flushes (`PricingOverrideRepositoryIT.groovy:100-105`); every constraint spec found does.

### SP5 — Slice tests use @AutoConfigureTestDatabase(replace = NONE) plus the singleton initializer
**Good** (real)
```groovy
@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE)
@ContextConfiguration(initializers = AruviiTestcontainersInitializer)
abstract class AgentsRepositoryIT extends Specification {

    @Autowired
    TestEntityManager em
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentsRepositoryIT.groovy:23-29` — real Postgres from the singleton; javadoc `:16-18` says why NONE is load-bearing.

**Bad** (adapted from Spring Boot §data-jpa (R22); `NEEDS COMPILE CHECK`)
```groovy
@DataJpaTest
abstract class AgentsRepositoryIT extends Specification {
```
— without `replace = NONE` Boot swaps in an embedded DB (or fails with none on the classpath). Every `@DataJpaTest` on master complies (7 files checked).

### SP6 — No @DirtiesContext without a one-line reason
**Good** (adapted from Spring `@DirtiesContext` docs (R22); `NEEDS COMPILE CHECK`)
```java
// The SSRF allowlist resolves once at construction (D11); this class changes it, so the context must not be reused.
@DirtiesContext
class NotificationTestSsrfAllowlistIT extends AbstractIT {
```
— reason names what is mutated and why reuse would lie. (Master avoids the need: the class runs in its own config.)

**Bad** (n/a) — 0 `@DirtiesContext` in any test source on master.

### SP7 — When ITs slow or connections grow, log the context cache at DEBUG and count first
**Good** (adapted from Spring caching.html (R22); `NEEDS COMPILE CHECK`)
```yaml
# aruvii-api/src/integrationTest/resources/application-it.yml — temporary, while diagnosing
logging:
  level:
    org.springframework.test.context.cache: DEBUG
```
— prints cache size/hit/miss so the context count is measured, not estimated.

**Bad** (real)
```java
    // configuration (~23 in aruvii-api alone — every @Import / @MockitoBean / @TestPropertySource
    // makes a new cache key), none are evicted below the cache's 32-entry default, and each holds a
    // Hikari pool that idles at application.yml's minimum-idle of 5. 23 x 5 = 115 idle connections
    ...
                    .withCommand("postgres", "-c", "max_connections=300");
```
`aruvii-test-support/src/main/java/ai/aruvii/testsupport/AruviiTestcontainersInitializer.java:43-45,54` — limit raised on an approximate ("~23") count; no cache logging configured anywhere on master.

### SP8 — Shared IT properties go in the singleton initializer, never per-class @DynamicPropertySource
**Good** (real)
```java
    public void initialize(ConfigurableApplicationContext ctx) {
        TestPropertyValues.of(
                "spring.datasource.url=" + POSTGRES.getJdbcUrl(),
                "spring.datasource.username=" + POSTGRES.getUsername(),
                "spring.datasource.password=" + POSTGRES.getPassword(),
                "spring.data.redis.host=" + REDIS.getHost(),
                "spring.data.redis.port=" + REDIS.getMappedPort(TestConstants.REDIS_PORT),
```
`aruvii-test-support/src/main/java/ai/aruvii/testsupport/AruviiTestcontainersInitializer.java:76-82` — one property set for every IT, one cache key.

**Bad** (real)
```java
    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url",      postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
        SharedRedis.registerProperties(r);
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:60-66` — per-class properties enter the cache key (documented bootstrap exception); also `UiModelSwapE2EIT.java`.

### SP9 — Redis consumers, schedulers and other lifecycle beans stay pauseable
**Good** (adapted from Spring context-pausing.html (R22); `NEEDS COMPILE CHECK`)
```java
public class ChatStreamConsumer implements SmartLifecycle {
    @Override public void start() { ensureGroup(); running.set(true); loopThread = Thread.ofPlatform().start(this::loop); }
    @Override public void stop()  { running.set(false); if (loopThread != null) loopThread.interrupt(); }
    @Override public boolean isRunning() { return running.get(); }
    // isPauseable() defaults to true: an idle cached test context stops reading the stream
}
```
— Spring stops it when the context is parked in the cache and restarts it on reuse.

**Bad** (real)
```java
    @EventListener(ApplicationReadyEvent.class)
    void start() {
        ensureGroup();
        running.set(true);
        loopThread = Thread.ofPlatform().name("chat-stream-consumer").daemon(false).start(this::loop);
        log.info("Started chat stream consumer on group={} consumer={}", CONSUMER_GROUP, consumerIdentity.name());
    }

    @PreDestroy
    void stop() {
```
`aruvii-worker/src/main/java/ai/aruvii/worker/chat/ChatStreamConsumer.java:73-82` — not a Lifecycle bean, so every cached worker context keeps consuming until JVM exit; same in `EvalStreamConsumer.java:83` (and TaskStreamConsumer).

### SP10 — No preemptive timeout (assertTimeoutPreemptively) in a transactional test
**Good** (adapted from Spring tx.html §preemptive timeouts (R22); `NEEDS COMPILE CHECK`)
```groovy
    @Timeout(10)   // Spock runs the feature on the test thread and interrupts it — the tx stays bound
    def "a run past its deadline is sweepable"() {
```
— timeout without moving the body to another thread.

**Bad** (adapted; `NEEDS COMPILE CHECK`)
```java
    @Test
    void shouldFindSweepableRuns() {
        assertTimeoutPreemptively(Duration.ofSeconds(10), () -> repo.findSweepable(now)); // new thread: no tx, no rollback
    }
```
— 0 `assertTimeoutPreemptively` on master.

### SP11 — No explicit @ComponentScan on the @SpringBootApplication/configuration slices find
**Good** (real)
```groovy
 * <p>No @ComponentScan: a @DataJpaTest must not drag the application services and their ports into
 * the context. The adapters under test are constructed by hand from the real repositories.
 */
@SpringBootConfiguration
@EnableAutoConfiguration
class AgentsJpaTestApplication {
}
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/AgentsJpaTestApplication.groovy:14-20` — slice filters stay intact. Production: `AruviiApiApplication.java:7` carries none.

**Bad** (real, latent)
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan("ai.aruvii.chat")
@EnableJpaRepositories(["ai.aruvii.chat.infrastructure.repository",
                        "ai.aruvii.agents.infrastructure.repository"])
class ChatTestApplication {
```
`aruvii-chat/src/integrationTest/groovy/ai/aruvii/chat/ChatTestApplication.groovy:38-44` — used by `@SpringBootTest` today (justified at `:21-22`), but any `@DataJpaTest` added in aruvii-chat would find it and load every service.

## spock.md

### K1 — Mock-argument closure: plain lines (each asserted); many fields → verifyAll(it, Type)
**Good** (real)
```groovy
        then: "the new version is saved as current"
        1 * versionRepo.save({ PricingVersionEntity v ->
            v.source == "litellm"
            v.notes == "weekly refresh"
            v.createdBy == actor
            v.current
        }) >> { PricingVersionEntity v -> v.setId(versionId); v }
```
`aruvii-infra/src/test/groovy/ai/aruvii/infra/adapter/PricingSyncAdapterSpec.groovy:41-47` — plain top-level lines; Spock ≥1.3 asserts each one.

**Bad** (real)
```groovy
        1 * repo.save({ FeedbackEntity e ->
            assert e.messageId == messageId
            assert e.createdBy == userId
            assert e.agentId == agentId
            assert e.rating == 1
            assert e.comment == "answered the question"
            true
        }) >> { FeedbackEntity e -> e }
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:63-70` — pre-1.3 `assert … true` ritual, and five fields stop at the first failure; `verifyAll(it, FeedbackEntity) { … }` reports all. 49 closures end in a bare `true` on master.

### K2 — Return-and-verify is one interaction: 1 * repo.save(_) >> saved
**Good** (real)
```groovy
        then: "swapping these two reports a passing suite as failing"
        1 * runRepo.save({ AgentEvalRunEntity e ->
            assert e.passCount == 7
            assert e.failCount == 3
            true
        }) >> { AgentEvalRunEntity e -> e }
```
`aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/AgentEvalRepositoryAdapterSpec.groovy:100-105` — count, argument check and return value in one interaction.

**Bad** (adapted from Spock interaction_based_testing.adoc:734-746; `NEEDS COMPILE CHECK`)
```groovy
        given:
        runRepo.save(_) >> { AgentEvalRunEntity e -> e }
        when:
        def saved = adapter.saveRun(run)
        then:
        1 * runRepo.save(_)          // overrides the given: stub — save now returns null
        saved.passCount() == 7       // NPE
```
— the then: interaction wins; the stub is dead. Heuristic scan of master found no live case.

### K2b — Verified interactions match real values or a field constraint; _ only when not promised
**Good** (real)
```groovy
        then: "scoping by message alone would clear every other user's rating of it"
        1 * repo.deleteByMessageIdAndCreatedBy(messageId, userId)
        1 * repo.save(_) >> { FeedbackEntity e -> e }
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:52-54` — the promise (scope) is matched by real values; save's argument is not this feature's promise, so `_`.

**Bad** (real)
```groovy
        then: "a step with no parent is unreachable from its pipeline"
        1 * stepRepo.deleteByPipelineId(_)
        1 * pipelineRepo.getReferenceById(pipelineId) >> parent
        2 * stepRepo.save({ PipelineStepEntity e -> e.pipeline.is(parent) }) >> { PipelineStepEntity e -> e }
```
`aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/PipelineRepositoryAdapterSpec.groovy:154-157` — deleting another pipeline's steps would pass; the id is known, use `pipelineId`.

### K3 — A Stub() never gets a call count; verified → Mock(). Stubs return empty, not null
**Good** (real)
```groovy
        TrustedCertificatesPort trust = Mock()
        ...
        then: "the unchanged path was exercised, not the pinned one"
        1 * trust.currentSslContext() >> globalContext
        0 * trust.allPems()
    ...
        TrustedCertificatesPort trust = Stub(TrustedCertificatesPort) {
            allPems() >> []
            currentSslContext() >> SSLContext.getDefault()
        }
```
`aruvii-worker/src/test/groovy/ai/aruvii/worker/llm/AdapterHttpHelperSpec.groovy:60,66-68,74-77` — Mock where calls are the assertion, Stub (returning `[]`) where they are not.

**Bad** (adapted from Spock interaction_based_testing.adoc:785-788; `NEEDS COMPILE CHECK`)
```groovy
        UserRepository userRepo = Stub()
        ...
        then:
        1 * userRepo.findById(callerId) >> Optional.of(user)   // InvalidSpecException: Stub cannot have cardinality
```
— Spock rejects it at run time, so none survive on master.

### K4 — Assert only promised interactions; 0 * _ only when "nothing else" is the behaviour
**Good** (real)
```groovy
        then: "reaching the repository with an unknown agent would create orphaned rows"
        thrown(AgentNotFoundException)

        and: "and nothing is written or read past the guard"
        0 * evalRepository._
        0 * testCaseRepository._
```
`aruvii-agents/src/test/groovy/ai/aruvii/agents/application/AgentEvalServiceSpec.groovy:49-54` — "nothing past the guard" is the feature's promise, so the blanket zero is earned.

**Bad** (real)
```groovy
    def "every field reaches its own column"() {
        when: "a rating with a comment is submitted"
        adapter.upsert(feedback(1))

        then: "message, session and agent are three distinct ids in the fixture"
        1 * repo.deleteByMessageIdAndCreatedBy(_, _)
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/FeedbackAdapterSpec.groovy:57-62` — the delete is not what this feature promises (that is `:48-55`'s job); counting it here couples the feature to an unrelated call.

### K5 — Exact count only when N is the contract; 0 * for must-not-happen; never count logs/metrics/retries
**Good** (real)
```groovy
    def "a refused creation writes no audit row"() {
        when: "a SUPER_ADMIN asks for a PLATFORM_ADMIN key, a role the platform roles forbid"
        service.create(new CreateApiKeyRequest("ci", null, "PLATFORM_ADMIN", null, null), callerId, "203.0.113.7")

        then: "creation is refused and nothing is audited"
        thrown(AruviiException)
        0 * audit.save(_)
    }
```
`aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:80-87` — 0 for must-not-happen; sibling `:50-51` uses `1 *` because "exactly one audit row" is AC-14.

**Bad** (real)
```groovy
        then: "the agent exists"
        1 * agentRegistry.get(agentId) >> agent()
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:67-68` — counts a read; calling it twice harms nothing, so `1 *` is not the contract (a stub suffices). 254 lines in 36 files count a find/get/exists/count/load/read/is call this way.

### K6 — Data tables: | inputs, || before expected; #var in name; no @Unroll
**Good** (real)
```groovy
    def "results per search #topK is used as #expected"() {
        when: "the operator's topK is read"
        final var config = valid(withValue('topK', topK))

        then: "it is taken as written"
        config.topK() == expected

        where: "absent and null both mean the default"
        topK || expected
        null || 5
        1    || 1
        12   || 12
```
`aruvii-tools/src/test/groovy/ai/aruvii/tools/domain/RagToolConfigSpec.groovy:23-34` — `||` splits input from expected, iterations named.

**Bad** (real)
```groovy
    @Unroll
    def "AC-25/26: a #scope key is refused on an admin-only handler for #method"() {
```
`aruvii-api/src/test/groovy/ai/aruvii/api/security/ApiKeyScopeInterceptorSpec.groovy:54-55` — `@Unroll` is the default since Spock 2.0; 11 occurrences on master.

### K7 — where: reads only @Shared/static fields; build mocks in given: from a plain discriminator
**Good** (real)
```groovy
    @Shared
    UUID agentId = UUID.randomUUID()
    @Shared
    UUID runId = UUID.randomUUID()
    ...
        where: "every method that guards on the agent"
        call << [
            { it.createTestCase(agentId, request(), userId) },
            { it.listTestCases(agentId) },
```
`aruvii-agents/src/test/groovy/ai/aruvii/agents/application/AgentEvalServiceSpec.groovy:35-38,56-59` — the ids the table reads are `@Shared` (immutable UUIDs).

**Bad** (adapted from Spock data_driven_testing.adoc:100; `NEEDS COMPILE CHECK`)
```groovy
    AgentRepository agentRepository = Mock()
    ...
        where:
        repo << [agentRepository]   // instance field: Spock refuses (only @Shared/static readable in where:)
```
— put `exists << [true, false]` in the table and stub `agentRepository.existsById(_) >> exists` in given:.

### K8 — A data-driven feature tests one rule: no if on a column; throws and returns split
**Good** (real)
```groovy
    def "results per search #topK is used as #expected"() {
    ...
    def "results per search #topK is refused, never clamped"() {
        when: "a value outside a whole number 1-50 is read"
        final var parsed = RagToolConfig.from([topK: topK])

        then: "the field is named so the save, the search and the UI all report the same thing"
        parsed == new RagToolConfig.Invalid(RagConfigField.TOP_K)

        where: "the rows from RAG-AC-11 and RAG-AC-17"
        topK << [0, 51, 99, -1, 2.5, '12', true]
```
`aruvii-tools/src/test/groovy/ai/aruvii/tools/domain/RagToolConfigSpec.groovy:23,39-47` — accepted and refused values are two features, each one rule.

**Bad** (adapted from spock-best-practices data-driven :205-255; `NEEDS COMPILE CHECK`)
```groovy
    def "topK #topK"() {
        when: def parsed = RagToolConfig.from([topK: topK])
        then:
        if (valid) { assert parsed.topK() == topK } else { assert parsed instanceof RagToolConfig.Invalid }
        where:
        topK | valid
        12   | true
        51   | false
```
— branching on a column hides two rules in one feature. No live case on master.

### K9 — @Shared only for expensive read-only resources; never mocks or mutable state
**Good** (real)
```groovy
    @Shared
    @AutoCleanup("stop")
    WireMockServer wireMock = new WireMockServer(
        WireMockConfiguration.options().dynamicPort().dynamicHttpsPort())

    HttpExchangePort exchange = new JdkHttpExchange(Clock.systemUTC())

    def setupSpec() {
        wireMock.start()
    }

    def setup() {
        wireMock.resetAll()
```
`aruvii-providers/src/test/groovy/ai/aruvii/providers/infrastructure/JdkHttpExchangeSpec.groovy:33-45` — expensive server shared and reset per feature; subject is a fresh instance field.

**Bad** (real, mild)
```groovy
    @Shared
    CustomPiiEndpointClient client

    def setupSpec() {
        wireMock.start()
        client = new CustomPiiEndpointClient(restClient(),
            SsrfGuard.seededWith(["localhost"], InetAddress::getAllByName).guard())
    }
```
`aruvii-guardrails/src/test/groovy/ai/aruvii/guardrails/infrastructure/CustomPiiEndpointClientSpec.groovy:42-49` — the class under test is shared across features; cheap to build, so it should be an instance field.

### K10 — Interactions live in the feature's own blocks, never hidden in helpers
**Good** (real)
```groovy
    def "a null aggregate from an empty window reaches the caller as zero, not as a null"() {
        given:
        jdbc.queryForObject(_, _ as Class, *_) >> null
        jdbc.query(_, _ as RowMapper, *_) >> []
        jdbc.queryForList(_, String, *_) >> []
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/ConversationAnalyticsAdapterSpec.groovy:63-67` — the stubs the feature depends on are visible in its given:.

**Bad** (real)
```groovy
    def "the feedback window is a JOIN condition, not a WHERE clause"() {
        given: "a September report is requested"
        stubTheOtherFourMetrics()
    ...
    private void stubTheOtherFourMetrics() {
        jdbc.queryForObject(_, Long, _, _) >> 0L
        jdbc.queryForObject(_, Double, _, _) >> 0.0d
        jdbc.queryForList(_, String, _, _) >> []
    }
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/infrastructure/adapter/ConversationAnalyticsWindowSpec.groovy:47-49,85-89` — interactions hidden in a helper; 14 such stub lines in helpers on master (also `ConversationAnalyticsTopicsSpec.stubAggregates:159`). 0 `@Verify`/`@VerifyAll` helpers.

### K11 — Variables an interaction uses are declared before when:, never assigned in when:
**Good** (real)
```groovy
        given: "a place to capture the audit entry"
        AuditLogEntry written = null

        when: "a SUPER_ADMIN creates a platform-wide ADMIN key"
        def created = service.create(new CreateApiKeyRequest("ci", null, "SUPER_ADMIN", null, "ADMIN"), callerId, "203.0.113.7")

        then: "the audit port receives exactly one entry"
        1 * audit.save(_) >> { AuditLogEntry e -> written = e; e }
```
`aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:44-51` — `written` exists before the hoisted interaction runs; `created` (a when: variable) is only read in plain conditions.

**Bad** (adapted from Spock interaction_based_testing.adoc:402-425; `NEEDS COMPILE CHECK`)
```groovy
        when:
        def created = service.create(request, callerId, "203.0.113.7")
        then:
        1 * audit.save({ it.entityId() == created.id() })   // hoisted before when: — created is not yet set
```
— no live case on master (heuristic scan).

### K12 — Several fields of one result: verifyAll(obj){…}; with(obj){…} if first-failure is fine; never Groovy .with{}
**Good** (real)
```groovy
        and: "all twelve fields survive the hop, in the right slots"
        with(stats.first()) {
            it.agentId() == agentId
            it.workspaceId() == workspaceId
            it.date() == day
            it.totalRuns() == 3
            it.totalInputTokens() == 1_000L
            it.totalOutputTokens() == 2_000L
            it.totalCostUsd() == new BigDecimal("1.25")
```
`aruvii-infra/src/test/groovy/ai/aruvii/infra/adapter/AgentDailyStatsAdapterSpec.groovy:56-64` — Spock `with()` asserts each line (first failure only; `verifyAll` would be better for twelve fields — 0 uses on master).

**Bad** (real)
```groovy
    def "a usage carries the four counts it was given"() {
        expect: "each accessor returns the count it was constructed with"
        new TokenUsage(11, 22, 33, 5).with {
            inputTokens() == 11 && outputTokens() == 22 && totalTokens() == 33 && cachedInputTokens() == 5
        }
    }
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/llm/TokenUsageSpec.groovy:29-34` — Groovy `.with{}`: only its `&&`-chained return value is checked, one opaque condition; `verifyAll(new TokenUsage(…)) { … }` per field.

### K13 — Assert call order only when order is the contract, via consecutive then: blocks
**Good** (real)
```groovy
    def "the lease is released before the row is closed"() {
        when:
        runner.finalizeTurn(new TurnOutcome.Completed("STOP"), ref, tally)

        then: """completeInteractionSafely chose this order and recorded why: a failed write must not
                 leave this process renewing a run that has finished."""
        1 * leases.release(interactionId)

        then:
        1 * interactions.completeInteractionIfInProgress(_, _, _) >> true
    }
```
`aruvii-worker/src/test/groovy/ai/aruvii/worker/chat/TurnRunnerFinalizeSpec.groovy:159-169` — order is the named contract; two then: blocks enforce it.

**Bad** (adapted from Spock interaction_based_testing.adoc:513-536; `NEEDS COMPILE CHECK`)
```groovy
        then: "the lease is released before the row is closed"
        1 * leases.release(interactionId)
        and:
        1 * interactions.completeInteractionIfInProgress(_, _, _) >> true   // and: imposes no order — reversed code passes
```
— no live case found on master.

### K14 — Spock ignores Jupiter parallel config; isolate global-state specs with @spock.lang.Isolated / @ResourceLock
**Good** (adapted from Spock parallel_execution docs; `NEEDS COMPILE CHECK`)
```groovy
@spock.lang.Isolated("attaches an appender to SessionService's logback logger and changes its level")
class SessionServiceSpec extends Specification {
```
— Spock's own annotation; Jupiter `@Isolated`/`@Execution` would be ignored. 0 uses of either on master; no `SpockConfig.groovy` → Spock specs run sequentially today.

**Bad** (real, latent)
```groovy
class SessionServiceSpec extends Specification {
    ...
    def setup() {
        logger = LoggerFactory.getLogger(SessionService) as Logger
        appender = new ListAppender<>()
        appender.start()
        logger.addAppender(appender)
        logger.level = Level.DEBUG
    }
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:36,51-57` — mutates a process-global logger with no isolation; safe only while Spock parallelism stays off.

### K15 — Spring-context specs prefer fake ports; @SpringBean only at an external boundary
**Good** (real)
```groovy
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableAruviiSpec
@Import(FailableAuditLogConfig)
class ApiKeyPrivilegeContainmentIT extends Specification {
```
`aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/ApiKeyPrivilegeContainmentIT.groovy:37-40` — a shared config wraps the real `AuditLogPort` (`FailableAuditLogConfig.java:21-27`); no `@SpringBean`, reusable cache key.

**Bad** (adapted from Spock module_spring.adoc CAUTION; `NEEDS COMPILE CHECK`)
```groovy
class ApiKeyPrivilegeContainmentIT extends Specification {
    @SpringBean
    AuditLogPort audit = Mock()   // owned port mocked; new uncached context for this spec alone
```
— 0 `@SpringBean` on master.

### K16 — cleanup: frees per-feature resources defensively (resource?.close())
**Good** (real)
```groovy
    def setup() {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0)
    ...
        server.start()
    }

    def cleanup() { server?.stop(0) }
```
`aruvii-worker/src/test/groovy/ai/aruvii/worker/llm/OllamaThinkingDisabledSpec.groovy:39-40,49-52` — null-safe if setup failed before assignment.

**Bad** (real)
```groovy
    def cleanup() {
        logger.detachAppender(appender)
    }
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/application/SessionServiceSpec.groovy:59-61` — NPE masks the real failure if `setup()` died before `logger` was set; the DEBUG level set at `:56` is never restored.

### K17 — Never spy the class under test; extract the collaborator and stub/fake it
**Good** (real)
```groovy
    InteractionPort interactions = Mock()
    ChatResponseSink sink = Mock()
    TurnLeaseRegistry leases = Mock()

    TurnRunner runner = new TurnRunner(interactions, sink, leases)
```
`aruvii-worker/src/test/groovy/ai/aruvii/worker/chat/TurnRunnerFinalizeSpec.groovy:23-27` — real subject, doubles only at its ports (contrast `ChatOrchestratorFixture.java:167`, which `spy()`s the same class).

**Bad** (real)
```java
    @Test
    @DisplayName("checkInfra never calls the secret-key methods — AC4")
    void checkInfra_neverTouchesSecretKeyPort() {
        // given
        SetupService spy = spy(service);

        // when
        spy.checkInfra();

        // then
        verify(spy, never()).getOrGenerateSecretKey();
        verify(spy, never()).getEffectiveSecretKey();
    }
```
`aruvii-api/src/test/java/ai/aruvii/api/service/SetupServiceTest.java:357-369` — partial mock of the subject verifying its own methods. Also `ChatOrchestratorFixture.java:102,167`; 4 spy sites on master.

### K18 — Records and value objects are constructed, never Mock()ed
**Good** (real)
```groovy
    private static LlmProvider build(String name, Instant createdAt, boolean archived) {
        new LlmProvider(UUID.randomUUID(), name, ProviderType.ANTHROPIC, [:],
            [], [],
            ProviderStatus.ACTIVE, null, null, null,
            archived, archived ? createdAt : null,
            null, null, createdAt, createdAt,
            null, [])
    }
```
`aruvii-providers/src/test/groovy/ai/aruvii/providers/application/RotationReminderBoundarySpec.groovy:100-107` — the domain record is built with the values the test needs.

**Bad** (real)
```groovy
    private WorkspaceEntity workspace() {
        def workspace = Spy(WorkspaceEntity)
        workspace.getId() >> UUID.randomUUID()
        workspace
    }
```
`aruvii-auth/src/test/groovy/ai/aruvii/auth/application/WorkspaceCallerRoleSpec.groovy:56-60` — a data holder doubled to fake a getter; `new WorkspaceEntity(id: …)` does it.

### K19 — def e = thrown(AruviiException) and assert what matters; noExceptionThrown() for none
**Good** (real)
```groovy
        when: "a SUPER_ADMIN creates a key while the audit store is down"
        service.create(new CreateApiKeyRequest("ci", null, "SUPER_ADMIN", null, null), callerId, "203.0.113.7")

        then: "creation fails with INTERNAL_ERROR"
        def ex = thrown(AruviiException)
        ex.errorCode() == ErrorCode.INTERNAL_ERROR
```
`aruvii-auth/src/test/groovy/ai/aruvii/auth/application/ApiKeyAuditSpec.groovy:72-77` — bound and the error code asserted.

**Bad** (real)
```groovy
        when: "the same pair is inserted again"
        link(agentId, toolId)
        em.flush()

        then: "agent_tool_links is keyed on (agent_id, tool_id) — the query needs no DISTINCT"
        thrown(Exception)
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:68-73` — any exception passes, including one unrelated to the key; bind `DataIntegrityViolationException`/`ConstraintViolationException` and check the constraint name. 69 unbound `thrown(` lines on master (14 of them `thrown(Exception|RuntimeException|Throwable)`) vs 31 bound.

### K20 — A block description says the scenario and the why, never restates the code
**Good** (real)
```groovy
        expect: "@SQLRestriction is what stops a deleted agent blocking a tool delete forever"
        repo.countAgentsByToolId(toolId) == 0L
```
`aruvii-agents/src/integrationTest/groovy/ai/aruvii/agents/repository/AgentCountByToolQueryIT.groovy:58-59` — says why the zero matters, which the code cannot.

**Bad** (real)
```groovy
        when: "it is saved"
        adapter.saveRun(run)
```
`aruvii-agents/src/test/groovy/ai/aruvii/agents/infrastructure/AgentEvalRepositoryAdapterSpec.groovy:120-121` — restates `saveRun`; also `:78-79`.

---

## Tally

42 rules (U 4 · IT 6 · SP 11 · K 21), 84 slots.

| | real | adapted (`NEEDS COMPILE CHECK`) | missing (n/a) |
|---|---|---|---|
| Good | 36 | 6 | 0 |
| Bad | 27 | 12 | 3 |
| **total** | **63** | **18** | **3** |

**No real Good on master:** IT5 (no fake/real contract spec) · SP6 (no `@DirtiesContext` at all) · SP7 (no context-cache logging) · SP9 (no Lifecycle consumer) · SP10 (no timeout anywhere) · K14 (no Spock `@Isolated`/`@ResourceLock`).

**Bad n/a:** SP1 (field names consistent across all 31 `@TestBean` files) · SP2 (no advised bean overridden) · SP6 (0 uses).

**Widely broken on master (counts from `origin/master`, 2026-10-02):**

| rule | what | count |
|---|---|---|
| U4 | `Instant/LocalDate/LocalDateTime/OffsetDateTime.now()` in `src/main` | 242 (79 in `application/`); `UUID.randomUUID()` in `src/main` 58 |
| K5 | exact count on a find/get/exists/count/load/read/is call | 254 lines, 36 files |
| U2 | camelCase `shouldXxx` Spock feature names | 80 (plus 206 `"should …"` sentence names) |
| K19 | unbound `thrown(...)` | 69 (14 of them `Exception/RuntimeException/Throwable`) vs 31 bound |
| K1 | `assert … ; true` argument closures | 49 |
| K10 | stubs inside helper methods | 14 lines |
| K6 | `@Unroll` | 11 |
| K12 | `verifyAll` | 0 uses (rule's preferred form never used) |
| U3 | `Mock()` 105 vs `Stub()` 25 declarations — many Mocks only stubbed (e.g. `RotationReminderBoundarySpec:31-33`); not individually verified |
| IT2/SP8 | per-class `@Container` / `@DynamicPropertySource` | 2 files each (`SetupControllerIT`, `FileToolHandlerS3IT` / `UiModelSwapE2EIT`) |
| IT4b | per-class `@TestBean` for a port `FakePortsConfig` already supplies | 4 (`AgentControllerIT`, `PromptBuilderControllerIT`, `SecurityIT`, `AgentSnapshotLimitIT`) |
