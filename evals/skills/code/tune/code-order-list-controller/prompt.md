---
description: A controller returns JPA entities from an unbounded findAll. The review should flag both.
expected_outcome: The entity returned from the controller is reported (LYN1); the unbounded findAll is reported (PS6).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, review this order endpoint and list each rule it breaks, with the fix.

```java
@Entity
class Order {
    @Id Long id;
    String customerEmail;
    String internalNotes;
    BigDecimal total;
}

interface OrderRepository extends JpaRepository<Order, Long> {}

@RestController
@RequestMapping("/v1/orders")
class OrderController {
    private final OrderRepository orders;

    OrderController(final OrderRepository orders) {
        this.orders = orders;
    }

    @GetMapping
    List<Order> all() {
        return orders.findAll();
    }
}
```

The orders table grows by thousands of rows a day.
