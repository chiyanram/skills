---
description: A branch wraps a repository save in a catch that logs and continues, and leaves a commented-out block. The pass should report the catch and remove the commented-out code.
expected_outcome: The silencing catch is reported, not fixed (DS8); the commented-out block is removed or reported (DS7).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/shop/StockService.java
+++ b/src/main/java/shop/StockService.java
@@ -18,7 +18,15 @@ final class StockService {
     void reserve(final Sku sku, final int quantity) {
         final Stock stock = stocks.get(sku);
-        stocks.save(stock.reserve(quantity));
+        // final Stock checked = stock.checkAvailable(quantity);
+        // stocks.save(checked);
+        try {
+            stocks.save(stock.reserve(quantity));
+        } catch (final RuntimeException e) {
+            log.warn("could not reserve {}", sku, e);
+        }
     }
```

`stocks` is a constructor-injected `StockRepository`.
