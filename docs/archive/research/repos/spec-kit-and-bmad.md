# spec-kit and BMAD-METHOD — per-repo deep report (one-rulebook map, 2026-10-01)

Roots used in every citation below:

```
SK = scratchpad/r9/github_spec-kit              HEAD 6244a2e, 2026-10-01
BM = scratchpad/r9/bmad-code-org_BMAD-METHOD    HEAD 1cbcfa2, 2026-09-28
```

## Headline — role model, theirs vs ours

```
 OURS (G2/G6)          spec-kit                          BMAD v6.12 → v7 (Unreleased)
 ─────────────         ──────────────────────────        ──────────────────────────────────────
 coordinator           human maintainer + label          `bmad` hub skill (advises, routes)
                       (bug-fix.md:63-68)                 + "orchestrator" outside BMAD
                                                          (autonomous-development-loops.md:13-17)
 analyst  (1–3)        /specify + /clarify commands      Mary analyst + John PM (+Sally UX)
 spec-reviewer (5)     /analyze, /checklist (read-only)  none — human CHECKPOINT 1 on plan
 developer (6)         /implement                        Amelia dev → bmad-build
 qa (7–8)              /converge + bug-test workflow     NONE — QA + SM folded INTO Amelia
                                                          (CHANGELOG.md:388, retired.toml:8-9)
 identity              none: "role" = install bundle     thin persona TOML + menu of skills
```

| | ours | spec-kit | BMAD |
|---|---|---|---|
| a role is made of | soul + brief + stage label | a bundle of commands/workflows (`bundle.yml:7`) or a 1-line "You are a bug-fix agent" + tool allowlist (`bug-fix.md:12-49`) | `customize.toml` role/identity/style/principles + `[[agent.menu]]` of skills (`bmad-agent-dev/customize.toml:40-81`) |
| who owns the steps | `crq.md` stages (G2) | command templates | workflow skills (`bmad-build/step-0N`) — agent only routes |
| separate QA identity | yes, fresh per round | yes (bug-test agent, separate label) | **removed**; review = context-free lens subagents launched by the dev's workflow |
| separate spec reviewer | removed (G1 decision) | `/analyze` exists, optional | never existed in v6/v7; human checkpoint only |

The one finding that matters most: **BMAD had SM + QA as personas and deleted both** (v6.3.0, 2026-04-09). Review
did not disappear — it moved from a *persona* into *context-free lens subagents* inside the build workflow. That
is the shape G3 already chose (fresh read-only reviewers, packets pushed in). It argues our `qa` role should be
"a fresh process with a review packet", not "a soul".

---

# 1. github/spec-kit

## 1.1 What it is

| | |
|---|---|
| What | GitHub's Spec-Driven Development toolkit: `specify` Python CLI + command templates rendered into each agent's native format |
| Maturity | `version = "1.0.14.dev0"` (`SK/pyproject.toml:3`); 42 built-in integrations (`SK/integrations/catalog.json`, counted) |
| Stars | badge only in README; not verifiable from the clone |
| One idea | The spec is the artifact; code is regenerated from spec → plan → tasks, governed by one `constitution.md` |

## 1.2 File tree (what matters)

```
SK/
├── AGENTS.md                         58-line pointer index for contributors (pointers, not rules)
├── .specify/memory/constitution.md   the project's own ratified constitution (governs spec-kit itself)
├── templates/
│   ├── constitution-template.md      [PRINCIPLE_N] placeholder scaffold
│   ├── spec-template.md · plan-template.md · tasks-template.md · checklist-template.md
│   └── commands/                     the 10 core commands, one .md each
│       specify · clarify · plan · tasks · analyze · checklist · implement · converge · constitution · taskstoissues
├── presets/lean/commands/            same commands rewritten in ~20 lines each
├── workflows/{speckit,bugfix}/workflow.yml   YAML steps incl. `type: gate`
├── workflows/ARCHITECTURE.md         engine, RunState persist + resume
├── presets/ARCHITECTURE.md           override > preset > extension > core resolution
├── design/integration.md             how one template becomes md/toml/yaml/skills per agent
├── examples/bundles/<role>/bundle.yml   "role bundles": analyst, PM, developer, security
├── extensions/{bug,assess,git,agent-context}/   optional command packs
├── .github/workflows/bug-{assess,fix,test}.md   label-gated agentic workflows (gh-aw)
└── docs/guides/agentic-sdlc.md       how spec-kit develops spec-kit
```

