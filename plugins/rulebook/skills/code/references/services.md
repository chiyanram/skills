# Services

Where a decision lives, when a class earns an interface, and what a single use-case method must hold together. Read it
when you write or review a controller, a service, an interface or a use case that makes two calls.

Contents: Rules · When X, use Y · Good / Bad (LY1, LY2) · Decided edges · Review checks

## Rules

- **LY1** — Keep a controller to binding, delegating and shaping the response; put any branch that chooses an outcome
  in a service, because logic in a controller cannot be tested without the web framework.
- **LY2** — Add an interface only where two implementations exist now, such as an adapter and a fake, or at a
  module boundary; else depend on the class, because a one-implementation interface is indirection without a seam.
- **LY3** — Put operations that must succeed or fail together, such as a change and its audit row, in one
  transactional use-case method, because two calls left to the caller let one commit without the other.
- **LYN1** — Return response DTOs from a controller, never persistence entities, because an entity in a response leaks
  every field it owns and ties the API to the schema.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a branch that chooses an outcome: a state check, or the order of calls | a service method that returns the outcome (LY1) | a service test reaches the decision without the web framework |
| a dependency with a production adapter and a test fake, or a type another module calls | an interface for the seam (LY2) | two implementations make the seam real |
| a class with one implementation | the concrete class, with no interface (LY2) | a one-implementation interface is indirection without a seam |
| operations that must succeed or fail together | one use-case method in one transaction (LY3) | two calls left to the caller let one commit without the other |
| a controller response | a response DTO, mapped from the entity (LYN1) | an entity leaks every field it owns and ties the API to the schema |

How a bean takes its dependencies (LY6) and binds its settings (LY7) is in `spring.md`.

## Good / Bad

### LY1 — A controller binds, delegates and shapes; a branch that chooses an outcome lives in a service

**Bad**
```java
@PostMapping("/books/{isbn}/loans")
public ResponseEntity<LoanResponse> borrow(
        @PathVariable final String isbn,
        @RequestBody final BorrowRequest request) {
    final var book = catalog.find(isbn);
    if (book.copiesOnShelf() == 0) {
        return ResponseEntity.status(HttpStatus.CONFLICT).build();
    }
    if (loans.countOpen(request.memberId()) >= MAX_OPEN_LOANS) {
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).build();
    }
    return ResponseEntity.ok(LoanResponse.of(loans.open(isbn, request.memberId())));
}
```
The controller decides whether a member may borrow. A test of that rule needs the web layer.

**Good**
```java
@PostMapping("/books/{isbn}/loans")
public ResponseEntity<LoanResponse> borrow(
        @PathVariable final String isbn,
        @RequestBody final BorrowRequest request) {
    return switch (lending.borrow(isbn, request.memberId())) {
        case BorrowOutcome.Lent lent -> ResponseEntity.ok(LoanResponse.of(lent.loan()));
        case BorrowOutcome.NoCopyOnShelf _ -> ResponseEntity.status(HttpStatus.CONFLICT).build();
        case BorrowOutcome.LoanLimitReached _ ->
                ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).build();
    };
}
```
The service checks the shelf and the loan limit and returns a sealed outcome. The exhaustive switch maps each case to
a status, which is shaping.

### LY2 — An interface only where two implementations exist now, or at a module boundary

**Bad**
```java
public interface LateFeeCalculator {
    Money feeFor(Loan loan, LocalDate returnedOn);
}

@Service
public class LateFeeCalculatorImpl implements LateFeeCalculator {
    @Override
    public Money feeFor(final Loan loan, final LocalDate returnedOn) {
        final long daysLate = Math.max(0L, ChronoUnit.DAYS.between(loan.dueOn(), returnedOn));
        return DAILY_FEE.times(daysLate);
    }
}
```
The calculator is pure arithmetic with one implementation, and no test fakes it. The interface is a seam that nothing
uses.

**Good**
```java
@Service
public class LateFeeCalculator {
    public Money feeFor(final Loan loan, final LocalDate returnedOn) {
        final long daysLate = Math.max(0L, ChronoUnit.DAYS.between(loan.dueOn(), returnedOn));
        return DAILY_FEE.times(daysLate);
    }
}
```
Tests call the concrete class with real loans. An interface stays for a boundary such as `MemberNotifier`, which has a
production adapter and a test fake.

## Decided edges

- **Skip when** the controller switches exhaustively over a sealed outcome the service returned: that switch is shaping,
  which is allowed (LY1). — **Do not skip when** the controller itself checks state or chooses the
  order of calls (LY1). — **Confidence** high

## Review checks

Walk every changed controller, service and interface.

- [ ] LY1 — For each controller method, list its `if`, `switch` and loop statements. A branch that chooses an outcome is
  a finding; an exhaustive `switch` over an outcome the service returned is not.
- [ ] LY2 — For each new or changed interface, find two implementations in the code now (a test fake counts) or a
  caller in another module. An interface with neither is a finding.
- [ ] LY3 — For each set of operations that must succeed or fail together, such as a change and its audit row, find one
  use-case method in one transaction. Two calls left to the caller, or two transactions, is a finding.
- [ ] LYN1 — List the entity classes (`grep -rlE "^\s*@Entity\b"`). A controller method whose return type is, holds
  or wraps one of them is a finding.
