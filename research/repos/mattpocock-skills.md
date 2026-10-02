# mattpocock/skills: per-repo deep report (2026-10-01)

Root for every path below: `.scratch/one-rulebook/refs/mattpocock-skills/` (HEAD `d81f3a1`, "release/v1.3" merge, 2026-09-29).

## 1. What it is

| | |
|---|---|
| What | A library of ~40 `SKILL.md` skills (27 shipped) for coding agents, plus repo-local meta-docs on how to write them |
| Maturity | v1.2.3 (`package.json:3`, `.claude-plugin/plugin.json:3`), changesets release flow (`.github/workflows/release.yml:29-37`), in Claude Code's official marketplace since 2026-08-05 (`.agents/adr/0002-ship-as-a-claude-code-plugin.md:30-41`) |
| Stars | not in the repo; README cites ~60,000 newsletter readers (`README.md:21`) |
| The one idea | **Small composable skills, not an owned process.** "Approaches like GSD, BMAD, and Spec-Kit … take away your control" (`README.md:17`). The process is a *router document* (`ask-matt`) over independent skills, and the human is the scheduler |

Second idea, nearly as central: **writing for agents is a discipline with named levers** (context pointer, two loads, information hierarchy, completion criteria, leading words, no-ops) in `skills/productivity/writing-for-agents/SKILL.md`.

## 2. File tree (what matters)

```
mattpocock-skills/
├── CLAUDE.md                      maintainer rules: buckets, plugin list sync, docs sync, no em-dashes (25 lines)
├── GLOSSARY.md                    the repo's own ubiquitous language (Issue tracker, Decision ticket, Triage role)
├── .agents/
│   ├── adr/0001-…hard-dependencies.md   setup pointer only where config is load-bearing
│   ├── adr/0002-ship-as-a-claude-code-plugin.md  why plugin.json lists skills explicitly; Codex deferred
│   ├── invocation.md              user-invoked vs model-invoked; "Call the Skill tool with X" convention
│   ├── install-block.md           single source of install wording
│   └── writing-docs.md            template for human-facing docs pages
├── .claude-plugin/plugin.json     explicit array of 27 promoted skill dirs
├── .claude-plugin/marketplace.json  repo-as-own-marketplace fallback
├── .out-of-scope/*.md             rejected requests KB (question caps, verify mode, niche trackers)
├── scripts/link-skills.sh         dev-only: symlink every non-misc/deprecated skill into ~/.claude/skills + ~/.agents/skills
├── scripts/sync-plugin-version.mjs  package.json version -> plugin.json
├── docs/{engineering,productivity}/<skill>.md   human docs pages (What / When / Common questions / It's working if)
└── skills/
    ├── engineering/   ask-matt (router) · grill-with-docs · to-spec · to-tickets · implement · implement-spec ·
    │                  code-review · tdd · diagnosing-bugs · wayfinder · triage · retro · pr · research · prototype ·
    │                  domain-modeling · codebase-design · improve-codebase-architecture · setup-matt-pocock-skills · wizard
    ├── productivity/  grilling (primitive) · grill-me · handoff · teach · to-questionnaire · wait-what · writing-for-agents
    ├── in-progress/   claude-handoff · loop-me · setup-ts-deep-modules · writing-* (not shipped)
    ├── misc/          git-guardrails-claude-code · setup-pre-commit · … (not shipped)
    └── deprecated/    empty; retired skills are deleted
    each skill: SKILL.md + agents/openai.yaml (Codex metadata) + optional sibling reference files
```

## 3. Approach, section by section

### a. Rules / standards

