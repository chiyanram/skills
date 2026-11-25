# Break the design

How a design is attacked before approval: which failures to try, how to report each one, and how each one is closed.
Read it when you try to break a design before approval, or when you close the break scenarios it raised.

## Rules

- Walk the break catalogue below once over each design decision that changes state, calls another system or takes
  new input, and report each scenario the design leaves unhandled, because a design read only for compliance hides how
  it fails. A read that feeds a later write in the same request counts as a change of state.
- Report a scenario only when the design or today's code makes its trigger reachable, and cite the decision or the
  line, because an unreachable scenario spends the human's attention on nothing. A fault outside the product, such as
  the database losing a committed write, is out unless the design adds that dependency.
- Give each scenario its trigger, its chain of effects, the first sign a person sees, and the AC-n or decision it
  hits, because "this might fail" cannot be tested.
- Close each kept scenario in exactly one way, because an open scenario is forgotten by build time:
  - a failure AC, `AC-n — should <refusal or recovery> when <trigger>`, when the system must refuse or recover in a
    way a test can see;
  - a mitigation in the design, with the signal that shows it in production, when the fix is a shape: a key, a lock,
    a constraint, an order of steps;
  - a named accepted risk in the spec (the scenario, who accepts it, the sign to watch), when the fix costs more than
    the risk.
  A scenario whose closure the design already names is closed, if that closure covers the trigger.

## The break catalogue

| the decision | try |
|---|---|
| calls another system | it is down; it is slower than the timeout; it succeeds but the reply is lost; it returns an error the design does not name |
| retries a call, or reads from a queue | the same message twice; messages out of order; one message that always fails |
| reads a value and then writes on its result | two requests at the same time |
| takes new input, an endpoint or a permission | empty, at the maximum size, the wrong type, hostile text, a caller without the permission |
| changes stored data or a default | rows from before the change; the migration stops halfway; a rollback after new writes |
| depends on time or dates | another time zone; a daylight-saving change; the end of a month; clocks that differ between machines |
| handles a list, a page or a batch | an empty list; one ten times larger than today |
| ships with a deploy, a setting or a flag | the old and new version running at once; the setting missing on one machine |
| writes to two stores, or to a store and a message | the first write succeeds and the second fails |

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### A scenario names its trigger, chain and first sign

**Bad**
```text
S1 — The payment call might fail and cause problems.
```
No trigger, no effect, no sign. No one can write a test for it or decide if it matters.

**Good**
```text
S1 — hits decision 3, AC-2
  trigger:    the payment service charges the card, then the reply times out after 5 seconds
  chain:      the order stays unpaid; the customer pays again; the card is charged twice
  first sign: a support ticket about a double charge
  closure:    mitigation — send the order id as an idempotency key on every charge attempt
```
The trigger is reachable from decision 3, the effect is concrete, and the closure is one of the three kinds.

### Close each scenario in one way only

**Bad**
```text
S2 — two checkouts take the last item at the same time.
  closure: add a failure AC, and maybe a lock, or accept it if it is rare.
```
Three closures, none chosen. The implementer cannot tell what to build.

**Good**
```text
S2 — two checkouts take the last item at the same time.
  closure: failure AC — AC-5 — should refuse the second order when the last item was taken a moment before
```
One closure. A test now proves the refusal.

## Review

Walk every design decision, its row of the break catalogue, and the code it cites on the default branch.

Each line is a finding, a blocker unless marked (warning).

- A decision that changes state, calls out or takes input, with a scenario from its row the design does not handle.
- (warning) A reported scenario with no trigger, chain, first sign, or AC-n or decision it hits.
- A kept scenario with no closure, or more than one.
- (warning) A scenario with no cited decision or code line that makes its trigger reachable.
