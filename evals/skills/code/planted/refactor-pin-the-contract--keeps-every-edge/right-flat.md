```java
long shippingCostCents(final Order order) {
    final boolean de = order.country().equals("DE");
    final long total = order.totalCents();
    if (de && total >= 5000) {
        return 0;
    }
    if (de) {
        return order.express() ? 990 : 490;
    }
    if (order.express()) {
        return 1990;
    }
    return total > 10000 ? 0 : 1490;
}
```
