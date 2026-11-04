# humanlayer — research→plan→implement and context engineering, per repo (2026-10-01)

Scope: five repos under `.scratch/one-rulebook/refs/`. Paths below are relative to that `refs/` dir.
Prior pass R11 (`issues/20-research-humanlayer-suite.md`) was comparative; this one is per-file.

```
 the humanlayer idea in one picture
 ┌─────────── human reviews HERE (cheap, high leverage) ───────────┐       ┌── human reviews here (expensive) ──┐
 ticket ─► /research_codebase ─► research.md ─► /create_plan ─► plan.md ─► /implement_plan (worktree) ─► PR ─► /validate_plan
            parallel read-only       │          interactive,     │         phase by phase, pause for          plan vs diff
            "documentarian"          │          skeptical        │         manual check each phase
            subagents                └── thoughts/ (separate git repo, synced; never in code repo) ─┘
 context rule: every arrow is a fresh session fed one compacted artifact; stay at 40–60% utilisation
```

| repo | what | maturity | the one idea |
|---|---|---|---|
| humanlayer-humanlayer | monorepo: `.claude/` prompt suite + hld daemon + hlyr CLI + WUI | **deprecated** — `README.md:3` | stage = command; artifact on disk = handoff; review the plan, not the code |
| humanlayer-claudelayer | MCP server that lets a subagent launch subagents | toy / experiment, 1-line README | one `launch` tool → recursive `claude -p` |
| humanlayer-skills | Claude Code plugin marketplace, 6 skills | live, small | skills as plugins; loops as sensor→controller→actuator with memory |
| humanlayer-12-factor-agents | essay: 12 principles for LLM apps | stable reference | own your context window and control flow |
| humanlayer-advanced-context-engineering… | essays `ace-fca.md`, `wsff.md`, side-quest | 2025 → 2026 | frequent intentional compaction; then "read the dang code" + program design |

---

## 1 · humanlayer-humanlayer

### 1.1 What it is
Monorepo; the root README says the code is pretty much all deprecated (`humanlayer-humanlayer/README.md:3`). What survives
and matters is `.claude/` — 30 commands, 6 agents — which ACE links as *the* RPI prompts (`ace-fca.md:230,239,246`).
One idea: **each workflow stage is a slash command that writes one markdown artifact; the next stage starts fresh from it.**

### 1.2 Tree (what matters)
```
humanlayer-humanlayer/
├── CLAUDE.md                       # 88 lines: repo map, make targets, TODO(0..4) priority scheme
├── .claude/
│   ├── settings.json               # allow hack/spec_metadata.sh; MAX_THINKING_TOKENS=32000
│   ├── agents/                     # 6 read-only subagents, all model: sonnet
│   │   ├── codebase-locator.md     # WHERE — Grep/Glob/LS only, never reads contents
│   │   ├── codebase-analyzer.md    # HOW — file:line, no critique
│   │   ├── codebase-pattern-finder.md  # examples to copy, no judgement
│   │   ├── thoughts-locator.md / thoughts-analyzer.md   # same pair over thoughts/
│   │   └── web-search-researcher.md
│   └── commands/
│       ├── research_codebase{,_generic,_nt}.md   # stage R  (3 near-copies)
│       ├── create_plan{,_generic,_nt}.md         # stage P  (3 near-copies, ~440 lines each)
│       ├── iterate_plan{,_nt}.md                 # P revision
│       ├── implement_plan.md                     # stage I
│       ├── validate_plan.md                      # post-I check
│       ├── create_handoff.md / resume_handoff.md # compaction across sessions
│       ├── ralph_{research,plan,impl}.md         # autonomous: pull top Linear ticket per status
│       ├── oneshot.md / oneshot_plan.md          # chain ralph_* across launched sessions
│       ├── linear.md                             # status machine + hard-coded state IDs
│       ├── commit / ci_commit / describe_pr / ci_describe_pr / founder_mode / debug / local_review / create_worktree
├── hack/spec_metadata.sh           # date, sha, branch, repo → frontmatter for every artifact
├── hld/                            # Go daemon: sessions, approvals, events (JSON-RPC + REST/SSE)
│   ├── CLAUDE.md / PROTOCOL.md / README.md
└── hlyr/                           # TS CLI: `launch`, `thoughts`, `claude init`, approvals MCP server
    ├── THOUGHTS.md                 # the thoughts/ system
    └── src/commands/{launch.ts, claude/init.ts, thoughts/*}
```

### 1.3 Approach

