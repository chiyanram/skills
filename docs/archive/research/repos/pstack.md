# pstack: per-repo deep report (one-rulebook map, 2026-10-01)

Root: `refs/cursor-plugins/pstack/` (all paths below are relative to it). HEAD `2eb7ed46`, 2026-09-30.

## 1. What it is

| | |
|---|---|
| What | A Cursor plugin by Lauren Tan (poteto). Skills + 2 subagents + 1 dormant automation pack |
| Version | `0.15.5` (`.cursor-plugin/plugin.json:4`) |
| Stars | unknown (it lives inside the `cursor/plugins` monorepo, `plugin.json:9-10`) |
| Maturity | High for its harness. Versioned, has a 10-page guide, bun-tested TS tooling (`scripts/orch/orch.test.ts`, `watch-pr/*.test.ts`). Cursor-only |
| The one idea | **One mode skill routes every task to a playbook whose steps are copied verbatim into the todo list; principles are named, short, single-rule skills the playbooks cite by name.** "Words carry the intent, the skill carries the rigor" (`docs/guide/02-poteto-mode.md:54`) |

## 2. File tree (what matters)

```
pstack/
├─ .cursor-plugin/plugin.json        manifest: skills dir + agents dir, nothing else
├─ README.md                         install, playbook + skill + principle tables
├─ agents/
│  ├─ poteto-agent.md                9 lines: "read poteto-mode SKILL.md in full first"
│  └─ comment-sicko.md               read-only comment reviewer persona, keep-list leash
├─ skills/
│  ├─ poteto-mode/                   THE ROUTER (143-line SKILL.md)
│  │  ├─ SKILL.md                    Non-negotiables · Principles index · Autonomy · Subagents · Reply · Playbooks
│  │  ├─ playbooks/*.md (23)         bug-fix, feature, refactoring, orchestrate, autopilot-*, shipping, babysit…
│  │  ├─ references/bugbot-triage.md fix/dismiss/ask rubric + learned-pattern format
│  │  └─ scripts/                    orch/ (coordinator store CLI), watch-pr/ (forge watcher), check-plan.mjs
│  ├─ interrogate/                   multi-model adversarial review + rubric + code-quality lens + lead judgment
│  ├─ arena/ · swarm/ · architect/   fan-out primitives (bakeoff+graft · slices/races · design-twice)
│  ├─ how/ · why/ · teach/ · recall/ · blast-radius/   understanding skills (why = 7 evidence categories)
│  ├─ reflect/                       3 transcript reviewers + synthesizer → skill edits, human approves
│  ├─ automate-me/                   mine transcripts → personal <name>-mode skill
│  ├─ setup-pstack/                  writes ~/.cursor/rules/pstack-models.mdc (per-machine model roles)
│  ├─ show-me-your-work/             decisions.tsv trail + log.sh + cross-model audit
│  ├─ figure-it-out/                 designs a bespoke playbook when none fits
│  ├─ unslop/ · technical-writing/ · no-comments/ · tdd/ · bro/
│  ├─ create-/maintain-verification-skill/   generate + upkeep a project-local verify-<app> skill
│  ├─ typescript-best-practices/     only skill with `paths:` (auto-loads on .ts/.tsx)
│  └─ principle-*/ (23)              one rule each, 16-34 lines
├─ automations/benny/                dormant Slack triage + repro/fix pack, copied into target repo
└─ docs/guide/01..10                 Diátaxis tutorial; prompts to copy; pitfalls
```

## 3. Approach, section by section

### a. Rules / standards