## 1.3 Approach

### a. Rules / standards

| What | Evidence |
|---|---|
| One governing file: `.specify/memory/constitution.md`, semver'd (MAJOR/MINOR/PATCH rules) | `SK/templates/commands/constitution.md:100-103` |
| Every amendment emits a "Sync Impact Report" naming which templates were re-checked | `constitution.md:112-119`; real one at `SK/.specify/memory/constitution.md:1-32` |
| Loaded on demand by each command, "IF EXISTS" | `specify.md:115`, `plan.md:64`, `implement.md:96` |
| Constitution is non-negotiable inside review; changing a principle is a separate act | `analyze.md:60` |
| Rules carry a **Rationale** paragraph each | `SK/.specify/memory/constitution.md:69-71, 95-97` |
| Customisation by layered resolution: override > preset > extension > core, with `replace/prepend/append/wrap` | `SK/presets/ARCHITECTURE.md:30-35, 49-54` |
| Contributor `AGENTS.md` is pure routing: "Before X, read Y" | `SK/AGENTS.md:11-51` |
| **Anti-pattern:** the ~35-line extension-hook dispatch block is copied into all 10 command templates (5–6 hits each for `extensions.yml`) | `specify.md:21-54` and `:236-268`; `plan.md:74-106`; `analyze.md:204-234` |

There are no code standards in the product: the constitution is per-project and generic. Spec-kit's own code
standards live in its constitution (`SK/.specify/memory/constitution.md:44-71`) and are enforced by conventional CI
(`SK/docs/guides/agentic-sdlc.md:149-154`), not by an agent reviewer.

### b. Process / workflow

```
 /constitution ─▶ /specify ─▶ /clarify ─▶ /plan ─▶ /tasks ─▶ /analyze ─▶ /implement ─▶ /converge
                    │  spec.md     ≤5 Q      plan.md   tasks.md   read-only   ticks [X]     appends
                    │  + checklists/requirements.md   research.md  T001 [P]   report        "Phase N:
                    ▼                                 data-model                            Convergence"
             specs/NNN-slug/  +  .specify/feature.json  (state on disk)
```

| Aspect | How | Evidence |
|---|---|---|
| State on disk | feature dir + `.specify/feature.json` so later commands find it without branch-name parsing | `specify.md:99-106` |
| Routing | `handoffs:` frontmatter offers the next command | `specify.md:3-10`, `plan.md:3-10` |
| Human gates | workflow engine `type: gate` (approve/reject, `on_reject: abort`) after specify and after plan | `SK/workflows/speckit/workflow.yml:46-62` |
| Resume | `RunState` saved after every step; gate pauses persist index; `specify workflow resume` | `SK/workflows/ARCHITECTURE.md:58-73` |
| Implement gate on checklists | unchecked items → STOP and ask | `implement.md:79-84` |
| Their own SDLC | label-gated stages: `bug-assess` → human label → `bug-fix` (draft PR) → label → `bug-test`; each stage reads the previous stage's **issue comment as its contract** | `SK/.github/workflows/bug-fix.md:49-68, 95-110`; `bug-test.md:96-101, 118-130` |
| Size by need | small change stays issue + PR; SDD only for substantial features | `SK/docs/guides/agentic-sdlc.md:79-98, 257-263` |

### c. Roles / personas

