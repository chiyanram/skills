# Smells — Good / Bad examples

Every approved Good/Bad pair for the smells rules, one per rule that can be misread. The rules, the baseline and the
review checks are in [`../smells.md`](../smells.md). Each pair is in one neutral domain (a lending library: members,
books and loans). The other rules state themselves and have no pair.

Contents: DS1 · DS3 · DS4 · DS12 · DS14

### DS1 — Delete the branch, do not move it

**Bad** (neutral)
```java
// CheckoutService.java
if (policy.isOpenEnded(member)) {
    return Loan.openEnded(member.id(), book.id());
}
return Loan.due(member.id(), book.id(), today.plusDays(policy.loanDays(member)));

// RenewalService.java
if (policy.isOpenEnded(member)) {
    return loan;
}
return loan.withDueDate(today.plusDays(policy.loanDays(member)));
```
The open-ended check moved into `LoanPolicy`, but each caller still branches on it. A third caller must remember the
branch, and the copies can disagree.

**Good** (neutral)
```java
public sealed interface LoanTerm {
    record OpenEnded() implements LoanTerm {}
    record Days(int count) implements LoanTerm {}

    default DueDate dueFrom(final LocalDate start) {
        return switch (this) {
            case OpenEnded _ -> new DueDate.None();
            case Days days -> new DueDate.On(start.plusDays(days.count()));
        };
    }
}
// DueDate is sealed: None() or On(LocalDate date).
// checkout: return new Loan(member.id(), book.id(), member.term().dueFrom(today));
// renewal:  return loan.withDue(member.term().dueFrom(today));
```
The term decides the due date once. Both callers lose their branch instead of each one taking it.

### DS3 — Model the case; add no second boolean

**Bad** (from martinfowler.com bliki FlagArgument, adapted)
```java
public Loan checkout(Member member, Book book, boolean isReference, boolean isInterLibrary, String lenderCode) {
    if (isInterLibrary) {
        return interLibraryLoan(member, book, lenderCode);
    }
    if (isReference) {
        return readingRoomLoan(member, book);
    }
    return regularLoan(member, book);
}
// caller: checkout(member, book, false, true, "N12");
```
Inter-library loans arrived as a second boolean plus a string that means something only when it is true. The caller
cannot tell what `false, true` means.

**Good** (neutral)
```java
public sealed interface LoanKind {
    record Regular() implements LoanKind {}
    record ReadingRoom() implements LoanKind {}
    record InterLibrary(LenderCode lender) implements LoanKind {}
}

public Loan checkout(final LoanRequest request) {
    return switch (request.kind()) {
        case LoanKind.Regular _ -> regularLoan(request);
        case LoanKind.ReadingRoom _ -> readingRoomLoan(request);
        case LoanKind.InterLibrary interLibrary -> interLibraryLoan(request, interLibrary.lender());
    };
}
```
Each kind is a sealed case that carries only its own data. A lender code cannot exist without an inter-library loan.

### DS4 — Remove the pass-through; apply the deletion test

**Bad** (from refactoring.com catalog Remove Middle Man, adapted)
```java
public final class Member {
    private final Branch branch;

    public Librarian librarian() { return branch.librarian(); }
    public OpeningHours openingHours() { return branch.openingHours(); }
    public Address returnAddress() { return branch.returnAddress(); }
}
// caller
final var librarian = member.librarian();
```
`Member` forwards three calls to `Branch` and adds nothing. Each new `Branch` query adds one more forward to trace.

**Good** (from refactoring.com catalog Remove Middle Man, adapted)
```java
public record Member(MemberId id, Branch branch) {
}
// caller
final Librarian librarian = member.branch().librarian();
```
The forwards are deleted. The caller asks the branch directly, and `Member` changes only for member data.

### DS12 — Define the rule once, call it everywhere

**Bad** (neutral)
```java
// OverdueNotifier.java
if (loan.dueDate().isBefore(today.minusDays(3))) {
    notifier.remind(loan);
}
// FineCalculator.java
final var overdue = loan.dueDate().plusDays(3).isBefore(today);
// BorrowingLimit.java
final var overdueCount = loans.stream().filter(loan -> today.isAfter(loan.dueDate().plusDays(2))).count();
```
"What counts as overdue" lives at three sites that already disagree: the limit uses two grace days, the others three.

**Good** (neutral)
```java
public record Loan(LoanId id, MemberId member, String title, LocalDate dueDate) {
    private static final int GRACE_DAYS = 3;

    public boolean isOverdueOn(final LocalDate today) {
        return today.isAfter(dueDate.plusDays(GRACE_DAYS));
    }
}
// OverdueNotifier: if (loan.isOverdueOn(today)) { notifier.remind(loan); }
// FineCalculator:  final boolean overdue = loan.isOverdueOn(today);
// BorrowingLimit:  final long overdueCount = loans.stream().filter(loan -> loan.isOverdueOn(today)).count();
```
The rule has one home. A change to the grace period is one edit, and every site learns it.

### DS14 — No shared helper for lines that share no rule

**Bad** (neutral)
```java
static String notice(final String kind, final Member member, final String title, final LocalDate date) {
    final var greeting = "Dear " + member.name() + ",";
    if ("overdue".equals(kind)) {
        return greeting + " please return " + title + " (due " + date + ").";
    }
    return greeting + " " + title + " is ready to collect until " + date + ".";
}
```
Two messages that share a greeting get one "shared" helper. It needs a mode argument at once and grows one branch per
new notice.

**Good** (neutral)
```java
// OverdueReminder — its wording follows the lending policy
static String reminderText(final Member member, final Loan loan) {
    return "Dear %s, please return %s (due %s).".formatted(
        member.name(),
        loan.title(),
        loan.dueDate());
}

// HoldNotice — its wording follows the reservation policy
static String readyText(final Member member, final Hold hold) {
    return "Dear %s, %s is ready to collect until %s.".formatted(
        member.name(),
        hold.title(),
        hold.collectBy());
}
```
The two texts stay apart. They look alike, but each one changes for a different reason.
