# R8 · Roles, souls and the SDLC around them — references vs ours

Ticket: [15](../issues/15-research-roles-souls-sdlc.md) · 2026-10-01 · primary sources only, read in the local clones.
Paths: `fm/` = `refs/kunchenguid-firstmate`, `ps/` = `refs/cursor-plugins/pstack`, `addy/` = `refs/addyosmani-agent-skills`,
`mp/` = `refs/mattpocock-skills`, `hl12/` = `refs/humanlayer-12-factor-agents/content`, `hls/` = `refs/humanlayer-skills`,
`oc/` = `refs/openclaw-openclaw`, `af/` = `refs/chiyanram-agent-fleet`, `ap/` = the agent-platform worktree.

## Per source (Q1 identity · Q2 location/authorship · Q3 install · Q4 process · Q5 separation)

### firstmate

| Q | Finding | Cite |
|---|---|---|
| 1 | Supervisor identity = repo `AGENTS.md` ("You are the first mate"). User prefs `data/captain.md` (+ `captain-shared.md`), memory `data/learnings.md`. Workers get role from a per-task brief ("You are a crewmate") | `fm/AGENTS.md:7-9,66` [drift 2026-10-17: cited lines rewritten at 5f2b81b; quoted text now at :7, see research/64b] · `fm/bin/fm-brief.sh:683,754 @5f2b81b` |
| 2 | Contract tracked in the distro repo, changed by PR. Private home `FM_HOME` (`data/ state/ config/ projects/`, gitignored). Firstmate itself writes `captain.md` "after inspect-then-update" | `fm/AGENTS.md:46-49,59,151 @5f2b81b` |
| 3 | `git clone` — "the cloned repo is the distro". Updates = fast-forward of the default branch | `fm/README.md:39,85 @5f2b81b` · `fm/AGENTS.md:405 @5f2b81b` |
| 4 | Intake → classify ship/scout → brief → `fm-spawn` → delivery path (no-mistakes owns review, tests, PR) → merge. Human gate: merge, "Never merge a PR without the captain's explicit word" unless `yolo`. Handoff = status-file appends, durable steering inbox, backlog notes. Forbids stacking extra manual reviews | `fm/AGENTS.md:33,182-185,210,216,229-231,240,371-374 @5f2b81b` |
| 5 | **Explicit.** "Keep fleet delivery posture and captain-private strategy out of project memory". Project `AGENTS.md` = deliberate human edits only | `fm/AGENTS.md:151-157` [drift 2026-10-17: cited lines rewritten at 5f2b81b; quoted text now at :161, see research/64b] |

### pstack (Cursor plugin)

| Q | Finding | Cite |
|---|---|---|
| 1 | Persona = `agents/poteto-agent.md` (9 lines: "Read the `poteto-mode` skill's `SKILL.md` in full"). Soul = `poteto-mode` SKILL (non-negotiables, principles, autonomy, reply style). User prefs = `~/.cursor/rules/pstack-models.mdc`; personal style = a `<handle>-mode` skill | `ps/agents/poteto-agent.md:9` [drift 2026-10-17: cited lines rewritten at f713f14; quoted text now at :9, see research/64a] · `ps/skills/poteto-mode/SKILL.md:13-107` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] · `ps/skills/setup-pstack/SKILL.md:8` · `ps/skills/automate-me/SKILL.md:69` |
| 2 | Plugin = author's. `/reflect` turns learnings into skill edits only after explicit user approval. `automate-me` defaults the personal skill **into the project** `.cursor/skills/` | `ps/skills/reflect/SKILL.md:53` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] · `ps/skills/automate-me/SKILL.md:69` |
| 3 | `/add-plugin pstack` | `ps/README.md:18` |
| 4 | Playbook steps copied verbatim into the todo list. Autopilot-full: one owner per PR, root swarm-verifies, merge needs the operator's grant + clean verdict. Always pause on irreversible writes. Trail = `decisions.tsv`, `children.tsv`; Orchestrate store has `gates.md`, `preferences.md` pasted into every spawn | `ps/skills/poteto-mode/SKILL.md:83,117` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] · `ps/.../playbooks/autopilot-full.md:6,8-9` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] · `ps/.../playbooks/orchestrate.md` §Store layout |
| 5 | **Explicit for persona** (plugin); project checks come from "the repo's AGENTS.md files and rules … for the touched paths". **Blurred** for user style (`automate-me` → project) | `ps/.../autopilot-full.md:6` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |

