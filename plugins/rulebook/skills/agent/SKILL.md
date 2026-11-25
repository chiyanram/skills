---
name: agent
description: "Use when you write or review code that calls an LLM or language model or runs an agent: a provider adapter, stop reasons, streaming, token usage and fallback; the tool loop, approval and resume; prompt and context building, compaction and prompt caching; guards and tool risk; GenAI spans; evals; run budgets. Lists each agent notes file and when to read it."
---

# Agent

Agent code earns its place when a model's reply, however wrong, cannot make the system act unsafely, lose work or
overspend. Everything below serves that.

These notes cover the production code of an agent. The tests of that code are in the `testing` skill's
`model-calls.md`: the fake model, and live tests against real models with the eval gate.

## Before you change agent code

1. Find the one place each concern lives: the adapter for a provider, the loop for steps, the request builder for
   context, the pipeline for guards. A change that adds a second place for one of them is the change to rethink,
   because two copies drift and one of them skips a check.
2. Treat every model reply, tool result and piece of outside content as untrusted input, because the model can be
   wrong or steered.
3. Read the notes for each part the change touches. Each one holds its rules, bad and good code, and a review list
   at its end.

## Notes

- A provider adapter, stop reason, model error or retry, streamed reply, tool-call arguments, usage record,
  output-token cap or fallback model: [adapter.md](adapter.md).
- The agent loop, a step result, a tool result or tool error, a call cap, an approval pause or a resume path:
  [loop.md](loop.md).
- The code that builds a model request, a memory window, compaction, a prompt cache breakpoint, or how a tool result
  enters context: [context.md](context.md).
- A guard, an approval gate, a tool's risk, the tool-call pipeline, an output check, an MCP tool, or outside content
  entering context: [guard.md](guard.md).
- A span, metric or log for a model call, tool call or run, content capture, or the record of each model call:
  [genai-obs.md](genai-obs.md).
- An eval harness, a golden set, an eval case or its status, a grader or LLM judge, a trajectory assertion, or an
  eval sandbox: [evals.md](evals.md).
- A run, workspace or tenant budget, a spend limit, or the usage checks around a model call: [cost.md](cost.md).

## Reviewing agent code

Walk the review list at the end of each notes file the diff touches, and every rule above it. Name a finding by the
notes file and its rule's words, quoted.
