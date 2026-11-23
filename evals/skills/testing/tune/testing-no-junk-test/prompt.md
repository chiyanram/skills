---
description: A request to raise coverage on a plain record. The skill should not add tests that cannot fail for a real defect, and should say why.
expected_outcome: No test of accessors or defaults; the reply explains that such tests protect no contract.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Coverage on this module is 61%. Add tests for `MemberCard` to bring it up. Show the spec you would add.

```java
record MemberCard(String memberId, String displayName, int maxLoans) {
    MemberCard {
        Objects.requireNonNull(memberId);
    }
    static MemberCard standard(final String memberId, final String displayName) {
        return new MemberCard(memberId, displayName, 5);
    }
}
```

Nothing else in the module reads `maxLoans` yet.
