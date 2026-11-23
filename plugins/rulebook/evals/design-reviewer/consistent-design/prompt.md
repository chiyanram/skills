---
description: A small, consistent design whose cites hold. The design review should mark every decision aligned and invent no blocking finding.
expected_outcome: Every decision is aligned; no conflict or open is raised; the review does not approve on the human's behalf.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this design with crq before I approve it. Give every decision one verdict.

The spec's AC-1: "The home page greets a member as `Hello, <name>!`, with no whitespace around the name, as Java's
`String.strip()` defines it." Out of scope: how names are stored. Assumptions: none beyond the cited code.

The design:

````markdown
## Design
1. In `Greeting.of(String name)` at `Greeting.java:4`, strip the name before formatting it, so a padded name no longer
   shows as `Hello,  Ann !`. No new type or signature, and no call path changes.
2. Alternative rejected: strip where the name is stored, because the spec puts how names are stored out of scope. We
   accept that other places that show a name may still show its whitespace, for a change that stays inside the spec.
3. Stored data: none changes; `Greeting` only builds a string. `Greeting` is package-private, and `HomePage.java:11` is
   its one user outside the class itself: `grep -rnw "Greeting" src/main` prints the declaration at `Greeting.java:3`
   and that one call. No new failure mode: the name is never null, because `MemberName.java:7` rejects a null value,
   and `strip()` throws nothing on a non-null string.
4. Refactor first: no. `Greeting` is one small class.
5. Files:
   ```diff
   ~ src/main/java/library/Greeting.java          strip the name in of()
   + src/test/groovy/library/HomePageSpec.groovy  new spec, two cases: " Ann " and "\u2003Ann\u2003" both show Hello, Ann!
   ```
   About 10 changed lines in 2 files.
6. One slice, for AC-1: the home page for a member whose name has whitespace around it shows `Hello, Ann!`, for ASCII
   spaces and for an EM SPACE that `trim()` would keep. Proved by `./gradlew test --tests HomePageSpec`, the new spec,
   which renders the page through `HomePage`. Manual: sign in as a member named " Ann " and read the greeting.
````

The code at the default branch:

```java
// src/main/java/library/Greeting.java
3  final class Greeting {
4      static String of(String name) {
5          return "Hello, " + name + "!";
6      }
7  }

// src/main/java/library/HomePage.java
11         model.put("greeting", Greeting.of(member.name().value()));

// src/main/java/library/MemberName.java
5  public record MemberName(String value) {
6      public MemberName {
7          Objects.requireNonNull(value, "value");
8          if (value.isBlank()) {
9              throw new IllegalArgumentException("a member name is not blank");
10         }
```

```text
$ grep -rnw "Greeting" src/main
src/main/java/library/Greeting.java:3:final class Greeting {
src/main/java/library/HomePage.java:11:        model.put("greeting", Greeting.of(member.name().value()));
```
