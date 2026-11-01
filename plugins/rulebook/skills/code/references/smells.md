# Smells

The smell baseline every diff is reviewed against, and the shape and naming rules behind it. Read it when you write
or review production code in any language.

Contents: Rules · When X, use Y · Good / Bad (DS1, DS3) · Decided edges · Review checks

## Rules

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
- **NM3** — Name a method that changes state for that change; a getter-shaped name (`get…`, `is…`) never writes,
  because a `get`-shaped name that also writes misleads the caller.
- **NM4** — Give one family of types one naming pattern and aligned method signatures (`*Outcome`, `*Port`), because a
  reader who learns one member should predict the rest; a mismatch reads as a difference.

## When X, use Y

The baseline (SM1): one row per smell, with its cure. Where a rule owns the cure, the row points at it.

| the diff shows | use | why |
|---|---|---|
| a name that does not say what it holds or does | **Mysterious Name**: rename it (NM1) | mp :45 (r48 :529) |
| the same logic shape in two hunks or files | **Duplicated Code**: extract it when it is a rule (DS12), not otherwise (DS14) | mp :46 (r48 :492, :497) |
| a method that reads another object's data more than its own | **Feature Envy**: move the method to that data; for a record, FW6 | mp :47 (r48 :520) |
| the same fields or parameters travelling together | **Data Clumps**: bundle them into one type | mp :48 (r48 :454) |
| a primitive or string standing for a domain concept | **Primitive Obsession**: give it its own small type (TY8, `types.md`) | mp :49 (r48 :454) |
| the same `switch` or `if` cascade on one type at several sites | **Repeated Switches**: one sealed type or one shared map (DS3) | mp :50 (r48 :472) |
| one logical change that edits many scattered files | **Shotgun Surgery**: gather what changes together into one module | mp :51 (r48 :454) |
| one module edited for several unrelated reasons | **Divergent Change**: split it so each part changes for one reason | mp :52 (r48 :454) |
| a parameter, hook or abstraction that no current need uses | **Speculative Generality**: delete it (DS6) | mp :53 (r48 :487) |
| a caller walking `a.b().c().d()` | **Message Chains**: hide the walk behind one method (FW8) | mp :54 (r48 :482) |
| a class or method that mostly delegates | **Middle Man**: call the real target (DS4, FW8) | mp :55 (r48 :482) |
| a subclass or implementer that ignores most of what it inherits | **Refused Bequest**: drop the inheritance and use composition | mp :56 (r48 :454) |
| a function you must read to understand | **Long Function**: extract and name the fragment (FW5) | F 3 (r48 :454, :461) |
| a long parameter list | **Long Parameter List**: more than 7 is FW1 | F 4 (r48 :461) · CS ParameterNumber, SONAR S107 default 7 (r48 :507) |
| data that any code can write, such as a mutable static field | **Global Data**: give it one owner that controls writes | F 5 · LUZ 2e list (r48 :454) |
| data that changes after it is set | **Mutable Data**: Encapsulate Variable, Remove Setting Method; a `final` field (TY4, `types.md`) | F 6 · LUZ 2e list (r48 :454) |
| a loop that computes a value | **Loops**: replace it with a pipeline (Replace Loop with Pipeline); the stream then only computes (JV3, `java.md`) | F 13 · LUZ 2e list (r48 :454) |
| a class or function that adds no meaning of its own | **Lazy Element**: inline it after the deletion test (DS4) | F 14 · LUZ 2e list (r48 :454) |
| a field set in some cases and empty in the others | **Temporary Field**: move it to the case that needs it (Extract Class, Introduce Special Case), as a sealed variant (DS3) | F 16 (r48 :454) |
| a module that reads another module's internals | **Insider Trading**: Move Function or Move Field to cut the trade, or Hide Delegate | F 19 · LUZ 2e list (r48 :454) |
| a class doing too much: many fields, many responsibilities | **Large Class**: Extract Class; a file past 1000 lines is DS2 | F 20 (r48 :454) · 1000 lines (r48 :502) |
| two types that do one job with different method names | **Alternative Classes with Different Interfaces**: align them (NM4) | F 21 · MP, LUZ (r48 :539) |
| a record or class whose callers decide from its fields | **Data Class**: move the logic onto it (FW6) | F 22 (r48 :461) · PMD DataClass (r48 :520) |
| a comment that explains what the code does | **Comments**: extract and name the fragment (FW5); comment rules are in `comments.md` | F 24 · LUZ what-comment (r48 :516) |
| nested or compound conditionals | **Conditional Complexity**: model the cases (DS3); nesting is DS9 (`../../deslop/SKILL.md`) | Kerievsky per SM1; LUZ credits Steve Smith (2013) and maps it to Repeated Switching (r48 :455) |
| one problem solved two different ways in one code base | **Oddball Solution**: keep one way (NM4) | Kerievsky 2005 via LUZ (r48 :454) |
| a class or method visible beyond the code that needs it | **Indecent Exposure**: narrow its visibility | Kerievsky 2005 via LUZ (r48 :454) |
| an unused private member or an unreachable branch | **Dead Code**: delete it (DS7, `../../deslop/SKILL.md`) | SONAR S1144 · PMD UnusedPrivateMethod · CCJS (r48 :459) |