| Question | Answer | Evidence |
|---|---|---|
| Where do *project* coding standards live? | **Not in this repo.** Skills read whatever the consuming repo documents (`CODING_STANDARDS.md`, `CONTRIBUTING.md`) | `skills/engineering/code-review/SKILL.md:34-36` |
| Fallback when a repo has none | 12 Fowler smells pasted into the Standards sub-agent, always judgement calls, repo overrides | `code-review/SKILL.md:38-56` |
| Where per-repo config lives | `docs/agents/issue-tracker.md`, `triage-labels.md`, `domain.md`, written once by `setup-matt-pocock-skills`, pointed to from a 3-line `## Agent skills` block in CLAUDE.md/AGENTS.md | `setup-matt-pocock-skills/SKILL.md:84-110` |
| Single source | Explicit rule: "Keep each meaning in a single source of truth"; restating the environment is a "cache" | `writing-for-agents/SKILL.md:78-79` |
| Shared reference between skills | Lives inside the owning skill; others "call the Skill tool with it", never `../other/FILE.md` links | `.agents/invocation.md:16` |
| Always vs on demand | Model-invoked skill = description always loaded; user-invoked = zero context load, human is the index | `writing-for-agents/SKILL-MECHANICS.md:9-12` |
| Where should CLAUDE.md/AGENTS.md go | "used incredibly sparingly, usually only for navigation pointers" | `skills/engineering/retro/SKILL.md:41` |
| Standards read by whom | Standards file "is read during review, not implementation"; reviewer imposes standards because it has least context pressure | `retro/SKILL.md:31-35,42` |
| Mechanical vs judgement rules | Mechanical violation gets a deterministic check "full stop"; `CODING_STANDARDS.md` only for judgement calls | `retro/SKILL.md:19` |
| Soft vs hard config dependency | Only skills whose output is *wrong* without config carry the setup pointer | `.agents/adr/0001-…:5-10` |

The repo's own maintainer rules sit in a 25-line `CLAUDE.md` (bucket invariants, docs sync, router sync, no em-dashes, `CLAUDE.md:1-25`). Nothing in it is a coding standard.

### b. Process / workflow

The process is **a document, not an engine**: `ask-matt` (user-invoked router) describes one main flow plus on-ramps.

```
main flow (ask-matt/SKILL.md:13-32)
 grill-with-docs ─► [prototype detour via handoff] ─► to-spec ─► to-tickets ─► implement (per ticket, /clear between)
                                                                          └► implement-spec (task graph, parallel)
                                                    each build: tdd at pre-agreed seams ─► code-review ─► commit ─► retro
on-ramps: triage (raw issues) · diagnosing-bugs · wayfinder (foggy, multi-session) ─► merges at to-spec
```

| Element | How | Evidence |
|---|---|---|
| Stages | Separate user-invoked skills; human types each | `ask-matt/SKILL.md:13-32` |
| Routing | Router skill + per-skill docs pages as "a distributed router" | `ask-matt/SKILL.md:1-11`; `.agents/writing-docs.md:5` |
| Human gates | Grilling waits for user per round; to-spec checks seams; to-tickets "Iterate until the user approves"; triage "Wait for direction" | `grilling/SKILL.md:8,28`; `to-spec/SKILL.md:15-17`; `to-tickets/SKILL.md:42-56`; `triage/SKILL.md:72` |
| No gate | `implement` commits straight to the current branch; no PR, no ticket close | `implement/SKILL.md:13-15`; `docs/engineering/implement.md:51-61` |
| State on disk | Issue tracker (GitHub/GitLab/local `.scratch/<feature>/issues/NN-*.md`); `GLOSSARY.md`; `docs/adr/`; `.out-of-scope/` | `setup-matt-pocock-skills/issue-tracker-local.md:5-11`; `triage/OUT-OF-SCOPE.md:3-6` |
| Multi-session planning | `wayfinder`: map issue = index, child decision tickets, native blocking links, frontier query, claim-by-assign, one ticket per session | `wayfinder/SKILL.md:19-71,103-127` |
| Phase boundaries | 5-option ordered tree: Continue → /clear → /handoff → subagent → /compact (default last) | `ask-matt/PHASE-BOUNDARIES.md:17-40` |
| Lesson loop | `retro` turns session mistakes into environment changes (checks, standards, pointers), most severe first | `retro/SKILL.md:7-25` |

### c. Roles / personas / agents

There are **no personas, souls or role files.** Agents appear only as *ephemeral sub-agents named by function*:

| "Role" | Defined where | Made of |
|---|---|---|
| Standards reviewer, Spec reviewer | inline prompt bullets in the orchestrating skill | diff command + commit list + sources + brief + "Under 400 words" (`code-review/SKILL.md:60-70`) |
| Implementer / merger / exploration subagent | `implement-spec` steps | context pointers to spec, tickets, notes; worktree per ticket (`implement-spec/SKILL.md:15-32`) |
| Design-it-twice designers | `codebase-design/DESIGN-IT-TWICE.md:19-38` | one distinct constraint each ("Minimize the interface") |
| Research agent | `research/SKILL.md:6-12` | background agent, primary sources, one cited file |
| Triage "roles" | **labels**, not agents: 5 state roles + 2 category roles, mapped to tracker strings per repo | `triage/SKILL.md:24-45`; `setup-matt-pocock-skills/triage-labels.md:5-13` |

