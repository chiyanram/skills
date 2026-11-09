---
description: A small, consistent design whose cites hold. The design review should mark every decision aligned and invent no blocking finding.
expected_outcome: Every decision is aligned; no conflict or open is raised; the review does not approve on the human's behalf.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this design with crq before I approve it. Give every decision one verdict.

The spec's AC-1: "A member name is stored without the spaces around it."

The design:

```markdown
## Design
1. Strip the value in the compact constructor of `MemberName` at `MemberName.java:6`, before the blank check, so
   every caller gets the stripped name.
2. Alternative rejected: strip in each controller, because three controllers create names and one would be missed.
3. No stored data changes: existing names are read as they are.
4. One slice: a padded name is stored stripped; proved by `./gradlew test --tests MemberNameSpec`.
```

The code at the default branch:

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
