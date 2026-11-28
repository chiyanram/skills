---
type: llm
---

Check: when two same-typed parameters can swap, give them distinct types so a swap does not compile.

PASS if the review finds that `cancelAndRefund` passes `order.customerId` and `order.id` in swapped order, and asks for a type change that makes the swap a compile error: branded or distinct id types (`OrderId`, `CustomerId`), or one object argument with named fields.

FAIL if the review does not find the swapped arguments, or fixes only the order of the arguments in this call with no type change.
