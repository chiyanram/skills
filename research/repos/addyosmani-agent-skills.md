# addyosmani/agent-skills — deep report (2026-10-01)

Clone: `refs/addyosmani-agent-skills` @ `2686b62` (2026-09-25, "bump plugin manifests to 0.6.11"; shallow, 1 commit).
All paths below are relative to that clone.

## 1. What it is

| | |
|---|---|
| What | 25 markdown **skills** + 4 **personas** + 9 **slash commands** + 7 shared **reference checklists**, packaged as one plugin for Claude Code, Codex, Gemini, Antigravity, Copilot CLI (`README.md:350-364`) |
| Maturity | v0.6.11 across 5 manifests, version-locked by CI (`scripts/validate-versions.js:7-31`); 5 CI jobs, 3-OS matrix (`.github/workflows/test-plugin-install.yml`); in-repo eval framework (`evals/README.md`) |
| Stars | not in the repo; Trendshift-badged (`README.md:7`). Comparison doc refuses star counts (`docs/comparison.md:30`) |
| The one idea | **Skills are processes, not prose** — every skill = steps + exit evidence + an anti-rationalization table (`docs/skill-anatomy.md:150-155`, `README.md:340-345`). Second idea: **the user or a slash command is the orchestrator; personas never call personas** (`references/orchestration-patterns.md:5`) |

## 2. File tree (what matters)

```
AGENTS.md                      repo-scoped only; OpenCode intent→skill map + "personas/skills/commands" layer rule (:70-84)
CLAUDE.md                      repo-scoped only; 60 lines; phases list, conventions, Boundaries (:54-60)
.claude/rules/skills-contributing.md   the ONE path-scoped rule (paths: skills/**) — points at CONTRIBUTING, restates nothing
.claude/commands/*.md (9)      /spec /plan /build /test /review /code-simplify /ship /constraints /webperf — thin "Invoke skill X" + steps
.gemini/commands/*.toml (9)    same commands, Gemini syntax
commands/*.toml (9)            same commands, Antigravity syntax
.claude-plugin/{plugin,marketplace}.json   Claude plugin: commands + skills + experimental evals
.codex-plugin/plugin.json · .agents/plugins/marketplace.json · plugin.json   Codex / Antigravity / Copilot manifests
skills/<name>/SKILL.md (25)    the product; 178–496 lines each
  constraint-driven-development/references/floor-guard.md   diff-scoped "bar got lowered" detector (Node)
  security-and-hardening/references/hardening-patterns.md    skill-local reference
agents/*.md (4)                code-reviewer · security-auditor · test-engineer · web-performance-auditor
references/*.md (7)            shared checklists: definition-of-done, orchestration-patterns, security, perf, a11y, obs, testing
hooks/                         session-start.sh (NOT wired), sdd-cache-{pre,post}.sh, simplify-ignore.sh + tests
scripts/                       validate-skills, skill-lint (single source of lint rules), validate-commands (parity),
                               validate-artifact-paths, validate-reference-links, validate-versions, run-evals
evals/                         cases/<skill>.json (25) · fixtures/ · plugin/ (claude plugin eval cases) · skill-impact.md (rejection ledger)
docs/                          agents.md, skill-anatomy.md, getting-started, adoption-guide, advanced-per-agent-configuration,
                               comparison, developer-onboarding, 10 per-harness setup guides
```

## 3. Approach, section by section

### a. Rules / standards

