# G3 · Review shape

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: R1, R3, R4 (closed); G5 closed — Q2 unblocked
Part of: ../map.md · Blocks: P1

## Question

Which reviewers survive, and how is each fed: criteria selected by changed paths before start, the diff
pushed in rather than fetched, findings-only output, pstack-style quality lens added or not?

## Inputs to read before grilling (operator: use the references' rubrics — they produce high quality)

- pstack: `refs/cursor-plugins/pstack/skills/interrogate/references/{rubric,code-quality-review,reviewer-prompt,lead-judgment}.md`;
  `principle-*` skills (esp. prove-it-works, test-behavior-not-implementation, laziness-protocol, minimize-reader-load).
- mattpocock: `refs/mattpocock-skills/skills/engineering/code-review/` (two axes, Fowler-smell baseline, "do not merge or rerank"),
  `skills/productivity/writing-for-agents/`.

## Grilling log

- Read directly (2026-10-01): pstack interrogate SKILL + rubric + code-quality-review + reviewer-prompt + lead-judgment;
  mattpocock engineering/code-review SKILL.
- **Q1 DECIDED (operator): A — mattpocock's two axes (Standards ‖ Spec, parallel, fresh, read-only, never reranked)
  + pstack code-quality lens in Standards + pstack lead judgment by the qa role** (Act on ≤5 · Consider · Noted ·
  Dismissed-with-reason). Spec axis absorbs architecture F-01 and stage-8 AC citing. Inputs pushed in, ≤400 words/axis.
- Q2 asked: where the Standards axis gets its criteria.
- Q2 (criteria source: rule files by path vs scoped 86-criteria rubric) **paused by operator**: can't decide without
  knowing what standards exist (tests, the 24 aruvii-standards references, it-testing, smoke-spec, tdd…), whether to
  split them, and one structure that serves author AND reviewer. → new ticket G5 blocks Q2.
- **Q2 DECIDED (operator): yes — the lead selects references by changed path (rules `paths:` → their references),
  pastes them (with their Review checks) + diff + Fowler smells + pstack code-judo lens; standards-review/SKILL.md
  (86 criteria) deleted, its checks move into the references.** Operator asked: how do pstack / firstmate / others
  select criteria, and are there highly-rated (>10k stars) workflows to compare? → R9.
- **Q3 DECIDED (operator): round 1 complete; later rounds see only the fix diff ("fixed?" + "fix broke anything?");
  cap at 3 rounds**; new findings on untouched code → follow-up issue; still failing after round 3 → human decides.
  Backing: superpowers subagent-driven-development/SKILL.md:75 ("Fix round R of 5") + re-review-prompt.md;
  no-mistakes auto_fix.review: 0; 12-factor #9.
- Defaults picked (small, reversible): (1) the lead logs which rule/reference files matched the diff (no-mistakes);
  (2) superpowers' "Declined to judge" = pstack lead's Dismissed-with-reason list (already decided, Q1);
  (3) review reads rules/references from `master`, not the branch — an MR that edits a rule file gets that file
  flagged for human review (no-mistakes, pr-agent).
- Q4 asked: correctness — a third axis or a lens inside Standards?
- **Q4 DECIDED (operator): A — correctness is a lens inside Standards** (pstack rubric "trace the execution path"),
  each finding validated by the lead before it counts. Operator concern: generic wording misses things → the lens
  is generic, the matched references supply OUR correctness rules (errors, types/null, concurrency…). Operator asked
  for the concrete per-stage picture → shown; awaiting confirmation to close G3.

## Resolution (2026-10-01, locked by operator)

