# R5 · humanlayer, Claude Code docs, AG-UI

Answers `issues/10`. Read 2026-10-01. `12f/` = `refs/humanlayer-12-factor-agents/`, `hls/` = `refs/humanlayer-skills/`,
`cc:` = `https://code.claude.com/docs/en/`. pstack / firstmate / mattpocock / addy are in `03-how-others-do-it.md` and are only cross-referenced here.

## Comparison

| | humanlayer 12-factor | humanlayer/skills | Claude Code docs |
|---|---|---|---|
| **(a) One source** | Prompts and context are owned code that you write yourself, not framework defaults (`12f/content/factor-02-own-your-prompts.md`, `factor-03-…`). Repo `12f/CLAUDE.md` is a promptx template: "MANDATORY PERSONA SELECTION" with 5 personas in `.promptx/personas/` | `design-control-loop` and `build-iterated-agentic-loop` both say "Keep one source of truth for each rule; do not repeat" it across skill, prompt and memory (`hls/plugins/design-control-loop/skills/design-control-loop/SKILL.md:87`). `improve-claude-md`: keep it inline in `<important if>` blocks and do **not** shard into files "unless … incredibly verbose" (`hls/plugins/improve-claude-md/…/SKILL.md`) | CLAUDE.md is "context, not enforced configuration". Target "under 200 lines". `@imports` "don't reduce its context cost". `AGENTS.md` is now read natively (v2.1.277+), or brought in by `@AGENTS.md`. `~/.claude/rules/` is user-level and loads for every project (`cc:memory`) |
| **(b) Roles / flow / HITL** | F8: break the loop at a high-stakes call and wait for approval. F7: a human is reached by a tool call (`request_human_input`). F10: agents of "3-10, maybe 20 steps max". F9: after about 3 errors, escalate to a human | Control loop = sensor → controller → actuator, and the human stays "*on* the loop" through a memory file plus `/iterate` on the PR. WIP is bounded to **1 open PR per loop** (`design-control-loop/SKILL.md:123-142`). No personas and no agents/ in any plugin | Subagents **cannot** ask the user (`AskUserQuestion` stripped). They nest up to 3 levels. `omitClaudeMd: true` gives a clean reviewer. A plugin agent ignores `hooks` / `mcpServers` / `permissionMode` (`cc:sub-agents`). `--permission-prompts none` is the setting for unattended runs (`cc:headless`) |
| **(c) Context budget** | F3: "Everything is context engineering", and hide resolved errors. F10: "As context grows, LLMs are more likely to get lost". App.13: a call you know you will need, run it deterministically and pre-fetch the result | `improve-claude-md`: "Less is more". Cut anything a linter or hook enforces, cut snippets, and leave the 90%-relevant material bare | Startup sample: system prompt 4.2k, project CLAUDE.md 1.8k, skill index 450. The **skill index is not re-injected after `/compact`**, while CLAUDE.md is (`cc:context-window`). MEMORY.md is capped at 200 lines / 25KB. `disable-model-invocation` costs zero until invoked |
| **(d) Distribution** | n/a. It is a guide plus a `create-12-factor-agent` template (`12f/packages/`) | One marketplace (`hls/.claude-plugin/marketplace.json`) with 6 single-skill plugins. Shared references are **copied** into each plugin (4 of 7 reference files byte-identical between the two loop plugins), because a plugin cannot reach outside its own dir. The README installs with `npx skills add` instead | Settings precedence is managed > CLI > local > project > user (`cc:settings`). Fleet rollout is `extraKnownMarketplaces` + `enabledPlugins` in managed settings. Containers use `CLAUDE_CODE_PLUGIN_SEED_DIR`. A managed CLAUDE.md lives at `/etc/claude-code/CLAUDE.md` or in the `claudeMd` key (`cc:plugins/org`, `cc:memory`) |

## (d) in detail: one setup on the laptop and the SSH VM