| Aspect | What pstack does | Evidence |
|---|---|---|
| Where rules live | Each principle is its own skill, one rule per file, uniform shape: rule sentence · **Why** · **Pattern** · **The test** / **Stop** · when it applies / doesn't | `skills/principle-boundary-discipline/SKILL.md:9-34`, `principle-attack-the-premise/SKILL.md:9-23` |
| Single source | The router holds a one-line **index** per principle (trigger + gist) and says "Read the leaf skill in full for any principle you apply" | `poteto-mode/SKILL.md:37-77` (line 39) |
| Cross-reference not restate | Principles link each other by relative path; playbooks cite principles by bold name | `principle-build-the-lever/SKILL.md:21-23`; `playbooks/refactoring.md:7-14` |
| Proof of application | "Cite only principles whose leaf SKILL.md you read this session" + name the decision each changed | `poteto-mode/SKILL.md:15`; `docs/guide/08-principles.md:27` |
| Always vs on demand | Every skill has `disable-model-invocation: true` (never auto-fires). The router is a **sticky mode** (`mode: true`, `reminder:` line) | `poteto-mode/SKILL.md:4-8` |
| Path-scoped | Only `typescript-best-practices` uses `paths: ["**/*.ts","**/*.tsx"]` | `typescript-best-practices/SKILL.md:4` |
| Rule → mechanism | "Pick the strongest mechanism": unrepresentable state > lint/CI > canonical helper > runtime check | `principle-encode-lessons-in-structure/SKILL.md:19-21` |
| Lint for its own prose | `check-plan.mjs` fails a plan on long dash, curly quote, mid-sentence colon, missing sub-blocks | `poteto-mode/scripts/check-plan.mjs:5-61` |

Note: pstack has **no project-rules layer**. It is entirely agent-side; project facts come from the repo's own `AGENTS.md` ("pre-review checks that the repo's AGENTS.md files and rules name for the touched paths", `playbooks/autopilot-full.md:6`).

### b. Process / workflow

```
 prompt ─► poteto-mode (sticky)
            │ read Principles index (always)
            ▼
        match playbook (23) ──none fits / large──► figure-it-out (designs a bespoke one)
            │                 ──program-scale────► orchestrate
            ▼
        todo list = playbook steps COPIED VERBATIM; skipped step stays as "skip: <reason>"
            │ steps fire skills by name: how · architect(arena) · interrogate · tdd · unslop · no-comments
            ▼
        every playbook ends ─► Opening a PR ─► (only when asked) Babysit ─► Shipping
```

| Aspect | Detail | Evidence |
|---|---|---|
| Routing by task type | 23 playbooks, each one line in the router with trigger phrases | `poteto-mode/SKILL.md:115-143` |
| Verbatim copy | "Open a todolist whose first items are the matched playbook's steps, copied in verbatim … A step you choose not to do stays in the list with a one-line `skip: <reason>`" | `poteto-mode/SKILL.md:117` |
| Playbook shape | Title · one bold **ownership line** ("You own the design. Plan, review, verify.") · numbered steps · **Reply:** contract | `playbooks/feature.md:1-21`, `bug-fix.md:3`, `orchestrate.md:3` |
| Human gates | Autonomy: reversible proceeds; "Always pause for irreversible writes"; explicit session overrides | `poteto-mode/SKILL.md:79-87` |
| Ask-or-test | Before asking a "which approach" fork, classify: an observable fact → prototype, not a question | `poteto-mode/SKILL.md:20` |
| Babysit ≠ merge | Babysit stops at merge-ready; only explicit "land/ship" routes to Shipping | `playbooks/babysit.md:23-25` |
| State-then-wait | "a request to state the plan is not a go"; execution only on explicit go, then `/goal` armed | `playbooks/autopilot-stack.md:7`, `autopilot-full.md:5` |
| State on disk | `decisions.tsv` (append-only, superseding rows); orchestrate store `preferences.md`, `units.tsv`, `ledger.tsv`, `frontier.json`, `inbox/`, `gates.md`, derived `status.md`; every file one writer | `show-me-your-work/SKILL.md:13-52`; `playbooks/orchestrate.md:21-32` |
| Pause / pickup | `wip:` commit + resume note off-context; pickup treats prior trail as authoritative, no redo | `playbooks/pause-safely.md:5-8`; `session-pickup.md:6-7` |
| Self-reread from trunk | Each audit tick runs `git show origin/main:…/autopilot-full.md` and re-reads the armed `/goal` | `playbooks/autopilot-full.md:10` |

