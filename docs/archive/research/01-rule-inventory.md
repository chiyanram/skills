# R1 · Rule inventory — every rule → every place it is stated

Ticket: `issues/01-research-rule-inventory.md` · Sources read 2026-10-01 at `e0cc30e8` · paths relative to
repo root; `sk/` = `.claude/skills/`, `AS/` = `sk/aruvii-standards/references/`, `~CM` = `~/.claude/CLAUDE.md`.
Bytes from `wc -c`; tokens ≈ bytes/4.

## 1. Sources — size and when they load

| source | words | bytes | loads |
|---|---|---|---|
| `CLAUDE.md` | 4,685 | 31,615 | startup (every session, every subagent) |
| `.claude/always-on/agent-output.md` | 880 | 5,656 | startup + resume/clear/compact — `SessionStart` hook `always-on-output-rules.sh` (`settings.json`) |
| `~CM` (user global) | 806 | 4,445 | startup, laptop only — fleet overwrites `~/.claude/CLAUDE.md` with the role file (`agent-fleet/scripts/create-agent.sh:548 @080aabb`) |
| skill + agent + command `description:` (model-invocable, repo only) | — | 11,406 | startup (listing); plugin/global skill descriptions extra, not counted |
| `rules/java-standards.md` + `rules/observability.md` | 741 + 563 | 5,133 + 3,738 | path-scoped, first read of `**/*.java` |
| `rules/it-testing.md` | 856 | 5,546 | read of `*IT.java`/`*IT.groovy`/`*Spec.groovy` |
| `rules/dependencies.md` | 2,071 | 13,678 | read of build files / `package.json` / `renovate.json` |
| `rules/migrations.md` | 1,233 | 8,407 | read under `**/db/migration/**` |
| `rules/smoke.md` · `rules/angular-ui.md` | 231 · 82 | 1,494 · 646 | `**/smoke-*.spec.ts` · `aruvii-ui/**` |
| `commands/crq.md` · `dod` · `issue` · `refine` · `v1-status` | 4,721 · 729 · 872 · 956 · 1,119 | 27,838 · … | on `/command` |
| `agents/architecture-reviewer.md` + preloaded `sk/architecture-review` | 1,161 + 5,243 | 7,155 + 32,244 | subagent start (`skills:` frontmatter) |
| `agents/code-standards-reviewer.md` + `sk/standards-review` | 757 + 7,511 | 4,812 + 46,227 | subagent start |
| `agents/spec-design-reviewer.md` + `sk/spec-review` | 983 + 3,870 | 6,046 + 24,758 | subagent start |
| `agents/smoke-spec-reviewer.md` + `sk/smoke-spec` | 873 + 3,546 | 6,142 + 23,988 | subagent start |
| `docs/agents/personas/{analyst,developer,qa,spec-reviewer}.md` | 819 / 1,107 / 751 / 690 | 4.3–6.9 K | never by Claude Code; source text for fleet `SOUL.md` (REQ-535) |
| fleet role `~/.claude/CLAUDE.md` | — | ~13–15 K | fleet startup; = header + Discord + toolchains + `purpose` + `SOUL.md` + `guardrails` + app/verifier/skills (`create-agent.sh:355-390` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :375-426, see refs/README.md]) |

Skills (34) — on invoke; SKILL.md words / all .md words: `aruvii-standards` 1,146 / **23,405** (161 KB, references loaded one at a time) ·
`standards-review` 7,511 · `architecture-review` 5,243 · `aruvii-git` 3,028 / 4,297 · `spec-review` 3,870 / 4,008 · `smoke-spec` 3,546 ·
`it-testing` 2,883 · `wayfinder` 2,023 · `teach` 1,490 / 2,801 · `triage` 1,005 / 2,976 · `diagnosing-bugs` 1,483 · `deslop` 1,257 ·
`code-review` 1,073 · rest < 1,000 each; `grill-me` 20, `grill-with-docs` 34, `wait-what` 49 (all `disable-model-invocation`).

