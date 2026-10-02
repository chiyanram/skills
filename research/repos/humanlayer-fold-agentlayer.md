# humanlayer `fold` + `agentlayer` — per-repo deep report (2026-10-01)

Both are **agent runtimes (SDK + CLI)**, not rulebooks. They have almost nothing on rules/roles/review *process*
(G1/G2/G5) and a lot on **the final step** (F-1 / D1): a coordinator over workers, an event stream a web UI can
render, durable resumable state, human approvals across a sub-agent tree.

Paths below are relative to `refs/` (`.scratch/one-rulebook/refs/`). `F:` = `humanlayer-fold/`,
`A:` = `humanlayer-agentlayer/`. Both clones are shallow (1 commit, 2026-09-30); stars unknown.

```
 WHAT EACH IS FOR US
 agentlayer (legacy, v0.0.36)        fold (current, v0.0.0, Effect v4 rc)
 ─ approvals hot+cold  ◄── USE ──►   ─ durable event log + live deltas  ◄── USE
 ─ JSON AgentState, portable         ─ steer / stop / interrupt / send(agentId)
 ─ one merged event stream           ─ RLM mode = coordinator with NO bash
 ─ docs-agent = CI review agent      ─ RPI roster incl. implementation-reviewer
 ─ yjs-fs: shared FS for a web UI    ─ Cloudflare Durable-Object host (HTTP)
                 \                     /
                  └── our AG-UI coordinator box (D1) wants BOTH halves ──┘
```

---

# Part 1 — `humanlayer-fold`

## 1. What it is

| | |
|---|---|
| What | "Effect-native, provider-agnostic, isomorphic agent core" + opinionated coding agent, CLI, TUI (`F:README.md:5`) |
| Maturity | unpublished `0.0.0` (`F:packages/fold-core/package.json:3`), Effect `4.0.0-rc.109` (`F:AGENTS.md:8`); real release pipeline exists (`F:docs/publishing.md`) |
| Relationship | HumanLayer calls agentlayer "legacy agent SDK" and codelayer "current agent" (`F:.humanlayer/workspace.json:28`); fold ports agentlayer's prompts (`F:packages/fold-agent/src/Mode/Rlm.ts:3`) |
| The one idea | **The session is an append-only, schema-versioned event log; everything (UI, resume, subagents, compaction) is a projection of it** (`F:packages/fold-core/src/EventLog/EventLogService.ts:7-20`, `Api/StartSession.ts:24-27`) |

## 2. File tree (what matters)

```
humanlayer-fold/
├── AGENTS.md                       41 lines: stack, commands, "read Effect v4 source not v3 docs"
├── .humanlayer/workspace.json      worktree template + sibling repos (riptide task workspaces)
├── .oxlintrc.jsonc                 lint = enforced standards (anti-slop + automation plugins)
├── .claude/skills/                 7 skills; effect-program-design = repo standard; codebase-design = mattpocock copy
├── tools/oxlint/{anti-slop,automation}/rules/*.ts   vendored custom lint rules
├── packages/
│   ├── fold-core/src/
│   │   ├── EventLog/Schemas.ts           every durable row type (session_started … agent-finished)
│   │   ├── AgentEvents/AgentEventsService.ts  FoldEvent = log row | ephemeral delta
│   │   ├── Api/StartSession.ts           FoldSession: send/steer/stop/interrupt/switchModel/events
│   │   ├── AgentRuntime/AgentRuntimeLayer.ts  the loop
│   │   ├── HookRunner/{Types,Schema}.ts  preRequest / preToolUse / postToolUse / onComplete
│   │   ├── Subagents/*                   fresh / fork / resume-by-id, roster = tool argument
│   │   ├── Compaction/CompactionPrompts.ts  pi's structured checkpoint prompt
│   │   ├── StopConditions/StopConditions.ts doom-loop detector
│   │   └── Tools/Contracts.ts            model-facing tool contracts (subagent, skill, …)
│   ├── fold-agent/src/
│   │   ├── Mode/{Mode,ModeName,Rlm,Rpi,Subagents,Launch}.ts   modes + rosters + prompts
│   │   ├── Memory/AgentFiles.ts         AGENTS.md / CLAUDE.md discovery
│   │   ├── Skills/DiskSkills.ts         SKILL.md scan (claude-compatible roots)
│   │   ├── Compatibility/Codex*,Grok*   read Codex/Grok plugins, skills, instructions
│   │   ├── Config/{ConfigSchema,FoldInfo}.ts  roles smart/fast/orchestrator, profiles
│   │   ├── EventLog/JsonlLayer.ts · Session/SessionLayout.ts   ~/.fold/sessions/<slug>/<id>.jsonl
│   ├── fold-cli/src/{Run.ts, tui/*}     headless runner + OpenTUI (in-process, no server)
│   └── fold/postinstall.mjs             native binary per platform (`foldcode`)
└── examples/alchemy-cloudflare/src/     fold hosted behind HTTP, one Durable Object per session
```

## 3. Approach

### a. Rules / standards

