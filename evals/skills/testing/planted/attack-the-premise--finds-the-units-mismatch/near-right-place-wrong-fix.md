The bug is in CheckoutService: use `BigDecimal.valueOf(cart.subtotalCents())` without any `movePointLeft`.
