# G4 · Distribution: laptop and VM load identical files

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: G1, G2, R5, G6 (all closed)
Part of: ../map.md

## Question

How do the laptop and the SSH fleet get the same rules and souls by construction: repo-owned personas
with `agent.yaml`/`SOUL.md` as a thin pointer, a Claude Code plugin, or a firstmate-style distro dir?
Lands changes in `agent-fleet`.

## Inputs from R8 (2026-10-01)
- D3: rendered role CLAUDE.md today carries project facts (repo path, ports, verifier) → must move project-side or
  into a per-machine config file to satisfy S-10.
- D4: agent owns `~/.claude`; identity immutability needs a different mechanism (managed settings / managed CLAUDE.md).
- From G6 (2026-10-01): with one coordinator + workers, per-role unix users may collapse to one (fewer users, one
  GitLab identity — loses per-role attribution in MR comments); concurrent workers still collide on /tmp, ports,
  Docker, RAM → resource caps / Verifier stay. Decide here.

## Grilling log

- Fact (claude --help on the laptop, 2026-10-01): `--agent <agent>` runs a session as an agent definition (a plugin
  can ship it); `--append-system-prompt[-file]`, `--plugin-dir`, `--settings` exist → a worker can start as
  `claude --agent <role>` with its soul from a plugin; nothing rendered into ~/.claude/CLAUDE.md.
- **Q1 DECIDED (operator): A — ONE unix user runs the coordinator and every worker**; per-worker worktree, TMPDIR,
  port block; one GitLab identity, comment header names the role ("qa · round 1 · #600").
- Operator: don't go narrow — step back each time, show the whole picture and compare decisions. → design-overview v2
  + consistency check before Q2.
- **Q2 DECIDED (operator): A — on the laptop the operator IS the coordinator** (their session runs /crq and starts
  fresh workers the same way: `claude --agent <role>` + brief + own worktree). Resolves T1.
- Operator's wider lanes (2026-10-01): (a) also run the fleet locally on a developer machine; (b) some developers want
  neither /crq nor the fleet; (c) SSH machine used separately, or Claude cloud; (d) END GOAL: a web app speaking AG-UI
  that talks to the coordinator or IS the coordinator; a CLI too if needed (MasterLaundry Ask Me pattern).
  → Q3: make "coordinator" a contract with interchangeable front ends and worker backends, plus opt-in tiers.
- **Q3 DECIDED (operator): A — "coordinator" is a CONTRACT** (written once in aruvii-agent-fleet: coordinator persona
  + brief template + firstmate's 5 hard rules + relay-with-context). Filled by: the operator in Claude Code, a
  coordinator agent (laptop / SSH VM / Claude cloud), or the AG-UI web app. Front ends (terminal, Discord, CLI,
  AG-UI) and worker backends (tmux laptop, tmux VM, cloud, boxes) are adapters. **Tiers are opt-in**: 0 = project
  side only (any developer), 1 = + /crq with fresh workers, 2 = + a coordinator agent.
  Backing: firstmate bin/backends/ (tmux, zellij, herdr, cmux, orca) + §4 harness adapters; MasterLaundry askme-box
  server.ts (same box behind an HTTP front). → R10 for the cloud backend.
- **Q4 DECIDED (operator): A — the agent side ships as PLUGINS everywhere** (aruvii-agent-fleet marketplace: agents/
  coordinator + 4 role souls + brief template; agent-fleet: reply card; upstream plugins). Laptop: user scope · VM:
  managed settings (fixes D4) · box: baked into the image. **Machine facts in one separate per-machine file** (repo
  path, port block, Verifier URL), never in a soul (fixes D3). Cloud adapter (no /plugin, R10) delivers souls another
  way — decided when that adapter is built.
- Operator asked to read 6 humanlayer repos before continuing → R11.
- Default from R11 (small/reversible): the coordinator's "never edits code" is enforced by its tool set (no Edit/Write
  on project worktrees), not only by its persona text (fold Rlm.ts).

## Resolution (2026-10-01, closed by operator)

Q1 one unix user runs coordinator + all workers (own worktree / TMPDIR / port block each) · Q2 on the laptop the operator
is the coordinator, same briefs and `claude --agent <role>` workers · Q3 coordinator = a contract; front ends (terminal,
Discord, CLI, AG-UI) and worker backends (tmux laptop, tmux VM, cloud later, boxes) are adapters; tiers 0/1/2 opt-in ·
Q4 agent side = plugins everywhere (user scope / managed settings / baked into image); machine facts in one per-machine
file · coordinator rules enforced by its tool set · cloud backend later (R10: no GitLab push-back on Anthropic-hosted).
- Caveat (mattpocock ADR-0002:15, verified): Codex copies plugin trees and drops symlinks → "one skills tree symlinked
  into each harness" fails for Codex; needs a generated flat copy or Codex deferred. Matters only when Codex is used.
- ECC report: a Claude Code plugin cannot ship `.claude/rules` → rules stay project-side (agent-platform), consistent with
  Q-11; the agent-side plugin ships agents, skills, hooks only.
