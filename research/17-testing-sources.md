# Testing domain — source list (verified sources only) · G9a · 2026-10-01

Format every reference uses: G5 five sections (Rules · When X, use Y · Good/Bad pinned file:line · Decided edges · Review
checks) + the R14 writing checklist (`16-skill-writing-standards.md`). Operator adds sources below "Operator-added".

| target reference | source | where | used for |
|---|---|---|---|
| strategy.md (tier choice) | addy test-driven-development | refs/addyosmani-agent-skills/skills/test-driven-development/SKILL.md:144-187 | test pyramid, decision guide |
| strategy.md | plinth 130 test-layer split | ~/workspace/claude/analysis/skills-analysis/docs/extractions/plinth-java-testing-strategies-and-the-test-layer-split.md | Java test layers |
| strategy.md | gherkin-to-test (ours, fixes per R13) | .claude/skills/gherkin-to-test/SKILL.md | scenario → tier |
| value-bar.md | openclaw test-audit | refs/openclaw-openclaw/.agents/skills/test-audit/SKILL.md:18-66 | 4-question gate, junk patterns |
| value-bar.md | ours test-value-bar (needs fixes) | .claude/skills/aruvii-standards/references/test-value-bar.md | retention bar |
| coverage-design.md | plinth 130 RIGHT-BICEP | corpus extraction above (130-…-right-bicep) | the correct 6 dimensions |
| boundaries.md | ours boundaries-correct (needs fixes) | .claude/skills/aruvii-standards/references/boundaries-correct.md | CORRECT |
| unit-tests.md | addy testing-patterns | refs/addyosmani-agent-skills/references/testing-patterns.md:16-124 | test shape, naming |
| unit-tests.md | superpowers writing-good-tests | scratchpad/r9/obra_superpowers/skills/test-driven-development/writing-good-tests.md | anti-patterns |
| unit-tests.md | mattpocock tdd (plugin, read only) | ~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills/1.2.3/skills/*/tdd/{tests,mocking}.md | seams, doubles |
| unit-tests.md / spock.md | anthropic-skills:spock-best-practices (installed) | ~/.claude/skills/synced/…/spock-best-practices/ (+ references/anti-patterns.md) | Spock idiom, Mock vs Stub |
| integration-tests.md | ours it-testing (rewrite) + ADR-0009 | .claude/skills/it-testing/SKILL.md · docs/adr/0009-* | facts only, re-verified on master |
| smoke-specs.md | ours smoke-spec (needs fixes) + playwright-rubric | .claude/skills/smoke-spec/SKILL.md · docs/guides/playwright-rubric.md | K-* rubric |
| workflows/audit.md | openclaw test-audit modes | refs/openclaw-openclaw/.agents/skills/test-audit/SKILL.md:8-14, :111-122 | audit mode |
| all (Good/Bad) | R13 real samples on master | research/15-testing-content-audit.md (11 samples) | pinned examples |
| all (writing) | superpowers "Match the Form to the Failure" | scratchpad/r9/obra_superpowers/skills/writing-skills/SKILL.md:461 | prohibition vs Good/Bad |

## Operator-added
<!-- add: source · where · used for -->
| strategy, coverage-design, boundaries, unit-tests | plinth 130 java-testing-strategies (RIGHT-BICEP · A-TRIP · CORRECT) | refs/plinth-pinned/130-java-testing-strategies.md (@c4276f64) | operator |
| unit-tests, spock | plinth 131 java unit testing | refs/plinth-pinned/131-java-testing-unit-testing.md | operator |
| integration-tests | plinth 132 java integration testing | refs/plinth-pinned/132-java-testing-integration-testing.md | operator |
| strategy (acceptance tier), scenario-to-tests | plinth 133 java acceptance tests | refs/plinth-pinned/133-java-testing-acceptance-tests.md | operator |
| unit-tests (Spring slices) | plinth 321 Spring Boot unit tests | refs/plinth-pinned/321-frameworks-spring-boot-testing-unit-tests.md | operator |
| integration-tests | plinth 322 Spring Boot integration tests | refs/plinth-pinned/322-frameworks-spring-boot-testing-integration-tests.md | operator |
| strategy (acceptance), smoke-specs? | plinth 323 Spring Boot acceptance tests | refs/plinth-pinned/323-frameworks-spring-boot-testing-acceptance-tests.md | operator |
| planning/acceptance-criteria, scenario-to-tests | plinth 058 design-bdd | refs/plinth-pinned/058-design-bdd.md (@5e338bb8) | operator |
| integration-tests (containers) | plinth 706 containers/docker | refs/plinth-pinned/706-technologies-containers-docker.md (@5e338bb8) | operator |
