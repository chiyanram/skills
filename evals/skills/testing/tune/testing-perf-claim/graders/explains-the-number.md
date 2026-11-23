---
type: llm
---

Check: a measured number needs an explanation of why it is that number.

PASS if the review points out that the benchmark uses only 50 distinct keys, so almost every lookup is a cache hit, and asks for a realistic key spread or the hit rate.

FAIL if the review does not question why the result is 2x or does not mention the 50 repeated keys.
