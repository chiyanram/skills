# 64b — Why firstmate does what it does (R38, map #9)

Repo `kunchenguid/firstmate`. Pin `549e07f` → `origin/main` `5f2b81b` (80 commits). Line cites are `@5f2b81b` unless marked.
Clone is shallow: rationale for rules older than the pin comes from VISION.md, code headers and PRs, not commit history.
Firstmate's own review practice matters: the maintainer's agent triages every PR against VISION.md rule by rule
and stamps a `contract-class` (`opt-in` / `new-default` / `restore`) — PR #5343 comments, PR #6682 intent.

## Core — why the shape

- **One coordinator + briefed workers.** VISION.md:12-14 — without it, parallel sessions mean the captain "juggles a long list of sessions, relearns what each one was about"; other tools only ease jumping between them, "the context switch remains the captain's burden". Depth capped: "every layer between the captain's intent and the acting agent costs fidelity and tokens" (VISION.md:38).
- **Coordinator never codes.** VISION.md:25 — even the smallest change is a worker's job, "because trivial is a guess and command attention does not scale." Enforced as hard rule 1 (AGENTS.md:28-32), with the one exception a concrete in-the-moment captain approval that "gains no standing authority".
- **Worker reports only to firstmate.** VISION.md:14 "every worker reports through the first mate and never addresses the captain"; AGENTS.md:11,39-40. Underlying: one interface keeps the captain out of tab-juggling, and firstmate translates mechanics to outcomes (AGENTS.md:316-341).
- **DoD checks the pushed HEAD.** bin/fm-dod-lib.sh:564 — done accepted only when "HEAD - your latest commit - is pushed"; "the check tests that commit, not merely that a branch moved." Why: VISION.md:52 "Workers are supervised, not trusted". Related field bugs: issue #5944 (teardown treated a published-but-unmerged branch as landed — "A published branch is not landed work"), PR #6233 (fetch before refusing a pushed head, still refuse unpushed). INFERENCE: a worker's "done" was being trusted while its last commit sat local.

## D1 rule layers + loading

