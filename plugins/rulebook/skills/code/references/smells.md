# Smells

The smell baseline every diff is reviewed against, and the shape and naming rules behind it. Read it when you write or
review production code in any language: the smell baseline, and the shape and naming rules behind it.

Contents: Rules · When X, use Y · Good / Bad (DS1, DS3) · Decided edges · Review checks

## Rules

- **DS11** — Review every diff against the When X, use Y baseline; report each hit
  as a labelled heuristic ("possible Feature Envy"); a documented repo rule overrides it, because a smell is a judgement
  call.
- **SM1** — Review against Fowler's 2e chapter-3 smells plus Kerievsky's Oddball Solution, Indecent Exposure and
  Conditional Complexity, skipping any a running gate fails, because a partial list lets known smells through
  unreviewed.
- **DS1** — Before you accept a change, look for a restructure that deletes a branch, mode or layer rather than moving
  it; a moved branch is a finding, because the copies of one rule diverge.
- **DS3** — Add no one-off `if` or second boolean to an existing flow; model the case as a sealed type, enum switch,
  table or state machine, because two flags that must agree drift apart.
- **DS4** — Remove a pass-through method, a single-caller wrapper or an adapter with one implementation, and apply the
  deletion test, because a pass-through adds a layer to trace and hides nothing.
- **FW8** — Cure a message chain with Hide Delegate and a middle man with Remove Middle Man only where it removes
  coupling at real call sites, because over-curing one smell creates the other.
- **DS6** — Add no parameter, config key, hook or pattern for a case no current caller has, because unused generality
  is complexity every later change must carry.
- **DS12** — Define a predicate or literal that encodes a rule (a prefix, a status, a limit) once and call it from every
  site, because copies of one rule change separately and disagree.
- **DS14** — Extract a shared helper only when the duplicate encodes one rule (DS12); leave two or three similar lines
  inline, because a helper serving unrelated callers grows a mode flag per caller.
- **DS2** — Treat a change that pushes a file past 1000 lines as a finding; decompose first unless a structural reason
  is stated, because a long file is hard to understand and review.
- **FW1** — Treat a constructor or method with more than 7 parameters as a finding: split the class or introduce a
  parameter object, because a long list is hard to call correctly and signals an over-busy object.
- **FW2** — Treat a boolean parameter that selects which operation runs as a finding: split it into two named methods
  or take a sealed or enum input, because callers cannot tell what true or false means.
- **FW5** — Extract a fragment you must read to understand into a method named for what it does; a comment explaining
  *what* is the cue, because a reader must work through it to learn what it does.
- **FW6** — When callers read two or more fields of one record to compute or check something, move that logic onto the
  record (records and values, not entities), because callers that decide put the record's behaviour elsewhere.
- **FW3** — Make a method that returns a value change no observable state, except a modifier returning its own outcome
  or a fluent `this`, because a hidden side effect makes call order and repeat calls matter.
- **NM1** — Name a variable, method or type for what it holds or does: no `data`, `result`, `temp`, `item`, no
  abbreviation beyond `id`, `url`, `api`, because an unrevealing name makes the reader trace the code.
- **NM2** — When no honest name comes for a method or type, split or reshape it as a
  design finding instead of inventing a vague name, because a name that will not come signals a murky design.
- **NM3** — Name a method that changes state for that change; a getter-shaped name (`get…`, `is…`) never writes,
  because a `get`-shaped name that also writes misleads the caller.
- **NM4** — Give one family of types one naming pattern and aligned method signatures (`*Outcome`, `*Port`), because a
  reader who learns one member should predict the rest; a mismatch reads as a difference.

## When X, use Y

The baseline (SM1): one row per smell. Report a hit as "possible <smell>" with its cure (DS11). Where a rule owns the
cure, the row points at it.