| What | Where | Evidence |
|---|---|---|
| Always-loaded index | `AGENTS.md`, 41 lines, stack + commands only, no rules | `F:AGENTS.md:1-41` |
| Repo coding standard | one skill, `effect-program-design`: defaults → sections → **Review checklist at the end** | `F:.claude/skills/effect-program-design/SKILL.md:31-46`, `:134-142` |
| Detail on demand | skill points at 3 reference files rather than inlining | `…/effect-program-design/SKILL.md:124-129` |
| Rules with teeth | custom oxlint rules, all `error`: no silent error swallow, no module mocking, no type assertions | `F:.oxlintrc.jsonc:10-24,55-58`; `F:tools/oxlint/automation/rules/no-silent-error-swallow.ts:22-31` |
| Upstream skills | `codebase-design`, `improve-codebase-architecture` are **copied** mattpocock skills, not plugins | `F:.claude/skills/codebase-design/SKILL.md:1-10` |
| How the runtime loads rules | global `~/.fold/AGENTS.md` → `~/.agents/AGENTS.md` → `~/.codex/AGENTS.md` (first wins), then every dir root→cwd, `AGENTS.md` else `CLAUDE.md`, plus `.local.md` overlay; baked once per model epoch | `F:packages/fold-agent/src/Memory/AgentFiles.ts:1-16,38-49` |
| Skills discovery | Claude-compatible roots scanned first, then fold/Agent-Skills roots; later shadows earlier; Agent Skills frontmatter validation | `F:packages/fold-agent/src/Skills/DiskSkills.ts:1-9` |
| Cross-harness | reads Codex's enabled plugins from `~/.codex/config.toml` and their skill roots | `F:packages/fold-agent/src/Compatibility/CodexPlugins.ts:28-40`, `CodexCompatibility.ts:19-35` |

Takeaway: the runtime treats `AGENTS.md` as the agent-agnostic index and `CLAUDE.md` as fallback — the same
convention as Q-2. Agent side (`~/.fold/AGENTS.md`) and project side (walked dirs) are separate layers (Q-11).

### b. Process / workflow

No SDLC process. "Process" is **modes**:

| Mode | Root tools | Prompt | Role binding | Evidence |
|---|---|---|---|---|
| `default` (coding) | full toolset + skill + subagent | "fold, a headless coding agent… delegate when a step would burn context" | `smart` | `F:packages/fold-agent/src/Mode/Mode.ts:56-82` |
| `rlm` (orchestrator) | read/write/edit/apply_patch + skill + subagent, **no bash** | "maintain coherency… delegate all non-trivial operations" | `orchestrator` (falls back to `smart`) | `F:packages/fold-agent/src/Mode/Rlm.ts:23-73` |
| `--rpi` flag | not a mode; appends 6 specialists to any mode's roster | `RPI_HINT_PROMPT` | per agent | `F:…/Mode/Mode.ts:10-12`, `Rpi.ts:35-39`, `:767-784` |

- A mode is data: name + role + prompt + `buildTools` (`F:…/Mode/Mode.ts:39-54`); adding one is one Record entry
  (`F:…/Mode/ModeName.ts:1-21`).
- RPI file artefacts live in `.humanlayer/tasks/<task>/` (ticket, research, prd, tdd, outline, plan), with a
  **document precedence rule** (`F:…/Mode/Rpi.ts:583-588`).
- Human gate: implementers pause after each phase — "Phase [N] Complete - Ready for Manual Verification"
  (`F:…/Mode/Rpi.ts:549-561`, `:619-628`). Progress state = checkboxes in the plan file (`:606-613`).
- Session state on disk: `~/.fold/sessions/<project-slug>/<sess_id>.jsonl` (`F:packages/fold-agent/src/Session/SessionLayout.ts:1-8`).

### c. Roles / agents

Agents are **code values** (`defineSubagent({name, description, systemPrompt[], tools, model})`), not markdown files.

| Agent | Tools (capability = what it holds) | Model role | Evidence |
|---|---|---|---|
| `general-purpose` | full coding + skills + roster incl. itself (recursion) | smart | `F:…/Mode/Subagents.ts:194-211` |
| `bash` | bash only; "cannot ask clarifying questions" | fast | `:56-68`, `:162-170` |
| `researcher` | read + bash + skill, **no edit tool at all** | fast | `:172-182` |
| `web-search-researcher` | web_search + web_fetch | fast | `:184-192` |
| `codebase-locator/-analyzer/-pattern-finder` | bash / read+bash; "documentarian, not a critic" | fast | `F:…/Mode/Rpi.ts:672-704` |
| `implementation-reviewer` | read + bash | fast | `:706-714` |
| `implementer-agent`, `outline-implementer-agent` | full coding + bash/general-purpose delegates | smart | `:716-734` |

Key design rules stated in source:
- **Capability by withholding, not by telling**: researcher "holds no write/edit/apply_patch value at all rather than
  being merely told not to edit" (`F:…/Mode/Subagents.ts:172-173`).
- **Depth is a roster choice, never an engine setting** (`F:…/Mode/Subagents.ts:15-17`).
- **Models bind by role name** (`smart`/`fast`/`orchestrator`), resolved per dispatch; `setProfile` rebinds live
  (`F:packages/fold-agent/src/Config/ConfigSchema.ts:64-79`; `F:packages/fold-core/src/Api/StartSession.ts:258-266`).
- Profiles are named role maps that may pin a mode (`ultraclaude` = RLM on fable-5) (`F:…/Config/FoldInfo.ts:86-118`).
- Ported prompts kept "byte-faithful to the sources"; additions ride as a **second** prompt block, never spliced
  (`F:…/Mode/Rpi.ts:16-19`). This is a single-source discipline for prompt text.

