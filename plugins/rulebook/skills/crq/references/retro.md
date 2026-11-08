# Retro

How a merged pull request teaches the pipeline: what to record, how to find the real cause, and how a lesson becomes a
rule, a script, a check or nothing. A rescue is a human fixing or finishing an agent's work. Read it when a pull
request is merged, rescued or reverted, or a defect escapes.

## Rules

- **RT1** — Record each merged pull request's timeline: rounds, findings per bucket and check, tokens per phase and
  every rescue, because a pipeline nobody measures cannot tell which phase helps.
- **RT2** — Trace each rescue or escaped defect past "the agent got it wrong" by asking why until a rule, check or step
  is named, because blaming the agent fixes nothing for the next change.
- **RT3** — For each rescue or escaped defect, tune the existing check that should have caught it, or propose a new
  one naming this issue as its origin, because a check without an origin is a guess.
- **RT4** — Give each action a type (rule, script, check or playbook), one owner, a due date and an issue, never just
  "improve", because an action without an owner and a date does not happen.
- **RT5** — Mine each run's transcripts for lessons, cite every number and claim from the transcript or a command,
  and keep only lessons that recur, because a retro from memory records what the coordinator believes.
- **RT6** — Fix a repeated mistake at the highest level that holds: structure, type, a lint whose error names the fix,
  then a test; a written rule only for judgement calls, because a skipped rule fails nothing.

## When X, use Y

| situation | use | why |
|---|---|---|
| a rescue, a revert or an escaped defect | a full retro: RT1 to RT6 | each one shows where the pipeline failed |
| any other merge | the RT1 record only | the record is cheap; the analysis goes where something failed |
| a mistake seen twice | a fix at the highest level that holds: structure, then a type, then a lint whose error names the fix, then a test (RT6) | a higher level stops the mistake; a written rule only asks |
| the lesson can be checked by a tool | an action of type script or check, not rule (RT4, RT6) | a script never forgets |
| the lesson needs judgement | an action of type rule (RT4, RT6) | every new rule still needs the operator's yes and a ledger row |
| an existing check should have caught it but did not | a rewrite of that check, with this issue as its example (RT3) | the check is mis-worded, not missing |
| facts for the retro | the transcripts of the coordinator, writers and reviewers, and the pull request's events; each number cited to one of them (RT5) | memory rounds off the bad parts |
| a lesson found once | kept only if it recurs; otherwise noted and dropped (RT5) | a one-off is not a learning, and a rule per one-off becomes noise |

## Good / Bad

### RT4 — An action that will happen

**Bad**
```text
Actions:
- Improve testing around renewals.
- Be more careful with reservations.
```
No type, no owner, no date, no issue. Nobody acts on either line.

**Good**
```text
Actions:
- script · fail the build when a renewal endpoint has no reservation test
  · owner: operator · due 2026-11-20 · issue #77
- check · CR1 example: "renewal ignores reservation" · owner: coordinator · due 2026-11-13 · issue #78
```
Each action says what kind of fix, who owns it, when, and where it is tracked.

## Decided edges

- **Skip the full retro when** a change merged with no rescue, revert or escaped defect: the RT1 record still runs. —
  **Do not skip when** it needed a rescue or was reverted (RT2, RT3). — **Confidence** high
- **Skip a new check when** an existing check covers the case and only missed it: tune that check. — **Do not skip
  when** no rule or check covers the case at all (RT3). — **Confidence** high
- **Skip the transcript mining when** the merge had no rescue, revert or escaped defect: the RT1 record is enough. —
  **Do not skip when** there was a rescue, a revert or an escaped defect (RT5). — **Confidence** high
- **Skip the recurrence bar when** the one instance is a rescue, a revert or an escaped defect: it is a lesson the first
  time. — **Do not skip when** the lesson comes from a merge that went well (RT5, RT2, RT3). — **Confidence** high

## Review checks

Walk the retro note on the issue.

- [ ] RT1 — Find the rounds, findings per bucket and check, tokens per phase and each rescue. Each one missing is a
  finding.
- [ ] RT2 — For each rescue or escaped defect, find the named rule, check or step behind it. A cause that stops at "the
  agent got it wrong" is a finding.
- [ ] RT3 — For each, find the answer to "should an existing check have caught it?" and the tuned or proposed check.
  Each one missing is a finding.
- [ ] RT4 — For each action, find its type, owner, due date and issue. Each one missing, or a bare "improve", is a
  finding.
- [ ] RT5 — In the retro, find a transcript or command cite for each number and each claim about what happened. A
  number with no cite, or a lesson from one instance that was not a rescue, revert or escaped defect, is a finding.
- [ ] RT6 — For each action of type rule, find why a structure, type, lint or test could not hold it. A rule for a
  mistake a lint or type could catch is a finding.
