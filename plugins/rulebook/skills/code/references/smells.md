# Smells

The smell baseline every diff is reviewed against, and the shape and naming rules behind it. Read it when you write or
review production code in any language: the smell baseline, and the shape and naming rules behind it.

Contents: Rules · When X, use Y · Good / Bad (DS1, DS3) · Decided edges · Review checks

## Rules

- **DS11** — Review every diff against the When X, use Y baseline; report each hit
  as a labelled heuristic ("possible Feature Envy"); a documented repo rule overrides it, because a smell is a judgement
  call.
- **SM1** — Take the baseline from Fowler and Beck's 24 smells (_Refactoring_ 2e, ch. 3), one line each in our
  words, and skip the ones a gate covers, because a 12-smell list misses half of them.
- **SM2** — Add Kerievsky's Conditional Complexity, Oddball Solution and Indecent
  Exposure to the baseline, because Fowler's 24 smells do not name these three.
- **SM3** — Treat Dead Code (an unused private member, an unreachable branch) as a baseline smell, because no gate or
  rule covers unused private members.
- **FW9** — Keep Long Function, Long Parameter List and Data Class in the baseline, because the 12-smell list it
  replaced misses Long Function.
- **DS1** — Before you accept a change, look for a restructure that deletes branches,
  modes or layers instead of moving them; kept incidental complexity is a finding, because a moved branch stays
  duplicated and the copies disagree.
- **DS3** — Add no one-off `if` or second boolean to an existing flow; model the case as a sealed type, enum switch,
  table or state machine, because a second boolean is synced by hand and drifts.
- **DS4** — Remove a pass-through method, a single-caller wrapper or an adapter with one implementation, and apply the
  deletion test, because a pass-through adds a layer to trace and hides nothing.
- **FW8** — Cure a message chain or a pass-through by Hide Delegate or Remove Middle Man, whichever removes coupling at
  real call sites; never add a wrapper then flag it, because each cure creates the other smell.
- **DS6** — Add no parameter, config, hook or pattern for a case that does not exist, and name the design pressure
  before you name a pattern, because added complexity compounds into every later change.
- **DS12** — Define a predicate or literal that encodes a rule (a prefix, a status, a limit) once and call it from every
  site, because copies of one rule drift apart.
- **DS14** — Extract a shared helper only when the duplicated thing is a rule (DS12),
  not for two or three similar lines, because a helper for unrelated callers grows a mode flag per caller.
- **DS2** — Treat a change that pushes a file over 1000 lines as a finding and
  decompose first (exception: Decided edges), because a reviewer misses a divergence inside a file too long to hold in
  mind.
- **FW1** — Treat a constructor with more than 7 collaborators as a finding: split the
  class (Extract Class) or bundle travelling values (Introduce Parameter Object), because a long constructor often
  signals an over-busy object.
- **FW2** — Treat a boolean parameter that selects which operation runs as a finding: split it into two named methods
  or take a sealed or enum input, because callers cannot tell what true or false means.
- **FW5** — Extract a fragment you must read to understand into a method named for what it does; a comment explaining
  *what* is the cue, because a reader must work through it to learn what it does.
- **FW6** — When callers read two or more fields of one record to compute or check something, move that logic onto the
  record (records and values, not entities), because callers that decide put the record's behaviour elsewhere.
- **FW3** — Make a method that returns a value change no observable state, except a modifier returning its own outcome
  (a compare-and-set result) or a fluent `this`, because only side-effect-free queries are safe in any order.
- **NM1** — Name a variable, method or type for what it holds or does: no `data`, `result`, `temp`, `item`, no
  abbreviation beyond `id`, `url`, `api`, because an unrevealing name makes the reader trace the code.
- **NM2** — When no honest name comes for a method or type, split or reshape it as a
  design finding instead of inventing a vague name, because a name that will not come signals a murky design.
- **NM3** — Name a method that changes state for that change; a getter-shaped name (`get…`, `is…`) never writes,
  because a `get`-shaped name that also writes misleads the caller.
