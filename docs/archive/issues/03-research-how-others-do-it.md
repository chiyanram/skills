# R3 · How others structure rules, roles and review

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G1, G2, G3

## Question

How do pstack (cursor/plugins), firstmate (kunchenguid/firstmate), mattpocock/skills,
addyosmani/agent-skills and Anthropic's own guidance (skills, subagents, CLAUDE.md, blogs) handle:
(a) one source of rules vs many, (b) role split across agents, (c) review shape and token budget,
(d) shipping the same setup to a laptop and a remote/headless machine?

## Resolution (2026-10-01)

Findings: `../research/03-how-others-do-it.md`. (a) Every source keeps ONE canonical tree, harness files point
at it (firstmate `CLAUDE.md` = `@AGENTS.md`; symlinked skill dirs); always-loaded = an index, bodies on demand;
pstack sets `disable-model-invocation` on nearly all skills; Anthropic: CLAUDE.md < 200 lines. (b) Routing by
task type: pstack playbook steps copied verbatim into a todo list; mattpocock `ask-matt` router; addy
skill/persona/command layers, personas never call each other; firstmate role via launch brief. (c) Nobody records
per-criterion MET/UNMET/N/A; diff command handed in, read-only, capped output, role-matched model; pstack 3 models +
lead judgment. (d) firstmate "clone is the distro", pushes a home over SSH from an allowlist; plugins over one
`skills/` tree; per-machine answers in a setup-written / gitignored file, separate from shared files.