**a. Rules / standards.** Thin. Root `CLAUDE.md` is a map plus make targets plus a `TODO(0)`–`TODO(4)` priority
convention (`CLAUDE.md:78-85`). Sub-dir `hld/CLAUDE.md:3` carries an operational rule ("you cannot run this process")
and two Go style rules (`hld/CLAUDE.md:52-55`). No standards tree; rules live inside each command. **Not single-source:**
`create_plan.md` / `create_plan_nt.md` / `create_plan_generic.md` are three ~440-line copies whose diffs are only the
thoughts/ lines (`diff create_plan.md create_plan_nt.md` → lines 30-31, 41, 54, 112-115, 274, 279-285); same for
`research_codebase*` where `_generic` drops the whole documentarian block (`research_codebase.md:10-18`). Drift is
visible: `create_handoff.md:19` calls `scripts/spec_metadata.sh` while settings allow only `hack/…`
(`settings.json:4-6`); `research_codebase.md:97` says "metadata gathered in step 4" — it is step 5; `ralph_plan.md:24`
reads `./claude/commands/…` (missing dot).

**b. Process / workflow.** Stages and their gates:

| stage | command | human gate | artifact on disk |
|---|---|---|---|
| research | `research_codebase.md` | user reads doc, follow-ups append (`:170-176`) | `thoughts/shared/research/YYYY-MM-DD-ENG-XXXX-*.md` (`:87`) |
| plan | `create_plan.md` | 3 gates: informed questions (`:74-89`) → design options (`:128-145`) → phase outline approval (`:151-166`) → draft review (`:285-304`) | `thoughts/shared/plans/…md` (`:172`) |
| plan revision | `iterate_plan.md` | confirm understanding before editing (`:93-111`) | same file, surgical edits (`:115-131`) |
| implement | `implement_plan.md` | pause after each phase's automated checks for manual check (`:45-65`) | checkboxes ticked in the plan itself (`:49`) |
| validate | `validate_plan.md` | report to user | validation report (`:86-127`) |
| commit / PR | `commit.md` asks first (`:23-26`); `ci_commit.md:34` never asks | — | `thoughts/shared/prs/{n}_description.md` (`describe_pr.md:60`) |

Routing is by **ticket status**, not by command text: `linear.md:40-51` defines Triage → Research Needed → Research in
Progress → Research in Review → Ready for Plan → Plan in Progress → Plan in Review → Ready for Dev → In Dev → Code
Review, and `:53` says alignment happens at the plan stage, not the PR. `ralph_research.md:13-16` picks the top-priority
XS/S ticket in "research needed", moves it (`:22`), bounces it back with a comment if under-specified (`:24`), and
finishes by attaching the doc and moving to "research in review" (`:52-55`). `ralph_impl.md:24-25` refuses without a
linked plan. `oneshot.md:5-6` chains research then **launches a new session** for plan+impl
(`oneshot_plan.md:5-6`). Handoff = file path in a ticket comment + Linear status.

**c. Roles / agents.** Six subagents, each `tools:` restricted and `model: sonnet` (`codebase-locator.md:4-5`). Persona
is a job, not a soul: "documentarian, not a critic" repeated in every agent (`codebase-analyzer.md:10-17,139`). Locator
is forbidden to read contents (`codebase-locator.md:98`). There are no top-level role personas; the *command* is the
role. ACE says outright subagents are context control, not roles (`ace-fca.md:191`).

**d. Review & verification.** Three layers, all plan-anchored:
- Plan success criteria split **Automated** (commands, prefer `make`) vs **Manual** (`create_plan.md:225-240,345-376`).
- `validate_plan.md`: fresh-or-same session (`:12-14`), git diff + `make check test` (`:20-28`), 3 parallel tasks
  (db / code / tests, `:42-58`), output buckets **Matches Plan · Deviations · Potential Issues · Manual Testing**
  (`:99-121`). No caps, no criterion selection, no cost control.
- `describe_pr.md:41-48` runs each "How to verify" checkbox command and ticks only what passed.
- `local_review.md:22-31`: reviewing a colleague = new worktree + launch a fresh session there.

**e. Context engineering.** The strongest part.
- Read named files fully, **yourself, before** spawning subagents (`research_codebase.md:30-34`, `create_plan.md:40-47`).
- Subagents for search; main agent synthesises only (`research_codebase.md:179,188`); don't tell agents *how* to search
  (`:71`); but do be extremely specific about directories (`create_plan.md:411-415`).
