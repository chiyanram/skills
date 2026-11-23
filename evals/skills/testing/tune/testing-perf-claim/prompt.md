---
description: A PR claims a cache makes lookups 2x faster from one run each. The skill should ask for repeated, alternating runs and an explanation of the number. Today's skill does not state this; it is expected to fail until PR 2 adds the perf note.
expected_outcome: The review does not accept 2x from one run each; it asks for repeated alternating runs with their spread and a reason for the number.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Review the evidence in this PR description. Is the speed-up shown?

> Adds a Caffeine cache in front of `CatalogClient.lookup`. Benchmark: before 412 ms, after 198 ms for 1000 lookups, measured on my laptop, one run each. So lookups are about 2x faster.
>
> ```java
> @Benchmark public void thousandLookups() { for (int i = 0; i < 1000; i++) client.lookup("isbn-" + (i % 50)); }
> ```
