---
description: A design adds an order record whose refund time may be set while the status is not cancelled, and a stored item count that the item list already decides. The design review should flag it under SR24.
expected_outcome: The order-record decision gets an open or conflict verdict that names both the forbidden combination and the stored copy, under SR24.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this design with crq before I approve it. Give every decision one verdict.

The spec's AC-1: "A customer can cancel an order until it ships; a shipped order cannot be cancelled."

The design:

```markdown
## Design
1. A new record `Order { id, items: List<Item>, itemCount: int, status: OPEN | SHIPPED | CANCELLED, refundedAt:
   Instant? }`, stored in the `orders` table. `itemCount` is set when the order is saved.
2. `OrderService.cancel(id)` sets `status = CANCELLED` and `refundedAt = now` unless the status is `SHIPPED`;
   `ShippingService.ship(id)` sets `status = SHIPPED` unless it is `CANCELLED`.
3. Alternative rejected: a separate cancellations table, because every read would need a join.
4. One slice: cancelling an unshipped order works and cancelling a shipped one is refused; proved by
   `./gradlew test --tests OrderServiceSpec`.
```
