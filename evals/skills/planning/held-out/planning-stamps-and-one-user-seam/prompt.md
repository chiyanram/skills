---
description: A draft design carries confirmation stamps and a pluggable provider interface with one implementation. The review should flag both.
expected_outcome: The review flags the in-text verification stamps and asks for runnable cites (WD1), and flags the one-user abstraction (SR14).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review this draft design and list your findings.

```text
## Design: invoice export
Today the export job runs nightly [confirmed: checked by Sam, 2024-05-02] and writes one CSV per customer.

ExportFormatProvider (interface): format(invoice) -> bytes
CsvExportFormatProvider implements ExportFormatProvider   <- the only implementation
The provider interface lets us add PDF or XML export later if anyone asks.
```
