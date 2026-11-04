# ECC (everything-claude-code) + Anthropic claude-code plugins — per-repo deep report (2026-10-01)

Path prefixes below: `ECC/` = `…/scratchpad/r9/affaan-m_everything-claude-code/`, `ACC/` = `…/scratchpad/r9/anthropics_claude-code/`.
Full absolute paths are in §7 of each part.

---

# Part 1 — affaan-m/everything-claude-code (ECC)

## 1. What it is

| | |
|---|---|
| What | A "harness-native agent operating system": one repo shipping agents, skills, commands, rules, hooks, MCP configs, installers for ~15 harnesses (`ECC/package.json:4`) |
| Maturity | v2.2.2 (`ECC/VERSION`); CI validators per artifact type (`ECC/scripts/ci/validate-{agents,rules,skills,hooks,install-manifests}.js`); Rust control plane `ecc2/` is "alpha" (`ECC/ecc2/README.md:1-5`) |
| Size | 68 agents · 293 skills · 94 commands (`ECC/AGENTS.md:3`) · 122 rule files across 22 language dirs |
| Stars | not in repo (badge only, `ECC/README.md:46`); R9 classed it >10k★ |
| One idea | **Catalogue breadth + specialist routing**: a rule/agent/skill per language × concern, selected by file path (rules) or by trigger table (agents). Not a single pipeline. |

## 2. File tree (what matters)

```
ECC/
├── AGENTS.md            index + DUPLICATED core rules (coding style, testing, security, git) — 221 lines
├── CLAUDE.md            repo-dev guidance + "Prompt Defense Baseline" + file→skill table
├── SOUL.md              17-line identity: 5 principles, "agent-first"
├── rules/
│   ├── README.md        layering contract: common/ + <lang>/ extends, precedence, install
│   ├── common/*.md      10 files, NO paths: → always loaded once installed
│   └── <lang>/*.md      5 files each (coding-style·testing·patterns·hooks·security), paths: glob
├── agents/*.md          68 subagents, frontmatter name/description/tools/model
├── commands/*.md        94 "legacy shims"; skills/ is canonical (AGENTS.md:174-178)
├── skills/<name>/SKILL.md  293; orch-pipeline + 5 orch-* wrappers; gateguard; continuous-learning-v2; santa-method …
├── workflows/orch-review.workflow.js   native Workflow-tool review: fan-out → dedup → adversarial verify
├── hooks/hooks.json + hooks.metadata.json (sidecar ids) + README  — profiles minimal|standard|strict
├── manifests/install-{profiles,modules,components}.json  — module → paths → 15 harness targets
├── .claude-plugin/plugin.json  ships skills+commands only; rules need the installer
├── .cursor/rules · .agents/skills · .codex · .kiro · .opencode · pi/ …  per-harness mirrors (see 3f)
├── scripts/lib/tmux-worktree-orchestrator.js   worker = tmux pane + worktree + task.md/handoff.md/status.md
└── ecc2/                Rust TUI/daemon, SQLite session store
```

## 3. Approach

### a. Rules / standards

| Aspect | Evidence |
|---|---|
| Two layers: `common/` (language-agnostic, "always install") + `<lang>/` that **extends** it | `ECC/rules/README.md:5-33` |
| Each lang file opens with an "extends" pointer to its common counterpart — the single-source mechanism | `ECC/rules/README.md:120-123`; `ECC/rules/java/testing.md:7` |
| Precedence: language-specific overrides common ("CSS specificity") | `ECC/rules/README.md:128-139` |
| On-demand loading = Claude Code `paths:` frontmatter on every lang file; `common/` has none, so it is always-on | `ECC/rules/java/testing.md:1-4`, `ECC/rules/java/hooks.md:1-7` (adds pom/gradle); common files have no frontmatter (scan of `rules/common/*.md`) |
| Rules = *what*, skills = *how*; lang rules link to skills | `ECC/rules/README.md:102-107` |
| Same rule text restated in the always-on index | `ECC/AGENTS.md:130-160` repeats coding-style/testing/80% coverage from `rules/common/` — **single-source is broken at the index** |
| Same 6-line "Prompt Defense Baseline" pasted into every agent + CLAUDE.md | `ECC/CLAUDE.md:9-16`, `ECC/agents/code-reviewer.md:8-15`; present in all 68 agent files |
| Java rules are generic (JUnit 5 + AssertJ + Mockito), not project rules | `ECC/rules/java/testing.md:11-14` |

### b. Process / workflow