- Verify user corrections with new research rather than accepting them (`create_plan.md:95-99`).
- No open questions in a final plan (`create_plan.md:338-343`).
- Handoff = deliberate compaction: Tasks · Critical References (2-3 paths) · Recent changes · Learnings · Artifacts ·
  Action Items · Other (`create_handoff.md:43-64`), file:line refs over code blocks (`:95`).
- Resume = read handoff + linked plan/research **without a subagent** (`resume_handoff.md:16`), then verify every claim
  against the current tree before acting (`:59-71,166-170`).
- `debug.md:7` exists explicitly to debug without polluting the primary window.
- Artifact frontmatter from `hack/spec_metadata.sh` (sha, branch, timestamp) so stale artifacts are detectable.

**f. Packaging & distribution.** `humanlayer claude init` **copies** `.claude/{commands,agents,settings}` into the target
repo (`hlyr/src/commands/claude/init.ts:66-87,112,323`), defaulting `alwaysThinking=true`, `model=opus`
(`:281-288`). Copy, not plugin → the same drift problem we have (#587). Per-machine: `settings.local.json` excluded
(`hlyr/README.md` "What Gets Copied").

**g. Hosting / UI.** `hld` daemon: JSON-RPC over unix socket + REST/SSE (`hld/README.md:5`, `PROTOCOL.md:5`).
`launchSession` takes query, model, `permission_prompt_tool`, `allowed_tools`, `disallowed_tools`, `system_prompt`,
`append_system_prompt`, `working_dir` (`PROTOCOL.md:85-106`). Approvals are a separate resource; `sendDecision` deny
**requires a comment** (`PROTOCOL.md:292-312`); events `new_approval`, `approval_resolved`, `session_status_changed`
(`:338-340`); statuses include `waiting_input` (`:385-391`). `hlyr launch` exposes
`--dangerously-skip-permissions-timeout` (minutes, `launch.ts:17-18,46-49,68-70`) — yolo with an expiry; approvals go
through `mcp__codelayer__request_permission` (`launch.ts:67`). thoughts/ is a separate git repo symlinked in, with
`searchable/` hard links for grep, pre-commit hook blocking it from the code repo, post-commit sync
(`hlyr/THOUGHTS.md:38-53,74-77,81-88`).

### 1.4 Three excerpts worth studying
1. `create_plan.md:225-240` — every phase ends with Automated vs Manual criteria and an explicit "pause here for
   manual confirmation". Turns a plan into a gated script; the gate is in the artifact, not the agent's memory.
2. `create_handoff.md:43-64` + `resume_handoff.md:59-71,166-170` — a compaction schema plus a resume that distrusts it
   ("never assume handoff state matches current state"). The pair is what makes fresh-session-per-stage safe.
3. `ralph_research.md:13-55` — a stage expressed as: pick by status → claim (move status) → bounce if under-specified →
   produce artifact → attach → move to "* in review". Exactly the shape a briefed fleet worker needs.

---

## 2 · humanlayer-claudelayer

### 2.1 What it is
Experiment (`README.md:1` is the title only; `CLAUDE.md:1-106` is unedited Bun boilerplate). One idea: **an MCP server
with a single `launch` tool so a subagent can spawn subagents** — Claude Code's Task tool cannot nest.

### 2.2 Tree
```
humanlayer-claudelayer/
├── src/index.ts        # MCP server, one tool `launch(name, input)` → spawn `claude -p` (haiku)
├── src/subagents.ts    # loads .claude/agents/*.md AND .claude/commands/*.md as launchable agents
├── .claude/agents/     # humanlayer's 6 agents (byte-identical copies) + codebase-analyzer-recursive + counter
├── .claude/commands/   # humanlayer copies (create_plan differs at :438, create_worktree at :1) + exhaustive-research
└── .claude/settings.json  # MAX_THINKING_TOKENS=4000, model opus, enableAllProjectMcpServers
```

### 2.3 Approach
- **Mechanism.** Comment at `src/index.ts:28`: register a single tool, "not multiple - avoid context rot". The tool's
  description embeds every agent's name+description as XML (`:26,33`); the call concatenates agent prompt +
  `<user_instruction>` (`:45`) and spawns `claude -p … --model claude-haiku-4-5 --dangerously-skip-permissions`
  (`:47-52`), teeing to `output.log` (`:59`).
- **Commands are agents too.** `subagents.ts:16-17,65-75` loads commands as launchable agents keyed by filename — any
  slash command becomes a sub-process worker.
- **Tests of the idea.** `counter.md:6-13` recurses to depth 10; `exhaustive-research.md:9-14` fans out one Task per
  directory, each of which fans out locator/analyzer via the MCP tool.
- **Rules / roles / review / distribution:** none of its own; copies humanlayer's, already drifting (diff above).
- **Context engineering:** one-tool-surface to keep the parent's tool list small; cheapest model for leaf work.

### 2.4 Excerpts
1. `src/index.ts:28-52` — the whole idea in 25 lines: subagent = fresh `claude -p` process with a prompt file.
2. `src/subagents.ts:65-75` — commands double as agent definitions; one text, two invocation paths.
3. `counter.md:6-13` — minimal recursion probe; useful as a template for testing a spawn mechanism.

---

## 3 · humanlayer-skills

### 3.1 What it is
A Claude Code marketplace (`.claude-plugin/marketplace.json:1-24`, schema anthropic.com) shipping six plugins, installed
via `npx skills add humanlayer/skills --skill X` (`README.md:7-8`). One idea: **a skill is a plugin; a repeatable agent
task is a control loop (sensor → controller → actuator) with a memory file a human edits by commenting `/iterate`.**

### 3.2 Tree
```
humanlayer-skills/
├── .claude-plugin/marketplace.json
└── plugins/<name>/.claude-plugin/plugin.json + skills/<name>/SKILL.md [+ references/]
    ├── show-me/                     # visual explanation; disable-model-invocation; agents/openai.yaml (Codex policy)
    ├── visual-pr/                   # PR body = 1-sentence why + ≤3 notes + show-me views
    ├── improve-claude-md/           # <important if> rewrite rules
    ├── narrow-react-prop-types/     # concrete actuator skill + example workflow + memory
    ├── build-iterated-agentic-loop/ # skill + GH workflow + prompt + memory + /iterate
    └── design-control-loop/         # same, framed as control theory; interview first
```

### 3.3 Approach
**a. Rules.** `improve-claude-md/SKILL.md` is a rulebook *about* rulebooks: always-relevant context bare, everything
else in narrow `<important if>` blocks (`:22-28,30-55`); **do not shard into files** that need tool calls unless very
long (`:57-63`); cut linter-enforceable rules and code snippets (`:65-70,121-122`); keep every command (`:72-74`).
Inside skills: "Keep one source of truth for each rule; do not repeat … in the skill, prompt, and memory file"
(`build-iterated-agentic-loop/SKILL.md:95`, `design-control-loop/SKILL.md:87`). Repo-specific targeting goes in the
workflow prompt, not the generic skill (`build-iterated…/SKILL.md:108`).

**b. Process.** `design-control-loop/SKILL.md` phases A–H: read repo before asking (`:26,43-56`) → interview set point /
sensor / controller / actuator / disturbances (`:58-77`) → write actuator skill (`:79-93`) → **run each component
locally before CI** (`:95-107`) → wire CI (`:109-121`) → human on the loop via memory + `/iterate` (`:123-134`) → flow
control: **one open PR per loop** (`:136-145`) → dry-run (`:147-157`). Every phase ends with a "Completion criterion".

**c. Roles.** None as personas. The actuator skill *is* the role; `skill-template.md:1-57` = Core Requirements → numbered
steps each with a Completion criterion → **Review Checklist at the end** (`:51-57`).

**d. Review.** `visual-pr/SKILL.md:29-31,51`: Why = exactly one sentence; Special notes = 1–3 bullets or "None.";
Change outline = show-me views (SQL/contract, types, pseudocode diff, file-tree diff, call-tree diff,
`pr_description_template.md:3-53`); "Do not expand the PR body beyond that template". Loop PRs are bounded and
labelled (`workflow-template.yml:44-56`).

**e. Context engineering / lesson loop.** `agent-iteration.ts:53` hides a marker
`codelayer-agent:workflow=…;memory=…` in the PR body so only the owning workflow answers `/iterate`. The iteration
prompt (`:76-84`) tells the agent to fix the PR **and** distil durable feedback into the memory file, but not
PR-specific feedback (`:80,82`). Memory good/bad entries: `build-iterated…/SKILL.md:125-137` — completion criterion
"deleting the memory file would lose useful future-run context". Memory injected **after the controller** each run
(`design-control-loop/SKILL.md:129`).

**f. Packaging.** Plugin per skill with its own `plugin.json` and version (`show-me/.claude-plugin/plugin.json`: 1.0.1).
Multi-harness: `show-me/agents/openai.yaml:1-2` sets `allow_implicit_invocation: false` for Codex, mirroring
`disable-model-invocation: true` (`show-me/SKILL.md:4`). `{SKILLBASE}` placeholder for reference paths
(`visual-pr/SKILL.md:14`). Plugins are self-contained, so `references/` is **duplicated** between the two loop plugins
and already differs (`diff -rq`: agent-runner-templates, memory-template, prompt-template, workflow-template).

**g. Hosting.** Headless runners per agent: Claude `-p --permission-mode bypassPermissions --output-format stream-json`
(`agent-runner-templates.md:22-24`), Codex, OpenCode, CodeLayer; "only on trusted, isolated runners" (`:3`).

### 3.4 Excerpts
1. `design-control-loop/references/control-loop-taxonomy.md:57-63` — flow control, dampener, scope gate, batch size,
   memory: five knobs that keep an autonomous loop from outrunning review.
2. `build-iterated-agentic-loop/references/agent-iteration.ts:76-84` — the cleanest **lesson loop** in any repo we have
   read: reviewer comment → fix now + distil standing guidance → next run reads it.
3. `improve-claude-md/SKILL.md:10-28` — why bare always-on text gets ignored (the injected "may or may not be relevant"
   reminder) and the bare-vs-wrapped rule of thumb (90%+ of tasks → bare).

---

## 4 · humanlayer-12-factor-agents

### 4.1 What it is
Essay series, 12 factors + appendix 13 (`README.md:59-71`). For building LLM apps, not coding agents, but it is the
theory behind everything above. One idea: **an agent is mostly deterministic software; you own the prompt, the context
window and the control flow.**

### 4.2 Tree
```
content/factor-01..12-*.md   # the factors (factor-N-*.md 1-line redirects alongside)
content/appendix-13-pre-fetch.md
CLAUDE.md                    # promptx persona template — unrelated to the essay
```

### 4.3 Approach (factors that bear on us)
| factor | claim | path:line |
|---|---|---|
| 3 own context window | input is "what happened so far, what's next"; custom dense formats; hide resolved errors | `factor-03…:7,227-230` |
| 5 unify state | infer execution state from the thread; serialise, resume, fork | `factor-05…:26,30-38` |
| 6 launch/pause/resume | simple APIs; resume via webhook | `factor-06…:17-21` |
| 7 humans via tools | `request_human_input` as a tool; Agent→Human outer loop | `factor-07…:117-121` |
| 8 own control flow | pause **between tool selection and invocation** for approval | `factor-08…:73-82` |
| 9 compact errors | cap ~3 consecutive errors then escalate | `factor-09…:31,62,83` |
| 10 small agents | 3–10, maybe 20 steps; context growth loses focus | `factor-10…:9` |
| 13 pre-fetch | if the tool call is likely, put its result in the prompt | `appendix-13…:3` |

Roles: the repo's `CLAUDE.md:1-17` is a promptx template forcing a persona choice (developer / reviewer / rebaser /
merger / multiplan manager) from `.promptx/personas/` — **the directory is not in the repo**; principles at
`CLAUDE.md:36-42` ("read at least 1500 lines", "delete more than you add"). Packaging / hosting / review: none.

