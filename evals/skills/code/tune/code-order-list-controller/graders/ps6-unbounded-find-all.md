---
type: llm
---

Check PS6: a query whose result grows with the data is bounded with a `Pageable`, `Limit` or SQL `LIMIT`, never `findAll()` as a `List`.

PASS if the review flags `findAll()` as loading the whole table and recommends a `Pageable` or limit.

FAIL if the unbounded `findAll()` is not flagged.