`orch-*` family: thin operation skills over one shared engine (`ECC/skills/orch-pipeline/SKILL.md:10-12`).

```
orch-add-feature │ orch-change-feature │ orch-fix-defect │ orch-refine-code │ orch-build-mvp
                 └──────────── each sets: size floor · phase mask · first move ────────────┘
                                         ▼
 0 Intake → 1 Research&Reuse → 2 Plan ──GATE 1── → (3 Scaffold) → 4 TDD → 5 Review → 6 Commit ──GATE 2──
```

| Element | Evidence |
|---|---|
| Routing by operation type (feature/tweak/fix/refactor/mvp) | `ECC/skills/orch-pipeline/SKILL.md:25-31` |
| **Size classifier** picks which phases run (trivial→large), highest signal wins, user can override | `ECC/skills/orch-pipeline/SKILL.md:39-54` |
| Operation's "first move" (fix = failing regression test first) | `ECC/skills/orch-fix-defect/SKILL.md:20-27` |
| Exactly two human gates; "everything between flows" | `ECC/skills/orch-pipeline/SKILL.md:76-85` |
| Handoff = planning docs on disk, "no hidden state" | `ECC/skills/orch-pipeline/SKILL.md:106-113` |
| Self-check list at end of the engine | `ECC/skills/orch-pipeline/SKILL.md:115-121` |
| Generic always-on workflow (Research → Plan → TDD → Review → Commit) | `ECC/rules/common/development-workflow.md:9-44` |

### c. Roles / agents

| Aspect | Evidence |
|---|---|
| Agent = markdown + frontmatter `name, description, tools, model` | `ECC/agents/code-reviewer.md:1-6` |
| Roles are *specialists by language/concern* (java-reviewer, security-reviewer…), not SDLC roles | `ECC/AGENTS.md:15-86` |
| Invoked "proactively without user prompt" via a trigger table | `ECC/AGENTS.md:88-112`, `ECC/rules/common/agents.md:28-34` |
| Identity file is tiny and product-level, not per-role | `ECC/SOUL.md:3-17` |
| **Delegation Completion Contract** — parent owns collection, never ends turn "waiting" | `ECC/rules/common/agents.md:51-59` |
| Agents run project tooling themselves (java-reviewer runs `./gradlew check`) | `ECC/agents/java-reviewer.md:19-31` |
| Many agents are condensed rewrites of Anthropic's pr-review-toolkit/feature-dev agents (diffs 110–185 lines, not copies) | `ECC/agents/silent-failure-hunter.md` vs `ACC/plugins/pr-review-toolkit/agents/silent-failure-hunter.md` |

### d. Review & verification — three surfaces, deliberately cross-referenced

| Surface | Shape | Evidence |
|---|---|---|
| `/code-review` | single-agent checklist, 7 categories, runs validation commands, writes `.claude/reviews/pr-N-review.md` | `ECC/commands/code-review.md:1-3, 120-127, 138-191` |
| `/review-pr` | 6 specialist agents, dedupe, ≥80 confidence | `ECC/commands/review-pr.md:13-37` |
| `/orch-review` → `workflows/orch-review.workflow.js` | **dimensions chosen by diff** → parallel reviewers → dedup → adversarial verify of each CRITICAL/HIGH | `ECC/commands/orch-review.md:8-11`; workflow below |

orch-review.workflow.js, step by step:

| Step | Evidence |
|---|---|
| Inputs pushed in: `diff` (required), `language`, `changedFiles`; invalid → throw (fail closed) | `:16-23, 152-172` |
| Criteria selection: quality always; language reviewer from a map; security only if regex hits diff+paths | `:34-59, 177-185` |
| Findings schema enforced at tool layer; `proof` **required by JSON-schema `if/then`** for HIGH/CRITICAL | `:61-94` |
| Diff fenced as untrusted input in the prompt | `:119-123` |
| Barrier before dedup, justified in a comment (11 raw → 4 unique, ~half verifier cost) | `:192-198`; `ECC/workflows/README.md:20` |
| Dedup key = file + normalized evidence snippet, strictest severity wins | `:217-237` |
| Verifier: refute only with confidence ≥0.8; uncertainty stays blocking | `:127-144, 258-274` |
| Verdict APPROVE only if every dimension ran and nothing blocks; stats returned | `:278-296` |
| Inconsistency: README says verifier "defaults to *refuted* on uncertainty" — code does the opposite | `ECC/workflows/README.md:18` vs `.js:132, 261` |

