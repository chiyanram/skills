# R32 · Who publishes high-quality best practices for Spring core, Spring Security, Spring AI and agent engineering

Ticket: `chiyanram/skills#73` (part of map #9 "One rulebook", feeds #33 G9b code + observability). Read 2026-10-03.
**Source survey only — no rules.** Rules come from the follow-up tickets in §6, which read the chosen sources.

Abbrev: **REF** = `/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs` ·
**AP** = agent-platform `origin/master` @ `27e3583e` (2026-10-03), read with `git show`, never checked out ·
**SBS** = `rrezartprebreza/spring-boot-skills` (local clone `~/workspace/claude/references/skill-packs/spring-boot-skills`, REF-033) ·
**pl NNN** = `REF/jabrena-plinth/skills/NNN-*/references/*.md` @ `5e338bb`.

Rating scale (per column): ●●● strong · ●● adequate · ● weak · ○ none/mismatch.
"Rules" = states imperative, checkable rules (or Good/Bad + gotcha lists); "Teach" = explains, no checkable rules.

## 0. What we actually run (AP)

| Thing | Version | Evidence |
|---|---|---|
| Spring Boot | **4.1.1** | `gradle/libs.versions.toml` `springBoot = "4.1.1"` |
| Spring Framework | **7.0.9** | `spring-boot-dependencies-4.1.1.pom` `<spring-framework.version>` (gradle cache) |
| Spring Security | **7.1.1** | same POM `<spring-security.version>` |
| Micrometer / Jackson | 1.17.1 / 3.1.5 | same POM |
| Spring AI | **2.0.1** (BOM) | `libs.versions.toml` `springAi = "2.0.1"` |
| Spring AI starters | anthropic, openai, vector-store-qdrant — **`aruvii-worker` only** | `aruvii-worker/build.gradle.kts:35-37`; ArchUnit `spring_ai_only_used_by_worker`, `aruvii-architecture-tests/.../ArchitectureRulesTest.java:104` |
| Spring AI **code** | **none.** Zero `import org.springframework.ai.*` in any `*.java` on master | `git grep 'import org.springframework.ai' origin/master` → empty |
| LLM calls | **hand-rolled HTTP** (`java.net.http.HttpClient` + Jackson 3) per provider: `AnthropicChatAdapter`, `OpenAiChatAdapter`, `BedrockChatAdapter`, `OllamaChatAdapter` behind `StreamingLlmAdapter` / `LlmAdapterRegistryImpl` | `aruvii-worker/src/main/java/ai/aruvii/worker/llm/`; Anthropic adapter hard-codes `https://api.anthropic.com/v1/messages`, `anthropic-version: 2023-06-01` |
| Anthropic / OpenAI SDK | **not used** (no `com.anthropic`, `com.openai`, langchain4j) | `git grep` → empty |
| Spring AI config | placeholder keys only | `aruvii-worker/src/main/resources/application.yml:53-57` (`spring.ai.openai/anthropic.api-key: ${…:placeholder}`) |
| Spring idioms in use (counts, `*.java`+`*.groovy`) | `@PreAuthorize` 255 · `@Configuration` 28 · `@ConditionalOn*` 37 · `@ConfigurationProperties` 12 · `SecurityFilterChain` 4 · `@EnableMethodSecurity` 2 · `MeterRegistry` 43 · `ObservationRegistry` 0 | `git grep -c` on AP |

**So:** Spring AI is a dependency, not a practice. The worker's chat orchestration, tool loop, memory windowing
(`MemoryWindower`, `HistoryCompressor`), prompt caching (`PromptCacheService`), token budgets and eval judge
(`worker/eval/*`) are all our own code on raw provider HTTP APIs. This decides topic 3 (§3) and makes topic 4 (§4)
the one that actually governs our AI code.

## 1. Spring core (beans, `@Configuration`, `@ConfigurationProperties`, conditionals, profiles, lifecycle)

| # | Source | Version / commit | Auth. | Currency | Depth | Rules/Teach | Covers | Licence / vendor |
|---|---|---|---|---|---|---|---|---|
| 1 | **Spring Boot reference** — docs.spring.io/spring-boot/reference (Core Features: Externalized Config, Profiles, Developing Auto-configuration; Actuator: Observability) | 4.1.1 (stable selector: 4.1.1, 4.0.8, 3.5.x) | ●●● | ●●● exact | ●●● | Teach (normative "should/must" sprinkled) | everything in scope; canonical for `@ConfigurationProperties` binding/validation, `@Conditional*` semantics, profile groups | docs, cite not vendor |
| 2 | **Spring Framework reference** — docs.spring.io/spring-framework/reference (Core: IoC container, `@Bean`/`@Configuration`, lifecycle callbacks, `@Primary`/`@Qualifier`) | 7.0.x | ●●● | ●●● | ●●● | Teach | DI, bean scopes, `proxyBeanMethods`, lifecycle, JSpecify nullness (Framework 7) | docs |
| 3 | **pl 301 `frameworks-spring-boot-core`** (REF) | plinth 0.19.0 @ `5e338bb`, targets **Boot 4.0.x** | ●● (Java Champion author, 443★) | ●● (4.0 not 4.1) | ●●● 1410 lines, 15 topics, 30 Good/Bad blocks | **Rules** (Constraints + Good/Bad) | exactly our scope: ctor injection, `@ConfigurationProperties`+`@Validated`, conditionals/profiles, `@Primary`/`@Qualifier`, bean minimisation, graceful shutdown, virtual threads, `@TestConfiguration` | Apache-2.0; Maven-bound workflow (`./mvnw compile` mandatory) — strip for Gradle |
| 4 | **SBS `spring-boot-4/configuration-properties`, `null-safety`, `layered-architecture`** | @ `f0c06a0` (2026-09-21), 292★, 23 commits | ● single author | ●●● Boot 4 / Framework 7 explicit | ● 59 lines for config-props | **Rules** (Gotchas = anti-pattern list) + "Official sources" links | Boot-4-specific traps (relocated packages, JSpecify) | MIT; **is a Claude plugin marketplace** (`.claude-plugin/marketplace.json`) |
| 5 | Operator corpus `~/workspace/claude/analysis/skills-analysis/docs/extractions/spring-boot-4-configuration-null-safety-and-platform-architecture.md` | mined from SBS @ `c43b0b6` (8 commits behind) | derived | ●● | ●●● 142 directives | Rules (already extracted) | same as #4, pre-mined | derived — re-verify against #4 head |
| 6 | Jeffallan `spring-boot-engineer` (REF) | @ `882ef55`, 11.7k★ | ●● | ○ **Boot 3.x / Security 6**, uses `@MockBean` (removed in Boot 4) | ●● 2375 lines | Teach + checklists | web/data/security/testing/cloud | MIT; stale — reject |
| 7 | piomin/claude-ai-spring-boot | 1.3k★, last push 2026-04-29 | ●● (Piotr Minkowski) | ● Boot 3.x | ●● | Teach | layered app, JPA, logging | Apache-2.0 |
| 8 | sivaprasadreddy/sivalabs-agent-skills `spring-boot` | 187★, 2026-09-03, Boot 4.0 (jvm-skills "curated") | ●● | ●●● | ● scaffolding-oriented | mixed | project scaffolding, JSpecify, Modulith verifier | MIT |
| 9 | ultrapowers-dev `spring-boot-patterns` (installed) | plugin 1.2.0, 1★ | ● | ○ recommends `@MockBean` (removed in Boot 4) | ● 54 lines | thin rules | generic layering | MIT; reject |
| 10 | **spring-standards** (Anthropic Directory, community, alexanderCanon) | `alexanderCanon/spring-standards` @ `d648fc7` (2026-04-22), **0★, 1 commit** | ○ | ○ version-free | ● 1353 lines of checklists, no Spring API detail | Rules, but architectural ("hexagonal mandatory", "Lombok only where…") | architecture baseline, not bean wiring | MIT; **reject** (§5) |

**Primary: Spring Boot 4.1 + Framework 7.0 reference** (only exact-version authority). **Secondary (rule-shaped): pl 301**,
cross-checked against SBS gotchas for Boot-4 deltas. No skill repo states rules for Boot **4.1** specifically.

## 2. Spring Security (authn/authz, method security, filter chain, CSRF/CORS, testing)

| # | Source | Version / commit | Auth. | Currency | Depth | Rules/Teach | Covers | Licence |
|---|---|---|---|---|---|---|---|---|
| 1 | **Spring Security reference** — docs.spring.io/spring-security/reference (Servlet → Authorization → Authorize HTTP Requests, Method Security; Exploits → CSRF; Integrations → CORS; **Testing → Method Security, MockMvc Support**) | **7.1.1** (stable selector 7.1.1 / 7.0.7 / 6.5.x) | ●●● | ●●● **exact** | ●●● | Teach (with explicit "we recommend") | every sub-topic incl. testing; migration notes 6→7 | docs |
| 2 | spring-projects/spring-security-samples | 1.8k★, push 2026-09-25 | ●●● | ●●● | ●● | Teach (runnable code) | per-feature samples | no SPDX on repo; cite |
| 3 | **SBS `spring-security-jwt`, `oauth2-resource-server`, `testing-pyramid`** | @ `f0c06a0` | ● | ●●● names Security 7 removals (`and()`, `antMatchers`, `AntPathRequestMatcher`→`PathPatternRequestMatcher`, `DaoAuthenticationProvider` ctor) | ●● 156+160 lines | **Rules** (gotchas) | filter chain, JWT, resource server, `@WithMockUser`+`@MockitoBean` | MIT, plugin |
| 4 | **pl 304 `frameworks-spring-boot-security`** (REF; already summarised in `research/32-java-standards-sources.md` §1.11) | 0.19.0 @ `5e338bb` | ●● | ●● Security-7-compatible lambda DSL but never says "7" | ●● 294 lines, 8 examples, 16 Good/Bad | **Rules** | filter chain, `@EnableMethodSecurity`/`@PreAuthorize` with bean refs, CSRF/session for stateless, CORS, headers, entry point / access-denied | Apache-2.0; **no security testing** |
| 5 | Jeffallan `spring-boot-engineer/references/security.md` + `testing.md` | Security **6** | ●● | ○ | ●● | Teach | has security tests but Boot 3 APIs | MIT; stale |
| 6 | ultrapowers-dev `auth-security` | 76 lines | ● | n/a (framework-free) | ● | thin rules | JWT/session/CSRF generic | MIT |
| 7 | OWASP ASVS / Cheat Sheets (owasp.org) | current | ●●● | n/a | ●●● | Rules (verification reqs) | framework-neutral controls | CC BY-SA |

**Primary: Spring Security 7.1 reference** (exact version; only source that covers **method-security testing**, which matters
because we have 255 `@PreAuthorize`). **Secondary: pl 304** for rule shape, **SBS** for the Security 7 removal list.
Overlaps #53 (security, after-v1).

## 3. Spring AI (ChatClient, advisors, tool calling, structured output, memory, observability, evaluation)

| # | Source | Version / commit | Auth. | Currency | Depth | Rules/Teach | Covers | Licence |
|---|---|---|---|---|---|---|---|---|
| 1 | **Spring AI reference** — docs.spring.io/spring-ai/reference | **2.0.1** (stable selector 2.0.1 / 1.1.8 / 1.0.9; preview 2.1.0-M1) | ●●● | ●●● **exact** | ●●● | Teach | Chat Client API + Advisors + Recursive Advisors, Structured Output (schema validation, provider-native), Chat Memory, Tool Calling (ToolCallingAdvisor, Tool Search), MCP, RAG, **Model Evaluation**, **Observability**, Testcontainers | docs |
| 2 | spring.io blog — "Spring AI Agentic Patterns" series (e.g. 2026-01-13 agent skills, 2026-01-28 Anthropic skills) | 2026 | ●●● (Spring team) | ●●● | ●● | Teach | agentic patterns on Spring AI | — |
| 3 | **SBS `spring-ai-integration`, `ai-observability`, `mcp-server`** | @ `f0c06a0`; explicitly Spring AI **2.0** (bom 2.0.0) | ● | ●●● (2.0 renames, flattened `spring.ai.*.chat.*` props, memory conversation-id required, no default temperature) | ●● 203+203 lines | **Rules** (gotchas) | ChatClient bean config, prompt templates, structured output, RAG, streaming, observation metrics, logging advisor, cost attribution, audit log | MIT, plugin |
| 4 | Operator corpus `extractions/spring-ai-integration-and-observability-standards.md` | from SBS @ `72ed30a` (stale) | derived | ● | 22 directives | Rules | notes "the ONLY Spring AI evidence in the whole corpus" | re-verify |
| 5 | spring-ai-community/spring-ai-agent-utils | 648★, 2026-08-30 | ●● (community org) | ●●● | ●● | Library + docs | Claude-Code-style tools/skills on ChatClient | Apache-2.0 (library, not rules) |
| 6 | spring-ai-community/awesome-spring-ai | 857★, 2026-09-17 | ●● | ●●● | index | pointer list | samples, talks | Apache-2.0 |
| 7 | jvm-skills catalogue (REF @ `c6d477f`) | — | ●● curator | — | — | — | **scouted Spring AI and promoted nothing**; every Spring AI candidate rejected as project-doc/demo (`skill-scout/db/rejected.csv`: tzolov, markpollack, jettro, coditori…) | evidence of absence |

**Primary: Spring AI 2.0.1 reference.** Secondary: SBS gotchas. **But see §0: we call no Spring AI API.** Writing Spring AI
rules now would govern code that does not exist. Recommendation: before any Spring AI rule ticket, decide whether
(a) the worker migrates its hand-rolled adapters to ChatClient/advisors, or (b) the three starters are removed
(they currently auto-configure unused model beans from placeholder keys). Rules follow the decision.

## 4. AI / agent engineering standards (not Spring) → our use cases

Use cases: **WCO** worker chat orchestration (`ChatOrchestrator`, `TurnRunner`, `MemoryWindower`, `HistoryCompressor`) ·
**TE** tool execution (`ToolDescriptorBuilder`, tool loop, approvals) · **GR** guardrails (`aruvii-guardrails`) ·
**PA** prompt assembly (`aruvii-prompt-builder`, `PromptCacheService`) · **EV** eval (`worker/eval/*`, LLM judge).

| # | Source | Version / commit | Auth. | Currency | Depth | Rules/Teach | Use cases | Licence / vendor |
|---|---|---|---|---|---|---|---|---|
| 1 | **Anthropic `claude-api` skill** — `anthropics/skills/skills/claude-api` (`shared/agent-design.md`, `tool-use-concepts.md`, `prompt-caching.md`, `prompt-audit.md`, `token-counting.md`, `error-codes.md`, `shared/evals/{build-eval,eval-audit,eval-hillclimb}.md`, `java/claude-api/{tool-use,streaming,files-api}.md`) | last change `8a1541c` 2026-09-29; repo 179k★ | ●●● first-party | ●●● tracks current models/API | ●●● | **Rules** in places (prompt-audit deletion rule, caching placement, tool-surface design) + reference | WCO, TE, PA, EV — the most direct match to our raw-HTTP Anthropic adapter | **Apache-2.0** (`LICENSE.txt` in skill dir); already available as built-in `claude-api` skill — vendor as plugin, never copy |
| 2 | **Anthropic engineering essays** — "Building effective agents", "Effective context engineering for AI agents", "Writing effective tools for agents" (anthropic.com/engineering) | 2024–2025 | ●●● | ●● (patterns, model-agnostic) | ●● | Teach | WCO (workflow vs agent), PA/context budget, TE (tool naming, response shaping, tool evals) | cite only |
| 3 | **Anthropic docs** — platform docs (tool use, prompt caching, streaming, stop reasons) + code.claude.com (Agent SDK) | current | ●●● | ●●● | ●●● | Teach / API contract | TE (`tool_use`/`tool_result`, `pause_turn`), PA (cache breakpoints) | docs |
| 4 | **humanlayer/12-factor-agents** (REF @ `d20c728`) | last push **2025-09-21** (stale 1 yr), 26.5k★ | ●● | ●● principles age well | ●● 12 factors + appendix | **Rules** (12 named factors) | WCO (own control flow F8, stateless reducer F12, unify state F5, pause/resume F6), PA (own prompts F2, own context window F3), TE (tools = structured output F4, contact humans F7 ≈ our approvals), errors (compact errors F9) | content **CC BY-SA 4.0** (share-alike — cite, don't vendor text), code Apache-2.0 |
| 5 | **anthropics/claude-cookbooks** (`patterns/`, `tool_use/`, `tool_evaluation/`, `evals/`, `observability/`, `claude_agent_sdk/`) | 53k★, 2026-09-28 | ●●● | ●●● | ●●● | Teach (notebooks) | EV (tool eval, LLM judge), TE, observability | MIT |
| 6 | **OpenAI "A practical guide to building agents"** (cdn.openai.com PDF) + developers.openai.com agents track / openai-agents-python (29.8k★) guardrails docs | 2025; SDK 2026-10-02 | ●●● | ●● | ●● | Teach, with a **guardrail taxonomy** (relevance, safety, PII, moderation, tool risk rating, rules-based, output validation, human escalation) | **GR** (best single guardrail taxonomy), TE (tool risk tiers) | docs / MIT |
| 7 | OWASP GenAI — Top 10 for LLM Applications / Agentic threats (genai.owasp.org) | 2025 editions | ●●● | ●● | ●● | Rules-ish (risks + mitigations) | GR (prompt injection, excessive agency, insecure output handling), TE | CC BY-SA |
| 8 | openclaw `docs/agent-runtime-architecture.md`, `openclaw-agent-runtime.md` (REF @ `b94e5177`) | 2026-10-01 | ●● | ●●● | ●●● | Teach (a real runtime's design) | WCO reference design (queued sessions, steering FIFO) | TS project; read-only reference |
| 9 | ultrapowers-dev `agent-loop`, `tool-calling`, `orchestrator-workers` (installed) | 1★ | ● | ●● | ● ~100–130 lines, Python examples | thin rules; self-declared "inspired by" Anthropic docs | WCO/TE | MIT; derivative — prefer #1/#2 |
| 10 | Jeffallan `prompt-engineer`, `rag-architect` (REF) | @ `882ef55` | ●● | ●● | ●● | Teach | PA, EV rubric | MIT |
| 11 | addy `context-engineering`; humanlayer `advanced-context-engineering-for-coding-agents` (REF) | — | ●● | ●● | ●● | Teach | about **coding** agents (our fleet), not product agents — wrong target for this topic | — |

**Primary: Anthropic `claude-api` skill** (first-party, Apache-2.0, current, has Java pages, and covers exactly what our
`AnthropicChatAdapter`/tool loop/prompt cache/judge do). **Secondary: 12-factor-agents** as the provider-neutral principle
set (names our orchestration choices), **plus OpenAI's guide for guardrails** (the only one with a usable guardrail taxonomy).

## 5. Marketplace plugins asked about

| Plugin | Source repo | Verdict | Why |
|---|---|---|---|
| **spring-standards** (community, alexanderCanon) | `github.com/alexanderCanon/spring-standards` @ `d648fc7`, MIT, 0★, **1 commit** (2026-04-22) | **Do not adopt** | Version-free (never names Boot/Security version), no Spring API-level rules (no bean wiring, no `SecurityFilterChain`, no `@PreAuthorize`, no testing APIs), architecture checklists only ("hexagonal mandatory", "Lombok only where…", Docker/Vault lists). Single unmaintained commit. Its hexagonal/domain-purity rules duplicate what AP already enforces by ArchUnit. |
| **Engineering** (Anthropic) | `anthropics/knowledge-work-plugins/engineering` @ `8444efc`, Apache-2.0, 26k★ | Out of scope | 10 workflow skills (standup, code-review, incident-response, system-design…), 765 lines total; no Spring, Security-framework or agent-engineering content. Generic OWASP line in `code-review`. |
| **SBS** `spring-boot-4-skills` (not in the Directory; self-hosted marketplace) | `rrezartprebreza/spring-boot-skills` @ `f0c06a0`, MIT, 292★ | **Best Spring plugin found** — candidate to vendor as plugin (G1) as a *secondary*, not primary | Only skill pack that is explicitly Boot 4 / Security 7 / Spring AI 2.0 aware with gotcha-style rules and an `evaluations/cases.json`. Risks: single maintainer, short skills, local REF-033 clone is 2 commits behind origin. |
| Installed: `jdtls-lsp`, `semgrep` (`install-mfw` only), `redis-development` (has `redis-semantic-cache`, `redis-observability`) | claude-plugins-official | Tooling, not standards | `redis-semantic-cache` is the only tangential hit (our `SemanticCacheService`). |
| Installed: `claude-api` | built-in = `anthropics/skills` `claude-api` | **Adopt** (topic 4 primary) | see §4 #1 |

## 6. Gaps no source covers

1. **Provider-neutral adapter layer on raw HTTP in Java** — translating one `ChatRequest`/`ToolCall`/`StreamChunk` model across
   Anthropic, OpenAI, Bedrock, Ollama (stop-reason mapping, tool_use ↔ function-call, streaming tool deltas, retries/circuit
   breaker per provider). Spring AI solves it *as a framework*; nobody publishes rules for doing it yourself. **Biggest gap.**
2. **Guardrails inside a Java worker** — OpenAI/OWASP give taxonomies, but no source gives Java/Spring placement rules
   (pre-model vs post-model vs pre-tool hooks, fail-open/closed, how a guardrail verdict is recorded).
3. **LLM observability with Micrometer when not using Spring AI** — Spring AI's observation conventions (`gen_ai.*`) only
   come for free via ChatClient; AP has 43 `MeterRegistry` uses and 0 `ObservationRegistry`. No source covers hand-rolled
   GenAI semantic-convention metrics/traces in Spring.
4. **Eval practice in Java** — Spring AI "Model Evaluation" is thin; Anthropic evals pages and cookbooks are Python. Rules for a
   JVM LLM-judge (our `JudgeVerdictParser`, `JudgeConfidence`) must be translated.
5. **Spring Boot 4.1-specific rules** — every rule-shaped source targets 4.0.x; 4.1 deltas only in the reference/release notes.
6. **Method-security testing at scale** (255 `@PreAuthorize`) — only the Security reference covers it; no rule pack does.

## 7. Follow-up tickets (proposed — not opened)

| Proposed ticket | Reads (primary → secondary) | Output | Blocked by |
|---|---|---|---|
| **R-Spring-core rules** — beans, `@Configuration`, `@ConfigurationProperties`, conditionals, profiles, lifecycle on Boot 4.1 | Boot 4.1.1 + Framework 7.0 reference → pl 301 → SBS `configuration-properties`/`null-safety` gotchas; diff against AP's 28 `@Configuration` / 37 `@ConditionalOn*` / 12 `@ConfigurationProperties` | `code/spring-core` candidate rules for #33 | — |
| **R-Spring-Security rules** — filter chain, method security, CSRF/CORS, **security testing** | Security 7.1.1 reference (incl. Testing chapter) → pl 304 → SBS `spring-security-jwt`/`testing-pyramid` | `code/security` (Spring) candidates; merge with `research/32` G-I | coordinate with #53 (after-v1) |
| **D-Spring-AI decision** (not a rules ticket yet) — adopt ChatClient/advisors in `aruvii-worker`, or drop the three unused starters | §0 evidence; Spring AI 2.0.1 reference | ADR in agent-platform | operator decision |
| **R-Spring-AI rules** — only if the decision is "adopt" | Spring AI 2.0.1 reference → SBS `spring-ai-integration`/`ai-observability` | `code/spring-ai` candidates | D-Spring-AI |
| **R-Agent-engineering rules** — WCO, TE, GR, PA, EV mapped to worker classes | `claude-api` skill (shared + java) → Anthropic engineering essays → 12-factor-agents (cite, CC BY-SA) → OpenAI guide (guardrails) → OWASP GenAI | `code/agents` candidates + explicit list of gap rules (§6.1–6.4) we must author ourselves | — |

## 8. What was read

- AP @ `27e3583e`: `gradle/libs.versions.toml`, all module `build.gradle.kts` (Spring/AI deps), `aruvii-worker/src/main/java/ai/aruvii/worker/llm/AnthropicChatAdapter.java:1-60`, `ArchitectureRulesTest.java:65-112`, `aruvii-worker/src/main/resources/application.yml:53-57`, repo-wide `git grep` counts; `~/.gradle/.../spring-boot-dependencies-4.1.1.pom`.
- Online (2026-10-03): docs.spring.io/spring-boot/reference (4.1.1), /spring-security/reference (7.1.1), /spring-ai/reference (2.0.1) nav pages; anthropic.com/engineering essay index; OpenAI practical-guide PDF (search summary); `gh api` metadata (★, last push, SPDX) for every GitHub repo named above; `anthropics/skills/skills/claude-api` tree + headings of `agent-design.md`, `tool-use-concepts.md`, `prompt-audit.md`.
- Cloned to scratch: `alexanderCanon/spring-standards` (full), `anthropics/knowledge-work-plugins/engineering` (sparse, full).
- REF: pl 301/304 outlines + constraints; jvm-skills `skills/framework/*.yaml`, `skill-scout/candidates.md`, `db/rejected.csv`; Jeffallan `spring-boot-engineer`, `prompt-engineer`; 12-factor `content/` + README licence; openclaw `docs/` listing; addy skill list.
- Local: SBS `skills/spring-boot-4/*` (headings, gotchas, versions), ultrapowers-dev `spring-boot-patterns` (full), `auth-security`, `agent-loop`, `tool-calling` (attribution); operator extractions `spring-ai-integration-and-observability-standards.md`, `spring-boot-security-and-integration-standards.md`, `spring-boot-4-configuration-null-safety-and-platform-architecture.md` (headers).
- Not read in full: Spring reference chapters themselves (follow-up tickets do that), Anthropic essays' bodies, OpenAI PDF body, piomin/sivalabs skill bodies.
