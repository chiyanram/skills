AC2 is broken. Move `refunds.save(Refund.full(order))` above `order.markCancelled()`; today the `PAID` branch never runs, because the status is already `CANCELLED` when it is checked.