| Question | Answer | Evidence |
|---|---|---|
| Where do rules live? | Not in an always-on file. Each concern is a **skill** (process) or a **shared reference** (checklist). Repo `CLAUDE.md`/`AGENTS.md` configure only contributors to this repo | `CLAUDE.md:5`, `AGENTS.md:5`, `docs/getting-started.md:56-58` |
| Single source? | Stated as a rule four times: "Never duplicate content between skills — reference" | `CLAUDE.md:60`, `docs/skill-anatomy.md:188`, `CONTRIBUTING.md:59`, `.claude/rules/skills-contributing.md:13` |
| Shared vs local | Material used by >1 skill → repo-root `references/`; used by one skill → inside the skill dir. Reason: copies drift, "single repo-root copy stays the source of truth" | `docs/skill-anatomy.md:117-125` |
| Pointer files | `.claude/rules/skills-contributing.md` and `AGENTS.md:88-92` point at CONTRIBUTING/skill-anatomy and say "do not restate" | `.claude/rules/skills-contributing.md:15`, `AGENTS.md:92` |
| Always vs on demand | Only name+description load at start; SKILL.md loads on activation; <500 lines, supporting files one level deep | `docs/skill-anatomy.md:127-135` |
| Two-router rule | The meta-skill `using-agent-skills` must NOT be preloaded on hosts with native skill routing (Claude Code, Codex) — "two routers for the same task". The SessionStart hook that would inject it is deliberately unwired | `hooks/session-start.sh:5-8`, `docs/getting-started.md:45-47`, `docs/codex-setup.md:27`, `CONTRIBUTING.md:85` |
| Project quality bar | A separate artifact, `CONSTRAINTS.md`, owned by the project: Floor · Enforced (with command per row) · Measured (ratchet) · Exceptions (owner + expiry) | `skills/constraint-driven-development/SKILL.md:93-140` |
| Cursor split | "1–2 thin `alwaysApply` rules + skills on demand"; never copy SKILL.md bodies into rules | `docs/cursor-setup.md:23-31,174-184` |

**Where single-source fails here (the lesson):** the review severity taxonomy exists in three different versions:

```
skills/code-review-and-quality/SKILL.md:181-187   (no prefix)=Required · Critical · Nit · Optional/Consider · FYI
agents/code-reviewer.md:49-57                     Critical · Required · Optional · Nit
.claude/commands/review.md:15  (+ .gemini, commands/)   Critical · Important · Suggestion   <-- drifted
```

`validate-commands.js:15-17` checks command *descriptions* across the 3 dirs but explicitly not bodies — so the drift is invisible to CI. 9 commands × 3 harness copies = 27 hand-maintained bodies.

### b. Process / workflow

```
DEFINE        PLAN          BUILD                      VERIFY          REVIEW         SHIP
/spec    →    /plan    →    /build | /build auto  →   /test     →    /review   →   /ship
SPEC.md       tasks/plan.md  one task / all tasks       TDD             code-reviewer  3-persona fan-out
              tasks/todo.md  (one commit per task)                                     → GO/NO-GO + rollback
human gate    human gate     human gate per task, or ONE gate for /build auto
```