**Does now** — One always-loaded contract (AGENTS.md) with a hard ceiling: "stated ceiling of 9,000 words" (VISION.md:39). Everything else is a skill loaded "only at its stated trigger"; skill descriptions are "the always-loaded trigger index" (AGENTS.md:412). Each section says "Load `<skill>` when/before …".
**Why** — VISION.md:37 "Token efficiency is a first-class concern: every agent's context stays lean". AGENTS.md:430-433: keep only what helps "almost every future agent session"; "Prefer rewriting or pruning existing entries over appending".
**Changed since pin**
- 0aa7fac (#7298): context re-emit now prints a read cue first. Why: Claude truncates hook output >10,000 chars to the first 2,000, so captain.md/learnings.md "never reached the session".
- 99da16d (#6725): daily startup-growth check. Why (PR intent): startup scripts and learnings "shouldnt be loaded too mcuh and use too much".
- PR #5343 triage: maintainer rejected an unconditional AGENTS.md sentence as `new-default` because it added a re-evaluation turn "that only costs tokens"; accepted once scoped to configured homes.
**Underlying need** — every always-loaded word taxes every session; loaded context silently truncates.

## D2 skill/reference format + sourcing/editing

**Does now** — Skills in `.agents/skills/`; AGENTS.md points to an owner rather than restating ("Do not repeat what the codebase already shows; point to the authoritative file", AGENTS.md:431). Script headers own mechanics (e.g. "`bin/fm-brief.sh` and its help own scaffold syntax", AGENTS.md:388). `agent-skill-trigger-index` is a maintained full index (AGENTS.md:413).
**Why** — VISION.md:34 — exact logic in scripts, understanding in agents: "the two never mix." Self-evolving: VISION.md:61 "plain instructions, scripts, and text records keep the whole system introspectable".
**Changed since pin**
- 2ce57d0 (#6784): index claimed complete but "omitted" six skills; added. Why: the index must match its claim.
- e5b9ddd (#6647): worker role names the skill file as a fallback. No stated reason in subject; INFERENCE: some harnesses could not invoke the skill by name.
**Underlying need** — one owner per fact, so a rule cannot drift between two copies.

## D3 orchestration

**Does now** — Firstmate dispatches via `bin/fm-spawn.sh` into isolated worktrees, "no concurrency cap" for independent work (AGENTS.md:202); secondmates are scoped sub-homes, idle by default (AGENTS.md:143). One live supervision cycle (AGENTS.md:264); restarts reconcile from disk (AGENTS.md:130).
**Why** — VISION.md:43 "Everything that matters survives the death of any conversation"; VISION.md:54 a new task shape earns its way only when "existing primitives genuinely cannot compose".
**Changed since pin**
- ac0811c (#5343) project capacity, spawn exits 75, item stays queued (AGENTS.md:203). Why (issue #4237): surplus workers spent "full-context turns retrying the resource" — one worker 129 turns, 21.9M tokens; 17% of wait-only tokens. Opt-in per maintainer triage (PR #5343: "the declaration is the explicit grant").
- 6a7b391 (#6442) `--base-branch` (AGENTS.md:196). Why: spawns "always reset … to origin's default branch", so feature/release work "started from the wrong code". Base read only from the brief's Setup line so "prose cannot redirect a spawn" (PR #6442 intent).
- 6407052 (#7154) prevent concurrent secondmate relaunch races — no stated reason beyond title; INFERENCE: two relaunches produced duplicate mates.
**Underlying need** — parallelism without oversubscribing finite local resources or starting from the wrong base.

## D4 brief + handoff record

**Does now** — Generated scaffold is "a safety contract, not a suggestion" (AGENTS.md:401). Two filled sections: `## Captain's intent` (verbatim ask; reviewer treats it as acceptance criteria) and `## Firstmate spec` (only build instructions the ask requires) (AGENTS.md:389-390). Mid-task asks are appended verbatim (AGENTS.md:223). Steering via durable per-task inbox, doorbell only in the pane (AGENTS.md:216).
**Why** — VISION.md:50 "Every task gets an explicit contract before it starts … the machinery refuses to guess." Widening intent is barred "because the reviewer treats that subsection as acceptance criteria" (AGENTS.md:389).
**Changed since pin**
- 6a7b391: brief carries a machine-read `Base branch:` line; spawn refuses without matching flag. Why: a decoy line in the intent must not redirect (PR #6442 ci-1).
- 7df545b (#7172): `--upstream-consent` recorded on brief, spawn and promotion (AGENTS.md:197). Why: consent must be per-task and auditable, not standing.
**Underlying need** — the worker's contract must be fixed, explicit and un-redirectable by prose.

## D5 human channel, escalation, status

**Does now** — Captain sees outcomes, never mechanics; an internal-term translation table (AGENTS.md:316-337). Escalate only for review-ready work, findings, real blockers, destructive actions, credentials (AGENTS.md:347-354). Final message must stand alone (AGENTS.md:318).
**Why** — VISION.md:16 "An escalation exists for a decision only a human can make"; progress and retries "are never news." VISION.md:17 silence "never hide a failure, a decision, or a risk."
**Changed since pin**
- 138cf11 (#6682): a worker parked on Claude's exit picker now reports `blocked-on-prompt`. Why (issue #4754): a modal "is indistinguishable from a healthy idle composer, so liveness stays quiet" — "Hours of zero status events".
- 42dd906 (#6518): count consecutive busy-deferred doorbells and escalate at a bound. Why (issue #6445): secondmate stuck on an `AskUserQuestion` panel ~20 min; each ring skipped as busy, "so nothing escalated".
- 9b1ada0 (#7338) captain hold bounds wedge escalation — title only; INFERENCE: avoid re-escalating work the captain parked.
**Underlying need** — silence must mean healthy; a stuck worker must surface without the human watching panes.

## D6 review

**Does now** — The selected delivery path owns rigor; with no-mistakes, it "alone owns review, fixes, tests, documentation, push, PR, and CI" (AGENTS.md:229). Never add a manual reviewer or "stack serial manual reviews" (AGENTS.md:230). Implementation worker "never answers its own finding" (AGENTS.md:244).
**Why** — VISION.md:71 "validation belongs to no-mistakes, CI belongs to the forge"; firstmate is "the command layer, not the workshop".
**Changed since pin** — 1a6714f (#7368) forge=external: firstmate "cannot observe, approve, or merge the review", so it always escalates (docs/external-review-forge.md:25). Why: review tool uploads a snapshot; no PR exists.
**Underlying need** — one review owner per path, so rigor is chosen once, not reinvented per task.

## D7 verification gate

**Does now** — Ready report accepted only when the named HEAD is on the forge/branch (bin/fm-dod-lib.sh:564,576,599). `bin/fm-pr-merge.sh` refuses "an unproved merge … instead of reported as landed" (AGENTS.md:245). Teardown owns the landed-work test (AGENTS.md:36).
**Why** — VISION.md:52 "Workers are supervised, not trusted"; VISION.md:53 "a refusal to discard is a finding, not an obstacle."
**Changed since pin**
- 1a6714f: new ready form `done: review <url> uploaded for review`, accepted only once HEAD is on the backup remote when one is recorded. Why: no PR head to check, so the durable copy stands in.
- 6af8331 (#6331): reject invalid completion inventories. Why: `complete` accepted the origin as its own inventory entry.
**Underlying need** — "done" must be a checkable fact about a commit, not a worker's claim.

## D8 branch/push/merge + publish authority

**Does now** — Hard rule 2: never merge without explicit word; `yolo` is the only standing relaxation and never merges red (AGENTS.md:33,240-243). Home role defaults to user/operator; upstream publication needs `config/firstmate-role` maintainer opt-in or one-task consent (AGENTS.md:50-51, bin/fm-role-lib.sh:4-10). forge=external: per-task pre-push guard (bin/fm-git-push-guard.sh).
**Why** — VISION.md:23 "autonomy exists only as an explicit grant, never as a default"; VISION.md:27 standing autonomy "never quietly widens".
**Changed since pin**
- 7df545b (#7172) publication role. Why (commit): users' agents hit a firstmate bug and "could drive a pull request at upstream because nothing distinguished" maintainer from user. Role "never inferred from gh identity, remotes, permissions, or CI"; secondmates honor only receipt-proven inherited grants "so a child cannot grant itself".
- 1a6714f (#7368) forge=external no-push. Why: task branches on a shared origin are seen by "colleagues" (docs/external-review-forge.md:4); captain wanted the protection "without publishing any employer-internal code" (PR intent). Three layers "from strongest to weakest": hook, spawn refusal, brief text (doc:17-22); `--no-verify` is a documented accepted residual.
- 6a7b391: worker contract names the base as a branch never to push to; local-only and Gerrit refuse a named base.
**Underlying need** — capability (credentials, push rights) is not authority; publish rights must be declared, scoped, and enforced below the prompt.

## D9 lessons / retro

**Does now** — Knowledge routed to its most specific owner: captain.md, learnings.md, backlog note, scout report, project AGENTS.md (human-only additions) (AGENTS.md:147-161). Workers may only correct wrong facts in project AGENTS.md, never add — "every entry taxes every agent session" (AGENTS.md:159). `/stow` curates.
**Why** — VISION.md:75 "field incidents become regression coverage" — lessons land as tests and script refusals, not prose.
**Changed since pin**
- 2911a3b (#6608) memory layering (AGENTS.md:149-150). Why: section 6 routed knowledge only to local files, so a captain with external stores "had no tracked rule keeping those stores authoritative". Review round added a pending-capture marker so a fact is never pruned before its tier holds it.
- 7df545b: user-home learnings general to all users stay local unless an authorized contribution (AGENTS.md:156).
**Underlying need** — every lesson needs one authoritative home, and unreachable stores must not lose it.

## D10 cost / effort / model

**Does now** — Effort fallback: low for well-understood work, xhigh for ambiguous design, "never max without explicit captain preference" (AGENTS.md:110). Quota-aware dispatch, never silently downgrade (AGENTS.md:105; VISION.md:67).
**Why** — VISION.md:37 "every task is achieved with the fewest tokens that do it well"; VISION.md:67 choices "stay inspectable and captain-owned".
**Changed since pin**
- 9cd4a3b (#7308) afk spend cap = live ordinary workers at entry, default as floor, explicit `--spend` wins. Why (PR intent, German): raise afk parallelism to the count present at entry; commit: so the mode does not throttle running parallelism. One counter shared with spawn "so entry and later lock cannot diverge" (translated).
- 98d80a1 (#5354) per-task pipeline-spend ledger at teardown, opt-in. Why (issue #4238): 26.5% of an account's spend was cold pipeline agents with no session log; firstmate "could see the account emptying but not that one task's review loop". Opt-in because an ungated recorder was triaged `new-default` (PR #5354 comments).
- ac0811c: capacity cap — cost of retry turns (D3).
**Underlying need** — spend must be attributable per task and bounded by explicit, inspectable settings.

## D11 security / sandbox

**Does now** — Isolated worktree assertion, stop if in primary checkout (AGENTS.md:211,394). Never dispatch on unverified harness (AGENTS.md:92). Only the captain changes account pins (AGENTS.md:94). Destructive/irreversible/security-sensitive always escalates (VISION.md:26).
**Why** — VISION.md:65 a scraped vendor surface is "a standing debt … never hardens into a shared contract".
**Changed since pin**
- 47aff86 (#6750) `config/crew-exclude-tools`. Why (issue #6744): hide e.g. tracker write tools; the only route was the raw-launch escape hatch. Runtimes that cannot apply it refuse rather than ignore.
- 1a6714f push guard, 7df545b role gate (D8). 24f3a6b (#6365) scope Orca launch env — title only; INFERENCE: env leaked across sessions.
**Underlying need** — refuse when a protection cannot be applied; never degrade silently.

## D12 testing discipline

**Does now** — PRs to main must go through no-mistakes with an attestation bound to the head SHA (CONTRIBUTING.md:6-13). Local Test is "intent-targeted"; CI owns broad regression (CONTRIBUTING.md:98,134). Opt-in backend tests self-skip and print the gate (CONTRIBUTING.md:148).
**Why** — VISION.md:75 "This repository ships through its own discipline … field incidents become regression coverage."
**Changed since pin** — PR bodies carry a live-validation table per scenario and disclose gaps ("untested", PR #6682; "I didn't revert the code to watch each new test fail", PR #6442). Fix rounds state "Each new test failed against the old code" (ac0811c body). 1a6714f dropped "string-grep hook assertion", keeping behavioral ones.
**Underlying need** — evidence of behavior, with honest disclosure of what was not driven live.

## Lessons

1. **Default off; capability ships as opt-in.** Spend ledger, capacity, memory tiers, tool exclusions all opt-in; maintainer triage blocks `new-default` (PR #5343, #5354; VISION.md:23).
2. **Authority is declared, never inferred from capability.** gh identity/remotes/CI grant nothing (7df545b; bin/fm-role-lib.sh:10). Children cannot self-grant.
3. **Enforce below the prompt, in layers.** Hook > spawn refusal > brief text, with the residual named (docs/external-review-forge.md:17-22); "done" checked against a commit (fm-dod-lib.sh:564).
4. **Silence must be honest.** Stuck-on-dialog and busy-doorbell gaps fixed because quiet looked healthy (#4754, #6445; VISION.md:17).
5. **Every always-loaded word is a tax.** 9,000-word ceiling, triggered skills, reject unconditional contract turns (VISION.md:39; PR #5343).
6. **Changes are justified by a measured field incident.** Issues quote tokens, minutes, counts (#4237: 21.9M tokens; #4238: 26.5%) and are judged rule-by-rule against VISION.md.
