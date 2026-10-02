# R11 · humanlayer suite — fold, agentlayer, skills, advanced-context-engineering, humanlayer, claudelayer

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G4, G7, D1, the REQ

## Question

What does each repo do, and what does it say or implement about: coordinator/worker or research→plan→implement
workflows; context engineering (frequent intentional compaction, sub-agents, what goes in context); review and
human approval gates; how rules/skills/personas are packaged and distributed; headless/remote/web-UI agent hosting
(relevant to D1's AG-UI web app). Compare each against the map's decisions (G1–G6, G4 Q1–Q4) — confirms / contradicts /
new idea — with file paths.

## Resolution (2026-10-01)

Findings: `../research/13-humanlayer-suite.md`. Lead spot-checks: humanlayer create_plan.md:225-240 Automated vs Manual
verification + "pause here for manual confirmation" (verified); humanlayer-skills show-me `disable-model-invocation: true`
(verified — already covered: G1 Q4's reply card carries the always-on part). Confirms G6 (ralph_impl: worktree + fresh
session briefed by a command), G2 (Linear "Research in Review"/"Plan in Review" statuses), G3 (agentlayer docs-agent,
fold implementation-reviewer: diff in, read-only, capped, fixed sections). Routing of new ideas:
- Spec axis output in 4 fixed buckets (as planned · deviations · additions · not done) — fold Rpi.ts:437-509 → G3 default.
- Coordinator "never edits code" enforced by withholding tools — fold Rlm.ts → G4/G6 default.
- Plan phases with Automated vs Manual checks, pause after automated — humanlayer create_plan → REQ (crq stage 6 text).
- One updated-in-place MR comment per (role, head sha) — agentlayer github.ts:29 → REQ detail (vs append-only record).
- Program-design step before code (types, call-tree diff, file-tree diff) — ACE wsff.md:481-536 → fog (stage 5 design).
- thoughts/ + create_handoff/resume_handoff → G7 input. ACE caution: subagents are context control, not roles.
- D1: hld daemon (REST+SSE, approvals via --permission-prompt-tool, deprecated); fold/agentlayer durable event log +
  live deltas, approval pauses and resumes elsewhere → maps to AG-UI interrupts → D1 input.
