---
description: A new repository method with a native SQL date filter. The skill should put its test against the real database in a container, not a mock.
expected_outcome: An integration test against real Postgres in a container, with cases on both sides of the date edge.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Where should the test for this go, and what cases would you write? Sketch the spec.

```java
interface LoanRepository extends JpaRepository<Loan, Long> {
    @Query(value = "select * from loan where due_date < :today and returned_at is null", nativeQuery = true)
    List<Loan> findOverdue(@Param("today") LocalDate today);
}
```

The service tests mock `LoanRepository`. The project already uses Testcontainers for two other repositories.
