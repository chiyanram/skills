# /wiki — anatomy of a guide+rubric reference file (2026-10-01, via skills-analysis corpus)

Verdict: the project already has the pattern, split in two — guide `aruvii-standards/references/*.md` (worked
examples) + rubric `standards-review/SKILL.md` (REF·FIRES·CHECK·MET·EDGE). Corpus offers only generic versions.

Installed testing ladder (aruvii-standards/SKILL.md:27-38, verified): 0 test-value-bar → 1 coverage-design
(RIGHT-BICEP) → 2 boundaries-correct (CORRECT) → 3 testing (G/W/T, harness per class) → 4 test-quality (A-TRIP).

Gaps (findings):
- standards-review cites neither test-value-bar nor coverage-design (verified: 0) → steps 0–1 never reviewed.
- No criterion for test-tier choice; none for unit-level mocking (Q-09 only covers @MockitoBean in ITs).
- testing.md, test-value-bar.md, coverage-design.md, boundaries-correct.md carry 0 file:line samples although
  aruvii-standards/SKILL.md:79 requires citations you can open.
- crq.md mentions aruvii-standards once, descriptively (:272) — never orders the ladder (verified) → R2 says it won't fire.

Anatomy patterns:
A pointer rubric over example library — PROJECT-SPECIFIC (ours today)
B Role→Goal→Constraints→Good/Bad per rule→Output→Safeguards — plinth skills/131, 130 (RIGHT-BICEP)
C Principle→numbered anti-pattern (bad/why/fix)→Detection Checklist — jeffallan test-master testing-anti-patterns.md;
  superpowers testing-anti-patterns.md (MINED) — closest to "guide + checks at end"
D Pyramid + Decision Guide + Anti-patterns — addy test-driven-development; kits/backend-engineer-skills testing.md
E generic meta-template — antigravity docs/contributors/skill-anatomy.md
Only A uses project examples; only C ends with checks.
