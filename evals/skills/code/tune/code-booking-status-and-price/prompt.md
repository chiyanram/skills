---
description: A booking record uses a String status and a double price. The review should flag both.
expected_outcome: The String status is reported (TY6); the double price is reported (TY5).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, review this booking model and list each rule it breaks, with the fix.

```java
public record Booking(String id, String status, double price, String currency) {

    public boolean isActive() {
        return status.equals("CONFIRMED") || status.equals("PENDING");
    }

    public double withDeposit() {
        return price * 0.1;
    }
}
```

`status` is one of PENDING, CONFIRMED, CANCELLED and is stored in a column.