## 2. Rule × location matrix

D = DEFINES · R = RESTATES (rule text repeated) · P = POINTS-AT (names it, sends you elsewhere). Line = first hit.

| # | rule | D | R | P |
|---|---|---|---|---|
| 1 | Jackson 3 (`tools.jackson.*`) | CLAUDE.md:209 | dependencies.md:111 · standards-review:597 (D-03) | CLAUDE.md:167,181 · standards-review:40 · hook-from-rule:86 |
| 2 | Jakarta, not EE `javax.*` | CLAUDE.md:205 | standards-review:590 (D-02) | — (D-02 REF → dependencies.md, which never says Jakarta) |
| 3 | AssertJ only | CLAUDE.md:190 · java-standards:12 | standards-review:431 · AS/testing.md:3 · crq.md:342 · arch-review:358 | CLAUDE.md:168,181 · deslop:118 · hook-from-rule:87 |
| 4 | Spock for every new test | it-testing.md:62 | CLAUDE.md:4 | CLAUDE.md:49 (hook) · hook-from-rule:24 |
| 5 | ITs under `src/integrationTest` | CLAUDE.md:223 (ADR-0009) | it-testing.md:12 · sk/it-testing:23 · standards-review:424 | — |
| 6 | no H2 / no MockMvc / no `@MockitoBean` | sk/it-testing:3,12 | CLAUDE.md:233 · it-testing.md:103 · standards-review:469 · dod.md:24 | CLAUDE.md:50 (hook) |
| 7 | `final` wherever applicable | java-standards:13 | CLAUDE.md:190 · AS/types-and-null:3 · standards-review:136 · crq.md:306,342 | deslop:117 · arch-review:358 |
| 8 | no `null` to decide a case | java-standards:14 | CLAUDE.md:190 · AS/types-and-null:3 · standards-review:138 · crq.md:342 | deslop:77 · AS/type-design:8 |
| 9 | Given/When/Then + `shouldXxx` | java-standards:15 | CLAUDE.md:191 · AS/testing:4 · standards-review:438 · crq.md:270 | deslop:119 · sk/it-testing:350 |
| 10 | no restating/decorative comments | java-standards:16 · AS/comments.md | CLAUDE.md:192 · crq.md:297 | deslop |
| 11 | `AruviiException`, never `ResponseEntity.status` | java-standards:18 | CLAUDE.md:193 · AS/error-handling:83 · standards-review:222 · crq.md:342 | — |
| 12 | expected outcome = sealed return type | java-standards:21 | CLAUDE.md:194 · AS/error-handling | standards-review |
| 13 | layers / domain purity | CLAUDE.md:187 | arch-review:145 | CLAUDE.md:168,181 · hook-from-rule:87 |
| 14 | Spring AI stays in worker (`AgentChatPort`) | CLAUDE.md:203 | arch-review:131 · standards-review:109 · sk/it-testing:57 | spec-review:271 |
| 15 | BOM: never override, never import unread | dependencies.md:13 | CLAUDE.md:212 · standards-review:583 | AS/messaging:108 |
| 16 | logging `action=` INFO + WARN/ERROR + duration | observability.md:23 (no literal `action=`) · AS/logging.md:11 | CLAUDE.md:296 · standards-review:336 (O-01) | migrations.md:27 · flyway-migration:71 |
| 17 | no PII above DEBUG | observability.md:32 | CLAUDE.md:297 · AS/logging:129 · AS/tracing:15 · standards-review:371 | arch-review:322 · AS/secure-coding:33 |
| 18 | decrypt only in `ToolHandler.execute()` | CLAUDE.md:273 | dod.md:33 (**wider**) · AS/secure-coding:4 | CLAUDE.md:53 · standards-review:40 · deslop |
| 19 | migration: `V{n}__`, never edit applied, use skill | migrations.md:19 · sk/flyway-migration:32 | CLAUDE.md:286 · AS/migration-review:11 · standards-review:494 | agent-output:95 |
| 20 | `app-icon` / `app-select` only | angular-ui.md:8 | CLAUDE.md:248 · AS/angular-ui:18 · standards-review:544 | deslop:119 |
| 21 | TDD, Red first | CLAUDE.md:85 · sk/tdd:3 | crq.md:256 · personas/developer:38 | — |
| 22 | MR title `type(area): subject (#NNN)` | CLAUDE.md:312 | crq.md:168 · aruvii-git:173 | — |
| 23 | every commit has a body | CLAUDE.md:321 (+ `.husky/commit-msg`) | aruvii-git:219,298 | — |
| 24 | `Closes #NNN` in MR description | CLAUDE.md:373 | aruvii-git (12 hits) · crq.md | code-review |
| 25 | no AI attribution trailer | CLAUDE.md:379 | aruvii-git:439 | — |
| 26 | stage explicit paths, never `git add -A` | CLAUDE.md:306 | aruvii-git:71 · aruvii-git/worktrees:15 | — |
| 27 | never pipe a gate through `tail` | CLAUDE.md:165 | — | standards-review:747 · flyway-migration:21 · CLAUDE.md:51 (hook) |
| 28 | `make smoke FULL=1` before done | CLAUDE.md:239 · smoke.md:14 | CLAUDE.md:95,399 · crq.md:371 | aruvii-git/worktrees:38 |
| 29 | number + 2–6 words context | agent-output:10 · ~CM:47 | CLAUDE.md:58 · ~CM:39 | — |
| 30 | diagram first / show-me | agent-output:31 · ~CM:17,28 · sk/show-me | CLAUDE.md:58 · sk/i-have-adhd | personas ×4 ("skills this role reads") |
| 31 | one thing per reply, recommendation not menu | agent-output:70,74 · ~CM:12,24,32 | CLAUDE.md:59 · sk/i-have-adhd | — |
| 32 | skill-first (merge conflicts etc.) | agent-output:90 | — | sk/README:56 |

