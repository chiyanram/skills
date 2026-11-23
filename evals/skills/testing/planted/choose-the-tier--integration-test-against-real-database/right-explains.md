The query is native SQL, so H2 or a mock could hide a dialect or null-handling difference. Put the spec in the integration source set with a Postgres Testcontainer and insert the rows directly.
