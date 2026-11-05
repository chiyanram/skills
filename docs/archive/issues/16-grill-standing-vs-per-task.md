# G6 · Standing agent per role, or coordinator + per-task workers?

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G4, D1

## Question

Keep four long-running agents, one per role, handing off stage to stage (ours today) — or move toward the reference
shape: one coordinator that gives each task a brief and spawns a fresh worker with the role (firstmate, pstack
orchestrate/autopilot)? Evidence: R8 D1; fleet failures cluster at handoffs (silence, findings in rounds).

## Grilling log

- Mechanics shown (firstmate bin/fm-spawn.sh, bin/backends/tmux.sh): each worker = a new INTERACTIVE claude in its own
  tmux window + own git worktree, first message = a brief; not `claude -p` (can't be watched/steered; skips
  project-scope plugins, R5). Role + soul from the brief; project rules from the worktree; talking set from plugins.
- **Q1 DECIDED (operator, 2026-10-01): A — one always-on coordinator + fresh per-task worker sessions.** You talk to
  the coordinator (Discord for now); it spawns workers with briefs, watches for silence, enforces the round cap.
  aruvii-agent-fleet's 4 roles become brief templates + souls; agent-fleet provisions one always-on agent.
- Q2 asked: worker lifetime — per stage, or per (work item, role)?
- Operator asked: (1) don't agents just compact and keep going? — references keep long-lived sessions only for the
  coordinator, and even there truth lives in files/forge, not memory (firstmate §5 "A restart must be a non-event";
  pstack principle-guard-the-context-window:9 "finite and non-renewable within a session"; 12-factor #3, #10).
  (2) who cleans up? — the coordinator tears down a worker's window + worktree once its work landed (firstmate hard
  rule 3 + bin/fm-teardown.sh; our aruvii-cleanup asks GitLab). (3) fewer unix users / caps? → feeds G4: one
  coordinator user can run all workers (fewer users, one GitLab identity), but concurrent workers still share
  /tmp, ports, Docker, RAM → caps stay.
- **Q2 DECIDED (operator): A — one worker per (work item, role)**: e.g. 600-dev lives through stage 6 and its ≤3 fix
  rounds, then the coordinator tears it down; qa is a fresh worker each round.
- Q3 asked: the coordinator's hard rules.
- **Q3 DECIDED (operator): A — coordinator adopts firstmate's 5 hard rules**: never edits code · never posts
  /approved or merges · never tears down unlanded work · workers never address the human (only the coordinator talks
  to you; workers write the GitLab record) · report outcomes faithfully.
- Q4 asked: human-in-the-loop stages (2 grill, 5 refine) under rule 4.
- **Q4 DECIDED (operator): A — the coordinator relays every worker question to the human, standalone, with work
  item + stage + recommendation** (firstmate §9; operator's own "decision with its context" rule).

## Resolution (2026-10-01)

1. **One always-on coordinator** (you talk only to it; Discord for now) + **fresh interactive worker sessions**
   (own tmux window + own worktree, first message = a brief: role label + soul + work item + stage), not `claude -p`.
2. **Lifetime**: one worker per (work item, role), living through its stage and ≤3 fix rounds; qa fresh each round;
   coordinator tears down after GitLab says merged, never unlanded work.
3. **Coordinator hard rules** (firstmate §1): never edits code · never /approved or merges · never tears down unlanded
   work · workers never address the human · report faithfully.
4. **HITL stages**: coordinator relays each worker question with full context; you answer the coordinator.
Consequences: aruvii-agent-fleet's 4 roles → brief templates + souls + 1 coordinator persona; agent-fleet provisions
one always-on agent; D1 becomes coordinator box + worker boxes; unix-user / identity questions → G4.
- Post-close input (pstack report, orchestrate.md:13-109): 9-field worker brief, spawn REFUSED if a field is missing,
  standing orders pasted verbatim into every spawn, parked questions carry a default answer → brief template in the REQ.
  Contrast: pstack "a worker cannot ask you a question" (orchestrate.md:11) vs our G6 Q4 relay — kept relay.
- addy anti-pattern C (orchestration-patterns.md:316-326, verified): an orchestrator running spec→plan→build fails by
  (1) losing human checkpoints, (2) drift from paraphrased hand-offs, (3) double tokens. Our G6 answers: (1) human gates
  2/5/9 + relay kept; (2) brief carries standing orders verbatim + GitLab record, no paraphrase; (3) coordinator does
  no stage work itself — cost to measure in the REQ.
- Post-close input (openclaw, verified templates/roles/{coordinator,researcher,writer,reviewer}): each role = 1-paragraph
  soul + ~50-line operating program under fixed headings incl. a Handoff contract; coordinator routes all results;
  specialists never delegate; a blocked specialist gets ONE clarified follow-up before escalation → brief template.
- firstmate fm-brief.sh:529-536: captain's own words kept apart from the coordinator's build spec in the brief; worker
  role prepended at every launch and overrides project files (fm-dod-lib.sh:108-122); status words needs-decision /
  blocked ("same obstacle twice") / done; scripts refuse "done" for unpushed work → GitLab comment shape + brief.
- humanlayer create_handoff/resume_handoff: what to write before ending a session; next session re-checks it → brief/handoff
  format. ace-fca.md:318-333: review effort belongs on research + plan → many code-review rounds signal a thin plan stage.