| Finding | Evidence |
|---|---|
| No personas, no souls, no names anywhere in core | (absence across `templates/commands/*`) |
| A "role bundle" is an installable set of extensions/presets/steps/workflows tagged `role:` | `SK/examples/bundles/developer/bundle.yml:3-31`; BA, PM, security siblings |
| In the GitHub agentic workflows a role = one sentence + **tool allowlist + permissions + `safe-outputs` caps** | `bug-fix.md:12-44` (e.g. `create-pull-request: draft: true, max: 1`, `add-labels: allowed: [...]`) |
| Who gates: "The maintainer is the gatekeeper" | `bug-fix.md:67-68` |

### d. Review & verification

| Command | Shape | Criteria | Output / cap | Evidence |
|---|---|---|---|---|
| `/specify` self-check | spec vs generated quality checklist | 16 fixed items | re-validate max 3 iterations | `specify.md:146-197` |
| `/clarify` | interview | 11-category coverage scan | ≤5 Q, **one at a time**, recommended option first | `clarify.md:129-179` |
| `/checklist` | "unit tests for English" | requirement quality, never implementation | append-only `CHK###`, reviewer owns checkboxes | `checklist.md:9-11, 139-191` |
| `/analyze` | read-only cross-artifact | 6 passes A–F + constitution | table, severity, **cap 50 rows**, coverage %, never edits | `analyze.md:115-190, 238-251` |
| `/converge` | code vs spec/plan/tasks | `missing/partial/contradicts/unrequested` | append-only tasks; byte-identical file when converged | `converge.md:73-83, 147-166, 202-232` |

There is no diff-scoped code-standards reviewer. Code review is a human maintainer plus CI.

### e. Context engineering

- "Progressive disclosure": load named sections only (`analyze.md:75-104`, `:238-243`; `converge.md:105-131`).
- Scripts return JSON paths so the model never guesses (`plan.md:62`, `analyze.md:66`).
- Plan Phase 0 fans out one research task per unknown (`plan.md:116-135`).
- Nothing on compaction or subagent briefs.

### f. Packaging & distribution

| | Evidence |
|---|---|
| `specify` CLI via uv/pipx/air-gapped | `SK/docs/install/*.md` |
| One template set rendered per agent: Markdown, TOML, YAML recipes, or `skills/speckit-*/SKILL.md` | `SK/design/integration.md:47-60` |
| `{SCRIPT}` resolved to sh / ps / py variants at render time | `integration.md:68-76` |
| Installed files tracked by SHA-256 manifest; edited files survive uninstall | `integration.md:80-86` |
| CLI does **not** own `AGENTS.md`/`CLAUDE.md`; an opt-in extension manages them | `integration.md:88-93` |

### g. Hosting / UI

None. The workflow engine is CLI; a `gate` pauses in CI (`SK/workflows/ARCHITECTURE.md:91`). Agentic runs happen in
GitHub Actions with sandboxed `safe-outputs`.

## 1.4 Three excerpts worth studying

| Where | Why |
|---|---|
| `SK/templates/commands/converge.md:147-166` | "completion claims are not evidence" — re-checks every task regardless of checkbox, and names four gap types including `unrequested`. Our stage 8 AC citing in prompt form |
| `SK/templates/commands/checklist.md:169-191` | WRONG/CORRECT pairs that turn "verify the page shows 3 cards" into "is the number of cards specified?" — a clean split between spec review and code review |
| `SK/.github/workflows/bug-fix.md:61-110` | a stage reads the prior stage's issue comment, treats it as the contract, refuses to re-litigate it, and stops with one comment when it is missing |

## 1.5 Against our decisions

| Decision | Verdict | Why (evidence) |
|---|---|---|
| G1 rules layers | confirms | one governing file + on-demand load; contributor `AGENTS.md` is a pointer index (`SK/AGENTS.md:11-51`). Counter-example: hook block copied ×10 shows what happens without one source |
| G2 one crq + role labels | confirms | stages = commands; roles are not first-class in core. Label = trigger + gate in their own SDLC (`bug-fix.md:6-10, 63-68`) |
| G3 Standards ‖ Spec | partial | Spec axis is strong (`/analyze`, `/converge`); Standards axis is left to CI. New: `unrequested` gap type |
| G5 5-section references | new idea | constitution principle = rules + **Rationale** paragraph (`constitution.md:69-71`). Our "Decided edges" could carry the why the same way |
| G6 coordinator + briefed workers | confirms | issue comment = handoff record, human label = dispatch (`agentic-sdlc.md:267-271`) |
| G4 plugins / tiers | new idea | one template source, many render targets (`integration.md:47-60`); SHA manifest protects edited files |

