## Review against the ticket

| # | criterion | finding | ask |
|---|---|---|---|
| 1 | AC2 | `order.markCancelled()` runs before `if (order.status() == OrderStatus.PAID)`. The status is already `CANCELLED` at that check, so the branch never runs and no refund is ever created. | Read the status before the change: `final boolean paid = order.status() == OrderStatus.PAID;` above `markCancelled()`, then refund when `paid`. |
| 2 | AC1 | The guard refuses only `SHIPPED`. AC1 allows a cancel only for `PLACED` and `PAID`, so a `DELIVERED` order, or an order already `CANCELLED`, is cancelled again. | Allow-list the two statuses: return `TooLate` unless the status is `PLACED` or `PAID`. |
| 3 | not in the ticket | `mailer.sendCancellationEmail(...)` is behaviour nobody asked for. It also runs inside the transaction, so a rollback after it still sends the email. | Remove it, or get it added to the ticket and send it after commit. |
| 4 | AC3 | Met: one `@Transactional` method holds the status change and the refund save. | none |

## Tests

The two tests cancel a `PLACED` and a `SHIPPED` order, so neither reaches finding 1 or 2. Ask for:

```java
@Test
void cancelling_a_paid_order_creates_a_full_refund() {
    final Order order = paidOrder(4_990);
    service.cancel(order.id());
    assertThat(refunds.findByOrderId(order.id())).hasValueSatisfying(r -> assertThat(r.cents()).isEqualTo(4_990));
}

@Test
void a_delivered_order_cannot_be_cancelled() {
    assertThat(service.cancel(deliveredOrder().id())).isInstanceOf(CancelOutcome.TooLate.class);
}
```

Verdict: request changes. Findings 1 and 2 break acceptance criteria.
