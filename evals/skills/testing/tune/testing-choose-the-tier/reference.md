---
approved: operator
---

An integration test of `LoanRepository` against a real Postgres in a container (Testcontainers), because only the real database shows what the native query does; a mock cannot. Cases: a loan due yesterday and not returned (found), a loan due today (not found, the edge), a loan due tomorrow (not found), and a loan overdue but returned (not found). Expected rows are written out by hand.
