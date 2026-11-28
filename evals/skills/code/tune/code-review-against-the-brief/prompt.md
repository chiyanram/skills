---
description: A diff that compiles and reads well but builds less than the ticket asks, and something it does not ask. The review should check the diff against each acceptance criterion and find the misread status rule and the refund that never happens. Today's skill has no step to review against the brief; the planned review pieces add it.
expected_outcome: The review finds that the guard blocks only SHIPPED although AC1 allows only PLACED and PAID, that the PAID check runs after markCancelled so no refund is created, and that the email is not in the ticket.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Review this diff against its ticket. List each finding with what you would ask the author to change.

Ticket: cancel an order.

- AC1: an order can be cancelled only while its status is `PLACED` or `PAID`.
- AC2: cancelling a `PAID` order creates a refund for the full amount.
- AC3: the cancel and the refund commit together.

`OrderStatus` is `PLACED`, `PAID`, `SHIPPED`, `DELIVERED`, `CANCELLED`. `Order.markCancelled()` sets the status to `CANCELLED`.

```diff
+    @Transactional
+    CancelOutcome cancel(final long orderId) {
+        final Order order = orders.findById(orderId).orElseThrow();
+        if (order.status() == OrderStatus.SHIPPED) {
+            return new CancelOutcome.TooLate();
+        }
+        order.markCancelled();
+        if (order.status() == OrderStatus.PAID) {
+            refunds.save(Refund.full(order));
+        }
+        mailer.sendCancellationEmail(order.customerEmail());
+        return new CancelOutcome.Cancelled(order.id());
+    }
```

The tests in the diff cancel a `PLACED` order and a `SHIPPED` order, and both pass.
