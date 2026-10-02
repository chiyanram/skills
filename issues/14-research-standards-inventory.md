# R7 · Standards inventory — every file, what it covers, who uses it, where it goes

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G5

## Question

Per file in the standards set (see G5): topics covered, MUST-level rules vs guidance vs worked examples, who reads it
today (author skill / rubric REF / persona / crq stage), overlaps with other files (cite file:line), and a proposed
target domain + file. Plus: exactly how addy, pstack and mattpocock lay out shared standards so author and reviewer
read the same text (paths).

## Resolution (2026-10-01)

Findings: `../research/08-standards-inventory.md` — 46 files inventoried (aruvii-standards has 23 refs, not 24).
Proposed tree: testing/ · code/ · obs/ (new) · migrations/ · delivery/ · planning/ + rules/ MUSTs only. Five
references have no review check (secure-coding, concurrency, coverage-design, test-value-bar, architecture-diagrams);
playwright-rubric read by nothing. Both-ways: addy shared `references/*-checklist.md` pointed at by author skill and
reviewer; mattpocock pastes repo docs into the Standards axis; **pstack interrogate does NOT use the principle skills**
(only rubric.md + code-quality-review.md) — corrects an earlier claim of mine. In-repo precedent: smoke-spec/SKILL.md
(authoring :6-155, rubric K-* :156-301). 10 open questions OQ1–OQ10 → G5.
