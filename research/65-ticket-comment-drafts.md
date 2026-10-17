# Ticket comment drafts — decisions of 2026-10-16/17 (skills #100)

Posted 2026-10-17 on operator approval (#100); each section below is the comment on its ticket.
One section per target ticket. Each line is an acceptance criterion to ADD, with the deciding ticket.
"PROPOSED" marks an idea that is not decided.

## agent-fleet #72 — roles, coordinator, briefs, post-status

Added by chiyanram/skills decisions of 2026-10-16/17:
- Replace the rebase rules in `worker-rules.md`: before stage 7 starts, a worker may rebase onto the default branch (force-with-lease, own branch only). After stage 7 starts, it merges the default branch into its branch and never force-pushes (skills #50 amendment, 2026-10-16).
- The coordinator claims a work item by setting the forge assignee. It does not take an item that has another assignee (skills #95 G25).
- Every stage handoff is a comment on the forge thread: decision, what ran, head SHA, open questions. Worker scratch stays uncommitted on its host (skills #89 G19).
- Souls, worker-rules, briefs and post-status say forge · issue · change request · thread. The forge commands live in one adapter (skills #89 G19).
- Caps by resource: at most 2 workers building per host; analysts and reviewers uncapped; at most 3 items waiting on the operator. Over a cap, the item is queued, not failed (skills #101 G26).
- A builder gets a fresh worktree from the pushed branch. `make worktree-setup` runs first; the worker starts only when it is green. Reviewers get no worktree (skills #102 G27).
- Delete a builder's worktree only after its done is accepted. Never delete a dirty tree; flag it to the operator (skills #102 G27).
- On a crash or hang, start one fresh worker from the forge thread and the pushed branch; never resume the dead session. Keep the dead worktree and name it in the thread. A second failure → blocked, to the operator with both failures (skills #102 G27).
- The coordinator checks each worker screen every few minutes. A waiting box → "stuck on: <the question>" to the operator (skills #102 G27).
- Test: a second item over the build cap is queued; a killed worker is retried once, then blocked.

## agent-fleet #73 — worker dev container image

Added by chiyanram/skills decisions of 2026-10-16/17:
- Managed settings turn off the ask-the-user tool for workers; workers post needs-decision instead. Permission mode stays auto (skills #102 G27, skills #69).
- Add the talking plugins to the plugin allow-list: humanlayer `show-me` and ayghri `i-have-adhd` (skills #14 G1 Q4: the talking set is on from session start everywhere).
- Add the chiyanram/skills plugin marketplace to the plugin allow-list (skills #93 G23: generic skills, references and crq ship from it).
- Put github.com and api.github.com in the Build egress list, not only in the comment (skills #69 amendment, comment 5969183454).
- PROPOSED, not decided: turn commit attribution off in managed settings, because a written rule lost to the harness (forge ADR-0074; skills #61 row 10; principle G22 #92).
- Test: inside the container, the ask-the-user tool is not available; `git clone` of chiyanram/skills succeeds with the read-only token.

## agent-fleet #74 — provisioning: two zones, runner, machine.env

Added by chiyanram/skills decisions of 2026-10-17:
- Build the new design in this repo beside the old scripts. Keep the Verifier, tokens, registry, tests and history (skills #95 G25).
- Install fresh into the zone users on the VM and the operator's laptop. Carry machine.env values and the Verifier over by hand. The operator re-creates the tokens (skills #95 G25).
- Run pilot skills #67 on the new install. Retire the old agents only after the pilot passes (skills #95 G25).
- After cutover, one command updates a host: git pull + plugin update + container rebuild (skills #95 G25).
- The runner runs one gate at a time (skills #101 G26).
- Test: the update command on a second host brings it to the same agent-fleet SHA and plugin versions.

## agent-fleet #75 — retro and /lesson wiring

Added by chiyanram/skills decision of 2026-10-16:
- Route each kept lesson strongest first: check (hook, lint, ArchUnit, test) → reference (rule + its reason) → soul → machine file → dropped (skills #88 G18).
- Before the retro picks a weaker destination, it states why each stronger one cannot hold the lesson (skills #88 G18).
- A dropped lesson gets one line, with the reason, in a rejected record, so it is not argued again (skills #88 G18). The file for that record is not named yet.
- Read the forge thread first, not "the GitLab thread" (skills #89 G19).
- Unchanged: at most 2 change requests per work item; the operator merges.
- Rejected lessons (G18 step 5) are recorded once, with the reason: generic → chiyanram/skills `.out-of-scope/<topic>.md`; Aruvii → agent-platform `docs/agents/out-of-scope/<topic>.md` (mattpocock `.out-of-scope/` pattern). Default picked 2026-10-17; reversible.

## agent-platform #643 — skeleton

Added by chiyanram/skills decisions of 2026-10-16/17:
- `make lint` fails when root AGENTS.md is 200 lines or more, when the root→leaf AGENTS.md chain passes Codex's 32 KiB cap, when a CLAUDE.md shim is not exactly `@AGENTS.md`, or when the `.claude/skills` symlink does not resolve. Extends check-doc-drift §5 (skills #90 G20; shared with #646).
- Note: generic skills and references move to the chiyanram/skills plugin; this project keeps only Aruvii (skills #93 G23). Workers run on today's files until the project layer lands (skills #94 G24). Decided 2026-10-17 (operator, option B): this skeleton shrinks to the AGENTS.md/CLAUDE.md flip, the `.agents/skills` tree with its `.claude/skills` link, and the Aruvii-only skills (flyway-migration, aruvii-git, aruvii-cleanup, v1-status, smoke-spec). Generic domains and the crq workflow do not move here; they go straight to the chiyanram/skills plugin, so each skill moves once. The WIP commit 71b5deb4 is reworked to this scope.

## agent-platform #644 — testing domain

Added by chiyanram/skills decisions of 2026-10-16/17:
- The testing references are written in chiyanram/skills, not in this project (skills #93 G23 Q1).
- Every Good/Bad pair is in one neutral domain: same mistake, same fix, no Aruvii names. The Aruvii path:line goes to the ledger as evidence (skills #93 G23 Q3; rewrite work skills #99).
- Each Rule line is one sentence: imperative + "because" + the failure it prevents, ≤35 words (skills #91 G21; reasons drafted in skills #98).
- AC-1 changes: "no copy in `.claude/rules/`" becomes "no copy in any AGENTS.md" (skills #72 G1b deleted `.claude/rules/`).
- Unchanged: the full replay proof before a new testing reference replaces the old one (skills #37).

## agent-platform #645 — one reviewer, role-tagged crq

Added by chiyanram/skills decisions of 2026-10-16/17:
- The crq workflow (stages, roles, lanes, review) is generic and lives in chiyanram/skills. This project keeps only its answers in `docs/agents/crq.md`: gate command, lane floor paths, role labels (skills #93 G23 Q2).
- `docs/agents/issue-tracker.md` is the one forge adapter (glab). crq text says forge · issue · change request · thread, never a forge name (skills #89 G19).
- Every stage handoff is a comment on the forge thread: decision, what ran, head SHA, open questions. A manual /crq run posts the same comments (skills #89 G19).
- Remove the "more than 5 in Act on" line. Keep the four buckets; the lead validates every finding (skills #87 G17).
- crq stage text: rebase only before stage 7; after stage 7 starts, merge the default branch into the branch, never force-push (skills #50 amendment).

## agent-platform #646 — AGENTS.md index

Added by chiyanram/skills decision of 2026-10-16:
- `make lint` runs the static delivery check: root AGENTS.md <200 lines, the root→leaf chain under 32 KiB, every CLAUDE.md shim exactly `@AGENTS.md`, `.claude/skills` symlink resolves (skills #90 G20).
- Each nested AGENTS.md carries one sentinel line for the delivery probe in #671 (skills #90 G20).
- Every probe failure is fixed in this item. Suspects to probe first: nested AGENTS.md under Codex, skills via symlink under Codex, nested rules on CREATE vs READ (skills #90 G20).
- AGENTS.md text is forge-neutral; forge commands point at `docs/agents/issue-tracker.md` (skills #89 G19).

## agent-platform #671 — CI on our own runner

Added by chiyanram/skills decision of 2026-10-16:
- Add a delivery probe job. It runs when any AGENTS.md or skill changes. Headless `claude -p` and `codex exec` each touch a file in every directory with a nested AGENTS.md and must quote its sentinel line. The job is red if one is not quoted (skills #90 G20).
- Test: remove one sentinel line on a branch; the probe job goes red.
- The pipeline posts its result on the change request without anyone pasting it — already AC-2; the probe result shows the same way.

## chiyanram/skills #65 — skills repo as source of truth

Wording update (skills #93 G23):
- The main question is decided: generic skills, references and the crq workflow live in chiyanram/skills, published as a plugin marketplace. G23 pulls this ticket into map #9.
- Remove "aruvii-agent-fleet" from the question. That repo does not exist (skills #14 amendment, 2026-10-03).
- Still open here: one plugin or several, versioning, office-work constraints.
- The update path is one command per host (skills #95 G25). Codex visibility of plugin skills is checked by the G20 probe (skills #90).

## chiyanram/skills #81 — split repos when the trigger fires

Wording update (skills #93 G23):
- "Today" changes: three repos. chiyanram/skills holds generic skills, references and crq as a plugin; agent-platform holds Aruvii only; agent-fleet holds the agent side.
- Row "common skills": done by G23, not waiting on a trigger.
- Row "crq pipeline": done by G23 Q2. crq is generic in chiyanram/skills; Aruvii answers are in agent-platform `docs/agents/crq.md`.
- Still waiting on a trigger: the coordinator package, and the Aruvii roles vs a generic fleet (G23: the fleet is Aruvii-specific now; extract the generic part later).

## agent-platform #670 — worktrees stop linking secrets/

Added by chiyanram/skills decisions of 2026-10-17:
- Add `make worktree-setup`: installs dependencies and node_modules in a new worktree and exits non-zero if any step fails. A fleet builder starts only after it is green (skills #102 G27; fleet retro #61 row 17). Owner picked 2026-10-17: this ticket, because it already changes how worktrees are made.
