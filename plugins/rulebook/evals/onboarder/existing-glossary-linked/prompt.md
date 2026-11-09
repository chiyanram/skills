---
description: A repo that already has a glossary file. The onboarder should link it, not copy its definitions.
expected_outcome: The brief or glossary.md links CONTEXT.md for the terms it defines; no definition from it is copied word for word.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, write this project's glossary.md, as the onboarder.

```markdown
<!-- CONTEXT.md in the product repo -->
# Context
**Loan**: one book lent to one member, from checkout to return.
_Avoid_: borrowing, rental
**Hold**: a member's place in the queue for a book that is out.
_Avoid_: reservation, booking
```

The code also uses the type `FineSchedule` (in `library/fines/FineSchedule.java`), which CONTEXT.md does not define.
