---
description: A Spock spec that mocks the team's own class and verifies an internal call with a wildcard. The review should flag both.
expected_outcome: The review says to use the real DiscountRules (own class) and assert the price, and flags the wildcard argument.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing Review this spec before it merges. List each problem and the change you would ask for.

```groovy
class PriceCalculatorSpec extends Specification {
    def rules = Mock(DiscountRules)          // DiscountRules is our own class, pure logic
    def calculator = new PriceCalculator(rules)

    def "applies the member discount"() {
        when:
        calculator.price(new Basket(100.00), Member.gold())

        then:
        1 * rules.rateFor(_) >> 0.10
    }
}
```
