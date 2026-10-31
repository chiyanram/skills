# 71 — Neutral Good/Bad pairs: LLM testing, Fake model and Agent loop (#133, G34)

Step 3 of the reference process (`research/00-reference-format.md` §"How a domain gets its references"): one Good/Bad
pair for each approved rule that can be misread, for the operator to approve on the review page
(`review/llm-testing-rules.html`), then logged in `research/33-good-bad-approvals.md`.

Rules covered: LT1–LT11, approved 2026-10-31 (`research/19-approved-rules.md`, section "LLM testing"). LT6 carries
its approved change (merged with LS12, the live tier); LT11 carries only "signals, never sleeps".

**Format rules applied** (`00-reference-format.md` §"Good / Bad rules"):
- Bad and Good are generic, in one neutral domain: an `OrderAssistant` that answers questions about orders and calls a `findOrder` tool. No project names. ≤15 lines each.
- Each Good obeys every approved rule and house style: "should …" names (U2a), labelled blocks (U2), Spock, `def` in Groovy, one argument per line only when a call wraps past 120 characters (CV3).
- **How the reference does it** quotes the reference project's real test code at its pinned commit. It is evidence for the operator, not text for the reference: rule 3 keeps real cases in the ledger and research, never in the reference.

**Stand-ins** used throughout:
- `ChatModelPort`, with `ChatReply reply(ChatRequest)`, is the model port;
- `ScriptedChatModel` is the shared fake in test-support (LT1, LT2);
- `orders` is a Spock `Stub(OrderStore)`;
- `ModelRequests` is the real-call guard (LT3);
- `MockWebServer` is OkHttp's fake HTTP server (LT5).

---

### LT1 — One shared scripted fake behind the model port

**Bad** (neutral)
```groovy
def "should answer with the order status"() {
    given:
    def model = Mock(ChatModelPort)
    model.reply(_) >>> [
        new ChatReply(toolCalls: [new ToolCall("findOrder", [orderId: "A-17"])]),
        new ChatReply(text: "Order A-17 has shipped."),
    ]
    def assistant = new OrderAssistant(model, orders)

    expect:
    assistant.ask("Where is A-17?") == "Order A-17 has shipped."
}
```
What goes wrong: every spec rebuilds the model's protocol by hand, a little differently each time. When the port
changes, dozens of hand-made mocks drift apart.

**Good** (neutral)
```groovy
def "should answer with the order status"() {
    given:
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"])
        .thenAnswer("Order A-17 has shipped.")
    def assistant = new OrderAssistant(model, orders)

    expect:
    assistant.ask("Where is A-17?") == "Order A-17 has shipped."
}
```
Why this is right: one fake in test-support speaks the port's protocol once, and every spec scripts it the same way.

**How the reference does it** — spring-ai `advisors/spring-ai-session-advisor/src/test/java/org/springframework/ai/session/advisor/ScriptedChatModel.java:36-46 @b19514195`
```java
/**
 * A model for {@code ChatClient} tests: answers each prompt with the next scripted reply
 * and keeps the prompts it got.
 */
class ScriptedChatModel implements ChatModel {
	private final Deque<Function<Prompt, ChatResponse>> replies = new ArrayDeque<>();
	private final List<Prompt> prompts = new ArrayList<>();
```

### LT2 — The fake fails on an extra call and on unused steps

**Bad** (neutral)
```groovy
class ScriptedChatModel implements ChatModelPort {
    private final Deque<ChatReply> replies = new ArrayDeque<>()

    ChatReply reply(ChatRequest request) {
        replies.poll() ?: new ChatReply(text: "")
    }
}
```
What goes wrong: a loop that runs one turn too many gets an empty answer, and the test still passes. A loop that
stops one turn early leaves a scripted reply unused, and nothing notices.

