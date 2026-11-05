# R5 · humanlayer (12-factor-agents, skills plugins), Claude Code overview, AG-UI

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G1, G2, G4

## Question

What do humanlayer/12-factor-agents and humanlayer/skills (plugins/) say about (a) one source of rules,
(b) roles / control flow / human-in-the-loop handoffs, (c) context-window budgeting, (d) distribution?
What does the Claude Code overview (https://code.claude.com/docs/en/overview) establish as the supported
surfaces (CLI, desktop, web, SDK, headless, plugins) relevant to laptop + SSH fleet parity? Is AG-UI
(https://docs.ag-ui.com/introduction) relevant to this map (the dev workflow), or only to the Aruvii product?
Local clones: `../refs/`.

## Resolution (2026-10-01)

Findings: `../research/05-humanlayer-cc-agui.md`. Distribution: one plugin marketplace + `extraKnownMarketplaces`/
`enabledPlugins` in managed settings (fleet VM already has `/etc/claude-code/managed-settings.json`); managed
CLAUDE.md can't be excluded; project-scoped marketplaces ignored in untrusted dirs / `-p`; `--bare` skips CLAUDE.md,
plugins, hooks. Context: after `/compact` CLAUDE.md reloads, skill descriptions don't. humanlayer `improve-claude-md`
says keep rules inline in `<important if>` blocks — contradicts R3's "index + bodies on demand"; G1 must pick.
12-factor gaps here: 3 (own context window), 9 (no retry ceiling → findings in rounds), 10 (small focused agents),
13 (pre-fetch diff + applicable criteria). Subagents cannot ask the user (AskUserQuestion removed) → every human
gate lives in the main session or MR/Discord. Symlinks within a marketplace share files across plugins.
AG-UI: Aruvii-product concern only (SSE chat, tool approval) → out of scope here.
