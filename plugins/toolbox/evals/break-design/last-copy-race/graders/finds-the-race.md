---
type: llm
---

Decision 1 reads the free copies and then saves a reservation. Two requests for the last copy can both read it as
free and both save. The `reservation` table has no unique constraint on `copy_id`, so the database does not stop it.

PASS if the report has a scenario for two members reserving the last copy at the same time, ties it to decision 1 or
AC-1/AC-2, and cites the read-then-write or the missing constraint (the repository query or the migration).

FAIL if the race is not reported, or the scenario names no trigger and no cite.
