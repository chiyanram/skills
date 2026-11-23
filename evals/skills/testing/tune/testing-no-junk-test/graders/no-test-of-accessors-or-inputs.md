---
type: llm
---

Check: a test must be able to fail for a real defect; a test that asserts a field default or the input it just passed in cannot.

PASS if the reply adds no test that only reads back `memberId`, `displayName` or `maxLoans` after passing them in, and says that such tests protect nothing or cannot fail for a defect. A single test that a null `memberId` is rejected is allowed. A single test that `standard()` puts each argument in its own field is also allowed, because both are `String` and a swap compiles: it can fail for a real defect.

FAIL if the reply writes one or more tests that construct a `MemberCard` and assert its accessors return the passed-in values (other than that `standard()` argument-order test), or adds tests only to raise coverage without saying why they are worth it.
