# G1 · Where do rules live?

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: R1, R2, R3, R5 (closed)
Part of: ../map.md · Blocks: G4

## Question

What is the single source of rules: one file, a slim `CLAUDE.md` + path-scoped rules, skills, or a
layered mix — and what is the rule for "a rule is stated in exactly one place"?

## Grilling log

- Q1 (2026-10-01): "one body file + pointer" vs inline. Operator pushed back: is `.claude/rules` even the right
  place? Testing alone spans strategy, RIGHT-BICEP, Given/When/Then, mocking, IT, audits for missing tests,
  deleting unnecessary tests — and should the structure be agent-agnostic like industry? → Q1 reframed as the
  layer model (Q1b).
- Testing material today (words): standards-review 7.5k · smoke-spec 3.5k · ADR-0009 2.9k · it-testing 2.9k ·
  playwright-rubric 2.1k · aruvii-standards refs testing 1.3k, test-quality 1.3k, boundaries-correct 1.1k,
  test-value-bar 1.0k · tdd · gherkin-to-test · acceptance-criteria-writing · rules/it-testing.md · CLAUDE.md block.
- **Q1b DECIDED (operator, 2026-10-01): A — 4 layers, agent-agnostic.** L1 `AGENTS.md` index (<200 lines),
  `CLAUDE.md` = `@AGENTS.md` · L2 path-scoped rules = short MUSTs only · L3 skills + `references/` in one tree,
  symlinked into each harness dir · L4 hooks/lint for must-happen. Each rule defined in exactly one place.
- Q2 asked: skill granularity — domain skills (router + references + workflows) vs today's 34 small skills.
- **Q2 DECIDED (operator, 2026-10-01): A — ~7 domain skills (router + references/ + workflows/)**, with the
  operator's policy: **a skill that exists upstream is consumed as its plugin, never copied** (mattpocock, i-have-adhd;
  per-repo answers live in `docs/agents/*.md`, as mattpocock's setup pattern does); only what is ours becomes a
  domain skill. The talking set (i-have-adhd, show-me, teach, wait-what) must be active **from session start** in every
  session — laptop, fleet, any Claude session — not only when invoked.
- Operator asked for: written requirements + scenarios for this map, and an example design per decision from here on.
  → `../requirements.md`.
- Requirements Q-1..Q-10 + scenarios S-1..S-9 **confirmed by operator 2026-10-01**.
- **Correction (operator, 2026-10-01):** agent identity is NOT project content. An agent (or machine) can come from
  anywhere and work on any project; when it is created it gets a CLAUDE.md for *itself* (user-level), not for the
  project. My "persona = repo file (docs/agents/personas)" design was wrong. Verified directly in the references:
  - firstmate `AGENTS.md` §1–2, §6: agent home (`FM_HOME`: `data/captain.md`, `data/learnings.md`) is separate from
    `projects/` clones; project knowledge goes in the project's own `AGENTS.md`; "keep … captain-private strategy out
    of project memory"; workers get their role from a launch brief (§11), not by loading a project file.
  - addyosmani `docs/agents.md`: personas ship in the plugin, "consumed as a system prompt by your harness", any repo.
  - pstack `agents/poteto-agent.md`: the persona ships in the plugin, not in any project.
  - agent-fleet `create-agent.sh:500`: already renders the role into the agent's `~/.claude/CLAUDE.md` — right shape.
  → New requirement Q-11. REQ-535's location (`docs/agents/personas/` in the project) is now in question → G1 Q3.
- Agent-side / project-side split (Q-11) **confirmed by operator 2026-10-01**. Asked for a swimlane data-flow view → `../design-overview.md`.
- Q3 first framing (agent package in chiyanram-kit) **rejected by operator: never use chiyanram-kit.** Only two
  projects are in play: `agent-fleet` (creates agents) and `agent-platform` (Aruvii, the code). Q3 reframed: which
  of the two holds the agent side.
- **Q3 DECIDED (operator, 2026-10-01): A — the fleet side holds the roles; agent-platform keeps only project things.**
  Operator plan: create **`aruvii-agent-fleet`** next to agent-platform (Aruvii-specific fleet: the 4 roles), and keep
  the **generic `agent-fleet`** (GitHub, operator's own) separate as tooling. Matches agent-fleet's own "fleet
  directory" concept (CONTEXT.md: self-contained, outside the tooling repo) — but secrets (agent.yaml tokens) stay
  out of git.
- Q4 asked: where does the talking set live — generic agent-fleet or aruvii-agent-fleet.
- Q4 facts (diffed 2026-10-01): show-me upstream = humanlayer/skills `plugins/show-me` (462 w); `~/.claude/skills/show-me`
  = upstream minus `disable-model-invocation`; repo copy (647 w) rewritten for Discord/MR. i-have-adhd upstream =
  ayghri/i-have-adhd 0.3.0 (1242 w, already installed, `/i-have-adhd`, sticky); repo copy (839 w) rewritten,
  model-invoked. teach, wait-what = stale mattpocock copies (#587).
- **Q4 DECIDED (operator): A — install the 4 upstream plugins as-is, delete every copy; our extras collapse into ONE
  reply card injected at session start (carries the "always on" part), hosted in generic `agent-fleet`.**

## Resolution (2026-10-01)

1. **4 layers, agent-agnostic**: `AGENTS.md` index (<200 lines, `CLAUDE.md` = `@AGENTS.md`) · path rules = short
   MUSTs · skills + `references/` in one tree linked per harness · hooks/lint for must-happen. One rule, one file.
2. **~7 domain skills** (router + references/ + workflows/), fired by stage text ("Run X").
3. **Upstream skills are plugins, never copies** (mattpocock, humanlayer show-me, ayghri i-have-adhd); per-repo
   answers in `docs/agents/*.md`.
4. **Agent side ≠ project side** (Q-11). Three repos: generic `agent-fleet` (tooling + reply-card plugin) ·
   new `aruvii-agent-fleet` (the 4 Aruvii roles) · `agent-platform` (AGENTS.md, rules, skills, /crq).
5. Talking set = 4 upstream plugins + our reply card, on from session start everywhere.
Never use chiyanram-kit.
- Post-close TEST (2026-10-01, laptop, claude -p, tools disabled): CLAUDE.md containing `@AGENTS.md` → AGENTS.md content
  loaded ✓; CLAUDE.md with a plain-text pointer ("See AGENTS.md") → NOT loaded. superpowers RELEASE-NOTES.md:17's
  warning applies only to plain pointers. G1 decision (CLAUDE.md = `@AGENTS.md`) holds.
