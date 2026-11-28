Escape single quotes in `name` with `name.replace("'", "''")` before it goes into the query, so a name like O'Brien works and cannot break out of the string.
