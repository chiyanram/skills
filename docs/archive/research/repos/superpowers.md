# obra/superpowers — deep report (2026-10-01)

Clone: `scratchpad/r9/obra_superpowers` @ `8ca22dba` (v6.4.2, 2026-09-25). Paths below are repo-relative.

## 1. What it is

| | |
|---|---|
| What | A **skills library + session bootstrap** that turns any coding agent into a fixed SDLC: brainstorm → spec → plan → subagent-driven (or native) execution → review → finish branch. Zero dependencies. |
| Maturity | v6.4.2; 14+ harnesses; eval lab (`superpowers-evals`, "Quorum") drives real CLIs (`AGENTS.md:102-104`, `docs/testing.md:25-37`); design specs carry measured $/token numbers (`docs/superpowers/specs/2026-06-10-strict-cost-sdd-design.md:13-20`). |
| Stars | Not in the clone. Popularity signal: "94% PR rejection rate" (`AGENTS.md:7`), listed in Anthropic's, OpenAI's and xAI's official marketplaces (`README.md:58-66,97,189`). |
| The one idea | **The bootstrap is the entire integration** (`docs/porting-to-a-new-harness.md:49-55`): inject `using-superpowers` at every session start; it orders the model to invoke a skill before *any* response (`skills/using-superpowers/SKILL.md:10-24`). Skills are behaviour-shaping **code**, tested like code (`AGENTS.md:93-100`). |

## 2. File tree (what matters)

```
.claude-plugin/{plugin,marketplace}.json   Claude Code manifest (no hooks key; hooks/hooks.json auto-found)
.cursor-plugin/ .codex-plugin/ .kimi-plugin/ .devin-plugin/ .muse-plugin/ .hermes-plugin/ .opencode/ .pi/
gemini-extension.json + GEMINI.md          Gemini: contextFileName → 2 @-includes (bootstrap + tool map)
.version-bump.json                         one version, 11 manifest fields kept in lockstep
hooks/
  hooks.json                               SessionStart matcher startup|clear|compact → run-hook.cmd
  run-hook.cmd                             bash/cmd polyglot (Windows)
  session-start                            cat using-superpowers/SKILL.md → JSON additionalContext, per-harness field
skills/                                    THE single source; every harness reads this tree verbatim
  using-superpowers/SKILL.md (65 l)        bootstrap: "1% chance → MUST invoke", red-flags table, harness refs
  using-superpowers/references/*-tools.md  per-harness action→tool mapping (7 files)
  brainstorming/                           3 paths (spike/bounded/architectural), HARD-GATE, spec reviewer prompt, visual companion server
  writing-plans/SKILL.md                   plan = decisions not code; Global Constraints + Review Focus + Interfaces
  subagent-driven-development/             controller loop + implementer / task-reviewer / re-review prompts
    scripts/{sdd-workspace,task-brief,review-package}   on-disk ledger, brief extraction, diff packet
  executing-plans/ + scripts/task-{start,done}          native (inline) mode, same ledger
  requesting-code-review/{SKILL.md,code-reviewer.md}    broad final/ad-hoc reviewer
  receiving-code-review/                   verify-then-act, no performative agreement
  test-driven-development/{SKILL.md,writing-good-tests.md}  (testing-anti-patterns.md was folded into the latter)
  verification-before-completion/          "evidence before claims" gate
  systematic-debugging/ dispatching-parallel-agents/ using-git-worktrees/ finishing-a-development-branch/
  writing-skills/                          TDD-for-skills, "Match the Form to the Failure", persuasion principles
  diagnosing-superpowers/                  transcript forensics, analyst subagent per dimension
docs/porting-to-a-new-harness.md           invariants + 3 integration shapes + acceptance test
docs/superpowers/{specs,plans}/            the repo eats its own dog food: every change is spec→plan
AGENTS.md                                  contributor rules (no CLAUDE.md — removed in v6.4.2)
tests/                                     plugin-infra tests; behaviour evals live in a separate repo
```

## 3. Approach

### a. Rules / standards

