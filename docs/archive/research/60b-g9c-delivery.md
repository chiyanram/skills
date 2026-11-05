# 60b · G9c candidates — DELIVERY (git · glab · worktrees · verification · dependencies)

> **DRAFT — candidates only, nothing here is approved (2026-10-12).** Decided on #34 so far: migrations tier A only (research/60a + ledger MG rows).

For **#34** (G9c). Brief `research/60-g9c-BRIEF.md`. Nothing here is approved. IDs prefix **DL** (DLG git · DLL glab ·
DLW worktrees · DLC cleanup · DLV verification · DLD dependencies · DLA root AGENTS.md).
Our text: AP skeleton `chore/643` @`71b5deb4` (prefix `skel:`); code evidence AP `origin/master` @`772736bf`.
Refs (paths under `refs/`): `fm/` kunchenguid-firstmate · `ad/` addyosmani-agent-skills · `oc/` openclaw-openclaw ·
`ps/` cursor-plugins/pstack/skills/poteto-mode · `hl/` humanlayer-skills · `mp/` mattpocock-skills.
Primary docs: GitLab, Git, Gradle, Spring Boot, GNU Bash, Conventional Commits (URL + § in each row).
superpowers is **not in refs** (R12 cited `sp executing-plans/.../task-done`) — not used; no rule rests on it.

## 1 · R12 rows (G1b-corrected)

