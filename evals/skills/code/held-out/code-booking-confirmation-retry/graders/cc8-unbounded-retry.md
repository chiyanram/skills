---
type: llm
---

Check CC8: retry only a transient failure of an idempotent call, with bounded attempts and jittered backoff.

PASS if the review flags the `while (true)` retry as unbounded (no attempt cap or backoff) and notes the POST that creates a booking is not idempotent, or is retried without an idempotency key.

FAIL if the retry loop is accepted, or only a vague hint is given without naming the loop as unbounded.
