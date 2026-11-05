# R19 · How agent SDKs / agent platforms balance unit vs integration tests

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G9a (strategy.md S1 emphasis)

## Question

In high-star agent SDKs / platforms (Spring AI, LangChain4j, OpenAI Agents SDK, Anthropic Claude Agent SDK, LangGraph,
CrewAI, Mastra, OpenHands, n8n) — measured from their repos: ratio of unit vs integration/e2e tests, how they fake the
LLM (scripted model, recorded cassettes, stub provider), what they run against real infra (DB, vector store, Redis,
containers), and any written testing philosophy (testing trophy vs pyramid). Compare with ours (313 unit-tree vs 141
integrationTest classes on master; scripted fake model work in #608). Is an integration-heavy mix right for Aruvii?

## Resolution (2026-10-02)

`../research/23-agent-sdk-test-mix.md`. IT share by test files: Aruvii 31% (313 unit / 141 IT, +93 smoke) — above every
Python/TS SDK measured (crewAI 3%, OpenHands 3%, openai-agents 8%, mastra 12%, n8n 12%, langgraph 18%), below spring-ai 43%
and langchain4j 44% (about half of theirs skip without a provider key). No repo sets a ratio target; openai-agents and
OpenHands pick the tier by which boundary is replaced (= S1). No repo calls a live LLM by default: scripted in-process model,
scripted HTTP server (ours: fake-llm #576/#608), record/replay, or real provider behind a key. Integration-leaning repos run
the SAME tests over several real backends (langgraph; langchain4j Abstract*IT contracts). Gap (verified): FakeAgentChatPort
in aruvii-test-support is used by no test on master. Candidate rules TM1–TM3, one by one.