Reviewer prompt anti-noise devices (`ECC/agents/code-reviewer.md`):
- >80% confidence, skip unchanged code, consolidate (`:29-37`)
- **Pre-Report Gate**: 4 questions — cite line, failure mode, read context, severity defensible (`:39-53`)
- HIGH/CRITICAL require snippet + scenario + why guards miss (`:55-64`)
- "Zero findings is expected" (`:66-74`); list of 12 common LLM false positives (`:76-111`)
- Severity table + verdict summary (`:259-288`); "do not withhold approval to appear rigorous" (`:297`)

No round cap anywhere in review; santa-method has an iteration cap + human escalation (`ECC/skills/santa-method/SKILL.md:28-60`).

### e. Context engineering

| Device | Evidence |
|---|---|
| Path-scoped rules (on demand) vs common (always) | 3a |
| `contexts/{dev,review,research}.md` mode prompts | `ECC/contexts/review.md` |
| Workers get a generated `task.md`, write `handoff.md` (Summary · Files Changed · Tests · Follow-ups), launcher writes `status.md`; "do not spawn subagents" | `ECC/scripts/lib/tmux-worktree-orchestrator.js:109-160, 182-212` |
| Strategic-compact hook nudges `/compact` every ~50 tool calls; PreCompact saves state | `ECC/hooks/README.md` (PreToolUse/Lifecycle tables) |
| **GateGuard**: first Edit/Write per file is denied until the agent lists importers, affected API, data shape, verbatim user instruction | `ECC/skills/gateguard/SKILL.md:19-33, 49-73` |
| **Instincts** (continuous-learning-v2): hooks log tool use → Haiku observer → atomic YAML instincts with confidence 0.3–0.9, project-scoped by git-remote hash, promoted to global when seen in 2+ projects | `ECC/skills/continuous-learning-v2/SKILL.md:48-79, 83-136` |
| `rules-distill`: promote a principle to a rule only if it appears in 2+ skills | `ECC/skills/rules-distill/SKILL.md:74-80` |

### f. Packaging & distribution

| Aspect | Evidence |
|---|---|
| Claude plugin ships `skills/` + `commands/` + userConfig (hooks on/off, profile) — **not rules** | `ECC/.claude-plugin/plugin.json:25-45` |
| Rules need the Node installer (`install.sh` → `scripts/install-apply.js`) or manual `cp -r` into `~/.claude/rules/ecc/` | `ECC/install.sh:37-42`; `ECC/rules/README.md:60-100` |
| Install = profile → modules → paths → per-harness targets | `ECC/manifests/install-profiles.json:4-104`; `ECC/manifests/install-modules.json` (rules-core targets 12 harnesses) |
| Hook ids live in a sidecar because Claude's hooks.json rejects extra keys; CI checks drift with fingerprints | `ECC/hooks/README.md:20-23` |
| Hook runtime control by env: `ECC_HOOK_PROFILE`, `ECC_DISABLED_HOOKS` | `ECC/hooks/README.md:64-75` |

**Multi-harness mirrors (collapsed):**

| Mirror | Relation to canonical | Evidence (sha1 scan) |
|---|---|---|
| `pi/skills/`, `pi/commands/` | 163 + 24 files **byte-identical** to `skills/`, `commands/` | shasum match |
| `.agents/skills/` (Codex) | 39 dirs, 9 identical, **30 drifted** (e.g. `tdd-workflow` 131 diff lines) | `diff .agents/skills/X/SKILL.md skills/X/SKILL.md` |
| `.cursor/rules/` | 39 flattened `common-*.md`, `alwaysApply: true` added, **content drifted** (Cursor testing lacks AAA section); no Java | `diff rules/common/testing.md .cursor/rules/common-testing.md` |
| `.codex/AGENTS.md` | "supplements the root AGENTS.md" + its own skill list | `ECC/.codex/AGENTS.md:1-21` |
| `.kiro/`, `.opencode/`, `.gemini/`, `.qwen/`, `.zed/`, `.trae/` … | per-harness adapters, mostly 1-file READMEs or own trees | dir listing |

Lesson: mirrors that are *copies* drift even in a repo with CI validators. Only generated/symlinked mirrors stay identical.

### g. Hosting / UI

`ecc2/`: Rust TUI + daemon, SQLite session store, worktree-aware sessions, "risk-scoring primitives" — alpha (`ECC/ecc2/README.md:7-30`). `team-agent-orchestration` defines an agent Kanban card schema and control-pane requirements (`ECC/skills/team-agent-orchestration/SKILL.md:21-61, 73-84`). No approval protocol beyond the two orch gates.