So "role" in this repo means a **label on a work item** (`ready-for-agent` / `ready-for-human`), and the per-repo file maps canonical names to real strings. Agents are never identities; they are briefs.

### d. Review & verification

| Facet | `code-review` | Evidence |
|---|---|---|
| Shape | 2 axes, **parallel sub-agents**, never merged or re-ranked | `code-review/SKILL.md:6-11,74-78` |
| Inputs | pushed in: diff command (`<fixed>...HEAD`), commit list, standards file list, smell baseline "pasted in full", spec path/contents | `:21,60-70` |
| Preflight | `git rev-parse` + non-empty diff before any spawn | `:23` |
| Spec discovery | commit refs → arg path → spec file by branch → ask; else skip axis, say "no spec available" | `:27-32,72` |
| Criteria selection | none by path: all documented standards + all 12 smells every run | `:34-56` |
| Output | Standards: per file/hunk, cite rule, hard vs judgement; Spec: missing/partial · scope creep · wrong; quote spec line | `:64,70` |
| Caps | "Under 400 words" per axis; no round cap | `:64,70` |
| Summary | count per axis + worst per axis, "Don't pick a single winner across axes" | `:78` |
| Known defects (documented honestly) | sub-agents recursively invoke `/code-review` (one report hit 50+ agents); reviews only committed work, but `implement` reviews before committing; findings are hypotheses; no convergence | `docs/engineering/code-review.md:54-76`; `docs/engineering/implement.md:63-67` |
| Same-session review | docs say prefer a fresh session: "confirmation bias with a slash command" (a quoted reader) | `docs/engineering/code-review.md:58-60` |
| Verification beyond review | `tdd` completion = red→green at confirmed seams; `diagnosing-bugs` Phase 1 completion criterion is a checkbox list (red-capable, deterministic, fast, agent-runnable) | `tdd/SKILL.md:20-38`; `diagnosing-bugs/SKILL.md:57-66` |
| PR evidence | `pr`: Summary (smallest visual), Evidence before/after (screenshot S-tier, test run A-tier), Merge Danger (one-/two-way door, blast radius) | `pr/SKILL.md:12-33,158-170` |

### e. Context engineering

| Technique | Where |
|---|---|
| **Context pointer** as a named object; wording decides reach; sharpen before inlining | `writing-for-agents/SKILL.md:10-18` |
| **Two loads** (context vs cognitive); human is the index | `writing-for-agents/SKILL.md:20-27` |
| **Information hierarchy** (in-file step → in-file reference → disclosed reference); disclose what only some branches need | `writing-for-agents/SKILL.md:29-43` |
| **Completion criteria** with clarity + demand; hide later steps only across a real context boundary | `writing-for-agents/SKILL.md:45-52` |
| Negation is a failure mode; prompt the positive | `writing-for-agents/SKILL.md:74` |
| No-op hunting, sediment | `writing-for-agents/SKILL.md:80-81` |
| Sub-agents to avoid axis pollution; "Communication to and from subagents should be sparse … context pointers" | `code-review/SKILL.md:11`; `implement-spec/SKILL.md:15` |
| Exploration subagent writes notes outside the repo for later implementers | `implement-spec/SKILL.md:23` |
| Phase-boundary tree; primary vs secondary sources | `ask-matt/PHASE-BOUNDARIES.md:42-51` |
| Keep grill→spec→tickets in one window; ~150k "smart zone" | `ask-matt/SKILL.md:34-38` |
| Handoff: temp dir, "suggested skills" section, reference artifacts not duplicate, redact | `handoff/SKILL.md:8-16` |
| `claude --bg --name` seeded background agent (in-progress) | `in-progress/claude-handoff/SKILL.md:8-10` |
| Agent brief: durable (no paths/line numbers), behavioural, testable ACs, explicit out-of-scope | `triage/AGENT-BRIEF.md:7-37` |
| Grilling: facts are the agent's job (dispatch sub-agent), decisions are the user's | `grilling/SKILL.md:26` |

### f. Packaging & distribution

