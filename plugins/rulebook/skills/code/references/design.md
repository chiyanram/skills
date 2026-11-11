# Design

Where a method decides and where it does I/O, and how branched one method may get. Read it when you write or review
a method that chooses an outcome, a method that does I/O, or a method with many branches.

Contents: Rules · When X, use Y · Good / Bad · Decided edges · Review checks

## Rules

- **SEAM1** — Make each decision a function that does no I/O, and keep I/O in a thin method that chooses no outcome,
  because logic tangled with I/O cannot be tested without the I/O.
- **DSN1** — Keep each method under the project's complexity gate (cyclomatic 10 if none is set), splitting by guard
  clauses or extracted helpers, because a highly branched method hides paths no test reaches.
- **DSN2** — Tidy only inside the lines the change touches, and propose anything beyond them as its own ticket,
  because a tidy outside the change mixes two reviews into one.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a decision to make | a function that does no I/O (SEAM1) | a decision with no I/O is tested with plain values, without the I/O |
| I/O to do | a thin method that does the I/O and chooses no outcome (SEAM1) | an I/O method that also decides cannot be tested without the I/O |
| a method with many branches | guard clauses or extracted helpers, under the project's gate or cyclomatic 10 (DSN1) | a highly branched method hides paths no test reaches |
| a value that may be absent | `Optional`, a sealed type or an enum (TY1, `types.md`) | a forgotten null check throws `NullPointerException` |
| code to check for smells | the smell baseline in `smells.md` | one smell list for the rulebook |
| a changed line is itself untidy: a restating comment, deep nesting, a dead parameter | tidy it in this change (DSN2) | it is already under review |
| untidy code sits next to the changed lines but outside them | leave it, and propose the tidy or refactor as its own ticket (DSN2) | the reviewer reviews only what the change is about |

## Good / Bad

SEAM1 and DSN1 have no approved pair. The pair for an absent value is TY1, and the pair for a sealed shape is TY3,
both in `types.md`.

## Decided edges

- **Skip when** the build already fails on cyclomatic complexity (for example a Checkstyle `CyclomaticComplexity`
  check): leave that count to the gate (DSN1). — **Do not skip when** no gate measures it: count the branches of each
  changed method by hand, against 10. — **Confidence** high
- **Skip when** a project states its own seam rules: point to them and do not copy them here (one owner per fact). —
  **Do not skip when** a project rule and SEAM1 disagree: no file wins, and the disagreement is a bug fixed in the
  same change. — **Confidence** high

## Review checks

Walk every changed method.

- [ ] SEAM1 — A method that chooses an outcome and also calls I/O (a repository, a client, a file, a queue) is a
  finding. An I/O method that branches on what it read to choose what happens next is a finding.
- [ ] DSN1 — Where a gate measures cyclomatic complexity (for example Checkstyle `CyclomaticComplexity`), cite the
  gate and skip the count. Otherwise a method above cyclomatic complexity 10 is a finding.
- [ ] DSN2 — Compare each tidy in the diff with the lines the change needed. A tidy outside them (a reformat, a rename,
  an extracted helper in untouched code) is a finding; a refactor proposed as its own ticket is not.