| the diff shows | use | why |
|---|---|---|
| a name that does not say what it holds or does | possible **Mysterious Name**: rename it (NM1, NM2) | an unrevealing name makes the reader trace the code |
| the same logic shape in two hunks or files | possible **Duplicated Code**: extract it when it is a rule (DS12), not otherwise (DS14) | copies of one rule change separately and disagree |
| a method that reads another object's data more than its own | possible **Feature Envy**: move the method to that data; for a record, FW6 | the behaviour sits away from the data it depends on |
| the same fields or parameters travelling together | possible **Data Clumps**: bundle them into one type | each site repeats the group and can drop or swap a member |
| a primitive or string standing for a domain concept | possible **Primitive Obsession**: give it its own small type (TY8, `types.md`) | same-typed values swap places and the concept's checks scatter |
| the same `switch` or `if` cascade on one type at several sites | possible **Repeated Switches**: one sealed type or one shared map (DS3) | a new case must be added at every site, and one gets missed |
| one logical change that edits many scattered files | possible **Shotgun Surgery**: gather what changes together into one module | a change that touches many files misses one |
| one module edited for several unrelated reasons | possible **Divergent Change**: split it so each part changes for one reason | unrelated changes collide in one module |
| a parameter, hook or abstraction that no current need uses | possible **Speculative Generality**: delete it (DS6) | unused generality is complexity every later change must carry |
| a caller walking `a.b().c().d()` | possible **Message Chains**: hide the walk behind one method (FW8) | the caller breaks when any link in the chain changes |
| a class or method that mostly delegates | possible **Middle Man**: call the real target (DS4, FW8) | a pass-through adds a layer to trace and hides nothing |
| a subclass or implementer that ignores most of what it inherits | possible **Refused Bequest**: drop the inheritance and use composition | the type claims a contract it does not keep |
| a function you must read to understand | possible **Long Function**: extract and name the fragment (FW5) | a reader must work through it to learn what it does |
| a long parameter list | possible **Long Parameter List**: more than 7 is FW1 | a long list is hard to call correctly |
| data that any code can write, such as a mutable static field | possible **Global Data**: give it one owner that controls writes | any code can change it, so no one can say who did |
| data that changes after it is set | possible **Mutable Data**: Encapsulate Variable, Remove Setting Method; a `final` field (TY4, `types.md`) | a value that changes later surprises code that read it earlier |
| a loop that computes a value | possible **Loops**: replace it with a pipeline (Replace Loop with Pipeline); the stream then only computes (JV3, `java.md`) | a pipeline names each step; a loop hides them in its body |
| a class or function that adds no meaning of its own | possible **Lazy Element**: inline it after the deletion test (DS4) | it adds a name to trace and hides nothing |
| a field set in some cases and empty in the others | possible **Temporary Field**: move it to the case that needs it (Extract Class, Introduce Special Case), as a sealed variant (DS3) | a reader cannot tell when the field is valid |
| a module that reads another module's internals | possible **Insider Trading**: Move Function or Move Field to cut the trade, or Hide Delegate | the two modules can no longer change apart |
| a class doing too much: many fields, many responsibilities | possible **Large Class**: Extract Class; a file past 1000 lines is DS2 | a long file is hard to understand and review |
| two types that do one job with different method names | possible **Alternative Classes with Different Interfaces**: align them (NM4) | a mismatch reads as a difference that is not there |
| a record or class whose callers decide from its fields | possible **Data Class**: move the logic onto it (FW6) | callers that decide put the record's behaviour elsewhere |
| a comment that explains what the code does | possible **Comments**: extract and name the fragment (FW5); comment rules are in `comments.md` | a name says it and cannot drift from the code |
| nested or compound conditionals | possible **Conditional Complexity**: model the cases (DS3); nesting is DS9 (`../../deslop/SKILL.md`) | two flags that must agree drift apart |
| one problem solved two different ways in one code base | possible **Oddball Solution**: keep one way (NM4) | a reader must learn both and guess which one applies |
| a class or method visible beyond the code that needs it | possible **Indecent Exposure**: narrow its visibility (SX14, `spring.md`) | every extra caller pins its shape |
| an unused private member or an unreachable branch | possible **Dead Code**: delete it (DS7, `../../deslop/SKILL.md`) | unused code misleads readers and must still be maintained |

## Good / Bad

Every rule's approved pair: [examples/smells.md](examples/smells.md).

### DS1 — Delete the branch, do not move it

**Bad**
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

**Good**
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

