---
description: A normal small feature. The implementer should give every AC an evidence row with a plain command, a test that fails on revert, and a PR body with PR1–PR7.
expected_outcome: One evidence row per AC with a plain re-runnable command; a test that fails on revert; a PR body with reason and spec link, evidence table, breaking change, rollback, file tree and where to look.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, build this approved spec as the implementer. Show the change you would commit, the evidence rows and
the PR body.

Approved spec (`specs/member-name-strip.md`):
- AC-1: A member name is stored without the spaces around it.
- AC-2: A name of only spaces is still rejected.

The code at the branch head:

```java
// src/main/java/library/MemberName.java
5  public record MemberName(String value) {
6      public MemberName {
7          Objects.requireNonNull(value, "value");
8          if (value.isBlank()) {
9              throw new IllegalArgumentException("a member name is not blank");
10         }
11     }
12 }
```

Tests run with `./gradlew test --tests MemberNameSpec`.