## 1.6 Adopt / adapt / reject

| # | Call | What | Shows it |
|---|---|---|---|
| 1 | ADOPT | `unrequested` as a stage-8 gap type beside missing/partial/contradicts | `converge.md:156-163` |
| 2 | ADOPT | role = tool allowlist + output caps (draft-only PR, `max: 1`, allowed labels), not prose | `bug-fix.md:12-44` |
| 3 | ADAPT | stage reads previous stage's GitLab comment as its contract; missing → one comment + stop | `bug-fix.md:70-110` |
| 4 | ADAPT | clarify loop: one question, "why it matters", recommended option first, cap 5 | `clarify.md:140-179` |
| 5 | ADAPT | Sync Impact Report when a rule file changes (which references/skills were re-checked) | `constitution.md:112-119` |
| 6 | REJECT | per-command boilerplate copies (hook block ×10) | `specify.md:21-54` |
| 7 | REJECT | full SDD artefact set for every change; they don't do it themselves | `agentic-sdlc.md:257-263` |

---

# 2. bmad-code-org/BMAD-METHOD

## 2.1 What it is

| | |
|---|---|
| What | "Open source framework for structured, agent-assisted software delivery" (`BM/AGENTS.md:3`), shipped as skills |
| Maturity | v6.12.0 on 2026-09-03; Unreleased = v7 cut in progress (`BM/CHANGELOG.md:3-22`); 42 platforms (`CHANGELOG.md:316`) |
| Stars | not verifiable from the clone |
| One idea | Named personas (Mary, John, Sally, Winston, Amelia) are a thin front door; the **work** lives in step-file workflow skills driven by a plan file with frozen intent |

The repo has been shrinking hard: "Core drops from fourteen skills to eight" and the release deletes ~1,900 more lines
than it adds (`CHANGELOG.md:47-51`).

## 2.2 File tree (what matters)

```
BM/
├── AGENTS.md                                 32 lines; "Writing prompts" rule at :16-20
├── skills/
│   ├── bmad/                                 hub: help, setup, migrate, initiative
│   │   ├── SKILL.md · references/setup.md
│   │   └── scripts/ render_skill.py · resolve_customization.py · setup.py · memlog.py · roster.py
│   ├── bmod-method/ roster.toml · retired.toml   who exists; what was deleted
│   ├── bmad-agent-{analyst,pm,architect,ux-designer,dev}/
│   │   ├── SKILL.md                          activation boilerplate (identical but 3 lines)
│   │   └── customize.toml                    persona + menu (DO NOT EDIT; override in _bmad/custom/)
│   ├── bmad-build/                           THE implementation loop
│   │   ├── workflow.md · step-01..05 · step-oneshot.md · plan-template.md
│   │   ├── customize.toml                    route, review, lenses, implementation_handoff
│   │   └── review-prompts/ · references/claims-check.md · deletion-check.md
│   ├── bmad-build-auto/                      unattended worker for an orchestrator
│   ├── bmad-code-review/                     standalone review (same lenses, copied)
│   ├── bmad-review/                          generic lens runner (adversarial, edge, gap, prose, structure)
│   ├── bmad-project-context/                 writes the managed AGENTS.md block
│   │   └── references/ best-practices.md · template.md
│   └── bmad-party-mode/ · bmad-ticket/ · bmad-prd/ · bmad-architecture/ · …
├── docs/{start,build,plan,customize,existing-codebases}/
├── web-bundles/                              planning skills packaged for Gemini Gems / Custom GPTs
└── tools/ validate_skills.py · skill-validator.md · quality.py
```