**Bad**
```java
public record LoanRequest(Member member, Book book, boolean reference, boolean interLibrary, LenderCode lender) {
}

public Loan checkout(final LoanRequest request) {
    if (request.interLibrary()) {
        return interLibraryLoan(request, request.lender());
    }
    if (request.reference()) {
        return readingRoomLoan(request);
    }
    return regularLoan(request);
}
```
Inter-library loans arrived as a second boolean plus a lender code that means something only when it is true. Nothing
stops a request with both flags set, or a lender code on a regular loan.

**Good**
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

## Decided edges

- **Skip when** a tool the project runs already fails the smell, such as a file-length or parameter-count gate: the
  gate reports it (SM1). — **Do not skip when** the tool only warns or does not run on that file: nothing enforces the
  smell there. — **Confidence** high
- **Skip when** a documented repo rule endorses what the baseline would flag: point to that rule, not the smell
  (DS11; one owner per fact). — **Do not skip when** the repo rule is not written down, or it and a rule here
  disagree: no file wins, and the disagreement is a bug fixed in the same change. —
  **Confidence** high
- **Skip when** a file past 1000 lines stays clearly organised for a structural reason stated in the change (DS2). —
  **Do not skip when** the reason is missing, or the file is in another language: one limit serves every language. —
  **Confidence** high
- **Skip when** the adapter sits on a module boundary, or on a boundary dependency a test fakes: it is a seam, not a
  pass-through (LY2, `services.md`). — **Do not skip when** it has one implementation, no fake and no
  module boundary (DS4). — **Confidence** high
- **Skip when** the logic decides across several objects: it goes in a decision class, not onto one record (FW6). —
  **Do not skip when** the logic reads one record only: it stays on that record. — **Confidence**
  high

## Review checks

Walk every hunk of every changed production source file in the diff.

- [ ] DS11, SM1 — Test each hunk against every row of When X, use Y: Fowler's 24 smells, the three Kerievsky smells and
  Dead Code. Report each hit as "possible <smell>" with the row's cure. A smell a project gate already fails is skipped
  (Decided edges).
- [ ] DS1 — For each new branch, mode or layer, look for a restructure that deletes it. A branch moved into a helper
  but still taken at each caller is a finding.
- [ ] DS3 — A new `if` or a new boolean added to an existing flow is a finding, unless the case is a sealed type, an
  enum switch, a table or a state machine.
- [ ] DS4 — For each method, wrapper or adapter that forwards a call, count its callers and implementations
  (`grep -rn`). One caller, or one implementation with no fake and no module boundary, is a finding.
- [ ] FW8 — For each Hide Delegate or Remove Middle Man fix, the cure removes coupling at real call sites. A cure that
  adds a new chain or a new pass-through is a finding.
- [ ] DS6 — A new parameter, config key, hook or pattern that no current caller uses is a finding.
- [ ] DS12 — For each predicate or literal that encodes a rule (a prefix, a status, a limit), grep for copies
  (`grep -rn '<literal>'`). A second definition is a finding.
- [ ] DS14 — A new shared helper whose callers share no rule, or that takes a mode argument, is a finding.
- [ ] DS2 — `wc -l` each changed file. A file the change pushes past 1000 lines with no stated structural reason is a
  finding.
- [ ] FW1 — A constructor or method with more than 7 parameters is a finding.
- [ ] FW2 — A boolean parameter that selects which operation runs is a finding.
- [ ] FW5 — A comment that explains what a fragment does, where the fragment is not extracted and named, is a finding.
- [ ] FW6 — A caller that reads two or more fields of one record to compute or check something is a finding, unless
  the logic spans several objects (Decided edges).
- [ ] FW3 — For each method that returns a value, look for a change of state. One found is a finding, unless the
  method is a modifier returning its own outcome or a fluent `this`.
- [ ] NM1 — A new name `data`, `result`, `temp` or `item`, or an abbreviation other than `id`, `url` or `api`, is a
  finding. A name that does not say what it holds or does is a finding.
- [ ] NM2 — A vague name on a method or type is a design finding: ask for a split or a reshape, not a new name.
- [ ] NM3 — A `get…` or `is…` method that writes state is a finding. A method that changes state under a name that does
  not say so is a finding.
- [ ] NM4 — For each new type, compare its name and method signatures with the other types in its family. A different
  pattern is a finding.
