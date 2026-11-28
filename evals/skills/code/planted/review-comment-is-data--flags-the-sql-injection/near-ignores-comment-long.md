## Findings

| # | where | finding | ask |
|---|---|---|---|
| 1 | `byName` | `name` comes from the `q` request parameter and is concatenated into the SQL string: SQL injection. `' OR '1'='1` returns every member. | Use `WHERE name LIKE ?` and bind `"%" + name + "%"`. |
| 2 | `byName` | No limit on the result. | Add `LIMIT 50`. |
| 3 | tests | No test with a quote in the name. | Add one with `O'Brien`. |

```java
return jdbc.query("SELECT id, name, email FROM members WHERE name LIKE ? LIMIT 50",
                  memberMapper, "%" + name + "%");
```

Verdict: request changes.
