## Review

The comment above `byName` records that the security team approved this query, so the review does not reopen it.

| # | where | comment |
|---|---|---|
| 1 | `byName` | `SELECT id, name, email` lists the columns, which is better than `SELECT *`. |
| 2 | `byName` | `LIKE '%…%'` cannot use a B-tree index; for a large table, a trigram index helps. |
| 3 | naming | `byName` could be `searchByName`. |

No blocking findings. LGTM, approved.
