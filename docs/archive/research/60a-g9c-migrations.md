# 60a · G9c candidates — MIGRATIONS (#34), 2026-10-04

For **#34** (G9c: approve migrations + delivery + review packet rules) under map **#9** (One rulebook). Brief: `60-g9c-BRIEF.md`.
Nothing here is approved. Prefix **MG**. Our text = skeleton `chore/643-one-rulebook-skeleton` @`71b5deb4` (`skel:`); code evidence = agent-platform `origin/master` @`772736bf` (`m:`).

**Legend.** `RF` = `/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/`.
`pl-ap` = `RF/jabrena-plinth/skills/313-frameworks-spring-db-migrations-flyway/references/313-…-antipatterns.md` ·
`pl-pc` = `…/313-…-parallel-change.md` · `pl-fw` = `…/313-frameworks-spring-db-migrations-flyway.md` · `pl-sk` = `…/313-…/SKILL.md` ·
`addy` = `RF/addyosmani-agent-skills/skills/deprecation-and-migration/SKILL.md` · `bugbot` = `RF/cursor-plugins/pstack/skills/poteto-mode/references/bugbot-triage.md` ·
`matt-retro` = `RF/mattpocock-skills/skills/engineering/retro/SKILL.md`.
Primary docs (read 2026-10-04): `PG-ALT` postgresql.org/docs/current/sql-altertable.html · `PG-IDX` …/sql-createindex.html · `PG-CON` …/ddl-constraints.html ·
`PG-CHR` …/datatype-character.html · `PG-JSON` …/datatype-json.html · `PG-LT` …/runtime-config-client.html (lock_timeout) · `PG-WIKI` wiki.postgresql.org/wiki/Don't_Do_This ·
`FW-VER` documentation.red-gate.com/fd/versioned-migrations-273973333.html · `FW-REP` …/fd/repeatable-migrations-273973335.html ·
`FW-<setting>` documentation.red-gate.com/fd/reference/configuration/flyway-namespace/flyway-<setting>-setting · `FW-TL` …/fd/postgresql-transactional-lock-setting-277579114.html ·
`CC-MEM` code.claude.com/docs/en/memory. `P1` = `p1/lead-judgment.md`.

## 1 · R12 rows (G1b-corrected)