| current file | target (G1b) | action | deletions | agree/change + why |
|---|---|---|---|---|
| `skel:aruvii-git/SKILL.md` | `delivery/references/git.md` (§5–6 commit + MR-title standard) + workflows §1–4 (see OQ1) + 4 MUSTs → root AGENTS.md git block | SPLIT | §3 `make verify-full` before undraft (R28: only the runner runs verify-full); §2-3 `glab mr rebase` (#50 Q20: local rebase onto origin/master + `--force-with-lease`); "CLAUDE.md wins" (:8-9); §5 description shape → owned `visual-pr` (#50 Q18); "Announce at start" | CHANGE: MR description shape leaves git.md for `visual-pr`; workflow placement per FL26 precedent (OQ1) |
| `skel:aruvii-git/references/glab.md` | `delivery/references/glab.md` | MOVE | dates/"single session" narration (:21-22); version-stamp prose | AGREE; add MR-state reader (retro row 13) and long-body/timeout row (retro row 18) |
| `skel:aruvii-git/references/worktrees.md` | `delivery/references/worktrees.md` (absorbs AGENTS.md worktree block) | MERGE | secrets-symlink explanation (:34-36) pending AP #670 (OQ2); node_modules symlink (:42-50) | CHANGE: node_modules symlink replaced by DLW5 (retro row 17) |
| `skel:aruvii-cleanup/SKILL.md` | flat workflow skill `cleanup` (OQ1) or `delivery/workflows/cleanup.md`; crq stage 0/10 + G6 coordinator teardown call it | MOVE | "Announce at start"; measured table (:29-33) → one Bad; "No automated test" section → Review check | AGREE on content; it already matches fm teardown |
| `skel:delivery/references/verification.md` | `delivery/references/verification.md` (absorbs AGENTS.md build + green/CI blocks) | MOVE+MERGE | "§Done means" pointers (:3,:85) → crq stage 8; §5 table → `make help` (WD8 hold) | CHANGE: "verify-full = the gate" becomes "runner pipeline = the gate" (R28) |
| `.claude/rules/dependencies.md` | ≤3 MUSTs → root AGENTS.md block «adding a dependency / touching `*.gradle.kts`, `libs.versions.toml`, `package.json`»; rest → `delivery/references/dependencies.md` | SPLIT | `.claude/rules/` deleted (G1b); "Historical note" + enforcer table (:72-90) → REQ-108 link; Renovate amendment narration (:55-70) → one When-X row; errorprone count story (:136-158) → one decided edge | CHANGE target only (G1b); Jakarta/Jackson 3 are ArchUnit-gated (FL17/FL18) → cite gate, no rule |
| AGENTS.md «build/test/lint/deploy» (91-140) | root AGENTS.md ≤8-line command list (DLA1) + `verification.md` | SPLIT | `cd &&` permission tip → harness note; settings.json note | CHANGE: list drops `verify-full`/`smoke FULL=1` for agents (R28 runner owns them) |
| AGENTS.md «green build / CI» (142-183) | `verification.md`; ungated list → `meta/references/gates.md` (FL18); CVE gap → `dependencies.md` | MERGE | "There is no CI" + #440 history (false once R28 lands); semgrep story | CHANGE: rewrite around the runner (#60) |
| AGENTS.md «branch/commit/MR» (303-390) | `git.md`; 4 MUSTs → root AGENTS.md (DLA2) | MERGE | #455 "Corrected" block; cz install prose (doctor reports it) | AGREE |
| AGENTS.md «worktree» (392-414) | `worktrees.md` | MERGE | — | AGREE |
| hooks `block-commit-on-master.sh` · `warn-piped-gate.sh` · `guard-concurrent-build.sh` | L4 · AP | KEEP | — | AGREE; references cite them instead of restating (checklist 4). guard stays: laptop workers share one Docker |
| `skel:dod/SKILL.md` | items → Review checks (ND-5 decided); only the Done-means evidence item lands in delivery (DLV7) | SPLIT→DELETE | whole file | AGREE (decided ND-5). Mapping: Code Quality → `layering`/`services`/`smells`; Test Coverage → testing refs; Security → `security.md`; API → `api.md`; tool-type table → `tool-types.md` |

## 2 · Candidates

### delivery/references/git.md

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLG1 | One issue → one branch `<feat\|fix\|docs\|chore\|refactor>/<issue>-<slug>` → one MR. | ad `git-workflow-and-versioning/SKILL.md:140-145` "fix/<short-description>" | AGENTS.md:305; R1:60-64 rule in 2–12 places | ADAPT (issue number ours) |
| DLG2 | A branch commit does one logical change; formatting or refactor goes in its own commit, never mixed with behaviour. | ad `git-workflow…:50` "Each commit does one logical thing"; `:98` | skel:aruvii-git:346-356 refactor Bad (3 changes, one commit) | ADOPT |
| DLG3 | A commit body says why: what was wrong before or what it enables; a body restating the subject fails review. (Body presence: `.husky/commit-msg` gates it.) | ad `git-workflow…:67` "explain the *why*, not just the *what*"; CC v1.0.0 §Spec item 6 (body MAY) → required = **project decision** #455 | #455 bodyless commits reached master; skel:aruvii-git:419-421 restating body passes the hook | ADAPT |
| DLG4 | Subject is `type(scope): subject`; the scope names a module or area, never an issue number. | CC v1.0.0 §Spec item 4 "a noun describing a section of the codebase" | AGENTS.md:366-370 `fix(331): …` wrong rows; old rule until #455 | ADOPT |
| DLG5 | The MR title is `type(area): subject (#NNN)`; it becomes master's only subject line. | GitLab `merge_requests/methods` §Fast-forward merge "without creating merge commits"; trailing `(#NNN)` = **project decision** #455 | !148 squash+merge commit `53830250`; skel:aruvii-git:164-167 | ADAPT |
| DLG6 | The MR description opens with `Closes #NNN`; a bare `#NNN` only links. | GitLab `issues/managing_issues` §Closing issues automatically "merge request description contains text matching the closing pattern" | skel:aruvii-git:134-135 issues left open after merge | ADOPT |
| DLG7 | Stage explicit paths; never `git add -A`, `git add .` or `commit -a`. | oc `AGENTS.md:124` [drift 2026-10-17: cited lines rewritten at d8faf8876; quoted text now at :112, see research/64d] "Stage only intended files" | skel:worktrees.md:15-16 shared-checkout dirt committed under your name | ADOPT |
| DLG8 | Read `git diff --staged` before every commit; no credential, key or `.env` content in it. | ad `git-workflow…:216-220` "Check what you're about to commit"; oc `AGENTS.md:112` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] | #69 floor (no host secrets); `secrets/` symlinked into worktrees (link-worktree-stack-files.sh:10-23) | ADOPT |
| DLG9 | No agent attribution trailer (`Co-Authored-By`, `Generated with`); this repo rule overrides the harness default. | oc `AGENTS.md:112` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "omit agent-attribution trailers" | retro #61 row 10 (precedence unclear) | ADOPT (+ precedence line in AGENTS.md, #646) |
| DLG10 | Check `git config user.name` and `user.email` before the first commit in a new worktree or container. | oc `AGENTS.md:124` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "verified author/writer identities" | AGENTS.md:382-383 invented identity → no GitLab account | ADOPT |
| DLG11 | Decide "merged?" from the GitLab MR `state`, never from `git branch --contains` or `merge-base --is-ancestor`. | GitLab `squash_and_merge` §Long-running branch behavior "a different SHA … Git treats the histories as diverged"; fm `bin/fm-teardown.sh:55 @5f2b81b` | #455 `fix/117` reported lost while on master as `e3fcb09d` | ADOPT |
| DLG12 | The MR body reports only what is knowingly failing, skipped or unverified; no stock praise ("clean", "robust", "I carefully"). | oc `AGENTS.md:94` "Report unrun checks and gaps"; `:23` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "omit stock phrases" | skel:aruvii-git:225-234 | ADAPT → target the owned `visual-pr` skill, not git.md |

