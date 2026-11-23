# Mutation testing

Run mutation testing on the code you changed: PIT on the JVM, Stryker for TypeScript. It shows whether the tests
would catch a bug, which coverage cannot.

- A check you have never seen fail proves nothing. A killed mutant is that failure, seen.
- Read each surviving mutant as a missing case. Name the RIGHT-BICEP or CORRECT case it reveals and add that test,
  not a test aimed at the mutated line, or the next mutant on that line survives too.
- NO_COVERAGE means the code is never reached; SURVIVED means it is reached and not asserted.
- A surviving mutant stays a finding. Report it with the mutated line, and keep the mutators, the exclusions and the
  product code as they are until the operator decides.
- Keep the default mutators; the others flood the report with mutants no test can kill. Exclude only code with no
  decisions in it, such as wiring and config, and never to raise the score.
- Keep it a report, not a CI gate, until someone picks a threshold from a measured score.
