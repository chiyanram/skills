# Design overview v2 — the whole picture after G1, G2, G3, G5, G6, G4-Q1 (2026-10-01)

> **SUPERSEDED (2026-10-17).** This is the 2026-10-01 picture. Changed since: no aruvii-agent-fleet repo — all agent
> side is in agent-fleet (G1 amendment skills #14, 2026-10-03); generic skills, references and crq live in
> chiyanram/skills as a plugin, agent-platform keeps only Aruvii (G23 #93); `.claude/rules/` → nested AGENTS.md
> (G1b skills #72); two zones and a worker container instead of one unix user (G13 #69); one reviewer with no Act-on
> cap (G3 amendment, G17 #87); the forge thread is the record (G19 #89). Current picture: map #9 and
> `research/00-decision-register.md`.

```
 THREE REPOS (G1 Q3, Q4)
 agent-fleet (generic tooling)      aruvii-agent-fleet (Aruvii crew)             agent-platform (the project)
 create/update/delete scripts       coordinator persona                          AGENTS.md index (CLAUDE.md=@AGENTS.md)
 reply-card plugin (talking)        role souls: analyst·spec-rev·dev·qa           .claude/rules (path MUSTs)
 enforcement · Verifier             brief templates (G6)                          skills/ testing·code·obs·migrations·…
                                    shipped as a plugin: agents/*.md (G4 Q?)      crq.md, stages tagged by role label
                                                                                  Roles table (labels, G2)
 UPSTREAM PLUGINS (G1 Q2, Q4): mattpocock · humanlayer show-me · ayghri i-have-adhd — never copied

 RUNTIME (G6, G4 Q1) — one unix user
 you ⇄ Discord ⇄ COORDINATOR (always on; firstmate hard rules; relays every question with context)
                     │ per (work item, role): new tmux window + worktree + TMPDIR + port block
                     ├─ 600-analyst  claude --agent analyst   brief: #600 · stages 1–3
                     ├─ 600-dev      claude --agent developer brief: #600 · stage 6 (+ ≤3 fix rounds)
                     └─ 600-qa-r1    claude --agent qa        brief: !NNN · round 1 (fresh every round)
                     each worker loads: project side from its worktree · agent side from plugins
                     record = GitLab issue/MR comment (G2) · teardown after merge (G6)

 REVIEW (G3, G5): Standards ‖ Spec, fresh read-only, packets pushed in, references by changed path
                  (5-section references: Rules · When X use Y · Good/Bad pinned · Edges · Review checks)
                  lead judgment (Act on ≤5…), 3-round cap · P1 confirmed shape on !230

 FINAL STEP (R6, D1): coordinator box + worker boxes, AG-UI web UI replaces Discord + tmux
```

## Consistency check (2026-10-01)

| # | tension | between | status |
|---|---|---|---|
| T1 | laptop: "you play every role" vs "a coordinator spawns workers" | G2 vs G6 | open → G4 Q2 |
| T2 | D1 paper design has 4 standing role boxes | D1 vs G6 | noted on D1 |
| T3 | REQ-535 personas live in agent-platform `docs/agents/personas/` | REQ-535 vs G1 Q3 | REQ moves them to aruvii-agent-fleet |
| T4 | `AGENTS.md` means project index (us) vs agent's own file (openclaw) | G1 vs R8 D5 | only matters for D1 |
| T5 | talking set "everywhere" but workers never talk to you | Q-6 vs G6 Q3 | fine: shapes coordinator replies + workers' GitLab comments |
