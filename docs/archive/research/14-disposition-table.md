# R12 · Disposition table — every file's fate, sources, learnings

Ticket: `../issues/22-research-disposition-table.md` · read 2026-10-01 at `e0cc30e8` · words = `wc -w`.
Feeds G9a–G9d (`../issues/23..26`). Decisions cited by ticket id (G1 Q2 = `../issues/05` Q2, G3 amend = `../issues/07`
§Amendment, …). Learnings cited by file:line in this folder.

> **SUPERSEDED IN PART (2026-10-17).** The rows below are the 2026-10-01 picture. Read these changes first; the table
> itself is not rewritten.
>
> | stale in this file | now | where decided |
> |---|---|---|
> | column `AAF` aruvii-agent-fleet (new repo) | no separate repo; all agent side in agent-fleet (AF); split only when a trigger fires | G1 amendment skills #14 (2026-10-03) · #81 |
> | AP holds every skill, reference and crq | generic skills, references (neutral-domain examples) and crq → chiyanram/skills plugin; AP keeps AGENTS.md, nested AGENTS.md, `docs/agents/*.md` answers, Aruvii-only skills | G23 #93 |
> | §Proposed target tree: `.claude/rules/` kept as L2 | `.claude/rules/` deleted; directory MUSTs → `<dir>/AGENTS.md`, file-type MUSTs → root AGENTS.md blocks | G1b skills #72 |
> | §Proposed target tree: AAF column, generic AF `skills/ retro · untouched-and-risk` | see the two ND rows below; layout per G23 | G23 #93 |
> | ND-12 retro: "AF generic skill" | mattpocock `retro` plugin as-is; crq stage 10 retro worker types `/retro` | #50 Q15–Q17 |
> | ND-16 `untouched-and-risk`: "AF plugin skill" | folded into the owned `visual-pr` adaptation, crq stages 5 and 9 | #50 Q18 |
> | "1 unix user" (create-agent, agent-yaml rows, tree) | two zones: `fleet-worker` for all workers (in one dev container image), `fleet-coord`, `fleet-runner` | G13 #69 |
> | souls rendered / SOUL companion | `claude --agent <role>` from a plugin; nothing rendered | G4 #17 |
>
> Current picture: `research/00-decision-register.md` and map #9.

**Legend**

| short | means |
|---|---|
| AP · AAF · AF · UP · U | agent-platform · aruvii-agent-fleet (new) · agent-fleet (generic, GitHub) · upstream plugin · user-level `~/.claude` (laptop only) |
| L1 · L2 · L3 · L4 · A · M | `AGENTS.md` index · path rule (`.claude/rules`, MUSTs only) · skill/reference/workflow · hook/lint · agent-side plugin · per-machine file (G1 res. 1, G4 Q4) |
| SK/ · AS/ · SR · AR | `.claude/skills/` · `SK/aruvii-standards/references/` · `SK/standards-review` · `SK/architecture-review` |
| `T/` | the one skills tree in AP. **Path not decided** — see ND-1 |
| R1 · R2 · R7 · P1 · FS | `01-rule-inventory.md` · `02-skill-pickup.md` · `08-standards-inventory.md` · `../p1/lead-judgment.md` · `00-fleet-self-reports.md` |
| ND-n | NEEDS DECISION — the decided design is silent; question at the end |

Reference repos (paths relative to each clone in `../refs/`, or as cited in `repos/*.md` §6): matt = mattpocock-skills ·
pstack · sp = superpowers · addy · oc = openclaw · fm = firstmate · nm = no-mistakes · hl = humanlayer · ace = hl
advanced-context-engineering · bmad · sk = spec-kit · ecc · acc = Anthropic claude-code plugins · fold.

---

