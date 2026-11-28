---
type: llm
---

Check: never silence the compiler with an `as` cast; type a value of unknown shape as `unknown` and parse it at the boundary.

PASS if the review flags `body as Order` because it checks nothing about the body, and asks to parse the body at the boundary with a schema (such as zod) or a type guard that checks each field.

FAIL if the review accepts the cast, asks only for a different cast or a non-null `!`, or does not mention `body as Order`.
