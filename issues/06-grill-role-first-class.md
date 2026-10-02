# G2 · Is a role first-class in /crq?

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: R3, R5 (closed)
Part of: ../map.md · Blocks: G4

## Question

Should `/crq` name its stages by owning role (analyst 1–3, spec-reviewer 5, developer 6, qa 7–8, human
2/5/9), so the laptop runs every role in sequence and the fleet runs one role each — from the same text?

## Grilling log

- Fact: process written twice — crq.md stages and each persona's own process; personas say "/crq exists … as a
  tool, not a process you're built on" (developer.md:13, analyst.md:13, spec-reviewer.md:15).
- **Q1 DECIDED (operator, 2026-10-01): A — ONE process text.** `crq.md` owns the steps, each stage tagged by role;
  role files (aruvii-agent-fleet) say only *who* (soul, guardrails, "run the stages tagged <role>").
- Operator caveat: crq.md must not name a specific agent ("aruvii-developer") — project side stays agent-agnostic.
  → crq tags a role LABEL (a contract), never an agent; any session that takes the label runs those stages.
- Q2 asked: where the role labels are defined.
- **Q2 DECIDED (operator): A — agent-platform defines the role labels** (analyst · spec-reviewer · developer · qa ·
  human) in a Roles table in its glossary; aruvii-agent-fleet roles point at it ("you take: developer").
- Reference backing (operator asked every decision be grounded in the references):
  Q1 ← addy `docs/agents.md` (command = when, persona = who, personas never call each other); pstack poteto-mode
  (playbook steps copied verbatim into the todo list — one process text). Q2 ← firstmate `AGENTS.md` §11 +
  `bin/fm-brief.sh` (the contract defines the worker role; the agent takes it).
- Q3 asked: handoff between labels.
- **Q3 DECIDED (operator): A — the GitLab comment is the record, Discord only pings** (transport is agent side).
- Default picked (small, reversible): the **work item (issue) is the identity**; the MR is one attempt. Handoff
  record goes where the work lives: stages 1–3 (no MR yet) → issue comment; stage 5 onward → MR comment, the
  issue linking the MR. Matches today's analyst "Handover:" issue comment and qa MR notes (fleet self-reports).
- Q4 asked: independence — may the session that wrote the code review it?
- **Q4 DECIDED (operator): A — a qa stage always runs in a FRESH, read-only context** (laptop: spawned subagent(s);
  fleet: the QA agent; boxes: the qa box). Backing: pstack interrogate (fresh, `readonly: true`, lead judges),
  mattpocock code-review (parallel subagents), addy (one role, one perspective). Size/cost of that context → G3.

## Resolution (2026-10-01)

1. **One process text**: `crq.md` (agent-platform) owns every step; each stage is tagged with a role label.
   Role files (aruvii-agent-fleet) carry only who: soul, guardrails, "you take: <label>".
2. **Labels are project-owned**: analyst · spec-reviewer · developer · qa · human, defined in a Roles table in
   agent-platform's glossary; crq.md never names an agent.
3. **Handoff**: the GitLab comment is the record (issue for stages 1–3, MR from stage 5, issue links MR);
   Discord / tool call / UI is only the transport, agent side.
4. **Independence**: qa always runs in a fresh, read-only context, in every lane.
