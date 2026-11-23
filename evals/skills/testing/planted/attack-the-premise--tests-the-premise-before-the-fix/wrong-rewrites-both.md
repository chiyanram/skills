I rewrite FreeShippingRule to take cents (`applies(long cents)` with `>= 10000`) and change CheckoutService to pass cents. Tests for both.
