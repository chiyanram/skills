# Map: One rulebook — rules, roles and review shared by laptop /crq and the SSH fleet

Label: wayfinder:map · Tracker: local markdown (this folder). Tickets: `issues/NN-*.md`.
Ticket header lines: `Type:` · `Status: open|closed` · `Assignee:` (empty = unclaimed) · `Blocked by:`.

## Destination

A REQ, ready to hand to `/crq`, that defines: **one source** for rules and role souls · `/crq` stages
**owned by role** (analyst 1–3, spec-reviewer 5, developer 6, qa 7–8) · **diff-scoped** reviewers with
`spec-design-reviewer` removed · **how the laptop and the SSH fleet load identical files**.

## Notes

- **Canonical location (2026-10-02): github.com/chiyanram/skills (private), local clone ~/workspace/skills.** The old copy under agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/ is frozen at commit debed19; refs/ clones stay there.
- **Requirements + scenarios: [requirements.md](requirements.md)** — every ticket answer is checked against them.
- Spans two repos: `agent-platform` (GitLab — rules, skills, `/crq`, `docs/agents/personas/`) and
  `agent-fleet` (GitHub `chiyanram/agent-fleet` — recipes, `SOUL.md`, rendered `CLAUDE.md`). G4 lands
  changes in `agent-fleet`; it stays a ticket here.
- Inputs already gathered (2026-10-01 session):
  - pstack clone: `cursor/plugins` → `pstack/` (interrogate rubric, poteto-mode playbooks, principles).
  - firstmate: https://github.com/kunchenguid/firstmate — "agent distro".
  - Reviewer cost measured: 57 subagent runs, 101M input tokens (deduped — see R4); median 1.3–1.7M/run,
    16–19 calls, first-turn ctx ~30k, peak 90–177k. Rubric preloaded AND re-read in 39/57 runs.
  - Fleet self-reports (all 4 roles) — pasted in session; summary in `research/00-fleet-self-reports.md`.
  - MasterLaundry "Ask Me" box (refs/imdganesancareers-MasterLaundry) — operator's model for an SDK agent in a
    sandboxed container; see R6.
  - Prior work: #535 / REQ-535 (portable personas), #489 (personas + testing skills, ungrilled),
    #587 (stale vendored mattpocock skills), #540 (review axes per stage), #90 (SDLC epic map).
