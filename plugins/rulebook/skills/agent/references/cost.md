# Agent cost

How a run and a workspace stay inside their token and spend budgets, one call at a time and under concurrent runs.
Read it when you write or review a run budget, a workspace or tenant budget, a spend limit, or the code that checks
or records usage around a model call.

Contents: Rules · When X, use Y · Good / Bad (AEN6) · Decided edges · Review checks

## Rules

- **AE51** — Check run and workspace budgets before each model call and settle them from actual usage after each
  response, ending the turn with a typed reason, because per-turn estimates let concurrent runs overspend.
- **AEN6** — Reserve each call's maximum cost in a shared workspace counter with one atomic step before the call,
  and settle it from actual usage after, because concurrent runs that check then record all pass together.

## When X, use Y

| situation | use | why |
|---|---|---|
| a run or a workspace has a budget | a check before each model call and a settlement from actual usage after it | per-turn estimates let concurrent runs overspend (AE51) · the crossing response: LS6 (`testing`'s `llm-tests`) |
| a budget is crossed | the turn ends with a typed reason, such as `BudgetExceeded(WORKSPACE)` | the caller can tell a budget stop from a failure (AE51) |
| several runs share one workspace budget | an atomic reserve of the call's maximum cost in a shared store, then a settle | runs that each check, then record, all pass the check together (AEN6) |
| a caller may call the provider at all | a per-caller rate limit and quota, before any budget | that limit is SE8 (`code`'s `security`) |

## Good / Bad

### AEN6 — Reserve before the call, settle after

**Bad**
```java
if (budgets.spent(workspaceId) + estimate(request) > budgets.limit(workspaceId)) {
    return Outcome.stopped(StopCause.BUDGET_EXCEEDED);
}
final var reply = model.send(request);
budgets.record(workspaceId, pricing.cost(reply.servedModel(), reply.usage()));
```
Ten runs read the same `spent` value at once. All ten pass, and the workspace ends far over its limit.

**Good**
```java
final var reservation = budgets.reserve(workspaceId, pricing.maxCost(request));
if (reservation.isEmpty()) {
    return Outcome.stopped(StopCause.BUDGET_EXCEEDED);
}
try {
    final var reply = model.send(request);
    reservation.get().settle(pricing.cost(reply.servedModel(), reply.usage()));
    return Outcome.reply(reply);
} finally {
    reservation.get().releaseUnsettled();
}
```
`reserve` adds the call's maximum cost to the shared counter in one atomic step, or refuses. `settle` replaces the
reservation with the real cost, and a failed call gives its reservation back.

## Decided edges

- **Skip when** only one run can use a workspace at a time, enforced by a lock or a queue: a check before each call
  and a record after it meet AEN6. — **Do not skip when** two runs, workers or replicas can spend from the same
  budget. — **Confidence** high
- **Skip when** the response that crosses the budget has already arrived: keep it and count it (LS6), then stop
  before the next call. — **Do not skip when** the code drops or re-requests that response. — **Confidence** high

## Review checks

Walk every changed budget check, usage record and model call inside a run with a budget.

- [ ] AE51 — For each model call in a run with a budget, find the check before it and the settlement after it. A
  missing one, a check on an estimate that is never settled, or a stop with no typed reason is a finding.
  Applies when: a run or a workspace has a budget
  Evidence: the check and the settlement at `file:line`
  Not a finding: none
  Severity: Act on
  Verify: re-open each model call path, resume included
- [ ] AEN6 — Open the workspace budget store. A read-then-write check, or a counter held in one process while several
  processes spend from it, is a finding.
  Applies when: more than one run can spend from one budget
  Evidence: the reserve or check at `file:line`
  Not a finding: one run at a time per workspace (decided edge)
  Severity: Act on
  Verify: re-open the store's reserve and settle operations