| Channel | Mechanism | Evidence |
|---|---|---|
| Claude Code plugin | `plugin.json` `skills` = explicit array of promoted dirs; official marketplace, sha-pinned, auto-update | `.claude-plugin/plugin.json:21-49`; ADR-0002 `:11,40` |
| Other harnesses | `npx skills@latest add mattpocock/skills` copies editable files | `.agents/install-block.md:25-37` |
| "Pick one" | plugin = subscribe (read-only), skills.sh = fork (own); both = every skill twice | `.agents/install-block.md:55-57` |
| Maintainer local | `scripts/link-skills.sh` symlinks into `~/.claude/skills` and `~/.agents/skills`; `git pull` updates; skips `misc/`, `deprecated/`; refuses if dest is a symlink into the repo | `scripts/link-skills.sh:15-62` |
| Multi-harness invocation parity | `disable-model-invocation: true` + `agents/openai.yaml` `policy.allow_implicit_invocation: false`, kept in sync | `.agents/invocation.md:5-10` |
| Codex plugin | deferred: Codex takes one skills path and drops symlinks on install | ADR-0002 `:13-23` |
| Per-repo config | `docs/agents/*.md` + `## Agent skills` block; edit CLAUDE.md if present else AGENTS.md, never create the other | `setup-matt-pocock-skills/SKILL.md:74-82` |
| Versioning | changesets; `sync-plugin-version.mjs` copies version, `--check` mode | `scripts/sync-plugin-version.mjs:1-41` |

### g. Hosting / UI

None. Pure harness skills. Closest: `claude --bg` background agents (in-progress), and HTML reports opened from `$TMPDIR` (`improve-codebase-architecture/SKILL.md:37-41`).

## 4. Three excerpts worth studying

| # | Path:lines | Why |
|---|---|---|
| 1 | `skills/productivity/writing-for-agents/SKILL.md:10-52` | The vocabulary our whole rulebook effort needs: context pointer, context vs cognitive load, information hierarchy, disclose-by-branch, completion criteria (clarity + demand). Directly answers Q-3 and G5 "what loads when" |
| 2 | `skills/engineering/code-review/SKILL.md:58-78` | Two parallel axes, inputs pushed in, 400-word cap, "Don't pick a single winner across axes". Same shape as G3; the paired docs page (`docs/engineering/code-review.md:54-76`) lists its failure modes (recursive spawning, uncommitted diff, no convergence), which tells us what to guard |
| 3 | `skills/engineering/retro/SKILL.md:17-35` | Mechanical violation → deterministic check, judgement → standards file; review agent, not implementer, carries standards. A ready-made lesson loop (fills R8 risk D2) and a rule for what goes in the G5 "Review checks" section vs a hook |

Runners-up: `ask-matt/PHASE-BOUNDARIES.md:17-40` (compaction policy as an ordered tree); `triage/AGENT-BRIEF.md:7-37` (brief template for G6 workers); `grilling/SKILL.md:6-28` (whole primitive in 28 lines).

## 5. Against our decisions