### c. Roles / personas / agents

| Kind | Made of | Who writes | Can change? | Evidence |
|---|---|---|---|---|
| `poteto-agent` | 9 lines: frontmatter + "read poteto-mode SKILL.md in full before any work" | author | edit file | `agents/poteto-agent.md:1-9` |
| `Comment Sicko` | voice + keep-list "leash" + output contract; report only, never writes app code | author | edit file | `agents/comment-sicko.md:12-32` |
| Personal mode | `<handle>-mode/SKILL.md`, **mined** from transcripts (3 slices, signal kept only if in 2+ slices) + AskQuestion | `/automate-me` | update mode mines since last edit | `automate-me/SKILL.md:15-40, 85-92` |
| Review "roles" | **None by persona.** "The adversarial signal comes from model diversity, not assigned personas" | — | — | `interrogate/SKILL.md:9` |
| Program roles | Coordinator (never edits code) · sub-coordinator (per track, cap ~10 children) · worker/verifier (cloud, verifier on a different model family) | playbook | — | `playbooks/orchestrate.md:13-19` |
| Playbook ownership | Each playbook's bold line names what the agent owns ("You own the verdicts, never the PRs") | playbook | — | `playbooks/autopilot-full.md:3` |

Key point: an agent's identity is just "load this skill first" (`poteto-agent.md:9`). The persona file holds no rules.

### d. Review & verification

| Mechanism | Shape | Evidence |
|---|---|---|
| `interrogate` inputs | intent paragraph (ask user if unsure) + diff + rubric + code-quality lens, **same filled template to every reviewer** | `interrogate/SKILL.md:23-57` |
| Reviewers | one per configured model (default 3 families), `readonly: true` | `interrogate/SKILL.md:36-47` |
| Criteria | fixed generic lenses: Correctness · Root causes · Structural integrity · Verification · Complexity budget · Security; "Review through whichever lenses are relevant" | `interrogate/references/rubric.md:1-77` |
| Code-quality lens | "code judo" + 7 dimensions + **approval bar** (presumptive blockers, e.g. file crossing 1k lines) | `references/code-quality-review.md:21-43` |
| Finding format | Severity critical/warning/nit · Location · Finding · Evidence · Suggestion; "An empty review is a valid outcome" | `references/reviewer-prompt.md:33-70` |
| Lead judgment | Act on / Consider / Noted / Dismissed; filters: nitpick gravity, hypothetical vs actual, "I would have done it differently"; **>5 Act-on means not filtering hard enough**; Dismissed = trust mechanism | `references/lead-judgment.md:18-58` |
| Independence | "Safe means a verdict from an agent that did not write the code. CI green is not a verdict" | `playbooks/shipping.md:7` |
| Verdict ↔ patch | Verdict keyed to head SHA + `git patch-id`; rebase with unchanged patch-id keeps the code verdict | `playbooks/shipping.md:9` |
| Rounds | New head → fresh swarm verdict; every proven finding goes back in one fix-forward; "A defect that a lane filed as a note is a finding"; behavior finding → red test covering every site; defect added to next round's brief | `playbooks/autopilot-full.md:8` |
| Swarm lanes | PASS / ISSUES / BLOCKED; result missing its SHAs is dropped and rerun once; a gap ≠ pass | `swarm/SKILL.md:34-42` |
| Ledger | `live-ui-verified | unit-test-verified | type-check-only | verifier-blocked | verifier-failed`, keyed PR+SHA | `playbooks/orchestrate.md:89` |
| Cost control | Scale verification to the unit: "A verifier agent whose entire product would be rerunning one command is ceremony" | `playbooks/orchestrate.md:87` |
| Bot comments | fix / dismiss / ask; learned dismissal patterns with Confidence candidate→recurring→strong; security/data/migration never auto-skipped | `poteto-mode/references/bugbot-triage.md:7-84` |
| Comments | separate reviewer, "not from the agent that wrote them" | `docs/guide/05-build-and-clean.md:63`; `no-comments/SKILL.md:19-24` |

