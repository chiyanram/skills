```groovy
def "holds its values"() {
  given: def card = new MemberCard("m1", "Ann", 5)
  expect:
    card.memberId() == "m1"
    card.displayName() == "Ann"
    card.maxLoans() == 5
}
```
This takes the class to 100%.
