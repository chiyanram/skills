---
name: agent
description: Use when you write or review code that calls an LLM or language model or runs an agent: a provider adapter, stop reasons, streaming, token usage and fallback; the tool loop, approval and resume; prompt and context building, compaction and prompt caching; guards and tool risk; GenAI spans; evals; run budgets. Lists each agent reference and when to read it.
---

# Agent

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks.

These rules cover the production code of an agent. The tests of that code are in the `testing` skill's
`model-calls.md`: the fake model, and live tests against real models with the eval gate. The eval harness itself is this skill's `evals` reference.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [adapter](references/adapter.md) | AE1–AE3, AE5–AE10, AEN2 | when you write or review a model adapter, a stop reason, a model error or retry policy, a streamed reply, a tool call's arguments, a usage record, an output-token cap or a fallback model |
| [context](references/context.md) | AE21–AE26 | when you write or review the code that builds a model request, a memory window, compaction or summarisation of history, a prompt cache breakpoint, or how a tool result enters context |
| [cost](references/cost.md) | AE51, AEN6 | when you write or review a run budget, a workspace or tenant budget, a spend limit, or the code that checks or records usage around a model call |
| [evals](references/evals.md) | AE43–AE46, AE48, AEN4 | when you write or review an eval harness, a golden set, an eval case or its status, a grader or LLM judge, a trajectory assertion, or the sandbox an eval runs in |
| [genai-obs](references/genai-obs.md) | AE37–AE41 | when you write or review a span, metric or log for a model call, a tool call or an agent run, the capture of prompts and completions, or the record kept for each model call |
| [guard](references/guard.md) | AE28–AE31, AE33–AE34, AE36 | when you write or review a guard, an approval gate, a tool's risk or approval setting, the tool-call pipeline, an output check, an MCP tool, or how outside content enters the model's context |
| [loop](references/loop.md) | AE12–AE20, AEN3 | when you write or review an agent loop, a step result, a tool-call result or tool error, a call cap, an approval pause, or a resume path |
<!-- /index -->
