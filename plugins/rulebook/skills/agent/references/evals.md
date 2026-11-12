# Agent evals

How an eval harness runs an agent's golden set, keeps side effects out, grades with code and judges, and records
what failed. Read it when you write or review an eval harness, a golden set, an eval case or its status, a grader
or LLM judge, a trajectory assertion, or the sandbox an eval runs in.

Contents: Rules · When X, use Y · Good / Bad (AE43, AEN4, AE45, AE48) · Decided edges · Review checks

## Rules

- **AE43** — Run each agent capability's versioned golden set through the real entry point and fail on a drop beyond
  the threshold against the stored baseline, because a harness that bypasses the entry point tests something else.
- **AEN4** — Point each tool that writes, sends or acts outside the run at a sandbox (test store or recording fake)
  whose end state the grader reads, because live tools send real messages and change real data.
- **AE44** — Record infrastructure failures, timeouts and truncations as their own eval status, never as a failed
  case, because they measure the harness, not the agent.
- **AE45** — Grade with code first and use an LLM judge only for properties code cannot check, passing the candidate
  output to it as data, because a judge is costlier, noisier and injectable.
- **AE46** — Calibrate a judge against human labels on a sample before it gates, and store the judge's model and
  prompt version with every score, because an uncalibrated judge drifts unseen.
- **AE48** — Assert required and forbidden tool calls on the recorded trajectory with a declared match mode, and
  judge task success on the end state, because the path proves safety and the end state proves the task.

## When X, use Y

| situation | use | why |
|---|---|---|
| an eval runs an agent capability | its versioned golden set, through the real entry point, against the stored baseline | a harness that bypasses the entry point tests something else (AE43) · thresholds over repeated runs: the `testing` skill's model-calls notes |
| the agent's tools write, send or act outside the run | a sandbox for those tools, a test store or a recording fake, and a grader that reads its end state | live tools send real messages and change real data (AEN4) |
| a case ends in an infrastructure error, a timeout or a truncation | its own status, kept out of the pass rate | it measures the harness, not the agent (AE44) |
| a property can be checked by code: a field, a number, a format, a tool call | a code grader | a judge is costlier, noisier and injectable (AE45) |
| a property needs judgement: tone, faithfulness, helpfulness | an LLM judge that gets the candidate output as data | code cannot check it (AE45) · the verdict form: `testing`'s model-calls.md |
| a judge is about to gate a release | its agreement with human labels on a sample, and its model and prompt version stored with each score | an uncalibrated judge drifts unseen (AE46) |
| a case has a safe and an unsafe path | required and forbidden tool calls on the trajectory, with a declared match mode, and the end state | the path proves safety and the end state proves the task (AE48) |

## Good / Bad

### AE43 — The eval calls the real entry point

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

### AEN4 — Side-effecting tools point at a sandbox the grader reads

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
The tools that change the outside world write to the sandbox instead, and the grader reads its end state (AE48).
Reads and the model stay real.

### AE45 — Code grades what code can check

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

### AE48 — Path for safety, end state for the task

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
was done (AEN4).

## Decided edges

- **Skip when** a capability has no tool that changes the outside world: AEN4 does not apply. — **Do not skip when**
  any tool writes, sends, pays or calls another system that changes state, even in a test account. —
  **Confidence** high
- **Skip when** the property is open-ended, such as tone or faithfulness, and a code check would need one fixed
  answer text: an LLM judge grades it (AE45). — **Do not skip when** the property is a fact in the output or the
  trajectory: code grades it. — **Confidence** medium
- **Skip when** a judge only reports and never gates: its calibration can wait, but each score still stores the
  judge's model and prompt version (AE46). — **Do not skip when** any threshold reads the judge's score. —
  **Confidence** medium

## Review checks

Walk every changed eval harness, golden set, grader, judge and eval sandbox.

- [ ] AE43 — Open the harness. A model call built by hand, an unversioned golden set, or no comparison against a
  stored baseline is a finding.
  Applies when: code runs an eval of an agent capability
  Evidence: the call into the agent and the baseline comparison at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open the harness and the entry point it calls
- [ ] AEN4 — List the tools each evaluated capability can call. A tool that writes, sends or acts outside the run
  and does not point at a sandbox, or a grader that does not read the sandbox's end state, is a finding.
  Applies when: an eval runs a capability with side-effecting tools
  Evidence: the tool wiring at `file:line`
  Not a finding: a capability with no side-effecting tool (decided edge)
  Severity: blocker
  Verify: re-open the eval's tool wiring against the capability's tool list
- [ ] AE44 — Open the case status type. An infrastructure error, timeout or truncation counted as a failed case is a
  finding.
  Applies when: code records an eval case's outcome
  Evidence: the status mapping at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open the mapping and the pass-rate calculation
- [ ] AE45 — For each judge call, name the property it grades. A property code can check, or a candidate output put
  into the judge's instructions, is a finding.
  Applies when: an eval calls an LLM judge
  Evidence: the judge call at `file:line`
  Not a finding: an open-ended property (decided edge)
  Severity: blocker
  Verify: re-open the judge's input builder
- [ ] AE46 — For each judge that gates, find its calibration against human labels and the stored model and prompt
  version. A missing one is a finding.
  Applies when: a threshold reads an LLM judge's score
  Evidence: the calibration record and the score record at `file:line`
  Not a finding: a judge that only reports (decided edge)
  Severity: blocker
  Verify: re-open the score record's fields
- [ ] AE48 — For each case with a safe and an unsafe path, find the trajectory assertions and the end-state check. A
  text-only assertion, no forbidden-call check, or no declared match mode is a finding.
  Applies when: an eval case runs tools
  Evidence: the assertions at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open the case and its grader
