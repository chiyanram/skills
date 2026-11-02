# LLM live tests

How to test against a real model: what earns a live test, how the live job runs, what a live test may assert, and how an
eval scores quality. Read it when you write or review a test that calls a real model provider, or an eval that scores
model quality. Tests with a fake model are in `llm-tests.md`; the tier decision is TM3 in `strategy.md`.

Contents: Rules · When X, use Y · Good / Bad (LT14, LT15, LT17) · Decided edges · Review checks

## Rules

- **LS11** — Live-test only what a fake cannot know, such as provider acceptance, real decisions, real chunking, real
  usage and errors, and keep the agent's own logic in fakes, because live tests cost money every run.
- **LT14** — Run real-model tests in their own job with a pinned small model, a per-call token cap and a protected
  secret, failing when skipped, because a silently skipped suite rots and default models change.
- **LT15** — Assert real-model output only on what the test controls: structure, parsed fields, tool arguments, a
  marker the tool returns, side effects, because exact prose flakes and "not empty" catches nothing.
- **LS13** — In a live test, assert a parameter's effect, not only its acceptance, because a provider accepts a
  dropped field silently.
- **LS15** — Live-test streaming by joining real partials and tool-call deltas into the final message, because real
  chunking differs from every fixture.
- **LS16** — Live-test cache and usage numbers, and the price computed from them, because only the provider reports
  cache-write and cache-read tokens.
- **LT16** — Never retry a failed real-model assertion; retry only transport errors, and test the code's own retry by
  injecting the fault, because blanket reruns hide flaky prompts.
- **LS19** — Give every live test an assertion that can fail, and check its gate does not always skip, because a test
  that never runs or never asserts protects nothing.
- **LS20** — Check each configured model name against the provider, and mark known-excluded names as expected failures
  that must fail, because providers retire models and a fix should be noticed.
- **LT17** — Have an LLM judge give atomic verdicts, count "not sure" as failing, compute the score in tested code, and
  never grade with the generating model, because judge arithmetic and self-grading inflate scores.
- **LT18** — Gate an eval on versioned per-metric thresholds over repeated runs, with an explicit pass-rate or minimum
  rule, because one lucky or unlucky sample decides otherwise.

## When X, use Y

| situation | use | why |
|---|---|---|
| the behaviour is the agent's own logic: loop cap, memory, guards, approval, fallback | the fake tier, `llm-tests.md` | LS11 · ledger :644 |
| the question is whether the provider accepts our schema or parameters | a live test in the shared adapter contract suite (LT6, `llm-tests.md`) | LS11, LT6 · ledger :644, :626 |
| a test calls a real provider | an opt-in by name (LT3), in its own job with a pinned small model, a token cap and a protected secret | LT14, TM3 · ledger :651, :39 |
| the live test checks a tool call | the exact argument JSON and a marker the stub tool returns | LT15 · ledger :653, :647 |
| the live test checks an agent run | the state the run changed: a row, a balance, the routed agent | LT15 · ledger :653, :650 |
| the request sets a parameter: a token limit, a stop sequence | the parameter's effect: a LENGTH finish, a cut text | LS13 · ledger :646 |
| the adapter streams | real chunks joined into the final message, tool-call deltas included | LS15 · ledger :648 |
| the adapter reads cache or usage numbers, or we price a call | the provider's real numbers, and our price from them | LS16 · ledger :649 |
| a live test fails some of the time | no retry of the assertion; an injected transport fault for our own retry | LT16 · ledger :654 |
| a live test has a skip condition | a check that the condition does not always skip, and an assertion that can fail | LS19 · ledger :655 |
| the project configures model names | one live check per configured name; excluded names as expected failures | LS20 · ledger :656 |
| quality is scored, not asserted | an eval: an atomic-verdict judge on another model, gated on versioned thresholds over repeated runs | LT17, LT18 · ledger :657, :658 |

Ledger is `research/19-approved-rules.md` in this repo; `:N` is a line. Which providers and flows run live, and
whether the job runs on every pull request or nightly, is each project's choice, written in its own testing docs.

## Good / Bad

Every rule's approved pair: [examples/llm-live-tests.md](examples/llm-live-tests.md).

### LT14 — A separate live job: pinned small model, token cap, protected secret, fails when skipped

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

### LT15 — Assert real-model output only on what the test controls

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

### LT17 — The judge gives atomic verdicts; code computes the score; "not sure" fails; never self-grade

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

## Decided edges

- **Skip when** the run is the gate: the live tier is opt-in and stays out of it (TM3). — **Do not skip when** prompt
  or provider code changes, or before a release: the live tier must pass then (TM3, ledger :39). — **Confidence** high
- **Skip when** choosing when the live job runs: on every pull request or nightly is the project's choice (LT14,
  ledger :651). — **Do not skip when** the job runs: wherever it runs, it pins the model and the cap and fails when
  skipped (LT14). — **Confidence** high

## Review checks

Walk every changed test that calls a real provider, every changed eval, and the job that runs them.

- [ ] LS11 — For each live test, name what only the provider can show. A live test of the agent's own logic is a
  finding: it belongs in the fake tier.
- [ ] LT14 — Open the live job and the live spec setup. A default model, no token cap, a key outside the protected
  secret store, or a suite that skips when the key is missing is a finding (`grep -nE "@Requires|@IgnoreIf"`).
- [ ] LT15 — For each live assertion, name what the test controls. An exact-prose comparison, or a not-empty check
  standing alone, is a finding.
- [ ] LS13 — For each parameter a live test sets, find the assertion on its effect. Acceptance alone is a finding.
- [ ] LS15 — For each live streaming test, find the join of partials and tool-call deltas into the final message. A
  non-empty check alone is a finding.
- [ ] LS16 — For prompt caching and pricing, find the assertions on the provider's cache and usage numbers and on our
  price. None is a finding.
- [ ] LT16 — A retry annotation or a rerun flag on a live test is a finding (`grep -nE "@Retry|rerun"`). For our own
  retry, find the test that injects the transport fault.
- [ ] LS19 — For each live test, find an assertion that can fail, and for each skip condition, a check that it does
  not always skip. `noExceptionThrown()` as the only assertion is a finding.
- [ ] LS20 — Find one live check per configured model name, and an expected failure for each excluded name. A
  hard-coded name the configuration does not use is a finding.
- [ ] LT17 — Open the judge. A whole-answer score from the judge, a "not sure" counted as a pass, or a judge on the
  generating model is a finding; the scoring arithmetic needs its own test with a scripted judge.
- [ ] LT18 — Open the eval's gate. A threshold in test code, a single run, or no stated pass-rate or minimum rule is a
  finding.