**Good** (neutral)
```groovy
class ScriptedChatModel implements ChatModelPort {
    private final Deque<ChatReply> replies = new ArrayDeque<>()
    final List<ChatRequest> requests = []

    ChatReply reply(ChatRequest request) {
        requests << request
        def next = replies.poll()
        if (next == null) throw new IllegalStateException("No scripted reply left for request ${requests.size()}")
        next
    }

    void assertComplete() {
        assert replies.isEmpty() : "${replies.size()} scripted replies were never used"
    }
}
```
Why this is right: an extra call throws, and `assertComplete()` fails a run that stopped early.

**How the reference does it** — spring-ai `…/ScriptedChatModel.java:71-78 @b19514195`
```java
public synchronized ChatResponse call(Prompt prompt) {
	this.prompts.add(prompt);
	Function<Prompt, ChatResponse> reply = this.replies.poll();
	if (reply == null) {
		throw new IllegalStateException("No scripted reply left for prompt " + this.prompts.size());
	}
	return reply.apply(prompt);
}
```
Also adk-java `core/src/test/java/com/google/adk/testing/TestLlm.java:197-207 @64ce48c74` ("out of responses"), and
openai-agents `src/agents/testing/model.py:313-319 @cd26bbbc5` (`UnconsumedModelSteps`).

### LT3 — A test that reaches a real model client fails, unless it opts in

**Bad** (neutral)
```groovy
@SpringBootTest
class OrderAssistantSpec extends Specification {
    @Autowired
    OrderAssistant assistant

    def "should answer with the order status"() {
        expect:
        assistant.ask("Where is A-17?").contains("A-17")
    }
}
```
What goes wrong: the context wires the real provider adapter. With a provider key set on a laptop or runner, this calls
the real model: it costs money, runs slowly and flakes, and nothing warns.

**Good** (neutral)
```groovy
// test-support: a global Spock extension, registered once, on for every spec
class RealModelGuardExtension implements IGlobalExtension {
    void visitSpec(SpecInfo spec) {
        def live = spec.isAnnotationPresent(LiveModel)
        spec.allFeatures*.addInterceptor { invocation ->
            ModelRequests.allowed = live
            try {
                invocation.proceed()
            } finally {
                ModelRequests.allowed = true
            }
        }
    }
}
// each real adapter calls ModelRequests.check() before it sends; it throws unless allowed
```
Why this is right: every spec is guarded by default. Only a spec annotated `@LiveModel` may reach a real provider.

**How the reference does it** — openai-agents `tests/conftest.py:129-141 @cd26bbbc5`
```python
@pytest.fixture(autouse=True)
def disable_real_model_clients(monkeypatch, request):
    if request.node.get_closest_marker("allow_call_model_methods"):
        return
    def failing_version(*args, **kwargs):
        pytest.fail("Real models should not be used in tests!")
    monkeypatch.setattr(OpenAIResponsesModel, "get_response", failing_version)
```
pydantic-ai puts the check inside each real model: `check_allow_model_requests()`
(`pydantic_ai_slim/pydantic_ai/models/__init__.py:2642-2643 @79e157e8b`), switched off suite-wide by
`ALLOW_MODEL_REQUESTS = False` (`tests/conftest.py:107`).

### LT4 — Assert on the request sent to the model, not only the answer

**Bad** (neutral)
```groovy
def "should answer a follow-up about a second order"() {
    given:
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"]).thenAnswer("A-17 has shipped.")
        .thenCall("findOrder", [orderId: "B-02"]).thenAnswer("B-02 is packed.")
    def assistant = new OrderAssistant(model, orders)

    when:
    assistant.ask("Where is A-17?")
    def answer = assistant.ask("And B-02?")

    then:
    answer == "B-02 is packed."
}
```
What goes wrong: the answer comes from the script, so the test passes even if the history lost the first tool result.
A real model would never have seen it.

