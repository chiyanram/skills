# Agent loop

How the loop turns model replies into steps, answers tool calls, handles tool errors, bounds itself, and pauses and
resumes a run for approval. Read it when you write or review an agent loop, a step result, a tool-call result or
tool error, a call cap, an approval pause, or a resume path.

Contents: Rules · When X, use Y · Good / Bad (AE14, AE15, AEN3, AE16) · Decided edges · Review checks

## Rules

- **AE12** — Classify each model reply into a closed step result (final, run again, paused, stopped) and switch on
  it, returning a pause as a value, because status-string branches miss new cases.
- **AE20** — Answer every tool call of one reply in the next message, results first, each matched by its call id,
  because providers reject a history with split, reordered or missing results.
- **AE16** — Return model-correctable faults (unknown tool, invalid arguments, denied approval) as error tool results
  naming the valid form, and end the run only on platform faults, because the model can fix them.
- **AE17** — Show the model a generic, actionable tool error, never a raw exception message or stack trace, because
  that text enters context and leaks internals into the model's output.
- **AE18** — Cap consecutive failures per tool and repeated identical calls, and end or escalate the run at the cap,
  because a model can retry one broken call until the step budget runs out.
- **AE19** — Check the run's model-call ceiling before every model call on every path, resume included, because a
  ceiling checked only in the main loop leaves the other paths unbounded.
- **AE13** — End a run that needs approval with a persisted pending request keyed by tool-call id, and resume through
  the same loop with the same checks, because a second resume path skips budget and guards.
- **AE14** — On resume, run only a call that matches the stored call this agent made, and re-check authorization and
  tool guards first, because a client can submit a forged call or approval.
- **AE15** — Persist each finished tool result keyed by run, step and call id before the loop moves on, and on resume
  run only calls without a stored result, because resume otherwise repeats side effects.
- **AEN3** — Derive a side-effecting tool call's idempotency key from the run id and the tool-call id, and pass it to
  the remote end, because resume runs a call with no stored result again.

## When X, use Y

| situation | use | why |
|---|---|---|
| the loop reads a model reply | a closed step result: final, run again, paused, stopped | status-string branches miss new cases (AE12) · the stop reason it reads: AE1 (`adapter`) |
| a reply holds several tool calls | one next message with every result, results first, each with its call id | providers reject split, reordered or missing results (AE20) |
| a tool call names an unknown tool, has invalid arguments or is denied | an error tool result naming the valid form; the run goes on | the model can fix it (AE16) · its test: LT7 (`testing`'s `llm-tests`) |
| a tool or the platform throws | a generic, actionable error text for the model; the exception goes to the log | raw text leaks internals into the model's output (AE17) · the HTTP twin: ER10 (`code`'s `errors`) |
| the same tool fails again, or the same call repeats | a per-tool failure cap and a repeat cap that end or escalate the run | one broken call can use up the step budget (AE18) |
| a path calls the model: main loop, resume, summariser, judge | the run's call-ceiling check before the call | a ceiling only in the main loop leaves other paths unbounded (AE19) · the cap's test: LT8 |
| a tool needs human approval | a persisted pending request keyed by call id; resume through the same loop | a second resume path skips budget and guards (AE13) · its test: LS8 |
| a client resumes a run with an approval or a call | a match against the stored call this agent made, then authorization and guards again | a client can forge a call or an approval (AE14) |
| a tool finishes | its result stored by run, step and call id before the next step | resume otherwise repeats side effects (AE15) |
| a tool changes something outside the run | an idempotency key from run id and call id, sent to the remote end | a call with no stored result runs again on resume (AEN3) · the remote end: CC15, CC19 (`code`'s `concurrency`) |

## Good / Bad

### AE14 — Resume runs only the stored call, after the checks

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
main loop (AE13).

### AE15 — Store each result before the next step; resume skips stored calls

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

### AEN3 — The tool call's key reaches the remote end

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
        context.runId() + ":" + context.callId());
