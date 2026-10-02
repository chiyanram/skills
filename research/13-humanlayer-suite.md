# R11 · humanlayer suite: fold, agentlayer, skills, ACE, humanlayer, claudelayer

Answers `issues/20`. Read 2026-10-01 from the local clones under `refs/`. This file extends R5 (`05-humanlayer-cc-agui.md`):
12-factor and the first skills pass are **not** repeated here.
Prefixes: `fold/ agl/ hls/ ace/ hl/ cl/` = `refs/humanlayer-{fold, agentlayer, skills/plugins, advanced-context-engineering-for-coding-agents, humanlayer, claudelayer}/`.

## 1. What each repo is

| repo | what it is | maturity (last commit) |
|---|---|---|
| **fold** | An Effect-based, provider-agnostic agent core with a coding agent, CLI and TUI (`foldcode`). It has subagents, auto-compaction, a JSONL event log and a Cloudflare Durable Object host example | **active** (2026-09-30). npm `@humanlayer/fold` |
| **agentlayer** | A TS framework for coding agents: a resumable loop and JSON state, with tool interface kept separate from executor. Ships `codelayer` (CLI agent) and `docs-agent` (CI reviewer) | active (2026-09-30). fold's own workspace file calls it "HumanLayer's legacy agent SDK" (`fold/.humanlayer/workspace.json`) |
| **skills** | A Claude Code marketplace with 6 single-skill plugins. Since R5 it adds `show-me`, `visual-pr` and `narrow-react-prop-types` | active (2026-09-17) |
| **ACE** | Essays. `ace-fca.md` covers research→plan→implement and frequent intentional compaction. `wsff.md` ("Why Software Factories Fail") covers product → architecture → program design → vertical slices. | reference text (2026-08-04) |
| **humanlayer** | README: the code "is pretty much all deprecated". **Still readable and used as reference:** `.claude/commands/` (26), `.claude/agents/` (6), the `thoughts/` system (`hlyr/THOUGHTS.md`), the `hld` daemon protocol, and the `humanlayer-wui` Tauri UI | **deprecated** (2026-06-18). The commands are the canonical RPI prompts that ACE links to |
| **claudelayer** | One MCP tool, `launch`, that runs any `.claude/agents/*.md` or `commands/*.md` as a `claude -p` subprocess, so agents can recurse deeper than CC's nesting limit | **experiment**, 1 commit (2026-01-12) |

## 2. Workflow shape

| repo | coordinator → workers | research → plan → implement | human gates (where) |
|---|---|---|---|
| fold | `rlm` mode: the root is an orchestrator that has **no bash**, so all execution goes through subagents (`fold/packages/fold-agent/src/Mode/Rlm.ts`). `--rpi` adds 6 specialists (`Mode/Rpi.ts`) | The RPI roster is ported from a "riptide-rpi-terminal-plugin" (`Rpi.ts:1-25`). Plans live in `.humanlayer/tasks/<slug>/NN-plan-*.md` | None in code. The approval hooks belong to the host |
| agentlayer | `codelayer --rlm`: orchestrator + subagent tool (`agl/agents/codelayer/README.md`) | The same RPI roster under `src/rpi-agents/` | A tool approval ends the run as `finishReason: 'approvalRequired'`. State is saved, approved later, and resumed **in another process** (`agl/packages/docs/content/concepts/run-api.md`) |
| skills | `design-control-loop` / `build-iterated-agentic-loop` (R5) | — | A `/iterate` comment on an agent PR updates that PR **and** a memory file for future runs (`hls/narrow-react-prop-types/.../agent-narrow-component-props.yml`) |
| ACE | Subagents are "not about … anthropomorphizing roles". They are context control (`ace/ace-fca.md:191`) | R→P→I, with a worktree "only" for implement (`ace-fca.md:248`) | The human reviews **research and plan**, where leverage is highest (`ace-fca.md:318-333`). `wsff.md:403-589`: product → architecture → **program design** → vertical slices; author-opt-in spec walk with the future PR reviewer |
| humanlayer | `ralph_impl` creates a worktree, then launches a **new session** whose brief is a slash command (`humanlayer launch -w ~/wt/... "/implement_plan …"`) (`hl/.claude/commands/ralph_impl.md`). | `research_codebase` → `create_plan` → `implement_plan` → `validate_plan`. + `create_handoff`/`resume_handoff` | Linear status is the state machine: Triage → … → **Research in Review** → Ready for Plan → **Plan in Review** → Ready for Dev (`hl/.claude/commands/linear.md:36-48`). Each phase also pauses after automated checks until the human confirms manual checks (`implement_plan.md`, `create_plan.md:225-240`) |
| claudelayer | One `launch` tool for every agent: "not multiple - avoid context rot" (`cl/src/index.ts`) | `exhaustive-research` fans out per directory | none |

