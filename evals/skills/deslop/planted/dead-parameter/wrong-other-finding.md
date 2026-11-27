Edit 1: replace the `for` loop in `sum` with `lines.stream().map(CartLine::amount).reduce(BigDecimal.ZERO, BigDecimal::add)`, which is shorter. Report: one style edit in `CartTotals.java`.
