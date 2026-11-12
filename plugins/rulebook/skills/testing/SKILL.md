---
name: testing
description: Use when you write, change or review a test, or choose where a test goes - unit tests and Spock specs, integration tests, Playwright smoke specs, property-based and mutation tests, and tests of code that calls a language model.
---

# Testing

A test earns its place by failing when a real defect ships. Everything below serves that.

## Before you write a test

Answer each in one line. If one has no answer, do not write the test: a test with no realistic failure costs upkeep
and protects nothing.

1. Which contract does it protect?
2. Which realistic change would make it fail?
3. Why does no existing test catch that already?

Then put it at the seam that owns the behaviour:

- Pure logic: a unit test.
- A real boundary (database, cache, HTTP, framework wiring): an integration test against the real thing in a
  container, because a mock cannot show what the real boundary does. Add unit tests only for branches the
  integration test cannot reach cheaply.
- A user journey: a smoke spec in the browser.
- An acceptance criterion: one test at one tier, named with the criterion's words, so a search for the criterion
  finds its test. Add a second tier only for a risk the first cannot see.

Before you change code, run the tests that touch it and note what was green, because a red test seen only after the
change cannot be told from one that was already red.

## Fixing a bug

1. Write one test that fails for the bug's reason, at the seam that owns the behaviour. Run it and watch it fail: a
   regression test that never failed proves nothing about the fix.
2. Fix the code and watch it pass.
3. Put the command and the failure output in the PR. Do not copy the test into every layer the bug crosses; copies
   at mocked layers cannot see the bug.

## Choosing cases

For new logic, walk RIGHT-BICEP: Right results, Boundaries, Inverse, Cross-check, Error, Performance. For each input,
walk CORRECT: Conformance, Ordering, Range, Reference, Existence (null, empty, missing), Cardinality (0, 1, many),
Time.

- For a range, test just inside and just outside each edge (1..10 gives 0, 1, 10, 11), because testing one side
  lets an off-by-one pass.
- For each external dependency, test the outage: a predictable failure, a WARN or ERROR log, no hang. An untested
  outage path tends to swallow the error.
- Write the expected value out by hand, because a value computed by the code under test shares its defect:

  ```groovy
  // Bad: passes whatever the discount logic does
  expect: price.total() == price.subtotal() * (1 - price.discountRate())
  // Good: worked out by hand
  expect: new Price(100.00, 0.15).total() == 85.00
  ```

- Name each case you skip on purpose in the PR, with what is missing and the risk, so a reviewer can tell a choice
  from an oversight.
- When the requirement says "for any input" (round-trip, idempotence, an invariant), write a property test and keep
  the edge examples beside it, because random generators rarely produce the edge. Print the seed on failure; never
  commit a fixed seed or retry a failing property.

## Writing the test

- Assert observable behaviour, never a field default or the input you just passed in; those cannot fail for a defect.
- Double only what you do not own. Prefer the real object, then an in-memory fake of the port, then a stub. Mock only
  a call that is itself the behaviour. Never mock your own classes, a value object, or the class under test, because
  the test then breaks on refactors that keep behaviour.
- Verify only the interactions the test name promises, with arguments matched by value; a wildcard lets the wrong
  value pass. Count calls only when the count is the contract; never count logs, metrics or retries.
- Fix the clock. Share no mutable state. Every test passes when run alone and in any order, or it fails one day for
  no defect.
- Wait on a condition, never on time; sleeps are what make tests flaky.
- Let nothing turn a failure green: no catch around the assertion, no `|| true`, no assertion inside an `if`.

## Junk tests

Do not add a test, and flag one in review, when it:

- has no assertion, or only a poll;
- compares a value with itself or a copy of it;
- hand-copies an enum or a registry list;
- greps source text instead of running the code;
- takes its expected value from the code under test;
- has a mock that implements the behaviour it asserts;
- proves again, at another layer, a contract already proven, with no new risk;
- breaks on a rename that keeps behaviour.

None of these can fail for a real defect. Prove a test is junk before you delete it, and keep it if it is the only
guard of a contract (API, protocol, config, migration, storage, security, a promised default). A test that fails on
main may be catching a real bug: reproduce it, never delete it.

## Mutation testing

Run mutation testing on the code you changed: PIT on the JVM, Stryker for TypeScript. It shows whether the tests
would catch a bug, which coverage cannot.

- Read each surviving mutant as a missing case. Name the RIGHT-BICEP or CORRECT case it reveals and add that test,
  not a test aimed at the mutated line, or the next mutant on that line survives too.
- NO_COVERAGE means the code is never reached; SURVIVED means it is reached and not asserted.
- Keep the default mutators; the others flood the report with mutants no test can kill. Exclude only code with no
  decisions in it, such as wiring and config, and never to raise the score.
- Keep it a report, not a CI gate, until someone picks a threshold from a measured score.

## Stack notes

Read the one that matches the code:

- Spock, Spring Boot integration tests, Playwright: [stack.md](stack.md).
- Code that calls a language model: [model-calls.md](model-calls.md).
