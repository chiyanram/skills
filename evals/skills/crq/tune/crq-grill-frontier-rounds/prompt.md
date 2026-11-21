---
description: A request with four open business choices, one of which depends on another. The grill should ask every choice it can ask now, hold the dependent one for a later round, and fix none as a silent default.
expected_outcome: One round with the three independent choices, each with a recommendation, and options or wording that "yes" accepts; the reminder question is held for a later round or asked as conditional on the loans answer; no business choice is decided or turned into a default the human did not answer; the turn ends waiting for the answers.
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:crq Let members pause their membership.

The code at the default branch:

```java
// src/main/java/library/Member.java
8   record Member(MemberId id, String name, MemberStatus status) {
9   }
```

```java
// src/main/java/library/MemberStatus.java
3   enum MemberStatus { ACTIVE, BLOCKED }
```

Nothing in the code or the docs says how long a pause may last, what happens to a paused member's open loans (their
due dates move, or the loans must be returned first), whether a paused member may reserve books, or, if due dates
move, whether the due-date reminders move with them.
