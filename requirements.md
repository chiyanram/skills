# Requirements — one-rulebook map  (confirmed by operator 2026-10-01)

Plain list of what this map must deliver. Decisions that satisfy each live in the tickets (see map.md).

## Must

| # | Requirement | Why (evidence) |
|---|---|---|
| Q-1 | Every rule is **defined in exactly one file**; everything else points at it | R1: Java rules ×4–5, AssertJ ×12, 5 contradictions |
| Q-2 | **Agent-agnostic**: `AGENTS.md` is the index, `CLAUDE.md` = `@AGENTS.md`, skills in one tree linked into each harness | G1 Q1b; R3 (firstmate, addy, Anthropic docs) |
| Q-3 | Always-loaded text stays small (`AGENTS.md` < 200 lines); bodies load on demand | R1: CLAUDE.md = 60% of startup; Anthropic memory docs |
| Q-4 | A skill fires because a **stage orders it** ("Run X"), not by hoping its description matches | R2: "Run X" 5/5, mention 0/1; 8 skills never fired |
| Q-5 | **Upstream skills come as plugins, never copies**; repo-specific answers live in `docs/agents/*.md` | G1 Q2; #587 (19 stale forks) |
| Q-6 | The **talking set** (i-have-adhd, show-me, teach, wait-what) is active **from session start** everywhere | operator, G1 Q2 |
| Q-7 | **Laptop and fleet load identical files** — no second copy of rules or souls | R1: soul ×3; fleet role file replaces `~/.claude/CLAUDE.md` |
| Q-8 | `/crq` stages are **owned by role**, so one text serves the laptop (all roles) and the fleet (one role each) | fleet self-reports: nobody runs /crq end to end |
| Q-9 | Review is **diff-scoped**: criteria chosen by changed paths, diff pushed in, findings only; `spec-design-reviewer` removed | R4: ~$2–2.8/review, 62–66% thinking |
| Q-10 | The output is a **REQ ready for `/crq`**, not the implementation | map destination |
| Q-11 | **Agent side vs project side.** Identity, role, soul, talking rules, user prefs travel with the agent (written at agent creation as its user-level CLAUDE.md + plugins), usable on any project; the project repo carries only project rules, skills and `/crq` | operator 2026-10-01; firstmate §1–2, §6, §11; addy docs/agents.md; pstack poteto-agent |

## Final step (after the above lands)

| F-1 | Role boxes: Agent SDK container per role, AG-UI web UI, one compose for laptop + VM, replacing tmux + Discord | R6, D1 |

## Scenarios the design must pass

| # | Scenario | Must be true |
|---|---|---|
| S-1 | You open any Claude session on the laptop, in any repo | talking set active from turn 1, and still active after `/compact` |
| S-2 | You run `/crq 600` on the laptop | each stage says which role it is and which skill/workflow to run; you play every role |
| S-3 | The fleet developer picks up an approved story on the VM | it loads the project's `AGENTS.md`, rules and skills from its clone, and its OWN role from its user-level CLAUDE.md + plugins — the same agent-side package a laptop session can load |
| S-10 | The same developer agent is pointed at a different repo | its role and talking rules come with it; only the project side changes |
| S-4 | A developer writes a new Spock test | `testing` → write-a-test runs; the test rules load from ONE file; no copy in CLAUDE.md |
| S-5 | QA reviews !NNN | reviewer gets the diff + only the criteria for the touched paths; returns findings only |
| S-6 | mattpocock ships a new `grilling` version | updating the plugin is the whole upgrade; nothing in this repo to re-copy |
| S-7 | A rule changes (e.g. AssertJ → Spock asserts) | one file edits; laptop and VM both see it on next session |
| S-8 | You start Codex/Cursor in this repo instead of Claude | it reads `AGENTS.md` and the same skills tree |
| S-9 | A new teammate clones the repo | one documented install step gets the plugins; nothing else to copy by hand |

## Acceptance evidence the REQ must produce

| A-1 | After the references are rewritten to the G5 shape, re-run P1 on !230 round 1 (head 70b84c0b) with ONE reviewer giving two verdicts (G3 amendment) from the merged packet; show run 2 vs run 1 (`p1/lead-judgment.md`) vs the real QA rounds: findings caught, misses (F6 `final`, F7 boundaries must now be caught), subagent tokens | operator 2026-10-01 |
| A-2 | `testing/workflows/audit.md` is run on one real package before it ships; every "missing test" and "delete" finding is checked by hand (or by P1-style lead judgment) and the hit rate is reported; ship only if the operator accepts it | operator 2026-10-01 (G9a Q1) |
