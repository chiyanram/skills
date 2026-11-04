# Integration tests

How an integration test (IT) gets its containers, calls the system, swaps a collaborator and stays isolated inside a
cached Spring context. Read it when you write or review an IT, a fake port, a test slice or a test configuration.

Contents: Rules · When X, use Y · Good / Bad (IT1, IT2, IT4, SP3, SP11) · Decided edges · Review checks

## Rules

- **IT1** — In an IT, prove wiring and contracts (HTTP boundary, SQL on real Postgres, streams, Spring wiring,
  lifecycle), one IT per contract, because ITs that re-run unit-owned branches add slow copies with no new risk.
- **IT2** — Take every IT container from the singleton initializer, never from `@Testcontainers`, `@Container` or
  `@ServiceConnection`, because a cached context can outlive a per-class container that has stopped.
- **IT3** — Call the HTTP API with `RestTestClient` against the real server on `RANDOM_PORT`, never MockMvc,
  MockMvcTester or TestRestTemplate, because MockMvc skips the real servlet stack, filters and error pages.
- **IT4** — In an IT, swap any outbound port except a repository (TM2) for an in-memory fake port bean, never
  `@MockitoBean`, because a mock has no behaviour of its own and couples the IT to calls.
- **TM4** — Give each dependency the system must survive one Toxiproxy IT injecting latency, timeout and a cut;
  assert predictable failure, WARN/ERROR logs and recovery, because an untested outage path can hang or swallow the error.
- **IT5** — Run one contract spec against each fake port and its real adapter, and change it in the same MR as the
  port or adapter, because an untested fake drifts from the real adapter it replaces.
- **SP1** — When several test classes override one bean with `@TestBean`, give the field the identical name in each,
  because a different field name creates a different cached context.
- **SP2** — Override with a `@TestBean` or fake only a bean whose transaction, cache, retry or method-security advice
  the IT does not assert, because the override is a bare object without that advice.
- **SP3** — Take isolation in a `RANDOM_PORT` IT from the shared reset, never from `@Transactional` rollback, because
  server work commits in another thread and never rolls back.
- **SP4** — In a `@DataJpaTest` spec, call `em.flush()` before asserting a constraint or a write, because unflushed
  changes skip the database check and give false positives.
- **SP5** — Give every slice test (`@DataJpaTest`, `@JdbcTest`) `@AutoConfigureTestDatabase(replace = NONE)` and the
  singleton initializer, because Boot otherwise swaps in an embedded database unlike production Postgres.
- **SP6** — Write a one-line reason beside every `@DirtiesContext`, because it closes the context and rebuilds it for
  every later test.
- **SP7** — When ITs slow down or database connections grow, log `org.springframework.test.context.cache` at DEBUG and
  count contexts before raising a limit, because each cached context holds its own pool, so connections grow per context.
- **SP8** — Put shared IT properties in the singleton initializer, never in a per-class `@DynamicPropertySource`,
  because each `@DynamicPropertySource` enters the cache key and forks a context.
- **SP9** — Keep Redis consumers, schedulers and other `SmartLifecycle` beans pauseable, because an unpaused cached
  context keeps consuming during other classes' tests.
- **SP10** — Never use a preemptive timeout (`assertTimeoutPreemptively`) in a transactional test, because the timed
  body runs in another thread and its writes commit.
- **SP11** — Never put an explicit `@ComponentScan` on the `@SpringBootApplication` class, because it disables the
  slice filters, so a slice loads every bean.

## When X, use Y

| the IT needs | use | why |
|---|---|---|
| a container, also in a spec with no Spring context | the singleton initializer's shared container; the spec never starts or stops it (IT2) | a cached context can outlive a per-class container (IT2) |
| to check a branch the unit spec reaches (field validation, error mapping) | the unit spec; the IT keeps one case for the contract (IT1); the tier split is TM1 (`strategy.md`) | ITs that re-run unit-owned branches add slow copies with no new risk (IT1) |
| to replace a collaborator | a fake port bean at an outbound port (IT4); which collaborators to replace is TM2 (`strategy.md`) | a mock has no behaviour of its own and couples the IT to calls (IT4) |
| a repository slice (`@DataJpaTest`, `@JdbcTest`) | `replace = NONE` with the singleton initializer (SP5); `em.flush()` before asserting a write (SP4) | Boot otherwise swaps in an embedded database (SP5); unflushed changes skip the database check (SP4) |
| a timeout in a transactional test | Spock's `@Timeout`, which keeps the feature on the test thread (SP10) | a preemptive timeout runs the body in another thread, where its writes commit (SP10) |
| a component scan for the full `@SpringBootTest` | a separate `@Configuration` that only the full test imports (SP11) | an explicit `@ComponentScan` disables the slice filters, so a slice loads every bean (SP11) |
| to prove the system survives a dependency outage | one Toxiproxy IT per dependency (TM4); the unavailable case of each call is C2 (`coverage-design.md`) | an untested outage path can hang or swallow the error (TM4) |
| to find why ITs slow down or connections grow | the cache logger at DEBUG; the cache holds at most 32 contexts and evicts the least recently used (SP7) | each cached context holds its own pool, so connections grow per context (SP7) |

