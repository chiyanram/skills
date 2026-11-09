# Retro

How a merged pull request teaches the pipeline: what to record, how to find the real cause, and how a lesson becomes a
rule, a script, a check or nothing. A rescue is a human fixing or finishing an agent's work. Read it when the engine
writes a merge's timeline record, or when a human starts a full retro.

## Rules

- **RT1** — The engine writes each merged PR's timeline record with no model: rounds, findings per bucket and check,
  tokens per phase and every rescue, because a pipeline nobody measures cannot tell which phase helps.
- **RT2** — Trace each rescue or escaped defect past "the agent got it wrong" by asking why until a rule, check or step
  is named, because blaming the agent fixes nothing for the next change.
- **RT3** — For each rescue or escaped defect, tune the existing check that should have caught it, or propose a new
  one naming this ticket as its origin, because a check without an origin is a guess.
- **RT4** — Give each action a type (rule, script, check or playbook), one owner, a due date and a ticket, never just
  "improve", because an action without an owner and a date does not happen.
- **RT5** — Mine each run's transcripts for lessons, cite every number and claim from the transcript or a command,
  and keep only lessons that recur, because a retro from memory records what the coordinator believes.
- **RT6** — Fix a repeated mistake at the highest level that holds: structure, type, a lint whose error names the fix,
  then a test; a written rule only for judgement calls, because a skipped rule fails nothing.
- **RT7** — Run a full retro only when a human starts one; a rescue, revert or escaped defect is flagged in the
  timeline record, never a trigger, because a human picks which lesson is worth a run.

## When X, use Y

| situation | use | why |
|---|---|---|
| every merge | the RT1 record, written by the engine with no model | the record is cheap and needs no judgement |
| a human starts a full retro on a merged, rescued or reverted change or an escaped defect | RT2 to RT6, read from the RT1 record | the human picks where the analysis is worth a run (RT7) |
| a mistake seen twice | a fix at the highest level that holds: structure, then a type, then a lint whose error names the fix, then a test (RT6) | a higher level stops the mistake; a written rule only asks |
| the lesson can be checked by a tool | an action of type script or check, not rule (RT4, RT6) | a script never forgets |
| the lesson needs judgement | an action of type rule (RT4, RT6) | every new rule still needs the operator's yes and a ledger row |
| an existing check should have caught it but did not | a rewrite of that check, with this ticket as its example (RT3) | the check is mis-worded, not missing |
| facts for the retro | the transcripts of the coordinator, implementer, finder and verify pass runs, and the PR's events; each number cited to one of them (RT5) | memory rounds off the bad parts |
| a lesson found once | kept only if it recurs; otherwise noted and dropped (RT5) | a one-off is not a learning, and a rule per one-off becomes noise |

## Good / Bad

### RT4 — An action that will happen

**Bad**
```text
Actions:
- Improve testing around renewals.
- Be more careful with reservations.
```
No type, no owner, no date, no ticket. Nobody acts on either line.

**Good**
```text
Actions:
- script · fail the build when a renewal endpoint has no reservation test
  · owner: operator · due 2026-11-20 · ticket #77
- check · CR1 example: "renewal ignores reservation" · owner: coordinator · due 2026-11-13 · ticket #78
```
Each action says what kind of fix, who owns it, when, and where it is tracked.

## Decided edges

- **Skip the full retro when** no human started one, even after a rescue, revert or escaped defect: the RT1 record
  flags it. — **Do not skip when** a human started it: run RT2 to RT6 (RT7). — **Confidence** high
- **Skip a new check when** an existing check covers the case and only missed it: tune that check. — **Do not skip
  when** no rule or check covers the case at all (RT3). — **Confidence** high
- **Skip the transcript mining when** no human started a full retro: the RT1 record is enough. — **Do not skip
  when** a human started one (RT5). — **Confidence** high
- **Skip the recurrence bar when** the one instance is a rescue, a revert or an escaped defect: it is a lesson the first
  time. — **Do not skip when** the lesson comes from a merge that went well (RT5, RT2, RT3). — **Confidence** high

## Review checks

Walk the timeline record, and the retro hand-off (`.factory/retro.md`) when a human started a full retro.

- [ ] RT1 — Find the rounds, findings per bucket and check, tokens per phase and each rescue, written by the engine at
  the merge. Each one missing is a finding.
- [ ] RT2 — For each rescue or escaped defect, find the named rule, check or step behind it. A cause that stops at "the
  agent got it wrong" is a finding.
- [ ] RT3 — For each, find the answer to "should an existing check have caught it?" and the tuned or proposed check.
  Each one missing is a finding.
- [ ] RT4 — For each action, find its type, owner, due date and ticket. Each one missing, or a bare "improve", is a
  finding.
- [ ] RT5 — In the retro, find a transcript or command cite for each number and each claim about what happened. A
  number with no cite, or a lesson from one instance that was not a rescue, revert or escaped defect, is a finding.
- [ ] RT6 — For each action of type rule, find why a structure, type, lint or test could not hold it. A rule for a
  mistake a lint or type could catch is a finding.
- [ ] RT7 — Find who started each full retro. One started by the engine, the coordinator or any run, not a human, is
  a finding.
