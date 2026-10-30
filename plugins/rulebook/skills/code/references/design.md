# Design

The shape of a seam: what it takes, what it returns, where it decides and where it does I/O. Read it when you write
or review an interface a caller depends on, or a method that implements one.

## Rules

- **SEAM1** — Give every seam one job, a record in, a sealed result out, pure decisions, I/O that decides nothing
  and rule lists at cyclomatic complexity ≤5, because a branching method hides paths no test reaches.

## When X, use Y

| the seam has | use | why |
|---|---|---|
| more than one job | one seam per job (SEAM1) | "one job" (ledger :133) |
| an input | one record (SEAM1) | "typed in and out (record in, sealed out)" (ledger :133) |
| an outcome to return | a sealed result (SEAM1); its caller switches over it with no `default` arm (TY2, `types.md`) | "seams chain by exhaustive switch over the previous seam's sealed result" (ledger :133) |
| a decision to make | a pure function that calls no I/O (SEAM1) | "decide or do (pure decision vs one-statement I/O)" (ledger :133) |
| I/O to do | a method that does the I/O and chooses no outcome (SEAM1) | "decide or do" (ledger :133) · "I/O decides nothing" (agent-factory#21 Q3) |
| a choice among several cases | a rule list, not an if-ladder; each method at cyclomatic complexity ≤5 (SEAM1) | "rule lists not if-ladders", "complexity ≤5" (ledger :133) |
| a value that may be absent | `Optional`, a sealed type or an enum (TY1, `types.md`) | "no null" is part of the seam principle (agent-factory#21 Q3) |
| code to check for smells | the smell baseline in `smells.md` | "Our own smells.md list … replaces the rameezk link in SEAM1" (ledger :568) |

`ledger :N` is a line of `research/19-approved-rules.md`. agent-factory#21 Q3 is the operator's decision that
splits the generic seam principle (this file) from a project's own seam rules.
SEAM1's reason comes from agent-factory research/32:34 (agent-factory#21 Part B), approved by the operator
(agent-factory#32 D9); the ledger row has none.

## Good / Bad

SEAM1 has no approved pair. The pair for an absent value is TY1, and the pair for a sealed shape is TY3, both in
`types.md`.

## Decided edges

- **Skip when** the build already fails on cyclomatic complexity (for example a Checkstyle `CyclomaticComplexity`
  check): leave that count to the gate (ledger OQ3 :200). — **Do not skip when** no gate measures it: count the
  branches of each changed method by hand. — **Confidence** high
- **Skip when** a project states its own seam rules: point to them and do not copy them here (one owner per fact,
  ledger OQ1 :383). — **Do not skip when** a project rule and SEAM1 disagree: no file wins, and the disagreement is a
  bug fixed in the same change (ledger OQ1 :383). — **Confidence** high

## Review checks

Walk every changed interface that a caller depends on, and every method that implements one.

- [ ] SEAM1 — Check each item the rule names. A seam with more than one job is a finding. An input that is not one
  record is a finding. An outcome returned as anything but a sealed result is a finding. A decision method that
  calls I/O is a finding, and so is an I/O method that chooses an outcome. An if-ladder where a rule list fits is a
  finding. A method above cyclomatic complexity 5, where no gate counts it, is a finding.