```
The key is the same on every run of this call, so the payment service applies the refund once.

### AE16 — A fault the model can fix goes back as a tool result

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

## Decided edges

- **Skip when** a tool only reads and changes nothing outside the run: AEN3 does not apply, and a repeat on resume is
  harmless (AE15 still stores its result). — **Do not skip when** the tool writes, sends, pays or calls another
  system that changes state. — **Confidence** high
- **Skip when** a tool error is a platform fault, such as a lost database or a missing credential: end the run
  (AE16), with the generic text of AE17. — **Do not skip when** the model's own call caused the fault. —
  **Confidence** high
- **Skip when** the run has no human approval step: AE13 and AE14 do not apply; AE15 still applies to a crash or
  restart. — **Do not skip when** any tool can pause the run. — **Confidence** high

## Review checks

Walk every changed agent loop, step handler, tool executor, approval pause and resume path.

- [ ] AE12 — Find where the loop decides its next step. A branch on a status string or a boolean flag, or a pause
  thrown as an exception, is a finding.
  Applies when: code decides the next step from a model reply
  Evidence: the branch at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the step type and every switch over it
- [ ] AE20 — Find where tool results are added to history. Results split over messages, out of call order, or a
  call with no result is a finding.
  Applies when: a reply can hold more than one tool call
  Evidence: the history append at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the append and the call-id match
- [ ] AE16 — For an unknown tool, invalid arguments and a denied approval, find what the model receives. A run that
  ends on one of them, or an error result that names no valid form, is a finding.
  Applies when: code dispatches tool calls
  Evidence: the branch for each fault at `file:line`
  Not a finding: a platform fault (decided edge)
  Severity: Act on
  Verify: re-open the dispatcher's error branches
- [ ] AE17 — Find each tool error text sent to the model. An exception message, a stack trace or a class name in it
  is a finding.
  Applies when: code turns a tool exception into a tool result
  Evidence: the text built at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the error mapping and the log call beside it
- [ ] AE18 — Find the per-tool failure cap and the repeated-call cap. A loop with either missing, or a cap that only
  logs, is a finding.
  Applies when: code runs a tool loop
  Evidence: the caps at `file:line`, or their absence
  Not a finding: none
  Severity: Act on
  Verify: re-open the loop and what happens at each cap
- [ ] AE19 — List every path that calls the model: main loop, resume, summariser, judge. A path with no call-ceiling
  check before the call is a finding.
  Applies when: code calls the model inside a run
  Evidence: each call site at `file:line` and its check
  Not a finding: none
  Severity: Act on
  Verify: re-open each call site
- [ ] AE13 — Find how a run pauses for approval and how it resumes. A pause not persisted by call id, or a resume
  path outside the main loop, is a finding.
  Applies when: a tool can need approval
  Evidence: the pause and the resume at `file:line`
  Not a finding: a run with no approval step (decided edge)
  Severity: Act on
  Verify: re-open the resume entry point and the loop it calls
- [ ] AE14 — Open the resume entry point. A call taken from the client's request, or a resume that skips
  authorization or tool guards, is a finding.
  Applies when: a client can resume a paused run
  Evidence: the resume code at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the lookup of the stored call and the checks after it
- [ ] AE15 — Find where tool results are persisted. A result stored only with its whole step, or a resume that runs
  calls with a stored result, is a finding.
  Applies when: a run can be resumed or restarted
  Evidence: the store and the resume filter at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open the store's key and the resume filter
- [ ] AEN3 — For each side-effecting tool, find the idempotency key it sends. A key not derived from run id and call
  id, or no key, is a finding.
  Applies when: a tool writes, sends, pays or changes state outside the run
  Evidence: the key at `file:line`
  Not a finding: a read-only tool (decided edge)
  Severity: Act on
  Verify: re-open the tool's request builder