- **NM4** — Give the types of one family one naming pattern and aligned method
  signatures (`CsvExporter`, `JsonExporter`), because inconsistent names in one family cost the reader a lookup each
  time.

## When X, use Y

The baseline: one row per smell. Report a hit as "possible <smell>" with its cure (DS11). Where a rule owns the cure,
the row points at it.

| the diff shows | use | why |
|---|---|---|
| a name that does not say what it holds or does | possible **Mysterious Name**: rename it (NM1, NM2) | mp :45 |
| the same logic shape in two hunks or files | possible **Duplicated Code**: extract it when it is a rule (DS12), not otherwise (DS14) | mp :46 |
| a method that reads another object's data more than its own | possible **Feature Envy**: move the method to that data; for a record, FW6 | mp :47 |
| the same fields or parameters travelling together | possible **Data Clumps**: bundle them into one type | mp :48 |
| a primitive or string standing for a domain concept | possible **Primitive Obsession**: give it its own small type (TY8, `types.md`) | mp :49 |
| the same `switch` or `if` cascade on one type at several sites | possible **Repeated Switches**: one sealed type or one shared map (DS3) | mp :50 |
| one logical change that edits many scattered files | possible **Shotgun Surgery**: gather what changes together into one module | mp :51 |
| one module edited for several unrelated reasons | possible **Divergent Change**: split it so each part changes for one reason | mp :52 |
| a parameter, hook or abstraction that no current need uses | possible **Speculative Generality**: delete it (DS6) | mp :53 |
| a caller walking `a.b().c().d()` | possible **Message Chains**: hide the walk behind one method (FW8) | mp :54 |
| a class or method that mostly delegates | possible **Middle Man**: call the real target (DS4, FW8) | mp :55 |
| a subclass or implementer that ignores most of what it inherits | possible **Refused Bequest**: drop the inheritance and use composition | mp :56 |
| a function you must read to understand | possible **Long Function**: extract and name the fragment (FW5) | F 3 |
| a long parameter list | possible **Long Parameter List**: for a constructor, FW1 | F 4 |
| data that any code can write, such as a mutable static field | possible **Global Data**: give it one owner that controls writes | F 5 |
| data that changes after it is set | possible **Mutable Data**: Encapsulate Variable, Remove Setting Method; a `final` field (TY4, `types.md`) | F 6 |
| a loop that computes a value | possible **Loops**: replace it with a pipeline (Replace Loop with Pipeline); the stream then only computes (JV3, `java.md`) | F 13 |
| a class or function that adds no meaning of its own | possible **Lazy Element**: inline it after the deletion test (DS4) | F 14 |
| a field set in some cases and empty in the others | possible **Temporary Field**: move it to the case that needs it (Extract Class, Introduce Special Case), as a sealed variant (DS3) | F 16 |
| a module that reads another module's internals | possible **Insider Trading**: Move Function or Move Field to cut the trade, or Hide Delegate | F 19 |
| a class doing too much: many fields, many responsibilities | possible **Large Class**: Extract Class; a file over 1000 lines is the DS2 operator preference | F 20 |
| two types that do one job with different method names | possible **Alternative Classes with Different Interfaces**: align them (NM4) | F 21 |
| a record or class whose callers decide from its fields | possible **Data Class**: move the logic onto it (FW6) | F 22 |
| a comment that explains what the code does | possible **Comments**: extract and name the fragment (FW5); comment rules are in `comments.md` | F 24 |
| nested or compound conditionals | possible **Conditional Complexity**: model the cases (DS3); nesting is DS9 (`../../deslop/SKILL.md`) | operator preference (SM2) |
| one problem solved two different ways in one code base | possible **Oddball Solution**: keep one way (NM4) | operator preference (SM2) |
| a class or method visible beyond the code that needs it | possible **Indecent Exposure**: narrow its visibility (SX14, `spring.md`) | operator preference (SM2) |
| an unused private member or an unreachable branch | possible **Dead Code**: delete it (DS7, `../../deslop/SKILL.md`) | SM3 · guru dead-code · simplification :152 |

