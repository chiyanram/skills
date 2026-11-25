# Agent loop

How the loop turns model replies into steps, answers tool calls, handles tool errors, bounds itself, and pauses and
resumes a run for approval. Read it when you write or review an agent loop, a step result, a tool-call result or
tool error, a call cap, an approval pause, or a resume path.

## Rules

- Classify each model reply into a closed step result (final, run again, paused, stopped) and switch on it, with a
  pause returned as a value, because branches on a status string miss new cases. The stop reason it reads comes from
  [adapter.md](adapter.md).
- Answer every tool call of one reply in the next message, results first, each matched by its call id, because
  providers reject a history with split, reordered or missing results.
- Return a fault the model can fix (unknown tool, invalid arguments, denied approval) as an error tool result that
  names the valid form, and go on, because the model can fix it. End the run only on a platform fault, such as a lost
  database or a missing credential.
- Show the model a generic, actionable tool error and send the exception to the log, because exception text enters
  context and leaks internals into the model's output. The HTTP twin is in `code`'s Errors rules.
- Cap consecutive failures per tool and repeated identical calls, and end or escalate the run at the cap, because a
  model can retry one broken call until the step budget runs out.
- Check the run's model-call ceiling before every model call on every path (main loop, resume, summariser, judge),
  because a ceiling checked only in the main loop leaves the other paths unbounded.
- End a run that needs approval with a persisted pending request keyed by tool-call id, and resume through the same
  loop with the same checks, because a second resume path skips the budget and the guards.
- On resume, run only a call that matches the stored call this agent made, and re-check authorization and tool
  guards first, because a client can submit a forged call or approval.
- Store each finished tool result by run, step and call id before the loop moves on, and on resume run only calls
  with no stored result, because resume otherwise repeats side effects. This holds for a crash or restart too, with
  no approval step.
- Send a side-effecting tool call's result key (run id, step, call id) to the remote end as its idempotency key,
  because resume runs a call with no stored result again. A read-only tool needs no key. When the remote end takes no
  key under any name, mark the call unknown before a resend and read the remote state to see whether it ran (`code`'s
  `concurrency` notes, Side effects and idempotency).

## Good / Bad

### Resume runs only the stored call, after the checks

**Bad**
```java
public RunResult resume(final ResumeRequest resume) {
    final var call = resume.toolCall();
    return loop.continueWith(tools.run(call));
}
```
The client sends the call to run. A forged call, or an approval for a call the agent never made, runs with no check.

**Good**
```java
public RunResult resume(final ResumeRequest resume) {
    final var pending = runs.pendingApproval(resume.runId(), resume.callId());
    if (pending.isEmpty() || !resume.approver().mayApprove(pending.get())) {
        return RunResult.rejected(resume.runId());
    }
    return loop.resume(pending.get(), resume.decision());
}
```
The call comes from the stored pending request. `loop.resume` runs the same guards, budget and pipeline as the
main loop.

### Store each result before the next step; resume skips stored calls

**Bad**
```java
for (final var call : reply.toolCalls()) {
    results.add(tools.run(call));
}
runs.saveStep(runId, step, results);
```
A crash after the second of three calls loses both results. Resume runs all three again, so two refunds repeat.

**Good**
```java
for (final var call : reply.toolCalls()) {
    final var key = new CallKey(runId, step, call.id());
    if (runs.result(key).isEmpty()) {
        runs.saveResult(key, tools.run(call));
    }
}
```
Each result is stored as it finishes. On resume, a call with a stored result does not run again.

### The tool call's key reaches the remote end

**Bad**
```java
final var refund = new RefundRequest(
        orderId,
        amount,
        UUID.randomUUID().toString());
```
The key is new on each run of the call. If the process stops after the refund but before its result is stored,
resume sends a second refund under a new key.

**Good**
```java
final var refund = new RefundRequest(
        orderId,
        amount,
        context.callKey().asIdempotencyKey());
```
`callKey()` is the run id, step and call id the result is stored under. The key is the same on every run of
this call, so the payment service applies the refund once.

### A fault the model can fix goes back as a tool result

**Bad**
```java
final var tool = registry.find(call.name())
        .orElseThrow(() -> new UnknownToolException(call.name()));
```
The model asked for `findOrders` instead of `findOrder`. The run ends with an error the model could have fixed.

**Good**
```java
final var tool = registry.find(call.name());
if (tool.isEmpty()) {
    return ToolResult.error(call.id(), "Unknown tool. Valid tools: " + registry.names());
}
```
The model sees the valid names and calls `findOrder` in the next step.

## Review

Walk every changed agent loop, step handler, tool executor, approval pause and resume path.

Each line is a finding, a blocker unless marked (warning).

- A next step decided by a status string or a boolean flag, or a pause thrown as an exception.
- Tool results split over messages, out of call order, or a call with no result.
- A run that ends on an unknown tool, invalid arguments or a denied approval, or an error result that names no valid
  form.
- An exception message, a stack trace or a class name in a tool error sent to the model.
- A loop with no per-tool failure cap or no repeated-call cap, or a cap that only logs.
- A path that calls the model with no call-ceiling check before it.
- A pause not persisted by call id, or a resume path outside the main loop.
- A resume that takes the call from the client's request, or skips authorization or tool guards.
- A tool result stored only with its whole step, or a resume that runs calls with a stored result.
- A side-effecting tool that sends no idempotency key, or a key that is not the call's result key.
