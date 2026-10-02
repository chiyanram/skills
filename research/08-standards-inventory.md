# R7 · Standards inventory — every file, who reads it, where it goes

Ticket: `issues/14-research-standards-inventory.md` · read 2026-10-01 at `e0cc30e8` · words = `wc -w`.
Legend: `AS/` = `.claude/skills/aruvii-standards/references/` · **SR** = `standards-review` (86 criteria) ·
**AR** = `architecture-review` (29) · router = `aruvii-standards/SKILL.md` table · dev/qa/analyst =
`docs/agents/personas/*.md` · kind **M** MUST · **G** guidance · **X** examples · **P** procedure · **Rb**
rubric. `obs/` is proposed (§2). Ticket says 24 references; **23 exist**.

## 1. Inventory

### aruvii-standards (SKILL + 23 references, 23.4k words)

| file | w | topics | kind | read by today | overlaps | target |
|---|---|---|---|---|---|---|
| `SKILL.md` | 1146 | test ladder 0–4; concern→ref table | P (index) | crq.md:272 (st 6) · java-standards.md:9 · dev | :12 "CLAUDE.md wins" ↔ java-standards.md:8-10 "rules here win" ↔ SR:22 "reference wins" | split: ladder → `testing/SKILL.md`, table → `code/SKILL.md`; delete |
| `angular-ui` | 422 | app-icon, app-select, colour | X | SR U-01..03 · rules/angular-ui.md:14 · deslop:119 | rules/angular-ui.md:8-11 · CLAUDE.md:248 | `code/references/angular-ui.md` |
| `architecture-diagrams` | 350 | Mermaid in docs | G | router only | always-on/agent-output.md:48 | `planning/references/diagrams.md` |
| `boundaries-correct` | 1086 | CORRECT | G+X | SR Q-10 · AR D-05 · gherkin-to-test · router step 2 | coverage-design | `testing/references/boundaries.md` |
| `comments` | 729 | banners, restating, why | X | SR C-01..04, X-07 · java-standards.md:16 | deslop:52 (cat. 1) · CLAUDE.md:192 | `code/references/comments.md` |
| `concurrency` | 542 | virtual threads, pools, locks | G | router only — **no criterion** | modern-java §2 · functional-java §6 (self-declared :3-5) | `code/references/concurrency.md` |
| `coverage-design` | 503 | RIGHT-BICEP | G | router step 1 — **no criterion** | tdd/SKILL.md:18 seams | `testing/references/coverage-design.md` |
| `error-handling` | 1361 | outcome vs fault, ErrorCode | M+X | SR E-01..05 · AR D-06 · java-standards.md:18-27 | java-standards.md:18-27 · CLAUDE.md:193-194 | `code/references/errors.md` |
| `functional-java` | 1547 | collectors, pattern match, async | G+X | SR J-04..06, X-10 | modern-java §6 | `code/references/java-functional.md` |
| `logging` | 958 | placeholders, exception last, forging | X | SR O-01,03-05 · AR D-08 · observability.md:52 | observability.md:23-36 · CLAUDE.md:296 | `obs/references/logging.md` |
| `messaging` | 1272 | Redis Streams vs Kafka, DLT | G+M | SR R-01..03 · AR D-04, D-06 | adr/0002:17 | `code/references/messaging.md` |
| `metrics` | 1174 | Micrometer, cardinality | G+X | SR O-07,08 | — | `obs/references/metrics.md` |
| `migration-review` | 1945 | expand/contract, narrowing, collisions | G+X | SR M-02..07 · AR C-05 · migrations.md:10 | flyway-migration:46-82 · migrations.md:15-70 | `migrations/references/review.md` |
| `modern-java` | 1510 | Java 25 features | G+X | SR T-05,09, J-01..03,07 · java-standards.md:13 | concurrency | `code/references/java-modern.md` |
| `ood-smells` | 751 | 8 Fowler smells | G | SR X-* · AR B-02, C-06 | SR:606-702 (13 smells) · mattpocock code-review step 3 | `code/references/smells.md` (absorbs SR X) |
| `secure-coding` | 602 | SSRF, decrypt, injection | M+G | router only — **no criterion** | CLAUDE.md:268-282 | `code/references/security.md` |
| `services` | 502 | interface+Default, controllers | X | SR L-04..06 | CLAUDE.md:195 | `code/references/services.md` |
| `test-quality` | 1343 | A-TRIP | G+X | SR Q-11 · java-standards.md:15 | testing §1 | `testing/references/test-quality.md` |
| `test-value-bar` | 1021 | should it exist; retention | G | router step 0 — **no criterion** | tdd/SKILL.md:28-34 | `testing/references/value-bar.md` |
| `testing` | 1263 | shape, AssertJ, invariants, harness | M+X | SR Q-04..08 · CLAUDE.md:191 | java-standards.md:12,15 · rules/it-testing.md:99 · gherkin-to-test:13-22 ↔ §8 | `testing/references/unit-tests.md` |
| `tracing` | 974 | Brave, sampling, async | G | SR O-09,10 | — | `obs/references/tracing.md` |
| `type-design` | 1170 | domain types, BigDecimal | G+X | SR T-06..08, X-07,09 · AR B-02 | ood-smells · java-standards.md:17 | `code/references/types.md` (merge) |
| `types-and-null` | 592 | null, sealed, `final` | M+X | SR T-01..05 · AR A-09, C-02, D-03 | CLAUDE.md:190 · java-standards.md:13-14 | `code/references/types.md` (merge) |
| `verification` | 642 | green that ran nothing | G+X | SR V-01,02 · qa · CLAUDE.md | CLAUDE.md:155-159 | `delivery/references/verification.md` |

