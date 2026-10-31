---
name: testing
description: Use when you write, change or review a test, or choose a test's tier: unit and Spock specs, integration tests, Playwright smoke specs, property-based and mutation tests, and tests of code that calls a language model. Lists each testing reference and when to read it.
---

# Testing

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

| reference | rule IDs | read it when |
|---|---|---|
| [strategy](references/strategy.md) | S | you choose a test's tier, fix a bug, or review a test's tier and doubles |
| [value-bar](references/value-bar.md) | V | you add, keep or remove a test: should it exist at all? |
| [coverage-design](references/coverage-design.md) | C | you write tests for new logic or for a call to an external dependency |
| [boundaries](references/boundaries.md) | B | the logic takes a number, collection, format, enum, time or optional input |
| [unit-tests](references/unit-tests.md) | U | you write or review a unit test or a Spock spec |
| [spock](references/spock.md) | K | you write interactions, data tables, shared state, cleanup or assertions in Spock |
| [integration-tests](references/integration-tests.md) | IT, SP | you write an IT, a fake port, a test slice or a test configuration |
| [scenario-to-tests](references/scenario-to-tests.md) | GT | a Gherkin scenario in a work item's acceptance criteria needs its tests |
| [property-based](references/property-based.md) | P | a requirement says "for any input", or you write a generator |
| [mutation](references/mutation.md) | M | you configure PIT, read its report, or answer a surviving mutant |
| [llm-tests](references/llm-tests.md) | LT1–LT13, LS1–LS10 | the code under test calls a language model: the scripted fake, the agent loop, agent scenarios, recorded traffic |
| [llm-live-tests](references/llm-live-tests.md) | LT14–LT18, LS11, LS13, LS15, LS16, LS19, LS20 | a test calls a real model provider, or an eval scores model quality |
| [smoke-specs](references/smoke-specs.md) | EA–ED | you write or review a Playwright smoke spec, or a fixture such specs import |