## 3. Context engineering

| repo | compaction | sub-agents | in vs out of context | artifacts on disk |
|---|---|---|---|---|
| fold | Auto-compaction keeps a 16k token reserve and a 20k recent tail verbatim. The summary format is fixed: Goal · Constraints · Progress · Key Decisions · **Tactics & failed commands** · Next Steps · Critical Context (`fold-core/src/Compaction/CompactionPrompts.ts`, `CompactionEngine.ts`). Post-compaction the agent is told where the archived log is (`CompactionArchiveAccess.ts`) | Depth is a **roster choice**: `bash`/`researcher` cannot delegate, while `general-purpose` can recurse (`Mode/Subagents.ts:1-20`). Models bind by role: `smart` / `fast` / `orchestrator` | Tool output is truncated in context, and the full text goes to `tool-output/<session>/<call>.txt` (`OutputStore.ts`). AGENTS.md/CLAUDE.md are baked once per model epoch and never re-read (`Memory/AgentFiles.ts:14`) | `.humanlayer/tasks/<slug>/` |
| agentlayer | Compaction is a hook, opt-in ("Love it", `docs/content/introduction/motivation.md`) | "Infinite-depth with recursive state". Subagent thinking is throttled to `low` (`codelayer/README.md`) | State is JSON-serializable, so "surgery on the context window mid-run" is possible | — |
| ACE | **Frequent intentional compaction**: keep utilisation at 40–60%, design the whole workflow around it, and compact progress back into the plan file after each phase (`ace-fca.md:214-283`). Priority order of harm: incorrect > missing > noise (`ace-fca.md:155-163`) | Fresh context for search/summarise. The ideal return looks like a compaction | 200 lines of plan are reviewable, 2000 of code are not (`ace-fca.md:357`) | `thoughts/shared/{research,plans}` |
| humanlayer | `create_handoff`: Task(s) · Critical References (2–3) · Recent changes · Learnings · Artifacts · Next Steps (`create_handoff.md`) | 6 **documentarian** agents: locator, analyzer, pattern-finder, thoughts-locator/analyzer, web. ("DO NOT critique", `hl/.claude/agents/*`). The parent reads the named files fully **before** spawning (`research_codebase.md:31-35`) | The main agent does synthesis "not deep file reading" | `thoughts/` is a **separate git repo** symlinked into each code repo (`hlyr/THOUGHTS.md`). (personal/shared/global, hard-linked `searchable/`, pre-commit guard) |

## 4. Packaging, distribution, per-machine config

| repo | rules / skills / personas / commands ship as | per-machine config |
|---|---|---|
| fold | npm CLI. Skills scanned from `~/.claude/skills` and repo roots (`Skills/DiskSkills.ts`). AGENTS.md comes first and CLAUDE.md is the fallback, with `.local.md` overlays and a global chain `~/.fold` → `~/.agents` → `~/.codex` (`AgentFiles.ts:1-16`). `.agents → .claude` symlink. **mattpocock's `codebase-design` and `improve-codebase-architecture` are vendored as copies** (`fold/.claude/skills/`) | `~/.fold/config.jsonc`: providers + **role bindings** (`Config/ConfigSchema.ts`). `.humanlayer/workspace.json`: a per-task worktree template with `copyGlobs` + `setupCommand` |
| agentlayer | npm packages. The RPI agents are code (`src/rpi-agents/*/index.ts`). `.claude → .agents` symlink | `~/.humanlayer/agent-sdk` auth store. `.humanlayer/workspace.json` (same shape) |
| skills | One marketplace, one plugin per skill. `show-me` has an `agents/openai.yaml` for Codex. **`show-me` and `visual-pr` are user-invoke only**: `disable-model-invocation: true` and `allow_implicit_invocation: false` (`hls/show-me/skills/show-me/SKILL.md:4`, `agents/openai.yaml`) | none |
| humanlayer | Commands and agents are committed in the repo's `.claude/`. `_nt`/`_generic` variants | `.claude/settings.json` sets `MAX_THINKING_TOKENS`. `local_review` copies `settings.local.json` into each worktree |