| Aspect | What they do | Evidence |
|---|---|---|
| Where rules live | Only in skills. No project rules at all — superpowers is *process*, project conventions go "in your instructions file" | `skills/writing-skills/SKILL.md:55-59` |
| Always-loaded | Exactly one skill body (`using-superpowers`, 65 lines) injected at startup/clear/compact | `hooks/hooks.json:5`, `hooks/session-start:11,27` |
| On demand | Every other skill, via the harness's Skill tool, triggered by the bootstrap's "1% chance" rule | `skills/using-superpowers/SKILL.md:11,20` |
| Single-source | Skills never name tools; per-harness mapping in `references/<harness>-tools.md`; "Do **not** edit skill bodies to fit your harness" | `docs/porting-to-a-new-harness.md:37-47,59-63` |
| Precedence | User instructions (CLAUDE.md/AGENTS.md) > skills > defaults | `skills/using-superpowers/SKILL.md:63-65` |
| Description discipline | Description = trigger conditions only; a workflow summary in it made agents skip the body (did 1 review not 2) | `skills/writing-skills/SKILL.md:150-158` |
| Token budget | getting-started skills <150 words, frequently-loaded <200 total | `skills/writing-skills/SKILL.md:215-221` |
| Rule form chosen by failure type | Prohibition+rationalization table for discipline; positive recipe for output shape; REQUIRED template slot for omissions; conditional on observable predicate | `skills/writing-skills/SKILL.md:461-476` |
| Measured doctrine | Composition prohibitions backfire (4.4 vs 3.6 control); positive recipe 3.0 zero variance; tripwires and recognition tables work | `docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md:12-33` |

Note the tension with our R2: superpowers relies on **description-triggered** pickup, but forced by an always-on "MUST check skills" bootstrap — and still ships an explicit-request test suite (`tests/explicit-skill-requests/`) because pickup is not guaranteed.

### b. Process / workflow

```
brainstorming ──classify──┬─ spike ──────► nod ──► report (throwaway)
                          ├─ bounded ────► in-chat design ──[HUMAN YES]──► implement (TDD), no plan
                          └─ architectural► Qs → 2-3 approaches → sections ──[YES]──► spec file
                                             ──[HUMAN reviews spec]──► writing-plans
writing-plans ──► plan file ──[HUMAN reviews plan + picks executor]──┬─ subagent-driven-development
                                                                    └─ executing-plans (native)
                         both ──► final whole-branch review ──► finishing-a-development-branch (3-option menu)
```

| Element | Detail | Evidence |
|---|---|---|
| Routing by size | spike / bounded / architectural; "when in doubt take the heavier"; one-way ratchet up | `skills/brainstorming/SKILL.md:58-88` |
| Human gates | HARD-GATE: each approval approves only the artifact shown; resume at earliest incomplete stage | `skills/brainstorming/SKILL.md:38-56` |
| Plan gate | "Approving an idea… no longer counts as approving a plan you haven't seen" | `RELEASE-NOTES.md:38`, `skills/writing-plans/SKILL.md:179-198` |
| Execution: no check-ins | Continuous; only 4 stops: irreversible, security, side effect outside worktree, plan so broken every path is a guess | `skills/subagent-driven-development/SKILL.md:17-31` |
| Rulings not stalls | Decide, ledger as `Ruling: what — why — cost if wrong`, surface all at the end | `skills/subagent-driven-development/SKILL.md:19-25,473-481` |
| State on disk | Per-plan git-ignored workspace `.superpowers/sdd/<plan>/`: `progress.md` ledger, `task-N-brief.md`, `task-N-report.md`, `review-<a>..<b>.diff` | `skills/subagent-driven-development/scripts/sdd-workspace:1-28`, `SKILL.md:131-154` |
| Resume after compaction | Ledger first line names the plan; `Task N: complete` lines are DONE; "trust the ledger and git log over recollection" | `skills/subagent-driven-development/SKILL.md:141-152` |
| Executor swap mid-flight | SDD and native share one workspace and ledger format | `skills/executing-plans/SKILL.md:121-123` |
| Pre-flight | Plan-conflict scan as a **table** (one row per shared interface pair + per task); "clean" without rows is not a scan | `skills/subagent-driven-development/SKILL.md:162-182` |

### c. Roles / personas

No personas or souls. Roles are **prompt templates filled per dispatch**, owned by the skill, never edited per project:

