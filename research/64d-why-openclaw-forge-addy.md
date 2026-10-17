# 64d — WHY: openclaw · forge · addy (R38, map #9, chiyanram/skills#86)

Learn the reason, not the rule. Every "why" below is the reference's own stated reason, cited.
Where none is stated: "no stated reason" + **INFERENCE**. Quotes ≤15 words.

| tag | repo | pin | read at |
|---|---|---|---|
| [forge] | rameezk/forge | 43d360e | origin/main 57f3619 (120 commits later; ADRs 0038–0074 new) |
| [oc] | openclaw/openclaw | b94e5177 (2026-10-01) | main d8faf8876 via `gh api` (local fetch incomplete) |
| [addy] | addyosmani/agent-skills | 2686b62 (2026-09-25) | origin/main aeac41d |

## D1 rule layers + loading

- **Does now**
  - [oc] One root `AGENTS.md` (~19.5 KB) + nearest scoped `AGENTS.md` + "Read when relevant" pointer list; "Update instructions at owner; no competing rules here." `AGENTS.md:14-15 @ d8faf8876`.
  - [forge] Tiny root `AGENTS.md` (54 lines); forge *appends* its own instructions to the harness prompt, never replaces. ADR-0057 `:20 @ 57f3619`.
  - [addy] Only name+description load at start; `SKILL.md` loads on demand. `docs/skill-anatomy.md:130 @ aeac41d`.