### addyosmani agent-skills

| Q | Finding | Cite |
|---|---|---|
| 1 | Persona = `agents/<role>.md`: role, single perspective, output format, Composition block. No soul, memory or user file | `addy/docs/agents.md:3,99-104` |
| 2 | Plugin. User's own `~/.claude/agents/` or `.claude/agents/` copy wins over the plugin's | `addy/.claude/commands/ship.md:26` |
| 3 | `/plugin marketplace add` + `/plugin install` | `addy/README.md:78-79 @aeac41d` |
| 4 | Command = when, persona = who, skill = how; "Personas do not call other personas". `/spec → /plan → /build → /test → /review → /ship`. Gates: confirm spec, plan review, one checkpoint for `/build auto`, Critical → NO-GO unless user accepts. Record = files (`SPEC.md`, `tasks/plan.md`) | `addy/docs/agents.md:16-22,55` · `addy/.claude/commands/spec.md:17` · `plan.md:14` · `build.md:34` · `ship.md:71` |
| 5 | **Explicit.** Repo `AGENTS.md` "is not meant to be copied into other projects" | `addy/AGENTS.md:5` |

### mattpocock skills

| Q | Finding | Cite |
|---|---|---|
| 1 | **No persona or soul.** Skills are workflows. "Roles" are **triage labels on work items** (`ready-for-agent`, `ready-for-human`, …) | `mp/skills/engineering/triage/SKILL.md:24-39` |
| 2 | Plugin = author's, read-only. Per-repo answers written once by `setup-matt-pocock-skills` into `docs/agents/*.md` + an `## Agent skills` block | `mp/skills/engineering/setup-matt-pocock-skills/SKILL.md:49,67-82` |
| 3 | `claude plugins install mattpocock-skills` ("subscribe rather than fork") or `npx skills` copy | `mp/README.md:27,35,52` [drift 2026-10-17: cited lines rewritten at 49dd158, see research/64c] |
| 4 | grill → `to-spec` (publishes, labels `ready-for-agent`) → `to-tickets` (user approves breakdown) → `implement` (tdd, `/code-review`, commit). Handoff = **agent brief comment on the issue**; `handoff` doc to OS temp dir. Wayfinder tickets tagged HITL/AFK | `mp/.../to-spec/SKILL.md:19` · `to-tickets/SKILL.md:56` · `implement/SKILL.md:9-15` [drift 2026-10-17: cited lines rewritten at 49dd158, see research/64c] · `triage/AGENT-BRIEF.md:3` · `productivity/handoff/SKILL.md:8` [drift 2026-10-17: cited lines rewritten at 49dd158, see research/64c] · `wayfinder/SKILL.md:75` |
| 5 | **Explicit.** Generic plugin; repo answers in `docs/agents/` | as Q2 |

### humanlayer (12-factor + skills)

| Q | Finding | Cite |
|---|---|---|
| 1 | No identity files. Factor 2 treats `Agent(role=, personality=)` as the black-box anti-pattern; "own your prompts" as code | `hl12/factor-02-own-your-prompts.md:15-20,33` |
| 2 | Prompts live in the app's own code | same |
| 3 | `npx skills add humanlayer/skills --skill X` (copy) | `hls/README.md:6-8` |
| 4 | Small focused agents, 3–10 steps; human gate is a **tool call** (`request_human_input`); state lives in the thread; trigger from Slack/email. `design-control-loop`: human "on the loop", validation commands agreed with the user | `hl12/factor-10…:9` · `factor-07…:29-42` · `factor-05…:26` · `factor-11…:9` · `hls/plugins/design-control-loop/skills/*/SKILL.md:20,73` |
| 5 | Not addressed | — |

### openclaw

