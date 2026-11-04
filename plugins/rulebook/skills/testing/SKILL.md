---
name: testing
description: Use when you write, change or review a test, or choose a test's tier: unit and Spock specs, integration tests, Playwright smoke specs, property-based and mutation tests, and tests of code that calls a language model. Lists each testing reference and when to read it.
---

# Testing

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [boundaries](references/boundaries.md) | B1–B3 | when you write or review tests for logic that takes a number, a collection, a formatted string, an enum or sealed set, a time value or an optional input |
| [coverage-design](references/coverage-design.md) | C1–C4 | when you write or review tests for new logic, or a test of a call to an external dependency |
| [integration-tests](references/integration-tests.md) | IT1–IT5, TM4, SP1–SP11 | when you write or review an IT, a fake port, a test slice or a test configuration |
| [llm-live-tests](references/llm-live-tests.md) | LS11, LS13, LS15–LS16, LS19–LS20, LT14–LT18 | when you write or review a test that calls a real model provider, or an eval that scores model quality |
| [llm-tests](references/llm-tests.md) | LT1–LT13, LS1–LS10 | when you write or review a test whose code under test calls the model: the scripted fake, the agent loop, agent scenarios or recorded traffic |
| [mutation](references/mutation.md) | M1–M6, M8–M10 | when you change a PIT configuration, read a mutation report, or write a test that answers a surviving mutant |
| [property-based](references/property-based.md) | P1–P4, P6–P8, P10 | when you write or review a property test, a generator, or a requirement that says "for any input" |
| [scenario-to-tests](references/scenario-to-tests.md) | GT1–GT6, CV2 | when you write or review a test for a scenario in a work item's acceptance criteria |
| [smoke-specs](references/smoke-specs.md) | EA1–EA6, EB2–EB4, EC1–EC5, ED3 | when you write or review a Playwright smoke spec, or a fixture that such specs import |
| [spock](references/spock.md) | K1–K2, K2b, K3–K20 | when you write or review a Spock spec, unit or integration: its interactions, data tables, shared state, cleanup or assertions |
| [strategy](references/strategy.md) | S1–S4, S6, TM1–TM3, AT1 | when you choose where a new test goes, when you fix a bug, or when you review the tier and the doubles of a changed test |
| [unit-tests](references/unit-tests.md) | U1–U3 | when you write or review a unit test or a Spock spec |
| [value-bar](references/value-bar.md) | V1–V5 | before you add a test, when you fix a bug, and when you review or remove a test |
<!-- /index -->