### 4.4 Excerpts
1. `factor-08-own-your-control-flow.md:73-82` — the three bad options when you cannot pause between selection and
   execution. This is the requirement behind approvals in hld and AG-UI interrupts.
2. `factor-09-compact-errors.md:31,62` — bounded retries then escalate: the same shape as our 3-round review cap.
3. `appendix-13-pre-fetch.md:3` — push what the agent will certainly need instead of letting it fetch: the theory under
   G3's "inputs pushed in".

---

## 5 · humanlayer-advanced-context-engineering-for-coding-agents

### 5.1 What it is
Two essays a year apart plus a side quest and two SlopCodeBench posts (headings only skimmed). `ace-fca.md` (Aug 2025):
research→plan→implement with frequent intentional compaction. `wsff.md` (2026): the lights-off factory fails; put human
review back, add program design and vertical slices. One idea: **the context window is the only lever, and human
attention belongs where one bad line multiplies most — research and plan.**

### 5.2 Tree
```
ace-fca.md                         # RPI + frequent intentional compaction
wsff.md                            # Why Software Factories Fail: 4 human-in-loop phases
side-quests/where-does-the-time-go.md   # 80/20 of up-front effort vs expected pain
benchmarking-*-slop-code-bench.md  # model slop measurements (not read in depth)
```