| Q | Finding | Cite |
|---|---|---|
| 1 | Workspace files: `AGENTS.md` (operating rules, Red Lines), `SOUL.md` (persona, tone, boundaries), `USER.md` (user directives), `IDENTITY.md` (name, vibe, emoji), `MEMORY.md` + `memory/YYYY-MM-DD.md`, `BOOTSTRAP.md` (first run) | `oc/docs/concepts/agent-workspace.md:73-102` |
| 2 | Agent home `~/.openclaw/workspace`, one per agent; backed up as a **private** git repo. **Agent edits its own soul**: "This file is yours to evolve", "If you change this file, tell the user" | `agent-workspace.md:23,141 @d8faf8876` · `oc/docs/concepts/multi-agent.md:11,19` · `oc/docs/reference/templates/SOUL.md:40,44` |
| 3 | `openclaw onboard/setup` seeds files; bootstrap ritual (agent + user) writes IDENTITY/SOUL, then deletes `BOOTSTRAP.md` | `agent-workspace.md:46` · `oc/docs/start/bootstrapping.md:20-39` |
| 4 | **No SDLC** — personal assistant. Red Lines + "Ask first" for outbound actions | `oc/docs/reference/templates/AGENTS.md:60-75` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] |
| 5 | Agent side only. Note: its `AGENTS.md` is an **agent-side** file — same name as our project index | `agent-workspace.md:73-74` |

### Ours today

| Q | Finding | Cite |
|---|---|---|
| 1 | `agent.yaml` (persona scalars, purpose, guardrails, skills, `enforced`, model) + `SOUL.md` → rendered `~/.claude/CLAUDE.md`. Memory = agent-private "project knowledge" in its home. Same souls also in `ap/docs/agents/personas/*.md` and root `~/.claude/agents/aruvii-*` (×3) | `af/.claude/skills/create-agent/agent-yaml.md:3-36` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :3-37, see refs/README.md] · `af/scripts/create-agent.sh:355-390` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :375-426, see refs/README.md] · `af/CONTEXT.md:62-65,83-90 @080aabb` · `ap/docs/spec/REQ-535-portable-agent-personas.md:33` |
| 2 | Recipe in fleet dir (outside git). Operator writes it via `/create-agent` grill; `/update-agent` re-renders. Rendered file root-owned 0444 — "the agent cannot rewrite who it is" | `af/.claude/skills/create-agent/SKILL.md:40-53` · `af/README.md:34-37,75` · `create-agent.sh:548 @080aabb` |
| 3 | `sudo create-agent.sh`; plugins `--scope user`; machine-wide `managed-settings.json` (fleet-guard + compact re-inject). Laptop: `make agent ROLE=` (REQ-535) | `create-agent.sh:510-521` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :558-571, see refs/README.md] · `af/enforcement/managed-settings.json:2-25` · `af/enforcement/fleet-identity.sh:11-16` · `REQ-535…:53` |
| 4 | `/crq` stages 0–10, human at 2/5/9. Personas run **their own** process: "/crq exists … as a tool, not a process". Handoff = Discord @mention + GitLab comment | `ap/.claude/commands/crq.md:16-32` · `ap/docs/agents/personas/developer.md:13` · `research/00-fleet-self-reports.md:10` |
| 5 | **Blurred.** Persona in project repo; rendered CLAUDE.md carries project facts (repo path, `ARUVII_PORT_BASE`, verifier) | `REQ-535…:33` · `agent-yaml.md:23` · `create-agent.sh:378 @080aabb` |

## Comparison

| | firstmate | pstack | addy | mattpocock | humanlayer | openclaw | **ours today** | **ours decided (G1/G2)** |
|---|---|---|---|---|---|---|---|---|
| 1 Identity | contract + captain.md + learnings; brief per worker | persona stub → mode skill; user rule | persona file, no soul | none (labels) | none (prompts as code) | 6 files incl. SOUL, USER, MEMORY | agent.yaml + SOUL.md → CLAUDE.md (×3 copies) | role file: soul + guardrails + "you take: <label>"; talking set = 4 plugins + reply card |
| 2 Location / who / self-edit | distro + private home; PR / agent writes prefs; yes (prefs, learnings) | plugin; author; via `/reflect` + user OK | plugin; user override wins; no | plugin; author; n/a | app code; dev; n/a | agent home; agent + user; **yes** | fleet dir; operator; **no** (root-owned) | `aruvii-agent-fleet`; operator; *undecided* |
| 3 Install | git clone | plugin | plugin | plugin / copy | copy | onboard seeds | root script render | script render + user plugins + managed settings; laptop *G4* |
| 4 Process / gates / record | intake→brief→ship→merge; merge gate; status + inbox | playbooks; irreversible + merge; decisions.tsv | commands; spec/plan/ship; files | to-spec→tickets→implement; approve breakdown; issue brief | tool-call gate; thread | none | crq vs persona process (two texts); /approved, merge; Discord + GitLab | one crq.md, stages tagged by label; /approved, merge; GitLab comment, Discord ping; qa fresh read-only |
| 5 Separation | explicit | explicit (persona), blurred (style) | explicit | explicit | — | agent-only | blurred | explicit (Q-11) |