| Decision | Verdict | Evidence / note |
|---|---|---|
| G1 rules layers (AGENTS.md index, bodies on demand, upstream as plugins) | **Confirms** | CLAUDE.md "only for navigation pointers" (`retro/SKILL.md:41`); plugin = subscribe not fork (`install-block.md:55-57`); per-repo answers in `docs/agents/*.md` (`setup…/SKILL.md:104-110`) is exactly our Q-5 split |
| G1 "~7 domain skills" | **New idea / nuance** | Skill vs plain file depends on invocation: shared reference two user-invoked skills need goes in "a plain file outside the skill system" (`SKILL-MECHANICS.md:14`). Our standards references that only reviewers read could be plain files, not skills |
| G2 one crq + role labels | **Confirms labels, contradicts the engine** | Roles are labels mapped per repo (`triage-labels.md:5-15`). But matt has no single pipeline: the flow is a router doc and each stage a separately typed skill (`ask-matt/SKILL.md:13-32`); README rejects process-owning frameworks (`README.md:17`) |
| G3 Standards ‖ Spec review | **Confirms shape** | Two parallel sub-agents, pushed inputs, word cap, per-axis worst (`code-review/SKILL.md:58-78`) |
| G3 criteria by changed path, round cap, lead judgment | **Not covered (we go further)** | matt loads all standards + all 12 smells every run, no rounds, aggregates verbatim (`:34-56,76`); its docs admit no convergence (`docs/engineering/code-review.md:70-72`) |
| G3 fresh read-only reviewer | **Confirms (in docs, not code)** | Docs prefer a fresh session (`docs/engineering/code-review.md:58-60`); but `implement` runs review in the authoring session (`implement/SKILL.md:13`) |
| G5 5-section references | **Partial confirm** | `tdd` = rules + anti-patterns + Good/Bad files (`tdd/SKILL.md`, `tests.md:3-77`); smell baseline is "what it is → how to fix" (`code-review/SKILL.md:43`). No "Review checks at end" section; review reads the whole doc |
| G6 coordinator + briefed workers | **Confirms brief style, no coordinator** | `implement-spec` = orchestrator + worktree-per-ticket implementers + merger, context pointers not copies (`implement-spec/SKILL.md:13-40`); brief template (`AGENT-BRIEF.md:39-68`). No standing coordinator; human is the scheduler |
| G4 plugins everywhere | **Confirms, with a caveat** | Explicit skills array (`plugin.json:21-49`); Codex drops symlinks, so "one tree linked into each harness" fails for Codex plugins (ADR-0002 `:15`); skills.sh copy is their Codex path |
| G4 coordinator-as-contract / tiers | **No signal** | Nothing in repo |
| Q-4 "stage orders it" | **Confirms strongly** | "Call the Skill tool with X" beats a `/name` mention (`.agents/invocation.md:16`); one skill per call (`:20`); user-invoked skills can never be called (`:22`) |
| Q-6 talking set | **Adjacent** | `wait-what` is user-invoked, a one-line re-pitch prompt (`wait-what/SKILL.md:7`), so it is *not* "active from session start" by itself |

## 6. Adopt / Adapt / Reject (ranked)

| Rank | Verdict | What | File |
|---|---|---|---|
| 1 | **ADOPT** | Write every rule/skill/brief with the `writing-for-agents` levers; run it as the rubric when rewriting AGENTS.md and the G5 references (it is already an upstream plugin, so no copy) | `skills/productivity/writing-for-agents/SKILL.md` |
| 2 | **ADOPT** | "Call the Skill tool with X" phrasing in every `/crq` stage; never reference a user-invoked skill from a stage | `.agents/invocation.md:16-22` |
| 3 | **ADOPT** | Mechanical → hook/check, judgement → reference file; reviewer (not implementer) carries standards. Use as the test for every rule in R1/R7 | `skills/engineering/retro/SKILL.md:19,29-35` |
| 4 | **ADAPT** | `code-review` shape for G3, plus guards for its documented defects: forbid recursive skill/agent spawning in reviewer briefs, review the committed diff only after commit, path-scoped criteria, round cap | `code-review/SKILL.md:58-78`; `docs/engineering/code-review.md:54-76` |
| 5 | **ADAPT** | `AGENT-BRIEF.md` template (current/desired behaviour, key interfaces, testable ACs, out of scope, no paths) as the G6 worker brief and the GitLab handoff comment | `skills/engineering/triage/AGENT-BRIEF.md:39-68` |
| 6 | **ADAPT** | `setup-matt-pocock-skills` pattern: one `## Agent skills` pointer block + `docs/agents/*.md` answers. We already have `docs/agents/`; keep it, but re-run upstream setup in verify mode to detect drift (their stated workflow) | `setup-matt-pocock-skills/SKILL.md:63-110`; `.out-of-scope/setup-skill-verify-mode.md:9` |
| 7 | **ADAPT** | `retro` as the D2 lesson loop: run at /crq stage 10, output goes to a hook or a reference "Review checks" line | `retro/SKILL.md:7-25` |
| 8 | **ADAPT** | Phase-boundary tree as the fleet's compaction/handoff policy (coordinator decides continue / fresh worker / handoff) | `ask-matt/PHASE-BOUNDARIES.md:17-40` |
| 9 | **ADOPT** | `.out-of-scope/` KB for rejected rule proposals, so reviewers stop re-suggesting them | `skills/engineering/triage/OUT-OF-SCOPE.md` |
| 10 | **ADOPT** | Explicit `skills` array in our own plugin.json; version sync script | `.claude-plugin/plugin.json:21-49`; `scripts/sync-plugin-version.mjs` |
| 11 | **REJECT** | Process as loose router with the human as scheduler: our fleet needs one stage-owned `/crq` (Q-8) | `ask-matt/SKILL.md` |
| 12 | **REJECT** | `implement` committing to current branch with in-session review and no ticket close | `implement/SKILL.md:7-15`; `docs/engineering/implement.md:51-67` |
| 13 | **REJECT** | Always-on 12-smell baseline every review: it is judgement noise on every run and works against Q-9 cost; fold the few that matter into G5 references instead | `code-review/SKILL.md:38-56` |
| 14 | **REJECT** | `link-skills.sh` symlinks as a distribution route for the fleet: author marks it dev-only, unsupported (`scripts/link-skills.sh:4-6`), and it `rm -rf`s non-symlink targets (`:55-57`) | `scripts/link-skills.sh` |