### 5.3 Approach
- **Compaction.** Intentional compaction = write progress to a file and restart (`ace-fca.md:112-121`); what eats
  context: search, flow-tracing, edits, logs, JSON blobs (`:123-133`). Optimise for correctness > completeness > size >
  trajectory; worst is incorrect info, then missing, then noise (`:152-163`). Keep utilisation 40–60% (`:218`).
- **Subagents** are context control, not role-play (`:189-193`).
- **Workflow.** Research / Plan / Implement, only Implement in a worktree (`:226-248`); compact status back into the plan
  after each verified phase (`:244`).
- **Human leverage.** A bad line of research → thousands of bad lines of code (`:318-333`); code review is for
  **mental alignment** (`:335-359`) — "I can read 200 lines of plan" (`:357`). Cost: team of three ~$12k/month (`:370`).
- **wsff revision.** Models erode maintainability because RL rewards pass/fail only (`wsff.md:228-232,295-349`); review
  bots raise the floor not the ceiling (`:388-397`). Four human-in-loop phases (`:411-416`): product review with HTML
  mockups (`:418-435`), system architecture (sequence diagrams, contracts, SQL; `:437-479`), **program design** — call-
  stack diff, file-tree diff, types/signatures before any code (`:481-536`), **vertical slices** not horizontal layers
  (`:538-570`). Triage: ~40% oneshot, medium = one plan doc, large = all steps (`:581-587`). Author-opt-in review: walk
  the future PR reviewer through the specs first (`:435,441`). "You have too many bad PRs" (`:589-597`). Close: read the
  dang code (`:613-618`).
