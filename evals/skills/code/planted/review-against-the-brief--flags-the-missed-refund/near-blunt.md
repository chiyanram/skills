Blocker (AC2): the refund is dead code. After `markCancelled()`, `order.status() == OrderStatus.PAID` is never true.
