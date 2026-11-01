# Design

Where a method decides and where it does I/O, and how branched one method may get. Read it when you write or review
a method that chooses an outcome, a method that does I/O, or a method with many branches.

Contents: Rules · When X, use Y · Good / Bad · Decided edges · Review checks

## Rules

- **SEAM1** — Make each decision a function that does no I/O, and keep I/O in a thin method that chooses no outcome,
  because logic tangled with I/O cannot be tested without the I/O.
- **DSN1** — Keep each method under the project's complexity gate (cyclomatic 10 if none is set), splitting by guard
  clauses or extracted helpers, because a highly branched method hides paths no test reaches.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a decision to make | a function that does no I/O (SEAM1) | business logic lives in pure functions (pstack `principle-boundary-discipline`, r48 :285); return results, don't produce side effects (mattpocock `codebase-design`, r48 :285) |
| I/O to do | a thin method that does the I/O and chooses no outcome (SEAM1) | the shell is thin and mechanical (pstack `principle-boundary-discipline`, r48 :285) |
| a method with many branches | guard clauses or extracted helpers, under the project's gate or cyclomatic 10 (DSN1) | Sonar S1541 defaults to 10 (r48 :294); extract conditions into guard clauses or helper functions (addy `code-simplification`, r48 :294) |

`r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source, read at the
commit it names.

## Good / Bad

SEAM1 and DSN1 have no approved pair.

## Decided edges

No source states an edge for SEAM1 or DSN1.

## Review checks

Walk every changed method.

- [ ] SEAM1 — A method that chooses an outcome and also calls I/O (a repository, a client, a file, a queue) is a
  finding. An I/O method that branches on what it read to choose what happens next is a finding.
- [ ] DSN1 — Where a gate measures cyclomatic complexity (for example Checkstyle `CyclomaticComplexity`), cite the
  gate and skip the count. Otherwise a method above cyclomatic complexity 10 is a finding.
