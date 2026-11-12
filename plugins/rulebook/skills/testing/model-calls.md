# Testing code that calls a language model

The general rules are in [SKILL.md](SKILL.md).

## In the gate, with a fake model

- Fake the model behind your own port, with one shared scripted fake. The fake fails on an unscripted extra call and
  on unused steps, so a loop that ran too many or too few turns fails.
- Fail any test that reaches a real model client without opting in by name.
- Assert on the requests the code sent the model, not only the final answer. A lost tool result shows up only in the
  next request.
- Test each provider adapter against a fake HTTP server under the real SDK, and assert the request JSON.
- Feed a tool error back to the model and assert the run goes on.
- Cap the loop by turns and test the cap.
- Script a stream in several chunks and assert they join in order, with every wait bounded.
- After an injected provider failure, assert what was stored and which side effects ran, not only the reply.
- Test that a blocking guard stops the run before the model or tool is called.
- Test approval by saving the paused run, restoring it, then approving; each side effect runs exactly once.
- Put a prompt injection in a tool result and run the whole loop. Tool results are where untrusted text enters.
- Order races with explicit signals, never sleeps.

## Live tests, with a real model

- Live-test only what a fake cannot know: that the provider accepts the request, real chunking, real usage numbers,
  real errors. The agent's own logic stays in fakes.
- Run them in their own job, outside the gate, with a pinned small model, a token cap per call, and a failure when
  the suite is skipped.
- Assert only what the test controls: structure, parsed fields, tool arguments, side effects. Exact prose flakes, and
  "not empty" catches nothing.
- Retry transport errors only, never a failed assertion.
- An LLM judge gives atomic verdicts, counts "not sure" as a fail, and never grades its own model's output. Gate an
  eval on per-metric thresholds over repeated runs.
