# R15 · plinth testing rules (130–133, 321–323, 058, 706) mapped onto our testing references

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a Q3+

## Question

For each operator-supplied plinth file: which of its rules/examples feed which of our target references (strategy,
value-bar, coverage-design, boundaries, unit-tests, spock, integration-tests, smoke-specs, scenario-to-tests,
planning/acceptance-criteria), which CONFLICT with our stack/decisions (Spock-first, Gradle, Testcontainers singleton,
RestTestClient, no MockMvc, no @MockitoBean, no H2, no Gherkin runtime, src/integrationTest), which we lack entirely, and
how plinth's format (Role · Goal · Constraints · Examples Good/Bad · Output Format · Safeguards) maps to our G5 sections.

## Resolution (2026-10-01)

`../research/18-plinth-testing-mapping.md`: per-rule ADOPT/ADAPT/REJECT; mnemonics verified at P130:19-21; 15 conflicts (X4 @Container/@ServiceConnection vs singleton initializer); 8 open questions Q1–Q8 for the operator, asked inside G9a batches. P706 body file not supplied.
