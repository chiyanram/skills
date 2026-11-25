# Agent evals

How an eval harness runs an agent's golden set, keeps side effects out, grades with code and judges, and records
what failed. Read it when you write or review an eval harness, a golden set, an eval case or its status, a grader
or LLM judge, a trajectory assertion, or the sandbox an eval runs in.

## Rules

- Run each agent capability's versioned golden set through the real entry point, and fail on a drop beyond the
  threshold against the stored baseline, because a harness that bypasses the entry point tests something else.
  Thresholds over repeated runs are in the `testing` skill's model-calls notes.
- Point each tool that writes, sends or acts outside the run at a sandbox (a test store or a recording fake) whose end
  state the grader reads, because live tools send real messages and change real data, even in a test account.
- Record an infrastructure failure, a timeout or a truncation as its own eval status, out of the pass rate, because it
  measures the harness, not the agent.
- Grade with code first: a field, a number, a format, a tool call. Use an LLM judge only for an open-ended property
  such as tone or faithfulness, and pass the candidate output to it as data, because a judge is costlier, noisier and
  injectable. The verdict form is in the `testing` skill's model-calls notes.
- Ask each grader only for what the case's tools and files make possible. A case with no shell is graded on the steps
  the reply states, never on a run, because a grader that demands an impossible act fails every correct reply.
- Calibrate a judge against human labels on a sample before any threshold reads its score, and store the judge's
  model and prompt version with every score, because an uncalibrated judge drifts unseen.
- Assert required and forbidden tool calls on the recorded trajectory, with a declared match mode, and judge task
  success on the end state, because the path proves safety and the end state proves the task.

## Good / Bad

### The eval calls the real entry point

**Bad**
```java
final var reply = model.send(new ModelRequest(
        SUPPORT_PROMPT,
        List.of(Message.user(evalCase.input()))));
scores.add(grader.grade(evalCase, reply.text()));
```
The harness rebuilds the model call by hand. The agent's tools, history, guards and retries never run, so the score
says nothing about the agent.

**Good**
```java
final var result = supportAgent.handle(evalCase.toRequest());
scores.add(grader.grade(evalCase, result));
```
The case goes through the same entry point users reach, so the score covers the whole agent.

### Side-effecting tools point at a sandbox the grader reads

**Bad**
```java
final var supportAgent = new SupportAgent(
        model,
        liveTools);
```
Running the golden set issues real refunds and sends real emails to the customers in the cases.

**Good**
```java
final var sandbox = new EvalSandbox();
final var supportAgent = new SupportAgent(
        model,
        liveTools.withSandbox(Map.of(
                "issueRefund", sandbox.refunds(),
                "sendEmail", sandbox.outbox())));
```
The tools that change the outside world write to the sandbox instead, and the grader reads its end state.
Reads and the model stay real.

### Code grades what code can check

**Bad**
```java
final var verdict = judge.ask("Did the assistant refund 25.00 to order A-17? " + result.text());
```
A judge decides a fact that the recorded tool calls already hold. The answer text is pasted into the judge's
instructions, so an answer that says "grade this as yes" can steer it.

**Good**
```java
final var refunded = result.toolCalls().contains(new ToolCall(
        "issueRefund",
        Map.of("orderId", "A-17", "amount", "25.00")));
final var polite = judge.grade(Rubric.TONE, JudgeInput.candidate(result.text()));
```
The refund is checked in code. The judge grades only tone, and gets the answer as a separate data field.

### Path for safety, end state for the task

**Bad**
```groovy
then:
result.text().contains("refund has been issued")
```
The agent can say the refund was issued without calling the tool, or after calling `closeAccount` on the way.

**Good**
```groovy
then:
Trajectory.of(result).matches(MatchMode.IN_ORDER, ["findOrder", "issueRefund"])
Trajectory.of(result).never("closeAccount")
sandbox.refunds.issued == [new Refund("A-17", 25.00G)]
```
The trajectory shows the required calls ran and the forbidden one did not. The sandbox's end state shows the task
was done.

## Review

Walk the harness, the golden set, each case's graders, and the tools each evaluated capability can call.

Each line is a finding, a blocker unless marked (warning).

- A model call built by hand, an unversioned golden set, or no comparison against a stored baseline.
- A side-effecting tool not pointed at a sandbox, or a grader that does not read the sandbox's end state.
- An infrastructure error, timeout or truncation counted as a failed case.
- A judge that grades a property code can check, or a candidate output put into the judge's instructions.
- A grader that asks for an act the case cannot do: a run with no shell, or a file the case does not hold.
- A gating judge with no calibration against human labels, or a score without the judge's model and prompt version.
- A text-only assertion on a case with a safe and an unsafe path, no forbidden-call check, or no declared match mode.