| Mechanism | Laptop (interactive, repo checkout) | SSH VM (fleet: `claude --dangerously-skip-permissions` in tmux, `refs/chiyanram-agent-fleet/README.md:29`) | Source |
|---|---|---|---|
| Project `.claude/settings.json` `extraKnownMarketplaces` | Applies after the folder-trust dialog | `-p` and untrusted folders are **silently ignored** unless `hasTrustDialogAccepted` is set in `~/.claude.json` | `cc:plugins/org#require-plugins-per-repository` |
| Relative-path marketplace in the repo | A worktree resolves the path to the **main checkout**, so all worktrees share it | Same | `cc:plugins/org` |
| Managed `extraKnownMarketplaces` + `enabledPlugins` | Installs at the next session start, and the user cannot disable it | Same. The fleet VM already uses `/etc/claude-code/managed-settings.json` for a hook (`refs/chiyanram-agent-fleet/.claude/skills/create-agent/agent-yaml.md:118`) | `cc:plugins/org` |
| Managed CLAUDE.md | `/Library/Application Support/ClaudeCode/CLAUDE.md` | `/etc/claude-code/CLAUDE.md`, which "cannot be excluded" | `cc:memory` |
| Private GitLab marketplace | `git` runs non-interactively and uses stored credentials. Use the full `https://gitlab…/x.git` URL (`owner/repo` means GitHub) | Needs a git credential helper that holds the credential. The fleet already provisions a "GitLab auth + git credential" | `cc:plugins/host-marketplace` |
| Pin or update | `version` bump is required or users stay cached. Omit `version` to track commits. `#ref` on add | Same, or a read-only seed dir | `cc:plugins/host-marketplace` |
| Remote Control | `claude remote-control` drives a local session from a browser or phone | For SSH it says "start it inside `tmux` or `screen`" | `cc:remote-control` |
| `--bare` | — | Skips CLAUDE.md, skills, plugins and hooks. It is "recommended" for `-p` and will become its default, so it **breaks parity** if the fleet ever moves to `-p` | `cc:headless` |

Cross-ref R3 pattern 1 ("one canonical tree + pointers") and pattern 7 ("per-machine setup separate"). The Claude Code docs supply the shipped mechanism for both: **one marketplace repo + managed `enabledPlugins` on each machine.**

## 12 factors → our setup

Meaning of the status column:
- **done**: we already do this.
- **gap**: it applies to us and we don't do it yet.
- **n/a**: it is about product runtime, not the dev workflow.