| current file | target (G1b) | action | deletions | agree/change + why |
|---|---|---|---|---|
| `skel:.agents/skills/migrations/references/review.md` (275 lines) | `.agents/skills/migrations/references/review.md` | MOVE + reshape to 5 sections | "How Flyway is wired" :22-62 → `who-migrates.md`; Boot 4 artifact :49-57 → `delivery/references/dependencies.md`; :260-261 "none on master today… consolidate branch" (count/narration, checklist 13); CLAUDE.md pointers :4,:87,:162,:217,:267 (CLAUDE.md block deleted) | **agree.** Content is an adaptation of `pl-ap:40-176` (same examples) — cite plinth as source; P1 F3/N2/F2 become its Bads |
| `skel:.claude/rules/migrations.md` (123 lines) | dir MUSTs → **`aruvii-infra/AGENTS.md`** (OQ-MG1); design → `migrations/references/postgres-design.md`; who-migrates → `…/who-migrates.md`; authoring → `flyway-migration` | SPLIT, then DELETE (`.claude/rules/` deleted, G1b #72) | :8-13 pointer + "most rules have no gate" (narration); :69-70 IT-speed measurement (no-op, MG56); :121-123 golden-file IT claim — **false at m:** (no golden/schema-dump IT exists; OQ-MG4) | **change.** R12 said "L2 `rules/migrations.md`"; G1b moves directory MUSTs into a nested AGENTS.md. Both load only on **Read** (`CC-MEM` "when Claude opens a file there with the Read tool"), so #500's create-time gap remains — hooks stay the enforcer |
| `skel:.agents/skills/flyway-migration/SKILL.md` (86 lines) | keep **flat** `.agents/skills/flyway-migration/SKILL.md` (OQ-MG2), not `migrations/workflows/new-migration.md` | MOVE content, fix contradictions | :10 `/dod` (deleted, ND-5); :18-22 version loop (hook does it, MG2); :44 "no DROP TABLE" and :52 "DROP TABLE forbidden" (contradicts expand/contract, X-MG2); :53 "every index CONCURRENTLY" (X-MG1); :68-75 #109/#154 history (→ one line + MG42) | **change target.** Decision register "workflows stay flat skills" (#643 hybrid); `skel` already has it flat. Keep "Use whenever a change needs a schema migration" trigger (R2:43,87-89; G10 #37 Q3) |
| `skel:AGENTS.md:285-292` «schema change» block | root AGENTS.md: **one pointer line** ("before creating `V*.sql`, read `aruvii-infra/AGENTS.md`"); flags list → `docs/CONTEXT.md` | DELETE body (restates) | :287-288 rule restated in 5 files (R1:57) | **agree**, but keep a pointer: nested AGENTS.md is read-triggered and a new migration is a create (`skel:AGENTS.md:30-33`, #500) |
| hooks `block-migration-edit.sh` · `check-migration-version.sh` | `.claude/hooks/` (L4) | KEEP | `block-migration-edit.sh:3,10` cite "CLAUDE.md" + "/migration skill" (stale name); `check-migration-version.sh:4` cites `rules/migrations.md:42` (file deleted) → repoint to `aruvii-infra/AGENTS.md` | **agree.** Plus MG72: hook reads `git branch -r` only (`check-migration-version.sh:23`) — an unpushed sibling-worktree branch is invisible, so `skel:rules/migrations.md:44-46` overclaims |

## 2 · Candidates

Format: `ID — rule — source — evidence — verdict`.

### 2a · `aruvii-infra/AGENTS.md` (directory MUSTs, G1b; ≤5)

- **MG1** — Never edit an applied `V*.sql`; fix it with a new forward version. — `pl-fw:225` "Do not edit migrations that already ran in shared environments"; `FW-VER` "best practice not to make changes to existing versioned migrations" — gate `block-migration-edit.sh:8-11` (checklist 4: cite the gate) — **ADOPT**
- **MG2** — A new version is unused on every branch; take max-across-branches + 1, never `ls` of your tree. — `FW-VER` "Each versioned migration must be assigned a unique version"; `pl-ap:24` "Detect duplicate version numbers" — #500 took V99 (commit `fa20fcb0`); #502/#496 both took V104; #161 six collisions; gate `check-migration-version.sh` — **ADOPT**
- **MG4** — Start every migration with a header that names each data change and lock it takes, and why; the header matches the statements. — `pl-sk:33` "assess whether it can break deployed application versions… production data interpretation"; `pl-ap:40` — P1 F3: V106 @`70b84c0b`:1 says "Expand-only" yet :15-16 rewrites every `agents` row; :2-3 says CHECK "in the same statement", it is a separate ALTER (P1:3) — **ADAPT**
- **MG5** — `SET lock_timeout` before any `ALTER TABLE` on an existing table. — `PG-LT` "Abort any statement that waits longer than the specified amount of time"; `PG-ALT` Description "An ACCESS EXCLUSIVE lock is acquired unless explicitly noted" — m: `V101:21`, `V104:8`, `V106:5` (Good) — **ADOPT**
- **MG3** — DDL lives only in `aruvii-infra/src/main/resources/db/migration/`, as SQL; no Java migrations. — **project decision?** `pl-fw:127` ✗ allows `BaseJavaMigration` for backfills — REQ-024 discarded one (TypeName vs Checkstyle, `skel:review.md:59-62`); REQ-064 — **project decision?** (OQ-MG6)

### 2b · `migrations/references/review.md`

- **MG10** — Change a column by expand → migrate → contract; contract ships in a later release; never DROP+ADD or RENAME in place. — `addy:166` "never change a column in place"; `pl-pc:28` — `skel:review.md:79-106`; api and worker deploy separately (`skel:review.md:124-127`) — **ADOPT**
- **MG11** — Between expand and contract the code writes both shapes and reads the new one with a fallback. — `addy:178` "App writes both `name` and `full_name`"; `pl-pc:41` — `ChatRequestEnvelope` persisted in Redis, read by the other process (`skel:review.md:126-127`) — **ADOPT**
- **MG24** — A destructive step (DROP, RENAME, SET NOT NULL on the old shape) is alone in its own migration and release. — `addy:186` "Additive first, destructive last and alone." — `skel:flyway-migration:51-52` — **ADOPT**
- **MG12** — Before narrowing a type or length, put the count query in the MR; otherwise widen or add a column. — `pl-ap:23` "Check existing production-like data before narrowing types, reducing lengths" — `skel:review.md:143-159` — **ADOPT**
- **MG13** — A `NOT NULL DEFAULT` on an existing table states what the default means for old rows; unknown → nullable, with the reason. — `pl-ap:81` "confirm the default is correct for historical rows" — m: `V90` nullable hash (Good); `V106:15-17` default 0 with R5 reason (Good, rewritten) — **ADOPT**
- **MG14** — Every `UPDATE`/`DELETE` has a `WHERE` naming its target, or a comment saying why every row is right. — `pl-ap:85` "require precise WHERE clauses, row-count expectations" — **P1 F3 Bad** V106 @`70b84c0b`:15-16 (no predicate, no reason); **Good** m:`V106:15-18` (R5 comment) — **ADOPT** (Good/Bad pair, real)
- **MG15** — A new UNIQUE index or constraint on existing data ships the duplicate query in the MR, or a cleanup migration first. — `pl-ap:52-55` — `skel:review.md:204-219` — **ADOPT**
- **MG16** — A changed column default or enum/status meaning names its effect on future inserts and on existing rows. — `pl-ap:102-110` "Bad future default: changes new-row behavior silently" — `skel:review.md:183-184` — **ADOPT**
- **MG17** — `R__` migrations are idempotent and additive; never `DELETE`/`TRUNCATE` at the top. — `FW-REP` "your responsibility to ensure the same repeatable migration can be applied multiple times" — no `R__` on m: (fires only when one appears) — **ADOPT** as a review check only
- **MG18** — Never set `out-of-order=true` to clear a branch collision; renumber the unmerged migration. — `FW-outOfOrder` default `false`; `pl-ap:25` "Treat `outOfOrder=true` as an exceptional operational decision" — `skel:review.md:238-241` — **ADOPT**
- **MG19** — A migration that touches existing rows has an IT that migrates to V(n-1) (Flyway `target`), seeds rows, migrates, asserts them. — `pl-ap:169` "Load a previous-release fixture, migrate, then assert preserved business data"; `FW-target` "target version up to which Flyway should consider migrations" — P1 F2: AC-6 proved only on rows inserted after V106; no IT on m: uses `target` (grep) — **ADAPT**
- **MG21** — A green context-load test is not migration verification. — `pl-ap:160` "A passing Spring context test is not enough." — `skel:review.md:263-275` — **ADOPT** (review check)
- **MG22** — Backfill a table whose size grows with customer use in batches; one statement only for a table the header names as small. — `addy:188` "A single `UPDATE` over millions of rows locks the table" — V106 `agents` (per-agent scale) — **ADAPT**
- **MG23** — Migrations are forward-only; no down script. Rollback = the previous image boots on the expanded schema. — `pl-fw:227` "Flyway does not auto-rollback; plan forward migrations"; ✗ `addy:187` "Every migration has a tested down path" — `skel:review.md:129-131` — **ADAPT** (reject addy; OQ-MG3)
- **MG20** — The lead never auto-dismisses a migration finding: it is fix or ask. — `bugbot:81` "Migration, schema, idempotency, concurrency… findings" (do not auto-skip) — P1:22 dismissal was right only because the header gave the reason — **ADOPT** → also `review/references/lead-judgment.md`

### 2c · `migrations/references/postgres-design.md`

- **MG30** — Timestamps are `timestamptz`, with no precision spec. — `PG-WIKI` "Don't use the timestamp type to store timestamps, use timestamptz" + "Don't use a precision specification" — V25 exists because mixing dropped `BETWEEN` rows (`skel:review.md:161-163`) — **ADOPT**
- **MG31** — New string columns are `TEXT`; a business length is `CHECK (length(col) <= n)`; existing `VARCHAR` stays. — `PG-CHR` 8.3 "no performance difference among these three types"; `PG-WIKI` "Don't use the type varchar(n) by default" — **P1 N2 Bad** V106 @`70b84c0b`:8,20 `VARCHAR(20)/(40)`; **Good** m:`V106:8,22-26` TEXT + CHECK — **ADOPT** (Good/Bad pair, real)
- **MG32** — Every `REFERENCES` states `ON DELETE` (`CASCADE`, `SET NULL` or `RESTRICT`). — `PG-CON` 5.5.5 "The default `ON DELETE` action is `ON DELETE NO ACTION`" (the default is silent) — m:`V101:29` (Good) — **ADAPT** (making it explicit is ours)
- **MG33** — Index every foreign-key column. — `PG-CON` 5.5.5 "does not automatically create an index on the referencing columns" — m:`V103` indexes V101's FK — **ADOPT**
- **MG34** — A `CHECK` on a nullable column either pairs with `NOT NULL` or says null is allowed. — `PG-CON` 5.5.1 "satisfied if the check expression evaluates to true or the null value" — m:`V106:24-26` CHECK on nullable `verdict_reason` (null intended, unstated) — **ADOPT**
- **MG35** — `UNIQUE` on a nullable column is not uniqueness; make it `NOT NULL`. — `PG-CON` 5.5.3 "possible to store duplicate rows that contain a null value" — `skel:rules:107` — **ADOPT**
- **MG36** — Never `timetz`, `money`, `serial`, `char(n)`; ids are `uuid DEFAULT gen_random_uuid()`, money `NUMERIC(p,s)`. — `PG-WIKI` "Don't use the timetz type", "Don't use the type char(n)", "identity columns should be used instead" — `skel:rules:108-111` — **ADOPT**
- **MG37** — `JSONB`, never `JSON`; a filtered JSONB path gets a GIN (`jsonb_path_ops` for containment) index. — `PG-JSON` 8.14 "most applications should prefer to store JSON data as `jsonb`"; 8.14.4 GIN — `skel:rules:102-105` — **ADOPT**
- **MG38** — Name every constraint and index (`pk_`/`uq_`/`ck_`/`fk_`/`idx_`). — **project decision?** no reference read — generated names unassertable (`skel:rules:33-34`) — **project decision?**
- **MG41** — `CREATE INDEX` on an existing table is `CONCURRENTLY`, alone in its migration; inside `CREATE TABLE` it is plain. — `PG-IDX` "a standard index build locks out writes"; "`CREATE INDEX CONCURRENTLY` cannot [run in a transaction block]" — X-MG1: `skel:flyway-migration:53` says every index CONCURRENTLY — **ADOPT**
- **MG42** — No `-- flyway:nonTransactional` marker, no `.conf` sidecar; the migrator's `postgresql.transactional-lock: false` is the mechanism. — `FW-TL` "should be set to `false` for statements such as `CREATE INDEX CONCURRENTLY`" — #109 (invented marker), #154 (measured); m: still carries `V92__…sql.conf` — **ADOPT**
- **MG43** — After a failed `CONCURRENTLY`, drop the invalid index before retrying; `IF NOT EXISTS` will skip it. — `PG-IDX` "recommended recovery method… is to drop the index and try again"; IF NOT EXISTS "no guarantee that the existing index is anything like" — `skel:flyway-migration:65` uses `IF NOT EXISTS` (reasoned, not measured) — **ADOPT**
- **MG44** — `ADD COLUMN … NOT NULL` carries a non-volatile `DEFAULT`. — `PG-ALT` Notes: a volatile `DEFAULT` "will cause the entire table and its indexes to be rewritten" — `skel:rules:30` — **ADOPT**
- **MG45** — `ADD CONSTRAINT` (CHECK, FK) on an existing table is `NOT VALID`; `VALIDATE CONSTRAINT` in a later migration. — `PG-ALT` Notes "With `NOT VALID`… does not scan the table"; validation takes "only a `SHARE UPDATE EXCLUSIVE` lock" — **Good** m:`V101:27-30` + `V104:10` (real) — **ADOPT**
- **MG46** — `ALTER COLUMN … TYPE` rewrites the table; use a new column (MG10) instead. — `PG-ALT` Notes "will normally cause the entire table and its indexes to be rewritten" — `skel:review.md:146-147` — **ADOPT**
- **MG47** — `SET NOT NULL` on an existing column: add `CHECK (col IS NOT NULL) NOT VALID`, validate, then `SET NOT NULL`. — `PG-ALT` Description "if a valid `CHECK` constraint exists… then the table scan is skipped" — new; our rules are silent — **ADOPT**

### 2d · `migrations/references/who-migrates.md`

- **MG50** — `aruvii-api` is the sole migrator; every other process sets `flyway.enabled: false` and relies on `ddl-auto: validate`. — **project decision?** (REQ-064) — #154, #222 hang; m:`aruvii-worker/…/application.yml:43` — **project decision?**
- **MG51** — The migrator keeps `baseline-on-migrate: false` and `validate-on-migrate: true`. — `FW-baselineOnMigrate` "removes the safety net that ensures Flyway does not migrate the wrong database"; `FW-validateOnMigrate` default `true`; `pl-fw:104` "Keep `validate-on-migrate` enabled"; ✗ `pl-fw:112` sets baseline true (brownfield only) — `skel:review.md:39-47` — **ADAPT**
- **MG52** — After a schema change, deploy `api` before `worker`. — **project decision?** — worker restart-loops on validate (`skel:rules:84-86`) — **project decision?**
- **MG53** — When a higher version already sits in the shared dev volume, reset the volume; never renumber. — `FW-outOfOrder` default `false` (explains the failure) — #502 + #496 (`skel:rules:47-63`) — **project decision?**
- **MG54** — `ddl-auto: validate` is not a drift gate: it misses nullability, length, indexes, FKs, checks, defaults. — **project decision?** (Hibernate docs not read) — `skel:rules:115-119`; golden-file IT claimed at :121 does not exist (OQ-MG4) — **project decision?**
- **MG55** — A migration that adds a seeded or reference table adds a `PRESERVE` decision in `AruviiTestReset`. — **project decision?** — m:`aruvii-test-support/…/AruviiTestReset.java:45` — **project decision?**
- **MG56** — Delete "never justify a schema change on IT speed" (`skel:rules:69-70`). — `00-reference-format.md` checklist 13/15 (measurements that rot; no-op) — **DROP**

### 2e · `flyway-migration` workflow (flat skill)

- **MG60** — Step 1 names the hook and MG53, and drops the hand loop. — `matt-retro:19` "a mechanical one… gets a deterministic check, full stop" — `skel:flyway-migration:18-22` duplicates `check-migration-version.sh` — **ADAPT**
- **MG61** — The skill's steps are: version (hook) → file → header (MG4) → SQL (MG41–47) → IT (MG19) → `make verify-module`. — `pl-sk:46-62` (read → scope → apply → verify) — `skel:flyway-migration:10` names deleted `/dod` — **ADAPT**
- **MG62** — `CREATE TABLE IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS` stay; `IF NOT EXISTS` on an index never replaces MG43. — `pl-fw:74` "Prefer idempotent-friendly DDL… (e.g. `IF NOT EXISTS`)" — `skel:flyway-migration:37` — **ADOPT**

### 2f · Gates (L4 / runner)

- **MG70** — `scripts/check-migrations.sh` (in `make lint` and the runner) fails on: `timestamp` without tz, `varchar(` in a new file, `flyway:nonTransactional`, a `.conf` sidecar, `CONCURRENTLY` with another statement, `UPDATE`/`DELETE` without `WHERE` or comment. — `matt-retro:19`; `pl-ap:135` "Prefer CI checks that scan `V*__*.sql`"; approved OQ3 (mechanical → gate) — semgrep deleted, "migration DDL safety" ungated (`skel:AGENTS.md:168,181`) — **ADAPT** (OQ-MG5)
- **MG71** — A runner job fails when two `V` files share a version in the merged set, and runs the full chain from empty. — `pl-ap:135` "fail when two files share the same V* prefix… run the full migration chain from an empty database" (`:141-143`) — #500, #161 merged cleanly — **ADOPT**
- **MG72** — `check-migration-version.sh` also reads local branches, so an unpushed sibling worktree counts. — **project decision?** — `check-migration-version.sh:23` `git branch -r` only; #502/#496 collided after a correct check — **project decision?**

## 3 · When X, use Y

| reference | situation (observable) | use | why |
|---|---|---|---|
| postgres-design | index on a table created in an earlier version | `CREATE INDEX CONCURRENTLY`, alone in the file | MG41, PG-IDX |
| postgres-design | index inside the `CREATE TABLE` migration | plain `CREATE INDEX` | empty table, no lock to avoid |
| postgres-design | CHECK or FK on an existing table | `NOT VALID` now, `VALIDATE` in the next version | MG45 |
| postgres-design | new NOT NULL on an existing column | CHECK NOT VALID → VALIDATE → `SET NOT NULL` | MG47 |
| postgres-design | new string column | `TEXT` + `CHECK (length…)` | MG31 |
| review | column rename or type change | new column + backfill + later contract | MG10, MG46 |
| review | `UPDATE` with no `WHERE` | a comment stating why every row | MG14 |
| review | migration changes existing rows | V(n-1) seed IT | MG19 |
| who-migrates | `Detected resolved migration not applied` on dev | `docker compose down -v` | MG53 |
| who-migrates | version collision at merge | renumber the unmerged file | MG18 |

## 4 · Decided edges

- **MG45 Skip when** the header names the tables as per-agent scale and gives that as the reason (V106, P1:22). **Do not skip when** the table grows with customer traffic (`interactions`, `chat_messages`, logs) or the header is silent. Confidence: candidate. Note: `skel:rules:37` states no exception — write it here, never in the Rule.
- **MG22 Skip when** the header names the table as small. **Do not skip when** it is message, log, interaction or run data. Confidence: candidate.
- **MG31 Skip when** the column already exists as `VARCHAR`. **Do not skip when** a spec prescribes `VARCHAR` for a new column: that is standard-vs-spec, settled at spec review, not in code-review round 3 (P1 N2). Confidence: recurring.
- **MG1 Skip when** never; the hook also blocks your own unmerged file, which may already have run on a dev DB (`skel:review.md:11-13`). Confidence: strong.
- **MG10 Skip when** a decision records that no shipped install holds the data (REQ-024 R4, `skel:review.md:133-141`). **Do not skip when** nobody asked the question. Confidence: candidate.
- **MG23** addy's down path is rejected for Flyway Community; **do not skip** expand/contract because "we can roll back". Confidence: strong.
- **MG20 / bugbot** a migration finding is never in the lead's auto-dismiss list. Confidence: strong.

## 5 · Review checks

`review.md` (every changed `V*.sql` and `R__*.sql` walked, each statement read):
- [ ] MG4 header lists every UPDATE/DELETE/constraint/lock in the file; compare line by line.
- [ ] MG10/MG24 no `DROP COLUMN`, `RENAME`, or DROP+ADD pair in the same release as the code change.
- [ ] MG11 both shapes written in the expand-release code (open the entity/mapper diff).
- [ ] MG12 any narrowing type/length has the count query quoted in the MR.
- [ ] MG13/MG16 every `NOT NULL DEFAULT` on an old table and every changed default states its meaning for old rows.
- [ ] MG14 every `UPDATE`/`DELETE` has a `WHERE` or a reason comment (`scripts/check-migrations.sh`).
- [ ] MG15 a new UNIQUE has the duplicate query or a cleanup migration.
- [ ] MG17 any `R__` file is idempotent (no top-level DELETE/TRUNCATE).
- [ ] MG18 no `out-of-order` in any `application*.yml` diff.
- [ ] MG19 a change to existing rows has an IT that seeds at V(n-1) — name the IT file.
- [ ] MG21 the verification cited is not a context-load test.

`postgres-design.md` (every new column, constraint, index):
- [ ] MG30/MG31/MG36/MG37 types per column (`scripts/check-migrations.sh` for `timestamp`, `varchar(`).
- [ ] MG32/MG33 each `REFERENCES` has `ON DELETE` and an index on the FK column (same or next version).
- [ ] MG34/MG35 each CHECK/UNIQUE on a nullable column has `NOT NULL` or a comment.
- [ ] MG41/MG42 `CONCURRENTLY` alone in its file; no marker, no `.conf`.
- [ ] MG44–MG47 lock shape per statement; MG5 `lock_timeout` present before the first `ALTER TABLE`.

`who-migrates.md` (any `application*.yml` or Flyway config diff):
- [ ] MG50/MG51 only `aruvii-api` has `flyway.enabled: true`; baseline false, validate true, transactional-lock false.
- [ ] MG55 a new seeded table is in `AruviiTestReset.PRESERVE` or marked not preserved.

## 6 · Already decided (do not re-propose)

| item | ticket |
|---|---|
| migration work takes the full lane (G8 floor) | G8 #30 · #35 Q24 |
| one fresh reviewer loads references by changed path; lead buckets Act/Consider/Noted/Dismissed | G3 #16 |
| `/dod` deleted; stage 8 = runner + AC citing | ND-5 |
| hooks stay as L4; `.claude/rules/` deleted; dir MUSTs → nested AGENTS.md | G1 res. 1 · G1b #72 |
| workflows stay flat skills; knowledge in domain skills | #643 hybrid |
| descriptions = "Use when <observable trigger>" | G10 #37 Q3 |
| mechanical rules live in a gate, not review checks | ledger OQ3 |
| a review counts only if it covered the head commit | #64 idea 1 |
| self-hosted runner job = the Verifier | #35 Q26 |
| write the unflattering operational fact ("only the api runs migrations") | ledger WD4 |
| a story with a migration escalates to a full REQ at spec review | ledger SR6 |
| build order is end-to-end slices, never migration → service → API → UI | ledger PD4 |
| tests guarding a migration contract are kept | ledger V5 |

## 7 · Open questions

1. **OQ-MG1 — where the directory MUSTs live.** Facts: G1b says `<dir>/AGENTS.md`. `db/migration/AGENTS.md` sits in `src/main/resources` and would ship in the jar. Any nested AGENTS.md loads on Read only (`CC-MEM`), the #500 gap. **Rec:** `aruvii-infra/AGENTS.md` (MG1, MG2, MG3, MG4, MG5) + one root pointer line + both hooks.
2. **OQ-MG2 — workflow placement.** Facts: R12 says `migrations/workflows/new-migration.md`; the register says workflows stay flat; skel keeps `flyway-migration/` flat, and it is one of two skills that fire unprompted (R2:43). **Rec:** keep it flat; `migrations/SKILL.md` routes to it.
3. **OQ-MG3 — down migrations.** Facts: `addy:187` wants a tested down path. `pl-fw:227` and our forward-only practice say no. Flyway Community has no undo. **Rec:** reject addy (MG23); rollback = expand/contract keeps the old image bootable.
4. **OQ-MG4 — the drift-gate claim.** Facts: `skel:rules:121-123` says one IT asserts `information_schema` against a golden file. No such IT exists at m:@`772736bf`. **Rec:** delete the claim, keep MG54 as a fact, open a ticket for the golden-file IT.
5. **OQ-MG5 — build `check-migrations.sh` now (MG70)?** Facts: semgrep is gone, so migration DDL safety is review-only (`skel:AGENTS.md:181`). P1 still found F3/N2 by review. **Rec:** yes. Run it report-only on the runner for one week, then make it blocking, the same path as mutation (#659).
6. **OQ-MG6 — Java migrations ban (MG3).** Facts: plinth allows them for backfills (`pl-fw:127`). REQ-024 hit Checkstyle `TypeName` and dropped one. None exist. **Rec:** keep the ban as a project decision. Lift it only with a Checkstyle suppression for `db/migration` Java.
