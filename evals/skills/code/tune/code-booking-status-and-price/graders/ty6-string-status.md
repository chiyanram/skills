---
type: llm
---

Check TY6: a closed set of states is an enum, never a `String` or `int` constant.

PASS if the review flags `status` as a `String` holding a closed set and recommends an enum.

FAIL if the string status is accepted or not mentioned.
