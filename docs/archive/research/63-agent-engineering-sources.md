# R35 · Agent-engineering sources — how to develop agent / LLM features well

Ticket: `chiyanram/skills#79` (R35, part of map #9, follows R32 `research/50-spring-ai-sources.md` §4/§6). Read 2026-10-04.
Scope: practices that do not depend on any library, for a worker that **owns its agent loop** and **hand-rolls raw-HTTP adapters**.
Spring AI is out of scope (#76 closed: no Spring AI API is used; ADR-0015 + AGENT-PRINCIPLES #1 stand).
**Candidates only.** No rule enters a reference without the operator's yes (map #9 Notes, `00-reference-format.md`).

Contents: §0 abbreviations · §1 source rating · §2–§8 the seven areas · §9 what no source covers · §10 candidate rules AE1–AE53 · §11 what was read

## 0. Abbreviations

| key | means | pinned at |
|---|---|---|
| **AP** | agent-platform `origin/master`, read with `git show`, never checked out | `772736bf` (2026-10-03) |
| `W/` · `SH/` · `G/` | `aruvii-worker/src/main/java/ai/aruvii/worker/` · `aruvii-shared/src/main/java/ai/aruvii/shared/` · `aruvii-guardrails/src/main/java/ai/aruvii/guardrails/` | AP |
| **CO** | `W/chat/ChatOrchestrator.java` | AP |
| **AS** | `anthropics/skills` → `skills/claude-api/` | `8a1541c` (2026-09-28) |
| **CB** | `anthropics/claude-cookbooks`; notebooks cited as `file.ipynb [cell N]` | `d7265d6` (2026-09-28) |
| **AD** | platform.claude.com docs; cited as page + section | fetched 2026-10-04 |
| **AE-blog** | anthropic.com/engineering essays. Quotes came through a summariser and are marked *(verify)* | fetched 2026-10-04 |
| **OA** | `openai/openai-agents-python` | `81f0ccf` (2026-10-02) |
| **OG** | OpenAI "A practical guide to building agents" (PDF), cited by page | 2025 |
| **PA** | `pydantic/pydantic-ai`; `PA/…` = `pydantic_ai_slim/pydantic_ai/…` unless the path says `pydantic_evals` or `docs` | `c68786e` (2026-10-03) |
| **ADK** | `google/adk-python` → `src/google/adk/` | `51dbf89` (2026-10-03) |
| **LG** | `langchain-ai/langgraph` → `libs/` | `9a0394d` (2026-10-03) |
| **12F** | `humanlayer/12-factor-agents` → `content/` (REF) | `d20c728` (2025-09-21) |
| **ACE** | `humanlayer/advanced-context-engineering-for-coding-agents` `ace-fca.md` (REF) | `f2bc7ae` |
| **WSH** | `wshobson/agents` → `plugins/` | `156b7a5` (2026-09-28) |
| **OWASP** | OWASP Top 10 for LLM Applications 2025, genai.owasp.org/llmrisk/…, §Prevention and Mitigation | 2025 edition |
| **MCP** | `modelcontextprotocol/modelcontextprotocol` spec rev `2026-07-28` (`docs/specification/2026-07-28/…`) | `75db1e9` (2026-10-03) |
| **OTG** | `open-telemetry/semantic-conventions-genai` `docs/gen-ai/…` (read over the web: section cites, no line numbers) | `e07f4eb` (2026-10-02) |

REF = `agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/`. The other clones are in the session scratchpad `refs/`.

**Caveat on OTel.** The usual clone `open-telemetry/semantic-conventions@a0dab2b` no longer holds GenAI. `docs/gen-ai/gen-ai-spans.md:5-11` is a stub pointing to OTG.
`gen_ai.client.token.usage` is deprecated there (`model/gen-ai/deprecated/metrics-deprecated.yaml:54-73`). The whole GenAI set is still **Status: Development**.

## 1. Source rating

Scale per column: ●●● strong · ●● adequate · ● weak · ○ none. **Rules** means imperative, checkable statements. **Teach** means explanation without checkable rules.

| # | Source | Authority | Currency | Depth | Rules / Teach | What makes it strong | Licence |
|---|---|---|---|---|---|---|---|
| 1 | **AS claude-api skill** (`shared/*.md`, `java/`) | ●●● first-party | ●●● names Opus 5.5 | ●●● 10k+ lines. Provider-neutral reasoning sits in `shared/`, syntax in `{lang}/` | **Rules** written for an agent. Gates are written into the prose (spend sign-off `shared/evals/build-eval.md:225-229`; pre-registered gates `cost-hillclimb.md:328-341`) | The rules come from incidents (tolerant parser, escaping drift, `pause_turn` not auto-resumed). Every check is measurable (cache meters, noise floor) | Apache-2.0 |
| 2 | **AD platform docs** (stop reasons, errors, rate limits, streaming, tool use, mitigate-jailbreaks, develop-tests) | ●●● API contract | ●●● live | ●●● exact | **Rules** (wire contract) | Spells out the cases a raw client gets wrong: spend-cap 429, error after HTTP 200, cumulative usage | © Anthropic, quote only |
| 3 | AE-blog: building-effective-agents · effective-context-engineering · writing-tools-for-agents | ●●● | ●● (2024-12, 2025-09, 2025-09) | ●● | Teach | Gives the principles (simplest tier, bounded loops, poka-yoke, context as a budget). Writing-tools is built around an eval loop | © Anthropic |
| 4 | CB cookbooks (`tool_use/`, `tool_evaluation/`, `claude_agent_sdk/`, `misc/`) | ●●● | ●● some cells stale (`misc/sampling_past_max_tokens.ipynb [cell 8]` prefill now 400s) | ●● runnable | Teach | Measures trade-offs (clearing vs compaction) on a real run | MIT |
| 5 | **OA OpenAI Agents SDK** (run loop, `RunState`, guardrails, tracing, retry) | ●●● vendor SDK | ●●● | ●●● | Code = de-facto rules; docs teach | Pause is a serialisable return value. The adapter *advises* a retry and the runner *decides*. Replay safety is its own axis | MIT |
| 6 | OG OpenAI practical guide | ●●● | ●● | ● taxonomy | Teach | The only usable guardrail taxonomy plus tool risk tiers (p24-31) | © OpenAI, paraphrase |
| 7 | **PA Pydantic AI + pydantic_evals** | ●●● | ●●● | ●●● deepest on the neutral message model, retries, OTel, evals | Code + explicit design docs (`docs/retries.md`, `docs/message-history.md`) | One closed message model. Per-model capabilities are data (`ModelProfile`). Finish reason is kept apart from loop state | MIT |
| 8 | **ADK Google ADK** (+ adk.dev callbacks / safety pages) | ●●● | ●●● | ●●● loop, plugins, eval, OTel | Code + contract docstrings | One guard contract at every seam. Resume is a pure function over the event log. Trajectory evals | Apache-2.0 |
| 9 | **LG LangGraph** | ●●● | ●●● | ●●● durability; no eval, no OTel in core | Code + docstrings | Saves each task's writes before the checkpoint, so resume skips finished calls. Retry decided by one pure classifier | MIT |
| 10 | **OWASP LLM Top 10 2025** (LLM01/02/05/06/07/10) | ●●● | ●● 2025 | ●● | Rules-ish (mitigation lists, no MUST) | Consistent on placement: controls live in deterministic code around the model | CC BY-SA 4.0, cite + paraphrase |
| 11 | **MCP spec** rev 2026-07-28 | ●●● normative | ●●● | ●●● protocol, ● host policy | **Rules** (RFC 2119) | Tool annotations are untrusted; a human SHOULD be able to deny calls; tool errors are split into execution vs protocol | MIT / CC-BY |
| 12 | **OTG OTel GenAI semconv** | ●●● CNCF | ●● Development, names churn | ●●● attribute-level | **Rules** (Required / Recommended / Opt-In) | Settled shape: span per model call, per tool call and per run; content capture opt-in | Apache-2.0 |
| 13 | 12F 12-factor-agents | ●● practitioner | ● stale 1 yr | ●● | Teach / principles | The best argument for owning control flow (F1, F4, F8). Weak on idempotency | **CC BY-SA 4.0 — cite only** |
| 14 | ACE advanced context engineering | ● coding agents | ●● | ●● anecdotal | Teach | Utilisation target, intentional compaction. Its human-review loop does not transfer to unattended product agents | no LICENSE, cite only |
| 15 | WSH wshobson/agents `llm-application-dev` | ● single author | ●●● | ● wide, shallow, Python / LangChain / LangSmith | Catalogue | Only usable part: regression vs a stored baseline + judge-vs-human agreement (`llm-evaluation/references/details.md:247-433`) | MIT |
| 16 | rmyndharis/antigravity-skills (port of WSH) | ● | ●●● | metadata only | — | Adds nothing original over WSH | MIT |

**Ranking for rules.** Primary: AS + AD (wire contract and incident-derived rules). Design reference: OA, PA, ADK, LG, used to show *how* to build a rule, not as rule text.
Normative cross-cuts: OTG (observability), MCP (tools), OWASP (guard placement). 12F, ACE and WSH are supporting citations only.

## 2. ADAPTER — requests, tool calls, streaming, errors, retries

**What the references say**

| ref | says (≤15 words) | cite |
|---|---|---|
| AD | stop reasons are a closed set; "Always check stop_reason … using a match/switch" | handling-stop-reasons §Quick reference, §Best practices |
| AD | "an error can occur after the API returns a 200 response" | errors §HTTP errors; streaming §Error events |
| AD | spend-cap 429 "has no `retry-after` header" — retries keep failing | errors §HTTP errors; rate-limits §Reaching your spend cap |
| AD | streamed `usage` in `message_delta` is cumulative; "handle unknown event types gracefully" | streaming §Event types, §Other events |
| AS | 429/500/529 retryable; 400/401/403/404/413 not | `shared/error-codes.md:7-17` |
| AS | "a truncated input usually parses as a valid partial object" | `shared/tool-use-concepts.md:72` |
| AS | build the INVALID_JSON error "with the JSON library (not string concatenation)" | `shared/tool-use-concepts.md:76-87` |
| OA | adapter returns `get_retry_advice`; `RetryDecision` "never bypasses replay protection" | `src/agents/models/interface.py:58`; `src/agents/retry.py:117-131` |
| PA | finish reasons "Mostly normalized to OpenTelemetry semantic convention values" | `messages.py:142-148` |
| PA | retries stack: one logical call can mean "N×M×K wire requests" | `docs/retries.md:23-33` |
| ADK | tool calls found from content parts; `tool_use` maps to plain STOP | `models/anthropic_llm.py:310-317` |
| ADK | Anthropic cache tokens are "disjoint from input_tokens" — the adapter folds them | `models/anthropic_llm.py:756-774` |
| LG | default retry: connection errors and 5xx; `ValueError`/`TypeError` never | `langgraph/langgraph/_internal/_retry.py:1-29` |
| OTG | `gen_ai.usage.input_tokens` SHOULD include cached tokens | gen-ai-spans.md §Inference |

**How the SDKs build it inside**
- **Adapter = pure translator + error normaliser.** OA has one `Converter` with two directions (`chatcmpl_converter.py:123,534`) and a stream handler that folds deltas into the same items. PA and ADK do the same with one closed message model (`PA messages.py:3046`; `ADK models/llm_response.py:117-139`).
- **Policy lives above the adapter.** OA merges adapter advice with app policy in the runner (`run_internal/model_retry.py:116-136`). PA and ADK implement fallback as a decorator over the model port (`PA models/fallback.py:90-145`; `ADK models/_fallback_model.py:15`).
- **Finish reason is not loop control.** PA keeps `finish_reason` (what the provider said) apart from `state` (what the loop does) (`messages.py:149-155`). Per-model capabilities are a record, not `if provider ==` (`profiles/__init__.py:54-209`).

**Our state (AP)**
- Neutral port `LlmAdapterPort.complete` (`SH/llm/LlmAdapterPort.java:11-24`). `FinishReason` has 4 values, `STOP, LENGTH, TOOL_CALL, ERROR` (`SH/llm/FinishReason.java:3-8`).
- Anthropic maps everything except `max_tokens` and `tool_use` to STOP, including `refusal` and `pause_turn` (`W/llm/AnthropicChatAdapter.java:167-172`). OpenAI maps `content_filter` to STOP (`W/llm/OpenAiChatAdapter.java:148-154`).
- The orchestrator reports LENGTH as `"STOP"` (`CO:1289-1294`).
- Anthropic defaults `max_tokens` to 1024 (`AnthropicChatAdapter.java:73`). The orchestrator always passes `maxTokens=null` (`CO:511-512`).
- Malformed tool arguments become `Map.of()` (`CO:1278-1286`).
- Errors are an exception hierarchy (`SH/llm/exception/LlmException.java:7-30`). Retry-After is parsed (`W/llm/AdapterHttpHelper.java:111-119`) and read by nobody. Retry is a fixed backoff of 500 ms to 5 s (`CO:842-853`).
- Some errors are classified by string match (`CO:1307-1353`).
- `retryWhen` re-subscribes after deltas were already emitted (`CO:861-881`; `OpenAiChatAdapter.java:328-330`).
- Anthropic and Ollama only pseudo-stream (`AnthropicChatAdapter.java:192-195`). Bedrock throws (`BedrockChatAdapter.java:25-30`).
- `cache_creation_input_tokens` is never read (`AnthropicChatAdapter.java:207-213`). Pricing subtracts cached from input (`aruvii-infra/.../PricingResolverAdapter.java:144-146`), which double-discounts Anthropic.
- Fallback sends the primary's model name to another provider (`CO:536`).

**Gap:** the stop-reason type is too small. Truncation and refusal are invisible. Retry policy sits inside a reactive chain that cannot tell "response started" apart. Usage folding is wrong for Anthropic.

## 3. LOOP — typed tool calls, approvals and pauses, resumability

**What the references say**

| ref | says | cite |
|---|---|---|
| OA | step results: `NextStepFinalOutput`, `NextStepRunAgain`, `NextStepInterruption`, `NextStepHandoff` | `src/agents/run_internal/run_steps.py:162-188` |
| OA | RunState schema: "Forward compatibility is intentionally fail-fast" | `src/agents/run_state.py:205-212` |
| OA | approvals scoped to tool-call ID; default tool error hides the exception | `docs/human_in_the_loop.md:50-55`; `src/agents/tool.py:1975-1978` |
| PA | approval is a run *output*: `DeferredToolRequests` / `DeferredToolResults` keyed by call id | `_deferred.py:28-170` |
| PA | client history can fabricate approvals "no human granted" | `docs/message-history.md:516-528` |
| ADK | on resume, the approved call must "match the original function calls in history" | `flows/llm_flows/tools/_confirmation.py:80-85` |
| ADK | resume is a pure decision CONTINUE / PAUSE / REPLAY_CALLS | `flows/llm_flows/core/_resume.py:42-75,353` |
| ADK | resumable apps "only guarantee an at-least-once behavior" | `apps/_configs.py:29-45` |
| ADK | "A name the model invented is the model's own mistake to correct" | `flows/llm_flows/tools/_error_handler.py:82-87` |
| LG | a step's completed writes are skipped on resume | `checkpoint/.../base/__init__.py:301-308`; `langgraph/pregel/_loop.py:784-823` |
| LG | interrupt: the graph resumes "re-executing all logic" of the node | `langgraph/langgraph/types.py:886-908` |
| AD | `pause_turn`: send content back; "Do NOT add an extra user message" | AS `shared/tool-use-concepts.md:132-149` |
| AD | tool_result blocks "must immediately follow" the tool_use turn and come first | handle-tool-calls §Important formatting requirements |
| MCP | "there SHOULD always be a human in the loop" able to deny tool calls | `server/tools.mdx:32-33` |
| MCP | tool execution errors use `isError`; clients SHOULD pass them to the model | `server/tools.mdx:765-785` |
| 12F | pause between tool *selection* and *invocation* (paraphrase) | `factor-08…md:73-77` |
| 12F | per-tool error cap of about 3, then escalate (paraphrase) | `factor-09…md:31,62` |
| OG | escalate to a human on failure thresholds and on high-risk actions | p31 |

**How the SDKs build it inside**
- The loop is a **switch over typed step values**. A pause is just another value. The runner returns, serialises versioned state, and resume feeds decisions keyed by call id into the same switch (OA, PA).
- ADK and LG make **crash recovery and human approval one mechanism**. Each tool result is persisted before the loop advances. "What next" is a pure function of the log. Resume replays only the unfinished calls.
- Model-correctable faults (unknown tool, bad arguments, denied approval) come back to the model as **data**. Platform faults propagate.

**Our state (AP)**
- Sealed `TurnOutcome` at turn end (`W/chat/TurnOutcome.java:19-73`) with one closer, `TurnRunner.finalizeTurn` (`W/chat/TurnRunner.java:63-93`).
- Unknown tool and schema-invalid arguments are fed back to the model (`CO:632-644`; `aruvii-tools/.../ToolService.java:499-517`).
- **Approval does not pause.** The loop injects a synthetic `approval_required` result and pays another LLM call (`CO:703-721`; ADR-0015 `:59-67`).
- **Resume is a second-class loop.** It makes one LLM call and drops the tool calls in that reply (`CO:1098-1110`). It has no budget, PAUSED or guard check, no `llm_call_log` row, and runs the tool with `requesterUserId=null` (`CO:1042-1043`).
- Loop state is not persisted per step. A crash mid-turn fails the turn (`W/lease/LeaseSweepJob.java:12-19`).
- The step cap is global (`CO:505`). There is no per-tool failure cap. Tools are dispatched sequentially (`CO:622-758`).
- AGENT-PRINCIPLES #2, #4, #5, #8 and #9 record this as planned or open.

**Gap:** a pause is not a pause, and resume does not run the same loop with the same checks. Nothing persists per-call results.

## 4. CONTEXT — assembly, token budget, compaction, prompt caching

**What the references say**

| ref | says | cite |
|---|---|---|
| AS | "Prompt caching is a prefix match. Any change … invalidates everything after it." | `shared/prompt-caching.md:7-11` |
| AS | order inputs by stability; per-request values "eliminate or move to the very end" | `shared/prompt-caching.md:21-27` |
| AS | silent invalidators: `now()` in system, early UUIDs, unsorted JSON, per-user tool sets | `shared/prompt-caching.md:107-114` |
| AS | forks (summariser, sub-agent) copy parent system, tools, model "verbatim" | `shared/prompt-caching.md:99` |
| AS | never estimate Claude tokens with tiktoken; it undercounts by about 15-20% | `shared/token-counting.md:3-10` |
| AS | "Don't truncate inputs … rather than silently truncating" | `SKILL.md:576` |
| AE-blog | context is "a finite resource with diminishing marginal returns" *(verify)* | effective-context-engineering §Why |
| CB | clearing is lossless if the tool is re-callable; compaction is "lossy in a controlled way" | `tool_use/context_engineering/context_engineering_tools.ipynb` (~md :315-331) |
| PA | history processors are `list[ModelMessage] -> list[ModelMessage]`; repair pass pairs calls and results | `_history_processor.py:11-21`; `docs/message-history.md:251-262` |
| PA | "Slice on message boundaries that keep each call with its result" | `docs/message-history.md:892` |
| OA | one `call_model_input_filter` runs immediately before each model call | `src/agents/run_config.py:68-73,448` |
| ADK | compaction is an appended event covering a range; trigger is a token threshold | `events/event_actions.py:58-74`; `apps/_configs.py:51-80` |
| ADK | cache marker placed by the adapter at the static-prefix end | `models/llm_request.py:124-132`; `models/anthropic_llm.py:877-888` |
| 12F | one owned function builds the next input from the thread (paraphrase) | `factor-03…md:7,116-140` |
| ACE | keep utilisation in "the 40%-60% range" (coding agents) | `ace-fca.md:218` |

**How the SDKs build it inside**
- **Storage and send are separate seams.** What the conversation stored is not what this request sends. A pure filter or processor chain shapes the send. A fixed repair step restores provider invariants without wall-clock data, so caches survive (OA, PA).
- History is **append-only**. Compaction appends a summary event and the request builder substitutes it (ADK).
- Caching is an **adapter concern driven by a stable-prefix index** (ADK). It is verified from usage meters, not assumed (AS).

**Our state (AP)**
- Three assembly paths: main (`CO:486-491`), resume (`CO:1008-1010`), summariser (`W/chat/DefaultLlmSummarizer.java`). AGENT-PRINCIPLES #3 is open.
- **`PromptCacheService` caches nothing.** It is an in-memory `hashCode` comparison (`W/chat/PromptCacheService.java:31-63`), and no `cache_control` is ever sent (`AnthropicChatAdapter.java:71-124`). The cost path passes `cachedInputTokens=0` (`CO:552`).
- The window counts messages, not tokens (`W/chat/MemoryWindower.java:68-86`). It can open with an orphan TOOL frame (`:88-95`). The 4 KB stub drops the tool name (`:128-133`).
- `HistoryCompressor` re-summarises every turn past 40 messages (`W/chat/HistoryCompressor.java:74-88`). It is called twice per turn (`CO:406,490`), runs synchronously, and is unbilled.
- The budget estimate is messages × 100 (`W/chat/TokenBudgetChecker.java:24`).
- The semantic cache keys on the user text only (`W/chat/SemanticCacheService.java:69-100`).

**Gap:** no stable-prefix discipline and no real caching. The count-based window can break call/result pairing. Compaction is not idempotent.

## 5. GUARD — input, output and tool guardrails

**What the references say**

| ref | says | cite |
|---|---|---|
| AD | "Put untrusted content only in tool results … never in `system`" | mitigate-jailbreaks §Indirect prompt injection |
| AD | "JSON-encode untrusted content"; screen tool outputs with a classifier returning a structured verdict | same section |
| AS | model-supplied tool inputs are untrusted: allowlists, canonical paths, no shell operators | `shared/tool-use-concepts.md:499-509` |
| AS | dedicated tools give the harness a hook "it can intercept, gate, render, or audit" | `shared/agent-design.md:24-33` |
| OA | guard verdict `tripwire_triggered`; blocking mode means the "agent never executes" | `src/agents/guardrail.py:20-29`; `docs/guardrails.md:36-38` |
| OA | tool guard verdict: allow · reject_content(message) · raise_exception | `src/agents/tool_guardrails.py:60-117` |
| OA | a rejected output is not persisted; a placeholder is stored | `docs/guardrails.md:54-56` |
| OA | approval predicates fail closed on malformed arguments | `docs/human_in_the_loop.md:15` |
| PA | HITL approval does not replace authorization: the tool re-checks | `docs/deferred-tools.md:108` |
| ADK | non-None return "will short circuit all remaining plugins and agent callbacks" | `plugins/base_plugin.py:55-62` |
| ADK | a plugin that throws fails the run (fail closed) | `plugins/plugin_manager.py:277-320` |
| ADK | one fixed per-call pipeline: guards → confirmation gate → run → guards | `flows/llm_flows/tools/_caller.py:497-625` |
| OG | tool risk "low, medium, or high"; guardrails are "a layered defense mechanism" | p25-26 |
| OWASP | LLM01 #6 segregate external content; LLM05 treat output as untrusted user input | llm01 / llm05 §Prevention |
| OWASP | LLM06 complete mediation, run in the user's context; LLM07 prompts are not security controls | llm06 / llm07 §Prevention |
| MCP | clients "MUST consider tool annotations to be untrusted" unless from trusted servers | `server/tools.mdx:305-306` |
| MCP | prefix tool names with a server id; `serverInfo.name` is not unique | `server/tools.mdx:324-331` |

**How the SDKs build it inside**
- **One interception contract at every seam:** `hook(ctx, input) -> Continue | ShortCircuit(result)`. Global guards run before agent guards. The first short-circuit wins, and a throwing guard fails the run (ADK). LG does the same as around-advice, `(request, next)`, with immutable request copies (`prebuilt/langgraph/prebuilt/tool_node.py:171-215`).
- Guards are **placed in three tiers**: run input (blocking or parallel), run output, per-tool in/out with a three-way verdict (OA).
- Tool risk is **static metadata on our side** that drives pause and escalation (OG, OWASP, MCP).

**Our state (AP)**
- The input injection scan is a list of 7 regexes (`SH/security/InjectionPatternMatcher.java:23-55`). It hard-blocks the turn (`CO:415-425`) and ignores its own setting (`G/application/SystemPromptGuard.java:18-20`).
- PII redaction runs in tiers 1-3. Tier 2 (NER) fails open (`G/application/GuardrailPipeline.java:25-27`). Tier 3 returns ALLOW on any error (`G/infrastructure/CustomPiiEndpointClient.java:29-30,98-125`).
- Tool output is sanitised before the LLM sees it (`G/application/ToolOutputSanitizer.java:129-151`).
- **No guard on model output.** Deltas stream to the client unchecked (`CO:879-881`) and are persisted and cached (`CO:589-597`).
- Earlier USER turns are re-sent unredacted (`MemoryWindower.java:32-33,99`).
- Tool output is not delimited or labelled before it enters context (`CO:736-737`).
- Verdicts are logs only (`CO:419-453`).
- `ApprovalGate` is off when it has no context (`ApprovalGate.java:33`, #611).

**Gap:** fail-open guards, no output seam, regex-only injection screening, no single tool pipeline with a declared risk class.

## 6. OBS — GenAI observability

**What the references say**

| ref | says | cite |
|---|---|---|
| OTG | inference span `{gen_ai.operation.name} {gen_ai.request.model}`, kind CLIENT; Required `operation.name`, `provider.name` | gen-ai-spans.md §Inference |
| OTG | Recommended: `response.model`, `response.finish_reasons`, `usage.input/output_tokens`, `cache_read`/`cache_write` | gen-ai-spans.md §Inference |
| OTG | content attributes Opt-In; "SHOULD NOT capture this attribute by default" | gen-ai-spans.md §Capturing instructions, inputs, and outputs |
| OTG | `execute_tool` span (INTERNAL) with `gen_ai.tool.name`, `tool.call.id`; `invoke_agent` span per run | gen-ai-spans.md §Execute tool; gen-ai-agent-spans.md |
| OTG | token counters `gen_ai.client.inference.usage.*`; old `gen_ai.client.token.usage` deprecated | gen-ai-token-metrics.md; old repo `metrics-deprecated.yaml:54-73` |
| PA | instrumentation is a decorator over any Model (`InstrumentedModel(WrapperModel)`) | `models/instrumented.py:333` |
| ADK | content "replaced with <elided>" unless capture is enabled | `telemetry/_stable_semconv.py:45-48` |
| ADK | tool span marked errored when the tool *returns* an error | `flows/llm_flows/tools/_error_handler.py:37-57` |
| OA | span kinds mirror the loop: agent, turn, generation, function, guardrail | `src/agents/tracing/create.py:89-466` |
| AS | read `model` from the *response* and assert it; time the final attempt only | `shared/evals/eval-audit.md:113,135` |
| AS | cache regressions are silent: "the bill is just higher - no error" | `shared/prompt-caching.md:196` |
| AD | log `request-id` from every response | errors §Request ID |

**How the SDKs build it inside**
- The span taxonomy mirrors the loop's own nouns: run → model call → tool call (+ guard).
- **Instrument the port once**, not each adapter (PA). Attribute names come only from semconv. Non-standard names are namespaced and documented.
- A single switch governs whether content enters spans.

**Our state (AP)**
- There are 6 meters in total. None is per LLM call (`CO:224-227,290-291`; `PromptCacheService.java:36-41`; `SemanticCacheService.java:59-62`).
- No `gen_ai.*` attribute, no `ObservationRegistry`, no spans. AGENT-PRINCIPLES #13 is open, #625.
- `llm_call_log` is written **only on success** (`CO:564-566`). The outer catch writes nothing (`CO:771-784`), so the `RATE_LIMIT_HIT` alert can never fire (`AlertEvaluatorJob.java:56-58`).
- Cached and reasoning tokens are hard-coded to 0 (`CO:810`).
- Resume and summariser calls are not logged at all (`CO:1098-1108`).

**Gap:** no per-call record of failures, no spans, wrong cache meters.

## 7. EVAL — LLM judge, golden sets, regression

**What the references say**

| ref | says | cite |
|---|---|---|
| AS | grader order: programmatic → pairwise → pointwise rubric → human; "pick the cheapest one that genuinely measures" | `shared/evals/build-eval.md:78-83` |
| AS | "The runner must call the user's actual entry point" | `shared/evals/build-eval.md:228` |
| AS | infra failures distinguished from model failures; truncation is `status: truncated` | `shared/evals/eval-audit.md:95-107` |
| AS | oracle + null baseline first; noise floor (25 cases × 2 reps ≈ ±14 points) | `shared/evals/eval-audit.md:123,185` |
| AS | judge biases: position, verbosity, self-preference; calibrate to human labels | `shared/evals/eval-audit.md:173-179` |
| AS | "grade the end state, not the transcript" (agents that act) | `shared/evals/eval-audit.md:147-149` |
| AD | use "a different model to evaluate"; edge cases: irrelevant, long, ambiguous input | develop-tests §LLM-based grading, §Edge cases |
| AD | red-team with documents and tool outputs "that deliberately contain injection attempts" | mitigate-jailbreaks §Red-team |
| PA | `Case` / `Dataset` as data; `LLMJudge{rubric}`; diff report against a baseline | `pydantic_evals/pydantic_evals/dataset.py:111,178`; `reporting/__init__.py:394-428` |
| PA | `HasMatchingSpan` asserts on the trace (tool X called) | `pydantic_evals/.../evaluators/common.py:367-377` |
| ADK | trajectory match EXACT / IN_ORDER / ANY_ORDER; default criteria tool 1.0, response 0.8 | `evaluation/trajectory_evaluator.py:45-60`; `eval_config.py:236-238` |
| ADK | each eval set run `NUM_RUNS = 2`; judge `num_samples=5`, majority vote | `evaluation/agent_evaluator.py:73,152`; `eval_metrics.py:127-138` |
| ADK | `EvalStatus` includes NOT_EVALUATED; efficiency metrics informational | `evaluation/eval_metrics.py:47-53` |
| WSH | regression detector, relative threshold 0.05 vs baseline; inter-rater agreement | `llm-evaluation/references/details.md:247-320,383-433` |
| OWASP | LLM01 #7 adversarial testing "treating the model as an untrusted user" | llm01 §Prevention |

**How the SDKs build it inside**
- An eval case is a **recorded conversation + initial state + expected trajectory + expected answer or rubric**. Evaluators are small typed functions, deterministic first.
- The runner executes each case N times, aggregates, and fails as an ordinary test (ADK).
- Reports diff against a stored baseline (PA). Infrastructure failures get their own status (AS, ADK).
- **Tension:** AS says grade outcomes, not paths. ADK and PA score trajectory. Read together: trajectory checks are for required or forbidden calls (safety, approvals), and the end state is for task success.

**Our state (AP)**
- Scoring is keyword `expectedContains` plus an optional judge (`W/eval/DefaultAgentEvalRunner.java:203,221-233`).
- `expectedToolCalled` **can never pass**: the runner passes `null` (`:203`).
- The judge rubric is the keyword list (`:41-47`). It runs a single sample and can be the agent-under-test's own model (`W/eval/JudgeModelResolver.java:22`).
- The judge goes through the full chat path, so the injection regex and the semantic cache apply to it.
- A missing `pass` becomes a CONFIDENT fail (`W/eval/JudgeVerdictParser.java:55-56`; `JudgeConfidence.java:32-34`).
- Evals run real tools (`dryRun=false`, `DefaultAgentEvalRunner.java:181-190`).
- No golden set and no regression gate anywhere in the build (field report `docs/research/agent-sdk-field-report.md:23`).

**Gap:** effectively no eval discipline yet: no baseline, no repeats, no calibration, infrastructure failures conflated with model failures.

## 8. COST — rate limiting, budgets, cache economics

**What the references say**

| ref | says | cite |
|---|---|---|
| PA | `UsageLimits`: request limit checked before each request, token limits after each response | `usage.py:471-549` |
| PA | `AbstractConcurrencyLimiter{max_running, max_queued}`, Redis-backed for multi-process | `concurrency.py:35-47` |
| PA | `UsageLimits` "bounds only N"; it never sees transport retries | `docs/retries.md:31` |
| ADK | per-invocation cost manager increments at the model-call chokepoint → `LlmCallsLimitExceededError` | `agents/invocation_context.py:57-87` |
| OA | keep per-request usage entries; run totals are sums | `docs/usage.md:11-55` |
| AD | rate limits are a token bucket; "ramp up your traffic gradually" | rate-limits §About rate limits |
| AD | "only uncached input tokens count toward your ITPM" | rate-limits §Cache-aware ITPM |
| AS | `max_tokens` is "a backstop, not a tuning knob" | `shared/cost-optimization.md:144` |
| AS | adopt a cost change only if quality, cost and mechanism gates pass, registered beforehand | `shared/evals/cost-hillclimb.md:328-341` |
| AS | if inputs fully determine the output, write it as plain code | `shared/prompt-audit.md:181` |
| CB | "cost per task instead of cost per token" | `cost_optimization/cost_optimization.ipynb [cell 12]` |
| OWASP | LLM10: rate limits + per-entity quotas, timeouts, "Limit Queued Actions" | llm10 §Prevention |

**How the SDKs build it inside**
- A **limits value object checked at two fixed points** (before the call, after the response), producing a typed stop.
- **Concurrency limiting is its own seam** with a bounded queue.
- Each layer knows which retries it cannot see.

**Our state (AP)**
- The rate limit is HTTP-ingress only, on 4 routes (`aruvii-api/.../ratelimit/RateLimitPolicy.java:21-43`). Webhook, Kafka, schedule, task, sub-agent and judge paths bypass it.
- The budget is checked **once per turn, by estimate** (`CO:405-409`). Usage is summed from *closed* interactions only (`aruvii-infra/.../WorkspaceBudgetAdapter.java:28-47`), so concurrent turns all pass.
- Summariser, resume and failed calls are never counted.
- A 429 counts as a circuit-breaker failure (`W/chat/LlmCircuitBreakerConfig.java:38`).
- AGENT-PRINCIPLES #14 is partial and CLAUDE.md's "rate limiting before any LLM call" is not met.

**Gap:** no limiter at the model port, and a budget that is neither per call nor based on actual usage.

## 9. What no source covers — we write these ourselves

| # | gap | nearest source, and why it is not enough |
|---|---|---|
| N1 | **The JVM raw-HTTP mapping tables**: the four-provider stop-reason and usage matrix (Bedrock Converse, Ollama `done` / no tool ids), and Anthropic vs OpenAI cache-token semantics in one record | ADK and PA do it in Python for their own types. No source publishes the table as a rule. The worst R32 gap is unchanged |
| N2 | **Circuit breaker vs retry vs rate limit together** (Resilience4j order; a 429 is back-pressure, not an outage; pseudo-stream vs chunk timeout) | LG gives the retry classifier and AD gives 429 semantics. Nobody says where the breaker sits or what it counts |
| N3 | **Exactly-once side effects across resume**: idempotency keys for tool calls | ADK says at-least-once (`apps/_configs.py:29-45`). LG re-executes nodes. 12F is silent. Nobody gives the key scheme |
| N4 | **Eval sandbox**: evals must not fire real side-effecting tools | Every source assumes eval tools are harmless. Our runner uses `dryRun=false` |
| N5 | **Response (semantic) cache correctness**: key composition, cross-user sharing, invalidation on prompt or tool change | LG `CachePolicy` (`types.py:530-538`) is a node memo with a key function. Nothing addresses LLM answer caches in multi-tenant use |
| N6 | **Workspace budget under concurrency**: reserve-then-settle vs post-hoc sum | PA `UsageLimits` is per run. AGENT-PRINCIPLES #14 found per-tenant budgets only in Mastra and Pydantic's harness |
| N7 | **Output guard on a stream**: check-then-stream vs chunk-level vs retract | OA output guardrails run after completion. Nobody covers token streaming to a UI |
| N8 | **Fallback model mapping across providers** (equivalent model, pricing with the served provider) | PA and ADK fallback assume the caller lists concrete models |
| N9 | **Multi-tenant governance**: approval policy per workspace, guard verdict audit rows, fail-closed defaults as product policy | OWASP and MCP give principles. This is the AGENT-PRINCIPLES "our layer" (#6, #7, #11) |

## 10. Candidate rules (for the operator's review — none approved)

Rule text is ≤30 words. "Our state" cites AP. **adopt** = clear source, clear gap. **hold** = needs an operator decision (structural, open AGENT-PRINCIPLES item, or provider-specific).
AGENT-PRINCIPLES is AP `docs/design/AGENT-PRINCIPLES.md`; a candidate that implements one says so.

### ADAPTER (AE1–AE11)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE1 | Each adapter maps provider stop reasons onto one closed sealed type — end, truncated, tool-call, refused, context-exceeded, error — and the loop switches on it exhaustively. | AD handling-stop-reasons §Quick reference; PA `messages.py:142-148`, `models/anthropic.py:105-113` | 4-value enum `SH/llm/FinishReason.java:3-8`; refusal and pause_turn → STOP `AnthropicChatAdapter.java:167-172`; LENGTH → "STOP" `CO:1289-1294` | adopt |
| AE2 | Never execute tool calls from a reply that stopped on truncation or refusal; end the turn with a typed Truncated or Refused outcome. | AS `shared/tool-use-concepts.md:72`; PA `_agent_graph.py:400-405` | not checked: loop decides on TOOL_CALL only `CO:584` | adopt |
| AE3 | An adapter returns a normalised error value (status, retryAfter, requestId, timeout/network flag, responseStarted); only the loop's retry policy decides whether to retry. | OA `src/agents/retry.py:50-131`, `models/interface.py:58` | exceptions `LlmException.java:7-30`; string-matched classes `CO:1307-1353` | adopt |
| AE4 | Retry only connection errors, 5xx/529 and 429 with retry-after; wait at least retry-after, else jittered capped backoff; never retry other 4xx or a spend-cap 429. | AS `shared/error-codes.md:7-17`; AD rate-limits §Reaching your spend cap; LG `_internal/_retry.py:1-29` | fixed 0.5–5 s backoff `CO:842-853`; retryAfter read by nobody `AdapterHttpHelper.java:111-119` | adopt |
| AE5 | Do not retry a call after its first streamed chunk reached a consumer; a mid-stream failure ends the call as a typed failure. | OA `src/agents/retry.py:93-131`; AD streaming §Error recovery | `retryWhen` re-subscribes after emitted deltas `CO:861-881`; `OpenAiChatAdapter.java:328-330` | adopt |
| AE6 | Accumulate streamed tool arguments until block stop, parse with a JSON library, validate against the schema; a malformed call returns to the model as an error result, never as `{}`. | AD streaming §Input JSON delta; AS `tool-use-concepts.md:69-87`; ADK `models/lite_llm.py:2709-2778` | `parseArgs` → `Map.of()` `CO:1278-1286` (AGENT-PRINCIPLES #2, #537) | adopt |
| AE7 | The adapter folds provider usage into one record — input including cache, cache-read, cache-write, output, reasoning — taking the last cumulative streamed value. | ADK `models/anthropic_llm.py:756-774`; OTG gen-ai-spans §Inference; AD streaming §Event types | cache_creation dropped `AnthropicChatAdapter.java:207-213`; double discount `PricingResolverAdapter.java:144-146`; zeros `CO:810` | adopt |
| AE8 | The SSE parser ignores ping and unknown event types and treats an error event after HTTP 200 as a failure of that request. | AD streaming §Ping/Error/Other events; errors §HTTP errors | Anthropic pseudo-streams `AnthropicChatAdapter.java:192-195`; OpenAI swallows line parse errors `OpenAiChatAdapter.java:323-325` | adopt |
| AE9 | Every request sets `max_tokens` from agent or model configuration, sized as a backstop; no adapter supplies a default. | AS `shared/cost-optimization.md:144`, `SKILL.md:579` | default 1024 `AnthropicChatAdapter.java:73`; orchestrator passes null `CO:511-512` | adopt |
| AE10 | Fallback to another model is a decorator over the adapter port with an explicit model mapping; usage is priced for the provider that served it. | PA `models/fallback.py:90-145`; ADK `models/_fallback_model.py:15` | same model name sent to fallback provider `CO:536`; priced with primary `CO:550-552` | hold — mapping is N8 |
| AE11 | Split each adapter into a pure request mapper, a pure stream accumulator and a thin transport; test the pure parts with recorded provider payloads. | OA `models/chatcmpl_converter.py:123,534`, `chatcmpl_stream_handler.py:392-449` | request body duplicated `OpenAiChatAdapter.java:76-109` vs `:225-261` | hold — structural |

### LOOP (AE12–AE20)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE12 | Classify each model reply into a sealed step result (final, run-again, paused, stopped) and switch exhaustively; a pause is a returned value, never a branch on a status string. | OA `run_internal/run_steps.py:162-188`; PA `_agent_graph.py:600-2609`; 12F factor-01 (cite) | turn end sealed `TurnOutcome.java:19-73`; in-loop branch on status `CO:703-721` (AGENT-PRINCIPLES #2) | adopt |
| AE13 | An approval-required call ends the run with a persisted pending request keyed by tool-call id; the decision resumes through the same loop with the same checks. | OA `docs/human_in_the_loop.md:50-55`; PA `_deferred.py:28-170`; ADK `tools/_confirmation.py:73-101` | no pause `CO:703-721`; one-shot resume `CO:1098-1110` (AGENT-PRINCIPLES #5, #533/#612) | adopt |
| AE14 | On resume, execute a call only if it matches the stored original this agent authored, and re-run authorization and tool guards before executing it. | ADK `_confirmation.py:80-85`, `core/_resume.py:~405`; PA `docs/message-history.md:516-528`, `docs/deferred-tools.md:108`; OA `docs/guardrails.md:77` | resumed tool runs with `requesterUserId=null` `CO:1042-1043` | adopt |
| AE15 | Persist each completed tool result keyed by run, step and call id before advancing; on resume run only calls without a stored result. | LG `checkpoint/.../base/__init__.py:301-308`, `pregel/_loop.py:784-823`; ADK `core/_resume.py:42-75` | not persisted; crash fails the turn `LeaseSweepJob.java:12-19` | hold — journal store is D-F5 (#531); idempotency is N3 |
| AE16 | Return model-correctable faults (unknown tool, schema-invalid arguments, denied approval) as error tool results naming the valid form; end the turn only on platform faults. | ADK `tools/_error_handler.py:79-97`; LG `prebuilt/.../tool_node.py:108,383-392`; MCP `server/tools.mdx:765-785` | held for unknown tool `CO:632-644` and schema `ToolService.java:499-517` | adopt — codifies current |
| AE17 | Tool error text shown to the model is generic and actionable; never forward a raw exception message or stack trace. | OA `src/agents/tool.py:1975-1980`; AD handle-tool-calls §is_error | sanitised `CO:678-701` | adopt — codifies current |
| AE18 | Cap consecutive failures per tool and repeated identical calls; reaching the cap ends or escalates the run with a typed outcome. | 12F factor-09:31,62 (cite); OG p31; PA `exceptions.py:59-112` | no per-tool cap (AGENT-PRINCIPLES #8, D-F9) | adopt |
| AE19 | Check a per-agent model-call ceiling before every model call, including resume; exceeding it ends the run with a typed outcome. | ADK `agents/invocation_context.py:57-87`; PA `usage.py:482,545-549` | global `max_agent_steps` `CO:505`; resume unbounded `CO:1098` (AGENT-PRINCIPLES #9, D-F10) | adopt |
| AE20 | Answer all tool calls of one reply in one message, results first, each matched by its call id. | AD handle-tool-calls §formatting; ADK `tools/_batch_executor.py:60`; MCP `client/sampling.mdx:380,438` | sequential dispatch `CO:622-758`; grouping not verified | hold — verify first |

### CONTEXT (AE21–AE27)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE21 | One pure function builds every model request — chat, resume, summariser, judge — from the run record; no other code appends messages. | OA `run_config.py:68-73`; PA `_history_processor.py:11-21`; 12F factor-03 (cite) | three paths `CO:486-491`, `CO:1008-1010`, `DefaultLlmSummarizer` (AGENT-PRINCIPLES #3) | adopt |
| AE22 | Never separate a tool call from its result when windowing or summarising; a deterministic repair step restores pairing before each request. | PA `docs/message-history.md:251-262,892,955` | window may start on an orphan TOOL frame `MemoryWindower.java:88-95` | adopt |
| AE23 | Render requests in stability order — sorted tools, frozen system prompt, append-only history, per-turn content last; no timestamps or ids before the last cache breakpoint. | AS `shared/prompt-caching.md:7-27,95-114` | no breakpoints `AnthropicChatAdapter.java:71-124` | adopt |
| AE24 | The adapter places provider cache breakpoints at the stable-prefix end; an IT asserts cache-read tokens are greater than zero on the second turn. | AS `prompt-caching.md:196`; ADK `models/anthropic_llm.py:877-888` | `PromptCacheService` is an in-memory hash `PromptCacheService.java:31-63` | adopt |
| AE25 | Window and compaction triggers use token counts from the provider or the last usage; compaction appends one summary per threshold crossing and never rewrites stored turns. | ADK `apps/_configs.py:51-80`, `events/event_actions.py:58-74`; AS `shared/token-counting.md:3-10` | count-based window `MemoryWindower.java:68-86`; re-summarised each turn `HistoryCompressor.java:74-88`, twice `CO:406,490` | adopt |
| AE26 | Bound each tool result before it enters context; a cut result says it was cut and how to fetch more; the full result stays in the run record. | AS `SKILL.md:576`; AE-blog writing-tools §token efficiency *(verify)*; OWASP LLM10 #1 | 4 KB stub without tool name `MemoryWindower.java:43,128-133` | adopt |
| AE27 | A response cache keys on every input that determines the answer (model, prompt version, tools, history, user) or is not used. | LG `langgraph/types.py:530-538` (explicit key function); rest is N5 | user text only, cross-agent rows `SemanticCacheService.java:69-100` | hold — N5 |

### GUARD (AE28–AE36)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE28 | A guard that errors, times out or is unconfigured blocks; configuration may tune a guard's strength but never switch it off. | ADK `plugins/plugin_manager.py:277-320`; OA `docs/human_in_the_loop.md:15` | NER and Tier-3 fail open `GuardrailPipeline.java:25-27`, `CustomPiiEndpointClient.java:98-125` (AGENT-PRINCIPLES #6, #401) | adopt |
| AE29 | Third-party content (tool, RAG, MCP, HTTP) enters context only as tool results, JSON-encoded and labelled with its source; never inside system or user text. | AD mitigate-jailbreaks §Indirect prompt injection; OWASP LLM01 #6 | raw tool body appended `CO:736-737` | adopt |
| AE30 | Check model output before it is persisted, cached or handed to a sink; a rejected output is replaced by a placeholder in every store. | OA `docs/guardrails.md:52-56`; OWASP LLM05 | streamed unchecked `CO:879-881`; persisted and cached `CO:589-597` | adopt — streaming placement is N7 |
| AE31 | Every tool declares a risk class in our configuration; approval policy derives from it, never from the model or from MCP tool annotations. | OG p26; MCP `server/tools.mdx:305-306`; OWASP LLM06 | `ApprovalGate.java:33` off without context (#611) | adopt |
| AE32 | Every tool call runs as the invoking user with permissions re-checked at execution, including after approval; the model never carries authority. | OWASP LLM06 (complete mediation), LLM07; PA `docs/deferred-tools.md:108` | `requesterUserId=null` on resume `CO:1042-1043` (AGENT-PRINCIPLES #7) | adopt |
| AE33 | Every tool call passes one fixed pipeline: schema validation → global guards → agent guards → approval gate → execute → output guards. | ADK `tools/_caller.py:497-625`; MCP `server/tools.mdx:787-805` | split across `ToolService.java:499-534` and `CO:725-744` | hold — structural |
| AE34 | Guard seams return a sealed Continue or ShortCircuit(result); global guards run before agent guards; the first short-circuit wins and is recorded with its guard name. | ADK `plugins/base_plugin.py:55-71,233-369`; OA `tool_guardrails.py:60-117` | guards inline `CO:415-454`; verdicts are log lines `CO:419-453` | hold — structural |
| AE35 | Screen inputs and tool outputs for injection with a classifier giving a structured verdict; a regex hit is one signal, not the only one. | AD mitigate-jailbreaks §screening | 7 regexes, false positives on "act as" `InjectionPatternMatcher.java:23-55` | hold — cost and model choice |
| AE36 | Expose every MCP tool as `<serverId>__<tool>` and validate its result (schema and size) before it enters context. | MCP `server/tools.mdx:324-331,795` | sanitised-name collisions `ToolDescriptorBuilder.java:85-89` | adopt |

### OBS (AE37–AE42)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE37 | Emit one CLIENT span `chat {model}` per provider call carrying operation, provider, request and response model, finish reasons, all usage fields and `error.type`. | OTG gen-ai-spans §Inference; ADK `telemetry/tracing.py:652-715` | no spans (AGENT-PRINCIPLES #13, #625) | adopt |
| AE38 | Emit one `execute_tool` span per tool call and one `invoke_agent` span per run, linked by tool-call id; mark a tool span errored when the tool returns an error. | OTG §Execute tool, gen-ai-agent-spans; ADK `tools/_error_handler.py:37-57` | `tool.call.duration` meter only `CO:224-227` | adopt |
| AE39 | Prompt, completion, system instructions and tool arguments stay out of spans and logs unless one explicit deployment setting turns capture on. | OTG §Capturing (SHOULD NOT by default); OA `docs/tracing.md:143-151`; ADK `_stable_semconv.py:45-48` | no spans yet; principle stated (AGENT-PRINCIPLES #13) | adopt |
| AE40 | Keep GenAI attribute and metric names in one constants class pinned to a dated semconv-genai version; emit `gen_ai.client.inference.usage.*`, never the deprecated `token.usage`. | OTG gen-ai-token-metrics; old repo `metrics-deprecated.yaml:54-73` | none | adopt |
| AE41 | Write a call record for every provider call — failed, retried, resume, summariser, judge — with request-id, served model, retry count and final-attempt latency. | AD errors §Request ID; AS `shared/evals/eval-audit.md:113,135`; OA `docs/usage.md:11-55` | success only `CO:564-566`; none on failure `CO:771-784`, resume `CO:1098-1108` | adopt |
| AE42 | Instrument the model port once as a decorator so every adapter gets identical spans and metrics. | PA `models/instrumented.py:333` | n/a | hold — structural, with #625 |

### EVAL (AE43–AE49)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE43 | Every agent capability has a versioned golden set (input, initial state, expected end state) run through the real entry point; a drop beyond the threshold vs the stored baseline fails. | AS `build-eval.md:228`; ADK `evaluation/eval_case.py:97-186`, `agent_evaluator.py:299`; PA `reporting/__init__.py:394-428` | per-agent rows, no gate (`agent-sdk-field-report.md:23`) | adopt |
| AE44 | Record infrastructure failures, timeouts and truncations as their own eval status; never score them as a failed case. | AS `eval-audit.md:95-107`; ADK `evaluation/eval_metrics.py:47-53` | missing `pass` → confident fail `JudgeVerdictParser.java:55-56`, `JudgeConfidence.java:32-34` | adopt |
| AE45 | Grade programmatically first; use an LLM judge only for judgment properties, with an atomic rubric, structured verdict, candidate text as untrusted data, and a model other than the agent's. | AS `eval-audit.md:147-179`; AD develop-tests §LLM-based grading; PA `evaluators/common.py:225-240` | keyword rubric `DefaultAgentEvalRunner.java:41-47`; self-judge tier `JudgeModelResolver.java:22`; judge via chat path | adopt |
| AE46 | Calibrate a judge against human labels on a sample before it gates; store judge model and prompt version with every score. | AS `eval-audit.md:173-179`; WSH `details.md:247-320`; ADK `eval_metrics.py:127-138` | none | adopt |
| AE47 | Run each case at least twice and sample the judge several times; state the noise floor; a delta inside it counts as no change. | ADK `agent_evaluator.py:73`, `eval_metrics.py:127-138`; AS `eval-audit.md:119,185` | single sample | adopt |
| AE48 | Assert required and forbidden tool calls on the recorded trajectory with a declared match mode; judge task success on the end state. | ADK `trajectory_evaluator.py:45-60`; PA `evaluators/common.py:367-377`; AS `eval-audit.md:147-149` | `expectedToolCalled` can never pass `DefaultAgentEvalRunner.java:203` | adopt |
| AE49 | The golden set includes injection cases (instructions inside tool output and retrieved text); it passes only if no case triggers an unapproved tool call. | AD mitigate-jailbreaks §Red-team; OWASP LLM01 #7 | none | adopt |

### COST (AE50–AE53)

| id | rule | source | our state | rec |
|---|---|---|---|---|
| AE50 | Every model call, from every trigger, passes a rate and concurrency limiter at the model port, shared across workers, with a bounded queue and a typed refusal. | PA `concurrency.py:35-47`; OWASP LLM10 #3, #10; AD rate-limits §About | ingress only `RateLimitPolicy.java:21-43` (AGENT-PRINCIPLES #14, CLAUDE.md) | adopt |
| AE51 | Check run and workspace budgets before each model call and settle them from actual usage after each response; a hit ends the turn with a typed reason. | PA `usage.py:471-549`; ADK `invocation_context.py:57-87`; OWASP LLM10 | once per turn by estimate `CO:405-409`, `TokenBudgetChecker.java:24`; closed interactions only `WorkspaceBudgetAdapter.java:28-47` | adopt — concurrency is N6 |
| AE52 | Report cost per completed task beside pass rate; adopt a cost change only if quality, cost and mechanism gates, registered beforehand, all pass. | CB `cost_optimization.ipynb [cell 12]`; AS `cost-hillclimb.md:328-341` | cost per call only (`llm_call_log`) | hold — needs AE43 first |
| AE53 | Before adding a model call, check whether its inputs fully determine the output; if they do, write plain code. | AS `shared/prompt-audit.md:181`; 12F appendix-13 (cite) | n/a | hold — design-time teaching, not checkable |

**Count.** ADAPTER 11 · LOOP 9 · CONTEXT 7 · GUARD 9 · OBS 6 · EVAL 7 · COST 4 = **53**, of which **42 adopt / 11 hold**.
14 candidates restate an AGENT-PRINCIPLES item at code level (#2, #3, #5–#9, #13, #14). The reference should cite the principle, not duplicate it.

## 11. What was read

- **AS** in depth: `SKILL.md`; `shared/` agent-design, tool-use-concepts, prompt-caching, prompt-audit, token-counting, error-codes, cost-optimization, managed-agents-client-patterns, `evals/{build-eval,eval-audit,cost-hillclimb}`; `java/` pages.
- **CB**: `tool_use/context_engineering`, `tool_evaluation`, `claude_agent_sdk/01,03`, `cost_optimization`, `misc/sampling_past_max_tokens`.
- **AD** pages: handling-stop-reasons, errors, rate-limits, streaming, prompt-caching, develop-tests, mitigate-jailbreaks, define/handle tool calls.
- **AE-blog**: three essays.
- **OA**: `run.py`, `run_internal/`, `models/interface.py`, chat-completions converter and stream handler, `retry.py`, `guardrail.py`, `tool_guardrails.py`, `tool.py`, `run_state.py`, `tracing/`, `usage.py`, docs. **OG** PDF text.
- **PA**: `messages.py`, `models/__init__.py`, `anthropic.py`, `openai.py`, `fallback.py`, `instrumented.py`, `_instrumentation.py`, `_agent_graph.py`, `_deferred.py`, `_history_processor.py`, `usage.py`, `concurrency.py`, `exceptions.py`, `profiles/`; `pydantic_evals/`; `docs/retries.md`, `message-history.md`, `deferred-tools.md`, `testing.md`.
- **ADK**: `models/`, `flows/llm_flows/` (`core/_resume.py`, `tools/_caller.py`, `_confirmation.py`, `_error_handler.py`, `_batch_executor.py`), `plugins/`, `agents/`, `apps/`, `events/`, `sessions/`, `telemetry/`, `evaluation/`; adk.dev callbacks and safety pages.
- **LG**: `types.py`, `_internal/_retry.py`, `_config.py`, `pregel/_loop.py`, `checkpoint/`, `checkpoint-postgres/`, `checkpoint-conformance/`, `prebuilt/tool_node.py`, `chat_agent_executor.py`.
- **12F** all factors; **ACE** `ace-fca.md`; **WSH** `llm-application-dev/*`, `agent-orchestration/*`; antigravity metadata only.
- **OWASP** LLM01, 02, 05, 06, 07, 10. **MCP** `server/tools.mdx`, `client/sampling.mdx`, `client/elicitation.mdx`, `basic/patterns/cancellation.mdx`, security best practices, `schema.ts`. **OTG** gen-ai-spans, gen-ai-agent-spans, gen-ai-metrics, gen-ai-token-metrics, mcp.
- **AP** @ `772736bf`: `W/llm/*`, `W/chat/*` (ChatOrchestrator, TurnRunner, TurnOutcome, MemoryWindower, HistoryCompressor, PromptCacheService, SemanticCacheService, TokenBudgetChecker, LlmCircuitBreakerConfig, ToolDescriptorBuilder, ApprovalDecisionPublisherAdapter), `W/eval/*`, `W/lease/*`, `SH/llm/*`, `G/*`, `aruvii-tools` ToolService and ToolHandlerPort, `aruvii-api` RateLimitPolicy, `aruvii-infra` pricing and budget adapters; `docs/design/AGENT-PRINCIPLES.md`, ADR-0015, `docs/research/agent-sdk-field-report.md`, `agent-principles-x-sdks.md`, `agent-principles-sdk-reference.md`.
- **Not verified verbatim:** AE-blog quotes (summariser) and OTG (fetched over the web, no line numbers). Re-check both before any rule cites them.