No round cap in `interrogate`. No path-based criteria selection anywhere. Cost is not a design constraint: 3-model panels by default, 10 live lanes per PR in plans (`playbooks/multi-phase-plan.md:13`).

### e. Context engineering

| Technique | Evidence |
|---|---|
| Bulk to subagents, summaries in main thread | `principle-guard-the-context-window/SKILL.md:14-16` |
| "Keep frequently used content inline" (templates used every call live in the skill) | same file `:15` |
| File pointers, not inlined context, in every Task | `poteto-mode/SKILL.md:93` |
| **Brief is the product**; 9-field template; missing field = refuse to spawn | `playbooks/orchestrate.md:34-56` |
| Standing orders pasted verbatim into every spawn and resume ("Directives decay across resumes") | `playbooks/orchestrate.md:25` |
| Never resume-chain; respawn fresh with consolidated scope | `poteto-mode/SKILL.md:95`; `orchestrate.md:56` |
| Completions are queue events; drain at 4 points; never review a diff inside a drain | `playbooks/orchestrate.md:70-75` |
| Liveness by side effects only, never by resuming an agent | `playbooks/orchestrate.md:95` |
| State CLI: "one command in and one line out. The CLI never spawns" | `playbooks/orchestrate.md:15`; `scripts/orch/orch.ts:1-80` |
| Untrusted transcript / review-comment text treated as data | `reflect/references/judgment-reviewer.md:5`; `playbooks/babysit.md:12` |

### f. Packaging & distribution

| Aspect | Detail | Evidence |
|---|---|---|
| Unit | One Cursor plugin: `"skills": "./skills/"`, `"agents": "./agents/"` | `.cursor-plugin/plugin.json:29-30` |
| Install | `/add-plugin pstack` | `README.md:17-19` |
| Per-machine config | `~/.cursor/rules/pstack-models.mdc`, `alwaysApply: true`, one line per role; a missing line = skill default; rewritten whole for idempotence | `setup-pstack/SKILL.md:8, 37-66` |
| Defaults live in skills | every skill carries its own default table; rule only overrides | `interrogate/SKILL.md:36-42`; `README.md:249` |
| Project-scope enablement | benny pack copied into `.cursor/automations/benny/`; pstack enabled via committed `.cursor/settings.json`; user config kept **outside** the pack so refreshes never overwrite it | `automations/benny/FOR_AGENTS.md:31-34, 67-81` |
| Deps it does not bundle | `deslop`, `control-ui/cli` from `cursor-team-kit` (another plugin) | `README.md:229-237` |
| Multi-harness | **No.** Task tool, `readonly`, `environment: "cloud"`, `/loop`, `AskQuestion`, `create-skill` are Cursor-specific | `swarm/SKILL.md:30`; `poteto-mode/SKILL.md:93` |
| Script deps | bun + frozen lockfile, self-installing bootstrap keyed by sha256 of package.json+lock | `poteto-mode/scripts/bootstrap.ts:17-61` |

### g. Hosting / UI

No daemon or protocol. Long runs use Cursor `/loop` + cloud agents (`playbooks/autonomous-run.md:6`). `make-bot-ui` builds a local page that POSTs to a Cursor webhook routine; sender key stays server-side (`make-bot-ui/SKILL.md:1-40`). benny = Cursor automations on Slack triggers, coordinator is the only Slack poster, children forbidden Slack writes (`automations/benny/skills/reproduce-and-fix-issues/SKILL.md:16-25`). Approvals are chat text plus `gates.md` entries with a default (`playbooks/orchestrate.md:30, 105`).

## 4. Three excerpts worth studying

