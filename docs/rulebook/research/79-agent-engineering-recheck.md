# R35 re-check · the agent-engineering candidates AE1–AE53 at today's heads

Ticket `chiyanram/skills#79` (map #130), read 2026-11-09. It re-checks the 53 candidates and 9 gaps of
`research/63-agent-engineering-sources.md` (2026-10-04), now at tag `design-archive-2026-11`:
`git show design-archive-2026-11:research/63-agent-engineering-sources.md`.
**Research only.** No rule here is approved. The operator decides each group in G33 (#132).

Contents: §0 pins · §1 what was not re-checked · §2 status of every candidate · §3 dropped as duplicates ·
§4 surviving candidates by area · §5 the 9 gaps · §6 new GUARD input · §7 where the rules live

**Result.** 17 hold, 36 drifted (21 on line numbers only, 15 in wording or behaviour), 0 gone. No drift weakens a candidate. Six candidates duplicate an approved rule and drop out. 47 survive: ADAPTER 9, LOOP 9, CONTEXT 6, GUARD 8, OBS 6, EVAL 6, COST 3. Recommendations: 42 yes, 3 fog, 2 no.

## 0. Pins

Abbreviations are research/63 §0's. Every clone was blobless, read with `git show`, and no downloaded code was run.

| key | repo | pinned 2026-10-04 | head 2026-11-09 | commits since |
|---|---|---|---|---|
| AS | anthropics/skills `skills/claude-api/` | 8a1541c | 2c5958e (2026-11-06) | 5 |
| CB | anthropics/claude-cookbooks | d7265d6 | ce8b262 (2026-11-04) | 10 |
| OA | openai/openai-agents-python | 81f0ccf | 1fc77bb (2026-11-09) | 119 |
| PA | pydantic/pydantic-ai | c68786e | 59ae8e1 (2026-11-09) | 1486 |
| ADK | google/adk-python `src/google/adk/` | 51dbf89 | 67b217d (2026-11-08) | 653 |
| LG | langchain-ai/langgraph `libs/` | 9a0394d | e5e37b5 (2026-11-06) | 161 |
| 12F | humanlayer/12-factor-agents (cite only) | d20c728 | d20c728 (unchanged) | 0 |
| WSH | wshobson/agents | 156b7a5 | 9c61ab2 (2026-11-08) | 40 |
| MCP | modelcontextprotocol/modelcontextprotocol, spec rev 2026-07-28 (still the newest) | 75db1e9 | 222640c (2026-11-09) | 176 |
| OTG | open-telemetry/semantic-conventions-genai `docs/gen-ai/` | e07f4eb | e6658f1 (2026-11-06) | 71 |
| AD | platform.claude.com docs, read as `.md` | fetched 2026-10-04 | fetched 2026-11-09 | — |
| AE-blog | anthropic.com/engineering essays | summariser quotes, *(verify)* | fetched 2026-11-09; both quotes verified verbatim | — |

Method: for each cite, the old lines were taken at the old pin and searched for at head, exact block first, then the
closest window. Every non-exact match was read by hand. **Holds** means the cited lines are byte-identical at the same
place. **Drifted** means the text moved (new pin given) or its wording or behaviour changed (said what). **Gone** means
the cited behaviour no longer exists anywhere at head.

## 1. Not re-checked

- **Our current state against agent-platform `origin/master`.** agent-platform (Aruvii) is not available in this
  environment, so research/63's "our state" column was not re-read. It is project-side anyway (map #130 Notes,
  "Generic only"), and goes to agent-platform through #135.
- **OWASP LLM Top 10 (genai.owasp.org) and the OpenAI practical guide PDF (cdn.openai.com).** Both hosts are blocked
  by this session's network. They are dated editions (OWASP 2025, OG 2025), so their research/63 cites stand as read
  on 2026-10-04; re-read them before any ledger row cites them.

## 2. Status of every candidate

| id | area | status | what changed, new pin |
|---|---|---|---|
| AE1 | ADAPTER | drifted (lines) | PA `messages.py:142-148` → `:169-175`; PA `models/anthropic.py` split into a package, the stop-reason map is now `models/anthropic/_response.py:26-35`, same values. AD stop reasons unchanged |
| AE2 | ADAPTER | drifted (lines) | AS `tool-use-concepts.md:72` holds; PA `_agent_graph.py:400-405` → `:839-844` |
| AE3 | ADAPTER | holds | OA `retry.py:50-131`, `models/interface.py:58` |
| AE4 | ADAPTER | holds | AS `error-codes.md:7-17`; LG `_internal/_retry.py:1-29`; AD errors `:27` and rate-limits `:61` (spend-cap 429 has no `retry-after`) |
| AE5 | ADAPTER | holds | OA `retry.py:93-131`; AD streaming §Error recovery `:1512` |
| AE6 | ADAPTER | drifted (lines) | AS `tool-use-concepts.md:69-87` holds; ADK `models/lite_llm.py:2709-2778` → `:3703-3772` |
| AE7 | ADAPTER | drifted (content) | ADK folds cache tokens in a new `_prompt_token_count` (`models/anthropic_llm.py:977-988`) and now also splits reasoning tokens out of output (`:991-1008`); OTG moved the "SHOULD include cached tokens" note to `client-inference.md:245`; AD streaming `:332` (cumulative usage) holds |
| AE8 | ADAPTER | holds | AD streaming `:335-337` (ping), `:350` (unknown event types), errors `:43` (error after 200) |
| AE9 | ADAPTER | drifted (content) | AS `cost-optimization.md:144` → `:145`: still "a backstop, not a tuning knob"; the upper bound is now the model's maximum output and a per-model value on the Effort page overrides 64,000. AS `SKILL.md:579` → `:592` |
| AE10 | ADAPTER | drifted (lines) | PA `models/fallback.py:90-145` → `:78-133`, still a decorator over `Model`; ADK `models/_fallback_model.py:15` holds |
| AE11 | ADAPTER | drifted (lines) | OA `chatcmpl_converter.py:123` holds, `:534` → `:559`; `chatcmpl_stream_handler.py:392-449` holds |
| AE12 | LOOP | drifted (lines) | OA `run_internal/run_steps.py:162-188` → `:164-190`; 12F unchanged |
| AE13 | LOOP | drifted (content) | OA `docs/human_in_the_loop.md:50-55` → `:51-56`, sticky decisions now scoped to the reused `RunContextWrapper`; PA `_deferred.py:28-170` → `:30-172`; ADK `_confirmation.py:73-101` holds |
| AE14 | LOOP | drifted (content) | ADK `_confirmation.py:80-85` holds; ADK resume guard `core/_resume.py:~405` → `:445-450` ("only replay a trailing function call the CURRENT AGENT authored"); PA `docs/message-history.md:516-528` → `:~790-802`, now a section: "Possession of the endpoint is the authorization boundary", re-validate high-stakes effects server-side; PA `deferred-tools.md:108` → `:110`; OA `guardrails.md:77` → `:79` |
| AE15 | LOOP | drifted (content) | LG `checkpoint/base/__init__.py:301-308` → `:324-331`, `pregel/_loop.py:784-823` → `:852-891`; ADK `core/_resume.py:42-75` → `:46-79`, replay now matches a call by id and name, per branch; ADK `apps/_configs.py:29-45` → `:25-41`, `ResumabilityConfig` no longer `@experimental`, still "at-least-once" (`:35`) |
| AE16 | LOOP | drifted (lines) | ADK `tools/_error_handler.py:79-97` → `:82-100`; LG `prebuilt/tool_node.py:108` → `:116`, `:383-392` → `:391-400`; MCP `server/tools.mdx:765-785` holds |
| AE17 | LOOP | drifted (content) | OA `tool.py:1975-1980` → `:1997-2002`; default text is now "An error occurred while running the tool." ("Please try again" dropped); still hides the exception |
| AE18 | LOOP | drifted (lines) | 12F unchanged; PA `exceptions.py:59-112` → `:79-132` |
| AE19 | LOOP | drifted (lines) | ADK `agents/invocation_context.py:57-87` → `:68-98`; PA `usage.py:482` → `:559`, `:545-549` → `:633-637` |
| AE20 | LOOP | drifted (lines) | ADK `tools/_batch_executor.py:60` → `:61`; MCP `client/sampling.mdx:380,438` hold; AD handle-tool-calls `:80` holds |
| AE21 | CONTEXT | holds | OA `run_config.py:68-73`; PA `_history_processor.py:11-21`; 12F factor-03 `:116-140` |
| AE22 | CONTEXT | drifted (content) | PA `docs/message-history.md:251-262` → `:380-396`, the repair section grew (tool, capability and settings deltas; orphan results removed whatever their outcome); `:892` → `:1283`, `:955` → `:1369` |
| AE23 | CONTEXT | holds | AS `prompt-caching.md:7-27`, `:95-114` |
| AE24 | CONTEXT | drifted (lines) | AS `prompt-caching.md:196` holds; ADK `anthropic_llm.py:877-888` → `:1205-1216`, `llm_request.py:124-132` → `:128-136` |
| AE25 | CONTEXT | drifted (content) | ADK `apps/_configs.py:51-80` → `:45-74`, `EventsCompactionConfig` no longer `@experimental`, fields unchanged; `events/event_actions.py:58-74` → `:90-106`; AS `token-counting.md:3-10` holds |
| AE26 | CONTEXT | drifted (lines) | AS `SKILL.md:576` → `:589`. The AE-blog quote is now verified: writing-tools "pagination, range selection, filtering, and/or truncation with sensible default parameter values" |
| AE27 | CONTEXT | drifted (lines) | LG `types.py:530-538` → `:531-539` |
| AE28 | GUARD | drifted (content) | ADK `plugins/plugin_manager.py:277-320` → `:315-350`, the loop now runs inside a callback scope; a throwing plugin still raises `RuntimeError` (`:343-350`); OA `human_in_the_loop.md:15` holds |
| AE29 | GUARD | holds | AS `tool-use-concepts.md:499-509`; AD mitigate-jailbreaks `:77` (tool results only), `:95` (JSON-encode) |
| AE30 | GUARD | drifted (lines) | OA `docs/guardrails.md:52-56` → `:54-58` |
| AE31 | GUARD | holds | MCP `server/tools.mdx:305-306`; OG and OWASP not re-read (hosts blocked, §1) |
| AE32 | GUARD | drifted (lines) | PA `docs/deferred-tools.md:108` → `:110` |
| AE33 | GUARD | drifted (content) | ADK `tools/_caller.py:497-625` → `:522-631`; the confirmation gate moved into `tools/_confirmation_utils.apply_confirmation_gate` (`_caller.py:581`), order unchanged: before-tool → gate → run → after-tool; MCP `server/tools.mdx:787-803` holds |
| AE34 | GUARD | holds | ADK `plugins/base_plugin.py:55-71`; OA `tool_guardrails.py:60-117` |
| AE35 | GUARD | holds | AD mitigate-jailbreaks `:18`, `:118`, `:150` (small-model screen, structured verdict) |
| AE36 | GUARD | holds | MCP `server/tools.mdx:324-331`, `:795`; spec revision 2026-07-28 is still the newest |
| AE37 | OBS | drifted (content) | OTG split the inference span out of `gen-ai-spans.md` into `client-inference.md`: span `gen_ai.client.inference`, name `{gen_ai.operation.name} {gen_ai.request.model}` (`:65`), kind CLIENT (MAY be INTERNAL in-process), cache read and write usage attributes Recommended; ADK `telemetry/tracing.py:652-715` → `:767-830` |
| AE38 | OBS | drifted (content) | OTG tool span now in `execute-tool.md` (name `execute_tool {gen_ai.tool.name}`, `:58`); agent span in `gen-ai-agent-spans.md`; ADK `_error_handler.py:37-57` → `:40-60` |
| AE39 | OBS | holds | OTG `gen-ai-spans.md:477` ("SHOULD NOT capture them by default"); OA `docs/tracing.md:143-151`; ADK `_stable_semconv.py:45-48` |
| AE40 | OBS | drifted (content) | OTG `gen-ai-token-metrics.md`: `gen_ai.client.inference.usage.*` counters stay primary and gain `cache_read`, `cache_write` and `reasoning` counters, plus `operation.*` histograms; status still Development |
| AE41 | OBS | holds | AS `eval-audit.md:113,135`; OA `docs/usage.md:11-55`; AD errors `:83` (request-id) |
| AE42 | OBS | drifted (lines) | PA `models/instrumented.py:333` → `:466` |
| AE43 | EVAL | drifted (content) | AS `build-eval.md:228` holds; ADK `evaluation/eval_case.py:97-186` gained `model_duration` and `tool_duration` (`:129-146`), case shape unchanged; `agent_evaluator.py:299` → `:319`; PA `reporting/__init__.py:394-428` → `:416-450` |
| AE44 | EVAL | holds | AS `eval-audit.md:95-107`; ADK `eval_metrics.py:47-53` |
| AE45 | EVAL | drifted (content) | AS `eval-audit.md:147-179` holds; `build-eval.md:78-83` reworded (judge returns "a score with a short explanation"); PA `evaluators/common.py:225-240` → `:223-238` |
| AE46 | EVAL | holds | AS `eval-audit.md:173-179`; WSH `details.md:247-320`; ADK `eval_metrics.py:127-138` |
| AE47 | EVAL | drifted (lines) | ADK `agent_evaluator.py:73` → `:74`; AS `eval-audit.md:119,185` hold |
| AE48 | EVAL | drifted (lines) | ADK `trajectory_evaluator.py:45-60` holds; PA `evaluators/common.py:367-377` → `:365-375`; AS `eval-audit.md:147-149` holds |
| AE49 | EVAL | holds | AD mitigate-jailbreaks `:155` (red-team with injected documents and tool outputs) |
| AE50 | COST | drifted (lines) | PA `concurrency.py:35-47` → `:34-46` |
| AE51 | COST | drifted (lines) | PA `usage.py:471-549` → `:548-690` (`check_before_request` `:633`, `check_tokens` `:681`); ADK `invocation_context.py:57-87` → `:68-98` |
| AE52 | COST | drifted (lines) | AS `cost-hillclimb.md:328-341` → `:329-342`; CB `cost_optimization.ipynb [cell 12]` holds |
| AE53 | COST | holds | AS `prompt-audit.md:181`; 12F appendix-13 |

Counts: **17 hold · 21 drifted (lines) · 15 drifted (content) · 0 gone.**

## 3. Dropped: a rule already approved covers it

| id | covered by |
|---|---|
| AE4 | CC8 (retry only transient failures, bounded, jittered) + CC16 (retry a 4xx only with `Retry-After`, wait at least that long). A spend-cap 429 carries no `Retry-After`, so CC16 already forbids retrying it |
| AE11 | SEAM1 (a decision is a function with no I/O; I/O stays in a thin method). LT5 already tests the adapter at the HTTP transport |
| AE27 | LS5 (key a response cache on tenant, system prompt and inputs; never cache an error), approved in G34 as an imperative rule |
| AE32 | SE10 (treat model output and tool arguments as untrusted; enforce permissions in code). Its remaining part, re-check after approval, is in AE14 |
| AE47 | LT18 (gate an eval on versioned thresholds over repeated runs). The noise-floor wording is the only extra, and LT18's repeated runs carry it |
| AE50 | SE8 (pass every LLM provider call through a per-caller rate limit and quota first) + CC4 (a bounded pool has a bounded queue and a stated rejection) |

Partial overlaps that stay, narrowed: AE19 (LT8 states the cap; AE19 adds "every path"), AE24 (its IT half is LS4
and LS16), AE39 (LG4 and TR3 cover secrets and bodies), AE45 (LT17 holds the judge's verdict form). The G34 testing
rules (LT1–LT18, LS1–LS20) test what most of these candidates build; the overlap column in §4 names each pair.

## 4. Surviving candidates by area

Each rule is written as it would ship, with its *because*, at most 35 words, provider-neutral: no vendor, model or
product name. **Sources** counts independent sources: pages from one company count once (AS, AD, CB and AE-blog are
one; OA and OG are one), and 12F is cite-only. A one-source rule is marked SRC2: it needs the operator's preference.

### ADAPTER (9)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE1 | Map each provider's stop reason onto one closed set (end, truncated, tool call, refused, context exceeded, paused, error) and switch on it exhaustively, because an unmapped refusal or truncation reads as success. | AD stop reasons; PA `models/anthropic/_response.py:26-35` | 2 | TY2 gives the switch form; this names the set. `paused` added (AD `pause_turn`) | yes |
| AE2 | Never run tool calls from a reply that stopped truncated or refused; end the turn with that typed outcome, because truncated arguments often parse as a valid partial object. | AS `tool-use-concepts.md:72`; PA `_agent_graph.py:839-844` | 2 | — | yes |
| AE3 | Have each adapter return one normalised error (status, retry-after, request id, timeout or network, response started), and let the retry policy above it decide, because retries inside adapters multiply attempts. | OA `retry.py:50-131`, `models/interface.py:58` | 1 | CC12 (retry at one layer) is the second source for the "policy above" half | yes (SRC2 for the error shape) |
| AE5 | Never retry a model call after its first streamed chunk reached a consumer; end it as a typed failure, because a retry replays text the user already saw. | OA `retry.py:93-131`; AD streaming §Error recovery | 2 | — | yes |
| AE6 | Parse a tool call's complete arguments with a JSON library and validate them against the schema; send a malformed call back to the model as an error, because empty-argument fallbacks run the tool wrongly. | AS `tool-use-concepts.md:69-87`; ADK `lite_llm.py:3703-3772` | 2 | SE10 covers the check before a sink; this covers the feedback | yes |
| AE7 | Fold each provider's usage into one record (input including cache, cache read, cache write, output, reasoning) from the final cumulative value, because providers split and repeat these counts differently. | ADK `anthropic_llm.py:977-1008`; OTG `client-inference.md:245`; AD streaming `:332` | 3 | LS16 live-tests the numbers | yes |
| AE8 | Treat an error event inside a stream as that request's failure even after a 200, and skip keep-alive and unknown event types, because providers fail mid-stream and add event types. | AD streaming `:335-350`, errors `:43` | 1 | — | yes (SRC2) |
| AE9 | Set every model call's output-token cap from agent or model configuration, sized as a backstop, never as an adapter default, because a hidden low cap truncates answers and wastes retries. | AS `cost-optimization.md:145`, `SKILL.md:592` | 1 | LS13 live-tests the cap's effect | yes (SRC2) |
| AE10 | Fall back to another model through a decorator over the model port with an explicit model mapping, and price usage on the model that served it, because the primary's name is wrong elsewhere. | PA `models/fallback.py:78-133`; ADK `models/_fallback_model.py:15` | 2 | LS9 tests it; the mapping itself is a project choice (N8) | yes |

### LOOP (9)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE12 | Classify each model reply into a closed step result (final, run again, paused, stopped) and switch on it, returning a pause as a value, because status-string branches miss new cases. | OA `run_steps.py:164-190`; PA `_agent_graph.py`; 12F factor-01 (cite only) | 3 | TY2 (switch form) | yes |
| AE13 | End a run that needs approval with a persisted pending request keyed by tool-call id, and resume through the same loop with the same checks, because a second resume path skips budget and guards. | OA `human_in_the_loop.md:51-56`; PA `_deferred.py:30-172`; ADK `_confirmation.py:73-101` | 3 | LS8 tests it | yes |
| AE14 | On resume, run only a call that matches the stored call this agent made, and re-check authorization and tool guards first, because a client can submit a forged call or approval. | ADK `_confirmation.py:80-85`, `core/_resume.py:445-450`; PA `message-history.md:~790-802`, `deferred-tools.md:110`; OA `guardrails.md:79` | 3 | absorbs AE32's re-check | yes |
| AE15 | Persist each finished tool result keyed by run, step and call id before the loop moves on, and on resume run only calls without a stored result, because resume otherwise repeats side effects. | LG `checkpoint/base/__init__.py:324-331`, `pregel/_loop.py:852-891`; ADK `core/_resume.py:46-79` | 2 | gives at-least-once; exactly-once is gap N3 (CC9, CC15) | yes |
| AE16 | Return model-correctable faults (unknown tool, invalid arguments, denied approval) as error tool results naming the valid form, and end the run only on platform faults, because the model can fix them. | ADK `_error_handler.py:82-100`; LG `tool_node.py:116,391-400`; MCP `server/tools.mdx:765-785` | 3 | LT7 tests it | yes |
| AE17 | Show the model a generic, actionable tool error, never a raw exception message or stack trace, because that text enters context and leaks internals into the model's output. | OA `tool.py:1997-2002`; AD handle-tool-calls §is_error | 2 | ER10 is the HTTP twin | yes |
| AE18 | Cap consecutive failures per tool and repeated identical calls, and end or escalate the run at the cap, because a model can retry one broken call until the step budget runs out. | 12F factor-09 `:31,62` (cite only); OG p31; PA `exceptions.py:79-132` | 3 | — | yes |
| AE19 | Check the run's model-call ceiling before every model call on every path, resume included, because a ceiling checked only in the main loop leaves the other paths unbounded. | ADK `invocation_context.py:68-98`; PA `usage.py:559,633-637` | 2 | LT8 states the cap and its test; this adds "every path" | yes |
| AE20 | Answer every tool call of one reply in the next message, results first, each matched by its call id, because providers reject a history with split, reordered or missing results. | AD handle-tool-calls `:80`; ADK `_batch_executor.py:61`; MCP `client/sampling.mdx:380,438` | 3 | — | yes |

### CONTEXT (6)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE21 | Build every model request (chat, resume, summariser, judge) in one pure function from the run record, because a second assembly path drifts and drops history, guards or cache order. | OA `run_config.py:68-73`; PA `_history_processor.py:11-21`; 12F factor-03 (cite only) | 3 | — | yes |
| AE22 | Never split a tool call from its result when windowing or compacting, and run one deterministic repair step before each request, because providers reject unpaired calls and results. | PA `message-history.md:380-396,1283,1369`; AD handle-tool-calls `:80` | 2 | LS1 tests it | yes |
| AE23 | Render each request in stability order (sorted tools, frozen system prompt, append-only history, per-turn content last) with no timestamps or ids early, because an early change invalidates the prompt cache. | AS `prompt-caching.md:7-27,95-114` | 1 | LS3 tests it, from PA's own test | yes (SRC2) |
| AE24 | Place the provider's cache breakpoints at the end of the stable prefix, in the adapter, because a breakpoint anywhere else caches nothing or misses on every turn. | AS `prompt-caching.md:196`; ADK `anthropic_llm.py:1205-1216`, `llm_request.py:128-136` | 2 | the "IT asserts cache reads" half dropped: LS4 and LS16 hold it | yes |
| AE25 | Trigger windowing and compaction on token counts from the provider or the last usage, appending one summary per threshold crossing and never rewriting stored turns, because rewrites re-summarise every turn. | ADK `apps/_configs.py:45-74`, `event_actions.py:90-106`; AS `token-counting.md:3-10` | 2 | LS2 tests it | yes |
| AE26 | Bound each tool result in context; a cut result says so and how to fetch more, and the full result stays in the run record, because oversized results crowd out the task. | AS `SKILL.md:589`, AE-blog writing-tools; OWASP LLM10 #1 | 2 | — | yes |

### GUARD (8)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE28 | Make a guard that errors, times out or is unconfigured block the action; configuration may tune a guard but never turn it off, because a guard that fails open protects nothing under load. | ADK `plugin_manager.py:343-350`; OA `human_in_the_loop.md:15` | 2 | — | yes |
| AE29 | Give third-party content (tool, retrieval, MCP, web) to the model only as tool results, JSON-encoded and labelled with its source, never in system or user text, because the model then treats it as data. | AD mitigate-jailbreaks `:77,95`; OWASP LLM01 #6 | 2 | a text control: never the only control for a harmful outcome (survey S1) | yes |
| AE30 | Check model output before it is stored, cached or sent to a sink, and store a placeholder for a rejected output everywhere, because a rejected answer otherwise returns through history or cache. | OA `guardrails.md:54-58`; OWASP LLM05 | 2 | streaming placement is gap N7 | yes |
| AE31 | Give every tool a risk class in your own configuration and derive approval from it, never from the model or the tool's own annotations, because those annotations come from an untrusted server. | OG p26; MCP `server/tools.mdx:305-306`; OWASP LLM06 | 3 | — | yes |
| AE33 | Run every tool call through one fixed pipeline: schema check, global guards, agent guards, approval gate, execute, output guards, because a check placed per call site is skipped on some path. | ADK `_caller.py:522-631`; MCP `server/tools.mdx:787-803` | 2 | — | yes |
| AE34 | Have each guard return Continue or ShortCircuit(result); run global guards before agent guards, stop at the first short-circuit and record which guard fired, because log-only verdicts cannot be audited. | ADK `base_plugin.py:55-71`; OA `tool_guardrails.py:60-117`; LG `tool_node.py` | 3 | — | yes |
| AE35 | Screen inputs and tool outputs with a classifier that returns a structured verdict, treating a pattern match as one signal only, because regex lists miss paraphrases and block innocent text. | AD mitigate-jailbreaks `:18,118,150` | 1 | the 2026-11-07 survey: every text guardrail with a published adaptive-attack number was bypassed above 50% | no (replace with the survey's capability rules S1–S3) |
| AE36 | Expose each MCP tool under a server-prefixed name and check its result's schema and size before it enters context, because server names are not unique and results are untrusted. | MCP `server/tools.mdx:324-331,795` | 1 | — | yes (the protocol's own spec) |

### OBS (6)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE37 | Emit one client span per model call, named and attributed per the GenAI semantic conventions (provider, request and response model, finish reasons, usage, error type), because tools and alerts read those names. | OTG `client-inference.md:65` ff.; ADK `tracing.py:767-830` | 2 | TR2 (instrument through the facade) | yes |
| AE38 | Emit a tool span per tool call and an agent span per run, linked by call id, and mark a tool span errored when the tool returns an error, because returned errors otherwise look successful. | OTG `execute-tool.md:58`, `gen-ai-agent-spans.md`; ADK `_error_handler.py:40-60` | 2 | — | yes |
| AE39 | Keep prompts, completions, system instructions and tool arguments out of spans and logs unless one deployment setting turns capture on, because they hold user data and are large. | OTG `gen-ai-spans.md:477`; OA `tracing.md:143-151`; ADK `_stable_semconv.py:45-48` | 3 | LG4 and TR3 cover secrets and bodies; this adds model content and the one switch | yes |
| AE40 | Keep GenAI attribute and metric names in one constants file pinned to a dated semantic-conventions version, because the GenAI conventions are still in development and rename fields. | OTG `gen-ai-token-metrics.md` | 1 | — | yes (SRC2) |
| AE41 | Write a call record for every model call (failed, retried, resume, summariser, judge) with request id, served model, retry count and final-attempt latency, because success-only records hide outages and cost. | AD errors `:83`, AS `eval-audit.md:113,135`; OA `usage.md:11-55` | 2 | — | yes |
| AE42 | Instrument the model port once, as a decorator, so every adapter emits the same spans and metrics, because per-adapter instrumentation drifts. | PA `instrumented.py:466` | 1 | TR2 | fog (structural, one source) |

### EVAL (6)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE43 | Run each agent capability's versioned golden set through the real entry point and fail on a drop beyond the threshold against the stored baseline, because a harness that bypasses the entry point tests something else. | AS `build-eval.md:228`; ADK `eval_case.py:97-186`, `agent_evaluator.py:319`; PA `reporting/__init__.py:416-450` | 3 | LT18 holds the thresholds over repeated runs | yes |
| AE44 | Record infrastructure failures, timeouts and truncations as their own eval status, never as a failed case, because they measure the harness, not the agent. | AS `eval-audit.md:95-107`; ADK `eval_metrics.py:47-53` | 2 | — | yes |
| AE45 | Grade with code first and use an LLM judge only for properties code cannot check, passing the candidate output to it as data, because a judge is costlier, noisier and injectable. | AS `build-eval.md:78-83`, `eval-audit.md:147-179`; PA `evaluators/common.py:223-238` | 2 | narrowed: LT17 holds atomic verdicts and never the generating model | yes |
| AE46 | Calibrate a judge against human labels on a sample before it gates, and store the judge's model and prompt version with every score, because an uncalibrated judge drifts unseen. | AS `eval-audit.md:173-179`; WSH `details.md:247-320`; ADK `eval_metrics.py:127-138` | 3 | — | yes |
| AE48 | Assert required and forbidden tool calls on the recorded trajectory with a declared match mode, and judge task success on the end state, because the path proves safety and the end state proves the task. | ADK `trajectory_evaluator.py:45-60`; PA `evaluators/common.py:365-375`; AS `eval-audit.md:147-149` | 3 | — | yes |
| AE49 | Include injection cases in the golden set, with instructions inside tool output and retrieved text, passing only when no case triggers an unapproved tool call, because tool results are where injection enters. | AD mitigate-jailbreaks `:155`; OWASP LLM01 #7 | 2 | LS10 already tests injection through a whole run; the survey says a static set measures the model's training, not the guard | fog (adaptive red-teaming, not a static set) |

### COST (3)

| id | proposed rule | sources at head | n | overlap with approved rules | rec |
|---|---|---|---|---|---|
| AE51 | Check run and workspace budgets before each model call and settle them from actual usage after each response, ending the turn with a typed reason, because per-turn estimates let concurrent runs overspend. | PA `usage.py:548-690`; ADK `invocation_context.py:68-98`; OWASP LLM10 | 3 | LS6 tests the crossing response; concurrency is gap N6 | yes |
| AE52 | Report cost per completed task beside pass rate, and adopt a cost change only when quality, cost and mechanism gates registered beforehand all pass, because per-token savings can lose solved tasks. | CB `cost_optimization.ipynb [cell 12]`; AS `cost-hillclimb.md:329-342` | 1 | needs AE43 first | fog (one company) |
| AE53 | Before adding a model call, check whether its inputs fully determine the output, and if they do write plain code, because code is cheaper, faster and testable. | AS `prompt-audit.md:181`; 12F appendix-13 (cite only) | 2 | not checkable in a diff | no as a rule; yes as an agent principle |

Changes against research/63's wording: AE1 adds `paused`; AE3 narrows to the error shape; AE24 drops its IT half;
AE40 drops the deprecated-name clause (the pinned version carries it); AE45 narrows to "code first, candidate as
data"; every rule names no provider. The old `hold`s on AE10, AE15, AE20 and AE33 were agent-platform reasons (fallback mapping, journal
store, "verify first", structure); with generic-only rules they become `yes`.

## 5. The 9 gaps no source covers

| # | gap | recommendation | why |
|---|---|---|---|
| N1 | Per-provider raw-HTTP mapping tables (stop reasons, usage, cache tokens) | leave in fog | provider-specific by nature; AE1 and AE7 give the neutral shape, and each project's own tables go with its adapters (#135) |
| N2 | Circuit breaker vs retry vs rate limit together | write ourselves (one rule) | CC8, CC11, CC12, CC16 and SE8 now cover most of it; what is left is "count a 429 as back-pressure, not as a breaker failure" |
| N3 | Exactly-once tool side effects across resume | write ourselves (one rule) | AE15 gives at-least-once; CC9, CC15 and CC19 give idempotency keys at the remote end. Left: derive a tool call's key from run id and call id and pass it to the side-effecting tool |
| N4 | Eval sandbox: evals never fire real side effects | write ourselves (SRC2) | one source now: AS `build-eval.md:165-169` (a test-mode wrapper that mocks only DB writes, outbound mail and external side effects) and `cost-optimization.md:164` ("Side-effect gate") |
| N5 | Response-cache correctness (key, sharing, invalidation) | leave in fog | LS5 covers the key and errors; invalidation on a prompt or tool change has no source |
| N6 | Workspace budget under concurrency | write ourselves (one rule) | PA's spend harness (`docs/harness/spend.md:87,197`) states the overshoot ("concurrent runs can each pass the check before any of them records anything") and keeps counters in a shared store; nobody publishes reserve-then-settle |
| N7 | Output guard on a stream | leave in fog | no source; the 2026-11-07 survey points at capability controls (S6: allowlisted output channels) instead |
| N8 | Fallback model mapping across providers | leave in fog | AE10 states the decorator and an explicit mapping; the mapping itself is a project choice (#135) |
| N9 | Multi-tenant governance (approval policy per workspace, verdict audit, fail-closed defaults) | leave in fog | product policy, project-side (#135); AE28 and AE34 cover the generic parts, survey S7 covers per-user memory |

Write ourselves: N2, N3, N4, N6, each one rule recorded like LS10 (an ours-rule). Leave in fog: N1, N5, N7, N8, N9.

## 6. New GUARD input (not re-checked here)

The operator's prompt-injection survey (map #130 comment, 2026-11-07) proposes eight GUARD rules. They are not AE
candidates and their sources (papers, incident write-ups) were not re-read in this ticket. They change two
recommendations above: AE35 becomes `no` (a text guardrail) and AE49 becomes `fog` (a static set measures the
model). Recommendation: re-check S1–S8 as their own group before G33 decides GUARD, and decide GUARD with them.

| id | survey candidate (abridged) |
|---|---|
| S1 | Sort every control as text or capability; each harmful outcome needs at least one capability control that makes it impossible |
| S2 | At most two of untrusted input, sensitive data or credentials, and state change or outbound communication in one session (Rule of Two) |
| S3 | Check tool-call arguments (recipient, amount, path, branch), not only tool names |
| S4 | A second-model judge sees the task and the proposed action, never the untrusted data, on top of a deterministic rule |
| S5 | For a high-stakes tool, fix the plan before reading untrusted data; the data fills only the body |
| S6 | Allowlist every output channel or remove it; secret scanning on output |
| S7 | Memory and multi-user agents: per-user scope with an owner check on each read, writes only from verified outcomes, a trust label per record |
| S8 | Treat responses through an LLM router or intermediary as untrusted, or do not route through one |

## 7. Where they live

**Recommendation: a new `agent/` domain** (its own `SKILL.md` router, ADR-0002), with one reference per area that
survives: `adapter`, `loop`, `context`, `guard`, `genai-obs`, `evals`, `cost`. **Reason:** the rules apply only to
code that calls a model, so their own router loads them only for that work, and keeps them out of the `code/` router
that every task reads and that agent-factory#32 is still building.

The alternative, `code/references/agent-*.md`, would put 47 rules behind a router most tasks load. Either way the
testing side stays where G34 put it (`testing/references/llm-tests.md`, `llm-live-tests.md`), and each `agent/` rule
names the testing rule that checks it.