### Other skills

| file | w | topics | kind | read by today | overlaps | target |
|---|---|---|---|---|---|---|
| `it-testing/SKILL.md` | 2883 | @EnableAruviiIT, archetypes, fakes, Redis, @Scheduled | P+X | crq.md:273 · SR Q-09 · rules/it-testing.md:105 · dev, qa | rules/it-testing.md:10-13,103 · ADR-0009 · CLAUDE.md:223-233 · **0 Spock mentions** ↔ rules/it-testing.md:62 | `testing/references/integration-tests.md` (checklist :341 = its review checks) |
| `smoke-spec/SKILL.md` | 3546 | authoring + K-00..K-16 | M+P+Rb | smoke-spec-reviewer (preload) · crq.md:274,357 · rules/smoke.md:8 | playwright-rubric A–H · rules/smoke.md:20-28 | `testing/references/smoke-specs.md` — **already author + reviewer in one file** |
| `tdd/` (SKILL, mocking, tests) | 1311 | loop, seams, anti-patterns | G+P | crq.md:260 · dev | upstream `mattpocock-skills/skills/engineering/tdd`: mocking/tests identical; SKILL adds PIT para :36-40 | delete → mattpocock plugin; PIT para → `testing/SKILL.md` |
| `gherkin-to-test` | 897 | tier choice, property, PIT | P | to-spec:49,75 · dev | testing §8 · tdd:38 | `testing/workflows/scenario-to-tests.md` |
| `acceptance-criteria-writing` | 674 | AC concision, parameterize | G | to-spec:44 · analyst | — | `planning/references/acceptance-criteria.md` |
| `flyway-migration` | 710 | version, file, DDL safety | P+M | crq.md:275 · migrations.md:10 · SR M-01 · CLAUDE.md:287 · dev | migrations.md:15-70 · migration-review | `migrations/workflows/new-migration.md` |
| `deslop` | 1257 | 6 slop categories | P | crq.md:296 (st 6a) | comments · types-and-null · ood-smells §8 · :117-119 restates Java MUSTs | `code/workflows/deslop.md`, categories point at `code/references/` |

### Rules (`.claude/rules/`)