## Patterns in ≥2 sources

| Pattern | Sources |
|---|---|
| Persona ships **outside** the project (plugin or agent home) | pstack, addy, firstmate, openclaw |
| Process text owns the steps; persona says only *who* | addy (`docs/agents.md:16-22`), pstack (playbooks copied verbatim), firstmate (brief is the contract) |
| Role delivered **per task** as a brief, not a standing identity | firstmate `fm-brief.sh`, pstack orchestrate (standing orders in every spawn), mattpocock agent brief on the issue |
| Durable handoff record on the tracker or in files | mattpocock (issue comment), firstmate (status/backlog), pstack (`decisions.tsv`, `gates.md`), addy (`SPEC.md`, `tasks/plan.md`) |
| User prefs in their own file, apart from persona | firstmate `captain.md`, openclaw `USER.md`, pstack user rule / `-mode` skill |
| Merge is a human gate (relaxable only by explicit grant) | firstmate (`yolo`), pstack (full-autonomy grant), ours |
| Per-repo answers stay in the repo; generic package never forked | mattpocock `docs/agents/`, firstmate project `AGENTS.md`, pstack repo AGENTS.md checks |
| Learnings flow back into identity/skills under a gate | pstack `/reflect` (user approval), firstmate (PR for contract; agent for prefs), openclaw (agent, tells user) |

## Where our decided design differs from all references (risks)

| # | Difference | Risk |
|---|---|---|
| D1 | **Persistent agent per role, chained stage-to-stage** over Discord + GitLab. No reference does this: addy's user runs the commands, pstack/firstmate run one coordinator plus per-task workers with briefs | Handoff is the failure point — matches today's 3-day silence and findings-in-rounds (`00-fleet-self-reports.md:5,7,8`) |
| D2 | **Identity frozen, no learning path back.** Every reference that keeps identity also has a route for learnings (reflect, PR, self-edit). Ours: learnings stay agent-private (`af/CONTEXT.md:62-65 @080aabb`) | Lessons die with the agent; same mistake recurs per role |
| D3 | Rendered CLAUDE.md carries **project facts** (repo path, ports, verifier) on the agent side | Breaks S-10 (same agent, other repo) |
| D4 | "Cannot rewrite who it is" is weaker than stated. `~/.claude` is created by the agent (`create-agent.sh:481 @080aabb`), and the script relies on that to replace a root-owned file (`create-agent.sh:554-557 @080aabb`). *Inferred:* the agent can also unlink and replace `CLAUDE.md`; fleet-guard has no rule for it | Guardrail is convention, not enforcement |
| D5 | `AGENTS.md` = project index for us; openclaw uses the same name for the **agent's** operating file | Naming clash if an openclaw-style workspace is adopted (D1 boxes) |

## Open questions for the operator (not decided here)

1. Can an agent **propose** edits to its own role file (pstack `/reflect` style, PR to `aruvii-agent-fleet`), or never?
2. Where do agent learnings land: agent-private memory (today), `aruvii-agent-fleet` PR, or project `AGENTS.md` (firstmate: human edits only)?
3. Project facts in the rendered CLAUDE.md (repo path, ports, verifier): keep, or move to a per-project attachment?
4. Laptop lane (G4): role via **per-run brief** (firstmate/pstack) or user-level install?
5. Keep persistent per-role agents, or move toward per-task briefed workers (D1)?
6. Close D4 (root-owned `~/.claude`, or a fleet-guard rule), or accept?
7. Should the operator's own prefs (`~/.claude/CLAUDE.md` rules) ship to agents as a `captain.md` / `USER.md`-style file?