### d. Review & verification

| Item | Shape | Evidence |
|---|---|---|
| `implementation-reviewer` | input: task dir / plan file + base branch; runs `git diff main...HEAD`; output four fixed sections: as planned · deviations · additions · planned-not-done; "None" not omitted; no good/bad judgment | `F:…/Mode/Rpi.ts:437-509` |
| Its purpose | feed **PR descriptions** for reviewers who already approved the plan | `:440-442`, `:709-710` |
| Cost control | runs on `fast` role; shares ast-grep outline guidance "before reading full source files" | `:713`, `F:…/Mode/Subagents.ts:107-119` |
| Doom loop | identical tool-call batch N times → graceful stop | `F:packages/fold-core/src/StopConditions/StopConditions.ts:1-5` |
| Lint gate | oxlint error-level rules = standards that need no reviewer | `F:.oxlintrc.jsonc:10-24` |

No standards reviewer, no criteria selection, no round cap. The reviewer is a **plan↔diff deviation reporter**,
which is our stage-8 "AC cited in both directions" idea in another shape.

### e. Context engineering

- Subagent result envelope: `agent_id` + turns + `<subagent_result>` + outcome note telling the parent it may resume
  by id (`F:packages/fold-core/src/Subagents/SubagentTool.ts:69-80` and following).
- Subagent selector: exactly one of `agent` (fresh) · `agent_id` (resume, full prior context kept) · `fork` (copy of
  caller's context); optional `skill` preloaded after the prompt (`F:packages/fold-core/src/Tools/Contracts.ts:241-290`).
  `skill` preload = a **brief + one named skill** handed to a worker — exactly G6's briefed worker.
- Compaction: pi's structured checkpoint (Goal · Constraints · Progress · Key Decisions · Tactics & Commands · Next
  Steps · Critical Context), incremental update merges into previous summary
  (`F:packages/fold-core/src/Compaction/CompactionPrompts.ts:10-80`). Top-of-turn proactive + one reactive retry on
  overflow (`F:packages/fold-core/src/AgentRuntime/AgentRuntimeLayer.ts:1-11`).
- Steering: queued text drains between turns as an ordinary user message (`AgentRuntimeLayer.ts:293-296`).
- Prefix stability: agentfiles baked once per epoch; a change writes one durable transition on resume
  (`F:…/Memory/AgentFiles.ts:12-14`; `F:…/Mode/Launch.ts:11-14`).
- Outputs too large → `OutputStore` full-output store per session (`F:…/Mode/Mode.ts:35-36`).

### f. Packaging & distribution

- npm `@humanlayer/fold` with per-platform native packages chosen in `postinstall.mjs` (AVX2 detection)
  (`F:packages/fold/package.json:8-17`; `F:packages/fold/postinstall.mjs:12-30`).
- Libraries publish in lockstep from `v*` tags; vendored providers carry `UPSTREAM.md` with checksum + delta
  (`F:docs/publishing.md:1-16`).
- Per-machine config: `~/.fold/config.jsonc` (providers + roles + profiles), credentials via `apiKeyEnv`
  (`F:…/Config/ConfigSchema.ts:1-14`). Managed tool binaries (rg, fd, ast-grep) into `~/.fold/bin`
  (`F:…/Mode/Subagents.ts:115-117`).
- Worktree-per-task via `.humanlayer/workspace.json`: `pathTemplate`, `branchTemplate`, `copyGlobs` for local-only
  files, sibling repos (`F:.humanlayer/workspace.json:1-30`). Same idea as G6's worktree-per-(item, role).

### g. Hosting / UI / protocol — **the part that matters for D1**

```
 FoldSession (one durable log, one root agent)          F:packages/fold-core/src/Api/StartSession.ts:196-277
   send(text, {agentId?})   → runs or queues; can target ANY agent incl. a finished subagent
   steer(text, {agentId?})  → inject into a RUNNING agent between turns
   stop(reason)             → graceful, finish current tool batch
   interrupt({agentId?})    → hard cancel; durable markers still written
   switchModel / setProfile / compact / setTitle
   events(fromSeq)          → Stream<FoldEvent>                      ◄── the UI feed
   entries                  → snapshot of all durable rows

 FoldEvent = { kind:'log',   entry: LogEntry }               durable, versioned, replayable
           | { kind:'delta', agentId, parentAgentId, toolCallId, part }   ephemeral, never persisted
              part = text-delta | reasoning-delta | tool-progress
                                                        F:…/AgentEvents/AgentEventsService.ts:16-30
```

| Durable row (`_tag`) | Evidence (`F:packages/fold-core/src/EventLog/Schemas.ts`) | Our AG-UI mapping (ours, not verified vs spec here) |
|---|---|---|
| `session_started` | `:246-269` | run/thread start |
| `agent_started` (agentId, parentAgentId, toolCallId, mode fresh/fork, agentType) | `:271-308` | step/subagent start — the tree edge |
| `user-message`, `assistant-message`, `tool-result` | `:343-427` | messages + tool call start/end |
| `compaction`, `model-change`, `tools-change`, `thinking-change` | `:453-560` | state delta / custom |
| `agent-finished` outcome completed·stopped·interrupted·error | `:561-592` | run finished / run error |
| `session_title`, `error` | `:594-638` | custom / error |
| delta `text-delta`, `reasoning-delta`, `tool-progress` | `AgentEventsService.ts:16-19` | text content / thinking / tool progress |