Counts of distinct files stating the rule (D+R+P): AssertJ 12 · `final` 8 · no-null 8 · decrypt 9 · Spock 6 · `action=` 6 · PII 8 · BOM 5 · Jackson 4 · Jakarta 2.

## 3. Duplicates and drift

**Fully duplicated (≥3 restatements):** the CLAUDE.md:187–198 Java block repeats java-standards.md:12–28 nearly verbatim; crq.md:342 repeats it a third time; standards-review restates it a fourth while its own `description:` (line 3) says "the rule is never restated here".

**Contradictions / drift — both sides:**

| rule | side A | side B |
|---|---|---|
| comparison format | agent-output.md:51–64 — siblings in an aligned code block, **not** a markdown table | ~CM:30 "Tables for anything compared"; ~CM:39 "lead with a table keyed by those numbers" |
| decrypt scope | CLAUDE.md:273 — only `ToolHandler.execute()` | dod.md:33 — "or `SetupService` (for setup)" |
| decrypt hook | CLAUDE.md:53 · AS/secure-coding.md:4 — hook deleted, nothing warns | `settings.json:83` still registers `warn-decrypt-outside-handler.sh`; file absent from `.claude/hooks/` |
| AssertJ vs Spock | CLAUDE.md:190 "AssertJ only" (unscoped) + CLAUDE.md:4 Spock for every new test | it-testing.md:99–100 — power assertions replace AssertJ in Groovy; AssertJ rule "governs Java" |
| test naming | java-standards:15 / CLAUDE.md:191 `shouldXxx` | it-testing.md:54 — Spock feature names read as sentences |
| IT standard language | it-testing.md:62 — every new test is Spock | `sk/it-testing` description "(*IT.java)"; 0 Spock mentions in that skill |
| Jakarta REF | standards-review:591 (D-02 at :590) REF `dependencies.md` | dependencies.md contains no "Jakarta" (0 hits); only CLAUDE.md:205 defines it |
| which file is examples | java-standards.md:8–10 "rules here win; skill is examples" | CLAUDE.md:197 calls java-standards.md "worked examples" |
| sequence diagrams | agent-output:48 mermaid for sequence/state | repo sk/show-me:99 ASCII inline; ~/.claude/skills/show-me (460 w, differs from repo 647 w) Mermaid |
| list length | sk/i-have-adhd:71 cap lists at 5 | ~CM:10 diagram + ~3 lines; agent-output — no cap |