| # | Where | Why it is good |
|---|---|---|
| 1 | `skills/poteto-mode/playbooks/orchestrate.md:34-56` (the brief) | Nine fields, each one checkable; "A field you cannot fill is a unit you have not scoped yet"; missing fields refuse the spawn; brief sized to the unit; sampled brief audit runs beside the wave, not in front of it. This is the closest existing text to our G6 brief template. |
| 2 | `skills/interrogate/references/lead-judgment.md:16-58` | Names the four false-positive families (nitpick gravity, hypothetical, premature abstraction, "I would have done it differently") and the calibration cap ">5 Act on = not filtering". Already adopted in G3; the "Dismissed is a trust mechanism" line (`:58`) is the reason to keep dismissals in our output. |
| 3 | `skills/reflect/references/synthesizer.md:13-46` | The lesson-loop gate: durability, specificity, existing-skill-first, convergence, decision-changing, **structural-mechanism check → Backlog**, skill-was-used, already-covered. One-sentence cells, user approves row by row. A ready answer to R8's "no lesson loop" risk (D2). |

Runner-up: `skills/poteto-mode/SKILL.md:117`, the verbatim-copy + `skip: <reason>` rule. It answers R2 (skills fire when a stage orders them) with one sentence.

## 5. Against our decisions

| Decision | Verdict | pstack evidence | Note |
|---|---|---|---|
| G1 rules layers (AGENTS.md index, bodies on demand, upstream as plugins) | **Confirms** | index inline + "read the leaf in full" `poteto-mode/SKILL.md:37-39`; plugin-only distribution `plugin.json:29-30`; `paths:` for language rules `typescript-best-practices/SKILL.md:4` | pstack has no project layer at all; it relies on the repo's AGENTS.md (`autopilot-full.md:6`). Matches our agent-side/project-side split (Q-11) |
| G1 "~7 domain skills" | **New idea** | 23 principles, one rule per file, 16-34 lines, uniform Why/Pattern/Test | Our domain skills could keep a principle-sized leaf per rule rather than one big file |
| G2 one crq + role labels | **Partly contradicts** | 23 task-type playbooks, not one pipeline `poteto-mode/SKILL.md:121-143`; no roles, but an **ownership line** per playbook (`feature.md:3`) | Fits "Not yet specified: pstack-style routing by task type" in map.md. Adopt the ownership line as the stage's role line |
| G2 "stage orders the skill" | **Confirms** | steps copied verbatim to todo, `skip: <reason>` kept `poteto-mode/SKILL.md:117`; guide pitfall: don't enumerate skills in the prompt `docs/guide/02-poteto-mode.md:94` | Strong backing for Q-4 |
| G3 Standards ‖ Spec, fresh read-only, lead judgment | **Confirms** lead judgment, read-only, independence; **contradicts** axis split | same prompt to all; diversity by model, "not assigned personas" `interrogate/SKILL.md:9`; generic lenses, no path selection `rubric.md:3` | Our single-model setup cannot buy diversity from models, so axes are the substitute. Keep G3 |
| G3 3-round cap | **New idea (rounds keyed to SHA)** | fresh verdict per changed head; patch-id reuse; "defect filed as a note is a finding"; next round's brief carries the defect `autopilot-full.md:8`, `shipping.md:9` | Gives the round loop a precise "what re-runs" rule |
| G5 5-section references | **Confirms** "checks at the end" | every principle ends in "The test:" or "Stop:" (`principle-boundary-discipline/SKILL.md:32-34`); approval bar at end of lens `code-quality-review.md:41-43` | bugbot-triage pattern format (Skip when · Do not skip when · Example · Source · Confidence) is a model for **Decided edges** |
| G6 coordinator + briefed workers | **Confirms strongly** | coordinator never edits code; brief template; standing orders verbatim; never resume-chain; liveness by side effects; gates.md with default `orchestrate.md:13-109` | **Contradicts** interactive workers: "a worker cannot ask you a question" `orchestrate.md:11`. G6 workers are interactive tmux windows; pstack's are fire-and-report with TIMEBOX |
| G6 "relay every question with context" | **Confirms** | `gates.md` = question, options, default on no answer; escalate only irreversible / product calls; batched `orchestrate.md:30, 105-107` | Same shape as the operator's decision format |
| G4 plugins everywhere + one machine file | **Confirms** | one plugin; `~/.cursor/rules/pstack-models.mdc` with defaults in skills, override only what differs `setup-pstack/SKILL.md:8, 41-47` | User config outside the copied pack `benny/FOR_AGENTS.md:34` matches "one machine file" |
| G4 coordinator-as-contract + adapters | **Confirms** | `orch` CLI is the coordinator's state contract, never spawns `orchestrate.md:15`; forge adapter "resolve once, gh default, origin if present" `opening-a-pr.md:25` | |
| G4 tiers | **New idea (model tiers by role)** | code / hardest / judgment roles + budget ladder `poteto-mode/SKILL.md:93`, `setup-pstack/SKILL.md:22-29` | Our tiers are deployment tiers; pstack's are model-cost tiers. Both can coexist |

