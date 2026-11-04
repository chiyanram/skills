# LLM tests

How to test code that calls a language model without a real model: the scripted fake, the agent loop, agent scenarios
(memory, caching, limits, guards, approval, fallback) and recorded traffic. Read it when you write or review a test
whose code under test calls the model: the scripted fake, the agent loop, agent scenarios or recorded traffic.
Real-model tests and evals are in `llm-live-tests.md`.

Contents: Rules · When X, use Y · Good / Bad (LT2, LT4, LT8) · Decided edges · Review checks

## Rules

- **LT1** — Fake the model behind your own model port with one shared, scripted fake in test-support, because copied
  per-test mocks drift from the protocol and from each other.
- **LT2** — Make the scripted fake fail on an unscripted extra call and on unused steps, because a tolerant fake hides
  a loop that ran too many or too few turns.
- **LT3** — Fail any test that reaches a real model client unless it opts in by name, because an unguarded path spends
  money, runs slowly and flakes.
- **LT4** — Assert on the request the code sent the model, not only on the final answer, because lost tool results
  and broken history show up only in the next call's input.
- **LT5** — Test each provider adapter against a fake HTTP server under the real SDK and assert the request JSON,
  because a model-level fake skips the request mapping that breaks in production.
- **LT6** — Run one shared contract suite on every model adapter, at IT and live, declaring each unsupported
  capability and testing that it throws, because an unchecked opt-out silently drops a parameter.
- **LT7** — Feed tool and validation errors back to the model in tests and assert the run continues, because a
  swallowed error stalls the loop or yields a confident wrong answer.
- **LT8** — Cap the agent loop by turns or requests and test the cap, because an unbounded tool loop turns one model
  misstep into a hung, billed run.
- **LT9** — In streaming tests, script several chunks, assert they join to the final message in order, and bound
  every wait, because streams lose, reorder or hang.
- **LT10** — After an injected provider failure, assert the persisted conversation and side effects, not just the
  reply, because a retry can store a partial reply or run a tool twice.
- **LT11** — Order races with explicit signals, never sleeps, because timing-based tests stop exercising the
  regression and still pass.
- **LS1** — Test the memory window with the real class, asserting the exact window after each message, because
  evicting a tool call without its result makes the provider reject the next request.
- **LS2** — Test compaction with a recording fake summariser, asserting what is kept, what it saw, and that a second
  pass summarises nothing, because repeated compaction rewrites history every turn.
- **LS3** — Assert each model request starts with the previous request's bytes while a fake clock moves, because a
  timestamp or rewritten history silently busts the prompt cache.
- **LS4** — Assert cache markers sit only where the provider allows and no more than its limit, because extra
  breakpoints waste the cache or fail the request.
- **LS5** — Key a response cache on tenant, system prompt and inputs, and never cache an error, because a key on user
  text alone serves one persona's answer to another.
- **LS6** — When a run crosses a usage or spend limit, keep the response that crossed it and count it, because
  dropping it under-counts spend and re-requesting it bills twice.
- **LS7** — Test that a blocking guard stops the run before the model or tool is called, with the rejection text as
  the tool result, because a late guard lets side effects through.
- **LS8** — Test approval by serialising the paused run, restoring it, then approving or rejecting, asserting each
  side effect ran exactly once, because resume re-runs completed tools.
- **LS9** — Test fallback by failing the primary fake, then assert the serving model's name, the failed attempt and
  the price on the serving model, because cost reports book the wrong model.
- **LS10** — Test prompt injection that arrives in a tool result through a whole run, because tool results are where
  untrusted text enters, and a guard on user input alone never sees it.
- **LT12** — If you replay recorded traffic, fail on unplayed or unmatched interactions and never accept near-matches,
  because a stale recording keeps passing after the code stops sending a field.
- **LT13** — Scrub credentials, account ids and vendor headers in a pre-record hook, and pin load-bearing facts in the
  test body, because recordings are committed forever and nobody reviews them.

## When X, use Y

| situation | use | why |
|---|---|---|
| a unit spec, IT or smoke spec reaches the model | the shared `ScriptedChatModel`, scripted per test | one protocol, strict on extra and unused turns (LT1, LT2, TM2) · ledger :621, :622, :38 |
| a test reaches a real provider client without opting in by name | a failure from the real-call guard | LT3 · ledger :623 · the opt-in tier: `llm-live-tests.md` |
| the code builds the next request: history, tool results, system prompt | an assertion on `model.requests` | LT4 · ledger :624 |
| the class under test is a provider adapter | the real SDK against a fake HTTP server, asserting the request JSON, inside the shared contract suite | LT5, LT6 · ledger :625, :626 |
| a tool throws or the model's output fails validation | the error fed back as the tool result, and the run continues | LT7 · ledger :627 |
| the code runs a tool loop | a turn or request cap, and a test where the script outlasts it | LT8 · ledger :628 |
| the code streams | several scripted chunks and a bounded wait | LT9 · ledger :629 |
| the provider fails mid-run | an injected failure, then the stored conversation and side effects | LT10 · ledger :630 · the case itself: C2 (`coverage-design.md`) · ledger :16 |
| the test depends on time | a fixed clock (U1, `unit-tests.md`) | ledger :27 |
| the test depends on which of two concurrent steps runs first | an explicit signal: a latch, an event, a scripted pause | LT11 · ledger :631 |
| the agent keeps a memory window or compacts history | the real window or compactor class, message by message | LS1, LS2 · ledger :632, :633 |
| the provider caches prompts | byte-prefix and cache-marker assertions on the requests | LS3, LS4 · ledger :634, :635 |
| the agent caches responses | a key with tenant, system prompt and inputs; errors never cached | LS5 · ledger :636 |
| the agent enforces a usage or spend limit | the crossing response kept and counted | LS6 · ledger :637 · rate limits before the call: SE8 (`code/references/security.md`) |
| a guard or a human approval sits in the run | the guard before any model or tool call; approval resumed from saved state | LS7, LS8 · ledger :638, :639 |
| a fallback model can answer | the primary fake failing, then name, attempt and price | LS9 · ledger :640 |
| a tool returns text someone outside wrote | an injection test through the whole run | LS10 (ours) · ledger :641 |
| the tests replay recorded provider traffic | strict replay and a pre-record scrub hook | LT12, LT13 · ledger :642, :643 |

