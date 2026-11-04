# R19 · How agent SDKs balance unit vs integration tests

Ticket: `issues/34-research-agent-sdk-test-mix.md` (R19, informs G9a / S1 emphasis). Measured 2026-10-02 on shallow
clones (default branch HEAD) under `scratchpad/r19/`. Stars via `gh api repos/OWNER/REPO --jq .stargazers_count`.
File counts are **test files, not test cases**; tier taken from each repo's own layout.

## Table

| repo · stars | unit | integ / e2e | integ share | LLM fake | real infra | philosophy (≤15 words, path) |
|---|---|---|---|---|---|---|
| spring-ai · 9,506 | 501 `*Test(s).java` | 374 `*IT.java` | 43% | Mockito `ChatModel` mocks in unit (175 test files import Mockito); ITs call real providers, 181 ITs gated `@EnabledIfEnvironmentVariable` | 125 ITs use Testcontainers (vector stores, `OllamaContainer` in `BaseOllamaIT.java:82`); ITs only in failsafe profile `integration-tests` (`pom.xml:808`) | "If possible run integration tests related to the part you modify" — `CONTRIBUTING.md:59` |
| langchain4j · 13,192 | 808 | 647 `*IT.java` | 44% | `ChatModelMock` — "Always returns a static response and records all invocations" (`langchain4j-core/src/test/.../mock/ChatModelMock.java:32`); 346 ITs env-gated on API key | 77 ITs on Testcontainers; shared contract bases `AbstractChatModelIT`, `EmbeddingStoreIT` every provider must extend | "Write unit and/or integration tests for your code… no tests, no review!" — `CONTRIBUTING.md:11` |
| openai-agents-python · 29,800 | 376 `tests/` | 31 `integration_tests/` | 8% | **`ScriptedModel` / `ModelStep` shipped in the SDK** (`src/agents/testing/model.py`), used by 110 test files; autouse fixture fails any real-model call (`tests/conftest.py:130-141`) | `integration_tests/containers/` Redis + Dapr via Testcontainers; live provider matrix needs a service-account key; "never run as part of ordinary `make tests`" (`integration_tests/README.md`) | "Use real provider adapters … for behavior owned by an external model" — `docs/testing.md:5` |
| claude-agent-sdk-python · 8,199 | 36 `tests/` | 18 `e2e-tests/` | 33% | `MockTransport` replaces the CLI subprocess (`tests/test_tool_callbacks.py:22`); 17 files mock/patch | e2e hits the real Claude API; fails without `ANTHROPIC_API_KEY` (`e2e-tests/README.md`) | none beyond the e2e README |
| langgraph · 42,589 | 146 | 32 in `integration*/` dirs | 18% (≈51% counting below) | `FakeChatModel(GenericFakeChatModel)` scripted message list (`libs/langgraph/tests/fake_chat.py:14`) | **one tier, many backends**: `make test` starts compose Postgres + Redis and parametrizes every checkpointer/store test over memory·sqlite·postgres·redis (`libs/langgraph/tests/conftest.py:62,94`; `Makefile:61-65`); 58 more files run this way | none written (`AGENTS.md` only says `make test`) |
| crewAI · 59,276 | 362 | 12 `*_integration.py` | 3% | **VCR cassettes**: 598 YAMLs, 566 `@pytest.mark.vcr` tests; `record_mode=none` on CI (`conftest.py:444-458`) | none in default run | "Write unit tests for new functionality focusing on behaivor" [sic] — `AGENTS.md:10` |
| mastra · 28,489 | 3,882 | 507 (e2e/integration-named + 21 docker-backed pkgs) | 12% | `@internal/llm-recorder`: MSW record/replay "Works like test snapshots" (`packages/_llm-recorder/README.md:3`); 370 files use `MockLanguageModelV*` | `stores/*`, `pubsub/redis-streams`: `pretest` = `docker compose up` (e.g. `stores/pg/package.json:25`) | "run unit/integration before E2E" — `AGENTS.md:10` |
| OpenHands · 89,759 (repo is now the GUI client) | 763 Vitest | 26 Playwright specs | 3% | **scripted mock-LLM server** `tests/e2e/mock-llm/scripts/mock-llm-server.py`, separate `playwright.mock-llm.config.ts` vs `playwright.live.config.ts` | Docker E2E profile | "Mock an underlying service rather than the hook that consumes it." — `AGENTS.md:74` |
| n8n · 206,477 | 6,172 | 820 (314 `cli/test/integration`, 303 Playwright, rest `*.integration.test`) | 12% | Playwright proxy replays **recorded expectations** of real provider calls (`packages/quality/testing/playwright/expectations/`, 166 instance-ai, 52 chat-hub); 441 unit files use `nock` | cli ITs default sqlite, `test:postgres:tc` via Testcontainers (`packages/cli/package.json:38`) | "Use Vitest for unit tests. Use Playwright when a test needs … containers" — `AGENTS.md:312` |

