# Break the design

How a design is attacked before approval: which failures to try, how to report each one, and how each one is closed.
Read it when you try to break a design before the approval gate, or when you close the break scenarios it raised.

Contents: Rules · When X, use Y · Good / Bad (BK2, BK3) · Decided edges · Review checks

## Rules

- **BK1** — Walk the break catalogue once over each design decision that changes state, calls another system or takes
  new input, and report each unhandled scenario, because a design read only for compliance hides how it fails.
- **BK2** — Give each scenario a trigger, its chain of effects, the first sign a person sees, and the AC-n or decision
  it hits, because a vague "this might fail" cannot be tested.
- **BK3** — Close each kept scenario in one way: a failure AC, a design mitigation, or a risk the human accepts by
  name, because an open scenario is forgotten by build time.
- **BK4** — Report a scenario only when the design or today's code makes its trigger reachable, and cite it, because
  an unreachable scenario spends the human's attention on nothing.

## When X, use Y

The break catalogue. For each decision that matches a situation, try every scenario in its row (BK1).

| the decision | try | why |
|---|---|---|
| calls another system | it is down; it is slower than the timeout; it succeeds but the reply is lost; it returns an error the design does not name | a call across a network fails in more ways than "error" |
| retries a call, or reads from a queue | the same message arrives twice; messages arrive out of order; one message always fails | a retry without a key repeats the side effect |
| reads a value and then writes on its result | two requests do it at the same time | check-then-act loses an update or books one thing twice |
| takes new input, an endpoint or a permission | empty, at the maximum size, the wrong type, hostile text, a caller without the permission | each input is a trust boundary (SR13) |
| changes stored data or a default | rows from before the change; the migration stops halfway; a rollback after new writes | new-row tests only test the default |
| depends on time or dates | another time zone; a daylight-saving change; the end of a month; clocks that differ between machines | a date rule that holds today breaks on one day a year |
| handles a list, a page or a batch | the list is empty; it is ten times larger than today | an unbounded read is fast until it is not |
| ships with a deploy, a setting or a flag | the old and the new version run at the same time; the setting is missing on one machine | a rolling deploy runs both versions |
| writes to two stores, or to a store and a message | the first write succeeds and the second fails | half a change is worse than none |

| a kept scenario | close it with | why |
|---|---|---|
| the system must refuse or recover in a way a test can see | a failure AC: `AC-n — should <refusal or recovery> when <trigger>` (GA5, GA6) | a test then proves the failure path |
| the fix is a shape: a key, a lock, a constraint, an order of steps | a mitigation in the design, with the signal that shows it in production (SR11, SR18) | the implementer builds it and review checks it |
| the cost of the fix is higher than the risk | a named accepted risk in the spec: the scenario, who accepts it, and the sign to watch | the human decides, and the record shows it |

## Good / Bad

Every pair uses one domain: an online shop's orders and payments.

### BK2 — A scenario names its trigger, chain and first sign

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

### BK3 — Close each scenario in one way only

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

## Decided edges

- **Skip when** the decision only reads data and calls nothing (no state change, no call, no new input). — **Do not
  skip when** the read feeds a later write in the same request. — **Confidence** high
- **Skip when** the design already names the scenario and its closure. — **Do not skip when** the named closure does
  not cover the trigger, such as a retry with no key. — **Confidence** high
- **Skip when** the scenario needs a fault outside the product, such as the database losing a committed write. — **Do
  not skip when** the design adds the dependency that fails. — **Confidence** medium

## Review checks

Walk: every design decision, its row of the break catalogue, and the code it cites at the default branch.

- [ ] BK1 — For each decision that changes state, calls another system or takes new input, try every scenario in its
  catalogue row; a scenario the design does not handle is a finding.
  Applies when: a design decision changes state, calls another system or takes new input
  Evidence: the decision text, and the catalogue row it matched
  Not a finding: a read-only decision; a scenario the design already closes (decided edges)
  Severity: blocker when the scenario loses or corrupts data, moves money or crosses a trust boundary; warning otherwise
  Verify: re-open the decision and confirm the design does not handle the scenario
- [ ] BK2 — Each reported scenario has a trigger, a chain of effects, a first sign and the AC-n or decision it hits; a
  scenario without them is a finding against the report itself.
  Applies when: a break scenario is reported
  Evidence: the scenario as written
  Not a finding: none
  Severity: warning
  Verify: re-read the scenario's four fields
- [ ] BK3 — Each kept scenario has exactly one closure: a failure AC, a mitigation or an accepted risk; none, or more
  than one, is a finding.
  Applies when: a scenario is kept by the verify pass, and the design is revised for approval
  Evidence: the scenario, and the spec or design line that closes it
  Not a finding: none
  Severity: blocker
  Verify: open the spec and the design and find the one closing line
- [ ] BK4 — Each scenario cites the decision or the code line that makes its trigger reachable; a scenario with no
  reachable trigger is a finding against the report.
  Applies when: a break scenario is reported
  Evidence: the cited decision or code line
  Not a finding: a fault outside the product (decided edge)
  Severity: warning
  Verify: open the cite and follow the path to the trigger