## 2.3 Approach

### a. Rules / standards

| What | Evidence |
|---|---|
| Project rules = one managed block in `AGENTS.md`, six sections: Orientation · Policy · Where things are · Running and verifying · Conventions that differ · Known pitfalls | `BM/skills/bmad-project-context/references/template.md:3-12` |
| Block carries provenance: date + verified SHA; refresh diffs from it | `template.md:18, 55`; `SKILL.md:89` |
| Admission test: "what does it cost when it doesn't" know it | `best-practices.md:5-9` |
| Retrieval rule: an index the agent must choose to fetch gets skipped; pointers need an **observable** trigger | `best-practices.md:51` |
| Nested `AGENTS.md` only when loading is verified per harness | `best-practices.md:53` |
| Deletion needs one of four grounds; "discoverable in the repo" is never enough | `best-practices.md:75-82` |
| `CLAUDE.md` reduced to `@AGENTS.md`; "No instruction lives in two loaded files" | `bmad-project-context/SKILL.md:95` |
| Prefer a hook/lint/CI check to a line; a landed check deletes its line | `SKILL.md:70`; `best-practices.md:63` |
| Pitfalls only from observed mistakes (`record` intent) | `SKILL.md:105-109`; `best-practices.md:16` |
| Team standards reach agents via `persistent_facts = ["file:…"]` in a committed override | `BM/docs/customize/adopt-bmad-across-a-team.md:34-54, 56-77` |
| Repo meta-rule: prompt length is paid every run; skip exotic cases | `BM/AGENTS.md:16-20` |
| **Anti-pattern:** review prompts copied into `bmad-build` and `bmad-code-review` and already drifted | `diff` of `review-prompts/verification-gap.md` (line 113) and `edge-case-hunter.md` (lines 8, 13, 51, 96-98) |

### b. Process / workflow

```
 bmad-build (one session-sized unit)
 step-01 clarify+route ─▶ step-02 plan ─▶ CHECKPOINT 1 (human) ─▶ step-03 implement ─▶ step-04 review ─▶ step-05 present
   resume by plan          Code Map,        approve+continue |      context-free         lenses ‖, triage,     commit local,
   status                  Open Questions   approve+STOP         subagent, plan =       loopback ≤5           never push
                           (HALT)           (fresh session)      sole source of truth
 state: plan-<slug>.md frontmatter  status: draft → ready-for-dev → in-progress → in-review → built → done | blocked
```

| Aspect | How | Evidence |
|---|---|---|
| State on disk | plan file frontmatter `status`, `baseline_revision`, `lenses_ran`, `review_loop_iteration` | `BM/skills/bmad-build/plan-template.md:1-14` |
| Resume | status → step mapping | `step-01-clarify-and-route.md:20` |
| Human-owned intent | `<frozen-after-approval>` holds Intent, Boundaries, I/O matrix; locked at approval | `plan-template.md:21-50`; `step-02-plan.md:67` |
| Gate | single checkpoint after planning, with "Approve and stop" so a fresh session implements | `step-02-plan.md:45-67` |
| Size gate | single goal, 900–1600-token plan, split → `deferred-work.md` | `workflow.md:23-31`; `step-01:71-83` |
| Investigate before asking | never ask what the repo can answer | `step-02-plan.md:11-13` |
| Unattended worker | `bmad-build-auto` builds exactly one named ticket, writes terminal status; orchestrator owns dispatch + checkpoints | `BM/docs/build/autonomous-development-loops.md:8-17, 59-69` |
| Worker HALT protocol | only sanctioned turn end is HALT with a status; never background a subagent | `bmad-build-auto/workflow.md:9-39` |

### c. Roles / personas

