```java
long shippingCostCents(final Order order) {
    if (order.country().equals("DE")) {
        if (order.totalCents() >= 5000) {
            return 0;
        }
        return order.express() ? 990 : 490;
    }
    if (order.express()) {
        return 1990;
    }
    return order.totalCents() >= 10000 ? 0 : 1490;
}
```