## 4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `ECC/workflows/orch-review.workflow.js:61-94, 217-274` | Review as **code**, not prose: schema-enforced proof for blockers, dedup on evidence snippet, adversarial verifier that can only clear with ≥0.8 confidence, fail-closed on a lost dimension. Exactly the P1/G3 shape, mechanised. |
| 2 | `ECC/agents/code-reviewer.md:39-74` | Pre-Report Gate (4 questions) + "zero findings is expected". Short, testable anti-noise text a Standards reviewer can reuse verbatim-in-spirit. |
| 3 | `ECC/rules/common/agents.md:51-59` | Delegation Completion Contract, with the observed failure that motivated it ("returned 'waiting' as their final answer"). Rule + rationale in 9 lines. |

Runner-up: `ECC/skills/orch-pipeline/SKILL.md:39-54` size classifier (ceremony scales to blast radius).

## 5. Against our decisions

| Decision | Verdict | Evidence |
|---|---|---|
| G1 rules layers (index always-on, bodies on demand, one source) | **Confirms** layering + `paths:`; **contradicts by example** on single-source — AGENTS.md restates rules, baseline pasted ×69, mirrors drift | `rules/README.md:5-33`; `AGENTS.md:130-160`; mirror table |
| G2 one crq + role labels | **New idea**: one engine + thin operation wrappers with phase mask + size tier — routing by task type *inside* one pipeline (our open "B'" item) | `orch-pipeline/SKILL.md:25-54` |
| G3 Standards ‖ Spec review, by changed path, lead judgment, round cap | **Confirms** diff-chosen dimensions + pushed-in diff; **adds** schema-enforced proof, evidence-keyed dedup, adversarial verify; **no** round cap, **no** Spec axis | `orch-review.workflow.js:177-274` |
| G5 5-section references | **Partial**: lang rule files have Good/Bad code but no "Review checks" section; review checklists live in agents instead (2 copies) | `rules/java/coding-style.md:23-30`; `agents/code-reviewer.md:113-257` |
| G6 coordinator + briefed workers | **Confirms**: worker = worktree + tmux + generated `task.md` brief + `handoff.md` template; no subagent spawning in worker | `tmux-worktree-orchestrator.js:109-160` |
| G4 plugins everywhere / tiers | **Contradicts our assumption**: a Claude plugin cannot ship rules, so ECC needs an installer; install *profiles* ≈ our tiers | `plugin.json:40-45`; `install-profiles.json:4-104` |
| Open: "stated a repo fact without checking" hook | **New idea**: GateGuard deny-force-allow, A/B claims +2.25/10 | `gateguard/SKILL.md:35-45` |
| D2 no lesson loop | **New idea**: instincts with confidence + project scope + 2-project promotion; rules-distill 2+-skills threshold | `continuous-learning-v2/SKILL.md:48-136`; `rules-distill/SKILL.md:74-80` |

## 6. Adopt / Adapt / Reject (ranked)

| Rank | Call | What | File |
|---|---|---|---|
| 1 | ADOPT | Findings JSON schema with `proof` required for blockers; reviewer returns structured findings | `workflows/orch-review.workflow.js:61-94` |
| 2 | ADOPT | Pre-Report Gate + "zero findings expected" + false-positive list (rewrite for Java/Spock) in the Standards reviewer prompt | `agents/code-reviewer.md:39-111` |
| 3 | ADAPT | Adversarial verifier per blocker (refute only ≥0.8) as the "per-finding validation" R9 said we lack; cheaper than a whole second round | `orch-review.workflow.js:127-144, 240-274` |
| 4 | ADAPT | Size tier → phase mask inside `/crq` (trivial skips stage 5 design) | `skills/orch-pipeline/SKILL.md:39-54` |
| 5 | ADOPT | Delegation Completion Contract into the coordinator/worker brief | `rules/common/agents.md:51-59` |
| 6 | ADAPT | Worker `task.md` / `handoff.md` (Summary · Files · Tests · Follow-ups) as the G6 brief/return template — but the record stays a GitLab comment (G2) | `scripts/lib/tmux-worktree-orchestrator.js:120-160` |
| 7 | ADAPT | GateGuard-style first-edit fact gate for analyst/spec-reviewer "unchecked repo fact" failure | `skills/gateguard/SKILL.md:49-73` |
| 8 | ADAPT (later, D2) | Instinct model for a lesson loop, project-scoped by remote hash | `skills/continuous-learning-v2/SKILL.md:48-79` |
| 9 | REJECT | Hand-maintained per-harness mirrors (`.cursor/rules`, `.agents/skills`) — they drifted; use AGENTS.md + one skills tree + symlinks (Q-2) | mirror table |
| 10 | REJECT | Restating rules in the always-on index and pasting a baseline into every agent | `AGENTS.md:130-160`; 69× baseline |
| 11 | REJECT | Generic language rule packs (Java = JUnit+Mockito) — conflicts with our Spock/fake-ports rules; take shape, not content | `rules/java/testing.md:11-14` |
| 12 | REJECT | "Use agents proactively without user prompt" routing by description — R2 showed description-firing fails | `AGENTS.md:88-112` |