- **Side quest.** Expected pain = P(rework) × cost; ~80% gone in the first minutes of up-front work
  (`where-does-the-time-go.md:31-39`).

### 5.4 Excerpts
1. `ace-fca.md:318-333` — the leverage ladder (research > plan > code); justification for review effort at stages 3–5.
2. `wsff.md:481-536` — program design as three cheap views (call-tree diff, file-tree diff, signatures). Already parked
   in our map's "Not yet specified"; this is the source text.
3. `wsff.md:538-570` — horizontal vs vertical plans; models default to stack order and must be steered.

---

## 6 · Against our decisions

| decision | verdict | evidence |
|---|---|---|
| **G1** rules layers, AGENTS.md index, bodies on demand | **confirms + one tension.** Confirms: always-on text gets discounted (`improve-claude-md/SKILL.md:10-14`); cut linter-enforceable rules (`:67-69`). Tension: it says **don't shard** into tool-call-discovered files (`:57-63`) — opposite of "bodies on demand". Resolves fine for us: our bodies are loaded because a stage *orders* them (Q-4), not discovered. | skills, humanlayer `CLAUDE.md` |
| **G1** single source | **confirms by counter-example.** humanlayer keeps 3 copies of create_plan / research_codebase and drifts (§1.3a); claudelayer copies drift; skills' self-contained plugins duplicate references and drift (§3.3f). | diffs cited above |
| **G2** one crq, stages tagged by role labels | **confirms.** Stage = command, ownership = ticket status (`linear.md:40-53`); ralph_* each own one status band. Roles there say only *which status* — same as our "roles say only who". | `ralph_research.md:13-55` |
| **G2** GitLab comment = handoff record | **confirms.** ralph attaches the artifact + comment on the ticket and moves status (`ralph_research.md:52-55`, `ralph_plan.md:31-32`). | |
| **G3** Standards ‖ Spec, fresh, pushed-in, 3-round cap | **partially.** Spec axis ≈ `validate_plan.md:99-121` buckets (Matches · Deviations · Issues · Manual). No Standards axis, no criteria-by-path, no cap — humanlayer bets on plan review instead (`ace-fca.md:318-333`). wsff adds: bots raise floor only (`wsff.md:388-397`) → human still reads code. 12-factor 9 = cap-then-escalate (`factor-09…:31,62`). | |
| **G5** 5-section references, review checks at the end | **confirms shape.** `skill-template.md:51-57` puts a Review Checklist at the end of every actuator skill; author and reviewer read one text. | skills |
| **G6** coordinator + briefed per-task workers | **confirms.** Fresh session per stage, briefed by one prompt + one artifact path (`ralph_impl.md:29-31`, `create_worktree.md:22-41`, `oneshot.md:5-6`); worktree only for implement (`ace-fca.md:248`). Brief = handoff schema (`create_handoff.md:43-64`). | |
| **G6** qa fresh per round | **confirms.** `validate_plan.md:12-14` distinguishes fresh vs same-session; `local_review.md` launches a new session. | |
| **G4** plugins everywhere | **confirms** (skills marketplace) and **contradicts by history**: humanlayer's own distribution was `claude init` copy (`hlyr/.../claude/init.ts:323`), the thing we are leaving. | |
| **G4** coordinator-as-contract, front/back adapters | **confirms.** hld = session + approval + event contract; CLI, TUI, WUI are adapters (`CLAUDE.md:33-37`, `PROTOCOL.md:85-106,292-340`). Deny needs a comment = context for the agent's retry. | |
| **G4** tiers | **new idea:** `--dangerously-skip-permissions-timeout` — autonomy that expires (`launch.ts:46-49`). | |
| (map: Not yet specified) program design at stage 5 | **source found:** `wsff.md:481-536`; also vertical slices `:538-570`. | |
| (R8 D2) no lesson loop | **new idea, fills the gap:** `/iterate` → memory file distilled, PR-only feedback excluded (`agent-iteration.ts:76-84`). | |
| (map) findings-in-rounds | **new angle:** the earlier the review, the cheaper (`ace-fca.md:318-333`; side-quest `:31-39`) — rounds at code stage are a symptom of thin plan stage. | |

