## Step 1: pin today's results

Compiling and a passing linter say nothing about the results, so a test pins them first and runs green on the current code.

```java
@ParameterizedTest(name = "{0} {1} express={2} -> {3}")
@CsvSource({
    "DE, 4999, false, 490",
    "DE, 4999, true,  990",
    "DE, 5000, false, 0",
    "DE, 5000, true,  0",
    "AT, 20000, true, 1990",
    "AT, 10000, false, 1490",
    "AT, 10001, false, 0",
})
void keeps_todays_cost(final String country, final long total, final boolean express, final long expected) {
    assertThat(new ShippingCost().shippingCostCents(new Order(country, total, express))).isEqualTo(expected);
}
```

Run: 7 of 7 green on the current code.

## Step 2: reshape

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

## Step 3: run the same test

7 of 7 green. Cyclomatic complexity drops from 6 nested branches to flat guard clauses.

| input | before | after |
|---|---|---|
| DE 5000 express | 0 | 0 |
| DE 4999 standard | 490 | 490 |
| AT 20000 express | 1990 | 1990 |
| AT 10000 standard | 1490 | 1490 |
| AT 10001 standard | 0 | 0 |

The two thresholds differ (`>= 5000` and `> 10000`); they are kept as they are. Ask the product owner whether that is intended.