| file | w | topics | kind | read by today | overlaps | target |
|---|---|---|---|---|---|---|
| `java-standards` | 741 | 9 MUSTs + JPA (:30-67) | M | `**/*.java` | CLAUDE.md:185-198 near-verbatim · crq.md:342; pointers drift: :13 `final`→modern-java (SR T-04→types-and-null §6), :15 GWT→test-quality (SR Q-05→testing §1) | `rules/java.md` MUSTs; JPA body → `code/references/persistence.md` |
| `observability` | 563 | level table, 7 rules | M | `**/*.java` · SR O-01,02,06 · AR D-02, D-08 | CLAUDE.md:293-300 · logging | `rules/observability.md` MUSTs; table → `obs/references/levels.md` |
| `it-testing` | 856 | placement, 5 Spock rules, language | M+X | IT/Spec globs · SR Q-02,03,09 | ADR-0009 · it-testing skill · CLAUDE.md:190 (AssertJ unscoped); **:62 governs every test, loads only on IT paths** | `rules/testing.md` (test-path globs); Spock rules → `testing/references/spock.md` |
| `migrations` | 1233 | authoring, who migrates, PG design, drift gate | M+G | `db/migration/**` · SR M-01,02 | flyway-migration §4 · migration-review §6 | `rules/migrations.md` MUSTs only; rest → `migrations/references/` |
| `dependencies` | 2071 | BOM, non-rules, CVE | M+G | build-file globs · SR D-01..03, L-02 · AR A-02 | CLAUDE.md:200-216 · SR D-02 Jakarta REFs here, **0 hits** | `rules/dependencies.md` MUSTs; non-rules → `delivery/references/dependencies.md` |
| `smoke` | 231 | tiers, DoD gates | M | smoke glob | smoke-spec · CLAUDE.md:237-243 | `rules/smoke.md` (keep) |
| `angular-ui` | 82 | 3 MUSTs | M | `aruvii-ui/**` · SR U-01 | AS/angular-ui · CLAUDE.md:245-254 | `rules/angular-ui.md` (keep) |

### Rubrics, CLAUDE.md, docs

| file | w | topics | kind | read by today | overlaps | target |
|---|---|---|---|---|---|---|
| `standards-review` | 7511 | L T E C J O Q M U D X R V | Rb | code-standards-reviewer (preload) · code-review:51 · crq.md:341 (st 7) | claims no restating (:22), restates (R1 §3); X ↔ ood-smells | dissolve: each criterion → "Review checks" in its reference (OQ1) |
| `architecture-review` | 5243 | A fit · B precedent · C extension · D behaviour · E record · F realised | Rb | architecture-reviewer · crq.md:214 (st 5), :344 (st 7) | A-02/03 = SR L-02/03 · B-02 → ood-smells | A–E → `planning/references/design-review.md`; F-01 → Spec axis (G3) |
| CLAUDE.md blocks | — | java :185-198 · deps :200-216 · tests :218-235 · smoke :237-243 · ui :245-254 · migrations :284-291 · obs :293-300 · gates :142-183 | M | every session | each restates a rule file | one-line pointers in `AGENTS.md` (G1 L1) |
| `docs/guides/playwright-rubric.md` | 2132 | scored Playwright audit A–H | Rb | **nothing in `.claude/`**; only `docs/research/audit-25-routes-selectors.md` | smoke-spec:83 B1 = rubric:59 D1 | delete, merged into `smoke-specs.md` (keep doc URLs) |
| `docs/adr/0009-*` | 2937 | `src/integrationTest`, serial ITs | decision | SR Q-03 · rules/it-testing.md:13 · hook `warn-it-in-src-test.sh` · spec-reviewer | it-testing skill:21-32 | keep as ADR; rules cite it |

## 2. Proposed tree

```
testing/     SKILL.md (ladder 0-4 + tier choice + PIT)
             references/ value-bar coverage-design boundaries unit-tests test-quality
                         spock integration-tests smoke-specs
             workflows/  scenario-to-tests            (tdd = mattpocock plugin)
code/        SKILL.md (concern table)
             references/ comments types errors services java-modern java-functional
                         concurrency smells security messaging persistence angular-ui
             workflows/  deslop
obs/  (new)  references/ levels logging metrics tracing
migrations/  references/ review postgres-design who-migrates · workflows/ new-migration
delivery/    references/ verification dependencies (+ git, out of scope here)
planning/    references/ acceptance-criteria design-review diagrams
rules/       java · observability · testing · migrations · dependencies · smoke · angular-ui  (MUSTs only)
```

