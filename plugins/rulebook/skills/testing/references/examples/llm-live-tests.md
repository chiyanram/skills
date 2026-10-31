# LLM live tests — examples

Every approved Good/Bad pair for the rules in [`../llm-live-tests.md`](../llm-live-tests.md), one per rule id, in one
neutral domain: an `OrderAssistant` that answers questions about orders and calls a `findOrder` tool.

Stand-ins: `@LiveModel` is the opt-in by name (LT3 in `../llm-tests.md`); `liveAdapter()` builds the real provider
adapter with the project's pinned small model; `LiveModels` holds the project's model names; `liveAssistant()` builds
the assistant on the real provider; `ScriptedChatModel` is the shared fake (LT1).

## LS11 — Live-test only what a fake cannot know

**Bad** (neutral)
```groovy
@LiveModel
class OrderAssistantLiveSpec extends Specification {
    def "should stop at the turn cap"() {
        given:
        def assistant = new OrderAssistant(liveAdapter(), orders, maxTurns: 1)

        when:
        assistant.ask("Check A-17, then B-02, then C-33")

        then:
        thrown(TurnLimitExceeded)
    }
}
```
The turn cap is our own code. A real model makes the test slow, paid and flaky: it may answer without
calling a tool, and the cap never fires. The fake tests it exactly (LT8).

**Good** (neutral)
```groovy
@LiveModel
class ProviderAcceptanceLiveSpec extends Specification {
    def "should have the provider accept our tool schema and call the tool"() {
        when:
        def reply = liveAdapter().reply(new ChatRequest(text: "Where is A-17? Use the tool.", tools: [FIND_ORDER]))

        then:
        reply.toolCalls*.name == ["findOrder"]
        reply.toolCalls[0].arguments == [orderId: "A-17"]
    }
}
```
Only the real provider can reject our tool schema, and only a real model decides to call the tool. (Real evidence: ledger row LS11.)

## LT14 — A separate live job: pinned small model, token cap, protected secret, fails when skipped

**Bad** (neutral)
```groovy
@Requires({ env.PROVIDER_API_KEY })
class ProviderContractLiveSpec extends ChatAdapterContract {
    ChatModelPort adapter() {
        new ProviderChatAdapter(System.getenv("PROVIDER_API_KEY"))
    }
}
```
Without the key, the whole suite skips and CI is green. The provider's default model changes under the
test, and nothing caps the tokens.

**Good** (neutral)
```groovy
@LiveModel
class ProviderContractLiveSpec extends ChatAdapterContract {
    def setupSpec() {
        assert System.getenv("PROVIDER_API_KEY") : "live tests need PROVIDER_API_KEY: they fail, never skip"
    }

    ChatModelPort adapter() {
        new ProviderChatAdapter(System.getenv("PROVIDER_API_KEY"), model: LiveModels.SMALL, maxOutputTokens: 256)
    }
}
```
A missing key fails the job, the model is pinned, and every call is capped. The job runs on its own,
with the key held as a protected CI secret. (Real evidence: ledger row LT14.)

## LT15 — Assert real-model output only on what the test controls

**Bad** (neutral)
```groovy
def "should tell the customer the order has shipped"() {
    given:
    orders.find("A-17") >> new Order("A-17", status: "SHIPPED")

    when:
    def answer = new OrderAssistant(liveAdapter(), orders).ask("Where is A-17?")

    then:
    answer == "Your order A-17 has shipped."
}
```
The wording changes with every model and run, so the test flakes. And a model that guessed "shipped"
without calling the tool would pass.

**Good** (neutral)
```groovy
def "should look the order up and use the result"() {
    given:
    orders.find("A-17") >> new Order("A-17", status: "SHIPPED-7Q4")

    when:
    def run = new OrderAssistant(liveAdapter(), orders).run("Where is A-17?")

    then:
    run.toolCalls*.name == ["findOrder"]
    run.toolCalls[0].arguments == [orderId: "A-17"]
    run.answer.contains("SHIPPED-7Q4")
}
```
Exact tool arguments, and a marker no model would guess, prove the tool was called and its result
reached the answer. For an agent that changes state, assert that state instead: the order cancelled once, the balance
moved. (Real evidence: ledger row LT15.)

## LS13 — Assert that a parameter took effect, not only that it was accepted