## 7. Files actually read

```
README.md
CLAUDE.md
GLOSSARY.md
CHANGELOG.md (headings + grep for code-review/implement/smell)
package.json
.agents/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md
.agents/adr/0002-ship-as-a-claude-code-plugin.md
.agents/install-block.md
.agents/invocation.md
.agents/writing-docs.md
.changeset/graduate-implement-spec.md
.changeset/user-invoked-skill-invocation.md
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.github/workflows/release.yml
.out-of-scope/mainstream-issue-trackers-only.md
.out-of-scope/question-limits.md
.out-of-scope/setup-skill-verify-mode.md
scripts/link-skills.sh
scripts/list-skills.sh
scripts/sync-plugin-version.mjs
docs/engineering/code-review.md
docs/engineering/implement.md
docs/engineering/wayfinder.md (head)
docs/productivity/writing-for-agents.md
skills/engineering/README.md
skills/productivity/README.md
skills/misc/README.md
skills/in-progress/README.md
skills/deprecated/README.md
skills/engineering/ask-matt/SKILL.md
skills/engineering/ask-matt/PHASE-BOUNDARIES.md
skills/engineering/code-review/SKILL.md
skills/engineering/code-review/agents/openai.yaml
skills/engineering/implement/SKILL.md
skills/engineering/implement/agents/openai.yaml
skills/engineering/implement-spec/SKILL.md
skills/engineering/setup-matt-pocock-skills/SKILL.md
skills/engineering/setup-matt-pocock-skills/domain.md
skills/engineering/setup-matt-pocock-skills/issue-tracker-gitlab.md
skills/engineering/setup-matt-pocock-skills/issue-tracker-local.md
skills/engineering/setup-matt-pocock-skills/triage-labels.md
skills/engineering/setup-matt-pocock-skills/agents/openai.yaml
skills/engineering/wayfinder/SKILL.md
skills/engineering/to-spec/SKILL.md
skills/engineering/to-tickets/SKILL.md
skills/engineering/triage/SKILL.md
skills/engineering/triage/AGENT-BRIEF.md
skills/engineering/triage/OUT-OF-SCOPE.md
skills/engineering/tdd/SKILL.md
skills/engineering/tdd/tests.md
skills/engineering/tdd/mocking.md
skills/engineering/retro/SKILL.md
skills/engineering/pr/SKILL.md
skills/engineering/research/SKILL.md
skills/engineering/domain-modeling/SKILL.md
skills/engineering/codebase-design/SKILL.md
skills/engineering/codebase-design/DESIGN-IT-TWICE.md
skills/engineering/diagnosing-bugs/SKILL.md
skills/engineering/improve-codebase-architecture/SKILL.md
skills/engineering/grill-with-docs/SKILL.md
skills/engineering/prototype/SKILL.md
skills/productivity/writing-for-agents/SKILL.md
skills/productivity/writing-for-agents/SKILL-MECHANICS.md
skills/productivity/grilling/SKILL.md
skills/productivity/grill-me/SKILL.md
skills/productivity/handoff/SKILL.md
skills/productivity/wait-what/SKILL.md
skills/productivity/teach/SKILL.md (head)
skills/in-progress/claude-handoff/SKILL.md
skills/in-progress/loop-me/SKILL.md
skills/misc/git-guardrails-claude-code/SKILL.md
```

Not read: `codebase-design/DEEPENING.md`, `improve-codebase-architecture/HTML-REPORT.md`, `prototype/LOGIC.md`, `prototype/UI.md`, `teach/*-FORMAT.md`, `domain-modeling/*-FORMAT.md`, `wizard/*`, most `docs/**` pages, remaining `.changeset/*`, other `agents/openai.yaml`.
