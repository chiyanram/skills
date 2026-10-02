# R13 · Is our existing testing content correct and good enough?

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a (Q2 onward)

## Question

For each current testing source (aruvii-standards refs test-value-bar, coverage-design, boundaries-correct, testing,
test-quality; it-testing skill; rules/it-testing.md; smoke-spec skill; gherkin-to-test; acceptance-criteria-writing;
tdd repo deltas): (a) CORRECTNESS — does every concrete claim still hold in the code (annotations, classes, make
targets, file paths, line refs)? list each false/stale claim with evidence; (b) CONTRADICTIONS between files;
(c) COMPLETENESS vs the best reference texts (addy test-driven-development + testing-patterns, superpowers
test-driven-development/writing-good-tests, openclaw test-audit, plinth 130/131 via the corpus, mattpocock tdd) —
what they cover that we don't; (d) for each file: how far it is from the G5 5-section shape and which real repo samples
(file:line in aruvii code) could pin its Good/Bad. Verdict per file: sound · needs fixes · rewrite.

## Resolution (2026-10-01)

`../research/15-testing-content-audit.md` (checked against origin/master @ 309982e1). Verdicts: REWRITE coverage-design,
testing, it-testing · NEEDS FIXES test-value-bar, boundaries-correct, test-quality, ladder, rules/it-testing, rules/smoke,
smoke-spec, gherkin-to-test, acceptance-criteria-writing · DELETE tdd copy (2 deltas move) · SOUND none.
Lead spot-checks (verified): coverage-design.md teaches a garbled RIGHT-BICEP (letters R, I, G, H, T, C, B, I, E, P at
:19-50); test-quality.md:107 still cites `pom.xml` for JaCoCo; @EnableAruviiSpec used in 13 groovy files on master and not
mentioned by it-testing; PricingDomainTest deleted (#539, replaced by PricingDomainSpec). Six rules missing entirely:
tier choice, unit-level doubles, assert behaviour not defaults, run existing tests first, boundaries trigger, Prove-It for
bug fixes. 11 real Good/Bad samples listed.