**Bad** (neutral)
```groovy
def "should accept a max-tokens limit"() {
    when:
    def reply = liveAdapter().reply(new ChatRequest(text: "Describe order A-17 in detail.", maxOutputTokens: 5))

    then:
    reply.text
}
```
An adapter that drops the limit still gets an answer, so the test passes while production pays for
full-length replies.

**Good** (neutral)
```groovy
def "should stop at five output tokens"() {
    when:
    def reply = liveAdapter().reply(new ChatRequest(text: "Describe order A-17 in detail.", maxOutputTokens: 5))

    then:
    reply.usage.outputTokens == 5
    reply.finishReason == FinishReason.LENGTH
}
```
Exactly five tokens and a LENGTH finish prove the limit reached the provider and was obeyed. (Real evidence: ledger row LS13.)

## LS15 — Join real streamed chunks and tool-call deltas into the final message

**Bad** (neutral)
```groovy
def "should stream an answer"() {
    when:
    def chunks = liveAdapter()
        .stream(new ChatRequest(text: "List the states an order goes through."))
        .collectList()
        .block(Duration.ofSeconds(30))

    then:
    !chunks.isEmpty()
}
```
Any stream passes. It never checks that the chunks join, or that only the last chunk carries the finish
reason, which is where real chunking breaks aggregators.

**Good** (neutral)
```groovy
def "should join streamed chunks and tool-call deltas into the final message"() {
    when:
    def events = liveAdapter()
        .stream(new ChatRequest(text: "Where is order A-17? Use the tool.", tools: [FIND_ORDER]))
        .collectList()
        .block(Duration.ofSeconds(30))

    then:
    def last = events.last()
    events.init().every { it.finishReason == null }
    events*.toolCallDelta.findAll().join() == last.toolCalls[0].argumentsJson
    last.toolCalls[0].arguments == [orderId: "A-17"]
}
```
The provider's real chunking runs through our aggregator, and the test checks the joined result. (Real evidence: ledger row LS15.)

## LS16 — Check real cache and usage numbers, and the price we compute from them

**Bad** (neutral)
```groovy
def "should enable prompt caching"() {
    when:
    def reply = liveAdapter().reply(longSystemPromptRequest("Where is A-17?").cached())

    then:
    reply.text
}
```
Caching may be silently off, or priced wrongly, and nothing looks at the provider's cache counts.

**Good** (neutral)
```groovy
def "should read the cache on the second turn and price it right"() {
    given:
    def adapter = liveAdapter()

    when:
    def first = adapter.reply(longSystemPromptRequest("Where is A-17?").cached())
    def second = adapter.reply(longSystemPromptRequest("And B-02?").cached())

    then:
    first.usage.cacheWriteTokens > 0
    second.usage.cacheReadTokens > 0
    pricing.cost(second) == pricing.atPublishedRates(second.usage)
}
```
Only the provider reports cache-write and cache-read tokens, and the test checks our price against
them. (Real evidence: ledger row LS16.)

## LT16 — Never retry a failed assertion; inject the fault and test our own retry

**Bad** (neutral)
```groovy
@Retry(count = 3)
def "should look the order up and use the result"() {
    when:
    def run = new OrderAssistant(liveAdapter(), orders).run("Where is A-17?")

    then:
    run.toolCalls*.name == ["findOrder"]
}
```
A prompt that works one time in three still goes green, so a flaky prompt is never fixed.

**Good** (neutral)
```groovy
def "should retry once after a dropped connection and then succeed"() {
    given:
    def transport = FaultyTransport.failFirst(new ConnectException("connection reset"))
    def adapter = liveAdapter(transport: transport)

    when:
    def reply = adapter.reply(new ChatRequest(text: "Reply with exactly READY."))

    then:
    transport.attempts == 2
    reply.text.trim() == "READY"
}
```
The test fails on a real assertion failure, and the adapter's own retry is proved by injecting one
transport fault before a real call. (Real evidence: ledger row LT16.)

## LS19 — Every live test can fail, and its gate does not always skip

**Bad** (neutral)
```groovy
def "should switch to the small model mid-conversation"() {
    given:
    def assistant = new OrderAssistant(liveAdapter(), orders)

    when:
    assistant.switchModel(LiveModels.SMALL)
    assistant.ask("Where is A-17?")

    then:
    noExceptionThrown()
}
```
It passes when the switch silently did nothing.