## 7. Files actually read (ECC)

Root prefix `/private/tmp/claude-501/-Users-chiyanram-workspace-agent-platform--claude-worktrees-crq-597-b837e3/33b4f667-1fb1-4419-a848-22e556edfb52/scratchpad/r9/affaan-m_everything-claude-code/`:
`CLAUDE.md` · `AGENTS.md` · `SOUL.md` · `VERSION` · `package.json` (head) · `rules/README.md` · frontmatter of all 112 `rules/<lang>/*.md` · `rules/common/code-review.md` · `rules/common/agents.md` · `rules/common/development-workflow.md` · `rules/java/testing.md` (1-60) · `rules/java/coding-style.md` (1-30) · `rules/java/hooks.md` · `agents/code-reviewer.md` · `agents/java-reviewer.md` (1-40) · `agents/silent-failure-hunter.md` (1-40) · `commands/code-review.md` · `commands/orch-review.md` · `commands/review-pr.md` · `workflows/README.md` · `workflows/orch-review.workflow.js` · `skills/orch-pipeline/SKILL.md` · `skills/orch-fix-defect/SKILL.md` · `skills/continuous-learning-v2/SKILL.md` (1-140) · `skills/gateguard/SKILL.md` (1-110) · `skills/rules-distill/SKILL.md` (1-80) · `skills/team-agent-orchestration/SKILL.md` · `skills/santa-method/SKILL.md` (1-60) · `hooks/README.md` (1-120) · `hooks/hooks.json` (parsed) · `hooks/hooks.metadata.json` (parsed) · `install.sh` · `manifests/install-profiles.json` · `manifests/install-modules.json` (parsed) · `.claude-plugin/plugin.json` · `.codex/AGENTS.md` (1-40) · `.claude/identity.json` · `.cursor/rules/common-testing.md` (diff) · `.agents/skills/*/SKILL.md` (diff vs skills/) · `contexts/review.md` · `scripts/lib/tmux-worktree-orchestrator.js` (1-50, 100-160, grep) · `ecc2/README.md` (1-30) · sha1 of every `*.md`/`*.mdc` for mirror detection.

---

# Part 2 — anthropics/claude-code `plugins/` (Anthropic's own reference)

## 1. What it is

| | |
|---|---|
| What | The bundled first-party plugin marketplace in the Claude Code repo (`ACC/.claude-plugin/marketplace.json:1-10`) — 13 plugins |
| Maturity | Shipped with the product; `code-review` authored by Boris Cherny (`ACC/plugins/code-review/.claude-plugin/plugin.json:5-8`); docs drift between README and command (see 3d) |
| Stars | not in repo |
| One idea | **Review is high-signal or silent**: few parallel agents, then a separate validation pass per issue; anything not validated is dropped. |

## 2. File tree (what matters)

```
ACC/plugins/
├── code-review/commands/code-review.md        9-step PR review: gate → CLAUDE.md paths → 4 reviewers → validate each → post
├── pr-review-toolkit/
│   ├── commands/review-pr.md                  pick aspects by what changed; sequential or parallel
│   └── agents/ code-reviewer · silent-failure-hunter · pr-test-analyzer · comment-analyzer · type-design-analyzer · code-simplifier
├── feature-dev/
│   ├── commands/feature-dev.md                7 phases, 3 human stops
│   └── agents/ code-explorer · code-architect · code-reviewer
├── hookify/  commands/ · agents/conversation-analyzer.md · core/{config_loader,rule_engine}.py · hooks/*.py · examples/*.local.md
├── security-guidance/hooks/  pattern hook + Stop-hook LLM diff review + agentic commit review (asyncRewake)
└── commit-commands · ralph-wiggum · plugin-dev (agent-creator, skill-reviewer, plugin-validator) · agent-sdk-dev
```

## 3. Approach

### a. Rules / standards

