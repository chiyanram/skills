# Agent cost

How a run and a workspace stay inside their token and spend budgets, one call at a time and under concurrent runs.
Read it when you write or review a run budget, a workspace or tenant budget, a spend limit, or the code that checks
or records usage around a model call.

## Rules

- Check run and workspace budgets before each model call, and settle them from actual usage after each response,
  because per-turn estimates let concurrent runs overspend. A crossed budget ends the turn with a typed reason, such
  as `BudgetExceeded(WORKSPACE)`, so the caller can tell a budget stop from a failure. The response that crossed it
  is kept and counted, and the run stops before the next call.
- Reserve each call's maximum cost in a shared workspace counter with one atomic step before the call, and settle it
  from actual usage after, because concurrent runs that each check, then record, all pass together. A failed call
  settles from the usage reported so far, zero when none was reported. A reservation expires after a set time, so a
  process that stops before it settles returns the reservation to the budget. When a lock or a queue lets only one
  run use a workspace at a time, a check before each call and a record after it are enough.
- Put a per-caller rate limit and quota in front of any budget: `code`'s `security` notes, Secrets. The test of the
  response that crosses a budget is in the `testing` skill's model-calls notes.

## Good / Bad

### Reserve before the call, settle after

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
} catch (final ModelError error) {
    reservation.get().settle(pricing.cost(request.model(), error.usageSoFar()));
    throw error;
}
```
`reserve` adds the call's maximum cost to the shared counter in one atomic step, or refuses. `settle` replaces the
reservation with the real cost; a failed call settles from the usage reported before it failed.

## Review

Walk every model call in a run with a budget, and the workspace budget store.

Each line is a finding, a blocker unless marked (warning).

- A model call with no budget check before it or no settlement after it, a check on an estimate that is never
  settled, or a stop with no typed reason.
- A read-then-write budget check, a counter held in one process while several processes spend from it, a failed call
  that does not settle from its usage so far, or a reservation with no expiry.
