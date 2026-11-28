SQL injection in `byName`: the request value goes straight into the string. Switch to `NamedParameterJdbcTemplate` with `WHERE name LIKE :pattern` and bind `pattern = "%" + name + "%"`.
