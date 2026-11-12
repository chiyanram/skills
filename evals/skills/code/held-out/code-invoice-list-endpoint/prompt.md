---
description: A new list endpoint could return every invoice and carry no version in its path. The written code should paginate and version it.
expected_outcome: The endpoint is paginated with a default and maximum page size (AP1); the path carries /v1 (AP6).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, write the controller for a new endpoint that lists a customer's invoices. Show the code and say which rules you applied.

```java
record InvoiceSummary(String id, String number, BigDecimal total, Instant issuedAt) {}

interface InvoiceQueries {
    List<InvoiceSummary> forCustomer(String customerId, int limit, String after);
}
```

The invoices service has not been released yet, and a customer can have tens of thousands of invoices.