## G9a · testing

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `SK/aruvii-standards/SKILL.md` (1146) | test ladder 0–4; concern→reference router table | L3 · AP · `T/testing/SKILL.md` (ladder, tier choice) + `T/code/SKILL.md` (concern table) | SPLIT→testing/SKILL.md+code/SKILL.md | G1 Q2 (domain skills), G5, R7:15 | pstack `poteto-mode/SKILL.md:37-77` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (one index line per leaf, "read the leaf in full"); matt `writing-for-agents/SKILL.md:78-79` | R7:15 three files claim three different winners (SKILL:12 · java-standards:8-10 · SR:22); `09-wiki-reference-anatomy.md`: crq never orders ladder steps 0–1 |
| `AS/test-value-bar.md` (1021) | should this test exist; retention bar | L3 · AP · `T/testing/references/value-bar.md` | MOVE | G5 (5 sections), R7:33 | oc `.agents/skills/test-audit/SKILL.md:18-66` [drift 2026-10-17: test-audit cut to 57 lines at d8faf8876, detail moved to `references/audit.md`, see research/64d] (4-question gate + junk patterns → Review checks, oc §6 #4); `:111-122` (evidence before deleting) | P1:12 AlertTriggerTypeSpec `valueOf(..) != null` junk test shipped; R7:33 no review criterion today |
| `AS/coverage-design.md` (503) | RIGHT-BICEP | L3 · AP · `T/testing/references/coverage-design.md` | MOVE | G5, R7:21 | addy `skills/test-driven-development/SKILL.md:144-300` (pyramid, good tests); sp `writing-plans/SKILL.md:77-87` (Review Focus: ≤5 untested input classes) | R7:21 no criterion; FS:6 qa "ACs asserting defaults not behaviour" |
| `AS/boundaries-correct.md` (1086) | CORRECT boundary checklist | L3 · AP · `T/testing/references/boundaries.md` | MOVE | G5, R7:18 | sp `writing-plans/SKILL.md:77-87,173` (each input class pinned by a test); pstack `playbooks/autopilot-full.md:8` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (behaviour finding → red test at every site); addy `docs/skill-anatomy.md:96-100 @aeac41d` (rationalizations table) | **P1 F7** (P1:26) boundaries missed although this file was in the packet → its Review checks must name concrete probes, not "consider boundaries" |
| `AS/testing.md` (1263) | test shape, AssertJ, invariants, harness | L3 · AP · `T/testing/references/unit-tests.md` | MOVE | G5, R7:34 | addy `references/testing-patterns.md:16-124`; matt `tdd/tests.md`, `tdd/mocking.md` (point at plugin, never copy); ecc `rules/java/testing.md:11-14` (REJECT content: JUnit+Mockito) | R1:85 AssertJ-vs-Spock contradiction; R1:41 AssertJ in 12 files; P1:11 RunModeSpec "exhaustive" test proves nothing; R7:34 overlap with gherkin-to-test:13-22 |
| `AS/test-quality.md` (1343) | A-TRIP | L3 · AP · `T/testing/references/test-quality.md` | MOVE | G5, R7:32 (merge into unit-tests = G9a call) | addy `testing-patterns.md:33-44` (naming); oc test-audit junk patterns | R7:56 java-standards:15 points GWT here while SR Q-05 points at testing §1 (drift) |
| `SK/it-testing/SKILL.md` (2883) | @EnableAruviiIT, archetypes, fakes, Redis guard, @Scheduled | L3 · AP · `T/testing/references/integration-tests.md` (checklist :341 → Review checks) | MOVE | G5, R7:44 | addy `testing-patterns.md:157-196`; oc test-audit `:18-66` | R1:87 0 Spock mentions vs rules/it-testing.md:62 "every new test is Spock"; R2:48 fired 1× in 530 IT prompts |
| `rules/it-testing.md` (856) | IT placement, 5 Spock rules, language | L2 · AP · `rules/testing.md` (MUSTs, glob = all test paths) + L3 `T/testing/references/spock.md` | SPLIT→rules/testing.md+testing/references/spock.md | G1 res. 1 (L2 = MUSTs only), R7:58, R7 OQ7 | anthropic `spock-best-practices` is a skill, not a ref — none adopted | R1:85-86 AssertJ vs power assertions, `shouldXxx` vs sentence names; R7:58 :62 governs every test but loads only on IT paths |
| `SK/smoke-spec/SKILL.md` (3546) | Playwright authoring + K-00..K-16 rubric | L3 · AP · `T/testing/references/smoke-specs.md` | MOVE | G5 (already author+reviewer in one file, R7:45) | in-repo precedent `smoke-spec/SKILL.md:6-155` / `:156-301` (R7:108); addy `testing-patterns.md:197-235` | FS:6 qa spawned smoke-spec-reviewer as a 3rd subagent; R2:47 0 slash, 4 model |
| `SK/smoke-spec/scripts/check-antipatterns{,.test}.sh` (3657) | mechanical smoke anti-pattern scan | L4 · AP · `T/testing/scripts/` | MOVE | G1 res. 1 (L4) | matt `retro/SKILL.md:19` (mechanical → check) | keeps its own test; referenced by smoke-specs.md Review checks |
| `docs/guides/playwright-rubric.md` (2132) | scored Playwright audit A–H | `T/testing/references/smoke-specs.md` | MERGE→smoke-specs.md, then DELETE | R7:71, R7 OQ10 | — | read by nothing in `.claude/` (R7:71); smoke-spec:83 B1 = rubric:59 D1 |
| `rules/smoke.md` (231) | smoke tiers, DoD gates | L2 · AP · `rules/smoke.md` | KEEP | G1 res. 1, R7:61 | — | — |
| `SK/tdd/{SKILL,mocking,tests}.md` (1311) | TDD loop, seams, anti-patterns | UP · mattpocock `tdd`; repo deltas → `T/testing/SKILL.md` | →PLUGIN(mattpocock-skills tdd) | G1 Q2, Q-5, R7 OQ9 | matt `.agents/invocation.md:16-22` ("Call the Skill tool with tdd" in stage text) | R2:54 never fired — crq.md:260 names it descriptively; **diff vs plugin 1.2.3**: repo copy adds PIT para (`tdd/SKILL.md:34-39`) **and** Beck "make the change easy" (`:40-53`) — both must land in testing/SKILL.md or are lost |
| `SK/gherkin-to-test/SKILL.md` (897) | tier choice, property tests, PIT | L3 · AP · `T/testing/workflows/scenario-to-tests.md` | MOVE | G1 Q2, R7:47 | addy `test-driven-development/SKILL.md:144-187` (pyramid) | R2:61 never fired, named nowhere; 09-wiki: tier choice has no review check |
| `CLAUDE.md` «writing tests» block (198) | 80% coverage, ITs in integrationTest, serial ITs, no H2/MockMvc/@MockitoBean | L2 `rules/testing.md` + L3 testing refs; L1 keeps one pointer line | DELETE (restates rules/testing.md + integration-tests.md) | Q-1, Q-3, R7:70 | bmad `best-practices.md:75-82` (no rule in two loaded files) | R1:44 no-H2 rule in 5 files |
| `CLAUDE.md` «smoke spec» block (61) | smoke FULL=1 before done | L2 `rules/smoke.md` + crq stage 8 | DELETE (restates smoke.md:14) | Q-1, G3 res. (stage 8 = verify-full + smoke) | — | R1:66 rule 28 in 4 places |
| `agents/smoke-spec-reviewer.md` (873) | smoke judgement subagent | review packet: smoke glob → `smoke-specs.md` Review checks | DELETE (replaced by the ONE reviewer, references by path) | G3 Q2 + amend | nm `review_path_instructions.go:31-76` | FS:6 3rd reviewer subagent per round |
| hooks `warn-junit-test-written.sh` (215) · `warn-it-in-src-test.sh` (205) · `warn-mockitobean-in-it.sh` (194) | advisory test hooks | L4 · AP · `.claude/hooks/` | KEEP | G1 res. 1 (L4) | — | #500 nine JUnit files (hook header :3-6); IT misplacement unguarded since #440 |
| `docs/adr/0009-*` (2937) | `src/integrationTest`, serial ITs | AP · ADR | KEEP | R7:72 | — | rules cite it, never restate |
| *(none)* | audit-missing-tests / delete-unneeded-tests workflows (G9a scope) | L3 · AP · `T/testing/workflows/audit.md` | NEW — ND-9 | G9a question | oc `test-audit/SKILL.md:8-14` (author · audit · campaign modes), `:111-122` [drift 2026-10-17: test-audit cut to 57 lines at d8faf8876, detail moved to `references/audit.md`, see research/64d] | `SK/README.md` row: test-value-bar dropped audit/campaign "deliberately" — reviving it reverses that |

## G9b · code + observability

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `AS/comments.md` (729) | banners, restating, why-comments | L3 · AP · `T/code/references/comments.md` | MOVE | G5, R7:19 | pstack `no-comments/SKILL.md:19-24` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (separate reviewer, not the author); oc `deslop/SKILL.md:12-22` [drift 2026-10-17: deslop deleted at d8faf8876, folded into pr-simplify (#173363), see research/64d] | P1:10 V106 header comment false (F3); R1:48 rule in 4 files |
| `AS/types-and-null.md` (592) | null, sealed, `final` | L3 · AP · `T/code/references/types.md` | MERGE→types.md | G5, R7:37, R7 OQ6 (settle in G9b) | pstack `principle-encode-lessons-in-structure/SKILL.md:19-21` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (unrepresentable state > lint > helper > check) | **P1 F6** (P1:25) `final` missed with java-standards in packet; R1:45 `final` in 8 files; R7:56 pointer drift (java-standards:13 → modern-java, SR T-04 → types-and-null §6) |
| `AS/type-design.md` (1170) | domain types, BigDecimal | L3 · AP · `T/code/references/types.md` | MERGE→types.md (survivor) | R7:36, OQ6 | addy `skills/api-and-interface-design/SKILL.md:20-216` [drift 2026-10-17: cited lines rewritten at aeac41d, see research/64d] | P1:14 `verdictReason` String → enum (real F4) |
| `AS/error-handling.md` (1361) | outcome vs fault, ErrorCode | L3 · AP · `T/code/references/errors.md` | MOVE | G5, R7:22 | nm `internal/pipeline/steps/review.go:149-170` (state the invariant, fix every site); addy `api-and-interface-design/SKILL.md:217-269` | R1:49-50 restated in CLAUDE.md:193-194 + java-standards:18-27 |
| `AS/modern-java.md` (1510) | Java 25 features | L3 · AP · `T/code/references/java-modern.md` | MOVE | R7:28, OQ6 | — | R7:28 overlaps concurrency |
| `AS/functional-java.md` (1547) | collectors, pattern matching, async | L3 · AP · `T/code/references/java-functional.md` | MOVE | R7:23, OQ6 | — | self-declared overlap :3-5 |
| `AS/concurrency.md` (542) | virtual threads, pools, locks | L3 · AP · `T/code/references/concurrency.md` | MOVE | R7:20, OQ5 (gets Review checks) | — | R7:20 no criterion today |
| `AS/ood-smells.md` (751) | 8 Fowler smells | L3 · AP · `T/code/references/smells.md` (pushed into every code packet, G3) | MERGE→smells.md (absorbs SR X, 13 smells) | G3 res. (Fowler smells lens), R7:29 | matt `code-review/SKILL.md:38-56` (fold only the few that matter — matt §6 #13 REJECT always-on 12) | P1:17 own-mapper finding (Std 8) |
| `AS/secure-coding.md` (602) | SSRF, decrypt, injection | L3 · AP · `T/code/references/security.md` | MOVE (absorbs CLAUDE.md credentials block + dod §Security) | G5, R7:30, OQ5 | addy `references/security-checklist.md:21-106`; oc `security-triage/SKILL.md:12-79` | R1:83 decrypt scope CLAUDE.md:273 vs dod.md:33 (wider); CLAUDE.md:273-280 15 decrypt sites "nobody has decided" → **ND-4** |
| `AS/services.md` (502) | interface+Default, thin controllers | L3 · AP · `T/code/references/services.md` | MOVE | R7:31 | — | SR L-04..06 → its Review checks |
| `AS/messaging.md` (1272) | Redis Streams vs Kafka, DLT | L3 · AP · `T/code/references/messaging.md` | MOVE | R7:25 | — | SR R-01..03 → Review checks |
| `AS/angular-ui.md` (422) | app-icon, app-select, colour | L3 · AP · `T/code/references/angular-ui.md` | MOVE | R7:16 | — | R1:58 rule in 4 files |
| `rules/angular-ui.md` (82) | 3 UI MUSTs | L2 · AP · `rules/angular-ui.md` | KEEP | R7:62 | — | — |
| `rules/java-standards.md` (741) | 9 Java MUSTs + JPA body :30-67 | L2 `rules/java.md` (MUSTs) + L3 `T/code/references/persistence.md` (JPA); test MUSTs → `rules/testing.md` | SPLIT→rules/java.md+code/references/persistence.md | G1 res. 1, R7:56 | — | R1:76 CLAUDE.md:187-198 near-verbatim copy; R1:89 "rules here win" vs CLAUDE.md:197 "worked examples"; P1 F1 (P1:8) JPA writes `current_version = 1` |
| `CLAUDE.md` «Java» block (138) | layers, AssertJ, final, null, GWT, exceptions | L2 `rules/java.md` / `rules/testing.md` | DELETE (restates java-standards, R1:76) | Q-1, Q-3 | bmad `best-practices.md:75-82` | crq.md:342 is a 3rd copy, deleted with the crq rewrite |
| `CLAUDE.md` «imports/dependencies» block (153) | shared purity, Spring AI in worker, Jakarta, Jackson 3, BOM | L2 `rules/dependencies.md` (Jakarta + Jackson lines) + layering → **ND-2** | MERGE→rules/dependencies.md | Q-1, R1:39-40 | — | R1:88 SR D-02 REFs dependencies.md for Jakarta, 0 hits — only CLAUDE.md:205 defines it |
| `CLAUDE.md` «credentials/encryption/LLM» block (144) | encrypt, mask, rate-limit, decrypt site | L3 `T/code/references/security.md` + one L2 MUST | MERGE→security.md | Q-1 | as security.md | ND-4 |
| `CLAUDE.md` «Angular» block (82) | standalone, app-icon, wired to real API | L2 `rules/angular-ui.md` | DELETE (restates) | Q-1 | — | R1:58 |
| `CLAUDE.md` «API endpoint» block (85) | `/api`, ApiResponse, ProblemDetail, RBAC, PUBLIC_PATHS | **no home** — proposed L3 `T/code/references/api.md` + L2 `rules/api.md` | NEW — ND-3 | design silent (R7 tree has no api file) | addy `api-and-interface-design/SKILL.md:217-269,323-367` | dod.md:36-41 API Contract checklist has no other home |
| `CLAUDE.md` «new tool type» block (223) | dry-run, outputSchemaJson, inputContract | **no home** — `T/code/references/tool-types.md` or module `aruvii-tools/` index | NEW — ND-3 | design silent | — | CLAUDE.md:405-427: outputSchemaJson/sampleResponseJson "missed" by review; dod.md:44-70 Tool-Authoring DoD |
| `SK/deslop/SKILL.md` (1257) | 6 slop categories, diff-only cleanup | L3 · AP · `T/code/workflows/deslop.md` (categories point at code refs) | MOVE | G1 Q2, G3 res. (stage 6 orders domain workflows), R7:50 | oc `deslop/SKILL.md:12-24` [drift 2026-10-17: deslop deleted at d8faf8876, folded into pr-simplify (#173363), see research/64d] ("never instead of" review); pstack `unslop` (pstack.md:38) | R2:46 5/5 fired via "Run the deslop skill"; FS:5 fleet dev skips deslop; deslop:117-119 restates Java MUSTs → delete those lines |
| `rules/observability.md` (563) | level table, 7 logging rules | L2 `rules/observability.md` (MUSTs, literal `action=`) + L3 `T/obs/references/levels.md` (table) | SPLIT→rules/observability.md+obs/references/levels.md | G1 res. 1, R7:57, OQ3 | addy `references/observability-checklist.md:16-23` (on-call questions first) | R1:54 observability.md:23 never says `action=` while CLAUDE.md:296 does; R1:55 PII rule in 8 files |
| `AS/logging.md` (958) | placeholders, exception last, forging | L3 · AP · `T/obs/references/logging.md` | MOVE | R7:24, OQ3 | addy `observability-checklist.md:24-35`; `skills/observability-and-instrumentation/SKILL.md:199-238` (rationalizations, red flags, verify) | customer is on-call (CLAUDE.md:293-300) |
| `AS/metrics.md` (1174) | Micrometer, cardinality | L3 · AP · `T/obs/references/metrics.md` | MOVE | R7:26, OQ3 | addy `observability-checklist.md:36-45` | SR O-07/08 → Review checks |
| `AS/tracing.md` (974) | Brave, sampling, async | L3 · AP · `T/obs/references/tracing.md` | MOVE | R7:35, OQ3 | addy `observability-checklist.md:46-55` | SR O-09/10 → Review checks |
| `CLAUDE.md` «logging» block (80) | action=, WARN/ERROR, duration, no PII | L2 `rules/observability.md` | DELETE (restates) | Q-1 | — | R1:54-55 |

## G9c · migrations · delivery · review packet

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `AS/migration-review.md` (1945) | expand/contract, narrowing, collisions | L3 · AP · `T/migrations/references/review.md` | MOVE | G5, R7:27 | addy `skills/deprecation-and-migration/SKILL.md:67-160`; pstack `references/bugbot-triage.md:7-84` (migration never auto-skipped); G8 floor (migration → full path) | P1:10 V106 UPDATE without rationale (F3); P1:22 NOT VALID+VALIDATE dismissed (header gave the reason); P1:15 VARCHAR vs TEXT = standard-vs-spec, resolved only in round 3 |
| `rules/migrations.md` (1233) | authoring, who migrates, PG design, drift gate | L2 `rules/migrations.md` (MUSTs) + L3 `T/migrations/references/{postgres-design,who-migrates}.md` | SPLIT→rules/migrations.md+migrations/references/* | G1 res. 1, R7:59 | — | #500 took V99: path rule absent on CREATE (hook `check-migration-version.sh:3-7`) |
| `SK/flyway-migration/SKILL.md` (710) | next version, file, DDL safety | L3 · AP · `T/migrations/workflows/new-migration.md` | MOVE | G1 Q2, R7:49 | matt `retro/SKILL.md:19` | R2:43,87-89 one of two skills that fire unprompted ("Use whenever…" + concrete artefact) → keep that wording in `migrations/SKILL.md` description |
| `CLAUDE.md` «schema change» block (52) | never hand-roll; feature flags list | L2 `rules/migrations.md`; flags list → `docs/CONTEXT.md` | DELETE (restates) | Q-1 | — | R1:57 rule in 5 files |
| hooks `block-migration-edit.sh` (125) · `check-migration-version.sh` (334) | block editing applied / colliding versions | L4 · AP | KEEP | G1 res. 1 | — | — |
| `SK/aruvii-git/SKILL.md` (3028) | worktree lifecycle, glab, commit + MR message standard | L3 · AP · `T/delivery/references/git.md` (§5–6 standard) + `T/delivery/workflows/{start-work,open-mr,finish-branch}.md` (§1–4) | SPLIT→delivery/references/git.md+delivery/workflows/* | G1 Q2 | hl `humanlayer-skills/plugins/visual-pr/SKILL.md:29-31,51` (1-sentence why, ≤3 notes); addy `git-workflow-and-versioning/SKILL.md:191-210`; fm `bin/fm-dod-lib.sh:25-49 @5f2b81b` (refuse "done" unless pushed) | R2:34 most model-initiated repo skill (13) → keep "Use when … commit or MR" in `delivery/SKILL.md` description; crq.md:409-418 commit `80f3bb4d` names a stage that no longer exists |
| `SK/aruvii-git/references/glab.md` (861) | glab invocations that work | L3 · AP · `T/delivery/references/glab.md` | MOVE | G1 Q2 | — | — |
| `SK/aruvii-git/references/worktrees.md` (408) | worktree + shared compose stack model | L3 · AP · `T/delivery/references/worktrees.md` (survivor) | MERGE→worktrees.md (absorbs CLAUDE.md worktree block) | Q-1 | fm `AGENTS.md:21-43` (worker per worktree) | G6/G4: port block per worker → machine file, not here |
| `SK/aruvii-cleanup/SKILL.md` (955) | post-merge sweep asking GitLab | L3 · AP · `T/delivery/workflows/cleanup.md`; coordinator brief orders it (G6 teardown) | MOVE | G6 res. 2 | fm `bin/fm-teardown.sh:44-68` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b] (refuses unlanded) | SKILL:19-46 `git branch --contains` false for squash-merged work |
| `AS/verification.md` (642) | green that ran nothing | L3 · AP · `T/delivery/references/verification.md` (survivor; absorbs CLAUDE.md build + CI blocks) | MOVE | R7:38 | sp `executing-plans/scripts/task-done:39-52` (complete only on green exit); addy `constraint-driven-development/references/floor-guard.md`; pstack `playbooks/orchestrate.md:88 @f713f14` | `make verify \| tail` reported green (hook `warn-piped-gate.sh:3-4`); "115 up-to-date" cache lie (CLAUDE.md:170-174); FS:5 RefusalReasonSpec not run; FS:6 early-stopped Verifier, gate status unclear |
| `rules/dependencies.md` (2071) | BOM, deliberate non-rules, Renovate | L2 `rules/dependencies.md` (MUSTs + Jakarta + Jackson 3) + L3 `T/delivery/references/dependencies.md` | SPLIT→rules/dependencies.md+delivery/references/dependencies.md | G1 res. 1, R7:60 | — | jjwt-bom databind downgrade broke 81 tests (CLAUDE.md:213); R1:88 Jakarta REF gap |
| `CLAUDE.md` «build/test/lint/deploy» block (506) | make front door, narrow targets | L1 ≤8-line command list + L3 `verification.md` | SPLIT→AGENTS.md+verification.md | Q-3 | sp `RELEASE-NOTES.md:17`-era bootstrap is ≤65 lines (sp §6 #6) | `TEST=` matching nothing fails (CLAUDE.md:122-125) |
| `CLAUDE.md` «green build / CI» block (595) | no CI, FRESH=1, no tail, concurrent builds, coverage floors, ungated rules | L3 `verification.md`; ungated-rules list → `T/meta/references/gates.md` | MERGE→verification.md (+ gates list) | Q-1 | addy `floor-guard.md` (lowered bar ≠ pass) | #440 98/100 pipelines failed at 0s; semgrep deletion left 6 rules ungated (CLAUDE.md:176-182) |
| `CLAUDE.md` «branch/commit/MR» block (842) | one issue → one MR, MR title, commit body, cz | L3 `T/delivery/references/git.md`; 4 hard MUSTs → L1 | MERGE→git.md | Q-1, Q-3 | bmad `best-practices.md:51` (pointer needs an observable trigger) | R1:60-64 rules 22–26 each in 2–12 places |
| `CLAUDE.md` «worktree» block (119) | shared compose, no `make secrets` | L3 `T/delivery/references/worktrees.md` | MERGE→worktrees.md | Q-1 | — | — |
| hooks `block-commit-on-master.sh` (1052) · `warn-piped-gate.sh` (152) · `guard-concurrent-build.sh` (218) | commit/gate/build guards | L4 · AP | KEEP | G1 res. 1 | — | 71 false failures from concurrent ITs (`guard-concurrent-build.sh:4-6`) |
| `commands/dod.md` (729) | per-change DoD checklist | items → Review checks of `security.md`, testing refs, `api.md`, `tool-types.md`; stage 8 = `make verify-full` + smoke | SPLIT→(review checks), then DELETE — ND-5 | G3 res. ("Stage 8: make verify-full + smoke only") | addy `references/definition-of-done.md:17-60` (standing DoD vs ACs) | R2:44 fired 7× via "Run `/dod`"; dod.md:33 decrypt scope wider than CLAUDE.md |
| `SK/standards-review/SKILL.md` (7511) | 86 criteria, groups L T E C J O Q M U D X R V | each group → Review checks: L→`services`/layering · T→`types` · E→`errors` · C→`comments` · J→`java-*` · O→`obs/*` · Q→`testing/*` · M→`migrations/review` · U→`angular-ui` · D→`delivery/dependencies` · X→`smells` · R→`messaging` · V→`verification` | SPLIT→(each reference's Review checks), then DELETE | G3 Q2 ("deleted, its checks move into the references"), G5 Q1 | acc `code-review/commands/code-review.md:44,55` (rule finding must quote the rule) | R4 preloaded and re-read in 39/57 runs; R1:126 46 KB preload, claims not to restate (:3) but does |
| `SK/code-review/SKILL.md` (1073) | spawns standards + architecture axes | L3 · AP · `T/review/SKILL.md` (build packet → ONE reviewer, two verdicts → lead validates) | MERGE→review/SKILL.md, then DELETE | G3 amend | matt `docs/engineering/code-review.md:54-76` [drift 2026-10-17: cited lines rewritten at 49dd158, see research/64c] (forbid reviewer spawning agents); sp `specs/2026-06-09-sdd-task-scoped-review-dispatch-design.md:54-70` | already repo-edited twice (SK/README.md row); named like the plugin's `/code-review` → new name `review` avoids the clash |
| `agents/code-standards-reviewer.md` (757) | standards subagent def | `.claude/agents/reviewer.md` (thin: read-only tools, no Agent tool, "read the packet") — ND-6 | MERGE→reviewer.md | G2 Q4 (fresh read-only), G3 amend | sk `bug-fix.md:12-44` (role = tool allowlist + output caps); fold `Mode/Rlm.ts:49-73` [drift 2026-10-17: cited lines rewritten at 4bd8c58, see research/64c] | FS:6 135k + 167k per round; P1:30 246k for two axes |
| *(none)* | reviewer prompt + guards | L3 · AP · `T/review/references/reviewer-prompt.md` | NEW | G3 res. + amend | nm `review.go:318-372` (report once w/ all locations, scope-growth → human, "was each piece needed?", reviewed_paths); oc `autoreview:3645-3670` [drift 2026-10-17: script removed at d8faf8876 when autoreview moved to shared `openclaw/agent-skills` (#163397), see research/64d] (repo text = evidence, `incomplete` ≠ clean); acc `security-guidance/hooks/llm.py:751-784` (rounds 2–3: + lines only, prior findings not re-flagged) | P1 F6/F7 (P1:25-26) — A-1 re-run must catch both; #576 findings dribbled over 3–4 rounds (FS:7-8) |
| *(none)* | lead judgment + per-finding validation | L3 · AP · `T/review/references/lead-judgment.md` | NEW | G3 res. + amend | pstack `interrogate/references/lead-judgment.md:16-58`; bmad `step-04-review.md:53-103` (re-verify at file:line, route intent_gap/bad_plan/patch/defer); acc `code-review.md:55-57` (validator per issue) | P1:7-22 the Act-on/Consider/Noted/Dismissed sort; N2 standard-vs-spec routed to analyst |
| *(none)* | packet builder: references by changed path, rules from `master`, matched-refs log | L3 · AP · `T/review/workflows/build-packet.md` | NEW | G3 Q2, G3 defaults | nm `review_path_instructions.go:31-76,161-184` (log unmatched); sp `scripts/review-package`, `re-review-prompt.md:55-100`; acc `security-guidance/README.md:62-70` (byte budget) | `../p1/packet-standards.md` / `packet-spec.md` are the working prototype (19.6k / 14.6k words — too large) |

## G9d · planning · talking · meta · crq · AGENTS.md index

### planning

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `SK/acceptance-criteria-writing/SKILL.md` (674) | AC concision, parameterize, shared setup | L3 · AP · `T/planning/references/acceptance-criteria.md` | MOVE | G1 Q2, R7:48 | sk `converge.md:156-163` (`unrequested` gap); bmad `plan-template.md:21-50` (`<frozen-after-approval>`) | R2:60 never fired ("Used from to-spec" — the plugin's to-spec never names it); FS:6 ACs asserting defaults; P1:9 AC-6 proved only on new rows |
| `SK/spec-review/SKILL.md` (3870) | REQ rubric A/B/C/D/T | L3 · AP · `T/planning/references/spec-review.md`, read by the spec-reviewer role at stage 5 | MOVE | map (spec-design-reviewer dropped), G2 (stage 5 = spec-reviewer) | hl `create_plan.md:338-343` (no open questions); sk `clarify.md:140-179`; ecc `skills/gateguard/SKILL.md:49-73` (fact gate) | FS:7 findings in rounds (#576: 3), unverified existing-behaviour claims, missing Escalation sections, line drift vs HEAD |
| `SK/spec-review/MEMORY.md` (138) | near-miss: defaulted value, un-defaulted reader | its "Decided edges" section | MERGE→planning/references/spec-review.md | G5 (Decided edges), G7 (lesson → owning reference) | pstack `bugbot-triage.md:15-29` (Skip when / Do not skip when / Confidence) | — |
| `SK/architecture-review/SKILL.md` (5243) | A fit · B precedent · C extension · D behaviour · E record · F realised | A–E → L3 `T/planning/references/design-review.md`; F-01 → review Spec verdict | SPLIT→design-review.md+review Spec verdict, then DELETE — ND-7 | G3 res. (removed at stage 7), R7 OQ8 | acc `pr-review-toolkit/commands/review-pr.md:35-43` | R7:69 A-02/03 = SR L-02/03 duplicate; P1:27 N3 group A not covered with no architecture axis |
| `agents/architecture-reviewer.md` (1161) | architecture subagent | none — stage 5 run by spec-reviewer role over design-review.md | DELETE | G3 res., G2 | — | FS:6 a 2nd subagent per qa round |
| `agents/spec-design-reviewer.md` (983) | REQ review subagent | none — human `/approved` + Spec verdict | DELETE | map "Drop spec-design-reviewer", Q-9 | — | FS:7 the fleet spec-reviewer never spawns it |
| `AS/architecture-diagrams.md` (350) | Mermaid in docs | L3 · AP · `T/planning/references/diagrams.md` | MOVE | R7:17, OQ5 | — | R1:90 mermaid vs ASCII contradiction — this file governs **docs** only; reply diagrams belong to the reply card |
| *(none)* | stage-5 program design: types, call-tree diff, file-tree diff | L3 · AP · `T/planning/references/program-design.md` | NEW | map "Not yet specified" | ace `wsff.md:481-570`; hl `create_plan.md:225-240` (Automated vs Manual checks) | hl `ace-fca.md:318-333`: many review rounds = thin plan stage (!230 = 3 rounds) |
| `commands/issue.md` (872) | create / groom / sharpen GitLab issues | L3 `T/planning/workflows/issue.md`; `/issue` entry per ND-1 | MOVE | G1 Q2 | matt `triage/AGENT-BRIEF.md:39-68` | R2:38 2 slash, 1 model |
| `commands/refine.md` (956) | wayfinder on GitLab; human gates; handoff | GitLab ops (:44-92) → `docs/agents/issue-tracker.md`; gates + handoff → `T/planning/workflows/refine.md` | SPLIT→issue-tracker.md+planning/workflows/refine.md | G1 Q2 (per-repo answers in `docs/agents/*.md`) | matt `setup-matt-pocock-skills/SKILL.md:84-110` [drift 2026-10-17: lines added inside the cited range at 49dd158; cited lines now span :84-112, see research/64c] | R2:26 18 slash |
| `commands/v1-status.md` (1119) | v1 progress verified against code | AP · project command (planning) | KEEP (edit: stage-8 AC citing now = Spec verdict) | project-only report | — | v1-status.md:15-30 grep probes reported 4 contradictions |
| `docs/agents/domain.md` (382) · `issue-tracker.md` (680) · `triage-labels.md` (185) | per-repo answers for upstream skills | AP · `docs/agents/` | KEEP (domain.md: "rules live in CLAUDE.md" → AGENTS.md; issue-tracker absorbs refine ops; domain.md absorbs the repo ADR-convention note) | G1 Q2, Q-5 | matt `setup-matt-pocock-skills/SKILL.md:84-110` [drift 2026-10-17: lines added inside the cited range at 49dd158; cited lines now span :84-112, see research/64c] | **vendored `domain-modeling/ADR-FORMAT.md` carries a repo-only note** (aruvii ADR convention) that dies with the copy unless moved here |
| *(none)* | Roles table: analyst · spec-reviewer · developer · qa · human | AP · glossary `docs/CONTEXT.md` §Roles | NEW | G2 Q2 | hl `linear.md:40-53` (status-band ownership); pstack `playbooks/feature.md:3` (one ownership line per stage) | FS:10 "No labels anywhere" |
| `CLAUDE.md` «documentation» block (298) | no stamps, no rotting counts, REQ numbering | REQ numbering → crq stage 3; stamps/counts → **no home** (ND-8) | SPLIT→crq.md+(ND-8) | design silent | bmad `best-practices.md:75-82` | #335 65 stamps, 3 sampled all defective (CLAUDE.md:433-437) |
| `CLAUDE.md` «starting a change» block (121) | /crq first, TDD, ask before designing, names from docs | crq.md stages 2/3/6 + 1 L1 hard rule | SPLIT→crq.md+AGENTS.md | Q-1, G2 | — | R1:59 TDD in 3 files |
| `CLAUDE.md` «sprint / done» block (102) | pre-sprint checklist, "done means" | done → crq stage 8–9; checklist already in `docs/guides/DEVELOPING.md:157` | MERGE→crq.md | Q-1 | — | — |

### talking (agent side)

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `SK/i-have-adhd/SKILL.md` (839) | reply shape, list cap 5 | UP · ayghri/i-have-adhd 0.3.0 (installed); extras → reply card | →PLUGIN(ayghri i-have-adhd) | G1 Q4, Q-6 | — | R2:35,84-86 "invoke it yourself, unprompted" → 1 call in 31 days |
| `SK/show-me/SKILL.md` (647) | diagrams-first, Discord/MR rewrite | UP · humanlayer/skills `plugins/show-me` (not installed yet); Discord/MR extras → reply card | →PLUGIN(humanlayer show-me) | G1 Q4 | hl `show-me/agents/openai.yaml:1-2` (per-harness policy) | R2:22 149 slash, 2 model |
| `SK/teach/` (2801, 5 files) · `SK/wait-what/` (49) | teaching; re-pitch | UP · mattpocock | →PLUGIN(mattpocock-skills teach, wait-what) | Q-6 talking set, Q-5 | — | stale vs plugin 1.2.3 (46 / 4 diff lines) |
| `.claude/always-on/agent-output.md` (880) | orientation, picture-first, reply shape, "skills not optional" | A · AF · reply-card plugin; "skills not optional" (:88-98) → DELETE (Q-4: stage orders skills; merge-conflict line → delivery workflows) | MERGE→reply-card | G1 Q4, Q-6, S-1 | sp `hooks/hooks.json:5`, `hooks/session-start:29-51` (re-inject on startup\|clear\|compact) | R1:82 aligned block vs table contradiction; R1:91 list cap — **ND-10** |
| `.claude/hooks/always-on-output-rules.sh` (114) + `settings.json` SessionStart entry | loads agent-output.md | the reply-card plugin's own SessionStart hook | DELETE | G1 Q4 | sp `hooks/hooks.json:5` | FS:5 dev loads agent-output 5.7 KB + adhd hook |
| `~/.claude/CLAUDE.md` top 4 prefs (~80) | concise; no commit w/o approval; no structural change w/o go-ahead; root cause | U · laptop operator | KEEP | Q-11 (user prefs) | — | fleet worker needs other rules (it commits) — G6 hard rules cover the coordinator |
| `~/.claude/CLAUDE.md` «How to explain» (~400) | ADHD ceiling, one thing, show-me default, go smaller, tables, recommendation first | A · AF · reply card | MERGE→reply-card | G1 Q4 | — | R1:31 rule 31 in 4 places; R1:13 fleet overwrites `~/.claude/CLAUDE.md` → talking prefs lost on VM today |
| `~/.claude/CLAUDE.md` «work-item naming + decisions» (~330) | `#NNN` first, 2–6 words context, decision with context | A · AF · reply card | MERGE→reply-card | G1 Q4 | — | R1:67 duplicates agent-output.md:10 |
| `~/.claude/always-on/orientation.md` (731) + `~/.claude/hooks/always-on-orientation.sh` (155) | orientation + show-me injected each session | A · AF · reply card + its hook | MERGE→reply-card | G1 Q4, S-1 | sp `hooks/session-start:29-51` | 3rd copy of the orientation rule (R1:99) |
| `~/.claude/skills/show-me/SKILL.md` (460) | upstream show-me minus DMI | UP · humanlayer show-me | DELETE | G1 Q4 | — | R1:90 differs from repo copy (Mermaid vs ASCII) |

### meta

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `SK/hook-from-rule/SKILL.md` (693) | ungated rule → hook | L3 · AP · `T/meta/workflows/rule-to-hook.md` — ND-11 | MOVE | G7 (mechanical → check) | matt `retro/SKILL.md:19,29-35`; pstack `principle-encode-lessons-in-structure/SKILL.md:19-21` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; addy `scripts/validate-commands.js:15-17` (parity checks) | R2:59 never fired; CLAUDE.md:59-63 "#310 closed having converted some rules" |
| `CLAUDE.md` «Where things live» rules/hooks prose (~430 of 744) | how layers load; READ not CREATE; loading ≠ enforcing; block vs advise | L3 · AP · `T/meta/references/rule-layers.md` (+ how to place a rule) | MOVE | G1 res. 1 | fm `firstmate-coding-guidelines/SKILL.md:18-64` (placement tree, one owner per fact); oc `AGENTS.md:8` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] ("update at the owner"); bmad `best-practices.md:75-82` | #500 V99: rule absent on CREATE (CLAUDE.md:38-41) |
| *(none)* | retro worker at close + `/lesson`; sort into dropped/check/reference/soul/machine | A · AF generic skill + per-repo owning-file map `docs/agents/lessons.md` — ND-12 | NEW | G7 res. | pstack `reflect/references/synthesizer.md:13-46` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; hl `agent-iteration.ts:76-84`; fm `AGENTS.md:158-160 @5f2b81b` + nm `memory_files.go:12-18` (correct, never add) | matt `retro` sits in plugin 1.2.3 `skills/in-progress/` — not a shippable dependency yet |
| `SK/README.md` (730) | owned vs vendored policy, upstream pin 1.2.3 | AGENTS.md skills row + plugin install step (S-9); provenance → header of each adapted file | DELETE | Q-5 (no vendoring) | — | README:15-20 stale ADR-0003 citation; README:91-93 "crq states each stage without the skills" fallback → obsolete under Q-4 |
| `SK/LICENSE` (244) | MIT for mattpocock + openclaw-adapted text | `T/LICENSE` (still covers deslop, test-value-bar from openclaw) | MOVE | licence requires retention for adapted text | — | — |
| `skills-lock.json` (26 entries) | upstream hashes for vendored skills | plugin version pin in `.claude/settings.json` (enabledPlugins / marketplace) | DELETE | Q-5, G4 Q4 | matt `.claude-plugin/plugin.json:21-49` | lock lists 7 skills never vendored (claude-handoff, handoff, implement, loop-me, setup-pre-commit, wizard, writing-for-agents) — already drifted |
| `.claude/settings.json` hooks (PreToolUse, PostToolUse) | registers 8 project hooks | L4 · AP | KEEP minus `warn-decrypt-outside-handler.sh` entry | G1 res. 1 | — | R1:84,125 entry points at a deleted file — live config bug |

### crq + AGENTS.md index

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `commands/crq.md` (4721) | 11 stages, gates, stage 7 axes, stage 8 AC citing | AP · `crq.md` (location ND-1), rewritten: role label per stage, stage-1 type×size mask, `skip: <reason>`, "Call the Skill tool with X", stage 7 = `review`, stage 8 = verify-full + smoke | KEEP (rewrite) | G2 res. 1, G8, G3 amend, Q-4, Q-8 | pstack `poteto-mode/SKILL.md:117` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; ecc `skills/orch-pipeline/SKILL.md:39-54`; matt `.agents/invocation.md:16-22`; acc `feature-dev/commands/feature-dev.md:57-92` (stop wording) | FS:5-8 nobody runs /crq end to end; crq.md:40 "never skip a stage" vs G8 mask; crq.md:342 3rd copy of Java rules; R2:74-76 "Run X" fires, descriptive mention does not |
| `CLAUDE.md` (4685) as a file | always-on rules, 60% of startup | `CLAUDE.md` = `@AGENTS.md` (one line) | SPLIT→(rows above; becomes `@AGENTS.md`) | G1 res. 1 + post-close test | sp `RELEASE-NOTES.md:17`; bmad `best-practices.md` (CLAUDE.md = @AGENTS.md) | R1:122 CLAUDE.md ≈ 60% of fixed cost |
| `AGENTS.md` (symlink → CLAUDE.md) | same bytes as CLAUDE.md | L1 · AP · real file, <200 lines | KEEP (invert: becomes the source) | G1 res. 1, Q-2, Q-3 | matt `retro/SKILL.md:41` ("used incredibly sparingly … navigation pointers"); oc `AGENTS.md:8` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] | today `ls -la AGENTS.md` → `CLAUDE.md` (symlink) |
| `CLAUDE.md` header + stack line (~40) | product + stack | L1 head | KEEP | Q-3 | — | — |
| `CLAUDE.md` «Where things live» table (~310 of 744) | doc map, skills row, subagents row | L1 table: domain skills, no subagent row, Roles pointer | KEEP (rewrite) | G1, G3 | matt `setup-matt-pocock-skills/SKILL.md:84-110` [drift 2026-10-17: lines added inside the cited range at 49dd158; cited lines now span :84-112, see research/64c] (`## Agent skills` pointer block) | subagents row describes 3 axes that G3 deletes |
| `CLAUDE.md` «Slash commands» (88) | /crq /issue /refine /dod | L1 | KEEP (drop /dod per ND-5) | Q-3 | — | — |
| `aruvii-*/CLAUDE.md` ×6 (509–1536) | module rules | not inventoried by this ticket | — ND-13 | — | sk/oc: nested `AGENTS.md` per dir | Codex reads nested `AGENTS.md`, not `CLAUDE.md` (S-8) |

## Agent side · aruvii-agent-fleet / agent-fleet

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `docs/agents/personas/analyst.md` (819) | soul + intake process + approval gate + tone | soul/tone/ownership → A · AAF `agents/analyst.md`; process → crq stages 1–3 | SPLIT→AAF agents/analyst.md+crq.md | G1 Q3, G2 res. 1, Q-11, T3 | oc `docs/reference/templates/roles/*/workspace/AGENTS.md` (5 headings incl. Handoff contract); hl `create_plan.md:40-47,95-99` | analyst.md:13 "/crq is a tool, not a process" (process written twice); FS:8 unverified repo facts (#585), contradicts decided work (D-F8 vs #533), gaps one per round (#576: 4) |
| `docs/agents/personas/developer.md` (1107) | soul + implement + review rounds + attribution | soul → AAF `agents/developer.md`; process → crq stage 6; fix-round rules → crq; attribution → `delivery/references/git.md` | SPLIT→AAF agents/developer.md+crq.md | G2 res. 1, Q-11 | nm `review.go:149-170` (fixer rules); fm `bin/fm-brief.sh:699-714 @5f2b81b` (status words, "same obstacle twice → blocked") | FS:5 skips /dod, stage 7, deslop; 3 days silent; developer.md:9-11 lists 8 skills to "read" (none ordered) |
| `docs/agents/personas/qa.md` (751) | independence, REVIEW, VERIFY, findings | minimal soul → AAF `agents/qa.md`; REVIEW → `T/review/`; VERIFY → crq stage 8 | SPLIT→AAF agents/qa.md+review/+crq.md | G2 Q4, G3 amend | bmad `CHANGELOG.md:388` (qa = fresh process with packet, not a soul); oc `auto-qa/SKILL.md:34` (discard if head SHA changed) | FS:6 gate status unclear (flake list only in Discord) → handoff comment shape |
| `docs/agents/personas/spec-reviewer.md` (690) | story pre-check + full spec review | soul → AAF `agents/spec-reviewer.md`; checklists → `planning/references/spec-review.md`; when → crq stage 5 | SPLIT→AAF agents/spec-reviewer.md+spec-review.md | G2, map destination | ecc `gateguard/SKILL.md:49-73` | FS:7 ~29k tokens/round, missing Escalation sections |
| *(none)* | coordinator persona + 5 hard rules + relay-with-context | A · AAF `agents/coordinator.md` | NEW | G6 res. 3–4, G4 Q3 | fm `AGENTS.md:21-43,316-364 @5f2b81b`; oc `roles/coordinator/workspace/AGENTS.md:21-42`; fold `Mode/Rlm.ts:49-73` [drift 2026-10-17: cited lines rewritten at 4bd8c58, see research/64c] (no shell) | addy `orchestration-patterns.md:316-326` anti-pattern C (human checkpoints, paraphrase drift, double tokens) |
| *(none)* | worker brief template (refuse spawn if a field is missing) | A · AAF `briefs/worker-brief.md` | NEW | G6 post-close | pstack `playbooks/orchestrate.md:25,34-56` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; fm `bin/fm-brief.sh:629-636 @5f2b81b` (captain's words kept apart); matt `triage/AGENT-BRIEF.md:39-68` | P1 packets show what a pushed-in brief costs |
| *(none)* | GitLab handoff comment shape (role · round · #NNN, status word) | A · AAF `briefs/handoff-comment.md` | NEW | G2 Q3, G4 Q1 | fold/agentlayer `docs-agent/src/github.ts:29-33` (one idempotent comment per agent+MR); hl `create_handoff.md:43-64` | FS:10 handoffs = Discord @mention + comment, no labels |
| AF `scripts/create-agent.sh:355-390,500` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :375-426,548, see refs/README.md] | renders role `~/.claude/CLAUDE.md` (header, Discord, toolchains, purpose, SOUL, guardrails, app/verifier/skills) | identity → AAF plugin (`claude --agent <role>`); repo path/ports/Verifier → M machine file; Discord → coordinator only | SPLIT→AAF plugin+machine file | G4 Q4, R8 D3/D4 | fm `bin/fm-dod-lib.sh:108-122` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b] (role injected at launch) | R1:13,26 role file 13–15 KB replaces `~/.claude/CLAUDE.md` |
| AF `<fleet>/agents/<name>/SOUL.md` (per agent, outside git, `chmod 600`) | role soul | A · AAF `agents/<role>.md` (in git, plugin) | MOVE | G1 Q3, G4 Q4, Q-7 | oc §6 #13 REJECT self-evolving SOUL | R1:68 soul ×3 copies (persona, SOUL.md, rendered CLAUDE.md) |
| AF `.claude/skills/create-agent/agent-yaml.md` (1323) | agent.yaml schema: skills (copied), plugin_skills | AF · schema: drop `skills` copy + SOUL companion; `plugin_skills` lists AAF + reply card; one unix user | KEEP (amend) | G4 Q1, Q4 | — | agent-yaml.md:18 fleet skills copied root-owned (a 2nd copy route) |
| AF `enforcement/managed-settings.json` · `fleet-guard.py` | VM-wide settings + hard guardrails | AF · add enabledPlugins (VM); coordinator: no Edit/Write on project worktrees | KEEP (amend) | G4 Q4, G4 R11 default | fold `Rlm.ts:49-73` [drift 2026-10-17: cited lines rewritten at 4bd8c58, see research/64c] | D4: agent owns `~/.claude` → identity not locked |
| AF `skills/dockerize-and-verify/SKILL.md` (460) | containerize + verify a project | AF generic skill | KEEP — ND-14 | G1 Q3 (generic tooling) | — | it reads/writes `~/.claude/knowledge/<repo>.md`, a lesson store outside G7's MR route |
| *(none)* | reply card (talking extras) + SessionStart hook | A · AF plugin `reply-card` | NEW | G1 Q4, Q-6 | sp `hooks/session-start:29-51`; addy (no 2nd SessionStart router, addy §1) | sources: agent-output.md, ~CM «explain»/«naming», orientation.md |
| *(none)* | per-machine file (repo path, port block, Verifier URL, JAVA_HOME, DOCKER_HOST) | M · AF provisions | NEW — ND-15 | G4 Q4, G7 Q2 default | fm `AGENTS.md:48,59 @5f2b81b` (per-home gitignored config) | FS:5 OOM, unset JAVA_HOME/DOCKER_HOST, /tmp ownership |
| `~/.claude/skills/untouched-and-risk/SKILL.md` (573) | MR summary: what was not touched, riskiest spot | ND-16 | — | Q-11 vs Q-1 | hl `visual-pr/SKILL.md:29-31` | overlaps aruvii-git:188-197 "Worth a reviewer's attention" |
| `~/.claude/skills/wiki/SKILL.md` (2240) | personal reference corpus search | U · laptop | KEEP | operator tool, not fleet | — | used for G5 (`09-wiki-reference-anatomy.md`) |
| `~/.claude/skills/improve-claude-md/SKILL.md` (1489) | `<important if>` CLAUDE.md rewriting | U · laptop | KEEP (not the AGENTS.md rubric — matt `writing-for-agents` is, matt §6 #1) | G1 res. 1 | matt `writing-for-agents/SKILL.md:10-81` | today's CLAUDE.md is its output: 19 `<important if>` blocks, 4.7k words |

## Upstream plugin rows (vendored copies → delete; plugin is the whole upgrade, S-6)

All are mattpocock-skills 1.2.3 unless named. "diff" = changed lines repo copy vs installed plugin 1.2.3.

| current file (path, words) | what it holds | target | action | why | reference excerpts | our learnings |
|---|---|---|---|---|---|---|
| `SK/grilling` (136) · `SK/grill-me` (20) · `SK/grill-with-docs` (34) | relentless interview; wrappers | UP | →PLUGIN(mattpocock-skills) | G1 Q2, Q-5 | — | R1:97 two are 1-line wrappers; diff 24/2/2 |
| `SK/domain-modeling` (+ADR-FORMAT, CONTEXT-FORMAT; 1390) | glossary + ADRs | UP; repo ADR note → `docs/agents/domain.md` | →PLUGIN(mattpocock-skills) | Q-5 | — | ADR-FORMAT.md:5-11 repo-only paragraph (see docs/agents row) |
| `SK/wayfinder` (2023) | map of decision tickets | UP; GitLab answers in `docs/agents/issue-tracker.md` | →PLUGIN(mattpocock-skills) | Q-5 | — | diff 74 |
| `SK/research` (133) · `SK/prototype` (+LOGIC, UI; 2558) | research, prototypes | UP | →PLUGIN(mattpocock-skills) | Q-5 | pstack `poteto-mode/SKILL.md:20` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (ask-or-test) | R2:58 prototype never fired |
| `SK/triage` (+AGENT-BRIEF, OUT-OF-SCOPE; 2976) | triage state machine, brief | UP; AGENT-BRIEF adapted (cited, not copied) into AAF brief | →PLUGIN(mattpocock-skills) | Q-5 | matt §6 #5, #9 (`.out-of-scope/` KB for rejected rules) | diff 106 |
| `SK/to-spec` (625) · `SK/to-tickets` (909) · `SK/to-questionnaire` (477) | synthesis to tracker | UP | →PLUGIN(mattpocock-skills) | Q-5 | — | DMI; R2:62 slash only |
| `SK/improve-codebase-architecture` (+HTML-REPORT; 1851) · `SK/codebase-design` (+DEEPENING, DESIGN-IT-TWICE; 1655) | deep-module vocabulary | UP | →PLUGIN(mattpocock-skills) | Q-5 | — | R2:56 codebase-design never fired |
| `SK/diagnosing-bugs` (+hitl script; 1680) | diagnosis loop | UP | →PLUGIN(mattpocock-skills) | Q-5 | — | R2:55 never fired |
| `SK/resolving-merge-conflicts` (134) | conflict procedure | UP; delivery workflows order it | →PLUGIN(mattpocock-skills) | Q-4, Q-5 | — | R2:23 55 slash; agent-output.md:90-95 "build before --continue" |
| `SK/tdd` | (row in G9a) | UP | →PLUGIN(mattpocock-skills) | — | — | repo deltas → testing/SKILL.md |
| `SK/teach` · `SK/wait-what` | (row in talking) | UP | →PLUGIN(mattpocock-skills) | — | — | — |
| *(installed, not vendored)* `writing-for-agents` | rubric for rewriting AGENTS.md + references | UP | →PLUGIN(mattpocock-skills) — already | matt §6 #1 | `writing-for-agents/SKILL.md:10-81` | — |
| *(in plugin, in-progress)* `retro` | lesson loop | UP — not yet shippable | — ND-12 | G7 | `retro/SKILL.md:7-25` | path `skills/in-progress/retro` |
| *(plugin, unused)* `code-review` | Standards ‖ Spec, 12 smells always | not used; ours is `T/review/` | — | G3 amend; matt §6 #13 REJECT | — | name clash avoided by naming ours `review` |
| SK/show-me → humanlayer/skills `plugins/show-me`; SK/i-have-adhd → ayghri/i-have-adhd | talking | UP | (rows in talking) | G1 Q4 | — | humanlayer plugin **not installed** on this laptop (`~/.claude/plugins/cache` has no humanlayer) |

---

## Counts per action

| action | rows |
|---|---|
| MOVE | 35 |
| SPLIT→x+y (incl. 4 "then DELETE": aruvii-standards SKILL, dod, standards-review, architecture-review) | 20 |
| KEEP (incl. amend / rewrite) | 20 |
| MERGE→x (incl. 2 "then DELETE": playwright-rubric, code-review) | 18 |
| →PLUGIN | 16 |
| NEW (no current file) | 14 |
| DELETE (outright) | 13 |
| no action yet / cross-reference rows | 5 |
| **total rows** | **141** |

Counts are rows, not files (a row may hold 2–5 files, e.g. the three test hooks). Files that end up gone from AP
(DELETE + →PLUGIN + "then DELETE"): 4 agents, `/dod`, 19 vendored skill dirs, `standards-review`,
`architecture-review`, `code-review`, `README.md`, `skills-lock.json`, `always-on/`, 1 hook, ~4.0k words of CLAUDE.md.

## Content with NO home yet

| content | today at | question |
|---|---|---|
| API contract: `/api`, `ApiResponse<T>`, ProblemDetail, RBAC tested, PUBLIC_PATHS = security decision | `CLAUDE.md:256-266`, `dod.md:36-41` | ND-3 |
| New-tool-type contract: dry-run, outputSchemaJson, sampleResponseJson, inputContract | `CLAUDE.md:405-427`, `dod.md:44-70` | ND-3 |
| Layering / domain purity / Spring AI only in worker / `aruvii-shared` zero Spring | `CLAUDE.md:187`, `:202-203`; SR L-01..03; AR A-02/03 | ND-2 |
| Doc-writing rules: no `[confirmed:]` stamps, no rotting counts, doc-drift section | `CLAUDE.md:429-453` | ND-8 |
| Decrypt rule — has a home (`security.md`) but its content is undecided | `CLAUDE.md:273-282` vs `dod.md:33` | ND-4 |
| "Rules with no gate" list (semgrep gone, CVE scan gone) | `CLAUDE.md:176-182` | proposed `T/meta/references/gates.md` — part of ND-11 |
| Repo deltas inside "vendored" copies: tdd PIT + Beck rule; domain-modeling ADR note | `SK/tdd/SKILL.md:34-53`; `SK/domain-modeling/ADR-FORMAT.md:5-11` | homes proposed above; must be moved **before** the copies are deleted |
| Agent knowledge file `~/.claude/knowledge/<repo>.md` | AF `dockerize-and-verify` | ND-14 |
| Module `aruvii-*/CLAUDE.md` ×6 | module roots | ND-13 |

## NEEDS DECISION

| # | question | options (state now) | recommendation |
|---|---|---|---|
| ND-1 | Where is the one skills tree, and are `/crq` `/issue` `/refine` commands or skills? | today `.claude/skills/` + `.claude/commands/` (Claude-only); S-8 needs a harness-neutral tree | `.agents/skills/` + `.claude/skills` symlink; crq/issue/refine as user-invoked skills (DMI); Codex flat copy later (G4 caveat, matt ADR-0002:15) |
| ND-2 | Home for layering / domain purity / Spring-AI-in-worker | not in R7 tree; 3 sources | `T/code/references/layering.md` + 3 MUSTs in `rules/java.md` |
| ND-3 | Home for API contract and new-tool-type contract | CLAUDE.md + dod only | `T/code/references/api.md` (+ `rules/api.md` on controllers/SecurityConfig); tool-type → nested `aruvii-tools/AGENTS.md` + `T/code/references/tool-types.md` |
| ND-4 | Decrypt rule: only `ToolHandler.execute()`, or wider? | CLAUDE.md:273 vs dod.md:33; 15 sites | operator decides; rule text then lives once in `security.md` |
| ND-5 | Does `/dod` survive as a thin stage-8 command? | G3 says stage 8 = verify-full + smoke only | delete `/dod`; stage 8 text runs `make verify-full` |
| ND-6 | Where the reviewer subagent definition lives | project (`.claude/agents/reviewer.md`) vs AAF plugin | project side — it is part of `T/review/`, not a soul |
| ND-7 | Merge `design-review.md` (AR A–E) into `spec-review.md`? | two stage-5 rubrics, 9.1k words | merge into one stage-5 reference, G5-shaped |
| ND-8 | Home for doc-writing rules | CLAUDE.md only | `T/planning/references/writing-docs.md` |
| ND-9 | Revive openclaw audit/campaign test modes as workflows? | test-value-bar dropped them deliberately | yes, as `testing/workflows/audit.md`, operator-invoked only |
| ND-10 | Reply card: compare in a markdown table or an aligned code block? mermaid or ASCII? list cap? | agent-output:51-64 vs ~CM:30; :48 vs show-me | table for compare; ASCII in chat, mermaid in docs; cap 5 |
| ND-11 | Is `meta/` its own AP domain skill? | hook-from-rule + rule-layers + gates | yes — 8th domain, small |
| ND-12 | Where the retro / `/lesson` skill lives | matt `retro` is in-progress | AF generic skill + `docs/agents/lessons.md` per repo |
| ND-13 | Module `aruvii-*/CLAUDE.md` → nested `AGENTS.md`? | 6 files, 6.1k words | yes, same `@AGENTS.md` inversion; inventory in its own ticket |
| ND-14 | `~/.claude/knowledge/<repo>.md` vs G7 MR route | agent writes it freely | fold into machine file / G7 retro route |
| ND-15 | Machine file name and format | none exists | `~/.config/agent-fleet/machine.env` (key=value, sourced) |
| ND-16 | `untouched-and-risk`: AF plugin, or merge into `delivery/references/git.md` MR section? | user-level, laptop only | AF plugin skill; git.md points at it |

## Proposed target tree

```
agent-platform (AP)                                 aruvii-agent-fleet (AAF, new)
├── AGENTS.md            L1 index <200 lines         ├── .claude-plugin/plugin.json + marketplace.json
├── CLAUDE.md            "@AGENTS.md"                ├── agents/
├── docs/CONTEXT.md      + §Roles (G2)               │   ├── coordinator.md   (5 hard rules, relay)
├── docs/agents/         domain · issue-tracker ·    │   ├── analyst.md · spec-reviewer.md
│                        triage-labels · lessons(ND12)│   └── developer.md · qa.md (souls + "you take: <label>")
├── .claude/                                         └── briefs/
│   ├── rules/           java · testing · obs ·          ├── worker-brief.md
│   │                    migrations · dependencies ·     └── handoff-comment.md
│   │                    smoke · angular-ui (+api ND3)
│   ├── hooks/           8 project hooks (L4)        agent-fleet (AF, generic)
│   ├── agents/reviewer.md   (ND-6)                  ├── plugins/reply-card/  (hook + card)
│   ├── settings.json    hooks + enabledPlugins      ├── skills/ dockerize-and-verify · retro (ND12)
│   └── skills -> ../.agents/skills   (ND-1)         │          · untouched-and-risk (ND16)
└── .agents/skills/  (T/)                            ├── scripts/ create-agent (1 unix user, no
    ├── crq/ · issue/ · refine/ (ND-1) · v1-status        rendered soul) · update · delete · list
    ├── testing/   SKILL · references/{value-bar,    ├── enforcement/ managed-settings (plugins),
    │              coverage-design, boundaries,           fleet-guard (coordinator tool set)
    │              unit-tests, test-quality, spock,  └── machine file template (ND-15)
    │              integration-tests, smoke-specs} ·
    │              workflows/{scenario-to-tests,     upstream plugins (UP)
    │              audit(ND9)} · scripts/            ├── mattpocock-skills 1.2.3: grilling, grill-me,
    ├── code/      SKILL · references/{comments,     │   grill-with-docs, domain-modeling, wayfinder,
    │              types, errors, services, layering │   research, prototype, triage, to-spec,
    │              (ND2), api+tool-types (ND3),      │   to-tickets, to-questionnaire, tdd,
    │              java-modern, java-functional,     │   codebase-design, improve-codebase-architecture,
    │              concurrency, smells, security,    │   diagnosing-bugs, resolving-merge-conflicts,
    │              messaging, persistence,           │   teach, wait-what, writing-for-agents
    │              angular-ui} · workflows/deslop    ├── humanlayer/skills show-me
    ├── obs/       references/{levels, logging,      └── ayghri/i-have-adhd
    │              metrics, tracing}
    ├── migrations/ references/{review, postgres-design, who-migrates} · workflows/new-migration
    ├── delivery/  references/{git, glab, worktrees, verification, dependencies}
    │              · workflows/{start-work, open-mr, finish-branch, cleanup}
    ├── review/    SKILL · references/{reviewer-prompt, lead-judgment} · workflows/build-packet
    ├── planning/  references/{acceptance-criteria, spec-review(+design-review ND7),
    │              program-design, diagrams, writing-docs(ND8)} · workflows/{issue, refine}
    ├── meta/      references/{rule-layers, gates} · workflows/rule-to-hook   (ND-11)
    └── LICENSE    (openclaw-adapted text)

user-level (laptop only): ~/.claude/CLAUDE.md = 4 operator prefs · skills/wiki · skills/improve-claude-md
```