| Role | Made of | Who writes | Changes? |
|---|---|---|---|
| Controller | the session itself following SDD | — | — |
| Implementer | `implementer-prompt.md` + brief file path + 1-line context | controller fills | fixed template; model chosen per task (`SKILL.md:184-219`) |
| Task reviewer | `task-reviewer-prompt.md` + brief + report + diff packet + global constraints | controller | fixed |
| Re-reviewer | `re-review-prompt.md` + findings list + fix diff | controller | fixed |
| Final reviewer | `requesting-code-review/code-reviewer.md`, most capable model | controller | fixed |
| Spec reviewer | `brainstorming/spec-document-reviewer-prompt.md` | — | fixed |

Hard rule in every role: **"You Do Not Dispatch Subagents"** — measured: worker-spawned reviewers duplicated the task review (`skills/subagent-driven-development/SKILL.md:272-277`, `implementer-prompt.md:50-60`, `task-reviewer-prompt.md:55-62`). Bootstrap carries `<SUBAGENT-STOP>` (`using-superpowers/SKILL.md:6-8`) and OpenCode detects child sessions structurally because model compliance with that tag "is not reliable" (`.opencode/plugins/superpowers.js:145-154`).

### d. Review & verification

| Aspect | Per-task review | Re-review | Final review |
|---|---|---|---|
| Template | `task-reviewer-prompt.md` | `re-review-prompt.md` | `requesting-code-review/code-reviewer.md` |
| Inputs (pushed in, as files) | brief, implementer report, diff packet, global constraints verbatim | findings verbatim, brief, report, **fix diff only** | branch packet, plan, spec, Review Focus, ledger `Ruling:`/minor lines |
| Shape | ONE reviewer, two verdicts: Spec (✅/❌/⚠️) + Quality | ADDRESSED / NOT ADDRESSED per finding; new breakage in fix diff; out-of-scope → ledger | Strengths, Critical/Important/Minor, **Declined to judge** list, verdict |
| Scope guard | "diff's context lines ARE the changed files"; leave the diff only for a **named risk**, one check per risk | cannot re-review untouched code | broad by design |
| Tests | do not re-run; implementer report is evidence | same | — |
| Severity | Important = "cannot be trusted until fixed"; plan-mandated defects still Important, labeled | — | executor re-grades by effect on a reasonable user |
| Caps | 5 fix rounds: 1-3 resume implementer, 4-5 fresh implementer one tier up; then controller adjudicates | — | ONE fix wave, one scoped re-review, no second wave |
| Output | "begin directly with the verdict… no preamble, no closing summary" | same | — |

Evidence: `task-reviewer-prompt.md:38-50,73-92,94-113,135-160`; `re-review-prompt.md:55-62,80-100`; `SKILL.md:354-430,445-469`; `code-reviewer.md:33-48`.

History worth knowing: spec and quality reviews were **two subagents**, merged into one after evals showed per-dispatch overhead dominated (−32% time, −37% tokens, −27% $; quality 9/10 vs 7/10) (`docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md:31,54-70`). Quality reviewers inheriting a "Ready to merge?" frame ran 50+ repo-wide greps and cost 4-8× spec reviewers (`same:9-15`). Uncapped re-reviews were "the churn engine" (`docs/superpowers/specs/2026-07-15-sdd-fix-loop-redesign-design.md:15-21,37-44`).

Verification gate (not review): `verification-before-completion` — IDENTIFY command → RUN → READ → VERIFY → claim; "Agent completed ← VCS diff shows changes, not agent report" (`skills/verification-before-completion/SKILL.md:22-48`). Native mode replaces per-task reviewers with a **completion contract** enforced by `task-done`, which runs the tests and writes the ledger line only on exit 0 (`skills/executing-plans/SKILL.md:207-232`, `scripts/task-done:39-52`).

### e. Context engineering

| Technique | Evidence |
|---|---|
| Brief as a file, extracted by script; dispatch = 5-part recipe, exact values only in brief; "Never make a subagent read the whole plan" | `subagent-driven-development/SKILL.md:251-262`, `scripts/task-brief:30-36` |
| Never paste history: a real dispatch hit 42k chars, 99% pasted history | `SKILL.md:267-271` |
| Diff as a file the controller never reads (`review-package`, `-U10`, BASE guard rejects bad ranges, never `HEAD~1`) | `scripts/review-package:25-50` |
| Worker returns <15 lines; full report in a file | `implementer-prompt.md:128-149` |
| Model per role, **always explicit**; "turn count beats token price" — mid-tier floor for reviewers | `SKILL.md:184-219` |
| Optional: whole loop pushed one layer down to a mid-tier orchestrator subagent | `using-superpowers/references/claude-code-tools.md:9-29` |
| Bounded waits (5-10 min) + reconcile children, never short polls | `SKILL.md:235-244`, `references/codex-tools.md:39-60` |
| Bootstrap re-injected after compaction (`compact` matcher; pi `session_compact`) | `hooks/hooks.json:5`, `.pi/extensions/superpowers.ts:27-29` |
| Bookkeeping rides with work (ledger append in the same call as commit) | `executing-plans/SKILL.md:179-181` |