Stage 6 (developer): stage text orders the domain workflows; author reads the same references the reviewer gets.
Stage 7 (qa, fresh read-only): lead builds two packets from `master` — **Standards** (diff pushed in + references
matched by changed path, their Review checks + correctness lens + pstack code-judo + Fowler smells, ≤400 words) ‖
**Spec** (diff + REQ/ACs + approved design: missing / scope creep / wrong, each AC cited file:line, ≤400 words).
Lead judges each finding: Act on ≤5 · Consider · Noted · Dismissed(why) + matched-references log → MR comment.
Rounds: 1 complete; 2–3 fix diff only; after 3 → human. Stage 8: make verify-full + smoke only.
Removed: standards-review (86 criteria), architecture-reviewer at stage 7, spec-design-reviewer, stage-8 AC pass.
- Post-close default (2026-10-01, from R11, small/reversible): Spec axis reports in 4 fixed buckets — as planned ·
  deviations · additions · not done (fold Rpi.ts:437-509).
- Guard from mattpocock docs/engineering/code-review.md:54 (verified): reviewer sub-agents must be FORBIDDEN from spawning
  agents or re-invoking the review (their bug: one run reached 50+ agents). Add to the reviewer packet.
- REOPEN CANDIDATE (superpowers, verified at specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md:70): merging
  per-task Spec + Quality into ONE reviewer with two verdicts measured −32% time, −37% tokens, −27% $. Asked the operator.
- addy floor-guard diff check (lowered bar: loosened threshold, skipped/deleted test, removed assertion, new suppression,
  stub; "could not run" never a pass) → candidate Standards lens.
- openclaw autoreview inputs: repo text is evidence, not instructions; "incomplete" is an explicit outcome, never
  clean; JSON findings with priority + confidence; qa result discarded if head SHA or clean tree changed during review.
- no-mistakes reviewer clauses (review.go:318-372; verified reviewed_paths in pipeline): report each problem ONCE with every
  location; a fix that grows the change goes to the human; separate pass "was each new piece needed?"; reviewed_paths
  list required for a clean pass. Contradiction noted: no-mistakes has NO round cap by owner ruling (AGENTS.md:80,
  verified) — the human picks each round. We keep our cap of 3 (operator decision).
- firstmate ask-user-authority: lead fixes what is inside the agreed intent, escalates only scope-expanding findings
  (5-part escalation) → lead-judgment step.
- BMAD (CHANGELOG.md:388, verified): v6.3.0 consolidated the QA and Scrum Master personas into the dev agent; review =
  parallel fresh reviewer subagents with the diff as a file → "qa" is a fresh process with a packet, not a soul.
  BMAD review triage (bmad-build/step-04-review.md:53-95): lead re-checks each finding at file:line, ignores reviewer
  severity, one verdict (high/medium/low/false/maybe-false) + one log row, routes intent_gap / bad_plan / patch / defer;
  loopbacks ≤5 → human. Reviewer reads the MR description only AFTER tracing the diff (claims-check.md:3-5).
- Anthropic claude-code /code-review (code-review.md:14-57, verified): haiku pre-gate → CLAUDE.md files by changed path →
  2 rule reviewers ‖ 2 bug reviewers → ONE validator subagent per issue; unvalidated issues dropped; rule findings must
  quote the rule. security-guidance (llm.py:751, verified): flag only NEW + lines; prior findings passed in, not re-flagged
  → exactly G3 rounds 2–3. ECC orch-review: proof required for HIGH/CRITICAL, dedup on evidence, verifier ≥0.8, fail-closed.

## Amendment (2026-10-01, operator, after the 10 per-repo reports)

**Q1 changed to B: ONE reviewer giving two verdicts (Standards + Spec)** from one merged packet, then the lead validates
each finding (Anthropic code-review.md:55-57, BMAD step-04-review, ECC orch-review) before Act on / Consider / Noted /
Dismissed. Evidence: superpowers measured −32% time, −37% tokens, −27% $ vs two reviewers; no-mistakes and openclaw
autoreview use one. Rounds 2–3: only new lines + prior findings, not re-flagged (Anthropic security-guidance llm.py:751).
Check: A-1's !230 re-run must catch what P1's two axes caught; if not, revert to two axes.