## 5. Hosting and the UI↔agent protocol (for D1)

| repo | host | protocol |
|---|---|---|
| fold | TUI, headless `--prompt`, and **a Durable Object per session** (`fold/examples/alchemy-cloudflare/README.md`). A crash mid-turn resumes through a synthetic "continue" message, at most 3 per turn | HTTP: `POST /sessions/:id/messages` with `whenRunning: queue | steer | interrupt`. Event spine = durable **log rows** + ephemeral **deltas** (`fold-core/src/AgentEvents/AgentEventsService.ts`) |
| agentlayer | Library + CLI. `codelayer` is driven by the closed-source "Riptide daemon" (`codelayer/README.md`) | `AgentRun` is an async iterator. Events include `approvalRequested`; live `resolveApproval()` or cold resume |
| humanlayer (deprecated) | The `hld` daemon wraps `claude --print --output-format stream-json --resume` (`hl/claudecode-go/client.go:188-305`). UIs: `humanlayer-wui` (Tauri+React) and the `hlyr` CLI | JSON-RPC 2.0 over a unix socket plus REST + **SSE `/stream/events`** (`hld/PROTOCOL.md`, `hld/api/openapi.yaml:876`). Approvals: an MCP `request_approval` tool plugged in as Claude's `--permission-prompt-tool` (`hld/mcp/server.go:59`). `launch --dangerously-skip-permissions-timeout` turns bypass off after N minutes |

AG-UI mapping: durable log + deltas ≈ `StateSnapshot` / `TextMessageContent`; approvalRequired + resume ≈ `interrupts` / `resume`.

HumanLayer moved **away from wrapping Claude Code** (hld, deprecated) **to its own agent core** (agentlayer → fold).

## 6. Review and verification

| repo | approach |
|---|---|
| fold | The `implementation-reviewer` subagent compares the plan to `git diff main...HEAD` and sorts findings into four buckets: **as planned · deviations · additions not in plan · planned but not implemented**. Empty sections are written as "None", never dropped, and it does not judge good/bad (`Rpi.ts:437-509`). It is read+bash, `fast` model. |
| agentlayer | `docs-agent`: the diff is **pushed into** the prompt, tools are read-only, the run is capped at `maxSteps(12)`, and the output has fixed sections (Verdict / Recommended Updates / Files). It runs **one upserted PR comment per agent**, keyed by `<!-- name:sha=… -->` (`agents/docs-agent/src/reviewer.ts`, `github.ts:29`). The editor gets a path-scoped approval hook. |
| skills | `visual-pr`: "Why" is exactly one sentence, plus 1–3 special notes, plus a `/show-me`-style change outline (call-tree / file-tree / type diffs). Saved under `.humanlayer/tasks/<slug>/` (`hls/visual-pr/skills/visual-pr/SKILL.md`) |
| ACE | Code review is for **mental alignment** (`ace-fca.md:335-360`). Tests do not catch design rot, which shows up "measured in weeks, months" (`wsff.md:359-370`). Remedy: review the program design before the code |
| humanlayer | `validate_plan`: parallel tasks compare plan vs diff for migrations, code and tests, then run `make check test` (`validate_plan.md`). Plans split **Automated** from **Manual** verification (`create_plan.md:345-371`) |

## Repo × our decisions

C = confirms · X = contradicts · N = new idea

