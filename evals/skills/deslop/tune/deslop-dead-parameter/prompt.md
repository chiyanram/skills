---
description: A branch adds a private helper with a parameter no caller uses. The pass should remove the parameter and change nothing else.
expected_outcome: The unused parameter is removed or reported as dead code; the computed total and every other line keep their behaviour.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/shop/CartTotals.java
+++ b/src/main/java/shop/CartTotals.java
@@ -12,6 +12,17 @@ final class CartTotals {
     BigDecimal total(final Cart cart) {
-        return cart.lines().stream().map(CartLine::amount).reduce(BigDecimal.ZERO, BigDecimal::add);
+        return sum(cart.lines(), Locale.ROOT);
+    }
+
+    private BigDecimal sum(final List<CartLine> lines, final Locale locale) {
+        BigDecimal total = BigDecimal.ZERO;
+        for (final CartLine line : lines) {
+            total = total.add(line.amount());
+        }
+        return total;
     }
```

`sum` has no other caller, and `locale` is read nowhere.