| candidate domain | for | against |
|---|---|---|
| **obs/** (observability) | 4 files ~3.7k w · own SR group O (10) · AR D-02/D-08 · its reader is the on-call operator, not the Java author | all four sit under `**/*.java`; could be `code/` |
| messaging · ui · security | own SR group / rule each | one file each → `code/` |
| build | verification + dependencies, 2.7k w | fits `delivery/` |

## 3. "Both ways" — how the references share one text

| ref | shared text lives | author reaches it | reviewer reaches it |
|---|---|---|---|
| **addy** | repo-root `references/*-checklist.md`; skill-private `skills/<n>/references/` for detail (CLAUDE.md:34) | `security-and-hardening/SKILL.md:166` "Before sign-off, walk `../../references/security-checklist.md`" · `performance-optimization/SKILL.md:443` | `code-review-and-quality/SKILL.md:351-352` "See Also" · `web-performance-auditor.md:175` "Use `references/performance-checklist.md` as the minimum baseline". `code-reviewer`/`security-auditor` name no checklist |
| **pstack** | one leaf skill per principle, `disable-model-invocation: true` (`principle-prove-it-works/SKILL.md:4`) | `poteto-mode/SKILL.md:38` "Read the leaf skill in full for any principle you apply." · `agents/poteto-agent.md:9` "Navigate to a leaf `principle-*` skill" | **`interrogate` does not name any principle.** Reviewers are `generalPurpose`, fed `references/rubric.md` + `code-quality-review.md` (`interrogate/SKILL.md:51-55`); `rubric.md:49` paraphrases one: "Do they test behavior or implementation details?" Sharing happens only through the poteto-mode lead, which routes to interrogate (`poteto-mode/SKILL.md:24`) |
| **mattpocock** | the repo's own docs | normal reading of repo docs | `code-review/SKILL.md:36` "Anything in the repo that documents how code should be written"; step 4 pastes them plus the smell baseline "in full (the sub-agent has no other access to it)" |
| mattpocock ladder | `writing-for-agents/SKILL.md:33-35`: in-file step → in-file reference → disclosed reference behind a pointer | :78 "single source of truth: one authoritative place" | `SKILL-MECHANICS.md:14`: reference shared by two skills → "Push it to a plain file outside the skill system" |

Common shape: one rules file, a pointer from author and from reviewer. In-repo precedent:
`smoke-spec/SKILL.md` — authoring :6-155, rubric K-* :156-301.

## 4. Open questions for the operator

| # | decide | facts |
|---|---|---|
| OQ1 | where review checks live: section at the end of each reference (smoke-spec shape) · separate `*-checklist.md` per domain (addy) · one pointer rubric (SR today) | SR is 7.5k w, preloaded every stage-7 run (R4) |
| OQ2 | precedence when rule and reference disagree | three files claim three different winners (§1 row 1) |
| OQ3 | add `obs/`? | §2 table |
| OQ4 | Standards reviewer source: mattpocock `code-review` plugin step 3 vs repo workflow picking references by changed path | G3 Q2, paused on this |
| OQ5 | unreviewed references: add checks or leave author-only | secure-coding, concurrency, coverage-design, test-value-bar, architecture-diagrams |
| OQ6 | merge `types-and-null`+`type-design`; `modern-java`+`functional-java`+`concurrency`; `ood-smells`+SR X? | 1.8k / 3.6k / 0.8k+13 criteria |
| OQ7 | re-scope test MUSTs to test-path globs | rules/it-testing.md:62 + AssertJ rule load on wrong paths |
| OQ8 | `architecture-review` A–E: `planning/` or a review home | stage 5 only after G3 |
| OQ9 | drop repo `tdd` for the plugin; where the PIT paragraph goes | only delta vs upstream |
| OQ10 | `playwright-rubric`: delete or merge | read by nothing in `.claude/` |

Drift seen: java-standards.md:13,:15 vs SR T-04/Q-05 · SR D-02 → no Jakarta rule · it-testing skill
Java-only vs rules/it-testing.md:62 Spock.