| Finding | Evidence |
|---|---|
| Roster is five: analyst, PM, UX, architect, dev | `BM/skills/bmod-method/roster.toml:11-49` |
| **SM, QA, quick-flow-solo-dev removed and folded into the dev agent** | `CHANGELOG.md:388`; `retired.toml:8-10` |
| Dev menu now carries build, QA test generation, code review, retrospective, tickets | `bmad-agent-dev/customize.toml:58-81` |
| Persona = 4 short fields: role, identity, communication_style, principles | `bmad-agent-dev/customize.toml:40-52` |
| Name/title hard-locked; everything else overridable | `customize.toml:1-10` |
| Three layers: shipped → team (`_bmad/custom/<skill>.toml`, committed) → personal (`.user.toml`, gitignored) | `bmad-agent-dev/SKILL.md:27-33`; `adopt-bmad-across-a-team.md:29-32` |
| Persona carries into every skill it dispatches; icon prefixes every message | `SKILL.md:43, 57-59, 75` |
| Agent = router: dispatches menu items to skills; one clarifying question only when two items are close | `SKILL.md:67-75` |
| All five `SKILL.md` files are the same text except 3 lines (copy per agent) | diff of dev vs analyst `SKILL.md` |
| Multi-persona = `bmad-party-mode` in one session, optional memory | `bmad-party-mode/SKILL.md:8, 28-29` |

### d. Review & verification

```
 orchestrator stages diff → /tmp/<unique>.diff   (path only; diff text never pasted)
        │
        ├── quick:  1 context-free subagent  — plan ACs + AGENTS.md/CLAUDE.md at root AND in touched dirs
        └── thorough (parallel, blocking):  blind-hunter │ edge-case-hunter (+claims last) │ verification-gap │ intent-alignment
        ▼
 triage by the orchestrator: re-verify every finding, ignore reviewer severity
   verdict ∈ high | medium | low | false | maybe-false   → one row each in "## Review Triage Log"
   route   ∈ intent_gap | bad_plan | patch | defer        → loopback cap 5, then HALT to human
```

| Mechanism | Evidence |
|---|---|
| Rules for the reviewer chosen by **touched directory** (`AGENTS.md` at root and in diff dirs) | `bmad-build/customize.toml:113` |
| Diff passed as a file path, never inline | `step-04-review.md:29, 37`; `bmad-code-review/step-01:25` |
| Plan/commit narrative = "testimony, not evidence", read only after tracing | `references/claims-check.md:3-5` |
| Reviewers emit no severity; triage grades after verifying | `step-04-review.md:53-63`; `lens-adversarial.md:19` |
| `low` rejected when fix adds guards/branches | `step-04-review.md:69` |
| Out-of-scope only if the *intent* excludes it, not the plan | `step-04-review.md:71` |
| Fixes that edit agent-context files → `defer` | `step-04-review.md:82` |
| Patch round: same implementer subagent, fixed 3-line message, run only touched tests | `step-04-review.md:87-95` |
| Loopback cap 5 → human | `step-04-review.md:84` |
| Blind hunter finding floor `min(floor(sqrt(kB)+1),10)` | `bmad-build/customize.toml:129` |
| Verification-gap lens: "read a test before claiming what it covers" | `review-prompts/verification-gap.md:11-17, 55` |
| Default build review = `quick` (one lens) | `bmad-build/customize.toml:97` |

### e. Context engineering

- Step files loaded just in time; never two at once (`bmad-build/workflow.md:62-83`).
- Investigation subagents return short summaries only; findings go into the plan's Code Map (`step-02-plan.md:11`).
- Implementation dispatch must not restate goals, files, ACs or CLAUDE.md rules — "the plan is the subagent's sole
  source of truth" (`step-03-implement.md:31-33`; handoff text `customize.toml:85-91`).
- No subagents → write a self-contained prompt file per lens and HALT for a human to run elsewhere
  (`step-04-review.md:47`).
- Skills rendered by Jinja + TOML into an immutable snapshot per project (`BM/skills/bmad/scripts/render_skill.py:6`;
  `CHANGELOG.md:51`).

### f. Packaging & distribution