| Aspect | Evidence |
|---|---|
| No rule library. Reviewers read the project's **CLAUDE.md** as the standard | `ACC/plugins/pr-review-toolkit/agents/code-reviewer.md:8, 16` |
| **Path-scoped rule selection**: only CLAUDE.md files in the root or in directories of changed files | `ACC/plugins/code-review/commands/code-review.md:24-26, 33` |
| Validator must confirm the cited rule "is scoped for this file and is actually violated" | `…/code-review.md:55` |
| Code-level opt-out respected: rule silenced by a lint-ignore comment is not flagged | `…/code-review.md:86` |
| security-guidance: user → project → project-local policy files concatenated, **8 KB budget**, local dropped first | `ACC/plugins/security-guidance/README.md:62-70`; `hooks/extensibility.py:45` |
| hookify: rules as `.claude/hookify.*.local.md` with frontmatter (`event`, `pattern`/`conditions`, `action: warn|block`) | `ACC/plugins/hookify/core/config_loader.py:209-211`; `examples/dangerous-rm.local.md:1-7`; `examples/require-tests-stop.local.md:1-10` |
| Anti-pattern: project facts hard-coded in reusable agents (Sentry `errorIds.ts`, `logForDebugging`; "prefer `function` keyword") | `pr-review-toolkit/agents/silent-failure-hunter.md:121-128`; `code-simplifier.md:44-51` |

### b. Process / workflow

feature-dev (`ACC/plugins/feature-dev/commands/feature-dev.md`):

```
1 Discovery → 2 Explore (2–3 explorer agents, each returns 5–10 key files; lead READS them)
 → 3 Clarifying questions ──STOP: wait for answers── (:57-69)
 → 4 Architecture (2–3 architects: minimal / clean / pragmatic) → recommend ──STOP: user picks── (:73-81)
 → 5 Implement ──"DO NOT START WITHOUT USER APPROVAL"── (:85-92)
 → 6 Review (3 reviewers: simplicity · bugs · conventions) ──STOP: fix now/later/as-is── (:101-109)
 → 7 Summary
```

| Notable | Evidence |
|---|---|
| "Whatever you think is best" → give recommendation, get explicit confirmation | `feature-dev.md:69` |
| Subagents return file lists, the lead reads files itself (context split) | `feature-dev.md:14, 41-52` |
| code-architect told to "pick one approach and commit" while the command fans out 3 architects with different lenses | `feature-dev/agents/code-architect.md:17, 34`; `feature-dev.md:78` |

### c. Roles / agents

| Aspect | Evidence |
|---|---|
| Agent = frontmatter (`name`, long `description` with `<example>` blocks, `model`, `color`, `tools`) + persona prompt | `pr-review-toolkit/agents/code-reviewer.md:1-6` |
| Model per role: haiku for gates/lookups, sonnet for summary + CLAUDE.md audit, **opus for bug hunting and bug validation** | `code-review/commands/code-review.md:14, 24, 28, 35-38, 55` |
| Lens agents (errors, tests, comments, types) are generic; output formats differ per agent (1–10 criticality, 4×1–10 ratings) | `pr-test-analyzer.md:42-47`; `type-design-analyzer.md:24-46` |
| Advisory-only clause | `comment-analyzer.md:70` |

### d. Review & verification

**`/code-review` (code-review plugin) — Anthropic's flagship shape:**

| Step | What | Evidence |
|---|---|---|
| 0 | "All tools work; no exploratory calls" — told to every subagent | `code-review.md:8-10` |
| 1 | Haiku pre-gate: closed / draft / trivial / already reviewed → stop | `:14-20` |
| 2 | Haiku: list **paths** of relevant CLAUDE.md (root + changed dirs), not contents | `:24-26` |
| 3 | Sonnet: PR summary | `:28` |
| 4 | 4 parallel reviewers: 2× CLAUDE.md compliance (sonnet), 2× bug (opus; one diff-only, one introduced-code) | `:30-39` |
| — | HIGH SIGNAL only: won't compile, definitely wrong, **quotable** CLAUDE.md violation; no style, no input-dependent issues | `:41-51` |
| — | Every agent gets PR title + description (intent) | `:53` |
| 5 | **One validation subagent per issue** (opus for bugs, sonnet for rule issues) | `:55` |
| 6 | Drop anything not validated | `:57` |
| 7–9 | Terminal by default; `--comment` posts one inline comment per unique issue; committable suggestion only if it fully fixes | `:59-77` |
| — | False-positive list: pre-existing, linter-catchable, general quality unless CLAUDE.md requires, silenced rules | `:79-86` |
| — | Citation format: full-SHA permalink with ±1 line context | `:103-109` |

