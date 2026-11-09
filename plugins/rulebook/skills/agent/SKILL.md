---
name: agent
description: Use when you write or review code that calls an LLM or language model or runs an agent: a provider adapter, stop reasons, streaming, token usage and fallback; the tool loop, approval and resume; prompt and context building, compaction and prompt caching; guards and tool risk; GenAI spans; evals; run budgets. Lists each agent reference and when to read it.
---

# Agent

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks.

These rules cover the production code of an agent. The tests of that code are in the `testing` skill: its
`llm-tests` reference for the fake model, and its `llm-live-tests` reference for real models and the eval gate
(LT17, LT18). The eval harness itself is this skill's `evals` reference.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [adapter](references/adapter.md) | AE1–AE3, AE5–AE10, AEN2 | when you write or review a model adapter, a stop reason, a model error or retry policy, a streamed reply, a tool call's arguments, a usage record, an output-token cap or a fallback model |
<!-- /index -->
