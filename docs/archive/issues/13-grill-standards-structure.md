# G5 · Standards content structure — one copy that serves author and reviewer

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: R7 (closed)
Part of: ../map.md · Blocks: G3 (Q2 onward)

## Question

Every standards text we have — `aruvii-standards` (SKILL + 24 references), `it-testing`, `smoke-spec`, `tdd`
(+ mocking, tests), `gherkin-to-test`, `acceptance-criteria-writing`, `flyway-migration`, `deslop`, the 7
`.claude/rules`, and the criteria inside `standards-review` / `architecture-review` — where does each belong in G1's
~7 domain skills, what is split or merged, and what single structure lets the SAME file guide the author when
writing and the Standards reviewer when reviewing? Grounded in how addy (`references/*-checklist.md` shared by build
skills and the review persona), pstack (`principle-*` skills used by poteto-mode and interrogate) and mattpocock
(repo standards docs pasted into the Standards axis) do it.

## Grilling log

- **Q1 DECIDED (operator, 2026-10-01): A — review checks live at the END of each reference** (smoke-spec shape);
  the Standards reviewer gets the whole file; no separate checklist, no central rubric.
- Operator's real problem (verbatim intent): references must carry OUR rules, OUR good and bad examples and samples
  from THIS project. Testing strategy, the right tests, Given/When/Then keep getting missed by the author and are only
  caught by the reviewer. No new hooks/extra process as the fix — write the references right, agent-agnostic, in the
  rubric-like shape that works in the references. Consult the skills-analysis corpus via /wiki.
- Q2 asked: the anatomy of one reference file.
- /wiki result: `../research/09-wiki-reference-anatomy.md` — ladder 0–4 exists (aruvii-standards/SKILL.md:27-38) but
  crq never orders it, review never checks steps 0–1, tier choice + unit mocking have no check, samples not pinned.
- **Q2 DECIDED (operator): A — every reference has all 5 sections: Rules (ours) · When X, use Y · Good/Bad pinned
  file:line from this repo · Decided edges · Review checks.** Each of the ~46 references is reviewed one by one
  with the operator (→ REQ work plan, not a grilling ticket each).
- openclaw testing skill = `aruvii-standards/references/test-value-bar.md` (adapted from openclaw
  `.agents/skills/test-audit`, read 2026-09-26; audit/campaign mode dropped on purpose). Also `deslop` from openclaw.
- Operator's main point: the thing that matters is agent-fleet + /crq + persona + SOUL — how do the reference
  projects' agents / SDLC handle roles and souls? → R8.

## Resolution (2026-10-01)

Structure decided: every reference = Rules (ours) · When X, use Y · Good/Bad pinned file:line · Decided edges ·
Review checks (at the end; the Standards reviewer reads the same file). Target tree = R7's proposal (testing/ code/
obs/ migrations/ delivery/ planning/ + rules/ MUSTs). Per-file placement and R7's OQ3–OQ10 (obs/ domain, merges,
precedence, unreviewed refs, tdd→plugin, playwright-rubric) are settled during the one-by-one reference review in the REQ.
- Post-close input (pstack bugbot-triage pattern: Skip when / Do not skip when / Confidence) → format for each
  reference's "Decided edges" section.