Doc drift: README still describes 0–100 confidence scoring + a git-blame agent (`code-review/README.md:19-24`), `plugins/README.md:17` says "5 parallel Sonnet agents"; the command now uses per-issue validation instead (`code-review.md:55-57`). Three descriptions of one workflow.

**`/review-pr` (pr-review-toolkit):** aspect agents chosen by what changed — tests changed → test analyzer; error handling → silent-failure-hunter; types → type analyzer; code-reviewer always; simplifier after passing (`review-pr.md:35-43`). Sequential by default, parallel on request (`:47-55`). Output Critical/Important/Suggestions/Strengths (`:57-88`). Reviewer confidence ≥80, Critical 90–100 / Important 80–89 (`pr-review-toolkit/agents/code-reviewer.md:22-32, 43`).

**security-guidance — review as hooks:**

| Layer | Evidence |
|---|---|
| Regex pattern warnings on Edit/Write | `security-guidance/README.md:5` |
| Stop-hook LLM diff review, findings fed back via `asyncRewake` | `hooks/hooks.json:57-66`; `README.md:6` |
| Agentic commit/push review (Read/Grep/Glob data-flow) via `if: Bash(git commit:*)` | `hooks/hooks.json:35-53`; `README.md:7` |
| Only **+ lines** are in scope; pre-existing and out-of-task issues excluded; exception for new data flow into old sink | `hooks/llm.py:751-763` (diff_instruction) |
| **Previous findings passed in: do not re-flag (file, category)** unless that code changed | `hooks/llm.py:767-784` |
| Byte caps: 80 KB/file, 400 KB total, truncation marked | `hooks/review_api.py:27-28`; `hooks/llm.py:165-180` |
| Default model chosen for precision — "false positives are the dominant uninstall driver" | `hooks/llm.py:61-64` |
| Optional dual-call union for recall at 2× cost | `README.md:56-60` |
| Multi-agent caveat: disable Stop review when another agent can move HEAD | `README.md:51` |

### e. Context engineering

- Pass paths, not contents, then let each agent read (`code-review.md:24`; `feature-dev.md:41-52`).
- Cheap model gates expensive fan-out (`code-review.md:14-20`).
- Prior findings injected to stop re-flagging across rounds (`llm.py:767-784`).
- Hard byte budgets on policy text and diff (`extensibility.py:45`; `review_api.py:27-28`).

### f. Packaging & distribution

One marketplace file lists plugins by relative `source` (`ACC/.claude-plugin/marketplace.json:10-30`); each plugin has `.claude-plugin/plugin.json` and conventional dirs `commands/ agents/ skills/ hooks/` (`ACC/plugins/README.md:13-27`). Hooks reference `${CLAUDE_PLUGIN_ROOT}` (`hookify/hooks/hooks.json:9`). Per-project config is `.local.md` files the plugin globs (`hookify/core/config_loader.py:209-211`) or env vars (`security-guidance/README.md:44-53`). No rules shipping either — standards stay in the project's CLAUDE.md.

### g. Hosting / UI

None. Hooks fail **open** by design: "ALWAYS exit 0 - never block operations due to hook errors" (`hookify/hooks/pretooluse.py:61-70`) — opposite of ECC's fail-closed review.

## 4. Three excerpts worth studying

| # | Where | Why |
|---|---|---|
| 1 | `ACC/plugins/code-review/commands/code-review.md:41-57` | HIGH SIGNAL definition + validate-every-issue-then-drop. The shortest statement of "findings only, no noise" from the vendor. |
| 2 | `ACC/plugins/security-guidance/hooks/llm.py:751-784` | Diff-scope rule (only + lines, pre-existing excluded, sink exception) and "previous findings: do not re-flag" — directly the round-2/3 fix-diff behaviour G3 wants. |
| 3 | `ACC/plugins/feature-dev/commands/feature-dev.md:57-92` | Three human stops with exact wording ("DO NOT START WITHOUT USER APPROVAL", recommendation + confirmation on "whatever you think"). Model for `/crq` stage text. |

## 5. Against our decisions