**Good** (neutral)
```groovy
def "should send the whole first exchange with the follow-up"() {
    given:
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"]).thenAnswer("A-17 has shipped.")
        .thenCall("findOrder", [orderId: "B-02"]).thenAnswer("B-02 is packed.")
    def assistant = new OrderAssistant(model, orders)

    when:
    assistant.ask("Where is A-17?")
    assistant.ask("And B-02?")

    then:
    model.requests[2].describe() == ["user: Where is A-17?", "call: findOrder A-17", "result: findOrder A-17",
                                     "assistant: A-17 has shipped.", "user: And B-02?"]
}
```
Why this is right: the request is where lost tool results and broken history show up.

**How the reference does it** — spring-ai `advisors/spring-ai-session-advisor/src/test/java/org/springframework/ai/session/advisor/SessionMemoryAdvisorToolLoopTests.java:49-60 @b19514195`
```java
this.model.thenCall("c1", "Lisbon").thenAnswer("Lisbon: sunny.")
	.thenCall("c2", "Porto").thenAnswer("Porto: rain.");
say(client, "Weather in Lisbon?");
say(client, "And Porto?");
assertThat(ScriptedChatModel.describe(this.model.prompts().get(3))).containsExactly("Weather in Lisbon?",
		"call:c1", "result:c1", "Lisbon: sunny.", "And Porto?", "call:c2", "result:c2");
```
(Lines joined for space; the assertion is verbatim.)

### LT5 — Test each adapter against a fake HTTP server and assert the request JSON

**Bad** (neutral)
```groovy
def "should send the tool to the provider"() {
    given:
    def api = Mock(ProviderApi)
    def adapter = new ProviderChatAdapter(api)

    when:
    adapter.reply(new ChatRequest(text: "Where is A-17?", tools: [FIND_ORDER]))

    then:
    1 * api.createMessage({ it.tools*.name == ["findOrder"] }) >> new MessageResponse(text: "ok")
}
```
What goes wrong: the JSON the adapter writes is never built. A wrong field name, such as `schema` instead of
`input_schema`, still passes, and the provider rejects it in production.

**Good** (neutral)
```groovy
def "should send the tool schema in the provider's request body"() {
    given:
    server.enqueue(new MockResponse().setBody(fixture("provider/text-reply.json")))
    def adapter = new ProviderChatAdapter(server.url("/").toString())

    when:
    adapter.reply(new ChatRequest(text: "Where is A-17?", tools: [FIND_ORDER]))

    then:
    def body = new JsonSlurper().parseText(server.takeRequest().body.readUtf8())
    body.tools[0].name == "findOrder"
    body.tools[0].input_schema.required == ["orderId"]
}
```
Why this is right: the real request mapping and JSON writing run, and the test reads exactly what went on the wire.

**How the reference does it** — adk-java `core/src/test/java/com/google/adk/models/FakeGeminiApiTest.java:44-57 @64ce48c74`
```java
private final FakeGeminiApi api = new FakeGeminiApi();
private final Client client = api.client();

String first = client.models.generateContent(MODEL, "Hi", null).text();
assertThat(api.kinds()).containsExactly(Kind.GENERATE, Kind.GENERATE);
assertThat(api.bodies(Kind.GENERATE).get(0).at("/contents/0/parts/0/text").asText())
    .isEqualTo("Hi");
```
Also langchain4j `MockHttpClient` (`langchain4j-http-client/src/test/java/dev/langchain4j/http/client/MockHttpClient.java:28-30 @709c6fd10`),
and spring-ai `MockWebServer` (`models/spring-ai-anthropic/…/AnthropicChatModelStreamingHttpTests.java:109-124 @b19514195`).

### LT6 — One contract suite every adapter passes; opt-outs are tested to fail

Approved with change: one rule with LS12. The same abstract suite runs at IT against a fake HTTP server, and live
against the provider.