## Good / Bad

Every rule's pair: [examples/integration-tests.md](examples/integration-tests.md).

### IT1 — Prove the contract once; leave unit-owned branches to the unit spec

**Bad**
```java
    @DisplayName("POST with customerId blank → 400 naming customerId")
    void createOrder_blankCustomerId_returns400() {
        postOrder("""
                { "customerId": "", "lines": [ { "sku": "SKU-1", "quantity": 1 } ] }
                """)
                .expectStatus().isBadRequest()
    ...
    @DisplayName("POST with lines empty → 400 naming lines")
    void createOrder_emptyLines_returns400() {
```
One slow HTTP test per blank field re-runs validation branches that the order validator's unit spec already owns.

**Good**
```groovy
    def "should answer an order the validator refuses with a 400 problem"() {
        when: "a clerk posts an order the validator refuses; which fields it refuses is the unit spec's job"
        def result = http.post()
            .uri("/api/orders")
            .header(HttpHeaders.AUTHORIZATION, login("CLERK"))
            .contentType(MediaType.APPLICATION_JSON)
            .body('{ "customerId": "", "lines": [] }')
            .exchange()
            .returnResult()

        then: "the HTTP contract holds: status 400 as a problem document"
        result.status.value() == 400
        result.responseHeaders.contentType == MediaType.APPLICATION_PROBLEM_JSON
```
One IT proves the refusal-to-400 mapping through the real stack; the field branches stay in the fast unit spec.

### IT2 — Take every container from the singleton initializer

**Bad**
```java
@Testcontainers
class PaymentGatewayIT {
    ...
    @Container
    @SuppressWarnings("resource")
    static final GenericContainer<?> GATEWAY = new GenericContainer<>("example/payment-sandbox:1.4.0")
        .withExposedPorts(GATEWAY_PORT)
        .waitingFor(Wait.forListeningPort());
```
The class starts its own container and stops it when the class ends, outside the shared singleton every other IT uses.

**Good**
```groovy
/**
 * No Spring context, so no @EnableSharedContainers: the gateway sandbox comes from the singleton,
 * the way shared Postgres serves non-Spring ITs, and this spec never starts or stops it.
 */
class PaymentGatewayIT extends Specification {

    @Shared
    String gatewayUrl = SharedContainersInitializer.sharedGatewayUrl()

    PaymentGatewayAdapter gateway = new PaymentGatewayAdapter(gatewayUrl)

    def setupSpec() {
        seedSandboxAccounts(gatewayUrl)
    }
```
The container lives in the shared initializer beside Postgres, so no spec owns its lifecycle and every spec reuses it.

### IT4 — Swap an outbound port for a fake, never a double

**Bad**
```groovy
    def "should send the overdue notice when the reminder runs"() {
        given: "a reminder whose email sender is a Spock double"
        EmailSender emailSender = Stub() {
            send(_) >> true
        }
        def reminder = new OverdueReminder(invoiceRepository, emailSender, clock)
```
The IT replaces an outbound port with a double that has no behaviour of its own, and repeats that stub per feature.

**Good**
```groovy
    @Autowired OverdueReminder reminder
    @Autowired FakeEmailSender emailSender // the EmailSender bean of OutboundFakesConfig

    @Issue(["#123", "AC-2"])
    def "should send one overdue notice when the reminder runs"() {
        given: "an invoice one day past due, and the wired reminder sending through the shared fake"
        saveInvoice(openInvoiceDue(TODAY.minusDays(1)))

        when: "the reminder runs"
        reminder.remindOverdue()

        then: "the fake holds exactly one notice, for this invoice's customer"
        emailSender.sent()*.to() == [CUSTOMER_EMAIL]
```
The subject is the wired bean, and the port is the shared in-memory fake from `OutboundFakesConfig`, with its own
contract spec (IT5), instead of one stub per feature.

### SP3 — Take isolation from the shared reset, never from @Transactional

**Bad**
```java
@Transactional
class InvoiceControllerIT extends AbstractIT {

    @Test
    void shouldPayInvoice() {
        http.post().uri("/api/invoices/{id}/payments", invoiceId).header(AUTHORIZATION, clerkAuth).exchange()
            .expectStatus().isCreated();
        // server thread already committed — this "rollback" undoes nothing it wrote
    }
```
The test's transaction is not the server's, so the payment rows the server committed leak into the next test.

**Good**
```groovy
/**
 * No @Transactional and no per-feature DELETE: @EnableSharedContainers resets the database before
 * every feature, and invoices and payments are not in its keep-list, so both start empty.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnableSharedContainers
class InvoiceControllerIT extends Specification {

    @Autowired
    ApplicationContext applicationContext

    @Autowired
    JdbcTemplate jdbc
```
One reset interceptor owns isolation and runs whatever thread the server committed on; the spec cleans up nothing by
hand.

