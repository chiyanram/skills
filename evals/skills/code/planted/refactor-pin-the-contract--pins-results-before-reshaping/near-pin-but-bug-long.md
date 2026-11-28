## Step 1: pin

A parameterized test of today's results comes first and runs green on the current code:

| country | total | express | expected |
|---|---|---|---|
| DE | 4999 | no | 490 |
| DE | 5000 | no | 0 |
| AT | 10000 | no | 1490 |
| AT | 10001 | no | 0 |

## Step 2: reshape

```java
long shippingCostCents(final Order order) {
    final boolean domestic = order.country().equals("DE");
    final boolean free = domestic ? order.totalCents() >= 5000 : order.totalCents() > 10000;
    if (free) {
        return 0;
    }
    if (domestic) {
        return order.express() ? 990 : 490;
    }
    return order.express() ? 1990 : 1490;
}
```

## Step 3

The four pinned cases stay green. The method has one free-shipping rule and one price table.