**Bad** (neutral)
```groovy
class FirstProviderAdapterSpec extends Specification {
    def "should call a tool"() { /* written for this provider */ }
    def "should stop at a stop sequence"() { /* … */ }
}

class SecondProviderAdapterSpec extends Specification {
    def "should call tools"() { /* a near-copy that has drifted */ }
    // no stop-sequence feature at all: nobody noticed this provider drops it
}
```
What goes wrong: each copy drifts, and a capability one provider lacks is silently missing instead of declared.

**Good** (neutral)
```groovy
abstract class ChatAdapterContract extends Specification {
    abstract ChatModelPort adapter()
    boolean supportsStopSequences() { true }
    @IgnoreIf({ !instance.supportsStopSequences() })
    def "should stop at a stop sequence"() { /* … */ }

    @IgnoreIf({ instance.supportsStopSequences() })
    def "should reject a stop sequence it cannot send"() {
        when:
        adapter().reply(new ChatRequest(text: "Count to five", stop: ["3"]))

        then:
        thrown(UnsupportedFeatureException)
    }
}
```
Why this is right: every adapter subclasses one suite, and an adapter that cannot send a field must say so and prove it
fails cleanly. A subclass per provider runs it against a fake HTTP server; a `@LiveModel` subclass runs it against the
real provider (LS12).

**How the reference does it** — langchain4j `langchain4j-core/src/test/java/dev/langchain4j/model/chat/common/AbstractBaseChatModelIT.java:1268-1288 @709c6fd10`
```java
@DisabledIf("supportsTools")
protected void should_fail_if_tools_are_not_supported(M model) {
    ChatRequest chatRequest = ChatRequest.builder()
            .messages(UserMessage.from("What is the weather in Munich?"))
            .parameters(ChatRequestParameters.builder().toolSpecifications(WEATHER_TOOL).build())
            .build();
    assertThatThrownBy(() -> chat(model, chatRequest))
            .isExactlyInstanceOf(UnsupportedFeatureException.class)
            .hasMessageContaining("not support");
```
(Shortened; the assertions are verbatim.) A provider opts out with a reason:
`// GPT-5 does not support maxOutputTokens, need to use maxCompletionTokens instead`
(`langchain4j-open-ai/src/test/java/dev/langchain4j/model/openai/common/OpenAiChatModelIT.java:87`).

### LT7 — Tool errors go back to the model, and the run continues

**Bad** (neutral)
```groovy
def "should fail when the order lookup fails"() {
    given:
    orders.find("A-17") >> { throw new IllegalStateException("store down") }
    def model = new ScriptedChatModel().thenCall("findOrder", [orderId: "A-17"])

    when:
    new OrderAssistant(model, orders).ask("Where is A-17?")

    then:
    thrown(IllegalStateException)
}
```
What goes wrong: the test pins the crash as correct. The model never sees the error, so it cannot apologise, retry or
ask the user.

**Good** (neutral)
```groovy
def "should send a failing tool's error to the model and finish the run"() {
    given:
    orders.find("A-17") >> { throw new IllegalStateException("store down") }
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"])
        .thenAnswer("Sorry, I cannot look up A-17 right now.")

    when:
    def answer = new OrderAssistant(model, orders).ask("Where is A-17?")

    then:
    answer == "Sorry, I cannot look up A-17 right now."
    model.requests[1].lastToolResult() == ToolResult.error("findOrder", "store down")
}
```
Why this is right: the error reaches the model as a tool result, and the run ends with an answer.

**How the reference does it** — anthropic-sdk-java `anthropic-java-core/src/test/kotlin/com/anthropic/helpers/BetaToolRunnerTest.kt:155-168 @c0f5915f7`
```kotlin
val expectedToolResponseMessageParam =
    BetaMessageParam.ofUser(BetaMessageContentParam.ofContentBlockParams(listOf(
        BetaContentBlockParam.ofToolResult(
            BetaToolResultBlockParam.builder()
                .toolUseId("toolUseId")
                .content("Error: Tool 'get_the_weather' not found")
                .isError(true)
                .build()))))
```
(Brackets joined for space.) This expected message must be the next request's input.