- Each row carries `seq`; `events(fromSeq)` replays then follows (`F:…/EventLog/EventLogService.ts:12-16`) —
  **reconnect = resubscribe from last seq**. Rows are schema-versioned with upcast on decode
  (`Schemas.ts:21-33`).
- Remote host proof: `examples/alchemy-cloudflare` — **one Durable Object per session**, log in its SQLite,
  `POST /sessions/:id/messages {text, whenRunning: queue|steer|interrupt}`, `GET /sessions/:id` = all rows
  (`F:examples/alchemy-cloudflare/src/Api.ts:1-8`; `ChatSession.ts:72-80`). Crash/deploy recovery: on wake, nudge the
  root to continue, at most 3 nudges per cut-off turn (`ChatSession.ts:8-10,35,117-125`). Streaming deltas over HTTP is
  explicitly **not done yet** (`F:examples/alchemy-cloudflare/README.md`, "Limits").
- **No human approval in fold.** Hooks can rewrite params or `replaceResult` but there is no "ask" decision
  (`F:packages/fold-core/src/HookRunner/Schema.ts:46-60`); fold-agent/fold-cli install no `preToolUse` hooks at all
  (grep of `packages/fold-agent/src`, `packages/fold-cli/src`: none). Safety is by tool withholding (RLM has no bash).
- TUI is in-process (`F:packages/fold-cli/src/tui/HostedTuiSession.ts:1-40`, `LiveSessionHost.ts:1-40`); no server
  protocol beyond the Cloudflare example.

## 4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `F:packages/fold-agent/src/Mode/Rpi.ts:437-509` — `implementation-reviewer` | A reviewer that does not judge: four mandatory sections, "None" never omitted, input = plan + diff. Cheap (fast model), deterministic shape, directly usable for our stage-8 AC↔code check and the MR description. |
| 2 | `F:packages/fold-agent/src/Mode/Rlm.ts:23-47` — RLM orchestrator prompt | 25 lines; "You have NO bash tool" paired with actually removing bash. Rule 4: give each sub-agent "all relevant context it needs" = our brief rule. Coordinator-as-contract in miniature. |
| 3 | `F:packages/fold-agent/src/Mode/Subagents.ts:122-134` — general-purpose prompt | Delegation economics in 4 lines: each dispatch costs a model call, do not nest deeply, "parent sees only your final message… end with what you did, found, could not complete". Good worker-report contract. |

Honourable mention: `F:packages/fold-core/src/Compaction/CompactionPrompts.ts:17-50` — the "Important Tactics &
Commands" section (proven commands + failed approaches) is exactly what our long `/crq` sessions lose on compact.

## 5. Against our decisions