| # | Factor (`12f/content/factor-NN-*.md`) | Status | Where / what |
|---|---|---|---|
| 1 | NL → tool calls | n/a | Claude Code's job. In the product it is Aruvii `ToolHandlerPort` |
| 2 | Own your prompts | **done**. *gap*: they are not tested | Skills, rubrics and `/crq` are ours, in `.claude/`. No evals on them (R2: 8 skills never fired) |
| 3 | Own your context window | **gap** | R1: CLAUDE.md is 60% of startup. Rules exist in 4–5 copies. The rubric is loaded twice (R4) |
| 4 | Tools = structured outputs | n/a | Product (`ToolInputContract`) |
| 5 | Unify execution + business state | **done** | The `/crq` state lives on the MR/issue thread (`.claude/commands/crq.md:26-31`). Nothing is held in the agent |
| 6 | Launch/pause/resume | **done** | The MR is the checkpoint. `claude --resume <id>` also works (`cc:headless`) |
| 7 | Contact humans with tools | **done** on the fleet, *partial* on the laptop | Fleet: Discord channel + `alert_mention` on blocked. Laptop: chat. Subagents cannot ask the human, which is correct per F10 |
| 8 | Own your control flow | **done**. *gap* in the middle stages | Hard human gates at stage 5 `/approved` and stage 9 merge (`crq.md:233,407`). Stages 6–8 are agent-driven with no deterministic break-out |
| 9 | Compact errors / escalate after ~3 | **gap** | Findings come back in rounds (map: #576 4 rounds, !230 3 rounds). No retry ceiling or escalation rule |
| 10 | Small focused agents | **gap**: this map's target | Reviewers run 16–19 calls with a 90–177k peak (R4). Diff-scoped reviewers (map decision A) are this factor |
| 11 | Trigger from anywhere | **done** on the fleet | Discord channel plugin, tmux. The laptop also has Remote Control |
| 12 | Stateless reducer | n/a | A conceptual restatement of 5 and 6 (42-word file) |
| 13 | Pre-fetch context | **gap**, cheap | Hand reviewers the diff and only the criteria that apply, chosen before spawn. That is map decision A. R3 pattern 5 ("hand over a diff command") agrees |

## humanlayer: what's new versus R3

| Finding | Source | Bearing on the map |
|---|---|---|
| `<important if>` blocks over sharding. Bare = relevant to 90%+ of tasks | `hls/plugins/improve-claude-md/…/SKILL.md` | **Contradicts** the R3 pattern 2 lean (index plus bodies loaded on demand). Our CLAUDE.md already uses `<important if>` and is still 60% of startup (R1), so inline-conditional does not fix size. G1 must choose |
| Duplicating content across plugins is accepted, because a plugin cannot reference files outside its own dir | `hls` reference files, `cmp`. The CC docs allow a symlink *within* the marketplace, which is dereferenced into the cache (`cc:plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks`) | G4: if rules ship as several plugins, shared rubric files go through symlinks, not copies |
| Memory file + `/iterate` = the human tunes future runs, not only the current PR | `design-control-loop/SKILL.md:123-132` | Fleet roles could carry standing reviewer feedback the same way. Nothing like it exists today |
| promptx persona gate in CLAUDE.md, "DO NOT PROCEED WITHOUT SELECTING A PERSONA" | `12f/CLAUDE.md` | Same shape as our `docs/agents/personas/`. It is selected by the prompt, not by contract. R3 pattern 6 prefers contract |
| Headless runner: `claude -p … --permission-mode bypassPermissions --output-format stream-json`, with `--max-turns` / `--max-budget-usd` as spend guards | `hls/…/references/agent-runner-templates.md:17-37` | A cost cap per reviewer run (R4: ~$2–2.8 per review) |

## AG-UI

**What it is (5 lines):**
1. An open, event-based Agent↔User Interaction protocol from CopilotKit, built with LangChain and CrewAI (`https://docs.ag-ui.com/introduction`).
2. It runs over HTTP / WebSockets and streams over SSE.
3. Its events cover run lifecycle, text deltas, tool calls, state snapshot and JSON-Patch delta, reasoning, and subagent events (`https://docs.ag-ui.com/concepts/events`).
4. HITL works like this: `RunFinished` can carry `interrupts`, and the client resumes with a new run that carries `resume`.
5. It is positioned as the user layer next to MCP (tools) and A2A (agent↔agent). SDKs include Java and Kotlin. There is no Angular client, only React and CopilotKit.

**Verdict: Aruvii product only. Not relevant to this map.**

| Reason | Evidence |
|---|---|
| This map is about how Claude Code loads rules and roles. AG-UI has no concept of rules, skills, settings or distribution | `map.md` §Destination |
| Our human surfaces are a GitLab MR thread, Discord and the terminal. None of them speaks AG-UI, and Claude Code exposes `stream-json`, not AG-UI | `cc:headless` |
| It fits the product: Aruvii already streams chat over SSE (`aruvii-api/src/main/java/ai/aruvii/api/chat/ChatResponseSubscriber.java`, `ChatStreamingIT.java`), and the interrupt/resume pair matches tool approval | — |
| Recommendation: file it as a product-side spike (event schema for `/api/chat` streaming), outside `one-rulebook` | — |
