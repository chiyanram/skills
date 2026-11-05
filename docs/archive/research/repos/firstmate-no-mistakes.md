# firstmate + no-mistakes — per-repo deep report (one-rulebook map, 2026-10-01)

Two repos by the same author (kunchenguid). firstmate is the **command layer** (coordinator + briefed workers);
no-mistakes is the **validation layer** firstmate delegates all review to. Read together they are the closest
existing match to our G6 + G3 design. Paths below are relative to each repo root:

- F = `.scratch/one-rulebook/refs/kunchenguid-firstmate`
- N = `scratchpad/r9/no-mistakes`

---

# Part A — firstmate

## A1. What it is

| | |
|---|---|
| What | "agent distro": a cloned repo whose `AGENTS.md` turns any harness into a fleet supervisor (README.md:36-40) |
| Maturity | very active; HEAD commit is PR #6255 (2026-09-30); shallow clone so history depth unknown |
| Stars | not in clone — unknown |
| Harnesses | claude, codex, opencode, pi, grok, kimi, cursor, omp + crew-only muse, gemini, rovo, agy, devin (AGENTS.md:90) |
| Session backends | tmux (reference), herdr, zellij, cmux, orca (`bin/backends/*.sh`) |
| The one idea | **"Scripts own the mechanics, agents own the judgment"** (VISION.md:32-39) + the captain talks to one agent only (VISION.md:10-19) |

## A2. File tree (what matters)

```
firstmate/
├── AGENTS.md              426 lines — the ENTIRE supervisor contract, always loaded (14 sections)
├── CLAUDE.md              "@AGENTS.md" one-liner (CLAUDE.md:1-2)
├── VISION.md              78 lines — product principles; 9,000-word ceiling on always-loaded text (:39)
├── .no-mistakes.yaml      gate config: disable_project_settings, document/test instructions, lint cmd
├── .claude/
│   ├── settings.json      hooks: SessionStart · PreToolUse(Bash, .*) · UserPromptSubmit · Stop(asyncRewake)
│   └── skills -> ../.agents/skills      (symlink — one tree for every harness)
├── .agents/skills/        29 agent-only skills, each `user-invocable: false`, trigger in description
│   ├── agent-skill-trigger-index/   the full trigger list, loaded only when auditing it
│   ├── firstmate-coding-guidelines/ knowledge-placement tree, one-owner rule, size discipline
│   ├── harness-adapters/            router + references/{common,harness}/*.md, JSON routing table
│   ├── validation-supervision/      how firstmate supervises a worker's no-mistakes run
│   ├── ask-user-authority/          decide-vs-escalate policy for review findings
│   └── ship-landing/ scout-completion/ stuck-crewmate-recovery/ …
├── skills/stow/           the one PUBLIC installer-facing skill (deliberately separate copy)
├── bin/                   ~200 shell scripts; each header comment IS the contract
│   ├── fm-session-start.sh  one digest = lock+bootstrap+wake-drain+context (1085 lines)
│   ├── fm-brief.sh          scaffolds data/<id>/brief.md (ship|scout|secondmate) (701)
│   ├── fm-dod-lib.sh        single owner of Definition-of-done + worker role + --intent contract (683)
│   ├── fm-spawn.sh          worktree + backend window + launch-brief + validation (5487)
│   ├── fm-teardown.sh       refuses unless work has LANDED (3856)
│   ├── fm-send.sh / fm-control.sh   steer (data plane) vs interrupt/exit/relaunch (control plane)
│   └── backends/tmux.sh …   session-provider adapters behind one function set
├── docs/                  architecture.md, configuration.md (2445, owns schemas), supervision-protocols/<harness>.md
│   └── documentation-audiences.{md,json}  machine-checked audience class per prose file
└── tests/                 ~300 `*.test.sh`, plus captures/no-mistakes-v1.70.1/
```

Private, gitignored per home: `data/` (backlog, briefs, reports, captain.md, learnings.md), `state/` (status
event logs, meta, inbox), `config/`, `projects/` (AGENTS.md:48).

