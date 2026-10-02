# R14 · Skill and reference writing standards + tooling — official and reference

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G10

## Question

From primary sources: Anthropic's skill authoring best practices + skills docs (platform.claude.com / code.claude.com),
the installed `anthropic-skills:skill-creator` skill (what it does: drafting, evals, description optimisation),
mattpocock `writing-for-agents` (+ SKILL-MECHANICS), superpowers "Match the Form to the Failure" + its skill-testing,
addy `docs/skill-anatomy.md` + `scripts/validate-*.js` + evals, BMAD best-practices.md, pstack authoring-a-skill
playbook + eval playbook. Output: a comparison of rules (length caps, description shape, progressive disclosure,
examples, testing/evals), what tooling exists to VALIDATE a skill/reference (lint, trigger evals, behaviour evals), and
a proposed writing checklist + proof method for our 5-section references.

## Resolution (2026-10-01)

`../research/16-skill-writing-standards.md`. All sources: body <500 lines, description <1,024 chars; after compaction CC
keeps only the first ~5k tokens of a skill → most important rule first. Wording: superpowers writing-skills/SKILL.md:461
"Match the Form to the Failure" (verified) — prohibition when the agent knows and skips a rule; Good/Bad pair when output
has the wrong shape. Tooling (verified on this laptop): `claude plugin eval` (case.yaml / prompt.md + graders, adds a
no-plugin baseline arm, --ablation) and `claude plugin validate`; skill-creator quick_validate.py, run_loop.py (trigger
evals), grader/benchmark/comparator; addy validate-skills.js. Proposed 16-line writing checklist mapped to the 5 sections
and a proof method: P1-style replay on #554 / !230, old vs new reference, 3 runs each, blinded judge + lead read; pass =
≥ real findings of old, owned findings hit in 2/3 runs, no lead-rejected false positives, ≤1.2× tokens; ~0.4–0.8M tokens
per reference per MR. Unverified: `claude plugin eval` against a repo-local skills folder.
