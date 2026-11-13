---
description: A design checks that a copy is free and then inserts a reservation, with no lock or constraint. The breaker should find two members reserving the last copy at once.
expected_outcome: A scenario for two reservations of the last copy at the same time, tied to decision 1, cited at the code, with one closure such as a failure AC or a unique constraint.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Try to break this design with crq before I approve it. Report each break scenario.

The spec's AC-1: "A member can reserve a copy of a book when a copy is free."
The spec's AC-2: "A member is told no copy is free when every copy is reserved."

The design:

```markdown
## Design
1. `ReservationService.reserve(memberId, bookId)` reads the free copies with
   `CopyRepository.findFreeCopies(bookId)`; when the list is not empty, it saves a `Reservation` for the first copy.
2. When the list is empty, it returns `NoCopyFree`.
3. Alternative rejected: a waiting list, because the library wants a direct answer.
4. One slice: reserve a free copy and refuse when none is free; proved by
   `./gradlew test --tests ReservationServiceSpec`.
```

The code at the default branch:

```java
// src/main/java/library/CopyRepository.java
12 @Query("select c from Copy c where c.book.id = :bookId and c.reservation is null")
13 List<Copy> findFreeCopies(BookId bookId);
```

```sql
-- src/main/resources/db/migration/V7__reservation.sql
1 create table reservation (
2   id uuid primary key,
3   copy_id uuid not null references copy(id),
4   member_id uuid not null
5 );
```