## 6. ADOPT / ADAPT / REJECT (ranked)

| Rank | Call | What | File that shows it |
|---|---|---|---|
| 1 | ADOPT | crq stage text copied **verbatim** into the todo list; a skipped step stays with `skip: <reason>` | `skills/poteto-mode/SKILL.md:117` |
| 2 | ADOPT | Brief template fields + "missing field = refuse to spawn" + standing orders pasted verbatim + never resume-chain | `skills/poteto-mode/playbooks/orchestrate.md:25, 34-56` |
| 3 | ADOPT | Verdict keyed to head SHA (+ patch-id reuse); a note that proves a defect is a finding; next round's brief carries prior defects | `playbooks/autopilot-full.md:8`; `playbooks/shipping.md:9` |
| 4 | ADOPT | Reflect synthesizer criteria as our lesson loop (D2), incl. the "could a mechanism enforce it → Backlog" check and human approval per row | `skills/reflect/references/synthesizer.md:13-46`; `reflect/SKILL.md:49-53` |
| 5 | ADAPT | One **ownership line** per crq stage ("You own the spec, not the code") as the role label's text | `playbooks/feature.md:3`, `orchestrate.md:3` |
| 6 | ADAPT | "Cite only principles you read this session; name the decision it changed" as the proof a reference was applied (cheaper than per-criterion receipts) | `skills/poteto-mode/SKILL.md:15`; `docs/guide/08-principles.md:27` |
| 7 | ADAPT | bugbot-triage learned-pattern format (Skip when / Do not skip when / Confidence) for G5 **Decided edges** | `skills/poteto-mode/references/bugbot-triage.md:15-29` |
| 8 | ADAPT | Escalation split: what reaches the human vs never; park as gate with a default | `playbooks/orchestrate.md:103-109` |
| 9 | ADAPT | Lint our own prose/plans (like `check-plan.mjs`) instead of more review text | `skills/poteto-mode/scripts/check-plan.mjs:5-61` |
| 10 | ADAPT | Ask-or-test rule: an observable fact goes to a prototype, not a question to the operator | `skills/poteto-mode/SKILL.md:20` |
| 11 | ADOPT (later) | `show-me-your-work` append-only TSV with superseding rows for long fleet runs | `skills/show-me-your-work/SKILL.md:13-52` |
| 12 | REJECT | 3-model panels and 10 live lanes per PR as defaults. Our R4 budget (~$2–2.8/review) cannot carry it | `interrogate/SKILL.md:38-42`; `playbooks/multi-phase-plan.md:13` |
| 13 | REJECT | Generic lenses only, no path-selected criteria (already rejected as direction A) | `interrogate/references/rubric.md:3` |
| 14 | REJECT | Cursor-only primitives (`environment: "cloud"`, `readonly`, `/loop`, `AskQuestion`). Fails Q-2 / S-8 | `skills/swarm/SKILL.md:30` |
| 15 | REJECT | "Never block on the human" as a default for /crq. Our human gates (`/approved`, merge) are by design | `principle-never-block-on-the-human/SKILL.md:13-20` |
| 16 | REJECT | `automate-me` personal mode mined from transcripts. Our souls are written deliberately (R8, Q-11) | `skills/automate-me/SKILL.md:27-40` |

## 7. Files actually read