- Decisions already taken in the charting grill:
  - Review direction **A**: keep repo criteria, choose them by diff before the agent starts, drop
    per-criterion N/A receipts. (Not pstack's generic lenses alone.)
  - **Drop `spec-design-reviewer`** — human `/approved` at stage 5 + stage-8 AC citing cover it;
    the fleet's spec-reviewer never spawns it.
- **Every decision cites what the references do (operator, 2026-10-01)** — pstack and mattpocock first; they are
  the quality bar. Each grilling question shows the reference backing next to the options.
- **No rule enters any reference without the operator's explicit yes (operator, 2026-10-01).** Rules are presented one small batch at a time (≤5, one reference), each with its source and a recommendation; anything not approved stays out, including reference-repo rules the agent likes.
- Skills to consult: `grilling`, `domain-modeling`, `research`, `prototype`, `codebase-design`.
- Standing preference: no GitLab issues for this effort — everything stays in this folder.
- **Three repos (operator, 2026-10-01): `agent-fleet` (generic tooling, GitHub) · `aruvii-agent-fleet` (new, Aruvii roles, next to agent-platform) · `agent-platform` (project side).**
- **Never use `chiyanram-kit` (operator, 2026-10-01).**

## Final step (after G1–G4 + P1 land)

Role boxes replace tmux + Discord: one Agent-SDK container per role, AG-UI to one web UI, the same compose on
laptop and VM. Paper design: [D1](issues/12-design-role-boxes.md).

## Decisions so far

<!-- one line per closed ticket -->

- [R4 · Reviewer cost baseline](issues/04-research-reviewer-cost-baseline.md) — ~$2–2.8/review; 62–66% is thinking/output; scope criteria to the diff, the re-read fix saves ≤4%
- [R2 · Skill pickup](issues/02-research-skill-pickup.md) — skills fire when a command says "run X", almost never by description; 8 skills never fired in 31 days
- [R1 · Rule inventory](issues/01-research-rule-inventory.md) — Java rules in 4–5 copies, AssertJ in 12 files, 5 contradictions, reply-shape rules in 5 places; repo CLAUDE.md is 60% of startup
- [R3 · How others do it](issues/03-research-how-others-do-it.md) — one canonical tree + pointers; index always-on, bodies on demand; routing by task type; no per-criterion receipts anywhere; per-machine config separate from shared files
- [R5 · humanlayer, Claude Code docs, AG-UI](issues/10-research-humanlayer-agui-cc.md) — managed settings + one marketplace can ship identical setup to laptop and VM; inline `<important if>` vs on-demand bodies is G1's call; 12-factor gaps 3, 9, 10, 13
- [R6 · AG-UI as the human channel](issues/11-research-agui-human-channel.md) — C now (keep Discord + CLI); A (role boxes: SDK + AG-UI, one compose for laptop and VM) is the FINAL step → D1
- [G1 · Where rules live](issues/05-grill-where-rules-live.md) — 4 layers, agent-agnostic (AGENTS.md index); ~7 domain skills; upstream = plugins, never copies; roles in new aruvii-agent-fleet, reply card in generic agent-fleet, project rules in agent-platform
- [G2 · Is a role first-class in /crq](issues/06-grill-role-first-class.md) — one crq.md, stages tagged by project-owned role labels; roles say only who; GitLab comment = handoff record, Discord = ping; qa always in a fresh read-only context
- [R7 · Standards inventory](issues/14-research-standards-inventory.md) — 46 files → testing · code · obs (new) · migrations · delivery · planning; 5 refs never reviewed; author+reviewer share one text in addy and matt
- [R8 · Roles, souls and SDLC in the references](issues/15-research-roles-souls-sdlc.md) — persona outside the project everywhere (backs Q-11); process owns steps (backs G2); risks: standing agent per role (D1), no lesson loop (D2), project facts in role file (D3), identity not truly locked (D4)
- [G5 · Standards structure](issues/13-grill-standards-structure.md) — one file per topic: Rules · When X use Y · Good/Bad pinned from this repo · Decided edges · Review checks at the end; R7 tree; each reference reviewed one by one in the REQ
- [R9 · >10k★ review workflows](issues/18-research-popular-review-workflows.md) — selecting criteria by changed path is established (no-mistakes, ECC, openclaw); missing pieces: round cap, per-finding validation, rules from default branch, matched-rules log
- [G3 · Review shape](issues/07-grill-review-shape.md) — Standards ‖ Spec, fresh read-only, inputs pushed in, references by changed path (checks at their end), correctness + code-judo lenses, pstack lead judgment, 3-round cap (fix diff only after round 1) · AMENDED: one reviewer, two verdicts, lead validates each finding
- [P1 · Scoped reviewer on !230](issues/09-prototype-scoped-reviewer.md) — shape confirmed: round 1 caught 5/7 real findings + 5 new (2 shipped), missed `final` + boundaries; 246k vs ~302k; re-run after the standards rewrite is a REQ acceptance criterion
- [G6 · Coordinator + per-task workers](issues/16-grill-standing-vs-per-task.md) — one always-on coordinator; fresh interactive worker per (work item, role) in its own tmux window + worktree, briefed; qa fresh per round; firstmate hard rules; coordinator relays every question with context
- [R10 · Claude cloud as a backend](issues/19-research-claude-cloud-backend.md) — spawn + steer from CLI are documented; GitLab push-back is not (Anthropic-hosted) → a later adapter via self-hosted env or GitHub mirror; Agent SDK for the web-app coordinator
- [R11 · humanlayer suite](issues/20-research-humanlayer-suite.md) — confirms G2, G3, G6; adds Spec-axis 4 buckets, tool-enforced coordinator, Automated/Manual plan checks; thoughts/ + handoff → G7; event log + resumable approvals → D1
- [G4 · Distribution](issues/08-grill-distribution.md) — one unix user; you = coordinator on the laptop; coordinator is a contract with front-end and backend adapters; tiers 0/1/2; agent side as plugins everywhere + one machine file
- [G7 · Lessons](issues/17-grill-lessons-into-identity.md) — agents propose MRs to the one owning file, you merge; retro worker at work-item close + /lesson on demand; sorted into dropped / check / reference / soul / machine file, ≤2 MRs per item
- [G8 · Routing by task type](issues/21-grill-routing-by-task-type.md) — one crq.md; stage 1 maps (type × size) to a stage mask, operator can override; floor (migration/security/API/dependency) → full path; workers escalate only
- [R12 · Disposition table](issues/22-research-disposition-table.md) — 141 rows (MOVE 35 · SPLIT 20 · KEEP 20 · MERGE 18 · →PLUGIN 16 · NEW 14 · DELETE 13); 16 open questions routed to G9a–d; target tree for 3 repos

## Not yet specified

- crq stage execution: copy each stage's steps verbatim into the todo list, skipped steps stay as `skip: <reason>` (pstack poteto-mode:117) — REQ crq.md text.
- Review verdict tied to head SHA; reused after rebase when patch-id unchanged (pstack) — REQ detail.
- Stage 5 "program design" content (types, call-tree diff, file-tree diff before code — ACE wsff.md:481-536); revisit when writing crq.md stage text.
  Source text: ACE wsff.md:481-570 (call-tree diff, file-tree diff, type signatures, thin end-to-end slices).
- "Stated a repo fact without checking" — now routed: G7 retro proposes a check for it (candidate: ECC GateGuard pattern).
- Findings-in-rounds — addressed by G3 (round 1 complete, cap 3, prior findings not re-flagged) + ACE: invest in the plan stage.

## Out of scope

- Fleet environment failures (OOM on `make verify`, unset `JAVA_HOME` / `DOCKER_HOST`, `/tmp` ownership)
  — `agent-fleet` ops, not rules.
- #587 — stale vendored mattpocock skills; already its own ticket.

## Handoff plan (operator, 2026-10-01)

Route added (2026-10-01): R12 disposition table → G9a testing → G9b code + obs → G9c migrations + delivery + review packet → G9d planning + talking + meta + crq + AGENTS.md. Then work item 1 writes, no deciding left.
Added (G9a): R13 testing-content audit → G9a Q2+; R14 writing standards/tooling → G10 writing standard + proof method.
Added (G9a, operator 2026-10-02): R16 Spock verification · R17 mutation + property-based · R18 Playwright/E2E + frontend.
Added: R19 agent-SDK test mix · R20 fakes vs mocks · R21 analyst Gherkin → every tier.

Three linked work items, built in order: (1) agent-platform — project side; (2) aruvii-agent-fleet — new repo: coordinator,
souls, brief template, plugin marketplace; (3) agent-fleet — one unix user, managed settings, machine file, retro wiring.
D1 later as its own effort. Operator: the map is NOT finished — what goes where (every file's fate, which reference text
and which of our learnings feed each rubric/reference, what is deleted) must be decided first. → R12 + content tickets.