| Decision | Verdict | Evidence |
|---|---|---|
| G1 rules layers (AGENTS.md index, agent vs project side) | **confirms** — runtime loads global agent file, then project walk; AGENTS.md first, CLAUDE.md fallback; `.local.md` overlay per machine | `F:…/Memory/AgentFiles.ts:1-16` |
| G1 upstream = plugins, never copies | **contradicts (their practice)** — mattpocock skills copied into `.claude/skills/` | `F:.claude/skills/codebase-design/SKILL.md` |
| G2 one crq + role labels | **neutral / new idea** — roles are model tiers (`smart/fast/orchestrator`) not SDLC roles; a profile pins mode+models. Suggests: role label → model tier is a separate axis from role → stages | `F:…/Config/ConfigSchema.ts:64-104` |
| G3 Standards ‖ Spec review | **partially confirms Spec side** — implementation-reviewer = plan↔diff deviation report; no Standards reviewer, standards go to lint | `F:…/Mode/Rpi.ts:437-509`; `F:.oxlintrc.jsonc` |
| G5 5-section references | **confirms** — `effect-program-design`: defaults · sections · decided edges (`Keep a simple direct _tag guard…`) · references · **Review checklist at end** | `F:…/effect-program-design/SKILL.md:31-142` |
| G6 coordinator + briefed workers | **confirms strongly** — RLM root without bash; `subagent{agent, prompt, skill}` = role + brief + one skill; resume by `agent_id` = rework round on same worker | `F:…/Mode/Rlm.ts`; `F:packages/fold-core/src/Tools/Contracts.ts:241-290` |
| G6 qa fresh every round | **new nuance** — fold offers `fresh` vs `fork` vs `resume`; QA should be `fresh` (never fork the dev's context) | `Contracts.ts:241-266` |
| G4 coordinator-as-contract / tiers | **confirms** — FoldSession is a transport-free contract; TUI, CLI, Cloudflare HTTP are adapters | `F:…/Api/StartSession.ts:196-277`; `F:examples/alchemy-cloudflare/src/Api.ts` |
| F-1 / D1 AG-UI role boxes | **new idea** — durable log + ephemeral delta split, seq-resume, `whenRunning: queue|steer|interrupt`, one durable unit per session | see §3g |

## 6. Adopt / adapt / reject (fold)

| Rank | Verdict | What | File |
|---|---|---|---|
| 1 | **ADOPT** (D1) | Coordinator↔UI contract = `send/steer/stop/interrupt(agentId)` + `events(fromSeq)` over a durable, versioned log with ephemeral deltas beside it | `F:packages/fold-core/src/Api/StartSession.ts:196-277`; `AgentEvents/AgentEventsService.ts:16-30` |
| 2 | **ADOPT** | `implementation-reviewer` shape for stage 8 / MR description: 4 sections, plan(REQ ACs) vs diff, no judgment, fast model | `F:packages/fold-agent/src/Mode/Rpi.ts:437-509` |
| 3 | **ADOPT** (G6) | Coordinator gets no shell; capability by withholding tools, not by prompt | `F:…/Mode/Rlm.ts:49-73`; `Subagents.ts:172-182` |
| 4 | **ADAPT** | `whenRunning: queue | steer | interrupt` as the web UI's message-send semantics to a busy worker | `F:examples/alchemy-cloudflare/src/ChatSession.ts:72-80` |
| 5 | **ADAPT** | Restart recovery: on box wake, nudge an unfinished run ≤3 times | `ChatSession.ts:8-10,35,117-125` |
| 6 | **ADAPT** | Compaction template with "Tactics & Commands" + "failed approaches" | `F:packages/fold-core/src/Compaction/CompactionPrompts.ts:17-50` |
| 7 | **ADAPT** | Role → model tier map (`smart/fast`) separate from role → stages; reviewers on `fast` | `F:…/Config/ConfigSchema.ts:64-79`; `Rpi.ts:21-24` |
| 8 | **ADOPT** | Ported prompt stays byte-faithful; local additions as a second block — keeps upstream text single-source | `F:…/Mode/Rpi.ts:16-19` |
| 9 | **REJECT** | Building on fold itself: Effect v4 rc, `0.0.0`, no approvals, TUI in-process; our box is Claude Agent SDK | `F:AGENTS.md:8`; `HookRunner/Schema.ts:46-60` |
| 10 | **REJECT** | Copying upstream skills into the repo | `F:.claude/skills/codebase-design/` |

---

# Part 2 — `humanlayer-agentlayer`

## 1. What it is

| | |
|---|---|
| What | "HumanLayer's toolkit for building coding agents" — resumable loop, tool interface ≠ executor (`A:README.md:3`) |
| Maturity | `agentlayer-core` `0.0.36` (`A:packages/agentlayer-core/package.json:5`); called "legacy" by fold's workspace (`F:.humanlayer/workspace.json:28`); codelayer is driven by HumanLayer's closed-source **riptide daemon** (`F:.humanlayer/workspace.json:24`) |
| The one idea | **State is a plain JSON token you can stop, store, approve hours later in another process, and resume** (`A:packages/docs/content/introduction/motivation.md:17-21`; `A:packages/agentlayer-core/src/state.ts:74-104`) |

## 2. File tree (what matters)

```
humanlayer-agentlayer/
├── AGENTS.md / CLAUDE.md         36 lines each — byte-identical copies, not a symlink
├── packages/
│   ├── agentlayer-core/src/
│   │   ├── agent.ts               the loop (1950 lines): steps, approvals, stop, compaction
│   │   ├── agent-run.ts           AgentRun: async-iterable event stream + resolveApproval (hot path)
│   │   ├── state.ts               AgentState JSON + withApprovals (cold path) + sub-agent tree paths
│   │   ├── hooks/approval.ts      next | deny | ask chain
│   │   ├── tools/subagent*.ts     subagent tool: type / agent_id resume / fork_turns / skill
│   │   ├── prompts/{orchestrator,subagent}.txt   the RLM text fold ported
│   │   └── interfaces/*.ts        tool contracts (read, edit, bash, comment, skill…)
│   ├── agentlayer-filesystem, -justbash      executors
│   ├── yjs-fs, yjs-fs-react, agentlayer-yjs-fs*   CRDT shared filesystem + presence + comments
│   └── docs/content/concepts/*.md            the design rationale (hooks, state, streaming, subagents)
├── agents/
│   ├── codelayer/src/              CLI agent: --rlm, --rpi, --tars; rpi-agents/* specialists
│   └── docs-agent/src/             CI review→apply agent (reviewer.ts, editor.ts, workflow.ts, github.ts)
└── examples/yjs-fs-editor + yjs-fs-agent   browser editor and an agent sharing one Y.Doc via Caddy
```

## 3. Approach

### a. Rules / standards

| What | Evidence |
|---|---|
| `AGENTS.md` = map + commands + contribution policy pointer; `CLAUDE.md` is a **duplicated copy** (two files to drift) | `A:AGENTS.md:1-36`; `A:CLAUDE.md` (identical, verified by diff) |
| Single source named explicitly for one policy: "`CONTRIBUTING.md` is the source of truth" + list of files to keep aligned | `A:AGENTS.md:33-36` |
| Runtime: repo instructions injected as one `# Repository Instructions` block | `A:packages/agentlayer-core/src/prompts/repo-instructions.ts:6-13` |
| No coding-standard skill; formatter `biome`, `bun check` the one gate | `A:AGENTS.md:26-27` |

### b. Process / workflow

- No SDLC. RPI exists only as specialist agents; implementer description says use it "when an RPI skill asks"
  (`A:agents/codelayer/src/rpi-agents/implementer-agent/index.ts:5-6`) — the skills (RPI workflow) live outside this
  repo (riptide plugin, per `F:…/Mode/Rpi.ts:8`).
- **docs-agent** is the only workflow, and it is a clean two-stage gate:

```
 PR opened/sync (src changed) ─► review mode ─► reviewer agent (read/glob/grep/list, 12 steps)
                                                 └► upsert ONE PR comment  <!-- docs-reviewer:sha=… -->
 human comments "@docs-agent apply" ──────────► apply mode ─► reuse reviewer comment as recommendations
                                                 └► editor agent (fs tools + approval hook: only docs/*.md, 20 steps)
                                                 └► build check ─► commit+push ─► upsert docs-editor comment
```
  Evidence: `A:agents/docs-agent/src/workflow.ts:102-104,118-206`; `A:agents/docs-agent/src/github.ts:29-33`;
  `A:.github/workflows/docs-agent.yml`. The human gate is a **comment command on the PR**, the handoff record is
  **the PR comment** — same as G2's "GitLab comment = handoff record".

### c. Roles / agents

| Agent | Made of | Evidence |
|---|---|---|
| specialist factory | `new Agent({model, tools, system:[prompt, ...extra], stopWhen: [doomLoop(3)]})` | `A:agents/codelayer/src/rpi-agents/shared.ts:14-24` |
| roster | general-purpose, bash, implementer, outline-implementer, locator, analyzer, pattern-finder, web-search, library-researcher (if keys) | `A:agents/codelayer/README.md` "Sub-agents" |
| sub-agent thinking | children throttled to `low` reasoning relative to parent; research at `xhigh` | `A:agents/codelayer/src/agent.ts:325-328,400-413` |
| persona | `--tars` adds a persona block; personas are prompt additions, not identities | `A:agents/codelayer/README.md` key flags |

No `implementation-reviewer` here — fold added it from the riptide plugin source (`F:…/Mode/Rpi.ts:437`).

### d. Review & verification

| Item | Shape | Evidence |
|---|---|---|
| docs reviewer input | **diff + changed-file list pushed in** (not fetched by the agent) | `A:agents/docs-agent/src/reviewer.ts:17-36` |
| docs reviewer output | fixed `## Verdict / ## Recommended Updates / ## Files Worth Updating` | `:23-26` |
| scope rule | "Only recommend concrete markdown updates tied to the provided diff"; "avoid speculative work" | `:19-22,74-77` |
| caps | `maxSteps(12)` reviewer, `maxSteps(20)` editor; specialists `doomLoop(3)` | `reviewer.ts:79`; `editor.ts:80`; `shared.ts:20` |
| path gate | approval hook **denies** write/edit outside `packages/docs/content/*.md` | `A:agents/docs-agent/src/editor.ts:57-66` |
| known hole (self-documented) | hook does not cover `bash`; build check is a no-op | `A:agents/docs-agent/README.md` "Key exports", intro |
| idempotence | one comment per agent per PR, keyed by HTML marker with sha | `A:agents/docs-agent/src/github.ts:29-33` |

### e. Context engineering

- One merged event stream at the root regardless of depth; each event tagged `agentId` + `parentToolCallId` so the
  call tree is rebuilt from a flat stream (`A:packages/docs/content/concepts/streaming.md:137-181`).
- Sub-agent tool: `subagent_type` (fresh specialist, "must be self-contained") · `agent_id` (continue) ·
  `fork_turns` all/none/N · `skill` preload (`A:packages/agentlayer-core/src/tools/subagent.ts:11-58`).
- Subagent tool prompt (Claude-Code-style): "Clearly tell the agent whether you expect it to write code or just to do
  research" (`A:packages/agentlayer-core/src/prompts/subagent.txt:22-27`).
- Context surgery via `preRequest` hook; compaction is a hook, not a fixed engine (`A:packages/docs/content/concepts/hooks.md:13-27`).
- `sanitizeStateForPersistence` strips provider session ids so state resumes on a different process
  (`A:packages/agentlayer-core/src/state.ts:193-208`).

### f. Packaging

- Bun monorepo, per-package `build.ts`, tagged release scripts (`A:scripts/release/*.ts`); `codelayer` as npm CLI
  (`bunx codelayer`) (`A:agents/codelayer/README.md`).
- Per-machine: auth store `~/.humanlayer/agent-sdk`, env overrides (`A:agents/codelayer/README.md` "Run it").
- External PRs require a "vouch" (`A:AGENTS.md:31-36`; `A:.github/workflows/vouch-*.yml`).

### g. Hosting / UI / protocol — **approvals across a tree, the piece fold lacks**

```
 agent.run({state, stream:true}) → AgentRun  (AsyncIterable<AgentEvent>)      A:…/agent-run.ts:101-228
   events: message · approvalRequested · tokenUsage · stepStart/Finish · textStart/Delta/End
           toolInputStart/Delta/End · reasoningStart/Delta/End · compaction   A:…/agent-run.ts:15-99
   every event: { agentId?, parentToolCallId? }                               A:…/agent-run.ts:10-13

 APPROVAL                                    HOT (run alive)                  COLD (run ended / other process)
 hook chain: next | deny(reason) | ask(msg)  run.resolveApproval(id, approve|deny)   result.state.pendingToolCalls
   A:…/hooks/approval.ts:5-67                 → own resolvers, then recurses into     → withApprovals(state, decisions)
                                                activeChildren   A:…/agent-run.ts:146-174   → agent.run({state})
                                              returns false ⇒ fall back to COLD       A:…/state.ts:293-306
 finishReason: complete|maxSteps|stopCondition|interrupted|approvalRequired|error    A:…/agent.ts:128
 partial approvals OK: approve 1 of 3, others stay pending                          A:…/state.ts:294-306
 approvals from any depth surface at root, resolved at root                         A:docs/…/streaming.md:191-202
```

- `getAllPendingApprovals(state)` returns `{path, pending}` across the sub-agent tree (`A:…/state.ts:254-270`);
  `AgentPath` = list of agentIds (`:38-45`).
- **yjs-fs**: a CRDT filesystem with comments and live-cursor presence so humans in a browser and agents edit one tree
  (`A:packages/yjs-fs/README.md:1-5`); tool interface `list_comments` etc. (`A:packages/agentlayer-core/src/interfaces/comment.ts`);
  example wires a Vite editor and an agent through Caddy + durable-streams long-poll/SSE
  (`A:examples/yjs-fs-editor/Caddyfile`; `A:examples/yjs-fs-agent/src/run.ts:1-40`).

## 4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `A:packages/agentlayer-core/src/agent-run.ts:146-174` + `state.ts:293-306` | Hot/cold approval in ~60 lines: deliver to a live loop if possible, else apply decisions to serialized state and re-run. The exact semantics an AG-UI "interrupt → human answers → resume" needs, including a box that restarted meanwhile. |
| 2 | `A:agents/docs-agent/src/reviewer.ts:17-36,65-80` | Minimal diff-scoped reviewer: diff and file list pushed in, read-only tools, fixed 3-section output, 12-step cap, "avoid speculative work". A worked instance of G3/Q-9 at a fraction of our cost. |
| 3 | `A:agents/docs-agent/src/workflow.ts:118-206` + `github.ts:29-33` | Review→human-comment→apply as one CLI with two modes; one idempotent PR comment per agent keyed by sha; refuses to run on a dirty tree (`:148-153`). Template for a fleet worker's GitLab handoff. |

## 5. Against our decisions

| Decision | Verdict | Evidence |
|---|---|---|
| G1 rules layers / Q-2 `CLAUDE.md = @AGENTS.md` | **confirms by counter-example** — they keep two identical copies, which is the drift Q-1 forbids | `A:AGENTS.md`, `A:CLAUDE.md` |
| G2 GitLab comment = handoff record | **confirms** — docs-agent's state lives in marked PR comments; apply reuses reviewer's comment | `A:agents/docs-agent/src/workflow.ts:155-174` |
| G3 diff-scoped review, inputs pushed in, findings only, caps | **confirms** — diff pushed in, fixed sections, `maxSteps(12)` | `A:agents/docs-agent/src/reviewer.ts` |
| G3 round cap | **confirms shape** — review once, apply on human command; no loop | `workflow.ts:118-206` |
| G5 5-section references | **no evidence** — no standards text | — |
| G6 coordinator + briefed workers | **confirms** — orchestrator prompt + `subagent_type` "must be self-contained"; skill preload | `A:…/prompts/orchestrator.txt`; `A:…/tools/subagent.ts:31-58` |
| G6 workers never talk to you; coordinator relays | **new mechanism** — child approvals bubble to root and are resolved at root; that is "coordinator relays every question" as a protocol, not a convention | `A:docs/…/streaming.md:191-202`; `agent-run.ts:146-174` |
| G4 coordinator-as-contract | **confirms** — Agent/AgentRun is transport-free; docs-agent, CLI, riptide daemon are adapters | `A:agents/codelayer/README.md` |
| F-1 AG-UI web app | **new idea** — approval-as-event + hot/cold resolve; tool-level path gates as approval hooks; yjs-fs for live shared artefacts | §3g |

## 6. Adopt / adapt / reject (agentlayer)

| Rank | Verdict | What | File |
|---|---|---|---|
| 1 | **ADOPT** (D1) | Approval protocol: `approvalRequested{agentId, parentToolCallId, toolCallId, message}` on one root stream; resolve hot, else cold via persisted state; partial decisions | `A:packages/agentlayer-core/src/agent-run.ts:15-26,146-174`; `state.ts:254-306` |
| 2 | **ADOPT** (G3) | Reviewer contract: diff + changed files pushed in, read-only tools, fixed sections, step cap | `A:agents/docs-agent/src/reviewer.ts:17-80` |
| 3 | **ADOPT** (G2/G6) | One idempotent MR comment per (agent, MR), marker `<!-- name:sha=… -->`, updated not re-posted | `A:agents/docs-agent/src/github.ts:29-33` |
| 4 | **ADAPT** | Path gates as approval hooks (`deny` outside allowed paths) — for qa (read-only) and for a docs worker; note their bash hole and close it | `A:agents/docs-agent/src/editor.ts:57-66` |
| 5 | **ADAPT** | Flat tagged stream → tree in UI via `(agentId, parentToolCallId)` | `A:packages/docs/content/concepts/streaming.md:137-181` |
| 6 | **ADAPT** | Children on lower reasoning than parent by default | `A:agents/codelayer/src/agent.ts:325-328` |
| 7 | **CONSIDER** (later) | yjs-fs: shared REQ/plan docs a human edits in the browser while a worker edits them, with comments | `A:packages/yjs-fs/README.md:1-5` |
| 8 | **REJECT** | Duplicate `AGENTS.md`/`CLAUDE.md` copies | `A:AGENTS.md`, `A:CLAUDE.md` |
| 9 | **REJECT** | Building on agentlayer: "legacy", Vercel AI SDK, superseded by fold | `F:.humanlayer/workspace.json:28` |

---

# Part 3 — Combined: what the AG-UI coordinator box (D1) should take

```
 web UI (AG-UI client)
   │  POST message {to: agentId?, text, whenRunning: queue|steer|interrupt}     ◄ fold ChatSession.ts:72-80
   │  POST approval {toolCallId, approve|deny, reason}                          ◄ agentlayer resolveApproval
   │  GET  events?fromSeq=N  (SSE)                                              ◄ fold events(fromSeq)
   ▼
 coordinator box (Agent SDK)  — no shell; delegates                              ◄ fold Rlm.ts
   │ durable log rows (seq, versioned) + ephemeral deltas                        ◄ fold AgentEventsService
   │ every row/delta tagged agentId · parentAgentId · toolCallId                 ◄ both
   ▼
 worker boxes  — fresh per (item, role), brief + one skill; resume by agent_id for fix rounds   ◄ fold Contracts.ts
   approvals bubble to coordinator stream; answered there                         ◄ agentlayer streaming.md:191-202
   qa: read-only by tool withholding + path-deny hook                             ◄ fold Subagents.ts:172; agentlayer editor.ts:57
 handoff record = one marked MR comment per (agent, MR)                          ◄ agentlayer github.ts:29
```

Gaps neither repo solves: auth/multi-user on the UI, cross-box (network) transport for deltas (fold says
"replies arrive whole" in its HTTP example), and Claude Agent SDK specifics — the shapes transfer, the code does not.

---

# 7. Files actually read

fold (`refs/humanlayer-fold/`):
- `README.md`, `AGENTS.md`, `.humanlayer/workspace.json`, `.oxlintrc.jsonc` (head), `docs/publishing.md` (head),
  `tools/oxlint/README.md`, `tools/oxlint/automation/rules/no-silent-error-swallow.ts` (head)
- `.claude/skills/effect-program-design/SKILL.md`, `.claude/skills/codebase-design/SKILL.md` (head); listing of `.claude/skills/*/SKILL.md`
- `packages/fold/package.json`, `packages/fold/postinstall.mjs` (head)
- `packages/fold-agent/src/Mode/{ModeName,Mode,Rlm,Rpi,Subagents}.ts` (full), `Mode/Launch.ts` (head)
- `packages/fold-agent/src/Memory/AgentFiles.ts` (head), `Skills/DiskSkills.ts` (head), `Session/SessionLayout.ts` (head),
  `EventLog/JsonlLayer.ts` (head), `Config/ConfigSchema.ts` (1-120), `Config/FoldInfo.ts` (80-150),
  `Compatibility/CodexPlugins.ts` (head), `Compatibility/CodexCompatibility.ts`
- `packages/fold-core/src/EventLog/EventLogService.ts`, `EventLog/Schemas.ts` (200-310 + tag index),
  `AgentEvents/AgentEventsService.ts`, `Api/StartSession.ts` (1-290), `AgentRuntime/AgentRuntimeLayer.ts` (1-80 + grep),
  `HookRunner/Types.ts`, `HookRunner/Schema.ts` (1-60), `StopConditions/StopConditions.ts` (head),
  `Subagents/SubagentTool.ts` (1-80), `Projection/Projection.ts` (head), `Compaction/CompactionPrompts.ts` (1-80),
  `Tools/Contracts.ts` (228-300 + grep)
- `packages/fold-cli/src/tui/LiveSessionHost.ts` (head), `tui/HostedTuiSession.ts` (head), `Run.ts` (head + grep)
- `examples/alchemy-cloudflare/README.md`, `src/Api.ts`, `src/DurableObjectEventLog.ts` (head), `src/ChatSession.ts` (grep)

agentlayer (`refs/humanlayer-agentlayer/`):
- `README.md`, `AGENTS.md`, `CLAUDE.md` (diffed identical)
- `packages/agentlayer-core/src/agent-run.ts` (full), `hooks/approval.ts` (full), `pending.ts` (full),
  `state.ts` (1-306), `agent.ts` (1-60 + grep), `prompts/orchestrator.txt`, `prompts/subagent.txt`,
  `prompts/repo-instructions.ts`, `tools/subagent.ts` (1-60), `interfaces/comment.ts` (head), `package.json`
- `packages/docs/content/concepts/hooks.md` (1-80), `concepts/run-api.md` (193-230 + headings),
  `concepts/state.md` (headings), `concepts/streaming.md` (grep 137-202), `concepts/subagents.md` (grep),
  `introduction/motivation.md` (1-80)
- `packages/yjs-fs/README.md`, `examples/yjs-fs-editor/Caddyfile`, `examples/yjs-fs-agent/src/run.ts` (1-40)
- `agents/docs-agent/README.md`, `src/workflow.ts`, `src/reviewer.ts`, `src/editor.ts` (full), `src/github.ts` (grep)
- `agents/codelayer/README.md` (1-80), `src/agent.ts` (25-45, 440-480 + grep), `src/rpi-agents/{shared,index}.ts`,
  `src/rpi-agents/implementer-agent/index.ts`
- `.github/workflows/docs-agent.yml` (grep)

Context: `one-rulebook/map.md`, `requirements.md`, `design-overview.md`, `research/repos/_BRIEF.md`.