**Good** (neutral)
```groovy
def "should send the next request with the small model after a switch"() {
    given:
    def assistant = new OrderAssistant(liveAdapter(), orders)

    when:
    assistant.switchModel(LiveModels.SMALL)
    def reply = assistant.reply("Where is A-17?")

    then:
    reply.servedBy == LiveModels.SMALL
}
```
The test checks what the provider says served the reply. It fails if the switch did nothing. (Real evidence: ledger row LS19.)

## LS20 — Check every configured model name; excluded names must still fail

**Bad** (neutral)
```groovy
def "should answer with the small model"() {
    expect:
    liveAdapter(model: "small-2025-01").reply(new ChatRequest(text: "Reply with OK.")).text.trim() == "OK"
}
```
It checks one hard-coded name. The names production is configured with are never checked, so users
find a retired model first.

**Good** (neutral)
```groovy
def "should get an answer from every configured model"() {
    expect:
    liveAdapter(model: model).reply(new ChatRequest(text: "Reply with OK.", maxOutputTokens: 5)).text.trim() == "OK"

    where:
    model << LiveModels.configured()
}

@FailsWith(ModelNotFound)
def "should still reject the model we excluded as retired"() {
    expect:
    liveAdapter(model: LiveModels.EXCLUDED).reply(new ChatRequest(text: "Reply with OK."))
}
```
Every configured name is checked, and the excluded one must keep failing. If it starts working, the
test fails, so someone notices it can come back. (Real evidence: ledger row LS20.)

## LT17 — The judge gives atomic verdicts; code computes the score; "not sure" fails; never self-grade

**Bad** (neutral)
```groovy
def "should rate the answer as faithful to the order record"() {
    given:
    def judge = new LlmJudge(assistantModel, prompt: "Score from 0 to 1 how faithful this answer is.")

    when:
    def score = judge.score(answer: "A-17 shipped on Monday.", context: orderRecord("A-17"))

    then:
    score >= 0.8
}
```
The model that wrote the answer also grades it, and the score is whatever number the judge returns.
Neither the judge's arithmetic nor the parsing of its reply is tested.

**Good** (neutral)
```groovy
def "should count unsure and missing verdicts as unsupported"() {
    given:
    def judge = new ScriptedChatModel(name: "judge-model")
        .thenAnswer('{"claims": ["shipped", "on Monday", "by courier", "signed for"]}')
        .thenAnswer('{"verdicts": ["SUPPORTED", "NOT_SURE"]}')
    def scorer = new FaithfulnessScorer(judge, answeredBy: "assistant-model")

    when:
    def result = scorer.score(answer: "A-17 shipped on Monday by courier, signed for.", context: orderRecord("A-17"))

    then:
    result.score == 0.25
    result.verdicts*.claim == ["shipped", "on Monday"]
}
```
The judge only splits claims and gives a verdict per claim. Our code does the arithmetic: one
supported claim out of four is 0.25, so NOT_SURE and the two missing verdicts count as unsupported. A scripted judge
makes that arithmetic testable. The scorer refuses a judge whose name equals `answeredBy`. (Real evidence: ledger row LT17.)

## LT18 — Gate an eval on versioned thresholds over repeated runs

**Bad** (neutral)
```groovy
def "should answer order questions well"() {
    given:
    def eval = new OrderAnswersEval(dataset: "evals/order-questions.json")

    when:
    def result = eval.runOnce(liveAssistant())

    then:
    result.averageScore > 0.7
}
```
One run decides, so a lucky run passes and an unlucky one blocks. The threshold lives in test code,
where it is quietly tuned until the test is green.

**Good** (neutral)
```groovy
def "should meet the versioned thresholds over repeated runs"() {
    given:
    def config = EvalConfig.load("evals/order-questions.thresholds.json")
    def eval = new OrderAnswersEval(dataset: "evals/order-questions.json")

    when:
    def runs = (1..config.runs).collect { eval.run(liveAssistant()) }

    then:
    config.metrics.every { metric -> metric.passes(runs*.score(metric.name)) }
}
```
The run count and each metric's rule (a minimum over runs, or a pass rate) live in a versioned file
that changes by review. `passes` treats a non-finite score as a failure. (Real evidence: ledger row LT18.)
