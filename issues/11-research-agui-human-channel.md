# R6 · AG-UI as the human↔agent channel for laptop + SSH agents (replacing Discord + `claude -p`)

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G4

## Question

Operator intent (2026-10-01): AG-UI was meant as the interface for driving the dev agents — on the laptop and on
the SSH machine — instead of Discord, with Claude Code headless (`claude -p` / Agent SDK) behind it. Can it?
What does an AG-UI front end over Claude Code look like (event mapping: text, tool calls, human approval / gates
like `/approved`), what existing project on the laptop already does this ("master laundry" — location TBC), and what
does it change for G4 distribution? Note R5: `--bare` / `-p` skip CLAUDE.md, plugins, hooks unless configured.

## Facts so far (2026-10-01, from refs/imdganesancareers-MasterLaundry — infra only, business ignored)

"Ask Me" box = the pattern the operator means:
- `docker/ask-me/docker-compose.yml`: compose profile `ask-me`; `askme-box` (Node, Claude Agent SDK) on an
  `internal` network; `askme-egress` CONNECT proxy allowing only `api.anthropic.com:443`; `askme-firewall`
  one-shot iptables (NET_ADMIN) on a shared netns before the box starts; read-only FS, tmpfs `/workspace`,
  cap_drop ALL, mem 2g / 2 cpu; `CLAUDE_CODE_OAUTH_TOKEN` from server `.env` (same token model as agent-fleet).
- `packages/askme-box/src/session.ts`: one long-lived streaming `query()` per session (inbox pushes user turns),
  `permissionMode: 'default'` + `canUseTool` gate, **`settingSources: []`** (loads NO CLAUDE.md / skills / rules —
  persona given as `systemPrompt` from `persona.md`), in-process MCP tools (`tools.ts`), idle timeout.
- `server.ts`: plain JSON over HTTP :4600, called by the app. **No AG-UI in the repo.**
Implication for G1/G4: a dev-agent box must set `settingSources: ['project', …]` or the rulebook never loads.

## Resolution (2026-10-01, operator)

**C now, A last.** Keep Discord + Claude Code CLI in tmux while the rulebook is fixed (G1–G4, P1). Record
**A — one Ask-Me-style box per role (Agent SDK in a container, AG-UI to one web UI, same compose on laptop and
VM, replacing tmux + Discord)** as the map's final step, after everything else lands. Design it now on paper:
ticket D1 (`12-design-role-boxes.md`).