## 4. Overlapping skills

| purpose | skills | relation |
|---|---|---|
| grilling | `grilling` (136 w) · `grill-me` (20) · `grill-with-docs` (34) | latter two are one-line wrappers: "Run a `/grilling` session" (+ `domain-modeling`); also `mattpocock-skills:grilling` plugin copy |
| reviewing code | `code-review` · `standards-review` · `deslop` · `architecture-review` | code-review spawns agents over standards-review + architecture-review; deslop (stage 6a) re-checks comments/`final`/null/icons from the same rules (deslop:77,117–119) |
| reporting to a human | `agent-output.md` · `i-have-adhd` · `show-me` (repo) · `~/.claude/skills/show-me` · ~CM "How to explain" · `wait-what` · `teach` | 5 texts on reply shape; personas list both `i-have-adhd` + `show-me` |
| design/architecture | `codebase-design` · `improve-codebase-architecture` · `architecture-review` · `domain-modeling` | shared deep-module vocabulary; different triggers |
| planning→tickets | `wayfinder` · `to-tickets` · `to-spec` · `triage` · `/refine` · `/issue` | `/refine` wraps wayfinder |
| Java examples vs rubric | `aruvii-standards` (examples) · `standards-review` (rubric) · rules files | three layers of the same rule set (§3) |
| vendored vs plugin | repo `tdd`, `research`, `grilling`, `code-review`, `diagnosing-bugs`, `prototype`, `domain-modeling`, `codebase-design`, `resolving-merge-conflicts` | same names also in `mattpocock-skills:*` plugin listing (#587 territory) |

## 5. Fixed startup cost

| | laptop (`/crq` session) | fleet agent |
|---|---|---|
| repo `CLAUDE.md` | 31.6 KB | 31.6 KB |
| `agent-output.md` (hook) | 5.7 KB | 5.7 KB |
| `~/.claude/CLAUDE.md` | 4.4 KB (user global) | 13–15 KB (role file, replaces global) |
| skill/agent/command descriptions (repo) | 11.4 KB | 11.4 KB |
| other | plugin skill listing (not measured) | MEMORY 0.1–2 KB · `i-have-adhd` always-on (repo SKILL 4.8 KB) |
| **total** | **≈53 KB ≈ 13k tokens** | **≈62–70 KB ≈ 16–17k tokens** |

Then on first `.java` read +8.9 KB; first build-file read +13.7 KB. A reviewer subagent starts at
repo CLAUDE.md + its agent file + preloaded rubric: code-standards ≈ 83 KB, architecture ≈ 71 KB.

## Observations

- No rule file is unscoped; everything at startup is CLAUDE.md + agent-output + global/role CLAUDE.md.
- CLAUDE.md is ~60% of fixed cost and restates most path-scoped rules, so path-scoping saves little.
- The Java rule set exists in 4–5 copies (CLAUDE.md, java-standards, AS/*, standards-review, crq.md:342).
- Output rules exist in 5 places across two repos and the user's home; the table-vs-aligned-block split is a live contradiction.
- One live config bug: `settings.json:83` points at a deleted hook.
- `standards-review` (46 KB) is the largest single preload, and claims not to restate rules but does.