Commands (abridged; `$D` = scratchpad/r19):
```
git -C $D/spring-ai ls-files | grep /src/test/ | grep -E 'IT\.(java|kt)$' | wc -l        # 374
git -C $D/spring-ai ls-files | grep /src/test/ | grep -E '(Test|Tests)\.(java|kt)$' | wc -l  # 501
git -C $D/spring-ai grep -l EnabledIfEnvironmentVariable -- '*IT.java' | wc -l          # 181
git -C $D/openai-agents-python ls-files | grep -E '(^|/)test_[^/]*\.py$' | awk -F/ '{print $1}' | sort | uniq -c
git -C $D/crewAI grep -c 'mark.vcr' -- '*.py' | awk -F: '{s+=$2} END{print s}'          # 566
git -C $D/mastra grep -l '"pretest.*docker compose' -- '*package.json'                  # 21 pkgs → 200 files
grep -E '/(integration|e2e)/|\.(integration|e2e)\.(test|spec)\.|^packages/quality/testing/playwright/' n8n_all.txt | sort -u | wc -l  # 820
```

**Aruvii (origin/master):**
```
git -C <worktree> ls-tree -r --name-only origin/master
  /src/test/(java|groovy)/…(Test|Tests|Spec)          313
  /src/integrationTest/…(IT|Spec|Test)                141   → 31% integ (JVM)
  aruvii-ui/src/**/*.spec.ts (UI unit)                 81
  smoke-NN-*.spec.ts (Playwright, deployed stack)      93
```
LLM fake: `aruvii-ui/playwright/fake-llm/` — scripted server on Ollama's port 11434 (#576 — scripted fake model
for smoke; extended by #608 — smoke-69/78 C01 made to fail when tools/memory break; `smoke-92-scripted-model.spec.ts`).
JVM side: `aruvii-test-support/.../FakeAgentChatPort.java` exists but **no test on master references it**
(`git grep -l FakeAgentChatPort origin/master` → only the class, a skill and two docs). Real infra: Testcontainers
Postgres/Redis via `@EnableAruviiIT` (31 IT files reference it directly).

## Primary sources for the debate

| source | claim (≤15 words) |
|---|---|
| Kent C. Dodds, *Write tests* — https://kentcdodds.com/blog/write-tests | quoting Rauch: "Write tests. Not too many. Mostly integration." |
| Dodds, *Testing Trophy and testing classifications* — https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications | layers static → unit → integration → e2e; integration = "multiple units integrating with one another" |
| Fowler, *TestPyramid* — https://martinfowler.com/bliki/TestPyramid.html | "many more low-level UnitTests than high level BroadStackTests" |
| Fowler, *On the Diverse And Fantastical Shapes of Testing* — https://martinfowler.com/articles/2021-test-shapes.html | quoting Searls: debating percentages "is a distraction"; trophy vs pyramid is mostly a solitary-vs-sociable naming dispute |

## What this says for Aruvii (facts, no decision)

1. **Aruvii's 31% integ share is already above every Python/TS peer measured** (3–18%) and below only the two JVM
   libraries (43–44%). The JVM peers' high share is inflated: about half their ITs are env-gated on a provider key
   and skip by default (spring-ai 181/374, langchain4j 346/647).
2. **Nobody in the sample sets a ratio.** Spring AI, LangChain4j and crewAI say "unit and/or integration"; openai-agents
   and OpenHands pick the tier by **who owns the behaviour / which seam is replaced** — the same axis as S1.
3. **The LLM is never live in the default run, anywhere.** Four techniques: scripted model in-process (openai-agents
   `ScriptedModel`, langgraph `FakeChatModel`, langchain4j `ChatModelMock`); scripted HTTP server (OpenHands mock-llm,
   Aruvii fake-llm); record/replay (crewAI VCR, mastra llm-recorder, n8n proxy expectations); real provider behind
   a key/flag (all Java, openai-agents, claude-agent-sdk).
4. **Peers that are integration-leaning get there by running the same test over real backends**, not by writing more
   test classes: langgraph parametrizes one suite over memory/sqlite/postgres/redis; langchain4j makes every provider
   extend a shared `Abstract*IT` contract; langgraph ships `checkpoint-conformance`.
5. Fowler/Searls: the pyramid-vs-trophy fight is mostly vocabulary. A Testcontainers IT of one service is a
   "sociable unit test" to a pyramid advocate and an "integration test" to Dodds — so "more ITs than units" is not
   by itself evidence of an inverted pyramid.
6. Aruvii gap vs peers: the in-process scripted fake (`FakeAgentChatPort`) is unused by any IT, so JVM ITs that touch
   the agent loop have no deterministic LLM seam; openai-agents treats this exact seam as the primary test tool.

## Candidate rules (for the operator, one at a time; none contradicts S1)

**R1 — boundary-first, not ratio-first.** "When S1 puts a behaviour at a boundary, its IT is the primary test; add unit specs only for branching the IT cannot reach cheaply."
Source: Dodds *Write tests*; openai-agents `docs/testing.md:524-530`; S1.

**R2 — fake the model at its seam, real everywhere else.** "In ITs and smoke, replace only the LLM — scripted `AgentChatPort` fake or fake-llm server; never mock our own services around it."
Source: openai-agents `ScriptedModel` + `conftest.py:130`; OpenHands `AGENTS.md:74`; Aruvii #576 fake-llm.

**R3 — one contract suite per port, run on the real backend.** "Each adapter port (store, stream, provider) has one shared spec every implementation extends, run against Testcontainers, never an in-memory stand-in."
Source: langchain4j `CONTRIBUTING.md:43,56`; langgraph `checkpoint-conformance`, `conftest.py:62`.