## A3. Approach

### a. Rules / standards

| Layer | Where | Loads | Evidence |
|---|---|---|---|
| Supervisor contract | `AGENTS.md` | always | AGENTS.md:1-9 "This file is your entire job description" |
| Conditional procedures | `.agents/skills/*/SKILL.md` | on a named trigger in description | AGENTS.md:403-406 |
| Mechanics (flags, paths) | each script's header + `--help` | when the script runs | firstmate-coding-guidelines:34-35 |
| Schemas / layout | `docs/configuration.md` | on demand | AGENTS.md:55 |
| Project rules | the PROJECT's own `AGENTS.md` | in the worker's worktree | AGENTS.md:151-156 |

Single-source is an explicit, written rule:
- **Knowledge-placement decision tree**, 7 tiers, "stop at the first tier that answers yes" (firstmate-coding-guidelines/SKILL.md:18-39).
- **One-owner rule**: every contract stated once, every other mention a one-line pointer (same file :41-47).
- **Inline-stub pattern**: what stays in AGENTS.md after a move = only the trigger + safety fact (:49-56).
- **Size discipline** with history: AGENTS.md "grew from 585 to 958 lines" before this rule (:15); ceiling 9,000 words (VISION.md:39).
- Docs carry an audience class in one JSON inventory, checked by `bin/fm-doc-audience-check.sh` (docs/documentation-audiences.md:3-5).
- Every reference in AGENTS.md is a pointer: "`bin/fm-brief.sh` and its help own scaffold syntax…" (AGENTS.md:381).

### b. Process / workflow

```
captain ──chat──▶ FIRSTMATE (coordinator, never writes to projects — hard rule 1, AGENTS.md:28-32)
   intake: resolve project → classify Ship|Scout → resolve mode + yolo (AGENTS.md:164-199)
   fm-brief.sh  → data/<id>/brief.md   (fill ## Captain's intent + ## Firstmate spec)
   fm-spawn.sh  → worktree + tmux window + launch-brief.md (role contract first)
        │
        ▼
   WORKER (ship|scout) ──status line──▶ state/<id>.status ──▶ fm-watch.sh (bash, 0 tokens) ──wake──▶ firstmate
        ▲                                                                                │
        └──────── fm-send.sh → state/<id>.inbox/NNN.msg + doorbell ◀─────────────────────┘
   ship: implement → done: → firstmate says "run /no-mistakes" → done: PR <url> checks green
   firstmate: ask-user findings → decide or escalate → captain merges (unless yolo)
   fm-teardown.sh refuses unless landed
```

| Element | How | Evidence |
|---|---|---|
| Stages | Intake → Dispatch → Validate → PR ready/landing → teardown | AGENTS.md:160-251 |
| Routing | by deliverable: **Ship** (default) vs **Scout** (report only) | AGENTS.md:178-186 |
| Delivery modes | `no-mistakes` · `direct-PR` · `local-only`, orthogonal to `yolo` merge authority | AGENTS.md:226-236 |
| Human gates | merge, discard, destructive, credentials, design picks | AGENTS.md:33-43, 340-348 |
| Handoff record | append-only `state/<id>.status`: `working|needs-decision|blocked|paused|done|failed`, keyed + `resolved` | fm-brief.sh:592-607 |
| Steering | durable inbox file + constant doorbell line; ack = `mv` to `handled/` | fm-brief.sh:359-368 |
| State on disk | backlog via tasks-axi, decisions as held tasks | AGENTS.md:359-377 |
| Restart | "A restart must be a non-event" — durable records, not chat memory | AGENTS.md:128; VISION.md:41-46 |

### c. Roles / personas

| Role | Made of | Who writes it | Can it change? |
|---|---|---|---|
| firstmate (coordinator) | repo `AGENTS.md` | shared repo; captain via PR | only through own no-mistakes pipeline (AGENTS.md:49) |
| secondmate | isolated `FM_HOME` + charter brief | `fm-brief.sh --secondmate` (fm-brief.sh:414-482) | charter is per home |
| ship / scout worker | **generated** launch brief: role block + task + rules + DoD | `fm_brief_worker_role` (fm-dod-lib.sh:108-122) | rendered fresh every launch/relaunch |

