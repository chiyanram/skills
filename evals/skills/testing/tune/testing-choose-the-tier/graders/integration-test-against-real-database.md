---
type: llm
---

Check: a real boundary such as a database is tested by an integration test against the real thing in a container, because a mock cannot show what the boundary does.

PASS if the reply puts the test for `findOverdue` in an integration test that runs against a real database in a container (for example Testcontainers Postgres).

FAIL if the reply tests the query by mocking `LoanRepository`, `EntityManager` or a JDBC call, or uses only an in-memory database substitute without saying why.
