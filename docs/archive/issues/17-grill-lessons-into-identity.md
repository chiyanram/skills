# G7 · Where do lessons go, and may an agent propose edits to its own role?

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G4

## Question

When a role learns something (e.g. "run existing specs touching the changed set", "verify repo facts before
stating them"), where does it land — role file (aruvii-agent-fleet), project reference (agent-platform), or private
memory — and through which gate (PR you approve, /reflect-style proposal)? Evidence: R8 D2 (pstack /reflect,
firstmate PR, openclaw self-edit + tell user).

## Inputs
- R11: humanlayer `thoughts/` dir + `create_handoff` / `resume_handoff` commands; pstack /reflect; firstmate PR (R8).
- mattpocock `retro/SKILL.md:19,29-35`: mechanical rule → hook/check; judgement rule → the standards file; the
  reviewer carries the standards.
- pstack `reflect` synthesizer criteria (see research/repos/pstack.md) — candidate lesson loop.
- openclaw: agent updates AGENTS.md / USER directives in place ("update instructions at their owner instead of adding
  competing rules") — adapt via MR. Claw packages: versioned agent setups, consent tied to a digest, drift check (D4).
- firstmate AGENTS.md:154-156 + no-mistakes memory_files.go:12-18 (verified): agents may only CORRECT AGENTS.md/CLAUDE.md,
  never ADD — additions are a human decision because they tax every future session.
- firstmate-coding-guidelines:18-64: 7-tier placement tree, one owner per fact → where a lesson lands.
- humanlayer-skills agent-iteration.ts:76-84 (verified): reviewer comments `/iterate` on a PR → agent fixes the PR AND writes
  lasting guidance into a memory file, leaving out PR-only feedback; one open PR per loop.
- BMAD best-practices.md: delete an AGENTS.md rule on only 4 grounds (:75-82); no rule in two loaded files; a pointer
  out of the index needs an observable trigger (:51).

## Grilling log

- **Q1 DECIDED (operator, 2026-10-01): A — agents PROPOSE via MR against the file that owns the rule; the operator
  merges.** In its own MR an agent may CORRECT a wrong line, never ADD one. Project lessons → agent-platform reference;
  role lessons → aruvii-agent-fleet soul. Backing: firstmate AGENTS.md:154-156, no-mistakes memory_files.go:12-18,
  pstack /reflect, humanlayer /iterate, BMAD best-practices.md:75-82.
- Q2 asked: when is a lesson captured, and how is "durable" told apart from "MR-only"?
- **Q2 DECIDED (operator): A — retro at work-item close + `/lesson <text>` on demand.** On merge the coordinator spawns a
  fresh retro worker (reads MR thread, findings, round count, worker reports) and sorts each item: MR-only → dropped ·
  mechanical → propose a check (lint/test/hook) · judgement about code → line in the agent-platform reference ·
  judgement about role → line in the aruvii-agent-fleet soul · ≤2 MRs per work item. Default picked (small): machine /
  environment lessons (DOCKER_HOST, JAVA_HOME) → the per-machine file or agent-fleet provisioning, same MR route.

## Resolution (2026-10-01)

Agents never edit the rulebook directly; they propose MRs to the one owning file and the operator merges (they may
correct, never add, inside their own MR). Capture = retro worker at work-item close + `/lesson` on demand; sorted into
dropped / check / project reference / role soul / machine file; ≤2 MRs per work item.
Backing: firstmate AGENTS.md:154-156, no-mistakes memory_files.go:12-18, mattpocock retro:19, pstack reflect:13,
humanlayer agent-iteration.ts:80, BMAD best-practices.md:75-82.