### SP11 — Keep the component scan off the class a slice finds

**Bad**
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan("com.example.orders")
@EnableJpaRepositories(["com.example.orders.repository",
                        "com.example.orders.billing.repository"])
@EntityScan(["com.example.orders.entity", "com.example.orders.billing.entity"])
class OrdersTestApplication {
```
Any `@DataJpaTest` that finds this class also scans and loads every service, because an explicit scan disables slice filters.

**Good**
```groovy
@SpringBootConfiguration
@EnableAutoConfiguration
@EnableJpaRepositories([
    "com.example.orders.repository",
    "com.example.orders.billing.repository"])
class OrdersTestApplication {
}

/** The services OrdersIT calls. Only OrdersIT imports it, so a slice that finds OrdersTestApplication loads none. */
@Configuration(proxyBeanMethods = false)
@ComponentScan("com.example.orders")
class OrdersServicesConfig {
}
```
The scan moves off the class a slice searches for; only the full `@SpringBootTest` imports the services config.

## Decided edges

- **Do not skip when** a framework guide starts the container with `@Testcontainers` and `@Container`, or wires it
  with `@ServiceConnection`: that default is not used, because the container stops per class and
  `@ServiceConnection` does not set every property the initializer sets (IT2). — **Confidence** high
- **Do not skip when** a guide shows `TestRestTemplate` or `MockMvcTester`, or a check touches the web layer only:
  those alternatives and `@WebMvcTest` are not used, because they conflict with IT3. — **Confidence** high
- **Skip when** no shared fake covers the port: one class may override it with `@TestBean` returning a fake (IT4). —
  **Do not skip when** the shared fake set already holds the port: use the shared set, so the Spring context is
  reused (IT4). — **Confidence** high
- **Do not skip when** a guide's example uses `@MockitoBean`: that default is not used under IT4. For a
  `@SpringBean` in a Spock spec, see K15 (`spock.md`). — **Confidence** high

## Review checks

Walk every changed IT, fake port, test configuration and test-support class.

- [ ] IT1 — For each changed IT feature, name the contract it proves: HTTP boundary, SQL, stream, Spring wiring or
  lifecycle. A feature that re-runs a branch the unit spec owns, or a second IT for one contract, is a finding.
- [ ] IT2 — `grep -nE "@Testcontainers|@Container|@ServiceConnection"`. A hit is a finding.
- [ ] IT3 — `grep -nE "MockMvc|TestRestTemplate"` (this also finds MockMvcTester). A hit is a finding.
- [ ] IT4 — `grep -n "@MockitoBean"`, then open each swapped bean. A hit, a swapped repository (TM2), or a swap that
  is not an outbound port replaced by a real in-memory implementation, is a finding.
- [ ] TM4 — For each dependency the system must survive, find one Toxiproxy IT that injects latency, a timeout and a
  cut, and asserts predictable failure, a WARN/ERROR log and recovery. A missing IT or item is a finding.
- [ ] IT5 — For each new or changed fake port, find a contract spec that runs against the fake and against the real
  adapter on Testcontainers.
  A changed port or real adapter with no change to its contract spec is a finding.
- [ ] SP1 — `grep -n "@TestBean"`. For each overridden type, compare the field name in every class. Two names for
  one type is a finding.
- [ ] SP2 — For each `@TestBean` or fake bean, open the bean it replaces. Transaction, cache, retry or method-security
  advice that the IT asserts is a finding.
- [ ] SP3 — `grep -n "@Transactional"` in every `RANDOM_PORT` IT. A hit is a finding.
- [ ] SP4 — For each `@DataJpaTest` feature that asserts a constraint or a write, find `em.flush()` before the
  assertion. A missing flush is a finding.
- [ ] SP5 — For each `@DataJpaTest` or `@JdbcTest` class, find `replace = NONE` and the singleton initializer. A
  missing one is a finding.
- [ ] SP6 — `grep -n "@DirtiesContext"`. A hit with no one-line reason beside it is a finding.
- [ ] SP7 — For a change that raises a connection limit or a pool size for ITs, find the context count from the cache
  logger. A raised limit with no count is a finding.
- [ ] SP8 — `grep -n "@DynamicPropertySource"`. A hit is a finding.
- [ ] SP9 — For each new or changed Redis consumer, scheduler or other lifecycle bean, confirm Spring can pause it
  while its context is idle in the cache. A loop that stops only at shutdown is a finding.
- [ ] SP10 — `grep -n "assertTimeoutPreemptively"` in every transactional test. A hit is a finding.
- [ ] SP11 — `grep -n "@ComponentScan"` on every `@SpringBootApplication` or `@SpringBootConfiguration` class. A hit
  is a finding.