### delivery/references/glab.md

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLL1 | Use `glab` for every GitLab read and write; raw git only for local operations and `fetch`/`pull`. | mp `setup-matt-pocock-skills/issue-tracker-gitlab.md:3` "Use the `glab` CLI for all operations" | skel:aruvii-git:15-18 HTTPS prompt hangs an unattended agent | ADOPT |
| DLL2 | Any multi-line body goes through a file: `glab api --method POST/PUT --header "Content-Type: application/json" --input payload.json`; never inline `--field` or a long `glab mr update --description`. | oc `AGENTS.md:124` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "use body files/heredocs for shell-sensitive text" | glab.md:38-44 (415, `@` trap, backticks mangled #279); retro #61 row 18 `glab mr update` timeout | ADAPT |
| DLL3 | A heredoc carrying text with backticks uses a quoted delimiter (`<<'EOF'`). | GNU Bash manual §Redirections › Here Documents "If any part of word is quoted … not expanded" | glab.md:43 #279 comment mangled | ADOPT |
| DLL4 | Read MR state (head SHA, draft, head pipeline, latest status comment) with one reader script, never by scrolling `glab mr view --comments`. | GitLab API `merge_requests` §Get single MR "sha: SHA of the head commit"; `head_pipeline`; ps `playbooks/orchestrate.md:90 @f713f14` "not memory and not the transcript" | retro #61 row 13: 1900 lines to find round/head/verdict | ADAPT — script home OQ4 |
| DLL5 | Correct a mangled or superseded note by editing it (`PUT …/notes/<id>`), never by reposting. | **project decision?** | glab.md:89-90 | project decision? |

### delivery/references/worktrees.md

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLW1 | Never work in the main checkout; one branch per worktree under `.claude/worktrees/<prefix>+<rest>`. | oc `AGENTS.md:21` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "Never switch a checkout while another agent or test run uses it"; ad `git-workflow…:149-171`; Git `git-worktree` §DESCRIPTION | skel:worktrees.md:10-13 build green for a tree that moved | ADOPT |
| DLW2 | Before creating one, run `git worktree list` and test whether you are already inside a worktree (and not a submodule). | oc `AGENTS.md:21` [drift 2026-10-17: cited lines rewritten at d8faf8876; quoted text now at :28, see research/64d] "Inspect `git status -sb` before editing" | skel:aruvii-git:45-57 | ADAPT |
| DLW3 | Never run `make secrets` in a worktree. | **project decision?** (REQ-026) | skel:worktrees.md:34-36 key cannot decrypt shared volume | project decision? — model changes with AP #670 (OQ2) |
| DLW4 | Trust a local smoke result only when its `deployed: <branch> @ <sha>` line equals your head SHA. | ps `playbooks/orchestrate.md:90 @f713f14` "A new head SHA voids the row" | skel:worktrees.md:27-30 last-deployed-branch wins; `COMPOSE_PROJECT_NAME` fallback greens unbuilt code (:38-40) | ADAPT (runner stack is separate, decided #62) |
| DLW5 | A new worktree gets its own frontend deps via `make worktree-setup` (`npm ci` in `aruvii-ui`); never symlink `node_modules` from another checkout. | oc `AGENTS.md:105` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "Never reconcile a shared/worktree install while other jobs use it" | retro #61 row 17; skel:worktrees.md:48-49 symlink "not gitignored at that path" | ADAPT (target name = OQ3) |

### cleanup workflow (OQ1 decides file)

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLC1 | Remove a branch or worktree only when GitLab reports its MR merged and the worktree is clean; uncommitted work blocks removal. | fm `bin/fm-teardown.sh:44` "REFUSES if the worktree holds work that has not LANDED"; `:68` [drift 2026-10-17: cited lines rewritten at 5f2b81b; quoted text now at :44,70, see research/64b] "Uncommitted changes are never landed"; Git `git-worktree` §remove "Only clean worktrees" | cleanup SKILL:105 refusal untested | ADOPT |
| DLC2 | Report by default; delete only on an explicit `--apply`; a dirty worktree only on the literal word `discard`, for that worktree. | fm `bin/fm-teardown.sh:40-42` "--force … authorizes discarding unlanded WORK"; mp `git-guardrails-claude-code/SKILL.md:12-16` (`branch -D`, `clean -f` blocked) | cleanup SKILL:15-17, :56 | ADAPT |
| DLC3 | An empty or failed GitLab answer aborts the sweep; never classify branches on no data. | fm `bin/fm-teardown.sh:68-69 @5f2b81b` "if that is also inconclusive, teardown refuses"; ad `floor-guard.md:11` "Never let a `2` read as a `0`" | cleanup SKILL:59 vacuous-pass shape | ADOPT |
| DLC4 | Touch only worktrees under `.claude/worktrees/`; never `master`, a protected branch, or the current branch. | fm `bin/fm-teardown.sh:114-121 @5f2b81b` (slot ownership before cleanup) | cleanup SKILL:54, :58 | ADAPT |

### delivery/references/verification.md

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLV1 | A gate's result is its own exit code: never pipe `make`/`gradlew` into another command; redirect to a log and print `$?` (or use `pipefail`). | GNU Bash §Pipelines "exit status of the last command in the pipeline, unless the `pipefail` option" | warn-piped-gate.sh:4-5 `make verify \| tail -60` reported green (#500) | ADOPT (hook only advises) |
| DLV2 | Read the executed-test count against what you expected on every run; zero or fewer tests than expected is not a pass. | ad `references/definition-of-done.md:63` "unverified work is not done"; ad `floor-guard.md:11` | verification.md:27-48 `+` filter ran nothing; "13 where you expected 22"; FS:5 RefusalReasonSpec not run | ADAPT |
| DLV3 | A command that can succeed while doing nothing is read for proof it did work: count, report file, row count, or deployed SHA. | ad `references/definition-of-done.md:23` "verified at runtime, not just compiled" | verification.md:72-79; smoke `--reporter=list` ban | ADAPT |
| DLV4 | `FROM-CACHE`/`UP-TO-DATE` at identical inputs is a valid result; use `FRESH=1` only to watch tests execute. | Gradle `build_cache` §Task Output Caching "outputs of the task have been loaded from the build cache" | AGENTS.md:153-159 "115 up-to-date" read as a lie; images pinned (#585) | ADOPT |
| DLV5 | Never lower a bar to reach green: no new skip, suppression, lowered coverage floor, longer timeout or retry; route a real exception through a tracked issue. | ad `floor-guard.md:10` (five moves), `:14` "loosening is loud"; oc `AGENTS.md:88` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "Do not rerun … merely to get green" | AGENTS.md:179-180 `-Djacoco.skip.check=true`; dependencies.md:134 retry-masked smoke (#441) | ADOPT |
| DLV6 | A red test is a defect: reproduce once in the same order, fix the owner, or record the failure and evidence on the MR; never rerun until green. | oc `AGENTS.md:88` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "Never claim a passing replay proves a fix" | FS:6 flake list only in Discord | ADOPT |
| DLV7 | A verification result belongs to one head SHA; a new head voids it, master advancing does not. | ps `playbooks/orchestrate.md:90 @f713f14` "A new head SHA voids the row"; oc `AGENTS.md:38` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "Prior-head CI remains prior-head evidence" | AGENTS.md:470 (Done means: stale once head changes); dod.md:34 | ADOPT (extends #64 idea 1 from review to verification) |
| DLV8 | Before starting a Docker-using build, check for another; a whole module failing at class-init is contention, a partial failure is yours. | **project decision?** | guard-concurrent-build.sh:4-7, 71 false failures | project decision? (hook advises) |

### delivery/references/dependencies.md (+ root AGENTS.md block, ≤3 MUSTs)

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLD1 | Never override a version the Spring Boot BOM manages; an unavoidable override carries a comment with the reason on the same line. | Spring Boot Gradle plugin `managing-dependencies` §Customizing Managed Versions "Overriding versions may cause compatibility issues" | dependencies.md:13-17 three overrides, all wrong (`mssql-jdbc`, `ojdbc11` pinned backwards) | ADOPT → **root MUST** |
| DLD2 | Read a library BOM before importing it; do not import one that manages coordinates the library does not own — pin its artifacts instead. | Spring Boot (as DLD1) + **project decision** for the leak test | dependencies.md:19-23 `jjwt-bom` → databind 2.12.7.1, 81 tests broke | ADAPT → **root MUST** |
| DLD3 | Every dependency change commits the `--write-locks` result for `aruvii-api`/`aruvii-worker`; review reads the lockfile diff. | Gradle `dependency_locking` §Lock State Location "Lockfiles should be checked in to source control"; §Locking Mechanism (transitives `strictly`) | dependencies.md:114-119 (#435) | ADOPT → **root MUST** |
| DLD4 | No pre-release versions (milestone, RC, beta, snapshot). | **project decision?** (oc `AGENTS.md:51` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] covers "beta, and nightly" contracts only) | dependencies.md:42-45 MapStruct 1.7, WireMock 4.0 held | project decision? |
| DLD5 | Versions that must match across ecosystems (Playwright Java ↔ `@playwright/test`) move in one commit; npm side pinned exactly. | **project decision?** | dependencies.md:47-49 browsers 15 minors apart | project decision? |
| DLD6 | Before adopting a test or build dependency, run it once and read its stdout for text addressed to agents; such a library is rejected. | **project decision?** | dependencies.md:30-40 jqwik engine prints an instruction to agents into every build log | project decision? (strong; also a security.md candidate) |
| DLD7 | A new library, BOM import or version override puts the MR on the full lane (G8 floor). | oc `AGENTS.md:119` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "dependency patches/overrides/vendor changes … need explicit approval" | jjwt-bom (81 tests) | ADAPT — OQ5 |
| DLD8 | Pin a static-analysis engine version in `libs.versions.toml`, not only its plugin. | **project decision?** | dependencies.md:25-28 Checkstyle 9.3 unannounced | project decision? |

### root AGENTS.md (L1)

| ID | rule | source | evidence | verdict |
|---|---|---|---|---|
| DLA1 | Command list (≤8 lines): `make help` · `make doctor` · `make test-module`/`it-module MOD= TEST=` · `make verify-module MOD=` · `make verify-fast` · `make smoke` (local only) · `make deploy`. Gates run only through `make`. | oc `AGENTS.md:106` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] "the supported wrappers own build freshness and process setup" | AGENTS.md:93-97 `npm run smoke*` greens replaced code | ADAPT; `verify-full` omitted (R28) |
| DLA2 | Git MUSTs block «about to branch, commit, push or open an MR» (≤3): DLW1 worktree + DLG7 explicit paths · DLG5+DLG6 MR title/`Closes` · DLG9 no attribution trailer. Master protection = hook + decided #50 Q19. | as cited rows | R1:60-64 | ADAPT |
| DLA3 | Dependency MUSTs block = DLD1 · DLD2 · DLD3; Jakarta/Jackson 3 cite ArchUnit (FL17). | as cited rows | — | ADOPT |

## 3 · When X, use Y · Decided edges · Review checks

**When X, use Y**

| situation (observable) | use | why |
|---|---|---|
| post or edit an MR/issue note, labels, state | `glab api … --input payload.json` + Content-Type header | `glab mr note` experimental, `--resolvable` defaults true (glab.md:17) |
| short one-line issue comment | `glab issue note <n> -m` | stable |
| create an MR | `glab mr create --draft --description "$(cat body.md)"` | flag parser, `@` trap does not apply (glab.md:106-110) |
| branch moved under you | local `git rebase origin/master` + `git push --force-with-lease` own branch | decided #50 Q20; Git `git-push` §OPTIONS "updated only if the 'lease' is still valid" |
| need JSON field | `glab api … \| jq -r` | `glab api --jq` does not exist (glab.md:72-80) |
| want a module's tests | `make test-module`/`it-module MOD= TEST=` | `TEST=` matching nothing fails the build (gate) |
| routine version bump | `version-catalog-update` against `libs.versions.toml` | dependencies.md:61 (#456) |
| CVE alert | Renovate `vulnerabilityAlerts` — currently inert; nothing scans | dependencies.md:51-53, 184-193 — gap, not rule |
| where a jar comes from | `./gradlew dependencyInsight --dependency <n>`; tree: `make deps MOD=` | dependencies.md:172-176 |

**Decided edges**

- git.md — **Skip when** a commit is `Merge`/`Revert`/`fixup!`/`squash!`/`amend!`: no body required (hook exempts). **Do not skip when** it is the MR title: no hook sees it; stage 9 human + review check DLG5. — Confidence high.
- git.md — **Skip when** a small rename rides a feature commit (ad `git-workflow…:109` "at reviewer discretion"). **Do not skip when** it is a formatter run. — medium.
- git.md — openclaw `AGENTS.md:38` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] says do not rebase only because main advanced; **we decided otherwise** (#50 Q20: rebase at spawn, before verify, before done) because stale master gave wrong diffs (retro row 4). — high.
- worktrees.md — **Skip when** the change is docs-only and runs no build: a worktree is still required (DLW1), deps setup (DLW5) is not. — medium.
- verification.md — **Skip when** a task shows `FROM-CACHE` at the same SHA: valid (DLV4). **Do not skip when** an IT container image tag is floating: cache key cannot see it (#585). — high.
- verification.md — **Do not skip when** the verifier is blocked/early-stopped or "no checks reported": never green (decided #64 idea 3; ps `orchestrate.md:90 @f713f14` "`verifier-blocked` is not a pass"). — high.
- verification.md — `-Djacoco.skip.check=true` only on a spike branch never opened as an MR. — medium.
- dependencies.md — `dependencyConvergence` OFF, Jackson 2 transitive allowed, test configs unlocked, Develocity declined, errorprone/NullAway out, pitest report-only (M1): each a decided non-rule with its reason (dependencies.md:92-165). — high.
- cleanup — **Skip when** a branch has both an open and a merged MR: active, never touched. — high.

**Review checks** (each names its rule; exhaustive bar)

- git.md: [ ] DLG5 MR title matches `^[a-z]+(\([a-z0-9-]+\))?!?: .+ \(#\d+\)$` (mechanical) · [ ] DLG6 description line 1 is `Closes #NNN` · [ ] DLG2/DLG3 every branch commit walked: one change, body says why · [ ] DLG9 `git log origin/master..HEAD` has no attribution trailer (grep) · [ ] DLG8 diff greps clean for `password|secret|api_key|token` values.
- glab.md: [ ] DLL4 the review packet's head SHA = `mr-state` SHA.
- worktrees.md: [ ] DLW5 no `node_modules` symlink in the diff (`git diff --name-only \| grep node_modules`).
- verification.md: [ ] DLV7 the what-ran note's SHA = MR head · [ ] DLV2 note states test counts per command · [ ] DLV5 diff adds no `@Ignore`/`@PendingFeature`/`.skip`/suppression/lowered floor/timeout without a linked issue (floor-guard pattern, mechanical candidate).
- dependencies.md: [ ] DLD1 every new `version` override in `*.gradle.kts`/`libs.versions.toml` has a reason comment · [ ] DLD3 a dependency diff carries a lockfile diff · [ ] DLD2 a new `platform(...)` import names the BOM read.
- cleanup: [ ] DLC1–DLC4 hand-verified on a fixture after any script edit (no `.test.sh`; cleanup SKILL:96-113).

## 4 · Already decided (do not re-propose)

| item | ticket |
|---|---|
| self-hosted runner = the Verifier; "Pipelines must succeed"; result posted to the MR (retro rows 1, 2) | #35 Q26 · R28 #60 |
| developer minimum before qa (touched-module tests + verify-fast + what-ran note); only the runner runs verify-full/smoke | #35 Q26 · R28 |
| runner owns its own Compose stack; agents never deploy to it | #62 note |
| "no checks reported" never green | #64 idea 3 |
| a review counts only if it covered the head commit | #64 idea 1 |
| workers commit and push their own branch; master protected; operator merges (never `glab mr merge`) | #50 Q19 |
| rebase onto origin/master at spawn/before verify/before done; `--force-with-lease`; conflicts via resolving-merge-conflicts | #50 Q20 |
| `post-status` refuses done unless pushed and not draft (fm `fm-dod-lib.sh:28,84-85 @5f2b81b`) | #50 Q14 |
| MR description shape = owned `visual-pr`, refreshed at stages 5 and 9 (retro row 9) | #50 Q18 · ND-16 |
| `/dod` deleted; items → Review checks; stage 8 = runner + AC citing | ND-5 |
| coordinator never tears down unlanded work; teardown ordered by coordinator | G6 |
| S3 run existing tests before changing code | ledger S3 |
| Jakarta / Jackson 3 → rules/dependencies + ArchUnit; ungated list → meta/gates.md | FL17 · FL18 |
| master key not linked into worktrees | #69 floor → AP #670 |
| machine.env (JAVA_HOME, DOCKER_HOST) + make doctor | ND-15 · R29 |
| Verifier wait timeout (half of retro row 18) | #60 |
| precedence line for attribution trailers in AGENTS.md (retro row 10) | #646 |

## 5 · Open questions

1. **Where do the four procedures live?** Facts: prompt/R12 say `delivery/workflows/{start-work,open-mr,finish-branch,cleanup}.md`; #643 "workflows stay flat skills" already overrode R12 once (FL26, deslop, 9287dc2b); `aruvii-git` was the most model-initiated repo skill (R2:34). start-work/open-mr/finish-branch mostly restate crq stages 6/9 + decided worker-rules. **Recommend:** follow FL26 — one flat `cleanup` skill (human + crq 0/10 + coordinator call it by name); fold start-work/open-mr/finish-branch into crq stage text + `git.md` §procedure; `delivery/SKILL.md` description keeps "Use when … commit or MR".
2. **Worktree secrets model vs #69.** Facts: `scripts/link-worktree-stack-files.sh:10-23` (origin/master) symlinks `secrets/` incl. `master_key` into every worktree; #69 floor says the master key is not linked into worktrees (AP #670). DLW3 + worktrees.md:34-36 describe the current model. **Recommend:** keep only DLW3 ("never `make secrets`") now; worktrees.md says nothing about linking until AP #670 lands; #670 owns the replacement text.
3. **Retro row 17 — worktree `node_modules`.** Facts: no `worktree-setup` target on master Makefile; current advice is a symlink that is not gitignored; dev container (#69 Q2) bakes toolchain, not per-worktree deps. **Recommend:** DLW5 with an AP chore adding `make worktree-setup` (`npm ci` in `aruvii-ui`, idempotent) called by the spawn script; reject the symlink.
4. **Retro row 13 — MR-state reader home.** Facts: GitLab API gives `sha`, `draft`, `head_pipeline`; status words + qa verdict on SHA are structured comments (#50 Q12–13); `post-status` lives in AF. **Recommend:** one AP script `delivery/scripts/mr-state.sh <iid>` printing head SHA · draft · pipeline status · latest status/verdict comment and its SHA; AF `post-status` and the review packet both call it (DLL4).
5. **DLD7 — dependency changes and the lane floor.** Facts: oc requires explicit approval for overrides/new deps; our G8 floor lists migration etc. but not dependencies; jjwt-bom broke 81 tests with a silent diff. **Recommend:** ADAPT as a G8 floor trigger (full lane), not a per-item operator approval — reversible and cheaper.
6. **MR title validated by nothing** (skel:aruvii-git:428-430). Facts: husky never sees it; DLG5 is the only issue link in `git log`. **Recommend:** a cheap runner job (or `post-status`) checks the DLG5 regex and fails; review check stays as backup.