### LT8 — Cap the loop and test the cap

**Bad** (neutral)
```groovy
def "should stop the loop"() {
    given:
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"])
        .thenAnswer("A-17 has shipped.")

    expect:
    new OrderAssistant(model, orders, maxTurns: 3).ask("Where is A-17?") == "A-17 has shipped."
}
```
What goes wrong: the model stopped by itself, so the cap never fired. A model that always calls a tool would loop,
and bill, forever.

**Good** (neutral)
```groovy
def "should stop at the turn cap when the model keeps calling tools"() {
    given:
    def model = new ScriptedChatModel()
        .thenCall("findOrder", [orderId: "A-17"])
        .thenCall("findOrder", [orderId: "A-17"])
        .thenAnswer("never reached")

    when:
    new OrderAssistant(model, orders, maxTurns: 2).ask("Where is A-17?")

    then:
    thrown(TurnLimitExceeded)
    model.requests.size() == 2
}
```
Why this is right: the script asks for more turns than allowed, so the cap is what stops the run.

**How the reference does it** — adk-java `core/src/test/java/com/google/adk/flows/llmflows/BaseLlmFlowTest.java:230-256 @64ce48c74`
```java
public void run_withFunctionCallsAndMaxSteps_stopsAfterMaxSteps() {
  Content unreachableContent = Content.fromParts(Part.fromText("This should never be returned."));
  TestLlm testLlm = createTestLlm(
      Flowable.just(createLlmResponse(contentWithFunctionCall)),
      Flowable.just(createLlmResponse(contentWithFunctionCall)),
      Flowable.just(createLlmResponse(unreachableContent)));
  BaseLlmFlow baseLlmFlow = createBaseLlmFlow(ImmutableList.of(), ImmutableList.of(), /* maxSteps= */ Optional.of(2));
  List<Event> events = baseLlmFlow.run(invocationContext).toList().blockingGet();
  assertThat(events).hasSize(4);
```
(Shortened; the scripted responses, cap and assertion are verbatim.)

### LT9 — Stream in several chunks, join them in order, bound the wait

**Bad** (neutral)
```groovy
def "should stream the answer"() {
    given:
    def model = new ScriptedChatModel().thenStream("A-17 has shipped.")

    when:
    def chunks = new OrderAssistant(model, orders).stream("Where is A-17?").collectList().block()

    then:
    chunks.join() == "A-17 has shipped."
}
```
What goes wrong: one chunk never crosses a boundary, so joining and ordering are never tested. And `block()` with no
timeout hangs the build when the stream never completes.

**Good** (neutral)
```groovy
def "should join streamed chunks in order into the final answer"() {
    given:
    def model = new ScriptedChatModel().thenStream("A-17 ", "has ", "shipped.")

    when:
    def chunks = new OrderAssistant(model, orders)
        .stream("Where is A-17?")
        .collectList()
        .block(Duration.ofSeconds(5))

    then:
    chunks == ["A-17 ", "has ", "shipped."]
    chunks.join() == "A-17 has shipped."
}
```
Why this is right: three chunks cross two boundaries, order is checked, and the wait is bounded.

**How the reference does it** — langchain4j `langchain4j-core/src/test/java/dev/langchain4j/model/chat/common/AbstractBaseChatModelIT.java:724-741 @709c6fd10`
```java
StringBuilder arguments = new StringBuilder();
for (PartialToolCall toolCall : metadata.partialToolCalls()) {
    assertThat(toolCall.index()).isEqualTo(0);
    assertThat(toolCall.id()).isEqualTo(toolExecutionRequest.id());
    arguments.append(toolCall.partialArguments());
}
assertThat(arguments).hasToString(toolExecutionRequest.arguments());
```
(Shortened.) Contrast: spring-ai's scripted fake "Streams the next reply as one chunk"
(`…/ScriptedChatModel.java:80-84 @b19514195`), so its streaming tests never cross a chunk boundary.

