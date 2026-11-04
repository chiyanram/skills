# R8 · How the references handle role, persona/SOUL and the SDLC around them

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G4, D1, the REQ

## Question

For firstmate, pstack, addy, mattpocock, humanlayer and openclaw: what is an agent's identity made of (persona,
soul, guardrails, memory), where does it live and who writes it, how is it installed on a machine, and how does a
role plug into the delivery process (intake → spec → build → review → verify → merge, human gates)? Compare with
ours: agent-fleet `agent.yaml` + `SOUL.md` → rendered `~/.claude/CLAUDE.md`; REQ-535 personas; `/crq`; G2 labels.

## Resolution (2026-10-01)

Findings: `../research/10-roles-souls-sdlc.md`. Persona lives outside the project in pstack, addy, firstmate,
openclaw (backs Q-11); mattpocock/humanlayer have no persona. Process owns steps, persona says who (backs G2).
Differences (risks): **D1** no reference chains one long-running agent per role stage to stage — they use one
coordinator + per-task workers given a brief; **D2** every reference with an identity lets lessons flow back into it
under a gate (pstack /reflect, firstmate PR, openclaw self-edit + tell user) — ours is frozen, lessons stay in private
memory; **D3** rendered role CLAUDE.md carries project facts (repo path, ports, verifier) → breaks S-10; **D4** agent
owns `~/.claude` (create-agent.sh:433; :504-509 comment confirms `claude plugin install` replaces the root-owned
settings file because the agent owns the dir) → "cannot rewrite who it is" is weaker than stated (inferred for
CLAUDE.md, not tested). 7 open questions.
