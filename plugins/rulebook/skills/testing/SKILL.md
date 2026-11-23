---
name: testing
description: Use when you write, change or review a test, or choose where a test goes - unit tests and Spock specs, integration tests, property-based and mutation tests, and tests of code that calls a language model.
---

# Testing

A test earns its place by failing when a real defect ships. Everything below serves that.

## Before you write a test

Answer each in one line. If one has no answer, do not write the test: a test with no realistic failure costs upkeep
and protects nothing.

1. Which contract does it protect?
2. Imagine two edits. A bug in that contract must turn the test red. A refactor that keeps every observable result
   must leave it green. A test that stays green on the bug proves nothing; a test that goes red on the refactor is
   pinned to the implementation.
3. Why does no existing test catch that bug already?

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

1. Test the premise. A bug report or a first guess names a cause, such as "`FreeShippingRule` is broken". Write
   that premise as one sentence. Then write and run a test of the named code at the reported input, before you change
   any code. A green result refutes the premise: the named code is correct, and the fault is upstream of it. Reading
   the code is not a test of the premise.
2. Find the seam that owns the wrong behaviour. Write one test there that fails for the bug's reason, run it, and
   watch it go red. A regression test that never went red proves nothing about the fix.
3. Ask whether the state that triggers the bug is legitimate. If it is, handle it where the code broke. If it must
   never exist, fix the code that produced it, because a guard at the symptom hides the bug.
4. Fix the code and watch the test go green. Every line you ship traces to evidence from steps 1 to 3. Revert each
   line that a refuted premise motivated.
5. Put the command and its red output in the PR. Keep the test at its one seam; copies at mocked layers cannot see
   the bug. If the deciding fact took a deep dig, name the cheap, always-on signal (a log line, a metric, an
   assertion) that would have shown it at first look.

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

- Assert observable behaviour, never a field default or an input read straight back; those cannot fail for a defect.
  When code routes two inputs of one type into separate places, a swap compiles: test that routing, because it can fail.
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

Prefer no new test to a junk test. Coverage is a measure, not a contract: when asked to raise coverage, add only
tests that can go red for a defect, and name the reason for each test you leave out.

Flag a test in review, and leave it out of your own work, when it:

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

## Stack notes

Read the one that matches the code:

- Mutation testing (PIT, Stryker) on the code you changed: [mutation.md](mutation.md).
- Spock and Spring Boot integration tests: [stack.md](stack.md).
- A Playwright end-to-end or smoke spec: the `playwright` skill.
- Code that calls a language model: [model-calls.md](model-calls.md).
