---
approved: operator
---

Do not add tests that read back the accessors or the fields just passed in, because they cannot fail for a defect. At most two tests are worth writing: `requireNonNull` rejects a null `memberId`, and, if wanted, `standard()` keeps `memberId` and `displayName` in their own fields, because both are `String` and a swap compiles. A test that the default `maxLoans` is 5, kept only if 5 is a written requirement, is also allowed. The reply says that coverage alone is not a reason to add a test.