| | G1 rules layers | G2 one crq + labels | G3 review shape | G5 reference anatomy | G6 coordinator + briefed workers | G4 Q1 one unix user | G4 Q4 plugins everywhere | G4 Q3 coordinator = contract | G4 Q3 tiers |
|---|---|---|---|---|---|---|---|---|---|
| fold | C: AGENTS.md first, `.local.md` overlay, `.agents↔.claude` symlink. **X**: upstream skills copied, not plugged | — | C: implementation-reviewer = our Spec axis, read-only, cheap model | — | C + **N**: orchestrator enforced by **missing tools**, not prompt | C: one user; isolation comes from the worktree template | N: role→model binding in a per-machine config | C: same core behind TUI / headless / DO (adapters) | — |
| agentlayer | C: `.claude→.agents` | **N**: one upserted comment per agent per MR, sha-keyed | C: diff pushed in, read-only, step cap, fixed sections | — | C: rlm orchestrator | — | — | C: approval = serialisable pause, any front end resumes | — |
| skills | — | — | N: PR description shape (`visual-pr`) | — | — | — | C: one plugin per skill. **X for Q-6**: show-me cannot auto-load (model invocation disabled) | — | — |
| ACE | — | C: human gates at research and plan = our grill + `/approved` | C: review for alignment. N: review program design before code | N: program-design views (types, call-tree diff, file-tree diff) | **X (caution)**: "subagents are not roles". Our souls must earn their keep as context, not costume | — | — | — | C: "not everything gets a product review" |
| humanlayer | C: commands in-repo. N: `thoughts/` as a separate repo | **C**: status labels drive which command runs. "in review" statuses = human gates | C: validate_plan = Spec axis + make. N: Automated vs Manual criteria | — | **C**: `ralph_impl` = fresh session + worktree + slash-command brief | C: one user launching sessions | — (pre-plugin) | C: daemon + many UIs. N: bypass-permissions **timeout** | — |

## 5 most useful NEW ideas for us

| # | idea | shown in | lands in |
|---|---|---|---|
| 1 | **Spec axis output = four fixed buckets**: as planned · deviations · additions · planned-not-done. Write "None", never omit, and no good/bad verdict (the lead judges) | `fold/packages/fold-agent/src/Mode/Rpi.ts:437-509` | G3 Spec packet template |
| 2 | **Phases carry Automated vs Manual success criteria. The worker pauses after automated checks pass** and the coordinator relays the manual ones | `hl/.claude/commands/create_plan.md:225-240`, `implement_plan.md` | stage-5 design template, stage 6, G6 relay |
| 3 | **Coordinator rules enforced by toolset**: the orchestrator simply has no bash/edit, so "never edits code" cannot break | `fold/packages/fold-agent/src/Mode/Rlm.ts` | coordinator `agents/*.md` `tools:` / `disallowedTools` (G4 Q3) |
| 4 | **One upserted MR comment per (role, head sha)** via a hidden marker, so the record does not spam and stays findable | `agl/agents/docs-agent/src/github.ts:29-33` | G2 handoff record |
| 5 | **Program design before code**: types/signatures, call-stack diff, file-tree diff as the stage-5 design, reviewed by the human | `ace/wsff.md:481-536` (also `hls/visual-pr/.../pr_description_template.md`) | stage-5 design + MR description shape |

Runners-up: compaction keeps **failed commands and why** (`CompactionPrompts.ts`) · per-task worktree template with `copyGlobs` (`fold/.humanlayer/workspace.json`) · bypass-permissions timeout (`ralph_impl.md`).

## Open questions for the operator (not decided)

| # | question | why it comes up |
|---|---|---|
| O1 | **Q-6 talking set**: the show-me plugin is user-invoke only. Should the always-on part (diagram-first, one thing per reply) live in the agent-side CLAUDE.md / SessionStart hook, with the plugin only for `/show-me`? | `hls/show-me/skills/show-me/SKILL.md:4` `disable-model-invocation: true` |
| O2 | Should stage 6 adopt **Automated vs Manual criteria with a pause**? That adds HITL moments the coordinator must relay | idea 2 |
| O3 | MR record: **append a comment per round** (full history) or **upsert one per role per head sha**? | idea 4 vs G3's 3-round audit trail |
| O4 | Coordinator: enforce "never edits code" with `disallowedTools` (it still needs bash for tmux), or stay prompt-only? | idea 3 |
| O5 | D1: HumanLayer **abandoned wrapping Claude Code** (hld, deprecated) for its own core. Does that change "Agent SDK container per role", or is the Agent SDK close enough to "own core"? | §5 |
| O6 | Does a `thoughts/`-style **separate notes repo** (research/plans outside the code repo) replace `.scratch/` and MR-carried specs, or stay out of scope? | `hl/hlyr/THOUGHTS.md` |
| O7 | fold vendors mattpocock skills **as copies**. Does that weaken Q-5 "never copies", or is it simply fold not having our #587 problem? | `fold/.claude/skills/codebase-design/` |