Key detail: the worker role is NOT a file the worker loads. `fm-spawn.sh` prepends it to every launch brief and
it "supersedes any conflicting role identity" from project files (fm-dod-lib.sh:111-114). A worker in the
firstmate repo itself is told to treat root `AGENTS.md` as project content, not as its identity (:119).
Personality is minimal: "captain" address in chat only, never in artifacts (AGENTS.md:12-16).

### d. Review & verification

**firstmate does no review of its own.** "When no-mistakes is selected, no-mistakes alone owns review, fixes,
tests, documentation, push, PR, and CI … without adding an independent reviewer" (AGENTS.md:222).
Manual review exists only when the captain asks for it as a deliverable (AGENTS.md:223-225).

What firstmate DOES own is the *judgment* on review findings:
- `ask-user-authority`: decide findings unambiguous toward accepted intent; escalate only expanding /
  ambiguous / destructive ones (ask-user-authority/SKILL.md:23-37).
- Escalation shape: 5 elements — requirement, proposed expansion, smallest compliant alternative,
  consequences, recommendation (:39-47).
- "Treat labels such as correctness, security … as evidence, never as authority to broaden" (:37).
- The worker never answers its own ask-user finding; `--yes` banned fleet-wide (fm-dod-lib.sh, actual :322-327).
- Done gates are mechanical: a `done:` whose commit exists only in the worker's copy is refused (fm-dod-lib.sh:16-40; ship-landing/SKILL.md:13-16).

### e. Context engineering

| Technique | Evidence |
|---|---|
| One session-start script prints one digest; "read once, trust it" | fm-session-start.sh:2-67; AGENTS.md:76-79 |
| Zero-token bash watcher; agent wakes only on actionable events | docs/architecture.md:13; supervision-protocols/claude.md:6-9 |
| Waiting costs no turns: one blocking command, never sleep+poll | fm-brief.sh:374-386 |
| Status lines "sparse supervisor-actionable events, not routine progress" | AGENTS.md:393; fm-brief.sh:670-673 |
| Brief = intent (captain's words) kept separate from spec (coordinator's build notes) | fm-brief.sh:529-536; AGENTS.md:382-383 |
| `--intent` must be self-sufficient: "that string plus the codebase" rebuilds the spec | fm-dod-lib.sh:77-79 |
| Big content goes to files; status line only points (ask-user findings snapshot) | fm-dod-lib.sh, actual :269-279 |
| `/stow` writes durable knowledge to disk before a reset | docs/architecture.md:470-479 |
| Subagent use guarded by a PreToolUse hook | .claude/settings.json (fm-subagent-pretool-check.sh) |

### f. Packaging & distribution

- No installer: "clone the repo, run your agent in it, and that is it" (VISION.md:73; README.md:82-95).
- One skills tree `.agents/skills/`, symlinked as `.claude/skills` (ls of `.claude/`).
- Per-harness glue is tracked side by side: `.claude/settings.json`, `.cursor/hooks.json`, `.pi/extensions/`, `.omp/extensions/` (README.md:96-120).
- Per-machine/private config is a gitignored home (`data/ state/ config/ projects/`) selected by `FM_HOME` (AGENTS.md:48, 56).
- Home-local worker instructions without editing tracked files: `config/brief-include.md`, appended last and lowest precedence (fm-brief.sh:111-121, 317-324).
- Public vs internal skills are deliberately separate copies (skills/stow/SKILL.md:7 maintainer comment).

### g. Hosting / UI

Headless, terminal-native. Visible crew = backend windows (tmux/herdr/…). No web UI; optional "Relay"
answers X/Discord mentions (README.md:51). Approvals happen in chat with the coordinator; a `lavish-axi`
board for visual decisions (AGENTS.md:355). Turn-end guards (Stop hooks) stop the coordinator from ending a
turn "blind" while work is live (AGENTS.md:261, 295).