`mp` is mattpocock `skills/engineering/code-review/SKILL.md` (plugin 1.2.3). `F n` is _Refactoring_ 2e ch. 3 at
[InformIT](https://www.informit.com/articles/article.aspx?p=2952392), `seqNum=n`. `guru` is
[refactoring.guru](https://refactoring.guru/refactoring/smells) and `simplification` is addy
`skills/code-simplification/SKILL.md`. `:N` is the line.
Smell names checked against refactoring.com; the 2e smell-to-cure pairs were not checked against the book text.

Operator preference, 2026-10-31 (SRC2), in whole or in part: DS11, SM2, DS1, DS14, DS2, FW1, NM2 and NM4.

## Good / Bad

Every rule's approved pair: [examples/smells.md](examples/smells.md).

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

## Decided edges

- **Skip when** a tool the project runs already fails the smell, such as a file-length or parameter-count gate: the
  gate reports it (SM1). — **Do not skip when** the tool only warns or does not run on that file: nothing enforces the
  smell there. — **Confidence** high (mp :41)
- **Skip when** a documented repo rule endorses what the baseline would flag: point to that rule, not the smell
  (DS11; one owner per fact). — **Do not skip when** the repo rule is not written down, or it and a rule here
  disagree: no file wins, and the disagreement is a bug fixed in the same change. —
  **Confidence** high (mp :40)
- **Skip when** a file over 1000 lines stays clearly organised for a structural reason stated in the change (DS2). —
  **Do not skip when** the reason is missing, or the file is in another language: one limit serves every language
  (operator preference, 2026-10-31). — **Confidence** high
- **Skip when** the adapter sits on a module boundary, or on a boundary dependency a test fakes: it is a seam, not a
  pass-through (LY2, `services.md`). — **Do not skip when** it has one implementation, no fake and no
  module boundary (DS4). — **Confidence** high (guru middle-man: a middle man that avoids a dependency may stay)
- **Skip when** the logic decides across several objects: it goes in a decision class, not onto one record (FW6). —
  **Do not skip when** the logic reads one record only: it stays on that record. — **Confidence**
  high

## Review checks

Walk every hunk of every changed production source file in the diff.

- [ ] DS11, SM1, SM2, SM3, FW9 — Test each hunk against every row of When X, use Y: the 24 Fowler smells, the three
  Kerievsky smells and Dead Code. Report each hit as "possible <smell>" with the row's cure. A smell a project gate
  already fails is skipped (Decided edges).
- [ ] DS1 — For each new branch, mode or layer, look for a restructure that deletes it. A branch moved into a helper
  but still taken at each caller is a finding.
- [ ] DS3 — A new `if` or a new boolean added to an existing flow is a finding, unless the case is a sealed type, an
  enum switch, a table or a state machine.
- [ ] DS4 — For each method, wrapper or adapter that forwards a call, count its callers and implementations
  (`grep -rn`). One caller, or one implementation with no fake and no module boundary, is a finding.
- [ ] FW8 — For each Hide Delegate or Remove Middle Man fix, the result adds no new chain and no new pass-through. A
  wrapper added and then flagged is a finding.
- [ ] DS6 — A new parameter, config key, hook or pattern that no current case uses is a finding. A pattern with no
  named design pressure is a finding.
- [ ] DS12 — For each predicate or literal that encodes a rule (a prefix, a status, a limit), grep for copies
  (`grep -rn '<literal>'`). A second definition is a finding.
- [ ] DS14 — A new shared helper whose callers share no rule, or that takes a mode argument, is a finding.
- [ ] DS2 — `wc -l` each changed file. A file the change pushes over 1000 lines with no stated structural reason is a
  finding.
- [ ] FW1 — A constructor with more than 7 parameters is a finding.
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