| | Evidence |
|---|---|
| `npx skills add bmad-code-org/BMAD-METHOD [--skill …]`, project or global scope | `BM/docs/start/install-bmad.md:16-26` |
| Or plugin marketplace in Claude Code and Codex (`bmad-code-org/bmad-plugins`); "use one installation method" per skill | `install-bmad.md:28-42` |
| `bmad setup` = check · update · config Qs · retire renamed/removed skills · migrate, one flow | `BM/skills/bmad/references/setup.md:5-81`; `CHANGELOG.md:16-20` |
| `retired.toml` per module; names never reused | `bmod-method/retired.toml:1-6` |
| Team customisation committed, personal gitignored | `adopt-bmad-across-a-team.md:29-32` |
| Planning skills also shipped as Gemini Gems / Custom GPT bundles | `BM/web-bundles/README.md:3, 17-20` |

### g. Hosting / UI

None. Party mode is an in-session roundtable. Unattended runs are `bmad-build-auto` driven by "an AI coding session or
bmad-loop" (`autonomous-development-loops.md:13-17`).

## 2.4 Three excerpts worth studying

| Where | Why |
|---|---|
| `BM/skills/bmad-build/step-04-review.md:53-95` | the best triage text in either repo: verify each claim at file:line, five verdicts, every finding logged, four routes, cap 5, fixed patch message |
| `BM/skills/bmad-project-context/references/best-practices.md:49-82` | retrieval (observable triggers), nested-file verification, and the four deletion grounds — directly reusable for our `AGENTS.md` |
| `BM/skills/bmad-build/references/claims-check.md:3-14` | the author's plan is testimony; read it last, try to falsify each claim |

## 2.5 Against our decisions

| Decision | Verdict | Why (evidence) |
|---|---|---|
| G1 rules layers | confirms + sharpens | one `AGENTS.md` block, `CLAUDE.md`=`@AGENTS.md`, no rule in two loaded files (`SKILL.md:95`); pointers need observable triggers (`best-practices.md:51`) |
| G2 one crq + role labels | confirms | agents only route to workflow skills; steps live in the workflow (`bmad-agent-dev/SKILL.md:67-75`) |
| G2 four roles incl. qa | **contradicts in part** | BMAD deleted QA and SM personas (`CHANGELOG.md:388`). Review survived as fresh lens subagents. Our `qa` stays defensible only as a fresh process, not as a soul |
| G3 Standards ‖ Spec | confirms shape, adds triage | parallel context-free lenses, diff by path, rules by touched dir (`customize.toml:113`); new: orchestrator re-verifies each finding, `false/maybe-false` verdicts |
| G3 3-round cap | close | they cap loopbacks at 5 (`step-04-review.md:84`) |
| G5 5-section references | new idea | their 6-section `AGENTS.md` block is the *project index* shape; "prohibition names the alternative" (`template.md:12`) fits our Rules section |
| G6 coordinator + briefed workers | confirms | worker builds one named ticket, never picks next; orchestrator owns checkpoints (`autonomous-development-loops.md:13-17, 64-69`); brief = plan file only (`step-03:31`) |
| G4 plugins everywhere / tiers | confirms | skills via plugin marketplace on Claude Code + Codex, or `npx skills`; team vs personal override files (`install-bmad.md:28-42`) |
| Q-11 agent side vs project side | confirms | persona in shipped TOML; project facts via `persistent_facts` file refs in a committed override, not in the persona |

## 2.6 Adopt / adapt / reject

