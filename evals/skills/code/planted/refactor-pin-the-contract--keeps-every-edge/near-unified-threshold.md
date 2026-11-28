```java
long shippingCostCents(final Order order) {
    final boolean de = order.country().equals("DE");
    final long threshold = de ? 5000 : 10001;
    if ((de || !order.express()) && order.totalCents() >= threshold) {
        return 0;
    }
    if (de) {
        return order.express() ? 990 : 490;
    }
    return order.express() ? 1990 : 1490;
}
```
