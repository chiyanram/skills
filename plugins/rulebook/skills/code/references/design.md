# Design

The shape of a seam: what it takes, what it returns, where it decides and where it does I/O. Read it when you write
or review an interface a caller depends on, or a method that implements one.

## Rules

- **SEAM1** (operator preference, 2026-10-31) — Give every seam one job, a record in, a sealed result out, pure decisions, I/O that decides nothing
  and rule lists at cyclomatic complexity ≤5, because a branching method hides paths no test reaches.

## When X, use Y

| the seam has | use | why |
|---|---|---|
| more than one job | one seam per job (SEAM1) | a class has one job, one reason to change (pl121p Example 2); operator preference |
| an input | one record (SEAM1) | operator preference |
| an outcome to return | a sealed result (SEAM1); its caller switches over it with no `default` arm (TY2, `types.md`) | the compiler must fail when a new variant is not handled (pstack :20); the compiler confirms every permitted subclass is covered (JEP 409) |
| a decision to make | a pure function that calls no I/O (SEAM1) | isolate side effects at the edges (pl142 :740); return results, do not produce side effects (mattpocock `codebase-design/SKILL.md` :83) |
| I/O to do | a method that does the I/O and chooses no outcome (SEAM1) | isolate side effects at the edges (pl142 :740) |
| a choice among several cases | a rule list, not an if-ladder; each method at cyclomatic complexity ≤5 (SEAM1) | operator preference |
| a value that may be absent | `Optional`, a sealed type or an enum (TY1, `types.md`) | a bag of optional fields lets contradictory combinations compile (pstack :15) |
| code to check for smells | the smell baseline in `smells.md` | one smell list for the rulebook |

`pstack` is cursor-plugins pstack `skills/principle-type-system-discipline/SKILL.md`. `pl121p` is plinth
`121-java-object-oriented-design-principles.md` and `pl142` is plinth `142-java-functional-programming.md`. `:N` is
the line. The sealed result and the pure decision are industry rules; the other SEAM1 parts are operator preference.

## Good / Bad

SEAM1 has no approved pair. The pair for an absent value is TY1, and the pair for a sealed shape is TY3, both in
`types.md`.

## Decided edges

- **Skip when** the build already fails on cyclomatic complexity (for example a Checkstyle `CyclomaticComplexity`
  check): leave that count to the gate. — **Do not skip when** no gate measures it: count the
  branches of each changed method by hand. — **Confidence** high
- **Skip when** a project states its own seam rules: point to them and do not copy them here (one owner per fact). — **Do not skip when** a project rule and SEAM1 disagree: no file wins, and the disagreement is a
  bug fixed in the same change. — **Confidence** high

## Review checks

Walk every changed interface that a caller depends on, and every method that implements one.

- [ ] SEAM1 — Check each item the rule names. A seam with more than one job is a finding. An input that is not one
  record is a finding. An outcome returned as anything but a sealed result is a finding. A decision method that
  calls I/O is a finding, and so is an I/O method that chooses an outcome. An if-ladder where a rule list fits is a
  finding. A method above cyclomatic complexity 5, where no gate counts it, is a finding.
