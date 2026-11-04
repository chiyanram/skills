# R12 · Disposition table — every existing file's fate, sources and learnings

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a, G9b, G9c, G9d

## Question

For every file in today's rulebook — `.claude/skills/*` (34, incl. references/), `.claude/rules/*` (7), `.claude/agents/*`,
`.claude/commands/*`, `.claude/always-on/*`, `.claude/hooks/*`, CLAUDE.md sections, `docs/agents/personas/*`, user-level
`~/.claude/CLAUDE.md` + skills that overlap — what is its fate under the decided design (G1–G8): target (layer + domain +
file, or repo: agent-platform / aruvii-agent-fleet / agent-fleet / upstream plugin) · action KEEP / MOVE / MERGE / SPLIT /
DELETE / → PLUGIN · which reference excerpts should feed its rewrite (path:line from research/repos/*) · which of our
learnings feed it (P1 misses, fleet self-reports, R1 contradictions, R7 gaps, G7 lesson routes). Grouped by G9 domain.

## Resolution (2026-10-01)

`../research/14-disposition-table.md` — 141 rows: MOVE 35 · SPLIT 20 · KEEP 20 · MERGE 18 · →PLUGIN 16 · NEW 14 · DELETE 13 ·
unassigned 5; every DELETE names its replacement; target tree for all three repos + plugins at the end.
Lead checks: AGENTS.md is a symlink → CLAUDE.md (verified; G1 must invert it); mattpocock `retro` only under
`skills/in-progress/` in plugin 1.2.3 (verified). CORRECTION: "settings.json still registers warn-decrypt-outside-handler.sh"
is true only in this stale worktree — origin/master already removed it (#617). Repo-only content inside vendored copies
(tdd PIT paragraph + "make the change easy"; domain-modeling ADR-FORMAT note) must MOVE before the copies are deleted.
Open questions routed: ND-9 → G9a · ND-2, ND-3, ND-4 → G9b · ND-6, ND-7 → G9c · ND-1, ND-5, ND-8, ND-10–ND-16 → G9d.
