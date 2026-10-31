# R41 · How to test each agent scenario right

Ticket: `chiyanram/skills#153` (R41, map #130). Read 2026-10-30. The operator's ask: "how we write tests for agent
coding scenarios right, and learn from the references and best practices". This file is organised **by agent
scenario**: for each one, how the strongest reference projects test it at each tier, and what Aruvii's tests should
be. It builds on `research/69` (R40), which covered the fakes, the loop, streaming and evals; read that first for the
patterns this file only names.

**Operator decisions already taken (#133):** live tests are purpose-built, not smoke specs rerun against a real
provider; smoke keeps the fake LLM server (#576, #608); live tests run on **every PR** first and move to nightly when
that becomes a bottleneck; the rulebook holds generic rules, the project holds its own choices in
`docs/agents/testing.md`.

**Candidates only.** No rule enters a reference without the operator's yes. G34 (#133) decides them.

Contents: §0 sources · §1 the four tiers · §2 scenario by scenario · §3 the kinds of live test · §4 what nobody tests
live · §5 Aruvii · §6 candidate rules LS1–LS20 · §7 open for G34 · §8 method

## 0. Sources

The same ten clones as `research/69` §0, at the same commits: spring-ai `b19514195` (SA), anthropic-sdk-java
`c0f5915f7` (AJ), langchain4j `709c6fd10` (L4J), adk-java `64ce48c74` (ADKJ), openai-agents-python `cd26bbbc5` (OA),
claude-agent-sdk-python `1ea8cb74d` (CA), pydantic-ai `79e157e8b` (PA), adk-python `c501d8eda` (ADKP), langgraph
`6f2df053f` (LG), mastra `5480e7b7c` (MA). Citations are `KEY:path:line`.

Path shorthands used below:
- SA-A = `models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/chat`
- SA-O = `models/spring-ai-openai/src/test/java/org/springframework/ai/openai`
- SA-T = `spring-ai-test/src/main/java/org/springframework/ai/test/chat/client/advisor`
- L4J-C = `langchain4j-core/src/test/java/dev/langchain4j/model/chat/common`
- L4J-S = `langchain4j/src/test/java/dev/langchain4j/service`

## 1. The four tiers

| tier | what is real | what is fake | it answers | in Aruvii today |
|---|---|---|---|---|
| **unit** | the class under test, e.g. the memory window or the loop | the model, behind the port (`research/69` §1) | does our logic do the right thing for a given model reply? | Spock; `FakeAgentChatPort` exists but no test used it (R19, 2026-10-02) |
| **IT** | the adapter, its HTTP client and JSON mapping | the HTTP server, with canned provider bodies | do we build and parse the provider's wire format right? | Testcontainers ITs |
| **smoke** | the deployed stack and UI journey | the model, as a scripted HTTP server | does the product journey hold together? | fake LLM server on Ollama's port (#576, #608) |
| **live** | the provider | nothing | does the real provider accept what we send and give back what we assume? | none yet; every PR to start (#133) |

The references put **almost all behaviour** in the unit tier, and use the live tier only for what a fake cannot
know: what the provider accepts, what it really returns, and what the model really decides (§3).

## 2. Scenario by scenario

Each scenario lists the best fake-tier test found, then whether and how any reference tests it live.

### 2.1 Provider adapter mapping: request JSON, stop reasons, usage

- **Fake tier:** a fake HTTP layer under the real adapter, asserting the request body (`research/69` LT5). The strongest form is one contract suite every adapter must pass: L4J's `AbstractBaseChatModelIT` has 33 methods run against 43 provider classes, with each unsupported capability declared and tested to throw (`L4J:L4J-C/AbstractBaseChatModelIT.java:1269-1286`). spring-ai does the same for the tool loop with 11 subclasses over 5 providers (`SA:SA-T/AbstractToolCallingAdvisorIT.java:275`).
- **Live:** the same contract suite, run against the real provider. It is the backbone of SA's and L4J's live tiers:
  - **Parameter effect, not just acceptance:** `maxOutputTokens(5)` must give exactly 5 output tokens and finish reason LENGTH (`L4J:L4J-C/AbstractBaseChatModelIT.java:1951`, `:396`); a stop sequence must cut the text (`:527`).
  - **Real error mapping:** OpenAI rejects an unknown parameter with "Unknown parameter" (`SA:SA-O/chat/OpenAiChatModelIT.java:895-902`); a bad model id gives a typed error with `terminal_reason == "api_error"` (`CA:e2e-tests/test_error_results.py:17,59`).
  - **Why a fake cannot do it:** a fake accepts whatever the adapter sends. Only the provider rejects a wrong wire name, a schema dialect or a model id.

### 2.2 One model call

- **Fake tier:** a scripted model (`research/69` LT1–LT3).
- **Live:** a known-answer call, "capital of Germany" → `containsIgnoringCase("Berlin")` with finish reason STOP (`L4J:L4J-C/AbstractBaseChatModelIT.java:171,188`), or a forced exact reply, "Say exactly: hello" with `maxTokens(32)` (`AJ:anthropic-java-aws/src/test/kotlin/com/anthropic/aws/backends/AwsLiveTest.kt:19-25`). It is the cheapest proof the whole request–response path works. AJ's live tests exist only for this, across each backend's auth (SigV4, profiles, ADC): a mock cannot check a signature.

### 2.3 Tool-call round trip

- **Fake tier:** scripted tool call then text, asserting the next request carries the tool result (`research/69` LT4).
- **Live:** the model must choose the tool and fill the arguments, and the provider must accept our tool-result message:
  - **exact arguments:** `isEqualToIgnoringWhitespace("{\"city\":\"Munich\"}")`, then the follow-up answer uses the result, `containsIgnoringCase("sun")` (`L4J:L4J-C/AbstractBaseChatModelIT.java:706,786`);
  - **parallel calls:** `L4J:…/AbstractBaseChatModelIT.java:1038,1078`;
  - **a marker from the stub tool:** "30", "10", "15" (`SA:SA-A/AnthropicChatModelIT.java:326`);
  - **verified call on a spied tool:** `verify(tool).add(37, 87)` (`L4J:L4J-S/common/AbstractAiServiceWithToolsIT.java:136`);
  - **a provider quirk only a real model shows:** some models say `stop` while tool calls are pending, so mastra runs an 8-model matrix asserting the loop still completes 5 tool calls (`MA:packages/core/src/agent/__tests__/tool-calls-finish-reason.e2e.test.ts:149`);
  - **strict schemas:** OpenAI used to reject a strict schema with an optional parameter, so SA pins that it is accepted now (`SA:SA-O/chat/OpenAiChatModelIT.java:906`).

### 2.4 Tool errors and loop caps

- **Fake tier:** unknown and throwing tools give an error result the model sees, and the run continues; caps are tested by scripting more turns than allowed (`research/69` LT7, LT8).
- **Live:** small caps only, e.g. one tool round trip must stop with "exceeded 1 tool calling round trips" (`L4J:L4J-S/AiServicesWithToolsIT.java:1544,1561`), and `callToolCallLimitIsEnforced` (`SA:SA-T/AbstractToolCallingAdvisorIT.java:275,296`). **No reference runs a long live loop** (§4).

### 2.5 Streaming

- **Fake tier:** several scripted chunks, assert they join and arrive in order (`research/69` LT9).
- **Live:** real SSE chunking is the most live-tested behaviour after basic chat:
  - every chunk but the last has a null finish reason (`SA:SA-O/chat/OpenAiChatModelIT.java:344`), across about 96 SA classes;
  - streamed tool-call deltas keep their index, id and name, and join to the final arguments (`L4J:L4J-C/AbstractBaseChatModelIT.java:724-726,1097-1100`);
  - cancelling a live stream never calls the completion callback (`L4J:L4J-C/AbstractStreamingChatModelIT.java:119,157`);
  - each reasoning id gets exactly one start and one end (`MA:…/reasoning-openai-summaries.e2e.test.ts:108`).
- **Why a fake cannot do it:** recorded or hand-written fixtures keep one chunking; the provider changes it.

### 2.6 Structured output and validation retry

- **Fake tier:** the model returns invalid output, then valid. Assert the second prompt carries the validation error (`SA:spring-ai-client-chat/src/test/java/org/springframework/ai/chat/client/advisor/StructuredOutputValidationAdvisorTests.java:584`; `PA:tests/test_agent.py:342`). Tool-call turns are not validated as final output (`SA:…/StructuredOutputValidationAdvisorTests.java:229`), and usage is summed across attempts (`:293`). A retry that does not send the error is a re-roll.
- **Live:** the provider must accept the schema dialect and the model must comply:
  - exact JSON, `isEqualToIgnoringWhitespace("{\"city\": \"Berlin\"}")` (`L4J:L4J-C/AbstractBaseChatModelIT.java:1474`);
  - `isValidJson(content)` for native schemas (`SA:SA-O/chat/OpenAiChatModelResponseFormatIT.java:124`);
  - tools first, then the schema is filled (`CA:e2e-tests/test_structured_output.py:64`);
  - 33 Zod-derived schemas against about 9 models (`MA:…/tool-builder/builder.e2e.test.ts:449`), because providers reject schemas differently.

### 2.7 Memory window

- **Fake tier:** no fake model at all. Use the real memory class: append user, tool request, tool result, answer, and assert the exact window after each step. The tool request and its result are evicted together (`L4J:langchain4j/src/test/java/dev/langchain4j/memory/chat/MessageWindowChatMemoryTest.java:167,204`), because an orphan tool result makes the provider reject the request with a 400. Also: snap to a turn boundary (`SA:spring-ai-model/src/test/java/org/springframework/ai/chat/memory/MessageWindowChatMemoryTests.java:263`), and keep the system prompt (`:208`), without it counting against the window (`SA:spring-ai-session/…/compaction/WindowCompactionStrategyTests.java:210`).
- **Live:** history replayed to a real model, a two-turn `contains("James Bond")` (`SA:SA-O/chat/OpenAiChatModelIT.java:794,813`). Light; the risk is in our trimming, which the fake tier covers.

### 2.8 Compaction and summarisation

- **Fake tier:** a fake summariser model that records its prompt. Assert:
  - kept = [summary, last N messages], and the summariser was not shown the kept tail (`SA:spring-ai-session/…/compaction/ChatModelSummarizerTests.java:218`);
  - a blank or failed summary declines and calls the failure callback (`:162,187`);
  - the trigger fires at the threshold and not below it (`SA:…/TokenCountTriggerTests.java:64,90`);
  - **idempotency:** a second pass over already-compacted history never calls the summariser (`ADKJ:core/src/test/java/com/google/adk/summarizer/SlidingWindowEventCompactorTest.java:81,95`), and projecting a view twice gives the same view (`SA:…/CompactionBoundaryTests.java:108`).
- **Live:** OA tests server-side compaction on the real API, where the state lives on the server (`OA:integration_tests/`, sessions group). Nothing live for client-side compaction.

### 2.9 Prompt caching and cached-token pricing

- **Fake tier:**
  - **breakpoint placement:** capture the outgoing request and assert only the last tool result carries `cache_control` (`SA:models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/AnthropicChatModelTests.java:1042`); a fifth breakpoint is refused, since the provider allows 4 (`SA:…/CacheEligibilityResolverTests.java:210`);
  - **byte-stable prefix:** request N+1 must start with the bytes of request N, ignoring only moved `cache_control`, with a fake clock moving between requests, over every capability and three providers (`PA:tests/test_history_append_only.py:459`; checker `PA:tests/append_only.py:1247`). This is the strongest test found: a timestamp in the instructions silently busts the cache;
  - **usage:** cache-read tokens summed across turns (`SA:spring-ai-model/…/support/UsageCalculatorTests.java:94`); an impossible breakdown degrades to "unpriced" instead of crashing (`PA:tests/test_usage_limits.py:1444`).
- **Live:** only the provider reports cache tokens:
  - turn 2 must read the cache written in turn 1, `turn2Read > 0` (`SA:SA-A/AnthropicPromptCachingIT.java:214`), plus the minimum-length threshold (`:219`);
  - `cacheReadInputTokens() > 0` (`L4J:…/BedrockPromptCachingIT.java:383`);
  - our cache options reach the wire and are accepted (`OA:integration_tests/openai/test_responses.py:186`);
  - PA snapshots real cache tokens **and cost** from a recorded real call (`PA:tests/models/test_anthropic.py:15157`).

### 2.10 Semantic and response cache

- **Fake tier:** a counting fake model and a recording cache:
  - the second identical call makes no model call (`MA:packages/core/src/agent/__tests__/agent-response-cache.test.ts:140`);
  - errors are never cached (`:164`);
  - the tenant is part of the key (`:306`);
  - a different system prompt gives a different key (`SA:vector-stores/spring-ai-redis-semantic-cache/src/test/java/…/SemanticCacheAdvisorTests.java:184`), because a key built from the user text alone serves one persona's answer to another.
- **Live:** none, and it does not need one: the cache is ours, not the provider's. **No reference tests invalidation** beyond TTL.

### 2.11 Usage, cost and budget limits

- **Fake tier:** a scripted model with a fixed price function:
  - the run that crosses the limit throws, and **the billed response is kept in history** (`PA:tests/test_usage_limits.py:1216`). Dropping it under-counts spend; re-requesting it double-bills;
  - usage is summed across turns, retries and sub-agents (`PA:tests/test_usage_limits.py:210,407`);
  - a persistent USD budget across runs (`PA:tests/harness/spend/test_spend.py:538`).
- **Live:** our token estimate must be within 8% of the provider's real count (`MA:…/token-accuracy.e2e.test.ts:157`). **No reference live-tests a spend ceiling** (§4).

### 2.12 Guardrails and prompt injection

- **Fake tier:**
  - a blocking guardrail trips and the scripted model was never called (`OA:tests/test_guardrails.py:423`);
  - a parallel guardrail is shown, deliberately, not to stop side effects, ordered by an event and not a sleep (`:491`);
  - a tool-input guardrail rejects before approval, the tool never runs, and the rejection text is what the model sees (`OA:tests/test_agent_runner.py:2331`);
  - an output-guardrail reprompt re-enters the full tool loop (`L4J:L4J-S/guardrail/AiServiceGuardrailTests.java:381`);
  - block vs warn (`MA:packages/core/src/processors/processors/prompt-injection-detector.test.ts:233,255`).
- **Gap:** no reference tests **prompt injection carried in a tool result** through a whole run (closest: `OA:tests/test_tool_guardrails.py:351`, called directly).
- **Live:** a hook deny really blocks the tool the model tried (`CA:e2e-tests/test_hooks.py:67`); `disallowed_tools` really blocks (`CA:e2e-tests/test_sdk_mcp_tools.py:93`). Live is needed only to prove the model's real attempt is stopped.

### 2.13 Human approval and resume

- **Fake tier:** run to the pause, serialise the run state to JSON, restore it, approve or reject, resume. Assert one model call per step, and that the side effect ran exactly once (`OA:tests/test_resume_tool_use_behavior.py:15`; three turns over a rehydrated session `OA:tests/test_hitl_session_scenario.py:89`). Adversarial cases: compaction after approval, an unrelated user turn, a reused call id (`ADKJ:core/src/test/java/com/google/adk/flows/llmflows/RequestConfirmationLlmRequestProcessorTest.java:142,162,213-352`). mastra adds the same "exactly once" check at the wire (`research/69` §4).
- **Live:** a real model given a paused or rejected call still answers coherently (`SA:SA-T/AbstractToolCallConfirmationIT.java:92,110`).

### 2.14 Model fallback

- **Fake tier:** the primary fake throws 500 and the secondary answers. Assert:
  - the response names the **serving** model, and the failed attempt is recorded (`PA:tests/models/test_fallback.py:186`);
  - usage is priced on the serving model, and a rejected attempt's tokens still count in the run total (`PA:tests/models/test_fallback.py:1992`);
  - the request sent to the fallback provider is inspected (`:228`).
- **No Java reference tests fallback at all.**
- **Live:** none in the references. For Aruvii, see §5: fallback sends the primary's model name to another provider, which only a real provider rejects.

### 2.15 Sub-agents and handoffs

- **Fake tier:** one scripted model shared by parent and child. Assert the ordered events and that the next user turn goes to the agent that took over (`ADKJ:core/src/test/java/com/google/adk/flows/llmflows/AgentTransferTest.java:208`), and the exact request the child receives (`ADKJ:core/src/test/java/com/google/adk/tools/AgentToolTest.java:407`).
- **Live:** the handoff decision is the model's:
  - a forced sentinel and the specialist's tool call (`OA:integration_tests/openai/test_handoffs.py:64-66`);
  - routing to the right sub-agent (`ADKJ:contrib/langchain4j/…/LangChain4jIntegrationTest.java:306`);
  - a supervisor agent's tools change state, asserted on the **bank balance**, not the text (`L4J:langchain4j-agentic/…/SupervisorAgentIT.java:312`).

### 2.16 Evals of answer quality

Covered in `research/69` §5 and LT17–LT18. ADKP's live tier **is** its evals: `AgentEvaluator` over `num_runs=4` with
thresholds in a versioned `test_config.json` (`ADKP:tests/integration/test_single_agent.py:21-25`). They run in no
workflow, and no reference blocks CI on an eval. Evals are a separate tier from live tests: they score quality over
repeats, while live tests check facts.

## 3. The kinds of live test

The four catalogues reduce to ten recurring kinds. Each exists for one reason a fake cannot meet.

| kind | the reason it needs a real provider | who | Aruvii needs it? (§5) |
|---|---|---|---|
| **K1 · request acceptance and parameter effect** | only the provider rejects a field, schema, effort tier, cache option or model id, and only it shows a parameter took effect | all ten | **yes** |
| **K2 · tool round trip with a real decider** | the model must pick the tool and fill the arguments; the provider must accept our tool-result message | all ten | **yes** |
| **K3 · stream reassembly** | real chunking, delta and event order; fixtures freeze one shape | all ten | **yes** |
| **K4 · usage, cache and cost facts** | only the provider produces cache-write, cache-read and token counts | SA, L4J, OA, PA, MA | **yes** |
| **K5 · real error and limit mapping** | typed errors need the provider's real status, body and codes | SA, CA, PA, ADKP, OA | **yes** |
| **K6 · agent outcome by side effect** | the run's result is checked on state it changed (a balance, a row, a routed agent), not on wording | L4J, ADKJ, CA, OA | **yes**, a few flows |
| **K7 · auth and backend acceptance** | signatures and credential chains can only be checked against the real endpoint | AJ, ADKP | only if Aruvii uses Bedrock or Vertex |
| **K8 · provider-hosted tools** | web search, code execution and grounding run on the provider | SA, OA, PA, ADKP, MA | no, unless Aruvii uses them |
| **K9 · model catalogue health** | providers retire and rename models; excluded names are `xfail(strict=True)` so a fix is noticed (`PA:tests/providers/test_gateway_catalog.py:80-84`) | PA, MA | **yes**, cheap |
| **K10 · scored evals over repeats** | quality varies by run, so it is scored against thresholds over several runs | ADKP, MA | separate tier, not per PR |

**One shape recurs: one contract suite, run per provider.** L4J and SA write each kind once as an abstract test, and
every provider subclass runs it. That is how they hold 40+ adapters to the same proof (`L4J:L4J-C/AbstractBaseChatModelIT.java`;
`SA:SA-T/`).

**How they keep it cheap:**
- small pinned models: Haiku and `GPT_5_MINI` by default (`SA:…/AnthropicChatOptions.java:76`, `SA:…/OpenAiChatOptions.java:61`);
- tiny token caps: `maxOutputTokens(5)`, 32, 128;
- one call per case;
- CA's 49 e2e tests run on every push and PR on three operating systems, and its README puts the suite under $0.10 a run (`CA:e2e-tests/README.md:51`).

**How they keep it honest:**
- a missing key fails instead of skipping (`CA:e2e-tests/conftest.py:24`);
- a test that always skips is the trap: mastra's prefill test blanks its own key before its gate, so it never runs (`MA:packages/core/…/prefill-error-recovery.e2e.test.ts:20,47`);
- tests with no assertion pass when nothing raises (`CA:e2e-tests/test_dynamic_control.py:44,79`), so they prove little.

## 4. What nobody tests live

Searched across every live directory (each reader's grep is listed in §8). None of the ten live-tests:
- rate limits or 429 back-pressure;
- an authentication failure (401, bad key);
- context-window overflow;
- a spend ceiling per run;
- a long agent loop; the longest are 3-step tool loops and caps of 1–3;
- flakiness measured over repeats (except ADKP's `num_runs=4`).

All of these are left to the fake tier, where they can be forced deterministically. That is the right place: forcing a
429 or an overflow on a real provider costs money and is not reproducible.

## 5. Aruvii

**Status: proposed, pending the operator.** Aruvii's components are taken from `research/63` §11 at agent-platform
`772736bf` (2026-10-03): provider adapters for Anthropic, OpenAI, Bedrock and Ollama (raw HTTP), `ChatOrchestrator`,
`TurnRunner`, approvals, `MemoryWindower`, `HistoryCompressor`, `PromptCacheService`, `SemanticCacheService`,
`TokenBudgetChecker`, the LLM circuit breaker and fallback, and `W/eval/*`. The operator confirms the current list and
the providers Aruvii ships (#153).

`research/63` §2 already found defects only a real provider exposes. Each maps to a live kind:

| known defect at `772736bf` (`research/63`) | fakes miss it because | caught by |
|---|---|---|
| `cache_creation_input_tokens` is never read; pricing subtracts cached from input, double-discounting Anthropic | fake usage numbers are whatever the fake says | K4 |
| fallback sends the primary's model name to another provider | every fake accepts any model name | K1, K5 |
| Anthropic and Ollama only pseudo-stream; Bedrock streaming throws | a fake streams whatever chunks it is given | K3 |
| the stop-reason type is too small; truncation and refusal are invisible | a fake returns the stop reasons we already model | K1 (`maxOutputTokens` → LENGTH) |

Proposed tests per scenario, by tier:

| scenario | unit (fake model) | IT (fake HTTP, real adapter) | smoke (fake LLM) | live, every PR | provider |
|---|---|---|---|---|---|
| adapter mapping (2.1) | — | one contract suite per adapter: request JSON, stop reasons, usage | — | **same contract suite** on the real API: K1, K5, `maxOutputTokens` → LENGTH | each shipped |
| one call (2.2) | scripted reply | — | journey | known-answer call | each shipped |
| tool round trip (2.3) | scripted call → result in next request | tool-result JSON | journey with tool | K2: exact args + stub-tool marker | each shipped |
| tool errors, caps (2.4) | errors fed back; cap tested | — | — | one small cap (1 round trip) | one |
| streaming (2.5) | several chunks; join; order | SSE fixtures per provider | — | K3: partials join; tool deltas; null finish until last | each shipped |
| structured output (2.6) | invalid → valid, error sent back; usage summed | schema translation | — | provider accepts our schema; parses | each shipped |
| memory window (2.7) | real `MemoryWindower`: pairs evicted together, system kept | — | — | — | — |
| compaction (2.8) | fake summariser; kept tail; idempotent second pass; trigger threshold | — | — | — | — |
| prompt cache (2.9) | breakpoints placed; **byte-stable prefix** with a moving clock; cached tokens priced | request carries cache markers | — | K4: turn 2 reads cache; priced right | Anthropic, OpenAI |
| semantic cache (2.10) | hit skips model; errors not cached; tenant and system prompt in key | — | — | — | — |
| budgets (2.11) | crossing run throws, billed reply kept; sums across turns and sub-agents | — | — | K4: estimate vs real tokens within a margin | one |
| guardrails (2.12) | block → model never called; tool reject → tool never runs; **injection in a tool result** | — | — | real tool attempt is blocked | one |
| approval (2.13) | serialise → restore → approve/reject → resume; side effect once | — | approval journey | — | — |
| fallback (2.14) | primary 500 → secondary; serving model named and priced | request to fallback provider | — | K1/K5: fallback request accepted by the second provider | the pair |
| sub-agents (2.15) | shared scripted model; next turn routes right | — | — | K6: outcome by side effect | one |
| model catalogue (§3 K9) | — | — | — | each configured model name answers | each shipped |
| evals (2.16) | judge parsing; score arithmetic | — | — | **not per PR**: a separate scored job | — |

Rows marked "—" in the live column are scenarios where the risk is in our own code, so a fake tests it fully and a live
test would only add cost.

## 6. Candidate rules (for the operator's review — none approved)

LS = live and scenario testing. These add to LT1–LT18 in `research/69` §8 and do not repeat them.

### Scenario rules, fake tier (LS1–LS10)

- **LS1** — Test the memory window with the real class, asserting the exact window after each message, because evicting a tool call without its result makes the provider reject the next request. — `L4J:langchain4j/src/test/java/dev/langchain4j/memory/chat/MessageWindowChatMemoryTest.java:167,204`; `SA:spring-ai-model/…/MessageWindowChatMemoryTests.java:208,263`
- **LS2** — Test compaction with a recording fake summariser: assert what is kept, what the summariser saw, and that a second pass never summarises again, because repeated compaction rewrites history every turn. — `SA:spring-ai-session/…/ChatModelSummarizerTests.java:218`; `ADKJ:core/src/test/java/com/google/adk/summarizer/SlidingWindowEventCompactorTest.java:81,95`
- **LS3** — Assert each request starts with the previous request's bytes while a fake clock moves, because a timestamp or rewritten history silently busts the prompt cache. — `PA:tests/test_history_append_only.py:459`; `PA:tests/append_only.py:1247`
- **LS4** — Assert cache markers sit only where the provider allows and no more than its limit, because extra breakpoints waste the cache or fail the request. — `SA:models/spring-ai-anthropic/…/AnthropicChatModelTests.java:1042`; `SA:…/CacheEligibilityResolverTests.java:210`
- **LS5** — Key a response cache on tenant, system prompt and inputs, and never cache an error, because a key on user text alone serves one persona's answer to another. — `MA:…/agent-response-cache.test.ts:140,164,306`; `SA:…/SemanticCacheAdvisorTests.java:184`
- **LS6** — When a run crosses a usage or spend limit, keep the response that crossed it and count it, because dropping it under-counts spend and re-requesting it bills twice. — `PA:tests/test_usage_limits.py:1216`; `PA:tests/harness/spend/test_spend.py:538,627`
- **LS7** — Test that a blocking guard stops the run before the model or tool is called, with the rejection text as the tool result, because a late guard lets side effects through. — `OA:tests/test_guardrails.py:423`; `OA:tests/test_agent_runner.py:2331`
- **LS8** — Test approval by serialising the paused run, restoring it, then approving or rejecting, asserting each side effect ran exactly once, because resume re-runs completed tools. — `OA:tests/test_resume_tool_use_behavior.py:15`; `ADKJ:…/RequestConfirmationLlmRequestProcessorTest.java:142,162`
- **LS9** — Test fallback by failing the primary fake, then assert the serving model's name, the recorded failed attempt and the price on the serving model, because cost reports book the wrong model. — `PA:tests/models/test_fallback.py:186,1992,228`
- **LS10** — Test prompt injection arriving in a tool result through a whole run, because every reference guards user input only, and tool results are where untrusted text enters. — gap: `OA:tests/test_tool_guardrails.py:351` is the closest, called directly

### Live-test rules (LS11–LS20)

- **LS11** — Live-test only what a fake cannot know — provider acceptance, real decisions, real chunking, real usage and errors — and keep the agent's own logic in fakes, because live tests cost money every run. — §3; §4
- **LS12** — Write each live check once as a contract suite every provider adapter runs, with unsupported features declared and tested to fail, because per-provider copies drift. — `L4J:L4J-C/AbstractBaseChatModelIT.java:1269-1286`; `SA:SA-T/AbstractToolCallingAdvisorIT.java:275`
- **LS13** — In a live test, assert a parameter's effect, not only acceptance (five output tokens give LENGTH; a stop sequence cuts text), because a dropped field is accepted silently. — `L4J:L4J-C/AbstractBaseChatModelIT.java:396,527,1951`
- **LS14** — Live-test tool calls on exact argument JSON and a marker the stub tool returns, because that proves the model called the tool and our result reached it. — `L4J:L4J-C/AbstractBaseChatModelIT.java:706,786`; `SA:SA-A/AnthropicChatModelIT.java:326`
- **LS15** — Live-test streaming by joining partials and tool-call deltas to the final message, because real chunking differs from every fixture. — `L4J:L4J-C/AbstractBaseChatModelIT.java:724-726,1097-1100`; `SA:SA-O/chat/OpenAiChatModelIT.java:344`
- **LS16** — Live-test cache and usage numbers, and the price computed from them, because only the provider reports cache-write and cache-read tokens. — `SA:SA-A/AnthropicPromptCachingIT.java:214`; `L4J:…/BedrockPromptCachingIT.java:383`; `PA:tests/models/test_anthropic.py:15157`
- **LS17** — Check agent-level live tests on the state the run changed — a balance, a row, the routed agent — never on wording, because wording varies by model and run. — `L4J:langchain4j-agentic/…/SupervisorAgentIT.java:312`; `ADKJ:contrib/langchain4j/…/LangChain4jIntegrationTest.java:306`
- **LS18** — Pin a small model and a small token cap per live test, and fail when the key is missing, because default models change and a skipped suite passes silently. — `CA:e2e-tests/conftest.py:16,24`; `SA:…/AnthropicChatOptions.java:76`
- **LS19** — Give every live test an assertion that can fail, and check its gate does not always skip, because a test that never runs or never asserts protects nothing. — `MA:…/prefill-error-recovery.e2e.test.ts:20,47`; `CA:e2e-tests/test_dynamic_control.py:44,79`
- **LS20** — Check each configured model name against the provider, and mark known-excluded names as expected failures that must fail, because providers retire models and a fix should be noticed. — `PA:tests/providers/test_gateway_catalog.py:80-84`; `PA:.github/workflows/gateway-model-health.yml:6`

## 7. Open for G34 (#133)

1. **Confirm Aruvii's components and providers** (§5). The table above is built on 2026-10-03 facts.
2. **Which providers run live on every PR:** each shipped provider, or one primary on PRs and the rest nightly?
3. **Evals:** a separate scored job (K10) on its own schedule. When does it start, and does a red result block anything?
4. **The live contract suite's home:** one abstract Spock spec in the adapter module, subclassed per provider (§3), or one file per provider?
5. **Placement in the rulebook:** a new `testing/references/llm-tests.md` for LT and LS, or rows added to `strategy.md`, `unit-tests.md` and `integration-tests.md`.

## 8. Method

- **Readers:** four, over the ten pinned clones of `research/69`.
  - Three catalogued every real-model test, one test or group per row: what it proves, why it needs a real model, what it asserts, its model and cost, when it runs.
  - The fourth read the fake-tier tests for memory, compaction, caching, budgets, guardrails, approvals, fallback, structured-output retry and sub-agents, which R40 did not cover.
- **What was searched for §4:** each reader grepped the live directories for `429|TooManyRequests`, `401|bad key`, `context_length|context window`, `budget|cost|spend`, `maxIterations|maxLlmCalls|maxToolCallingRoundTrips`, `seed(` and `temperature(0`.
- **Spot-checks:** 17 citations re-checked by hand with `sed -n` across the four reports, all matching. Among them:
  - `SA:SA-A/AnthropicPromptCachingIT.java:214`, `SA:build-and-deploy-snapshot.yml:173`, `SA:SA-T/AbstractToolCallingAdvisorIT.java:296`;
  - `L4J:L4J-C/AbstractBaseChatModelIT.java:1951`, `L4J:…/SupervisorAgentIT.java:312`, `L4J:…/MessageWindowChatMemoryTest.java:167,204`;
  - `ADKJ:…/SlidingWindowEventCompactorTest.java:95`, `PA:tests/test_history_append_only.py:459`, `PA:tests/models/test_fallback.py:1992`, `OA:tests/test_guardrails.py:423`, `MA:…/prefill-error-recovery.e2e.test.ts:20,47`.
- **Counts are approximate:** about 191 key-gated SA ITs and 38 key-gated L4J provider classes, counted by grep.
- **Not re-measured:** agent-platform. It is on GitLab and outside this session.
