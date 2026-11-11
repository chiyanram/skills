---
description: The branch diff is clean, and a file outside it holds a commented-out block. The pass should leave that file alone and post its nothing-to-clean line.
expected_outcome: No edit to the file outside the diff; the report says there was nothing to clean in the diff.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With deslop, run the cleanup pass on this branch diff. Show each edit you would make and the report line you would post.

```diff
--- a/src/main/java/shop/OrderNumbers.java
+++ b/src/main/java/shop/OrderNumbers.java
@@ -5,6 +5,6 @@ final class OrderNumbers {
     String next(final long sequence) {
-        return "ORD-" + sequence;
+        return "ORD-%08d".formatted(sequence);
     }
```

While reading around, you see this in `src/main/java/shop/LegacyExport.java`, which the branch does not touch:

```java
    void export(final List<Order> orders) {
        // for (Order order : orders) {
        //     writer.write(order.toCsv());
        // }
        orders.forEach(order -> writer.write(order.toCsv()));
    }
```
