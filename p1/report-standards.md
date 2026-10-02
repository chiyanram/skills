# P1 Standards axis report (round 1, head 70b84c0b) — gist
1 [critical] AgentEntity.java:77 currentVersion = 1 → JPA writes 1, DB default 0 never applies (correctness lens).
2 [warning] V106:7,19 VARCHAR(n) on new columns — migrations.md "New string columns are TEXT".
3 [warning] V106:16 UPDATE with no predicate and no rationale comment — migration-review.md §4.
4 [nit] V106:3-4 header comment false (CHECK is a separate ALTER); NOT VALID skipped (judgement).
5 [warning] AgentEvalRunEntity.verdictReason String for a closed set — enums over string literals.
6 [warning] RunModeSpec "exhaustive" test: 2 rows for 3 cases, Groovy default branch — test-value-bar.
7 [warning] AlertTriggerTypeSpec `valueOf(x) != null` can never be false — test-value-bar junk test.
8 [nit] VersionedCertificationRefusalSpec builds its own JsonMapper, not the stream's.
9 [nit] AgentRuntimeConfig null→List.of() with no wire caller — types-and-null §4.
references used: migrations, migration-review, types-and-null, comments, test-value-bar, testing, java-standards