```
.cursor-plugin/plugin.json
README.md
agents/poteto-agent.md
agents/comment-sicko.md
skills/poteto-mode/SKILL.md
skills/poteto-mode/playbooks/authoring-a-skill.md
skills/poteto-mode/playbooks/autonomous-run.md
skills/poteto-mode/playbooks/autopilot-full.md
skills/poteto-mode/playbooks/autopilot-stack.md
skills/poteto-mode/playbooks/babysit.md
skills/poteto-mode/playbooks/bug-fix.md
skills/poteto-mode/playbooks/eval.md
skills/poteto-mode/playbooks/feature.md
skills/poteto-mode/playbooks/hillclimb.md
skills/poteto-mode/playbooks/investigation.md
skills/poteto-mode/playbooks/multi-phase-plan.md
skills/poteto-mode/playbooks/opening-a-pr.md
skills/poteto-mode/playbooks/orchestrate.md
skills/poteto-mode/playbooks/pause-safely.md
skills/poteto-mode/playbooks/perf-issue.md
skills/poteto-mode/playbooks/prototype.md
skills/poteto-mode/playbooks/refactoring.md
skills/poteto-mode/playbooks/runtime-forensics.md
skills/poteto-mode/playbooks/session-pickup.md
skills/poteto-mode/playbooks/shipping.md
skills/poteto-mode/playbooks/trace-forensics.md
skills/poteto-mode/playbooks/visual-parity.md
skills/poteto-mode/playbooks/worktree-cleanup.md
skills/poteto-mode/references/bugbot-triage.md
skills/poteto-mode/scripts/check-plan.mjs (lines 1-80)
skills/poteto-mode/scripts/bootstrap.ts
skills/poteto-mode/scripts/package.json
skills/poteto-mode/scripts/orch/orch.ts (lines 1-80 + command list)
skills/poteto-mode/scripts/orch/store.ts (function index only)
skills/interrogate/SKILL.md
skills/interrogate/references/code-quality-review.md
skills/interrogate/references/lead-judgment.md
skills/interrogate/references/reviewer-prompt.md
skills/interrogate/references/rubric.md
skills/arena/SKILL.md
skills/swarm/SKILL.md
skills/architect/SKILL.md
skills/architect/references/design-red-flags.md
skills/architect/references/rationale-template.md
skills/architect/references/runner-prompt.md
skills/reflect/SKILL.md
skills/reflect/references/divergent-reviewer.md
skills/reflect/references/judgment-reviewer.md
skills/reflect/references/synthesizer.md
skills/reflect/references/tooling-reviewer.md
skills/automate-me/SKILL.md
skills/setup-pstack/SKILL.md
skills/figure-it-out/SKILL.md
skills/show-me-your-work/SKILL.md
skills/show-me-your-work/scripts/log.sh
skills/principle-*/SKILL.md (all 23)
skills/how/SKILL.md
skills/how/references/explainer-prompt.md
skills/how/references/explorer-prompt.md
skills/why/SKILL.md
skills/why/references/epistemics.md
skills/why/references/investigator-prompt.md (lines 1-40)
skills/why/references/synthesizer-prompt.md (headings)
skills/recall/SKILL.md
skills/blast-radius/SKILL.md
skills/teach/SKILL.md
skills/bro/SKILL.md
skills/no-comments/SKILL.md
skills/tdd/SKILL.md
skills/unslop/SKILL.md
skills/technical-writing/SKILL.md
skills/create-verification-skill/SKILL.md
skills/maintain-verification-skill/SKILL.md
skills/typescript-best-practices/SKILL.md
skills/make-bot-ui/SKILL.md (lines 1-40)
automations/benny/README.md
automations/benny/FOR_AGENTS.md
automations/benny/skills/reproduce-and-fix-issues/SKILL.md (lines 1-60)
docs/guide/README.md, 01-setup.md … 10-recipes-and-pitfalls.md (all 10)
```

Not read: `why/references/sources/*.md`, `typescript-best-practices/references/patterns.md`, `create-verification-skill/references/feature-map-example/*`, `watch-pr/*.ts`, `orch.test.ts`, benny setup/triage skills and templates, images.
