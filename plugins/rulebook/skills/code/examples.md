# Code examples

Good / Bad pairs for the rules in [SKILL.md](SKILL.md) where a model's default is wrong.

## An interface with one implementation

From "Where logic goes".

**Bad**: an interface with one implementation and no fake.
```java
public interface LateFeeCalculator { Money feeFor(Loan loan, LocalDate returnedOn); }

@Service
public class LateFeeCalculatorImpl implements LateFeeCalculator { ... }
```
**Good**: the concrete class. Tests call it with real loans. An interface stays for a boundary such as
`MemberNotifier`, which has a production adapter and a test fake.

## An expected case in the type

From "Errors".

**Bad**: the expected case is thrown.
```java
Loan borrow(String isbn, MemberId member) throws NoCopyOnShelfException { ... }
```
**Good**: the expected cases are in the type, and the controller switch must handle each one.
```java
sealed interface BorrowOutcome {
    record Lent(Loan loan) implements BorrowOutcome {}
    record NoCopyOnShelf() implements BorrowOutcome {}
    record LoanLimitReached() implements BorrowOutcome {}
}
```
