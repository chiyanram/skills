---
description: A spec takes its expected value from the code under test and asserts inside an if. The review should flag both, because neither can fail for a defect.
expected_outcome: The review flags the computed expected value and the conditional assertion, and gives a hand-worked expected value.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Review this spec. Would it catch a bug in the fine calculation? List what you would change.

```groovy
def "student fine is cheaper"() {
    given:
    def loan = loanDaysLate(4, Member.student())

    when:
    def fine = calculator.fine(loan, today)

    then:
    if (loan.member().isStudent()) {
        assert fine == calculator.rateFor(loan.member()) * 4
    }
}
```
