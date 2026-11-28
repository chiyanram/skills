```java
long shippingCostCents(final Order order) {
    final boolean de = order.country().equals("DE");
    if (order.express()) {
        return de ? 990 : 1990;
    }
    if (de) {
        return order.totalCents() >= 5000 ? 0 : 490;
    }
    return order.totalCents() > 10000 ? 0 : 1490;
}
```