### f. Packaging & distribution

| Aspect | Detail | Evidence |
|---|---|---|
| One tree, many manifests | `skills/` + one bootstrap; 11 manifest version fields bumped together | `.version-bump.json:2-14` |
| Three integration shapes | A shell hook (Claude Code, Cursor, Copilot), B in-process plugin (OpenCode, pi, Hermes), C extension-shipped context file (Gemini) | `docs/porting-to-a-new-harness.md:6-26,208-215` |
| Hook emits the field each harness reads (Claude Code reads both and would double-inject) | `hooks/session-start:29-51` |
| Never edit the user's files — everything rides the harness install mechanism | `docs/porting-to-a-new-harness.md:65-77` |
| Acceptance test for a port: "Let's make a react todo list" must auto-trigger brainstorming; prove injection with a unique marker, not belief | `AGENTS.md:72-91`, `docs/porting-to-a-new-harness.md:118-125,200-206` |
| Install = one plugin command per harness; no per-machine config besides opt-in Codex backstop | `README.md:52-200`, `references/codex-tools.md:70-79` |
| Codex marketplace is a **synced copy** in a fork, made deterministic by script | `scripts/sync-to-codex-plugin.sh:5-13` |

### g. Hosting / UI

Only the brainstorming **visual companion**: zero-dep Node HTTP+WebSocket server on localhost, keyed URL, agent writes HTML to `screen_dir`, clicks land as JSON lines in `state_dir/events` read next turn (`skills/brainstorming/scripts/server.cjs:1-40`, `visual-companion.md:29,51-52,258-270`). No daemon, no approvals protocol; approvals are chat turns.

## 4. Three excerpts worth studying

1. **`skills/subagent-driven-development/SKILL.md:19-31` + `473-481`** — "Rulings, not stalls" plus four named stops, and the end-of-run "Rulings I made" list. Autonomy with an audit trail: every decision the agent took on the human's behalf reaches them, each priced "cost if wrong". Exactly what a coordinator relaying to a human needs.
2. **`skills/subagent-driven-development/task-reviewer-prompt.md:38-50` + `64-71` + `145-157`** — diff-packet-first reading, breadth only for a *named* risk, "Do Not Trust the Report" (rationales like "per YAGNI" never downgrade severity), Important defined as "cannot be trusted until fixed", plan-mandated defects still reported. Tight, measured, cheap.
3. **`skills/writing-skills/SKILL.md:461-476`** — "Match the Form to the Failure" table, backed by `docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md:12-33`. The best evidence-based rule for *how to phrase* any rule we write in the G5 references.

Runner-up: `skills/writing-plans/SKILL.md:77-87,140-161` — Review Focus (five untested input classes, each pinned by a test) and "a plan longer than the code it describes has written the code".

## 5. Against our decisions