Ledger is `research/19-approved-rules.md` in this repo; `:N` is a line. LS10 is ours: no reference project tests
injection through a tool result in a whole run (ledger :641).

## Good / Bad

Every rule's approved pair: [examples/llm-tests.md](examples/llm-tests.md).

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
A loop that runs one turn too many gets an empty answer, and the test still passes. A loop that
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
An extra call throws, and `assertComplete()` fails a run that stopped early. (Real evidence: ledger row LT2.)

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
The answer comes from the script, so the test passes even if the history lost the first tool result.
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
The request is where lost tool results and broken history show up. (Real evidence: ledger row LT4.)

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
The model stopped by itself, so the cap never fired. A model that always calls a tool would loop,
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
The script asks for more turns than allowed, so the cap is what stops the run. (Real evidence: ledger row LT8.)

## Decided edges

- **Skip when** the project never replays recorded traffic: LT12 and LT13 do not apply, and hand-written payloads at
  the fake HTTP server are LT5. — **Do not skip when** any recording is committed: both apply to it. — **Confidence**
  high
- **Skip when** the behaviour needs a real provider's decision, chunking, usage numbers or acceptance: that test is
  in the live tier, `llm-live-tests.md`, opted in by name (LT3). — **Do not skip when** the same flow has agent logic
  of its own: that logic is tested here, with the fake. — **Confidence** high
- **Skip when** no tool returns text that someone outside the system wrote: LS10 does not apply. — **Do not skip
  when** any tool result carries text from a customer, a web page, a file or another system. — **Confidence** medium:
  an ours-rule, with no reference project behind it.

## Review checks

Walk every changed test whose code under test calls the model, and every changed model adapter, fake or recording.

- [ ] LT1 — Find each double of the model port. A `Mock(ChatModelPort)` or a fake class outside test-support is a
  finding (`grep -nE "Mock\(ChatModel|Stub\(ChatModel"`).
- [ ] LT2 — Open the shared fake. A call with no scripted reply that returns a default instead of throwing is a
  finding; a test that does not check for unused steps is a finding.
- [ ] LT3 — Find the guard every real adapter calls before it sends. A real client a test can reach without opting
  in by name is a finding.
- [ ] LT4 — For each test of history, tool results or the system prompt, find the assertion on the request sent. An
  answer-only assertion is a finding.
- [ ] LT5 — For each adapter test, check the real SDK runs against a fake HTTP server and the request JSON is
  asserted. An adapter tested through a model-level fake is a finding.
- [ ] LT6 — Check each adapter's spec subclasses the shared contract suite. A per-provider copy, or an opt-out with
  no test that the capability throws, is a finding.
- [ ] LT7 — For each tool and each validated output, find the test that fails it and asserts the run continues. No
  such test is a finding.
- [ ] LT8 — Find the loop's cap and the test whose script outlasts it. A cap no test reaches is a finding.
- [ ] LT9 — For each streaming test, check it scripts several chunks, asserts order and the joined message, and
  bounds every wait. One chunk or an unbounded wait is a finding.
- [ ] LT10 — For each injected provider failure, find the assertions on the stored conversation and side effects. A
  reply-only assertion is a finding.
- [ ] LT11 — A `sleep` or a timeout used to order two steps is a finding (`grep -nE "sleep\(|Thread\.sleep"`).
- [ ] LS1 — For the memory window, check the real class runs and the exact window is asserted after each message. A
  mocked window, or a tool call evicted without its result, is a finding.
- [ ] LS2 — For compaction, find the assertions on what was kept, on what the summariser saw, and on a second pass.
  A missing one is a finding.
- [ ] LS3 — For prompt caching, find the byte-prefix assertion across requests with a moving fake clock. None is a
  finding.
- [ ] LS4 — For cache markers, find the assertion on where they sit and how many. None is a finding.
- [ ] LS5 — Open the response cache key. A key without tenant or system prompt, or a cached error, is a finding.
- [ ] LS6 — For each usage or spend limit, find the test that the crossing response is kept and counted. None is a
  finding.
- [ ] LS7 — For each blocking guard, find the assertion that no model or tool call happened. None is a finding.
- [ ] LS8 — For each approval, check the test serialises and restores the run and counts each side effect. An
  in-memory resume is a finding.
- [ ] LS9 — For fallback, find the assertions on the serving model's name, the failed attempt and the price. A
  missing one is a finding.
- [ ] LS10 — For each tool that returns outside text, find the injection test through a whole run. A guard tested
  on user input only is a finding.
- [ ] LT12 — Open the replay setup. Accepting unplayed or unmatched interactions, or near-matches, is a finding.
- [ ] LT13 — Open the pre-record hook. An unscrubbed credential, account id or vendor header in a committed recording
  is a finding (`grep -rniE "authorization|api[-_]key|x-request-id"` over the recordings).