| Decision | Verdict | Evidence |
|---|---|---|
| G1 rules layers | **Confirms** path-scoped selection (CLAUDE.md by changed dirs) + layered policy files with byte budget | `code-review.md:24-26`; `security-guidance/README.md:62-70` |
| G2 one crq + role labels | **Neutral/confirms**: one command per workflow, human stops named inline; no role concept | `feature-dev.md:57-109` |
| G3 Standards ‖ Spec, diff-scoped, lead judgment, 3-round cap | **Confirms** split by axis (2× rule-compliance ‖ 2× bug), PR intent pushed in, per-finding validation; **adds** "don't re-flag prior findings" for later rounds; **no** Spec-vs-AC axis, **no** round cap | `code-review.md:30-57`; `llm.py:767-784` |
| G5 5-section references | **New idea**: a rule finding must *quote* the rule and the validator checks scope — argues for short, quotable rule lines in each reference | `code-review.md:44, 55` |
| G6 coordinator + briefed workers | **Confirms** "agent assumptions" preamble every subagent gets (a brief header); workers return paths/findings, lead reads | `code-review.md:8-10`; `feature-dev.md:41-52` |
| G4 plugins everywhere | **Confirms** marketplace + plugin dirs; **contradicts** nothing; note plugins don't carry rules — standards stay project-side (matches Q-11) | `marketplace.json`; `plugins/README.md` |
| R8 D3 project facts in role file | **Confirms the risk** with a live example | `silent-failure-hunter.md:121-128` |

## 6. Adopt / Adapt / Reject (ranked)

| Rank | Call | What | File |
|---|---|---|---|
| 1 | ADOPT | Per-finding validation subagent, drop unvalidated (pair with ECC's schema) | `code-review/commands/code-review.md:55-57` |
| 2 | ADOPT | HIGH SIGNAL + false-positive list (pre-existing, linter-catchable, silenced) in both reviewers | `code-review.md:41-51, 79-86` |
| 3 | ADOPT | Rule findings must quote the rule; validator checks the rule is scoped to that path | `code-review.md:44, 55` |
| 4 | ADOPT | Rounds 2–3: pass prior findings, "do not re-flag (file, category) unless changed"; review + lines only | `security-guidance/hooks/llm.py:751-784` |
| 5 | ADAPT | Cheap pre-gate before reviewer fan-out (draft/trivial/already reviewed) — for us: docs-only diff → skip Standards | `code-review.md:14-20` |
| 6 | ADAPT | Aspect agents chosen by what changed (tests → test lens) as the lens half of G3 | `pr-review-toolkit/commands/review-pr.md:35-43` |
| 7 | ADAPT | feature-dev's stop wording for `/crq` gates | `feature-dev/commands/feature-dev.md:57-92` |
| 8 | ADAPT | Policy-file byte budget for the reference packet pushed to reviewers | `security-guidance/README.md:62-70` |
| 9 | REJECT | Hard-coding project facts in reusable agents | `silent-failure-hunter.md:121-128` |
| 10 | REJECT | Fail-open for a review gate (fine for advisory hooks, wrong for QA) | `hookify/hooks/pretooluse.py:61-70` |
| 11 | REJECT | Three diverging descriptions of one workflow — keep the stage text the only description | `code-review/README.md:19-24` vs `code-review.md:55` |

## 7. Files actually read (ACC)

Root prefix `/private/tmp/claude-501/-Users-chiyanram-workspace-agent-platform--claude-worktrees-crq-597-b837e3/33b4f667-1fb1-4419-a848-22e556edfb52/scratchpad/r9/anthropics_claude-code/`:
`.claude-plugin/marketplace.json` (1-30) · `plugins/README.md` (1-40) · `plugins/code-review/commands/code-review.md` · `plugins/code-review/.claude-plugin/plugin.json` · `plugins/code-review/README.md` (grep) · `plugins/pr-review-toolkit/commands/review-pr.md` · `plugins/pr-review-toolkit/agents/{code-reviewer,silent-failure-hunter,pr-test-analyzer,comment-analyzer,type-design-analyzer,code-simplifier}.md` · `plugins/feature-dev/commands/feature-dev.md` · `plugins/feature-dev/agents/{code-explorer,code-architect,code-reviewer}.md` · `plugins/hookify/hooks/hooks.json` · `plugins/hookify/hooks/pretooluse.py` · `plugins/hookify/examples/{dangerous-rm,require-tests-stop}.local.md` · `plugins/hookify/core/{config_loader,rule_engine}.py` (grep) · `plugins/hookify/agents/conversation-analyzer.md` (1-80) · `plugins/security-guidance/README.md` · `plugins/security-guidance/hooks/hooks.json` · `plugins/security-guidance/hooks/llm.py` (55-70, 745-800, grep) · `plugins/security-guidance/hooks/{review_api,extensibility}.py` (grep) · `plugins/plugin-dev/agents/skill-reviewer.md` (1-12).

Context read first: `.scratch/one-rulebook/{map,requirements,design-overview}.md`.
