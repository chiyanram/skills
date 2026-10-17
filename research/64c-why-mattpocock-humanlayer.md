# 64c — Why mattpocock + HumanLayer do what they do (R38, map #9, chiyanram/skills#86)

Learn from references, don't follow them: they change. Per area: what each does **now**, its **own** stated
reason, and the stated reason for each change since our pin. No stated reason → "no stated reason" + **INFERENCE**.

| repo (tag) | pin | now (origin/main) | Δ |
|---|---|---|---|
| mattpocock/skills [matt] | `d81f3a1` (2026-09-29) | `49dd158` | 52 commits |
| humanlayer/skills [hl] | `ca7c808` | `653b641` | 24 commits, new `plugins/rpi` (PR #13) |
| humanlayer/advanced-context-engineering… [hl-ace] | `f2bc7ae` | `da16ab7` | new SlopCodeBench article |
| humanlayer/fold [hl-fold] | `864a60e` | `4bd8c58` | PRs #51 #52 #57 #61 #65 |

Cite shorthand: `M:` = mattpocock-skills, `H:` = humanlayer-skills, `F:` = fold, `A:` = ace repo; all at the "now" SHA above unless a SHA is given.

## D1 rule layers + loading

- **Does now**
  - [matt] `CLAUDE.md` is navigation + repo rules only; `AGENTS.md` is a one-word symlink-style pointer to it (`M:AGENTS.md:1`). Retro says CLAUDE.md is "used incredibly sparingly, usually only for navigation pointers" (`M:skills/engineering/retro/SKILL.md:41`).
  - [matt] Coding standards are a separate file "read during review, not implementation" (`M:…/retro/SKILL.md:42`).
  - [hl] rpi loads one phase's `process.md` per request; chart lives in a conditional reference (`H:plugins/rpi/skills/rpi/SKILL.md:20,24`).
  - [hl] rpi uses `<important if=…>` blocks to branch on harness capability (`H:…/rpi/SKILL.md:65-77`).
- **Why**
  - [matt] Two budgets: context load (always-loaded, costs every turn) vs cognitive load (human is the index) (`M:skills/productivity/writing-for-agents/SKILL.md:24-27`).
  - [matt] Implementation agent has "the most context pressure"; reviewer has least → standards belong to review (`M:…/retro/SKILL.md:31-35`).
  - [hl] Chart kept in a conditional reference so users compare flows "without loading it for every phase" (commit `8276a26`).
- **Changed since pin**
  - [matt] `.out-of-scope/lazy-load-writing-for-agents.md` (PR #1240): retro loads `writing-for-agents` on **every** run. Why: it is the yardstick for judging steering files; lazy load means candidates "get judged with no yardstick" (`M:.out-of-scope/lazy-load-writing-for-agents.md:7`). PR #1240 why: so triage closes repeats instead of re-arguing.
  - [matt] `ask-matt` must read a skill's SKILL.md before asserting what it does; summaries are "for orientation only" (`M:skills/engineering/ask-matt/SKILL.md:11`, commit `954ee7f`). No stated reason in commit body → **INFERENCE**: router summaries drifted from skill bodies.
- **Underlying need**: always-loaded text must be tiny; the rest loads at the step that needs it, and a judge loads its yardstick before judging.

## D2 skill/reference format + how rules are sourced/edited

- **Does now**
  - [matt] Every promoted skill = SKILL.md + README entry + plugin.json + docs page; user- vs model-invoked declared explicitly (`M:CLAUDE.md:9,17,19`). No em-dashes (`M:CLAUDE.md:25`).
  - [matt] Hard vs soft setup dependency: only hard deps carry the setup pointer (`M:.agents/adr/0001-…md:7-10`). Why: keeps soft skills "token-light", avoids cargo-culting.
  - [matt] Fixes land only with an **observed failure** + fits philosophy (`M:SCOPE.md:9-10`). Every PR since pin has a Before/After **Evidence** block and **Merge Danger: Door/Blast Radius** (`M:skills/engineering/pr/SKILL.md:21-30`).
  - [hl] rpi = router SKILL.md + `references/<phase>/process.md` + templates + `final_answer` templates (PR #13 change outline). Subagent instructions mirrored for hosts without named agents (`H:…/rpi/SKILL.md:65-77`).
  - [hl-fold] Vendored lint rules each pinned to source repo + SHA in a table (`F:tools/oxlint/README.md`).
- **Changed since pin**
  - [matt] `SCOPE.md` + `.out-of-scope/` + issue forms (PR #1179). Why: "so `/triage` and human reporters work to the same rules". Each record = scope statement + "Why" + prior requests.
  - [matt] `new-skills.md`: no new skills. Why: each skill is "permanent maintenance surface"; "if you can compose the behaviour from existing skills, it doesn't get a new skill" (`M:.out-of-scope/new-skills.md:7,9`).
  - [matt] `harness-name-collisions.md`: never rename to dodge a harness built-in. Why: "chasing a moving target" across harnesses (`M:.out-of-scope/harness-name-collisions.md:7`).
  - [matt] `docs: unslop every docs page` (PR #1168): applied cursor `unslop` rules. Stated why: so published pages "read as plain prose".
  - [matt] Skill-to-skill calls reworded to "Call the Skill tool with …" (implement, commit `e48341a`). No stated reason in commit body → **INFERENCE**: `/tdd` prose was not reliably triggering the skill.
  - [hl] rpi made portable across Claude Code + Codex (PR #13). Why: "usable in Claude Code and Codex without HumanLayer-specific services". Research agents kept "verbatim" (commit `6148793`); static checks + live Codex fixture tests added (`04ecf04`, `scripts/test-rpi-workflows.ts`).
  - [hl-fold] PR #51: 5 vendored rules left **off** "because Fold code still violates them", with violation counts (`F:tools/oxlint/README.md:24-26`). `no-comments` "intentionally off": no stated reason → **INFERENCE**: comments carry Effect rationale.
- **Underlying need**: a rule changes only on evidence of a real failure, and every rejection is written down once so it is not re-litigated.

## D3 orchestration

- **Does now**
  - [matt] wayfinder: map of decision tickets; HITL vs AFK per ticket; "never resolve more than one ticket per session", except research (`M:skills/engineering/wayfinder/SKILL.md:75,105`).
  - [matt] code-review runs 2 axes as parallel sub-agents "so they don't pollute each other's context" (`M:skills/engineering/code-review/SKILL.md:11`).
  - [hl] rpi: one phase per context window by default; documents carry state (`H:…/rpi/SKILL.md:57`; `…/references/workflow.md:55`).
  - [hl] research fans out 2–6 read-only subagents, waits for all before synthesis (`H:…/create-research/process.md:17,34`).
- **Changed since pin**
  - [matt] **chief-of-staff** (in-progress, commits `e47c149`…`6fd9479`, no PR, no commit bodies): DRI for a long goal; "All work should be done in subagents. Protect your context window." (`M:skills/in-progress/chief-of-staff/SKILL.md:20`); background agents "so you can stay in active dialogue" (`:22`); talk via **context pointers** (`:24`); FIRST improve the environment, "pit of success" (`:28-32`); "no workarounds" (`:40-43`). Reasons are the in-text ones; no PR/issue → commit-level why: **no stated reason**.
  - [matt] `subagent-recursion.md` (PR #1190): skills add no recursion/depth guards. Why: "The harness should be responsible for stopping infinite subagent loops"; a prose guard "covers only that skill, costs tokens on every run" (`M:.out-of-scope/subagent-recursion.md:7`).
  - [hl] 4 flows, chosen by the user (`H:…/rpi/SKILL.md:18`). Why: "Use the shortest path that gives the user useful review points" (`H:…/references/workflow.md:3`); per-flow fit: design discussion = few clear options, PRD→TDD = open product questions, TDD = fixes/refactors, research-only = no design needed (`workflow.md:34-37`).
  - [hl] Implementation can start from any step (commits `a8959fb`, `3b53bed`). Why: skip "once a phase document specifies the task well enough".
- **Underlying need**: the orchestrator's context is the scarce resource; workers get pointers, not pasted context, and the path length matches the task.

## D4 brief + handoff record

- **Does now**
  - [matt] wayfinder map is "an index, not a store"; a decision lives in one ticket (`M:…/wayfinder/SKILL.md:23`). Humans see names, never bare ids (`:17`).
  - [matt] code-review sub-agent briefs are fixed text with word caps (`M:…/code-review/SKILL.md:62-72`).
  - [hl] rpi docs are numbered `NN-` files, frontmatter `repos: [{identifier, sha}]` (`H:…/rpi/SKILL.md:51-53`); next command carries task dir + chosen flow (`workflow.md:55-62`).
  - [hl] implementer reads docs itself; precedence "outline > TDD > PRD > design discussion > research > original request" (`H:…/implement-outline/process.md:11,17`).
- **Changed since pin**
  - [matt] `/implement` fetches a passed ticket and states its title (PR #1196). Why: in #700 a bare `#2` bound "to whichever numbered list is nearest in context, silently".
  - [matt] wayfinder: real ids only, no placeholder `#<n>` (PR #1181, #507): placeholders auto-linked to unrelated issues.
  - [matt] wayfinder: read the ticket's type **label**, not just the body (PR #1181, #625): Codex read body only and solved a HITL grilling ticket alone.
  - [matt] handoff: summary passed via temp file to `claude --bg` (commit `07b7105`). Why (in SKILL text): keeps the shell from running backticks or expanding `$` (`M:skills/in-progress/claude-handoff/SKILL.md:8`).
  - [hl] Task directory reused if obvious, asked only if ambiguous (commit `ada4a55`).
  - [hl] Artifacts in `.agents/artifacts/`, **not committed**: "The RPI framework authors recommend not committing the artifacts" (`H:…/rpi/SKILL.md:49`); commit `ada4a55`: "without requiring ignore-rule changes". **No stated reason** for not committing. **INFERENCE**: artifacts are working state per session; the PR, not the artifact, is the durable record.
- **Underlying need**: a handoff names exact identity (fetched ticket, SHA, path) so the next agent can't bind to the wrong thing.

## D5 human channel, escalation, status

- **Does now**
  - [matt] grilling asks the whole frontier per round, each with a recommended answer; facts are the agent's job, never the user's (`M:skills/productivity/grilling/SKILL.md:8,28`); done only when user confirms (`:30`).
  - [hl] create-tdd: "one decision per message, then wait" (`H:…/create-tdd/process.md:27`).
  - [hl] implementer on mismatch: STOP, report Expected/Found/Why this matters, ask (`H:plugins/rpi/agents/outline-implementer-agent.md:30-42`).
- **Changed since pin**
  - [matt] grilling: "Word each question so 'yes' accepts your recommended answer" (PR #1193, #706). Why: agreeing meant answering "No, but yes to the recommendation".
  - [matt] tdd: each proposed seam gets a note on what it catches/misses (PR #1192, #607). Why: user was asked to choose between seams "named only by label".
  - [matt] `native-question-tool.md`: grilling stays plain chat. Why: skills are harness-neutral, and pickers push "multiple-choice questions with pre-baked answers" (`M:.out-of-scope/native-question-tool.md:7,9`).
  - [matt] `question-limits.md` (unchanged since pin): no question cap. Why: too-many vs low-value questions are different failures; low-value is "a prompt-quality issue" (`M:.out-of-scope/question-limits.md:14`).
  - [hl] Flow choice shown as box-drawing chart, not Mermaid (commits `4400d10`, `9454f32`): "so users can see the four paths… before choosing".
  - [hl] Offer to open each doc in the user's editor at every review point (`create-tdd/process.md:35`). No stated reason.
- **Underlying need**: the human's answer must be cheap (yes = accept), informed (tradeoff per option), and asked in the human's own words.

## D6 review

- **Does now**
  - [matt] 2 axes (Standards, Spec) + fixed Fowler smell baseline; repo standard overrides baseline; smells are always judgement calls (`M:…/code-review/SKILL.md:38-41`). Never rerank across axes (`:78-80`). Why: "Reporting them separately stops one axis from masking the other" (`:89`).
  - [matt] Refactoring belongs to review, not the red→green loop (`M:skills/engineering/tdd/SKILL.md:38`).
  - [hl] research/analyzer agents document only: "DO NOT suggest improvements" (`H:plugins/rpi/agents/codebase-analyzer.md:10-11`).
- **Changed since pin**
  - [matt] PR #1208: standards = **search** for every standards file; `CODING_STANDARDS.md`/`CONTRIBUTING.md` must be included. Why (#1065): the agent listed files "from memory", so a root standards file never reached the reviewer.
  - [matt] PR #1208: both sub-agents "together, in the foreground". Why (#1073): a Sonnet run backgrounded them and aggregated "before their reports arrived".
  - [matt] PR #1208: tracker doc path no longer hard-coded (#937): broke repos whose tracker doc lives elsewhere.
  - [matt] Recursion guard for review sub-agents rejected (PR #1186 closed; `subagent-recursion.md:14`), see D3.
- **Underlying need**: review sees every standard by search, not recall, and the orchestrator waits for every reviewer's report.

## D7 verification gate

- **Does now**
  - [matt] diagnosing-bugs Phase 1 completion = one **tight**, **red-capable** command "already run at least once" (`M:skills/engineering/diagnosing-bugs/SKILL.md:57-59`).
  - [matt] implement: typecheck + single tests regularly, full suite once at end (`M:skills/engineering/implement/SKILL.md:13`).
  - [hl] outline phases split **Automated Verification** vs **Manual Verification** (`H:…/create-structure-outline/process.md:38`); automated boxes ticked as they pass, manual only "when the user confirms" (`implement-outline/process.md:23`); pause for pending manual checks by default (`:25`).
  - [hl] research: "Distinguish tests read from checks run" (`H:…/create-research/process.md:54`).
- **Why**
  - [hl] Manual checks exist "when they need human judgment" (`create-structure-outline/process.md:38`). Separation reason beyond that: **no stated reason**. **INFERENCE**: an agent can tick an automated box honestly; it cannot honestly tick a judgement box.
  - [hl] Phases are small end-to-end slices so "each phase should work and be verifiable when it ends" (`create-structure-outline/process.md:21`).
- **Changed since pin**
  - [matt] diagnosing-bugs: if red was forced by mutation, `diff` against a pristine copy (PR #1209, #955). Why: BSD `sed -i` "exited 0 and changed nothing" yet the test was reported mutation-checked; `diff` not `grep` because grep proves presence, not change.
- **Underlying need**: a green/red is trusted only after proving the thing under test actually changed, and human-judgement checks are never auto-ticked.

## D8 branch/push/merge + publish authority

- **Does now**
  - [matt] implement ends "Commit your work to the current branch" (`M:…/implement/SKILL.md:17`). PR template carries Door (one/two-way) + Blast Radius (`M:…/pr/SKILL.md:24-30`).
  - [hl] implement: "Make commits when requested, following repository rules" (`H:…/implement-outline/process.md:35`); ticket integrations and PR writing "stay outside this workflow" (PR #13).
- **Changed since pin**
  - [matt] wayfinder research: push `research/<name>` but "open no PR: it is never merged" (PR #1181, #576). Why: the subagent opened a draft PR against a throwaway branch.
  - [matt] wayfinder tickets carry only `wayfinder:` labels, never `ready-for-agent` (#518). Why: decisions were labelled as ready to implement.
  - [matt] setup creates missing triage labels; to-tickets attaches tickets as sub-issues (commits `5b7cade`, `cffab50`). No body-level reason beyond PR titles → **no stated reason**.
- **Underlying need**: what may be published (PR, label, merge) is decided by the artifact's lifecycle, not by what the agent can reach.

## D9 lessons/retro

- **Does now**
  - [matt] `/retro`: suggest **environment** improvements, ordered by severity: navigation, automated checks, coding standards, AGENTS.md, tool economy, no-ops, information access (`M:…/retro/SKILL.md:7,15-25`).
  - [matt] SCOPE: hypotheticals fail the bar; reactions/+1s don't count (`M:SCOPE.md:9,12`).
- **Changed since pin**
  - [matt] ask-matt routes post-bug reflection to `/retro` in the same session (commit `c5b9869`, PR #1121). No body → **no stated reason**.
  - [matt] Every rejected idea gets an `.out-of-scope/` record with prior requests (PR #1179, #1190, #1240). Why (#1190): #573 was closed but "the reasoning was recorded nowhere".
  - [matt] chief-of-staff: "Use every user message as an excuse to search for these improvements" (`chief-of-staff/SKILL.md:45`).
- **Underlying need**: a lesson becomes an environment change (check, standard, pointer) or a written rejection; never a memory.

## D10 cost/effort/model

- **Does now**
  - [matt] retro "Tool economy" category: flag token-inefficient tooling (`M:…/retro/SKILL.md:21`).
  - [hl-fold] model switch = new **configuration epoch** (D17): `model-change` + recomposed leading prompt recorded in the log (`F:packages/fold-core/src/AgentRuntime/AgentRuntimeService.ts:89,116`); epochs predate pin, README documents them now (`F:README.md:88`).
- **Changed since pin**
  - [hl-ace] SlopCodeBench Oct 2026 (`A:benchmarking-new-models-on-slop-code-bench.md`, commits `1a9b65e`…`eefe48c`). Why written: track whether agents keep **all** behaviour working as requirements change (`:149`). Findings: XHigh costs 2.11–4.22× Medium (`:23`); Opus 5.5 Medium 28 vs XHigh 25 strict passes (`:73`); author: effort "was not a reliable way to buy more strict passes" (`:77`), single runs, not causal (`:69`). Counter-finding: Opus XHigh code "~5x cleaner" (`:129`). Leftover scratch code counted on purpose (`:108`).
  - [hl-fold] PR #65: `switchModel` now closes the replaced runtime's scope. Why: old runtime's HTTP client/layers stayed open until session end (bug, failing test added).
- **Underlying need**: effort level is a measured trade (passes vs cleanliness vs cost), not a default of "max".

## D11 security/sandbox

- **Does now**
  - [matt] diagnosing-bugs: redact every secret in shown output; build loops against env vars (`M:…/diagnosing-bugs/SKILL.md:14`).
  - [matt] `misc/git-guardrails-claude-code` is **frozen**, unmaintained (`M:.out-of-scope/frozen-misc-skills.md`). Why: "I can't tell whether a fix is right" for skills not used daily (`:7`).
  - [hl] rpi asks before writing to a sandbox-blocked path (`H:…/rpi/SKILL.md:47`; README: Codex sandbox may make `.agents` read-only).
  - [hl] research/analyzer agents are read-only (`create-research/process.md:28`).
- **Changed since pin**
  - [matt] wizard `write_env` creates `.env` mode 0600, quotes values (PR #1237). Reasons in commit titles only (#1220…#1003) → **no stated reason** in body read here.
  - [hl-fold] PR #57: schema-invalid tool params return a **failed tool result**, not a run-ending error. Why: "The model should get a failed tool result instead, so it can fix the call"; observed live (`update_plan` without `title`).
  - [hl-fold] PR #61/#60: existing log identity is authoritative; conflicting id / bad history / double start **fails** rather than silently initialising (`F:README.md:86-88`); "Never put unrelated sessions under one shared EventLog" (`F:.claude/skills/effect-program-design/SKILL.md:69`). Why (#60): the descriptor was "an unnecessary value-level bridge"; resume "must not silently resume from a new empty in-memory log".
- **Underlying need**: fail loud on identity/persistence faults, fail soft (recoverable result) on agent input faults.

## D12 testing discipline

- **Does now**
  - [matt] tdd: test only at **pre-agreed seams**, confirmed with the user (`M:skills/engineering/tdd/SKILL.md:22`); red before green, one slice at a time (`:36-37`); named anti-patterns: tautological, horizontal slicing (`:31-32`).
  - [hl] TDD doc: Program Design shows code shape + tests; patterns to follow cited by path (`H:…/create-tdd/process.md:39,45`). Outline tests "following the project's existing patterns" (`create-structure-outline/process.md:29`).
  - [hl-fold] Every fix PR ships a test that "fails without the fix" (PR #57, PR #65); flaky test root-caused to ns→ms truncation (PR #52).
- **Why**
  - [matt] Seams agreed up front because "You can't test everything" (`tdd/SKILL.md:22`).
  - [hl] System Design approved before Program Design (`create-tdd/process.md:3,33,49`; `workflow.md:49`). **No stated reason** for two approvals. **INFERENCE**: code shape is wasted if the component interaction is still moving.
- **Changed since pin**
  - [matt] seam catches/misses note (PR #1192), see D5.
  - [matt] forced-mutation diff (PR #1209), see D7.
  - [hl-fold] PR #51 anti-slop + typed lint turned on as errors; tests exempt from stricter rules (`F:tools/oxlint/README.md:38`). Why: **no stated reason** in PR body beyond adopting the rules. **INFERENCE**: mechanical slop is cheaper to block in lint than catch in review (matches chief-of-staff "Lint rules which force correctness", `chief-of-staff/SKILL.md:31`).

## Lessons

1. **Change a rule only on an observed failure, and attach the evidence.** Every mattpocock PR since pin carries a Before/After from a real session (`M:SCOPE.md:9`; PRs #1193 #1196 #1208 #1209).
2. **Write down every "no" with its reason and prior requests.** That stops the same idea being argued again (`.out-of-scope/*`; PR #1190 "reasoning was recorded nowhere").
3. **Put limits in the harness or a check, not in prose.** Prose guards cost tokens every run and still need the model to obey (`subagent-recursion.md:7`; fold PR #51 lint; chief-of-staff `:31`).
4. **Bind identity by fetching it, never by context.** Fetch and state the ticket title, use real ids, read the type label, treat the existing log as authoritative (PR #1196, #1181; fold README `:86`).
5. **Trust a red/green only after proving the change landed. Never auto-tick a judgement check** (PR #1209; rpi `implement-outline/process.md:23-25`).
6. **More effort is not more quality by default.** Measure it per task: XHigh cost 2–4× for no reliable pass gain (`A:benchmarking-new-models-on-slop-code-bench.md:23,77`).