| Decision | Verdict | Why (evidence) |
|---|---|---|
| **G1** rules layers, AGENTS.md index, bodies on demand | **Confirms**, with a twist | one tiny always-on bootstrap, everything else on demand (`hooks/session-start:27`); but project rules are explicitly out of scope — "put in your instructions file" (`writing-skills/SKILL.md:58`). Their `CLAUDE.md` was deleted because CC reads `AGENTS.md` only when no `CLAUDE.md` exists (`RELEASE-NOTES.md:17`) — **check our `CLAUDE.md = @AGENTS.md` plan against that** |
| **G1** upstream = plugins, never copies | **Confirms** | "Manually copying skill files… will be closed" (`AGENTS.md:84-89`) |
| **G2** one crq, stages tagged by role label | **Confirms** | roles are templates the process owns, not identities (`subagent-driven-development/*-prompt.md`); size-routing (spike/bounded/architectural) is a **new idea** for our "routing by task type" gap (`brainstorming/SKILL.md:58-88`) |
| **G3** Standards ‖ Spec review | **Contradicts (per task)** / confirms (final) | they **merged** spec+quality into one reviewer, two verdicts, after measuring dispatch overhead (`specs/2026-06-09…:31,54-59`); kept one separate broad final review. Our two parallel axes double the per-dispatch cost they cut |
| **G3** inputs pushed in, fresh read-only, 3-round cap | **Confirms** | diff packet as file, read-only (`task-reviewer-prompt.md:38-53`); cap is 5 with escalation at 4 (`SKILL.md:372-386`); scoped re-review = our "fix diff only after round 1" (`re-review-prompt.md:55-62`) |
| **G3** references by changed path | **No equivalent** | criteria are fixed in the template + `[GLOBAL_CONSTRAINTS]` from the plan (`task-reviewer-prompt.md:25-26,194-197`); nothing selects by path |
| **G5** 5-section references | **Partly confirms** | Good/Bad pairs (`test-driven-development/SKILL.md:75-106`), rationalization tables, gate functions (`writing-good-tests.md:65-79`); adds **form-by-failure** rule (`writing-skills/SKILL.md:461-476`) for the "Review checks" section |
| **G6** coordinator + briefed workers | **Strongly confirms** | brief file per task, report file back, <15-line return, workers never spawn agents, controller never fixes (`SKILL.md:251-283,408-410`); adds ledger-for-compaction and rulings list |
| **G6** qa fresh per round | **Contradicts mildly** | fix rounds 1-3 **resume** the same implementer; only reviewer is fresh (`SKILL.md:375-386`) — matches us for qa, differs for dev |
| **G4** plugins everywhere / one machine file | **Confirms** | one install command per harness, no user-file edits (`porting…:65-77`); version lockstep (`.version-bump.json`) |
| **G4** coordinator-as-contract, front/back adapters | **Confirms the pattern** | skills name actions; per-harness tool map is the adapter (`porting…:37-55`) |
| **G4** tiers 0/1/2 | **Echo** | SDD vs Native is a cost tier choice offered with a recommendation (`writing-plans/SKILL.md:187-194`) |
| **Q-6** talking set from session start, survives `/compact` | **Confirms mechanism** | SessionStart matcher `startup|clear|compact` (`hooks/hooks.json:5`) |

## 6. ADOPT / ADAPT / REJECT (ranked)

| # | Call | What | File that shows it |
|---|---|---|---|
| 1 | **ADOPT** | Review packet as a file + scoped re-review (findings + fix diff only, out-of-scope → ledger) | `scripts/review-package`, `re-review-prompt.md:55-100` |
| 2 | **ADOPT** | "Do Not Trust the Report" + Important = "cannot be trusted until fixed" + plan-mandated defects still flagged | `task-reviewer-prompt.md:64-71,145-157` |
| 3 | **ADOPT** | Workers never spawn subagents; return <15 lines; full report to a file | `implementer-prompt.md:50-60,128-149` |
| 4 | **ADOPT** | Rulings ledger `Ruling: what — why — cost if wrong`, all surfaced at the end; 4 named stops | `subagent-driven-development/SKILL.md:19-31,473-481` |
| 5 | **ADOPT** | "Match the Form to the Failure" as the authoring rule for every G5 reference | `writing-skills/SKILL.md:461-476` |
| 6 | **ADOPT** | Bootstrap re-injected on `startup|clear|compact`, emitting only the field the harness reads | `hooks/hooks.json:5`, `hooks/session-start:29-51` |
| 7 | **ADAPT** | On-disk per-work-item ledger (`progress.md`) for compaction/resume — put it in the worker's worktree; GitLab comment stays the human record | `scripts/sdd-workspace`, `SKILL.md:131-154` |
| 8 | **ADAPT** | Merge Standards+Spec into one reviewer with two verdicts **for small diffs**; keep two axes for large ones — measure with P1 re-run (A-1) before deciding | `specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md:54-70` |
| 9 | **ADAPT** | Spike / bounded / architectural classification at `/crq` stage 1 (fills our "routing by task type" gap) | `brainstorming/SKILL.md:58-108` |
| 10 | **ADAPT** | Plan "Review Focus" (≤5 untested input classes, each pinned by a test) → stage-5 design output feeding qa | `writing-plans/SKILL.md:77-87,173` |
| 11 | **ADAPT** | `task-done`: a script writes "complete" only on a green test exit — a cheap hook for "stated it passes without running it" | `executing-plans/scripts/task-done:39-52` |
| 12 | **ADAPT** | Explicit model per dispatch; mid-tier floor for reviewers (turn count beats token price) | `subagent-driven-development/SKILL.md:184-219` |
| 13 | **REJECT** | "1% chance → MUST invoke" description-driven pickup as our trigger — R2 shows "Run X" from a stage wins; keep Q-4 | `using-superpowers/SKILL.md:10-24` |
| 14 | **REJECT** | Auto-continue with no human between tasks for **merge-affecting** steps — our `/approved` gate and human merge stay | `subagent-driven-development/SKILL.md:17` |
| 15 | **REJECT** | ALL-CAPS persuasion ("EXTREMELY-IMPORTANT", "Delete means delete") for our references — fine for discipline, backfires for shape per their own data | `writing-skills/persuasion-principles.md:11-28` vs `writing-skills/SKILL.md:470-476` |

