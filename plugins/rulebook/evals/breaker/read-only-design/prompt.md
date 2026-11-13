---
description: A small read-only design that changes no state, calls nothing outside and takes no new input. The breaker should invent no unreachable scenario and leave the approval to the human.
expected_outcome: No blocker scenario; any scenario reported is reachable from the design; the report does not approve the design.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Try to break this design with crq before I approve it. Report each break scenario.

The spec's AC-1: "A member sees the due date of each book they have on loan, on the loans page."

The design:

```markdown
## Design
1. `LoansPage` shows `loan.dueDate()` for each loan the page already lists, formatted with the existing
   `DateFormats.shortDate` the other pages use.
2. No stored data, call or input changes: the page already loads the loans.
3. Alternative rejected: a separate due-dates page, because members look for it next to the loan.
4. One slice: the loans page shows each due date; proved by `./gradlew test --tests LoansPageSpec`.
```

The code at the default branch:

```java
// src/main/java/library/web/LoansPage.java
21 List<LoanView> loans = loanQueries.loansOf(memberId);
22 model.addAttribute("loans", loans);
```
