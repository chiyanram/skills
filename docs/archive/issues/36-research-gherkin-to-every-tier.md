# R21 · Analyst-written Gherkin → unit / IT / e2e tests that read the same, without a Cucumber runtime

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G9a

## Question

How do primary sources and reference projects make Given/When/Then scenarios (written by an analyst) the shared language across tiers WITHOUT a Gherkin runtime: Spock's BDD support (feature names, given/when/then block labels, @Title/@Narrative/@See, reports), Playwright test.step / annotations, Jest/Angular describe-it naming, plinth 058 design-bdd + 133 acceptance, our acceptance-criteria-writing + gherkin-to-test skills, Spock Reports / living documentation, traceability (scenario id ↔ test), and how the analyst's scenarios are stored (REQ prose vs .feature files without runtime). Who writes what (analyst vs developer), and how review checks every scenario has a test.

## Resolution (2026-10-02)

`../research/25-gherkin-to-every-tier.md`. REQ-500 already stores scenarios as a fenced gherkin block in the REQ (verified
:294); REQ-075 uses numbered prose AC-n. Drift verified: REQ-500:311 "…then grows, then stops at the cap" vs
LoginBackoffPolicySpec:25 "…then doubles to the cap". No @Issue/@See/@Title/@Narrative in any spec; no Playwright
test.step. REQ-500 tags scenarios @domain/@api (tier hints) contradicting acceptance-criteria-writing. Proposed: scenario id +
verbatim title in the test + @Issue / Playwright issue annotation; Spec verdict lists one row per scenario. Candidates GA1–GA5
(acceptance-criteria) and GT1–GT6 (scenario-to-tests), 6 open questions — one by one.