`mp` is mattpocock `skills/engineering/code-review/SKILL.md` (plugin 1.2.3). `F n` is _Refactoring_ 2e ch. 3 at
[InformIT](https://www.informit.com/articles/article.aspx?p=2952392), `seqNum=n`. `:N` is the line. `r48` is
agent-factory `research/48-industry-recheck-code.md` and `r48 :N` its line, where the source is quoted with the
repository path it was read at; source keys are those of r48's source table (r48 :363-383). Smell names checked
against refactoring.com; the 2e smell-to-cure pairs were not checked against the book text.

## Good / Bad

Every rule's approved pair: [examples/smells.md](examples/smells.md).

### DS1 — Delete the branch, do not move it

**Bad** (neutral)
```java
// OverdueReminder.java — the job decodes the sentinel …
final int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    log.debug("overdue_reminder customerId={} never_overdue — skipped", customer.id());
    continue;
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
// InvoicePreviewController.java — … and the preview decodes it again
int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    return new OverduePreview(customer.id(), 0, null, 0L);
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
```
The "0 means never overdue" rule and the cutoff arithmetic are written twice, so the preview can disagree with the job.

**Good** (neutral)
```java
public sealed interface GracePeriod {
    record NeverOverdue() implements GracePeriod {}
    record Days(int count) implements GracePeriod {}   // compact ctor rejects count <= 0, unchanged

    default Optional<Instant> overdueBefore(final Instant now) {
        return switch (this) {
            case NeverOverdue _ -> Optional.empty();
            case Days days -> Optional.of(now.minus(days.count(), ChronoUnit.DAYS));
        };
    }
}
// job:     period.overdueBefore(clock.instant()).ifPresent(cutoff -> remind(customer.id(), cutoff));
// preview: final long invoiceCount = period.overdueBefore(clock.instant())
//                  .map(cutoff -> invoiceRepository.countOpenDueBefore(customer.id(), cutoff))
//                  .orElse(0L);
```
The cutoff rule lives on the type, so both callers lose their branch instead of each switching on it. (Real evidence:
ledger row DS1. Pair: 68f § DS1 — Look for a restructure that deletes branches, not one that moves them.)

### DS3 — Model the case; add no second boolean

**Bad** (neutral)
```java
private void recordPaymentSafely(PaymentIds ids, GatewayExchange exchange, PaymentStatus status,
                                 boolean requiresReview, UUID reviewId,
                                 boolean sandbox, String sandboxSource) {
```
Sandbox mode arrived as a boolean plus a string that means something only when it is true. Review repeats that shape.

**Good** (neutral)
```java
sealed interface GatewayRun {
    record Live() implements GatewayRun {}
    record Sandbox(SandboxSource source) implements GatewayRun {}
}

sealed interface ReviewGate {
    record NotRequired() implements ReviewGate {}
    record Required(UUID reviewId) implements ReviewGate {}
}

record PaymentAttempt(PaymentIds ids, PaymentMethod method, GatewayExchange exchange, PaymentStatus status,
                      ReviewGate review, GatewayRun run) {
}

private void recordPaymentAttempt(final PaymentAttempt attempt) {
```
Each mode is a sealed case that carries only its own data, so a sandbox source or a review id cannot exist without its
mode. (Real evidence: ledger row DS3. Pair: 68f § DS3 — No one-off `if` or second boolean in a flow; model the case.)

## Decided edges

- **Skip when** a tool the project runs already fails the smell, such as a file-length or parameter-count gate: the
  gate reports it (SM1). — **Do not skip when** the tool only warns or does not run on that file: nothing enforces the
  smell there. — **Confidence** high (mp :41; r48 :454)
- **Skip when** a documented repo rule endorses what the baseline would flag: point to that rule, not the smell
  (SM1; one owner per fact). — **Do not skip when** the repo rule is not written down, or it and a rule here
  disagree: no file wins, and the disagreement is a bug fixed in the same change. —
  **Confidence** high (mp :40; r48 :450)
- **Skip when** a file past 1000 lines stays clearly organised for a structural reason stated in the change (DS2). —
  **Do not skip when** the reason is missing. — **Confidence** medium (the number 1000 comes from PS and ADDY, possibly
  one lineage; tools default to 750 and 2000, r48 :502-503)
- **Skip when** the adapter has a second implementation, such as a fake a test uses: two adapters make a real seam,
  not a pass-through (LY2, `services.md`). — **Do not skip when** it has one implementation and no fake (DS4). —
  **Confidence** high (MP codebase-design: one adapter means a hypothetical seam, r48 :477)

## Review checks

Walk every hunk of every changed production source file in the diff.

- [ ] SM1 — Test each hunk against every row of When X, use Y: Fowler's 24 smells, the three Kerievsky smells and Dead
  Code. Report each hit with the row's cure. A smell a project gate already fails is skipped (Decided edges).
- [ ] DS1 — For each new branch, mode or layer, look for a restructure that deletes it. A branch moved into a helper
  but still taken at each caller is a finding.
- [ ] DS3 — A new `if` or a new boolean added to an existing flow is a finding, unless the case is a sealed type, an
  enum switch, a table or a state machine.
- [ ] DS4 — For each method, wrapper or adapter that forwards a call, count its callers and implementations
  (`grep -rn`). One caller, or one implementation with no fake, is a finding.
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
- [ ] FW6 — A caller that reads two or more fields of one record to compute or check something is a finding.
- [ ] FW3 — For each method that returns a value, look for a change of state. One found is a finding, unless the
  method is a modifier returning its own outcome or a fluent `this`.
- [ ] NM1 — A new name `data`, `result`, `temp` or `item`, or an abbreviation other than `id`, `url` or `api`, is a
  finding. A name that does not say what it holds or does is a finding.
- [ ] NM3 — A `get…` or `is…` method that writes state is a finding. A method that changes state under a name that does
  not say so is a finding.
- [ ] NM4 — For each new type, compare its name and method signatures with the other types in its family. A different
  pattern is a finding.
