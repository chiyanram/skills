# R1 · Inventory: every rule → every place it is stated

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G1, G3

## Question

For each rule this project enforces by text, where is it stated, and how many times? Sources:
`CLAUDE.md`, `.claude/rules/*.md`, `.claude/always-on/*`, `.claude/skills/*` (34, incl. `references/`),
`.claude/agents/*.md`, `.claude/commands/*.md`, `docs/agents/personas/*.md`, and the fleet's
`agent-fleet` rendered role `CLAUDE.md` / `SOUL.md` shape. Output: a rule × location matrix, the
duplicates and contradictions, word counts per source, and what loads at startup vs on demand.

## Resolution (2026-10-01)

Findings: `../research/01-rule-inventory.md`. Startup: laptop ~53 KB (~13k tok; repo CLAUDE.md 31.6 KB);
fleet ~62–70 KB (role file *replaces* `~/.claude/CLAUDE.md`, create-agent.sh:500); reviewer subagent 71–83 KB
(standards-review 46 KB preloaded). Java rules in 4–5 copies; AssertJ-only in 12 files; rubric claims it
"never restates" but does. Contradictions: aligned block vs table (agent-output.md:51 vs ~/.claude/CLAUDE.md);
decrypt scope (CLAUDE.md:273 vs dod.md:33); AssertJ/shouldXxx vs Spock-first (it-testing.md:54,99); D-02 cites
dependencies.md for Jakarta, which never mentions it. Dead hook registered: settings.json:83
`warn-decrypt-outside-handler.sh`. Overlaps: grill-me/grill-with-docs wrap grilling; code-review/standards-review/
deslop re-check one rule set; reply-shape guidance in 5 places; 9 repo skills shadow mattpocock plugin names.