---

## 7 · ADOPT / ADAPT / REJECT (ranked)

| # | verdict | what | file that shows it | where it lands |
|---|---|---|---|---|
| 1 | **ADOPT** | Plan phases end in **Automated** (make targets) vs **Manual** checks + "pause here" | `humanlayer-humanlayer/.claude/commands/create_plan.md:225-240` | crq stage 5/6 text (REQ) |
| 2 | **ADOPT** | Handoff schema (Tasks · Critical refs ≤3 · Recent changes · Learnings · Artifacts · Next) + resume that re-verifies | `create_handoff.md:43-64`, `resume_handoff.md:59-71,166-170` | G6 brief template + G7 |
| 3 | **ADOPT** | Lesson loop: reviewer feedback distilled into a per-role memory file; PR-only feedback excluded; good/bad entry rules | `humanlayer-skills/.../agent-iteration.ts:76-84`, `build-iterated-agentic-loop/SKILL.md:125-137` | R8 D2; aruvii-agent-fleet role memory |
| 4 | **ADOPT** | Program design before code: call-tree diff, file-tree diff, types/signatures; vertical slices | `humanlayer-advanced…/wsff.md:481-570` | crq stage 5 (closes "Not yet specified") |
| 5 | **ADOPT** | "Read named files yourself before subagents"; "verify corrections, don't accept"; "no open questions in final artifact" | `create_plan.md:40-47,95-99,338-343` | analyst role / stage 3 text |
| 6 | **ADAPT** | Spec-axis buckets Matches · Deviations · Issues · Manual (add our "not done") | `validate_plan.md:99-121` | G3 Spec axis output |
| 7 | **ADAPT** | Status-band stage ownership + bounce-back with a comment when under-specified | `linear.md:40-53`, `ralph_research.md:22-24` | G2 role labels on GitLab |
| 8 | **ADAPT** | Bounded autonomy: one open MR per loop; autonomy with expiry | `control-loop-taxonomy.md:57-63`, `hlyr/src/commands/launch.ts:46-49` | G4 tiers, coordinator policy |
| 9 | **ADAPT** | PR body = 1-sentence why + ≤3 notes + show-me views, never expanded | `humanlayer-skills/plugins/visual-pr/SKILL.md:29-31,51` | aruvii-git MR description |
| 10 | **ADAPT** | Artifact frontmatter with sha/branch/time so staleness is visible | `hack/spec_metadata.sh`, `research_codebase.md:98-111` | crq artifacts on MR |
| 11 | **ADAPT** | `openai.yaml` beside SKILL.md for per-harness invocation policy | `show-me/agents/openai.yaml:1-2` | Q-2 / S-8 multi-harness |
| 12 | **REJECT** | Copy-install of `.claude/` (`claude init`) and `_nt`/`_generic` command forks | `hlyr/.../claude/init.ts:323`; 3× create_plan | violates Q-1, Q-5 |
| 13 | **REJECT** | thoughts/ as a separate synced git repo | `hlyr/THOUGHTS.md:38-77` | GitLab MR/issue already is our record (G2) |
| 14 | **REJECT** | Hard-coded tracker state IDs inside a command | `linear.md:363-374` | project facts in prompt (R8 D3) |
| 15 | **REJECT** | Recursive subagents via MCP + `--dangerously-skip-permissions` | `humanlayer-claudelayer/src/index.ts:47-52` | conflicts with G6 (coordinator spawns, workers don't) |
| 16 | **REJECT** | Mandatory persona selection inside project CLAUDE.md | `humanlayer-12-factor-agents/CLAUDE.md:5-17` | persona belongs agent-side (Q-11) |
| 17 | **REJECT** | "documentarian, never critique" for all research | `codebase-analyzer.md:10-17` | fine for locator; our analyst must judge the spec |

---

## 8 · Files actually read

Full read:
- `humanlayer-humanlayer/README.md`, `CLAUDE.md`, `.claude/settings.json`
- `humanlayer-humanlayer/.claude/commands/`: `research_codebase.md`, `create_plan.md`, `iterate_plan.md`,
  `implement_plan.md`, `validate_plan.md`, `create_handoff.md`, `resume_handoff.md`, `ralph_research.md`,
  `ralph_plan.md`, `ralph_impl.md`, `local_review.md`, `oneshot.md`, `oneshot_plan.md`, `founder_mode.md`,
  `commit.md`, `ci_commit.md`, `describe_pr.md`, `create_worktree.md`
- `humanlayer-humanlayer/.claude/agents/`: `codebase-locator.md`, `codebase-analyzer.md`, `thoughts-analyzer.md`
- `humanlayer-humanlayer/hld/README.md`, `hld/CLAUDE.md`; `hlyr/THOUGHTS.md`; `hack/spec_metadata.sh`
- `humanlayer-claudelayer/`: `README.md`, `CLAUDE.md`, `package.json`, `.mcp.json`, `.claude/settings.json`,
  `src/index.ts`, `src/subagents.ts`, `.claude/agents/counter.md`, `.claude/commands/exhaustive-research.md`
- `humanlayer-skills/`: `README.md`, `plugins/show-me/skills/show-me/SKILL.md`, `.../show-me/agents/openai.yaml`,
  `plugins/show-me/.claude-plugin/plugin.json`, `plugins/visual-pr/skills/visual-pr/SKILL.md`,
  `.../visual-pr/references/describe_pr_final_answer.md`, `.../pr_description_template.md`,
  `plugins/improve-claude-md/skills/improve-claude-md/SKILL.md`,
  `plugins/design-control-loop/skills/design-control-loop/SKILL.md`, `.../references/control-loop-taxonomy.md`,
  `plugins/build-iterated-agentic-loop/skills/build-iterated-agentic-loop/SKILL.md`,
  `.../references/prompt-template.md`, `memory-template.md`, `skill-template.md`, `agent-iteration.ts`
- `humanlayer-12-factor-agents/content/factor-03…`, `factor-05…`, `factor-06…`, `factor-10…`, `factor-11…`, `factor-12…`
- `humanlayer-advanced-context-engineering-for-coding-agents/ace-fca.md`, `wsff.md`,
  `side-quests/where-does-the-time-go.md`

Partial / targeted read:
- `humanlayer-humanlayer/.claude/commands/linear.md` (status sections, grep), `debug.md:1-80`; agents
  `codebase-pattern-finder.md` (1-60, 180-227), `thoughts-locator.md:1-50`, `web-search-researcher.md:1-30`
- `humanlayer-humanlayer/hld/PROTOCOL.md` (methods, decisions, data types), `humanlayer.md:1-40`,
  `hlyr/README.md` (88-135, 255-300), `hlyr/src/commands/launch.ts` (grep), `hlyr/src/commands/claude/init.ts` (grep)
- Diffs only: `create_plan_nt.md`, `research_codebase_generic.md` vs originals; claudelayer agents/commands vs humanlayer;
  the two loop plugins' `references/`
- `humanlayer-skills/.claude-plugin/marketplace.json:1-40`, `narrow-react-prop-types/SKILL.md:1-60`,
  `agent-runner-templates.md` (grep), `workflow-template.yml` (grep)
- `humanlayer-12-factor-agents/README.md:1-80`, `CLAUDE.md`, `factor-01/02/04/07/08/09` (prose, code elided),
  `appendix-13-pre-fetch.md` (prose)
- `benchmarking-*-slop-code-bench.md` (headings only)

Not read: `create_plan_generic.md`/`iterate_plan_nt.md`/`describe_pr_nt.md`/`ci_describe_pr.md` beyond existence
(variants), hld Go sources, `humanlayer-wui/`, `apps/`, `drafts/`, `workshops/`.
