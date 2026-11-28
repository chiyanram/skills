The method compiles and the linter passes, so the reshape is safe to do directly.

## Result

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
    return order.totalCents() > 10000 ? 0 : 1490;
}
```

## Tests added after the change

| country | total | express | expected |
|---|---|---|---|
| DE | 5000 | yes | 0 |
| DE | 4999 | no | 490 |
| AT | 20000 | yes | 1990 |
| AT | 10000 | no | 1490 |
| AT | 10001 | no | 0 |

Complexity drops from nested `if`/`else` to guard clauses, and the behaviour is the same.