| Element | What | Evidence |
|---|---|---|
| Gates | Spec → Plan → Tasks → Implement, human review at each | `skills/spec-driven-development/SKILL.md:22-32` |
| Approval strictness | `/build auto`: hedged replies ("looks reasonable") are NOT approval | `.claude/commands/build.md:34` |
| Stop conditions | auto mode stops on unpassable test, ambiguous spec, or anything not undoable by `git revert` | `.claude/commands/build.md:36-41` |
| State on disk | `SPEC.md` / `tasks/plan.md` / `tasks/todo.md` — a CI validator pins these paths so producer and consumer commands cannot drift (PR #93 broke it once) | `scripts/validate-artifact-paths.js:5-38` |
| External tracker | If AGENTS.md/CLAUDE.md names a tracker, one tracker item per task; plan.md keeps an ordered index of IDs | `skills/planning-and-task-breakdown/SKILL.md:157-164` |
| Never overwrite | unchecked tasks for different work → stop and ask | `skills/planning-and-task-breakdown/SKILL.md:150-155` |
| Handoff | files, not chat: "Don't assume approvals you can't see in the artifacts" | `docs/getting-started.md:179-188`, `skills/context-engineering/SKILL.md:123-137` |
| Routing | intent → skill table; lifecycle by phase | `skills/using-agent-skills/SKILL.md:16-43`, `AGENTS.md:22-45` |
| Who orchestrates | the **user** runs the sequence; an LLM lifecycle orchestrator is anti-pattern C | `references/orchestration-patterns.md:78-92,316-326` |
| DoD vs AC | standing Definition of Done (same every change) vs per-task acceptance criteria | `references/definition-of-done.md:5-15` |

### c. Roles / personas

| Question | Answer | Evidence |
|---|---|---|
| Made of | One markdown file: frontmatter (`name`, `description`), "You are…" line, review framework, severity table, **output template**, Rules, **Composition** block | `agents/code-reviewer.md:1-102` |
| Rules for personas | one role, one output format; may invoke skills; never another persona; must end with Composition | `docs/agents.md:99-104` |
| Three layers | Skill = *how* · Persona = *who* · Command = *when* | `docs/agents.md:14-20`, `AGENTS.md:72-78` |
| Who writes / can change | Repo maintainers; users override by putting a same-name file in `.claude/agents/` or `~/.claude/agents/` (plugin agents rank lowest) | `.claude/commands/ship.md:26` |
| Runtime controls | NOT in the portable files — `model`, `tools`, `max_turns` go in per-harness adapter files | `docs/advanced-per-agent-configuration.md:7-22` |
| Platform limits noted | plugin agents ignore `hooks`, `mcpServers`, `permissionMode` | `references/orchestration-patterns.md:162-166` |
| Router persona | explicitly banned ("pure routing layer… 2× token cost") | `docs/agents.md:79-97` |
| Identity / soul | none — personas are reviewers, not long-lived workers; no memory, no lesson loop | (absence; `docs/comparison.md:111` admits cross-session memory is unsolved) |

### d. Review & verification

| Aspect | `/review` (code-review-and-quality) | `/ship` | doubt-driven-development |
|---|---|---|---|
| Shape | single reviewer, 5 axes | 3 personas in parallel → main-agent merge | fresh-context adversarial reviewer per decision, in flight |
| Input | "current changes" (staged / recent commits) | same diff to all three | ARTIFACT + CONTRACT only — **not the claim, not your reasoning** |
| Criteria selection | all 5 axes every time; no by-path selection | fixed per persona | the contract |
| Output | severity-labelled findings, file:line, verdict, "what's done well" | GO/NO-GO, blockers, rollback plan | issues only ("Do NOT validate. Do NOT summarize") |
| Caps | lead with leverage; "one structural problem and ten nits → the structural problem *is* the review" | skip fan-out if ≤2 files, <50 lines, no auth/payments/config | **3 cycles max**, then escalate; too big → decompose, never lift the bound |
| Reconcile | — | merge in main context | classify each finding: contract-misread → actionable → trade-off → noise |
| Evidence | `skills/code-review-and-quality/SKILL.md:22-87,177-192` | `.claude/commands/ship.md:9-72` | `skills/doubt-driven-development/SKILL.md:75-191` |

Mechanical review layer: `floor-guard` reads the diff from merge-base (incl. untracked files) and flags 5 "cheap road to green" moves — threshold loosened, test skipped/deleted/assertion removed, new suppression, stub/empty catch, new exception row. Exit 0/1/2; "Never let a 2 read as a 0" (`skills/constraint-driven-development/references/floor-guard.md:7-13`, `SKILL.md:202-224`). Rank of checks by circularity: external > project > own suite (`SKILL.md:218-224`).

Cost control: placement by cost — edit loop <5s, task end <90s, review minutes, CI rest; "Scope to the diff" (`skills/constraint-driven-development/SKILL.md:186-200`).

### e. Context engineering

| Technique | Evidence |
|---|---|
| 5-level hierarchy: rules → spec → source → errors → history | `skills/context-engineering/SKILL.md:20-36` |
| Selective include brief: TASK · RELEVANT FILES · PATTERN TO FOLLOW (file:line) · CONSTRAINT | `skills/context-engineering/SKILL.md:155-172` |
| Budget: trim at 75%; cut failed attempts first; protect task def + live error; task-critical content LAST | `skills/context-engineering/SKILL.md:198-239` |
| Restartable boundary = completed task, with 5 persisted items | `skills/context-engineering/SKILL.md:123-137` |
| Fresh session per phase; artifacts are the handoff | `docs/getting-started.md:179-200` |
| Research isolation → built-in `Explore`, not a custom persona | `references/orchestration-patterns.md:96-113` |
| Untrusted inputs: fetched docs, error output, browser content, config files are data | `skills/source-driven-development/SKILL.md:97-115`, `skills/debugging-and-error-recovery/SKILL.md:272-280`, `skills/context-engineering/SKILL.md:98-103` |
| Model-neutral rule: a step justified only by naming a model belongs in an issue, not a skill | `docs/skill-anatomy.md:158-169` |

### f. Packaging & distribution

```
one skills/ tree ──┬─ .claude-plugin/  (Claude: commands + skills + agents auto-discovered)
                   ├─ .codex-plugin/   (Codex reads skills/ directly — "no files are copied")
                   ├─ plugin.json      (Antigravity, Copilot CLI)
                   ├─ npx skills add   (per-skill install; loses references/ — issue #361)
                   └─ copy into .cursor/skills, .opencode/skills, .kiro/skills
commands: 3 hand-written copies (.claude/commands .md · .gemini/commands .toml · commands/ .toml)
```

- One version, five manifests, CI-locked (`scripts/validate-versions.js`).
- CI installs the plugin for real: `claude plugin validate .` then `claude plugin marketplace add ./` + `claude plugin install` (`.github/workflows/test-plugin-install.yml:133-166`).
- Per-machine config: user-level agents override plugin ones (`.claude/commands/ship.md:26`); hooks are opt-in snippets for `.claude/settings(.local).json` (`hooks/SDD-CACHE.md:13-47`).
- Known portability gap: shared `references/` vanish under per-skill install (`docs/skill-anatomy.md:123`, `docs/getting-started.md:163-169`).

### g. Hosting / UI

None. No daemon, no protocol, no approvals UI. Human gates are chat turns. Closest thing: Agent Teams worked example (`references/orchestration-patterns.md:174-278`) and "Ralph loop" restarts as harness behaviour, not skill behaviour (`docs/getting-started.md:190-194`).

### Evals (unique to this repo)

| Tier | Checks | Runs | Evidence |
|---|---|---|---|
| 1 Structural | frontmatter, naming, required sections, command parity | CI | `scripts/lib/skill-lint.js:10-24` |
| 2 Trigger/routing | TF-IDF over descriptions: positives rank top-k, negatives lose to named `owner`, collision ≥75% errors; CI floor `--min-rank1 95` | CI | `evals/README.md:16-22,99` |
| 3 Behavioural | headless `claude -p` in a throwaway git repo, LLM grader vs `expectations[]` | on demand | `evals/README.md:36-38` |
| Plugin eval | `claude plugin eval`, with/without plugin, `Δ` column | on demand | `evals/README.md:40-53` |

Measured finding: skill invocation is **stochastic** — review skill fired 5/7; one clause ("even when the diff is pasted inline") moved 7/27 → 21/27 fires (`evals/README.md:53`). Rejected changes go to an append-only ledger (`evals/skill-impact.md`).

## 4. Three excerpts worth studying

1. **`skills/doubt-driven-development/SKILL.md:75-110` + `:168-191`** — the reviewer brief. Pass ARTIFACT + CONTRACT, never the CLAIM ("biases it toward agreement"); adversarial prompt overrides persona's balanced default; reconcile with a precedence order; hard 3-cycle stop; "too big → decompose, do not lift the bound". This is the cleanest written form of our G3 qa brief + round cap.
2. **`skills/constraint-driven-development/SKILL.md:202-224` + `references/floor-guard.md:7-13`** — guard the bar itself. Five cheap-road-to-green moves, checkable with `git diff` alone; "tightening silent, loosening loud"; exit 2 never reads as 0; checks ranked by whether the agent can pass them with broken code. Directly portable to our `make verify` / Checkstyle / coverage floors.
3. **`references/orchestration-patterns.md:282-339` + `docs/agents.md:99-104`** — anti-patterns A–D (router persona, persona→persona, paraphrasing sequential orchestrator, deep trees) each with "why it fails" and "do instead". Best test to hold our coordinator design against.

Runner-up: `skills/context-engineering/SKILL.md:123-137` (restartable session boundary, 5 persisted items, "do not infer approval from a previous conversation").

## 5. Against our decisions

| Decision | Verdict | Evidence / note |
|---|---|---|
| G1 rules layers (AGENTS.md index, bodies on demand, upstream as plugins) | **Confirms** | on-demand skills, <500 lines, one-level refs (`docs/skill-anatomy.md:127-135`); pointer rule file restates nothing (`.claude/rules/skills-contributing.md:15`); one tree, many manifests (`docs/codex-setup.md:3`) |
| G1 — "a stage orders the skill" (Q-4) | **Confirms, with data** | stochastic firing 5/7, descriptions are the lever (`evals/README.md:53`); commands are "Invoke the X skill" one-liners (`.claude/commands/*.md:5`) |
| G1 — always-on talking set (Q-6) | **New caution** | they refuse to preload a router as always-on (`hooks/session-start.sh:5-8`). Fine for reply-shape rules; do NOT also preload a skill router |
| G2 one crq + role labels | **Partly contradicts** | process lives in commands the *user* sequences; no roles own stages; personas are reviewers only (`docs/agents.md:14-22`). Supports "roles say only who" |
| G3 Standards ‖ Spec, fresh, inputs pushed, 3-round cap | **Confirms shape, contradicts criteria selection** | fresh context + artifact+contract + 3 cycles + lead-with-leverage all match (`doubt-driven:75-191`, `code-review:191`). But criteria = all 5 axes every time, no by-path selection; they DO keep "What's done well" (we drop it) |
| G5 5-section references | **Confirms the closing-checks idea; new idea on format** | every skill ends Rationalizations · Red Flags · Verification (`docs/skill-anatomy.md:66-79`). Add a **Common Rationalizations** section — absent from our G5 shape |
| G6 coordinator + briefed workers | **Contradicts in letter, not spirit** | anti-pattern C bans an agent that runs /spec→/plan→/build on the user's behalf (`orchestration-patterns.md:316-326`) for 3 reasons: lost checkpoints, paraphrase drift, 2× tokens. Our G6 answers each: human `/approved` stays, briefs are files not paraphrase, workers are fresh. Must keep those answers explicit in the REQ |
| G6 — qa fresh per round | **Confirms** | "re-spawning fresh-context on an unchanged artifact" is a red flag; fresh only when artifact changed (`doubt-driven:214`) |
| G4 plugins everywhere | **Confirms** | one marketplace, CI install test (`test-plugin-install.yml:146-166`); user-level agent beats plugin agent = per-machine override (`ship.md:26`) |
| G4 coordinator-as-contract / tiers | **New idea** | runtime controls (model, tools, turns) in per-harness adapter files, portable files spec-only (`docs/advanced-per-agent-configuration.md:16-22`) → coordinator contract stays harness-free, adapters carry the knobs |

## 6. Adopt / adapt / reject (ranked)

| # | Call | What | File |
|---|---|---|---|
| 1 | **ADOPT** | qa/worker brief = ARTIFACT + CONTRACT, never the author's claim or reasoning; reconcile precedence; 3-cycle stop, "too big → decompose" | `skills/doubt-driven-development/SKILL.md:75-191` |
| 2 | **ADOPT** | floor-guard for our bar: diff-scoped check for weakened Checkstyle/JaCoCo floors, `@Ignore`/`@PendingFeature`, removed assertions, `// nosemgrep`, new suppressions. Exit 2 ≠ 0 | `skills/constraint-driven-development/references/floor-guard.md` |
| 3 | **ADOPT** | a CI-style parity check for every place a rule is copied (they built `validate-commands`, `validate-artifact-paths`, `validate-reference-links` after real drift) — and learn from their gap: check bodies, not just descriptions | `scripts/validate-commands.js:15-17`, `scripts/validate-artifact-paths.js:5-17` |
| 4 | **ADOPT** | "Common Rationalizations" table in each G5 reference (excuse → reality); cheap, targets the agent's actual failure | `docs/skill-anatomy.md:95-99` |
| 5 | **ADAPT** | trigger evals: positive/negative prompts per skill with `owner`; our version = "does stage N's order fire the skill" rather than description TF-IDF | `evals/README.md:55-97` |
| 6 | **ADAPT** | restartable boundary checklist (5 items) as the worker hand-back format; "no approval unless the artifact records it" | `skills/context-engineering/SKILL.md:123-137` |
| 7 | **ADAPT** | "hedged reply is not approval" + stop list (anything not `git revert`-able) for fleet workers | `.claude/commands/build.md:34-41` |
| 8 | **ADAPT** | per-harness adapter files for model/tools/turns; portable role files stay spec-only | `docs/advanced-per-agent-configuration.md` |
| 9 | **ADAPT** | rejected-change ledger for rule/reference edits that failed a P1-style re-run | `evals/skill-impact.md` |
| 10 | **REJECT** | 5-axis review over every diff with all criteria — the cost we measured in R4; keep by-path selection | `skills/code-review-and-quality/SKILL.md:22-87` |
| 11 | **REJECT** | hand-maintained command copies per harness (27 bodies, already drifted); one source + generated adapters | `.claude/commands/review.md:15` vs skill `:181-187` |
| 12 | **REJECT** | "What's Done Well — always include at least one" in the reviewer output; findings only | `agents/code-reviewer.md:80-81` |
| 13 | **REJECT** | user-as-only-orchestrator for the fleet; valid for laptop, not for G6 | `references/orchestration-patterns.md:78-92` |

## 7. Files actually read

Full read:
`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.claude/rules/skills-contributing.md`,
`.claude/commands/{build,code-simplify,constraints,plan,review,ship,spec,test,webperf}.md`,
`.gemini/commands/review.toml`, `commands/review.toml`,
`plugin.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`,
`agents/{code-reviewer,security-auditor,test-engineer,web-performance-auditor}.md`,
`docs/agents.md`, `docs/skill-anatomy.md`, `docs/getting-started.md`, `docs/advanced-per-agent-configuration.md`, `docs/codex-setup.md`, `docs/adoption-guide.md`, `docs/comparison.md`, `docs/developer-onboarding.md`,
`skills/{using-agent-skills,code-review-and-quality,context-engineering,doubt-driven-development,spec-driven-development,planning-and-task-breakdown,incremental-implementation,constraint-driven-development,test-driven-development,source-driven-development,interview-me,code-simplification,debugging-and-error-recovery,documentation-and-adrs,git-workflow-and-versioning,shipping-and-launch}/SKILL.md`,
`skills/constraint-driven-development/references/floor-guard.md`,
`references/definition-of-done.md`, `references/orchestration-patterns.md`,
`hooks/session-start.sh`, `hooks/SDD-CACHE.md`,
`.github/workflows/test-plugin-install.yml`, `scripts/validate-skills.js`, `scripts/validate-versions.js`,
`evals/README.md`, `evals/skill-impact.md`, `evals/cases/code-review-and-quality.json`,
`evals/plugin/code-review-fires/{prompt.md,graders/*.md}`, `evals/plugin/code-review-stays-quiet/prompt.md`.

Partial (header/heading map + named line ranges):
`README.md` (1-44, 88-215, 319-380 + heading index), `hooks/SIMPLIFY-IGNORE.md` (1-60), `scripts/lib/skill-lint.js` (1-80 + function index), `scripts/validate-commands.js` (1-60), `scripts/validate-artifact-paths.js` (1-40), `scripts/validate-reference-links.js` (1-40), `docs/cursor-setup.md` (grep: rules/mdc/alwaysApply), `docs/opencode-setup.md` (grep: AGENTS.md),
`skills/security-and-hardening/SKILL.md` (1-75 + headings), `skills/ci-cd-and-automation/SKILL.md` (164-192, 298-308 + headings), `skills/idea-refine/SKILL.md` (1-60 + headings), `skills/idea-refine/scripts/idea-refine.sh`,
headings + frontmatter only: `skills/{api-and-interface-design,browser-testing-with-devtools,deprecation-and-migration,frontend-ui-engineering,observability-and-instrumentation,performance-optimization}/SKILL.md`, `references/{accessibility,observability,performance,security}-checklist.md`, `references/testing-patterns.md`.

Not read: `evals/fixtures/**`, remaining `evals/cases/*.json`, `hooks/*.sh` other than session-start, `scripts/*-test.js`, `scripts/run-evals.js`, `skills/idea-refine/{examples,frameworks,refinement-criteria}.md`, `skills/security-and-hardening/references/hardening-patterns.md`, the remaining 8 per-harness setup guides, remaining `.gemini`/`commands` TOMLs (parity is CI-checked), `.github/ISSUE_TEMPLATE/skill-gap.yml`.