| # | Call | What | Shows it |
|---|---|---|---|
| 1 | ADOPT | triage step for QA output: re-verify each finding, verdict `high/medium/low/false/maybe-false`, log every one, reviewer severity ignored | `step-04-review.md:53-75` |
| 2 | ADOPT | four deletion grounds + "no rule in two loaded files" for the R1 de-dup work | `best-practices.md:75-82`; `SKILL.md:95` |
| 3 | ADOPT | claims-last: reviewer reads the MR description / REQ only after tracing the diff | `claims-check.md:3-5` |
| 4 | ADOPT | brief = one file; dispatch never restates it | `step-03-implement.md:31-33` |
| 5 | ADAPT | `<frozen-after-approval>` block in the REQ/design: what `/approved` locks; only the human edits it | `plan-template.md:21-50` |
| 6 | ADAPT | route findings `intent_gap → analyst`, `bad_plan → design`, `patch → developer`, `defer → issue` | `step-04-review.md:78-103` |
| 7 | ADAPT | role file = 4 fields + menu of skills; name locked, team/personal overrides | `bmad-agent-dev/customize.toml:1-81` |
| 8 | ADAPT | fixes touching `AGENTS.md`/rules are deferred, never auto-patched by review | `step-04-review.md:82` |
| 9 | REJECT | copied activation boilerplate per agent and copied review prompts per workflow — both already drifted | dev vs analyst `SKILL.md`; `review-prompts/*` diff |
| 10 | REJECT | always-in-character personas with icons and voices for workers that never talk to a human | `bmad-agent-dev/SKILL.md:43, 57-59` |
| 11 | REJECT | "find at least N issues" floors; they inflate findings we then pay to triage | `customize.toml:129`; `lens-adversarial.md:5` |

---

# 3. Files actually read

spec-kit (`SK/`):
`AGENTS.md` · `.specify/memory/constitution.md` (1-150) · `templates/constitution-template.md` ·
`templates/plan-template.md` (1-60) · `templates/tasks-template.md` (1-60) · `templates/commands/specify.md` ·
`templates/commands/plan.md` · `templates/commands/analyze.md` · `templates/commands/implement.md` (1-200) ·
`templates/commands/converge.md` · `templates/commands/checklist.md` (1-200) · `templates/commands/constitution.md` (56-140) ·
`templates/commands/clarify.md` (129-200) · `presets/lean/commands/speckit.implement.md` · `presets/ARCHITECTURE.md` (1-80) ·
`workflows/ARCHITECTURE.md` (1-120) · `workflows/speckit/workflow.yml` · `workflows/bugfix/workflow.yml` ·
`design/integration.md` · `docs/guides/agentic-sdlc.md` · `examples/bundles/{developer,product-manager,business-analyst,security-researcher}/{README.md,bundle.yml}` ·
`.github/workflows/bug-fix.md` (1-110) · `.github/workflows/bug-test.md` (1-130) · `integrations/catalog.json` (keys) · `pyproject.toml` (version)

BMAD (`BM/`):
`AGENTS.md` · `CHANGELOG.md` (1-60, 381-400, grep hits) · `skills/bmod-method/roster.toml` · `skills/bmod-method/retired.toml` ·
`skills/bmad-agent-dev/{SKILL.md,customize.toml,bmod.toml}` · `skills/bmad-agent-analyst/customize.toml` (36-103) + `SKILL.md` (diff) ·
`skills/bmad-build/{SKILL.md,workflow.md,step-01-clarify-and-route.md,step-02-plan.md,step-03-implement.md,step-04-review.md,step-05-present.md,customize.toml,plan-template.md (1-60)}` ·
`skills/bmad-build/references/{claims-check.md,deletion-check.md}` · `skills/bmad-build/review-prompts/*` (diff vs code-review) ·
`skills/bmad-code-review/{workflow.md,step-01..04}` · `skills/bmad-code-review/review-prompts/verification-gap.md` ·
`skills/bmad-review/{SKILL.md,references/lens-adversarial.md}` · `skills/bmad-project-context/{SKILL.md,references/template.md,references/best-practices.md}` ·
`skills/bmad/{SKILL.md,references/setup.md}` · `skills/bmad/scripts/render_skill.py` (1-45) · `skills/bmad-build-auto/workflow.md` (1-40) ·
`skills/bmad-party-mode/SKILL.md` (1-30) · `docs/start/install-bmad.md` · `docs/customize/adopt-bmad-across-a-team.md` (1-80) ·
`docs/build/autonomous-development-loops.md` (1-80) · `web-bundles/README.md` (1-20)

Context (`.scratch/one-rulebook/`): `map.md` · `requirements.md` · `design-overview.md`