### LT10 — After an injected failure, check the stored conversation and side effects

**Bad** (neutral)
```groovy
def "should retry after the stream drops"() {
    given:
    def model = new ScriptedChatModel()
        .thenStreamThenFail("A-17 ha", new IOException("connection reset"))
        .thenStream("A-17 has shipped.")

    expect:
    assistant(model).ask("Where is A-17?", conversation: "c-1") == "A-17 has shipped."
}
```
What goes wrong: the reply is right, but the stored conversation may hold "A-17 haA-17 has shipped." or two assistant
messages. The next turn sends that history to the model.

**Good** (neutral)
```groovy
def "should keep only the complete reply after a retried stream"() {
    given:
    def model = new ScriptedChatModel()
        .thenStreamThenFail("A-17 ha", new IOException("connection reset"))
        .thenStream("A-17 has shipped.")

    when:
    assistant(model).ask("Where is A-17?", conversation: "c-1")

    then:
    conversations.assistantMessages("c-1") == ["A-17 has shipped."]
    model.requests.size() == 2
}
```
Why this is right: the test checks what was stored, which is what the next turn will send.

**How the reference does it** — mastra `packages/core/src/loop/test-utils/aimock/scenarios/api-error-retry-rollback.scenario.test.ts:71-89 @5480e7b7c`
```ts
fixtures: llm => {
  llm.on({ endpoint: 'chat', sequenceIndex: 0 }, { content: CUT_OFF_REPLY }, midStreamDrop);
  llm.on({ endpoint: 'chat', sequenceIndex: 1 }, { content: FULL_REPLY });
},
expect(await output.text).toBe(FULL_REPLY);
expect(getMock().getRequests()).toHaveLength(2);
expect(await savedAssistantText(memory, 'thread-26857')).toEqual([FULL_REPLY]);
```
(Shortened; the lines are verbatim.)

### LT11 — Order races with explicit signals, never sleeps

Approved with change: only this half. The fixed clock is already U1.

**Bad** (neutral)
```groovy
def "should report the guard's block when it lands after the turn cap"() {
    given:
    def guard = { input -> Thread.sleep(200); GuardVerdict.block("refund looks like fraud") }
    def model = new ScriptedChatModel().thenCall("refundOrder", [orderId: "A-17"])

    when:
    assistant(model, guard, maxTurns: 1).ask("Refund A-17")

    then:
    thrown(GuardBlocked)
}
```
What goes wrong: 200 ms only approximates "after the cap". On a slow runner the guard finishes first, so the test passes
even against the bug it guards.

**Good** (neutral)
```groovy
def "should report the guard's block when it lands after the turn cap"() {
    given:
    def capReached = new CountDownLatch(1)
    def guard = { input -> capReached.await(5, SECONDS); GuardVerdict.block("refund looks like fraud") }
    def model = new ScriptedChatModel().thenCall("refundOrder", [orderId: "A-17"])

    when:
    assistant(model, guard, maxTurns: 1, onTurnCap: { capReached.countDown() }).ask("Refund A-17")

    then:
    thrown(GuardBlocked)
}
```
Why this is right: the latch makes the guard finish only after the cap is reached, on every machine.

**How the reference does it** — openai-agents `tests/test_stream_input_guardrail_timing.py:198-212 @cd26bbbc5`
```python
"""This race must not be ordered with a real-time sleep: a fixed delay only
approximates "the guardrail finishes after max_turns is exceeded", and
under CI load ... the test would observe the correct exception even
against the unpatched (buggy) implementation and silently stop being a
regression test. Instead, an `error_handlers={"max_turns": ...}` hook
... sets an `asyncio.Event` at the precise moment the run loop
establishes current_turn > max_turns."""
max_turns_reached = asyncio.Event()
```
(Docstring shortened with "...".)
