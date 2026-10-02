# G9a · Content: testing domain

Type: wayfinder:grilling (HITL) · Status: open · Assignee: claude · Blocked by: R12 (closed)
Part of: ../map.md

## Question

testing/ — strategy (tier choice), value bar, RIGHT-BICEP coverage, CORRECT boundaries, Given/When/Then, mocking, Spock, integration tests, smoke specs, audit-missing / delete-unneeded workflows; tdd → plugin. Learnings: P1 miss F7 (boundaries), !230 'asserts a default', RefusalReasonSpec not run. Approve each R12 row for this domain (target · action · deletions), and decide each reference's Rules, When-X-use-Y,
Good/Bad samples to pin, Decided edges and Review checks — from the reference excerpts and our learnings R12 lists. Output
is a per-file spec work item 1 writes without further deciding.
- ND questions to settle here: ND-9 (revive audit/campaign test workflows).

## Grilling log

- **Q1 DECIDED (operator, 2026-10-01): A** — testing/ = SKILL.md router (ladder 0–4, tier choice, tdd repo-only bits) ·
  references: strategy (NEW), value-bar, coverage-design, boundaries, unit-tests (= testing.md + test-quality MERGED),
  spock, integration-tests, smoke-specs (+ playwright-rubric merged) · workflows: write-a-test, scenario-to-tests,
  audit (NEW, one class/package at a time, no repo-wide campaign) · rules/testing.md MUSTs on every test path ·
  DELETE tdd copy (→ plugin), 2 CLAUDE.md test blocks, smoke-spec-reviewer · KEEP rules/smoke.md, 3 hooks, ADR-0009.
  Condition: audit.md must be PROVEN on a real package before it ships → requirement A-2.
- Operator asked: (1) is our existing testing content correct/any good? → R13 (AFK audit, below). (2) do we rewrite with
  the references + official skill-writing guidance/tooling? → new ticket G10. (3) where does BDD live? → answered:
  acceptance-criteria (G/W/T prose in the REQ) → planning/references/acceptance-criteria.md; scenario → tests →
  testing/workflows/scenario-to-tests.md; no Gherkin runtime by design (to-spec SKILL.md:46).
- R13 in (verdicts above). Small contradictions — defaults picked by the lead (reversible, operator may override):
  naming: Spock feature names as plain sentences; JUnit legacy `shouldXxx` left as is · cases: happy path AND failure
  (CLAUDE.md:221 wins over gherkin-to-test:81) · coverage: the per-module floor in gradle.properties is the gate; "new
  class ≥80%" stays as the author target · TDD: Red → Green → Refactor (repo standard overrides plugin) · ITs MAY assert
  DB rows when persistence is the behaviour (repo overrides plugin) · doubles: Spock `Stub()` for returns, `Mock()` only
  when the interaction IS the behaviour.
- Q2 asked: how the 3 REWRITE files are produced.
- **Q2 DECIDED (operator): A — the 3 REWRITE files are written FRESH in the G5 shape from verified sources only**; old
  file deleted, not edited; proven by G10's method before replacing. Operator will add more sources → the source list
  lives in `../research/17-testing-sources.md`; format follows G5 + R14 checklist.
- Operator (2026-10-01): every rule is approved individually — some reference rules the operator is against. R15 output is presented in batches of ≤5 rules per reference; nothing is adopted by default.
- Approved rules are recorded in `../research/19-approved-rules.md` (S1 approved).
- R15 Q1 DECIDED (operator): the PINNED plinth file (@c4276f64) is the authority; corpus-only rules ("independent expected value", "record gaps") come only if approved one by one.
- SP1 (Spock closure trap) PARKED: operator wrote the installed spock-best-practices skill and is unsure of it → R16
  verifies Spock guidance against official Spock docs + high-star sources first.
- Operator added scope (2026-10-02): mutation testing (PIT), property-based testing (jqwik or our own harness) for
  boundary scenarios, Playwright / E2E rules, frontend (Angular/Jest) unit-test rules — from reference projects or
  high-star TypeScript repos → R17 (mutation + property-based), R18 (Playwright / E2E / frontend). New candidate
  references: testing/references/{mutation.md, property-based.md, frontend-unit.md}; smoke-specs.md widened to e2e.
  Facts (origin/master): jqwik NOT used — home-grown harness aruvii-guardrails/src/test/java/…/property/Property.java;
  PIT wired via build-logic aruvii.mutation-conventions.gradle.kts; UI = Jest unit tests + Playwright smoke (core + full).
- Operator (2026-10-02): prefers MORE integration tests than unit for this project — asks if that is wrong and how agent SDK projects test. Today on master: 313 unit-tree test classes vs 141 integrationTest classes. → R19.
- R16: SP1 as written is WRONG (Spock ≥1.3 asserts every top-level closure line) — replaced by candidate K1. Spock specs run sequentially (no SpockConfig).
- IT4 note: plinth 322 itself USES @MockitoBean (:71, :545, verified) — our fake-port rule is ours (CLAUDE.md), backed by mattpocock tdd mocking.md:3-12 and openclaw junk pattern #6, not by plinth.
- Operator's model (2026-10-02): the ANALYST writes Gherkin-format behaviour scenarios for each feature/bug; the DEVELOPER
  picks unit / IT / e2e per scenario; Spock feature names + given/when/then labels (and e2e steps) mirror the Gherkin, so
  every tier reads the same. Not yet researched → R21. Also asked: wider industry check on fakes vs mocks → R20.
- CORRECTION (2026-10-02): IT4 migration clause void — 0 @MockitoBean annotations on master (the lead's earlier count matched javadoc text). Overrides on master: @TestBean in 31 files + FakePortsConfig.