## 7. Files actually read

```
AGENTS.md
GEMINI.md
README.md (install section, Basic Workflow, What's Inside, Philosophy)
RELEASE-NOTES.md (v6.4.2, v6.4.1 head)
package.json
index.js
gemini-extension.json
.version-bump.json
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.codex-plugin/plugin.json
.cursor-plugin/plugin.json
.devin-plugin/plugin.json
.kimi-plugin/plugin.json
.hermes-plugin/plugin.yaml
.hermes-plugin/__init__.py (1-90)
.opencode/plugins/superpowers.js (1-215 + hook lines 216-383 via grep)
.pi/extensions/superpowers.ts
hooks/hooks.json
hooks/hooks-cursor.json
hooks/run-hook.cmd
hooks/session-start
scripts/sync-to-codex-plugin.sh (1-30)
docs/porting-to-a-new-harness.md (1-300 + headings)
docs/testing.md (1-40)
docs/superpowers/specs/2026-06-10-strict-cost-sdd-design.md (1-90)
docs/superpowers/specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md (1-70)
docs/superpowers/specs/2026-07-15-sdd-fix-loop-redesign-design.md (1-60)
docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md (1-45)
skills/using-superpowers/SKILL.md
skills/using-superpowers/references/{antigravity,claude-code,codex,gemini,hermes,muse,pi}-tools.md
skills/brainstorming/SKILL.md
skills/brainstorming/spec-document-reviewer-prompt.md
skills/brainstorming/visual-companion.md (grep)
skills/brainstorming/scripts/server.cjs (1-40)
skills/writing-plans/SKILL.md
skills/subagent-driven-development/SKILL.md
skills/subagent-driven-development/implementer-prompt.md
skills/subagent-driven-development/task-reviewer-prompt.md
skills/subagent-driven-development/re-review-prompt.md
skills/subagent-driven-development/scripts/{review-package,sdd-workspace,task-brief}
skills/executing-plans/SKILL.md
skills/executing-plans/scripts/{task-start,task-done}
skills/requesting-code-review/SKILL.md
skills/requesting-code-review/code-reviewer.md
skills/receiving-code-review/SKILL.md
skills/test-driven-development/SKILL.md
skills/test-driven-development/writing-good-tests.md
skills/verification-before-completion/SKILL.md
skills/dispatching-parallel-agents/SKILL.md (1-80)
skills/finishing-a-development-branch/SKILL.md (1-120)
skills/using-git-worktrees/SKILL.md (headings)
skills/systematic-debugging/SKILL.md (1-40 + headings)
skills/writing-skills/SKILL.md (1-60, 140-278, 461-595 + headings)
skills/writing-skills/persuasion-principles.md (1-30)
skills/writing-skills/testing-skills-with-subagents.md (1-40)
skills/diagnosing-superpowers/SKILL.md (1-70)
tests/explicit-skill-requests/prompts/skip-formalities.txt
```

Not read: `skills/writing-skills/anthropic-best-practices.md`, `docs/plans/*`, most `docs/superpowers/plans/*`, `tests/*` bodies, brainstorm server beyond line 40. Note: no `testing-anti-patterns.md` exists any more — its content is `test-driven-development/writing-good-tests.md`.