- **Why**
  - [oc] OpenClaw caps injected AGENTS.md at 20,000 chars; above it keeps "9K head, a policy digest, and a 3K tail" — rules arrived as fragments. commit 0fc181d08 (#163325) body.
  - [forge] Claude Code run should behave "as it would for a developer in that repository". ADR-0057:24.
- **Changed since pin**
  - [oc] 27,918 → 18,900 B (#163325, 10-02) → 22,668 → 19,499 B (#171161, 2091c6e69, 10-13). Why: root "exceeded the former 20,000-character bootstrap budget and was truncated". Method: "Enriched the owning docs/skills before removing detail from root"; then a "fresh-context adversarial no-loss audit". #171161 body. First trim lost clauses; autoreview caught it and they were restored (#163325 second commit).
  - [oc] 872d5b20e "tighten root agent charter in caveman style" — no stated reason. **INFERENCE:** same byte budget.
  - [forge] AGENTS.md gained the scoped-check block (diff 43d360e..57f3619); why → D7.
- **Underlying need:** every rule must arrive whole in context; size is a hard budget, so detail lives at its owner behind a pointer.

## D2 skill/reference format + how rules are sourced/edited

- **Does now**
  - [addy] Frontmatter limited to six spec keys; vendor keys go under `metadata`. `skill-anatomy.md:34`. `SKILL.md` < 500 lines, detail to `references/`. `:132`.
  - [oc] Skills point back at AGENTS.md sections instead of restating: pr-simplify "Rules:" names four root sections. `.agents/skills/pr-simplify/SKILL.md:12 @ d8faf8876`.
  - [oc] Shared skills live upstream (`openclaw/agent-skills`), repo keeps a 23-line entrypoint. `.agents/skills/autoreview/SKILL.md:8,21`.
  - [forge] Skills vendored under `.agents/skills`, `.claude/skills` symlinked; refreshed by "chore: update skills" PRs (20e887f #478, body empty) — no stated reason. **INFERENCE:** sourced from the operator's own skills repo.
- **Why**
  - [addy] #608: hosts "do not promise to ignore unknown top-level keys and a strict client can reject" the file. Made an error not a warning because it "fires on nothing on main". #608 body.
  - [addy] Context efficiency: full SKILL.md loads when relevant, "To keep that load cheap" (`skill-anatomy.md:130`).
- **Changed since pin**
  - [addy] #608 (9d0c60d40): rule existed in a doc (#316) but "Nothing links to it. Nothing enforces it." → linked + linted.
  - [addy] #580 (11eb57ba7): performance-optimization 496 → 267 lines, Step 3 moved **verbatim** to `references/optimization-patterns.md`, "-25% tokens per load"; every rule later sections depend on "still stated inline". Verified byte-identical by script; routing untouched (no description edit). #580 body.
  - [oc] autoreview → shared skill (3d74794d8, #163397, −10k lines incl. 7,860-line script): "Repository-local autoreview copies drift and can retain retired prerequisites". "Shared changes belong upstream". #163397 body.
  - [oc] deslop folded into pr-simplify (f19a7365a, #173363): "keeping two would let them drift apart"; AGENTS.md gains one sentence, "The rules stay in the skill". #173363 body. Writing follows mattpocock `writing-for-agents`.
  - [oc] test-audit 169 → 57 lines + `references/audit.md` (16a29a010 "centralize proof policy and trim testing guides") — no stated reason (no PR, no body). **INFERENCE:** same drift/size motive as #171161.
- **Underlying need:** one owner per rule; duplicates drift, so move verbatim and leave a pointer — and lint the format so a rule is enforced, not just written.

## D3 orchestration

- **Does now**
  - [forge] Ticket on frontier + `forge:ready` → claimed (`forge:running`) → isolated workload of a declared worker (harness+model+prompt). ADR-0016:18. Separate workload kinds: dispatch, revision (`on.feedback`, ADR-0050), conflict resolution (`on.conflict`, ADR-0069).
  - [forge] Harness behind one adapter seam; "runner, fingerprint, store and frontend know nothing" of which harness. ADR-0055:18.
  - [oc] "Task defines scope and authorization; chosen workflow owns execution". `AGENTS.md:12`. Delegate lanes only "when saving time or improving verification"; lead "stays hands-on". `:56`.
  - [addy] `/review` and `/test` run in main session, spawn nothing (#682).
- **Why**
  - [forge] Harness-driven: workers are declared, every run isolated + recorded "so you can trace what every worker did". `README.md:11`. Pi contract written against a fake failed first live run → contract fixed + real-binary check. ADR-0008:9,17.
  - [forge] Claude Code harness added because pi on subscription was billed as third-party usage ("You're out of extra usage" at 2%). ADR-0054:11.
  - [forge] Conflict as own kind, not fake feedback: Option 1 "bends the feedback cursor". ADR-0069:11.
  - [addy] #682: "a single-perspective review is better with the conversation's context and without the cost of a subagent".
- **Changed since pin**
  - [forge] ADR-0054/0055 (#352, #353): second harness; adapter owns everything harness-specific (pi "leaks through it", ADR-0055:11).
  - [forge] ADR-0069 (#471): siblings touching same files leave PRs conflicting; "Nothing in forge notices".
  - [addy] #682: docs said commands wrap personas; they don't — docs fixed, not commands.
- **Underlying need:** an orchestrator owns trigger + success check per workload kind; the worker's skill owns how.

## D4 brief + handoff record

- **Does now**
  - [forge] Revision brief carries the full text+URL of every feedback item; each must be answered. ADR-0062:19.
  - [forge] Worker report ends with one line of local commands passed + "full suite: CI". `AGENTS.md:39-40`.
  - [oc] PR body = problem, solution, impact, evidence, kept current. `AGENTS.md:112`. pr-simplify reports "machinery that disappeared", behaviour still protected, LOC deltas. `pr-simplify/SKILL.md:61`.
- **Why**
  - [forge] On PR #414 a review summary was "silently dropped" — skill read only unresolved threads; "only forge, which owns the cursor, knows". ADR-0062:11.
  - [forge] Before: verification "buried in a side remark". ADR-0064:21.
- **Changed since pin**
  - [forge] ADR-0062 (#424) replaces 0050's identity-only brief. ADR-0070 (#463): failed revision restores cursor — crash on #414 consumed feedback; recovery needed hand-editing DB. ADR-0070:11.
- **Underlying need:** the party that knows what is owed writes it into the brief; the handoff states what was verified, explicitly.

## D5 human channel, escalation, status

- **Does now**
  - [forge] Labels are the only thing written to a ticket; failure reasons only on dashboard. ADR-0016:18. Failed dispatch closes its PRs with one fixed note naming only the ticket. ADR-0066:18.
  - [forge] Only OWNER/COLLABORATOR comments count as feedback. ADR-0063:19.
  - [oc] "ask only about consequential decisions context cannot resolve"; "Silence never authorizes gated action". `AGENTS.md:26`. Skill-caused pause must quote the exact SKILL.md line. `:27`.
- **Why**
  - [forge] "Forge must also not publish its internals" to GitHub. ADR-0066:9. Stranger's comment would "spend the operator's budget, and become text the worker acts on". ADR-0063:11.
- **Changed since pin**
  - [forge] ADR-0063 (#423), ADR-0066 (#436), ADR-0068 (#476): status labels recoloured because ready looked like running/done on GitHub. ADR-0068:9. ADR-0071: run status and outcome side by side.
- **Underlying need:** one status surface the human trusts; outsiders' text is data, never a trigger.

## D6 review

- **Does now**
  - [addy] Reviewer answers "would tests catch a regression" by inverting one condition and running the suite. `skills/code-review-and-quality/SKILL.md:164 @ aeac41d`.
  - [oc] Fresh review via shared autoreview before nontrivial commit/landing; "Actionable = likely or high-impact". `openclaw-pr-maintainer/SKILL.md:50`.
  - [oc] pr-simplify = author's editing pass; "precedes review and never replaces it". `pr-simplify/SKILL.md:8`.
- **Why**
  - [addy] #618: checklist "asks the question but gives no way to answer it"; one dropped `!` left "all 127 tests" green. #618 body.
  - [oc] #173363: agent PRs "keep growing past the smallest fix", causing follow-up repair PRs; AGENTS.md rule had no step that applies it.
- **Changed since pin**
  - [addy] #618 (633ff8261, 10-02): two sentences added; checked not-duplicate vs Stryker skill and rejection ledger.
  - [oc] #173363 (f19a7365a, 10-15): pr-simplify incl. staging rule: above ~800 non-mechanical lines (~500 complex) "name the smallest coherent stage that can land first". `pr-simplify/SKILL.md:24`. Source: openai/codex's removed `code-review-change-size` skill (#173363 Sources).
  - [oc] dc02d331e "weigh review findings by likelihood and complexity" — no body; reason stated in rule itself: decline "unlikely, recoverable edge cases" (`openclaw-pr-maintainer/SKILL.md:50`).
- **Underlying need:** review needs an executable probe, not a read; shrink the change before review so review is cheap.

## D7 verification gate

- **Does now**
  - [forge] Agents run only scoped commands for touched areas; never full `make check-no-vm`; CI is full gate. `AGENTS.md:29-47`. Done = ready PR + required checks green, **read by forge**. ADR-0065:18.
  - [oc] "**PR CI = broad proof.** Pre-PR: touched tests + targeted typecheck/lint/format". `AGENTS.md:87`. "never delay PR for pre-PR suite runs". `openclaw-testing/SKILL.md:10-11`.
  - [addy] Onboarding verification loop now lists exactly what CI runs; workflow file is source of truth (#644).
- **Why**
  - [forge] Full check OOM-killed on 3.7 GB box, slow on Mac; workers already fell back "and mentioned it only in passing". ADR-0064:9. "standing rule, not a stopgap". `:17`.
  - [forge] Done must not take "the agent's word for it". ADR-0065:22. Before: draft or red PR counted done. `:9`.
  - [oc] 299d289e9 body: 1,892 Codex lanes, "only 33% of 3,133 box runs exited 0", boxes cost 1,040 lane-hours, PR CI ~9 min.
- **Changed since pin**
  - [oc] **Reversal.** Pin said "CI is expensive; do not spend it on proof … trust those results" (`AGENTS.md:91 @ b94e5177`). 299d289e9 (10-12) replaced it with PR CI as default broad proof — measured reason above.
  - [forge] ADR-0042 → ADR-0064 (#427, #444): from full non-VM local run to scoped-only. ADR-0072 (#482): missing `node_modules` read as "cannot run", fix left unpushed on #477 → repo installs own deps. ADR-0072:9.
  - [forge] ADR-0065 (#436): done = ready + green; ADR-0066 closes PRs left by failed dispatch.
  - [addy] #644: docs promised "everything CI runs, you can run locally" but listed a subset.
- **Underlying need:** cheap scoped proof locally, broad proof where it is cheapest and reliable (CI), and done read from the forge, not claimed.

## D8 branch/push/merge + publish authority

- **Does now**
  - [forge] Conflicts: merge default branch into PR branch, never rebase/force-push. ADR-0069:17,22; skill `git-pr-resolve-conflicts/SKILL.md:15,229`.
  - [forge] Commits authored by the App's bot (ADR-0051); attribution forced off by runner (ADR-0074).
  - [oc] "don't rebase or merge `main` just because it advanced"; integrate for conflicts/failing gate/base risk. `AGENTS.md:44`. Red main fixes pushed directly to main. `:88`. "fix/ship authority ≠ release authority". `:107`.
- **Why**
  - [forge] Rebase "would rewrite commits reviewers have seen, orphan inline comments and rewrite rework". ADR-0069:17. Behind-not-conflicting is "what GitHub's update branch or a merge queue is for". `:16`.
  - [forge] Attribution: written rules "lose to the harness's own system prompt often enough to leak" (#476, #480). ADR-0074:9,13.
- **Changed since pin**
  - [forge] ADR-0069 (#471), ADR-0074 (#493/#495), ADR-0051 (#398).
  - [oc] Red-main/CI-spend rules moved verbatim to `landing.md` (#163325) — same rule, new owner.
- **Underlying need:** never rewrite history others reviewed; integrate only for a named reason; enforce attribution in config, not prose.

## D9 lessons / retro

- **Does now**
  - [forge] Every run records a config fingerprint; runs sharing one form a cohort to compare. ADR-0034:18. Subagent kind = skills it loaded. ADR-0037:17.
  - [addy] `evals/skill-impact.md`: append-only ledger of skill changes "rejected on eval evidence". `:3 @ aeac41d`.
  - [oc] Incidents become rules with the evidence in the PR (e09f3ecd4/#168083: five compaction mistakes unit tests missed).
- **Why**
  - [forge] "To tell whether forge improves as its config changes, runs have to be compared". ADR-0034:9.
  - [addy] so contributors "review prior attempts before proposing overlapping work". ledger `:3`.
- **Changed since pin**
  - [forge] Most ADRs 0062–0072 cite a concrete failed run (#414, #477) as their context — no separate retro doc. **INFERENCE:** the ADR is the retro.
- **Underlying need:** a lesson is a recorded incident → one owned rule change, measurable by cohort.

## D10 cost / effort / model

- **Does now**
  - [forge] Budget (5 USD) + timeout (2 h) per workload, hard stop as `exceeded`; fails closed on unpriced spend; agent not told its limits. ADR-0044:19, ADR-0045:17.
  - [forge] Unset reasoning effort = model's own default. ADR-0038.
  - [oc] "Model-facing core additions cost ongoing context". `AGENTS.md:20`. "Test changes: obey cost/timing budget". `:89`.
- **Why**
  - [forge] "A budget cannot be silently bypassed by a model forge cannot price". ADR-0045:21. Limits kept out of fingerprint since agent isn't told. `:17`.
  - [oc] 299d289e9: box runs 33% success, 1,040 lane-hours → CI cheaper per proof.
  - [addy] #580: "-25% tokens per load"; #682: avoid subagent cost.
- **Changed since pin**
  - [forge] ADR-0044/45 (#292, #296); ADR-0047/56 list-price equivalent for subscription runs.
- **Underlying need:** cost is a measured, enforced limit, not a guideline; context bytes are cost too.

## D11 security / sandbox

- **Does now**
  - [forge] bwrap sandbox; workload holds only credentials runner deliberately gives. ADR-0024:18. Per-run empty `CLAUDE_CONFIG_DIR`, discarded after. ADR-0057:20. GitHub token in a read-only file, per-repo App token. ADR-0049:19.
  - [forge] Forge's `gh` comes before the dev shell on PATH. ADR-0073:20.
  - [oc] Untrusted fork code "only secretless isolation, never locally". `AGENTS.md:103`. Security = product tradeoff, "never invent gates". `:84`.
- **Why**
  - [forge] Empty config dir: "no host state or earlier run reaches it"; shared writable dir lets "Any workload could change what later runs load". ADR-0057:16,24.
  - [forge] Token file (2fa5d7e, #365): App token "expires and must be swapped mid-run without restarting the harness"; file replaced atomically. #365 Why. Binds the dir, not file, so rename shows inside sandbox.
  - [forge] Nothing a run writes should change "what pi loads at startup in a later run". ADR-0015:18.
- **Changed since pin**
  - [forge] ADR-0049 (#369), 2fa5d7e (#365), ADR-0057 (#353), ADR-0063 (#423), ADR-0073 (#488).
- **Underlying need:** each run starts from a known-empty state; credentials are data read from outside run-writable state.

## D12 testing discipline

- **Does now**
  - [addy] TDD skill description fires on pasted code "even when … the request does not mention tests". `skills/test-driven-development/SKILL.md:3`.
  - [oc] test-audit authoring gate: four questions before any test; reject mocks supplying asserted behaviour. `test-audit/SKILL.md:14-34`. pr-simplify: keep only tests with a "named failure". `pr-simplify/SKILL.md:53`.
  - [forge] Fix a bug by "reproducing it end to end" first. `AGENTS.md:22`.
- **Why**
  - [addy] #678: skill fired 0/6 on pasted-code prompts; with clause 6/6; must-not-fire 0/24 both ways. Negative eval `tdd-stays-quiet-on-debug` guards "fix a bug" wording.
  - [oc] #168083: implementation-mirroring tests "can miss broken provider requests, recovery, and persisted state".
- **Changed since pin**
  - [addy] #678 (7d65f5e78, 10-13), supersedes #645 which "made the same description change without measurements". Follows #612 (review skill: 7/27 → 21/27).
  - [oc] #168083 (e09f3ecd4), 16a29a010 test-audit rewrite (no stated reason; INFERENCE: size + one proof-policy owner).
- **Underlying need:** a skill trigger is measured with fires and must-not-fire evals; a test earns its place by a named failure.

## Lessons

1. **Measure before you move a rule.** oc flipped "local proof" → "PR CI = broad proof" on 1,892 lanes / 33% box success (299d289e9); addy changes a trigger only with fires + stays-quiet numbers (#678, #612). Copying the old rule would have copied a reversed one.
2. **Done is read, not claimed.** forge reads draft flag + required checks itself (ADR-0065:22); oc "Verify remote outcomes before success" (`AGENTS.md:111`).
3. **One owner per rule; move verbatim, leave a pointer, then audit for loss.** oc #171161 + #163325 (first trim lost clauses, review restored them); addy #580 byte-identical move; oc deslop→pr-simplify to stop drift.
4. **Prose loses to the harness — enforce in config or code.** forge ADR-0074 (attribution leaked despite AGENTS.md); addy #608 (rule existed in a doc, nothing enforced it).
5. **Whoever owns the state writes the brief.** forge ADR-0062: skill guessed which feedback was new and silently dropped it; forge owns the cursor so forge lists the items.
6. **Never rewrite history others reviewed; integrate only for a named reason.** forge ADR-0069:17; oc `AGENTS.md:44`.
