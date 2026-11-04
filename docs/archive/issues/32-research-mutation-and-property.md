# R17 · Mutation testing (PIT) and property-based testing (jqwik / our harness)

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a

## Question

What do primary sources and reference projects say about PIT (pitest docs, gradle-pitest-plugin, plinth/corpus, addy/superpowers/openclaw if any) and property-based testing (jqwik docs, Spock + jqwik, our home-grown Property.java harness in aruvii-guardrails) — when to use each, how they target boundaries, cost/time limits, how results are judged (surviving mutants, shrinking). Include our current state (build-logic aruvii.mutation-conventions.gradle.kts, which modules, make targets) and candidate rules for testing/references/{mutation,property-based}.md.

## Resolution (2026-10-02)

`../research/21-mutation-and-property.md`: PIT on aruvii-guardrails only via `make mutation` (outside every gate), threshold
0, default mutators, last measured #505 (85%, 18 survivors), targetClasses hard-coded. Property harnesses: JVM
`Property.java` (one real user: ToolOutputSanitizerPropertyTest — verified) and UI `support/property.ts` (fixed seed 0x5eed);
no jqwik / fast-check. Keep our harness (jqwik was removed for its coding-agent stdout message — see Property.java:13-17).
Gaps vs jqwik: no edge-case injection, no "condition reached" count. 17 candidate rules (M1–M10, P1–P7) and 8 open questions,
to be put to the operator one by one. Stale: gherkin-to-test:61 names PiiRedactorTest as a harness user (verified: it is not
among harness users); :70 says mutation "on any module".
