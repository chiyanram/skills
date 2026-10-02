# D1 · Design sketch: role boxes — Agent SDK + AG-UI, laptop and VM from one compose (FINAL STEP)

Type: wayfinder:research (AFK, design-on-paper now) · Status: open · Assignee: claude · Blocked by: — (paper design);
execution blocked by G1, G2, G3, G4, P1
Part of: ../map.md

## Question

What is the structure of a role box (analyst, spec-reviewer, developer, qa) modelled on MasterLaundry's Ask Me box
(`refs/imdganesancareers-MasterLaundry/docker/ask-me/`, `packages/askme-box/`), speaking AG-UI to one web UI?
Cover: container layout + compose (laptop and VM identical), how the rulebook loads (`settingSources`, plugins,
mounted repo), repo/git/glab credentials and workspace per role, sandbox + egress, the human gates (`/approved`,
merge) as AG-UI human-in-the-loop events, role→role handoff (today Discord @mention), Verifier integration, session
lifetime and memory, cost/observability, and the migration path from agent-fleet's tmux+Discord. Open questions for
the operator listed at the end, not answered by assumption.

## Paper design delivered (2026-10-01)

`../research/07-role-box-design.md`: web UI ⇄ AG-UI (HTTP+SSE) ⇄ one gateway ⇄ 4 role boxes + Verifier service,
one egress allowlist proxy (Ask Me pattern). Rulebook via `settingSources: ['project']` + plugins in image; persona
= `docs/agents/personas/<role>.md` (same file as laptop); `~/.claude/CLAUDE.md` does NOT load in boxes. Git rules
become hard denies in `canUseTool`. Docker: per-box privileged DinD sidecar for targeted ITs; `make verify-full`
in Verifier service; host socket rejected. ~34g RAM all profiles on (unmeasured). Gates: gateway watches GitLab for
`/approved` / merge → resumes paused run; handoff = tool call. AG-UI Agent-SDK adapter v0.0.4, no subagent events
(ag-ui #2755). 8 reversible migration steps; 12 open operator questions. Ticket stays OPEN: execution is the final step.
- Update needed (after G6, 2026-10-01): the paper design assumed 4 standing role boxes; G6 decided one coordinator +
  per-task worker sessions → D1 becomes one coordinator box + short-lived worker boxes. Also R8 D5: openclaw uses
  `AGENTS.md` for the agent's own operating file, we use it for the project index — naming clash if adopted in boxes.
- R11 input: humanlayer hld daemon (REST+SSE, approvals via --permission-prompt-tool; deprecated); fold/agentlayer split a
  durable event log from live deltas, approvals pause and resume possibly in another process → maps to AG-UI interrupts.
- openclaw Gateway: every front end (Slack, Discord, Telegram, web, CLI) is a client of one gateway; approvals are events
  any client can resolve → same shape as D1's AG-UI gateway.
- Repo report humanlayer-fold-agentlayer.md: ADOPT for D1 — fold's session interface (send/steer/stop/interrupt +
  events(fromSeq): durable log rows + live deltas tagged agent/parent/tool call) and agentlayer's approval protocol
  (request events from any depth on one root stream; resolve live or later from saved state; partial approval). These
  map onto AG-UI runs/events/interrupts. Do NOT build on either codebase (fold 0.0.0 on Effect v4 rc; agentlayer legacy).