## A4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `.agents/skills/firstmate-coding-guidelines/SKILL.md:18-56` | The best single-source policy we have seen: a 7-tier placement tree, the one-owner rule, and the inline-stub rule, plus the measured failure (585→958 lines) that motivated it. Directly answers our Q-1/Q-3. |
| 2 | `bin/fm-dod-lib.sh:108-122` (`fm_brief_worker_role`) | Role injected per launch, stated first, with explicit precedence over project files. Exactly the "agent side vs project side" split of Q-11, done without a user-level file. |
| 3 | `.agents/skills/ask-user-authority/SKILL.md:23-57` | Lead judgment over review findings: decide in-intent fixes, escalate only contract expansion; 5-element escalation; worked classification examples. A drop-in for our G3 "pstack lead judgment". |

Runner-up: `bin/fm-brief.sh:646-694` — the whole ship brief (isolation assertion, rules, status protocol,
"same obstacle twice → blocked", project-memory corrections-only).

---

# Part B — no-mistakes

## B1. What it is

| | |
|---|---|
| What | local git proxy remote; `git push no-mistakes` runs an AI pipeline in a disposable worktree, then pushes + opens the PR (README.md:37-38) |
| Maturity | v1.86.0 (HEAD 2026-10-01, PR #1269); Go; Trendshift-badged (README.md:26) |
| Stars | not in clone — unknown (Trendshift badge implies notable) |
| Agents | claude, codex, grok, rovodev, opencode, pi, copilot, antigravity, ACP targets (README.md:41) |
| The one idea | **"one deliberate push means a change was independently validated"**; the core pipeline is fixed and can only be added to (VISION.md:3, 11) |

## B2. File tree (what matters)

```
no-mistakes/
├── AGENTS.md            88 lines: layout map + "Invariants every change must keep", each with Owner: <skill>
├── CLAUDE.md            "@AGENTS.md"
├── VISION.md            84 lines — product law (never lose work, pipeline runs forward, judgment stays human)
├── .claude/skills -> ../.agents/skills
├── .agents/skills/      15 per-AREA maintainer skills (implementation maps, invariants, regression lists)
├── skills/no-mistakes/SKILL.md   GENERATED from internal/skill/skill.go; shipped to user level by `init`
├── internal/pipeline/steps/
│   ├── review.go                  fixer prompt (:136-175) + reviewer prompt (:318-396) + session rule (:398+)
│   ├── review_path_instructions.go  path-glob → instruction blocks, logged applied/unmatched
│   ├── intent_prompt.go           authoritative vs inferred intent framing + conformance clause
│   ├── round_history.go           human decisions carried into every later prompt
│   ├── review_questions.go        opt-in reviewer→human question channel
│   └── test.go document.go lint.go ci*.go push.go pr*.go …
├── internal/config/     config.go (3271), review_agents.go (per-round reviewer/fixer pinning), gates.go
├── internal/agent/memory_files.go     MemoryFilesRule appended to every editing prompt
├── internal/testguidance/guidance.go  shared test-quality rule
└── docs/src/content/docs/reference/{repo-config,pipeline-steps}.md   own every key and step
```

## B3. Approach

### a. Rules / standards

| Concern | Mechanism | Evidence |
|---|---|---|
| Core review rules | hard-coded in the Go prompt, identical for every repo | review.go:318-396 |
| Repo house rules | `review.path_instructions`: `{path, instructions}`; only blocks whose glob hits a changed file are injected, each labelled with its scope and matched files | review_path_instructions.go:31-76, 141-159; repo-config.md:441-497 |
| Rule must fire visibly | step log names applied rules AND rules that matched nothing | review_path_instructions.go:161-184 |
| Trust | rules read only from the **default branch** at a freshly fetched SHA; a pushed branch can't add/remove them | repo-config.md:8-17, 494-496; review.go:258-266 |
| Limits | ≤32 entries, ≤16 KB section, fail at parse time | repo-config.md:484-492 |
| Shared prompt rules | `MemoryFilesRule`, `testguidance.Rule` constants appended to every relevant prompt | memory_files.go:12-18; guidance.go:8-43 |
| Maintainer rules | AGENTS.md invariants each name an Owner skill; per-area skills in `.agents/skills/` | AGENTS.md:17-22, 24-56 |
| Extra checks | `gates`: shell command after a core step; can add, never skip/reorder | repo-config.md:498-554 |

### b. Process / workflow

```
intent → rebase → review → test → document → lint → push → pr → ci      (fixed; concepts/pipeline.md:6-9)
            each step: findings{severity, action: auto-fix|ask-user|no-op}
            auto-fix loop INSIDE the step, bounded by auto_fix.<step>  (review default 0 = human picks)
            ask-user → park → human/agent: approve | fix(--instructions) | skip | abort
```

| Element | How | Evidence |
|---|---|---|
| Fixed order, add-only | repo `gates` insert after anchors; core never removed | concepts/pipeline.md:24, 93-99 |
| "Runs forward" | a step never sends the run back to Review; each step answers for its own edits | VISION.md:37-47 |
| Human gate | `ask-user` = author's call; unclassifiable finding fails closed to the human | VISION.md:30; review.go:355-360 |
| Decisions persist | human rulings carried into every later step and run as a prompt section | round_history.go:19-45; VISION.md:42 |
| Agent driving | `no-mistakes axi run --intent …` / `axi respond`; TOON output | skills/no-mistakes/SKILL.md:143-175 |
| State | daemon + SQLite run records; disposable worktree | concepts/daemon.md (listed) |

### c. Roles / personas

No personas. Roles are **pipeline functions**: `reviewer`, `fixer`, `reviewer_after_round`, `fixer_after_round`,
each pinnable to a harness/model/effort (review_agents.go:13-46). The strongest role rule:
reviewer and fixer have separate memory; a reviewer session never survives a fix round, so a reviewer
"never certifies its own prescription" (VISION.md:53-54; review.go:78, 398-410).
Gate agents must not adopt the repo's identity: `disable_project_settings` suppresses project
`AGENTS.md`/`CLAUDE.md` for gate agents, per harness, fail-closed if unverified (repo-config.md:160-182).

### d. Review & verification

| Aspect | no-mistakes | Evidence |
|---|---|---|
| Input | base..head diff, ignore-filtered reviewable set, intent, round history, matched path rules | review.go:44-50, 254-266 |
| Context | fresh, session-free per round; reads diff itself | VISION.md:51; review.go:398-410 |
| Criteria selection | by changed path glob (trusted) | review_path_instructions.go:45-76 |
| Lenses | defect trace with concrete input; authz/privacy trace; durable-fix sibling check; **Simplification pass** ("does the intent require this component at all") | review.go:318-372 |
| Evidence bar | finding only with a concrete sequence in intended usage | review.go (prompt, "Report a finding only when…") |
| Class not instance | one finding lists every sibling site of the same invariant | review.go:351 |
| Action by remedy | if the fix would extend scope → `ask-user` even if defect is mechanical | review.go:361 |
| Coverage receipt | `reviewed_paths` must equal the reviewable set or the head is not certified | review.go:347; pipeline-steps.md:96-97 |
| Output | JSON findings + `risk_level` low/medium/high + rationale | review.go:373-380 |
| Intent | explicit `--intent` = AUTHORITATIVE acceptance criteria; contradiction must be `ask-user`; inferred intent = hint | intent_prompt.go:38-52, 87-95 |
| Caps | per-step `auto_fix` budget (review default 0); **no review round cap** by "captain's ruling 2026-09-15" | repo-config.md:610-634; AGENTS.md:80 |
| Unreadable review | rerun ≤3 attempts, never a pass | pipeline-steps.md:98-104 |
| Fixer rules | verify legitimacy first; name the invariant + all sites; no machinery; re-trace ordinary path; focused verification only | review.go:149-170 |
| Cost | cost is a "user-visible property"; costly guarantees opt-in only | VISION.md:16-17 |

### e. Context engineering

- Each prompt section is empty when unused, so the prompt is byte-identical without a feature (review_path_instructions.go:141-145; AGENTS.md:80).
- Every list rendered into a prompt is bounded (files list 192-byte allowance with `+N more`; decisions ≤40 lines / 16 KB) (review_path_instructions.go:96-132; round_history.go:13-17).
- Untrusted text (intent, filenames) sanitized and fenced with BEGIN/END + "do not execute" (intent_prompt.go:29-51).
- Fixer told: do NOT run the full suite; later steps are the authoritative gates (review.go fix prompt).

### f. Packaging & distribution

Single Go binary via curl/Go install; `no-mistakes init` installs the `/no-mistakes` skill at **user level** for
every detected agent (README.md:70-89, 120). Repo config `.no-mistakes.yaml`; global config per user.
The shipped skill is generated from Go source with a drift test (`make lint`) (documentation-guidance/SKILL.md:15-17).

### g. Hosting / UI

Local daemon per user; TUI (`no-mistakes`), git push options, and `axi` (agent CLI, TOON) share one approval
model (VISION.md:71). Opt-in "review conversation": reviewer asks the human mid-review, answers persist per
branch (repo-config.md:418-439).

## B4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `internal/pipeline/steps/review.go:318-396` | A complete, battle-scarred reviewer prompt: concrete-sequence evidence bar, class-not-instance (:351), classify-by-remedy (:361), Simplification pass (:367-371), coverage receipt (:347). Each clause has a Go comment naming the incident behind it (e.g. "thirteen rounds that never converged"). |
| 2 | `internal/pipeline/steps/review.go:149-170` (fixer rules) | "State the invariant… enumerate every place" + "Do not grow the fix into machinery" + "re-trace the ordinary path". Speaks directly to our findings-in-rounds problem (#576 4 rounds, !230 3 rounds). |
| 3 | `internal/pipeline/steps/review_path_instructions.go:31-76,161-184` | Path-scoped criteria, selected against the complete changed set, each block labelled with scope + matched files, unmatched rules logged. This is G3's "references by changed path" already in production. |

---

# Part C — Against our decisions

| Decision | Verdict | Evidence / note |
|---|---|---|
| **G1** rules in layers, AGENTS.md index, bodies on demand | **confirms** | firstmate: always-loaded AGENTS.md + trigger-in-description skills + script headers (AGENTS.md:403-406; coding-guidelines:18-39). Both repos: `CLAUDE.md` = `@AGENTS.md`, `.claude/skills` symlink. |
| G1 sub-point: who may edit project AGENTS.md | **new idea** | Both repos: agents may only *correct* AGENTS.md/CLAUDE.md, never add (firstmate AGENTS.md:154-156; no-mistakes memory_files.go:12-18). Adds a rule we lack. |
| **G2** one crq + role labels; roles say only who | **confirms (partly)** | firstmate has no per-role process file; process lives in AGENTS.md §7 + skills, worker role is 5 lines (fm-dod-lib.sh:108-122). But it has only 2 worker shapes (ship/scout), not analyst/dev/qa. |
| G2: GitLab comment = handoff record | **contradicts (mechanism)** | firstmate's record is a local append-only status log + inbox, not the forge (fm-brief.sh:592-607, 359-368). Forge only for PR. Our choice stays valid; theirs is faster/zero-token. |
| G2: qa fresh read-only context | **confirms** | no-mistakes: review fresh, reviewer≠fixer memory, session forgotten before fix (VISION.md:51-54; review.go:78). |
| **G3** Standards ‖ Spec review | **contradicts (shape)** | no-mistakes runs ONE reviewer with many lenses + intent conformance, not two parallel axes (review.go:318-396). Spec-axis is the intent conformance clause (intent_prompt.go:87-95). |
| G3: references by changed path | **confirms** | `review.path_instructions` (review_path_instructions.go:45-76). |
| G3: inputs pushed in, findings only | **confirms** | diff scope, intent, history pushed into prompt; JSON findings out (review.go:44-50, 373-380). |
| G3: 3-round cap | **contradicts** | "There is NO review round cap and none may be added" (no-mistakes AGENTS.md:80); bound is `auto_fix.review` (default 0 → human picks each round). |
| G3: lead judgment | **confirms + sharpens** | firstmate `ask-user-authority` decides in-intent findings, escalates only expansion (SKILL.md:23-47). |
| G3: per-criterion receipts "nowhere" (R3) | **contradicts R3** | `reviewed_paths` is a per-file coverage receipt; clean review without it does not certify (pipeline-steps.md:96). |
| **G5** 5-section references | **neutral / new idea** | Neither uses 5-section topic files. no-mistakes rules are prompt constants + path blocks; firstmate uses placement tree. Idea: our "Review checks" section ≈ a `path_instructions` block. |
| **G6** coordinator + per-task briefed workers | **confirms strongly** | firstmate is exactly this: one coordinator, fresh worker per task in its own worktree + backend window, scaffolded brief, never writes projects (AGENTS.md:21-43, 198-217). |
| G6: coordinator relays every question with context | **confirms** | evidence-first escalation, translate internals to outcomes (AGENTS.md:309-357). |
| **G4** plugins everywhere | **contradicts (mechanism)** | firstmate ships as a cloned repo, not plugins (VISION.md:60, 73); no-mistakes ships a binary + user-level skill. Neither uses a marketplace. |
| G4: coordinator-as-contract | **confirms** | AGENTS.md is the contract; harness glue per vendor is separate files (README.md:96-120). |
| G4: one machine file | **confirms** | per-home gitignored `config/`, `FM_HOME` (AGENTS.md:48, 56). |

---

# Part D — Adopt / Adapt / Reject (ranked)

| # | Verb | What | File that shows it |
|---|---|---|---|
| 1 | **ADOPT** | Knowledge-placement tree + one-owner rule + inline-stub rule as OUR rule for writing rules | F `.agents/skills/firstmate-coding-guidelines/SKILL.md:18-64` |
| 2 | **ADOPT** | Path-scoped review blocks: select by complete changed set, label with scope + matched files, **log unmatched rules** | N `internal/pipeline/steps/review_path_instructions.go` |
| 3 | **ADOPT** | Reviewer prompt clauses: concrete-sequence bar, class-not-instance, classify-by-remedy, Simplification pass, `reviewed_paths` receipt | N `review.go:318-372` |
| 4 | **ADOPT** | Fixer rules (invariant + all sites, no machinery, re-trace ordinary path) for our developer fix rounds | N `review.go:149-170` |
| 5 | **ADOPT** | Lead-judgment policy + 5-element escalation for findings | F `.agents/skills/ask-user-authority/SKILL.md` |
| 6 | **ADOPT** | Memory-file rule: agents only correct AGENTS.md/CLAUDE.md, never add | N `internal/agent/memory_files.go:12-18`; F `AGENTS.md:154-156` |
| 7 | **ADAPT** | Brief = `## Captain's intent` (verbatim words) + `## Firstmate spec`; intent self-sufficient; reviewer treats intent as acceptance criteria | F `bin/fm-brief.sh:529-536`, `fm-dod-lib.sh:66-84`; N `intent_prompt.go:87-95` |
| 8 | **ADAPT** | Worker role injected at launch with explicit precedence, not a user-level file — check against Q-11 (we chose user-level CLAUDE.md + plugins) | F `bin/fm-dod-lib.sh:108-122` |
| 9 | **ADAPT** | Status vocabulary `needs-decision/blocked/paused/done/failed` + keyed `resolved`, "same obstacle twice → blocked", as the shape of our GitLab comment | F `bin/fm-brief.sh:592-607, 680-685` |
| 10 | **ADAPT** | Mechanical done-gates (refuse done unless commit pushed; teardown refuses unlanded) → script checks behind our stages | F `fm-dod-lib.sh:16-40`, `fm-teardown.sh:44-68` |
| 11 | **ADAPT** | `disable_project_settings` idea: QA/reviewer must not inherit the project's operator identity — relevant once coordinator lives in a repo | N `repo-config.md:160-182`; F `.no-mistakes.yaml` |
| 12 | **REJECT** | No-round-cap stance — keep G3's 3-round cap; their bound is a human approving each round (`auto_fix.review: 0`), which costs operator attention we want to save | N `AGENTS.md:80`, `repo-config.md:610-634` |
| 13 | **REJECT** | Single-reviewer-with-all-lenses replacing Standards‖Spec — P1 already showed our scoped split works; keep, but borrow lenses | N `review.go:318-396` |
| 14 | **REJECT** | Clone-the-repo distribution and 200-script bash control plane — too heavy for our scale; plugins + one machine file stays | F `VISION.md:73`, `bin/` |
| 15 | **REJECT** | Nautical persona flavour / "captain" address | F `AGENTS.md:7-17` |

---

# Part E — Files actually read

**firstmate** (F = `/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/kunchenguid-firstmate`)
- F/AGENTS.md (full, 426 lines)
- F/VISION.md (full)
- F/CLAUDE.md
- F/README.md:1-140
- F/CONTRIBUTING.md:1-40
- F/.no-mistakes.yaml (full)
- F/.claude/settings.json (full); `ls` of F/.claude (skills symlink, mods/)
- F/bin/fm-brief.sh (full, 701 lines)
- F/bin/fm-dod-lib.sh:1-127, 269-463
- F/bin/fm-spawn.sh header :2-90
- F/bin/fm-session-start.sh header :2-89
- F/bin/fm-teardown.sh header :2-68
- F/bin/backends/tmux.sh header :2-21 + function list
- F/.agents/skills/agent-skill-trigger-index/SKILL.md (full)
- F/.agents/skills/validation-supervision/SKILL.md (full)
- F/.agents/skills/ask-user-authority/SKILL.md (full)
- F/.agents/skills/ship-landing/SKILL.md (full)
- F/.agents/skills/scout-completion/SKILL.md (full)
- F/.agents/skills/firstmate-coding-guidelines/SKILL.md (full)
- F/.agents/skills/harness-adapters/SKILL.md (full)
- F/skills/stow/SKILL.md:1-25
- F/docs/documentation-audiences.md (full)
- F/docs/architecture.md:1-20, 255-320, 364-420 (partial), 465-511
- F/docs/supervision-protocols/claude.md (full)

**no-mistakes** (N = `/private/tmp/claude-501/-Users-chiyanram-workspace-agent-platform--claude-worktrees-crq-597-b837e3/33b4f667-1fb1-4419-a848-22e556edfb52/scratchpad/r9/no-mistakes`)
- N/README.md:1-140
- N/VISION.md (full)
- N/AGENTS.md (full), N/CLAUDE.md
- N/internal/pipeline/steps/review.go:27-60, 78, 120-175, 230-410 (+ grep of all funcs)
- N/internal/pipeline/steps/review_path_instructions.go (full)
- N/internal/pipeline/steps/intent_prompt.go (full)
- N/internal/pipeline/steps/round_history.go:1-45
- N/internal/config/review_agents.go:1-60; N/internal/config/config.go:445-447
- N/internal/agent/memory_files.go:12-24
- N/internal/testguidance/guidance.go:8-46
- N/skills/no-mistakes/SKILL.md:1-30, 121-175, 312-354
- N/.agents/skills/documentation-guidance/SKILL.md (full); `wc` of all 15 `.agents/skills`
- N/docs/src/content/docs/reference/repo-config.md:1-80, 160-184, 403-636, 821-835
- N/docs/src/content/docs/reference/pipeline-steps.md:87-117
- N/docs/src/content/docs/concepts/pipeline.md (full)
- N/docs/src/content/docs/concepts/auto-fix.md:1-60
