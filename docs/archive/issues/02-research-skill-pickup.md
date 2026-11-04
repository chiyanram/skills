# R2 · Skill pickup: which skills fire, which never

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G1

## Question

Which of the repo's skills are actually invoked, and which never trigger even when relevant? Evidence:
transcripts under `~/.claude/projects/*agent-platform*/` (`Skill` tool_use, `attributionSkill`).
Correlate with description shape (length, trigger phrasing, `important if` blocks, grouping). What do
Anthropic's skill-authoring docs say drives pickup?

## Resolution (2026-10-01)

Findings: `../research/02-skill-pickup.md` (483 transcripts, 2026-08-31 → 10-01). ~630 slash invocations vs
~100 model-initiated Skill calls; model calls are mostly *directed* by a running command ("Run the deslop
skill" 5/5), not discovered — a descriptive mention ("the `tdd` skill carries…", crq.md:260) fired 0×.
Never fired in 31 days: tdd, diagnosing-bugs, codebase-design, domain-modeling, prototype, hook-from-rule,
acceptance-criteria-writing, gherkin-to-test (+ manual-only to-spec/to-tickets/to-questionnaire), despite
trigger words in prompts. Description shape alone predicts nothing. Anthropic: description is the only
discovery signal; skill list capped ~1% of context, least-used dropped first; unused levers here: `paths:`
frontmatter, `user-invocable: false` for preload-only rubrics.
