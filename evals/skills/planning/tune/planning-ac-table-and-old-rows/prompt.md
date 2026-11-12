---
description: A draft spec adds a late-fee column to invoices with ACs that are three near-identical lines and only test new invoices. The review should ask for one AC with a table and an old-row AC.
expected_outcome: The review asks to merge the value-only ACs into one AC-n line with a table (GA4) and to add an AC that starts from an invoice stored before the change (AC7).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review the acceptance criteria of this draft spec and list your findings, then give the corrected ACs.

```text
Change: add a `late_fee_percent` column to the invoices table, default 2 for every invoice.

AC-1 — should charge a late fee of 2% when a new invoice of 100.00 is paid 1 day late
AC-2 — should charge a late fee of 2% when a new invoice of 500.00 is paid 10 days late
AC-3 — should charge no late fee when a new invoice of 100.00 is paid on time
```
