# R40 · How agent SDKs and Spring code test LLM features

Ticket: `chiyanram/skills#131` (R40, map #130). Read 2026-10-30. Builds on `research/23-agent-sdk-test-mix.md` (R19),
which measured the unit/IT split and named the fake used by each SDK; this file reads one level deeper: how the fakes
are built, how recordings stay honest, how real-model tests are gated and asserted, how the agent loop is tested, and
how evals run.

**Candidates only.** No rule enters a reference without the operator's yes (`research/00-reference-format.md`).
G34 (#133) decides them.

Contents: §0 repos · §1 fake model · §2 record/replay · §3 real-model tests · §4 agent loop · §5 evals ·
§6 where the repos disagree · §7 fit with approved rules and Aruvii today · §8 candidate rules LT1–LT18 ·
§9 open for G34 · §10 method

## 0. Repos

Shallow clones of each default branch. Citations are `key:path:line`; every one was opened, and a sample of each
reader's citations was re-checked by hand (§10).

| key | repo | commit | date | language |
|---|---|---|---|---|
| SA | spring-projects/spring-ai | `b19514195` | 2026-10-29 | Java |
| AJ | anthropics/anthropic-sdk-java | `c0f5915f7` | 2026-10-23 | Kotlin/Java |
| L4J | langchain4j/langchain4j | `709c6fd10` | 2026-10-29 | Java |
| ADKJ | google/adk-java | `64ce48c74` | 2026-10-29 | Java |
| OA | openai/openai-agents-python | `cd26bbbc5` | 2026-10-27 | Python |
| CA | anthropics/claude-agent-sdk-python | `1ea8cb74d` | 2026-10-30 | Python |
| PA | pydantic/pydantic-ai | `79e157e8b` | 2026-10-30 | Python |
| ADKP | google/adk-python | `c501d8eda` | 2026-10-29 | Python |
| LG | langchain-ai/langgraph | `6f2df053f` | 2026-10-29 | Python |
| MA | mastra-ai/mastra | `5480e7b7c` | 2026-10-29 | TypeScript |

## 1. Fake model in unit tests

**Three seams, and the strong repos use more than one.**

| seam | what runs for real | who | why |
|---|---|---|---|
| scripted model behind the SDK's own model interface | the whole loop: tools, retries, validation, history | OA `ScriptedModel` (`OA:src/agents/testing/model.py:249-270`), PA `FunctionModel`/`TestModel` (`PA:pydantic_ai_slim/pydantic_ai/models/function.py:56`, `models/test.py:62`), ADKJ `TestLlm` (`ADKJ:core/src/test/java/com/google/adk/testing/TestLlm.java:47-54`), SA `ScriptedChatModel` (`SA:advisors/spring-ai-session-advisor/src/test/java/org/springframework/ai/session/advisor/ScriptedChatModel.java:36-42`), L4J `ChatModelMock` | the unit under test is the loop, not the provider |
| fake HTTP transport under the real provider SDK | request mapping, JSON, SSE parsing | L4J `MockHttpClient` (`L4J:langchain4j-http-client/src/test/java/dev/langchain4j/http/client/MockHttpClient.java:28-30`), AJ `FakeHttpClient` (`AJ:anthropic-java-core/src/test/kotlin/com/anthropic/helpers/FakeHttpClient.kt:18-25`), ADKJ `FakeGeminiApi` (`ADKJ:core/src/test/java/com/google/adk/models/FakeGeminiApi.java:52,59`), SA `MockWebServer` (`SA:models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/AnthropicChatModelStreamingHttpTests.java:109-124`) | the adapter owns the wire format |
| scripted HTTP server for whole-loop scenarios, asserting the request journal | everything, including cross-turn message composition | MA AIMock: a real provider pointed at an in-test server via `baseURL` (`MA:packages/core/src/loop/test-utils/aimock/README.md:23-24`), 287 scenario files | per-step tests "pass even when the **composition** of steps regresses" (`MA:…/aimock/README.md:9-11`) |

**Strict fakes.** The good fakes fail both ways:
- On an extra call: OA raises `UnexpectedModelCall` (`OA:src/agents/testing/model.py:487-496`), ADKJ fails "out of responses" (`ADKJ:…/TestLlm.java:197-207`), SA throws "No scripted reply left" (`SA:…/ScriptedChatModel.java:73-76`), L4J's `request()` throws unless exactly one request was made (`L4J:…/MockHttpClient.java:64-68`).
- On a missing call: OA's `assert_complete()` raises `UnconsumedModelSteps` (`OA:…/model.py:313-319`), though only 17 files call it.

**Fakes record what they were sent.** OA keeps deep-copied `.calls` (`OA:…/model.py:271-274`), ADKJ and ADKP keep
`requests` (`ADKP:tests/unittests/testing_utils.py:416-489`), and tests assert on them: SA checks the exact
transcript of a two-turn tool loop with `containsExactly("Weather in Lisbon?", "call:c1", "result:c1", …)`
(`SA:advisors/spring-ai-session-advisor/src/test/java/org/springframework/ai/session/advisor/SessionMemoryAdvisorToolLoopTests.java:49-60`).
LG's fake goes further: its reply is the prompt echoed back (`LG:libs/prebuilt/tests/model.py:36`), so an output
assertion like `"Foo-hi?"` also proves the system prompt was sent (`LG:libs/prebuilt/tests/test_react_agent.py:146-154`).

**Guard against real calls.**
- OA: an autouse fixture replaces the real model methods with `pytest.fail("Real models should not be used in tests!")` (`OA:tests/conftest.py:129-141`); the opt-out is a named marker (`OA:pyproject.toml:262`).
- PA: `ALLOW_MODEL_REQUESTS = False` suite-wide (`PA:tests/conftest.py:107`), checked inside every real provider before it sends (`PA:pydantic_ai_slim/pydantic_ai/models/__init__.py:2642-2643`), opt-in fixture (`PA:tests/conftest.py:580-582`).
- MA: dummy keys `sk-dummy-for-replay-mode` outside live mode (`MA:packages/_test-utils/src/llm-helpers.ts:225-249`).
- CA and ADKP have no guard; ADKP only injects fake credentials, so a stray call fails on auth (`ADKP:tests/unittests/conftest.py:32-38`).

**Weak spots.**
- Fakes copied per test drift apart: CA defines five-plus mock transports, and two fake CLIs report different versions (`CA:tests/test_run_end_subprocess.py:42` vs `CA:tests/test_close_cancellation.py:203`).
- One-chunk streaming fakes never exercise chunk boundaries: SA's scripted model "Streams the next reply as one chunk" (`SA:…/ScriptedChatModel.java:80-84`), ADKP's `MockModel` ignores `stream`.
- SA mocks the vendor SDK with `Strictness.LENIENT` (`SA:models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/AnthropicChatModelTests.java:126`), so stale stubs go unreported.

## 2. Record/replay

Only PA and MA make recorded real traffic a practice. SA keeps a handful of recorded payloads; the other JVM repos
hand-write theirs.

| repo | mechanism | honesty guard | weakness |
|---|---|---|---|
| PA | VCR cassettes are the default test style (`PA:tests/AGENTS.md:13`): 466 `pytest.mark.vcr`, 2,156 cassettes; rewrite with `make update-vcr-tests` (`PA:Makefile:117-119`) | a test fails if its cassette has unplayed interactions (`PA:tests/conftest.py:847-875`); `request_capture` hook above the replay transport to assert what was sent (`PA:tests/AGENTS.md:159`); body matcher opt-in (`:163`); "Pin recorded facts in the test body, never in the cassette alone" (`:268`) | matchers "aren't always sensitive to the request body" (`PA:tests/AGENTS.md:15`) — documented, with the two fixes above |
| MA | MSW record/replay keyed on URL + body hash (`MA:packages/_llm-recorder/README.md:14`), per provider and model | a miss fails with "Run with UPDATE_RECORDINGS=true" (`MA:packages/_llm-recorder/src/llm-recorder.ts:1010`) | a fuzzy match at similarity ≥ 0.6 only warns (`:608`, `:1019-1044`); CI runs `auto`, not strict replay, despite the README (`MA:.github/workflows/test-suite.yml:203-222` vs `README.md:122`); the promised nightly drift check has no caller (`MA:…/src/llm-contract.ts:1-8`); request bodies are stored unscrubbed (`:142-146`) |
| AJ | spec-driven mock server from the generated OpenAPI spec, request validation on (`AJ:scripts/mock:13-17,28`) | the spec is regenerated with the SDK | service tests check only `.validate()` shape (`AJ:…/services/blocking/beta/MessageServiceTest.kt:214`) |
| SA | eight recorded `/v1/responses` payloads parsed with the OpenAI SDK's own mapper (`SA:models/spring-ai-openai/src/test/java/org/springframework/ai/openai/responses/ResponsesTestFixtures.java:28-44`) | a fixture that no longer matches the SDK types fails to parse | no refresh path; ids look hand-edited |
| OA | no model recordings; inline snapshots of normalized trace spans (`OA:tests/test_agent_tracing.py:55`); RunState fixtures produced by each historical commit's own writer (`OA:tests/fixtures/run_state/README.md:11,15`) | the fake builds the provider's real response types (`OA:src/agents/testing/model.py:21-49`) | — |
| L4J, ADKJ, ADKP, LG, CA | none for model traffic | L4J asserts real requests in live ITs with a `SpyingHttpClient` wrapping a real client (`L4J:langchain4j-http-client/src/test/java/dev/langchain4j/http/client/SpyingHttpClient.java:15-19`); CA tests its own fake (`CA:tests/test_close_cancellation.py:197-199`) | hand-written frames go stale: CA names a retired model id (`CA:tests/test_integration.py:46`) |

**Scrubbing.** PA does it in pre-record hooks: auth, cookie and vendor headers (`PA:tests/cassette_hooks.py:63-77`),
tokens in JSON bodies (`:97`), AWS secrets (`:237-238`), and account and project ids normalized in URIs so a
cassette recorded in one account replays in another (`:132-143`). MA drops headers only (`MA:…/llm-recorder.ts:344-355`).

## 3. Real-model tests

**Every repo keeps the model out of the default run.** They differ on when the real model does run:

| when | who | evidence |
|---|---|---|
| every push and same-repo PR, gating release | CA | OIDC identity, no stored key (`CA:.github/workflows/test.yml:81-90,161`); auto-release only after tests pass (`CA:.github/workflows/auto-release.yml:4-15`) |
| scheduled | SA Mon/Wed/Fri, L4J nightly, PA weekly | `SA:.github/workflows/spring-ai-integration-tests.yml:4-28`; `L4J:.github/workflows/nightly_jdk17.yaml:5`; `PA:.github/workflows/gateway-model-health.yml:4-7` with a protected environment and a Slack alert (`:19-26,42-45`) |
| in CI, but not blocking | L4J | `continue-on-error: true` (`L4J:.github/workflows/main.yaml:183-186`) |
| manual only | OA, AJ, MA | `OA:.github/scripts/run_integration_tests.py:92-96`; `AJ:anthropic-java-aws/src/test/kotlin/com/anthropic/aws/backends/AwsLiveTest.kt:10-16`; `MA:.github/workflows/vitest-all.yml:3-4` |
| never in CI | ADKJ, ADKP | `ADKJ:.github/workflows/validation.yml:50-51`; `ADKP:.github/workflows/continuous-integration.yml:202` |

**Gating** is an env var per class or method: `@EnabledIfEnvironmentVariable(named = "ANTHROPIC_API_KEY", matches = ".+")`
(`SA:models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/chat/AnthropicChatModelIT.java:90`;
`L4J:langchain4j-open-ai/src/test/java/dev/langchain4j/model/openai/common/OpenAiChatModelIT.java:35`), a separate
tree or marker (`OA:integration_tests/pytest.ini:8-24`), or a flag plus a key (`PA:tests/conftest.py:814-818`).
Two stop a live suite from silently passing by skipping everything: OA's `STRICT=1` turns skips into failures
(`OA:integration_tests/README.md:29`), and PA and CA fail rather than skip a missing key in CI
(`PA:tests/providers/test_gateway_catalog.py:29-38`; `CA:e2e-tests/conftest.py:19-28`).

**Model and cost.** Small, pinned models: Haiku for SA tool tests (`SA:…/AnthropicChatModelIT.java:306`), `GPT_5_MINI`
(`L4J:…/OpenAiChatModelIT.java:50`), `maxTokens(32)` (`AJ:…/AwsLiveTest.kt:19-25`), `max_tokens=256`
(`PA:tests/providers/test_gateway_catalog.py:52-56`), `max_turns=1` and "less than $0.10" a run
(`CA:e2e-tests/README.md:51`). CA pins the model because "the CLI's default model … changes between CLI releases"
(`CA:e2e-tests/conftest.py:7-16`).

**Asserting on non-deterministic output.** Nobody matches exact prose from a live model. What they assert instead:
- **Structure and invariants**: tool-call count 5, at least 2 steps (`MA:packages/core/src/agent/__tests__/tool-calls-finish-reason.e2e.test.ts:149-159`); event count and function name (`ADKJ:contrib/langchain4j/src/test/java/com/google/adk/models/langchain4j/LangChain4jIntegrationTest.java:117,138`); tool arguments exactly, `isEqualToIgnoringWhitespace("{\"city\":\"Munich\"}")` (`L4J:langchain4j-core/src/test/java/dev/langchain4j/model/chat/common/AbstractBaseChatModelIT.java:706`); usage `total == prompt + completion` (`SA:…/AnthropicChatModelIT.java:130-132`).
- **Parsed structured output**: `actorsFilms.movies()).hasSize(5)` (`SA:…/AnthropicChatModelIT.java:217-219`).
- **A marker the test controls**: the stub tool returns "sunny", and the answer must contain it (`ADKJ:…/LangChain4jIntegrationTest.java:159`); the prompt forces a sentinel, "answer exactly HANDOFF_RESOLVED" (`OA:integration_tests/openai/test_handoffs.py:38-39,64-66`).
- **Side effects of real tools**: the disallowed tool was not executed (`CA:e2e-tests/test_sdk_mcp_tools.py:87-88`), tolerating a model that retries a write (`CA:e2e-tests/test_run_end.py:185-190`).
- **Keywords only for prose**: `containsIgnoringCase("Berlin")` (`L4J:…/AbstractBaseChatModelIT.java:171`).
- **Too weak to catch anything**: "not empty" alone (`AJ:…/AwsLiveTest.kt:51`; `PA:tests/providers/test_gateway_catalog.py:58-65`).

**Retries hide flakes.** L4J retries every failure 3 times, assertion failures included
(`L4J:internal/langchain4j-internal-test-retry/src/main/java/dev/langchain4j/test/retry/GlobalTestRetryExtension.java:23,37-38`);
SA reruns failing ITs twice (`SA:.github/actions/do-integration-test/action.yml:33-39`). OA instead injects a fault
into a real call and asserts the SDK's own retry: `attempts == 2` (`OA:integration_tests/openai/test_retry.py:34-44,78-79`).

## 4. The agent loop under test

All of this runs on the fakes from §1.

- **Tool errors go back to the model, and the run continues.** Unknown tool → `Error: Tool 'get_the_weather' not found` with `isError(true)` in the next request (`AJ:anthropic-java-core/src/test/kotlin/com/anthropic/helpers/BetaToolRunnerTest.kt:142-197`); a throwing tool → `Error: BOOM!` (`:1189-1211`); the error is the third message of the second request (`L4J:langchain4j/src/test/java/dev/langchain4j/service/AbstractAiServicesWithToolErrorHandlerTest.java:101-104`); the unknown-tool error lists the available tools (`ADKP:tests/unittests/flows/llm_flows/tools/test_functions_error_messages.py:103-128`); a validation error is retried with `RetryInfo(cause='validation_error', attempt=1)` in the history (`PA:tests/test_agent.py:342-420`).
- **Caps.** `maxIterations(2)` (`AJ:…/BetaToolRunnerTest.kt:74`); exactly 4 events with an unreachable third response (`ADKJ:core/src/test/java/com/google/adk/flows/llmflows/BaseLlmFlowTest.java:230-256`); `UsageLimits(request_limit=1)` (`PA:tests/test_usage_limits.py:74-86`); `recursion_limit` (`LG:libs/langgraph/tests/test_pregel.py:588-589`); `MaxTurnsExceeded` on a resumed run (`OA:tests/test_agent_runner.py:880`). By contrast, SA's live IT loops `while (response.hasToolCalls())` with no bound (`SA:…/AnthropicChatModelIT.java:321-325`).
- **Streaming.** Partial chunks must join to the final text, and partial tool-call arguments to the final arguments (`L4J:…/AbstractBaseChatModelIT.java:193,727-741`); callback order with `InOrder` and `verifyNoMoreInteractions` (`:749-757`); exact block sequence (`AJ:anthropic-java-core/src/test/kotlin/com/anthropic/helpers/BetaRefusalFallbackInterceptorStreamingTest.kt:73-85`); a stream that ends before `finish_reason` raises and the tool does not run (`OA:tests/models/test_chatcompletions_stream_eof.py:97-104`); a partial streamed function call is not executed (`ADKJ:…/BaseLlmFlowTest.java:342-365`).
- **Cancellation and backpressure.** No events after `cancel()` (`OA:tests/test_cancel_streaming.py:89-101`); disposing the run cancels the model stream within 2 s (`ADKJ:core/src/test/java/com/google/adk/flows/llmflows/BaseLlmFlowCancelTest.java:67-77`); cancellation reaps the child process (`CA:tests/test_close_cancellation.py:101-144`).
- **Retry correctness is checked in stored state.** After a mid-stream disconnect (`MA:…/aimock/scenarios/api-error-retry-rollback.scenario.test.ts:24`), only the complete reply is persisted (`:87-89`); the regression it guards is the partial attempt merged into the stored message (`:47-51`). After a suspend and resume, the tool's side effect ran exactly once (`MA:…/approval-suspend-paths.scenario.test.ts:138-143`).
- **Time is controlled, not waited for.** A fixed `Clock` and a recording sleeper for `Retry-After` backoff (`AJ:anthropic-java-core/src/test/kotlin/com/anthropic/core/http/RetryingHttpClientTest.kt:195-227`); patched `sleep` asserting backoff `[0.01, 0.02]` (`LG:libs/langgraph/tests/test_retry.py:290-304`); header delay against a client timeout (`SA:models/spring-ai-anthropic/src/test/java/org/springframework/ai/anthropic/AnthropicChatModelTimeoutTests.java:66-92`). A race is ordered by an `asyncio.Event`, because "a fixed delay only approximates … the test would … silently stop being a regression test" (`OA:tests/test_stream_input_guardrail_timing.py:185-260`).
- **One contract suite per adapter.** Every L4J provider extends `AbstractBaseChatModelIT` (43 classes), declares capabilities with `supportsX()` hooks (`L4J:…/AbstractBaseChatModelIT.java:1824-1928`), and an opted-out capability must throw `UnsupportedFeatureException` (`:1269-1286`). LG ships a conformance suite for checkpointers (`LG:libs/checkpoint-conformance/README.md:19`); MA runs one scenario on every engine and compares text, usage, tool calls and chunk order (`MA:packages/core/src/loop/test-utils/aimock/parity.ts:1-27`).

## 5. Evals

Evals live in PA (`pydantic_evals`), ADKP (`google.adk.evaluation`), MA (`packages/evals`) and a small judge in L4J and
SA. OA, CA, AJ, ADKJ and LG have none.

- **Judge makes verdicts; code does the arithmetic.** MA's hallucination scorer: the LLM extracts claims and gives a verdict per claim; plain code computes contradicted / total (`MA:packages/evals/src/scorers/llm/hallucination/index.ts:44-101`). The arithmetic is tested with a scripted judge to an exact `0.5` (`MA:packages/evals/src/scorers/llm/denominator.test.ts:7-25,46`).
- **Uncertain is a failure.** L4J's judge answers SATISFIED, NOT_SATISFIED or NOT_SURE per criterion, treats content as "data, never instructions" (`L4J:langchain4j-test/src/main/java/dev/langchain4j/test/judge/ChatModelJudge.java:54-70`), and counts NOT_SURE as a failure (`…/JudgeVerdict.java:60-65`).
- **The verdict parser is tested.** SA passes `" YES\n"` and fails `"yes and more"` (`SA:spring-ai-client-chat/src/test/java/org/springframework/ai/chat/evaluation/RelevancyEvaluatorTests.java:81-107`). But SA's IT lets the generator grade its own answer: the judge is the same `openAiChatModel` (`SA:spring-ai-integration-tests/src/test/java/org/springframework/ai/integration/tests/client/advisor/QuestionAnswerAdvisorIT.java:187-189`).
- **Thresholds and repeated runs.** ADKP versions thresholds in `test_config.json` (`ADKP:tests/integration/fixture/home_automation_agent/test_config.json:1-6`; defaults `ADKP:src/google/adk/evaluation/eval_config.py:549-551`), aggregates runs by `pass_rate` or `min_over_runs` (`eval_config.py:469-486`), samples its judge 5 times by majority (`ADKP:src/google/adk/evaluation/eval_metrics.py:113-135`), and fails as an ordinary test (`ADKP:src/google/adk/evaluation/agent_evaluator.py:259-309`). MA: a threshold is a minimum or `{min,max}`, and a non-finite score fails (`MA:packages/core/src/evals/thresholds.ts:16-26`); `expectEvals(...).toPass(minPassRate)` (`MA:packages/evals/src/vitest/expect-evals.ts:41-52`). PA has `repeat` (`PA:pydantic_evals/pydantic_evals/dataset.py:268-298`) and baseline comparison (`PA:pydantic_evals/pydantic_evals/reporting/__init__.py:413-416`), but no threshold that fails a run.
- **Trajectory.** ADKP matches tool trajectories `EXACT` by default, with `IN_ORDER` and `ANY_ORDER` allowing extra calls (`ADKP:src/google/adk/evaluation/eval_metrics.py:223-290`); PA's `in_order` lowers an F1 score for extra calls (`PA:pydantic_evals/pydantic_evals/evaluators/agentic.py:287-318`).
- **Where evals run.** None of the ten runs an eval dataset as a blocking CI step. MA runs scorer tests from recordings in the normal suite, and a separate eval workflow on preview deployments (`MA:.github/workflows/2027dev-evals.yml:1-3`); ADKP runs evals locally or by hand only.

## 6. Where the repos disagree

| question | one side | other side |
|---|---|---|
| default test style for provider code | replay recorded real responses (PA: unit tests must justify why they are not VCR, `PA:tests/AGENTS.md:13-15`) | hand-written payloads behind a fake transport (L4J, AJ, ADKJ, SA) |
| where the loop fake sits | the model object (LG, ADKJ, OA, SA) | the HTTP wire, asserting the request journal (MA, `MA:…/aimock/README.md:9-19`) |
| when the real model runs | every PR, gating release (CA) | manual or never (OA, AJ, ADKJ, ADKP) |
| retrying live failures | blanket retries (L4J 3×, SA 2×) | inject the fault and assert the retry (OA) |
| extra tool calls in a trajectory | pass under `IN_ORDER` (ADKP) | lower the score (PA) |

## 7. Fit with approved rules, and Aruvii today

Facts only; G34 decides.

- **S1** (tier by what the behaviour depends on) and **U3** (double only at a boundary) already say "fake the model at its port". Every strong repo agrees; §1 adds *how*: strict, recording, shared, and streaming in more than one chunk.
- **research/24 (fakes vs mocks).** The repos favour scripted fakes over mocking-library stubs for the model, and use Mockito only around the vendor SDK (SA) — where SA's `LENIENT` setting shows the cost.
- **V3 junk patterns** already reject a mock that implements the asserted behaviour; LT4 (assert the request sent) is the positive form for LLM code.
- **Aruvii (from R19, `research/23` §"Aruvii").** Smoke tests use a scripted fake model server on Ollama's port (#576, #608). On the JVM, `FakeAgentChatPort` exists but no test on master uses it, so JVM ITs that touch the agent loop have no deterministic model seam. Not re-measured here: agent-platform is on GitLab and outside this session.

## 8. Candidate rules (for the operator's review — none approved)

Each: imperative + because + failure, then its sources. LT = LLM testing.

### Fake model (LT1–LT6)

- **LT1** — Fake the model behind your own model port with one shared, scripted fake, because copied per-test mocks drift from the protocol and from each other. — `OA:src/agents/testing/model.py:249`; `ADKJ:core/src/test/java/com/google/adk/testing/TestLlm.java:47`; contrast `CA:tests/test_tool_callbacks.py:22`, `CA:tests/test_streaming_client.py:26`
- **LT2** — Make the scripted fake fail on an unscripted extra call and on unused steps, because a tolerant fake hides a loop that ran too many or too few turns. — `OA:…/model.py:487-496,313-319`; `ADKJ:…/TestLlm.java:197-207`; `SA:…/ScriptedChatModel.java:73-76`
- **LT3** — Fail any test that reaches a real model client unless it opts in by name, because an unguarded path spends money, runs slowly and flakes. — `OA:tests/conftest.py:129-141`; `PA:tests/conftest.py:107,580-582`; `PA:pydantic_ai_slim/pydantic_ai/models/__init__.py:2642-2643`
- **LT4** — Assert on the request the code sent the model, not only on the final answer, because lost tool results and broken history show up only in the next call's input. — `SA:…/SessionMemoryAdvisorToolLoopTests.java:49-60`; `OA:tests/test_agent_runner.py:2024-2037`; `LG:libs/prebuilt/tests/model.py:36`; `MA:…/aimock/README.md:15-19`
- **LT5** — Test each provider adapter against a fake HTTP transport under the real SDK and assert the request JSON, because a model-level fake skips the request mapping that breaks in production. — `L4J:…/MockHttpClient.java:28-30`; `ADKJ:core/src/test/java/com/google/adk/models/FakeGeminiApi.java:52,59`; `AJ:…/FakeHttpClient.kt:18-25`
- **LT6** — Make every model adapter pass one shared contract suite, with each unsupported capability declared and tested to throw, because an unchecked opt-out silently drops a parameter. — `L4J:…/AbstractBaseChatModelIT.java:679,1269-1286,1840`; `LG:libs/checkpoint-conformance/README.md:19`

### Agent loop (LT7–LT11)

- **LT7** — Feed tool and validation errors back to the model in tests and assert the run continues, because a swallowed error stalls the loop or yields a confident wrong answer. — `AJ:…/BetaToolRunnerTest.kt:142-197,1189-1211`; `PA:tests/test_agent.py:342-420`; `ADKP:tests/unittests/flows/llm_flows/tools/test_functions_error_messages.py:103-128`
- **LT8** — Cap the agent loop by turns or requests and test the cap, because an unbounded tool loop turns one model misstep into a hung, billed run. — `AJ:…/BetaToolRunnerTest.kt:74`; `ADKJ:…/BaseLlmFlowTest.java:230-256`; `PA:tests/test_usage_limits.py:74-86`; contrast `SA:…/AnthropicChatModelIT.java:321-325`
- **LT9** — In streaming tests, script several chunks, assert they join to the final message and arrive in order, and bound every wait, because streams lose, reorder or hang. — `L4J:…/AbstractBaseChatModelIT.java:193,727-757`; `L4J:…/AbstractStreamingChatModelIT.java:215`; contrast `SA:…/ScriptedChatModel.java:80-84`
- **LT10** — After an injected provider failure, assert the persisted conversation and side effects, not just the reply, because a retry can store a partial reply or run a tool twice. — `MA:…/api-error-retry-rollback.scenario.test.ts:24,47-51,87-89`; `MA:…/approval-suspend-paths.scenario.test.ts:138-143`
- **LT11** — Control time with a fixed clock and order races with explicit signals, never sleeps, because timing-based tests stop exercising the regression and still pass. — `AJ:…/RetryingHttpClientTest.kt:195-227`; `LG:libs/langgraph/tests/test_retry.py:290-304`; `OA:tests/test_stream_input_guardrail_timing.py:185-260`

### Recordings (LT12–LT13)

- **LT12** — If you replay recorded traffic, fail on unplayed or unmatched interactions and never accept near-matches, because a stale recording keeps passing after the code stops sending a field. — `PA:tests/conftest.py:847-875`; `PA:tests/AGENTS.md:15,159,163`; contrast `MA:packages/_llm-recorder/src/llm-recorder.ts:608,1019-1044`
- **LT13** — Scrub credentials, account ids and vendor headers in a pre-record hook, and pin load-bearing facts in the test body, because recordings are committed forever and nobody reviews them. — `PA:tests/cassette_hooks.py:63-77,132-143,237-238`; `PA:tests/AGENTS.md:268`; contrast `MA:…/llm-recorder.ts:142-146`

### Real-model tests (LT14–LT16)

- **LT14** — Run real-model tests in their own scheduled job with a pinned small model, a token cap and a protected secret, failing when skipped, because skipped-everywhere tests rot unnoticed. — `PA:.github/workflows/gateway-model-health.yml:4-7,19-26`; `CA:e2e-tests/conftest.py:7-28`; `SA:.github/workflows/spring-ai-integration-tests.yml:4-28,111-117`; `OA:integration_tests/README.md:29`
- **LT15** — Assert real-model output only on what the test controls — structure, parsed fields, tool arguments, a sentinel or tool marker, side effects — because exact prose flakes and "not empty" catches nothing. — `MA:…/tool-calls-finish-reason.e2e.test.ts:149-159`; `L4J:…/AbstractBaseChatModelIT.java:706`; `ADKJ:…/LangChain4jIntegrationTest.java:159`; `OA:integration_tests/openai/test_handoffs.py:38-39,64-66`; contrast `AJ:…/AwsLiveTest.kt:51`
- **LT16** — Never retry a failed real-model assertion; retry only transport errors, and test the code's own retry by injecting the fault, because blanket reruns hide flaky prompts. — `OA:integration_tests/openai/test_retry.py:34-44,78-79`; contrast `L4J:…/GlobalTestRetryExtension.java:23,37-38`, `SA:.github/actions/do-integration-test/action.yml:33-39`

### Evals (LT17–LT18)

- **LT17** — Have an LLM judge give atomic verdicts, count "not sure" as failing, compute the score in tested code, and never grade with the generating model, because judge arithmetic and self-grading inflate scores. — `MA:…/hallucination/index.ts:44-101`; `MA:…/denominator.test.ts:7-46`; `L4J:…/JudgeVerdict.java:60-65`; `SA:…/RelevancyEvaluatorTests.java:81-107`; contrast `SA:…/QuestionAnswerAdvisorIT.java:187-189`
- **LT18** — Gate an eval on versioned per-metric thresholds over repeated runs, with an explicit pass-rate or minimum rule, because one lucky or unlucky sample decides otherwise. — `ADKP:src/google/adk/evaluation/eval_config.py:469-486,549-551`; `MA:packages/core/src/evals/thresholds.ts:16-26`; `MA:packages/evals/src/vitest/expect-evals.ts:41-52`

## 9. Open for G34 (#133)

1. **Record/replay or not.** PA makes replay the default; the four JVM repos hand-write payloads. Do we record real provider traffic (LT12–LT13), or keep hand-written fixtures and rely on LT14 to catch drift?
2. **Where the loop fake sits.** Model port (LT1) only, or also a wire-level scenario server for cross-turn composition (MA)? Aruvii's smoke fake already works at the wire.
3. **When real-model tests run.** Per PR (CA), scheduled (PA, SA, L4J), or manual — and whether a red scheduled run blocks anything.
4. **Evals in the gate.** None of the ten blocks CI on an eval. Do evals stay a separate, reported job (G14-style), or become a gate?
5. **Trajectory strictness.** Exact, in order with extras allowed, or scored (§5)?
6. **Placement.** One `testing/references/llm-tests.md`, or rows in `strategy.md`, `unit-tests.md` and `integration-tests.md`.

## 10. Method

- Shallow clones of each default branch into a scratch folder, pinned in §0. Five readers each took two repos (SA+AJ,
  L4J+ADKJ, OA+CA, PA+ADKP, LG+MA) and the same five layers, citing only lines they opened.
- Every reader's citations were spot-checked by hand with `sed -n`, 4–5 per reader, 23 in all, including
  `OA:src/agents/testing/model.py:487-496`, `PA:tests/conftest.py:107,847-875`, `PA:tests/AGENTS.md:15`,
  `L4J:…/AbstractBaseChatModelIT.java:1269-1286`, `L4J:.github/workflows/main.yaml:183-186`,
  `ADKJ:…/TestLlm.java:197-207`, `SA:…/ScriptedChatModel.java:73-76`, `SA:…/QuestionAnswerAdvisorIT.java:187-189`,
  `MA:…/llm-recorder.ts:608`, `LG:libs/prebuilt/tests/model.py:36`. All matched.
- Not re-measured: R19's unit/IT counts and star counts (`research/23`); agent-platform's current state.
