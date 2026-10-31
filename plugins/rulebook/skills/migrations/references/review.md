# Migration review

How a migration changes a table that already holds rows and serves a running app, without blocking it or breaking the
deployed code. Read it when you write or review a migration that alters, indexes, constrains, renames, drops or
backfills an existing table, or that touches an applied migration.

Contents: Rules · When X, use Y · Good / Bad (MG5, MG10, MG41, MG45, MG44, MG22) · Decided edges · Review checks

Which types, keys and names a schema uses is in `postgres-design.md` (MG30–MG38).

## Rules

- **MG5** — Start every migration that locks an existing table with `SET lock_timeout` and retry on timeout, because a
  queued `ACCESS EXCLUSIVE` request blocks every later query on that table.
- **MG10** — Never `RENAME`, `DROP` or retype a column or table the deployed app uses; expand, dual-write, backfill,
  switch reads, then drop next release, because running app versions still query the old shape.
- **MG41** — On an existing table, `CREATE`/`DROP INDEX` only `CONCURRENTLY`, alone in a non-transactional migration,
  after `DROP INDEX CONCURRENTLY IF EXISTS`, because plain builds block writes and failed ones leave INVALID indexes.
- **MGN1** — Add `UNIQUE` or `PRIMARY KEY` to an existing table as `CREATE UNIQUE INDEX CONCURRENTLY` then
  `ADD CONSTRAINT … USING INDEX`, because the inline form builds the index while blocking reads and writes.
- **MG45** — On an existing table, add `CHECK`/FK as `NOT VALID`, validate in a later migration, and reach
  `SET NOT NULL` via a validated `CHECK`, because a direct add scans the table under lock.
- **MG44** — Add a column to an existing table nullable or with a constant `DEFAULT`; never `NOT NULL` without one, nor
  a volatile default, because the first breaks old-code inserts and the second rewrites the table.
- **MG22** — Run backfills in their own migration or job, never beside DDL, as `WHERE`-bounded batches each committed
  alone, because a whole-table statement holds locks and one long transaction for its whole run.
- **MG1** — Never edit, rename or delete a merged or applied versioned migration; write a new one, because its checksum
  then fails `validate` and environments that ran the old text diverge.

## When X, use Y

| the migration, on a table that existed before it | use | why |
|---|---|---|
| runs any `ALTER TABLE`, `CREATE`/`DROP INDEX` or `ADD CONSTRAINT` | `SET LOCAL lock_timeout` first (plain `SET` when non-transactional), and a rerun on timeout (MG5) | PG ALTER TABLE, client config; squawk safe migrations; strong_migrations; GitLab style guide · r47 :160-163 |
| renames, drops or retypes a column or table the app reads | expand → dual-write → backfill → switch reads → drop in a later release (MG10) | GitLab avoiding downtime; strong_migrations; squawk renaming-table, ban-drop-column · r47 :203-205 |
| creates or drops an index | `CONCURRENTLY`, in its own non-transactional migration, after `DROP INDEX CONCURRENTLY IF EXISTS` (MG41) | PG CREATE INDEX; squawk concurrent-index rules; strong_migrations; GitLab; Flyway transactional lock · r47 :169-172 |
| adds `UNIQUE` or `PRIMARY KEY` | `CREATE UNIQUE INDEX CONCURRENTLY`, then `ADD CONSTRAINT … USING INDEX` (MGN1) | squawk disallowed-unique-constraint; strong_migrations · r47 :178-180 |
| adds a `CHECK` or a foreign key | `NOT VALID` now, `VALIDATE CONSTRAINT` in a later migration (MG45) | PG ALTER TABLE; squawk constraint-missing-not-valid; strong_migrations; GitLab foreign keys · r47 :186-189 |
| sets a column `NOT NULL` | a validated `CHECK (col IS NOT NULL)`, then `SET NOT NULL` (MG45) | PG ALTER TABLE "the table scan is skipped"; squawk adding-not-nullable-field; strong_migrations · r47 :186-188 |
| adds a column | nullable, or `NOT NULL` with a constant `DEFAULT` (MG44) | PG ALTER TABLE; squawk adding-required-field, adding-field-with-default; strong_migrations · r47 :195-197 |
| updates or deletes existing rows | its own migration or job, `WHERE`-bounded batches, each committed (MG22) | strong_migrations; GitLab style guide, batched migrations; Django; Flyway RG06, RG09 · r47 :211-214 |
| fixes a migration that is merged or applied | a new versioned migration (MG1) | Flyway migrations, validate; Rails migrations guide · r47 :220-221 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file. Every rule has ≥2
independent industry sources, quoted there; none comes from one project's history (operator, 2026-10-31,
agent-factory#34).

## Good / Bad

### MG5 — A lock timeout before a lock on a live table

**Bad** (neutral)
```sql
ALTER TABLE orders ADD COLUMN note text;
```
It waits for the lock with no limit, and every query on `orders` queues behind it.

**Good** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN note text;
```
After two seconds it gives up, and the queue behind it drains. On "canceling statement due to lock timeout", rerun the
migration.

### MG10 — Rename through expand and contract

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers RENAME COLUMN name TO full_name;
```
The running app still selects `customers.name` and fails until the new version is deployed everywhere.

**Good** (neutral)
```sql
-- Release N   (V30): expand
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers ADD COLUMN full_name text;
-- Release N   app: writes name and full_name, reads full_name, falls back to name
-- Release N   (V31, data job): batched backfill full_name from name (MG22)
-- Release N+1 app: reads and writes full_name only
-- Release N+2 (V40): contract
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers DROP COLUMN name;
```
Every deployed version finds the columns it queries. The drop waits until no running version reads `name`.

### MG41 — A concurrent index in its own migration

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
```
The build blocks every write to `orders` until it ends.

**Good** (neutral)
```sql
-- its own migration, run outside a transaction
-- (Flyway: flyway.postgresql.transactional.lock=false)
SET lock_timeout = '2s';
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_customer_id;
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```
Writes go on during the build. A rerun first drops an INVALID index that a failed build left behind.

### MG45 — `NOT VALID`, then validate in a later migration

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE invoices
  ADD CONSTRAINT fk_invoices_order_id FOREIGN KEY (order_id)
  REFERENCES orders (id) ON DELETE RESTRICT;
ALTER TABLE invoices ALTER COLUMN order_id SET NOT NULL;
```
Both statements scan `invoices` while they hold the lock, and the foreign key also blocks writes on `orders`.

**Good** (neutral)
```sql
-- V20
SET LOCAL lock_timeout = '2s';
ALTER TABLE invoices
  ADD CONSTRAINT fk_invoices_order_id FOREIGN KEY (order_id)
  REFERENCES orders (id) ON DELETE RESTRICT NOT VALID;
ALTER TABLE invoices
  ADD CONSTRAINT ck_invoices_order_id_nn CHECK (order_id IS NOT NULL) NOT VALID;
-- V21 (later migration)
SET LOCAL lock_timeout = '2s';
ALTER TABLE invoices VALIDATE CONSTRAINT fk_invoices_order_id;
ALTER TABLE invoices VALIDATE CONSTRAINT ck_invoices_order_id_nn;
ALTER TABLE invoices ALTER COLUMN order_id SET NOT NULL;
ALTER TABLE invoices DROP CONSTRAINT ck_invoices_order_id_nn;
```
V20 takes the lock without a scan. V21 validates under a lighter lock, and the valid `CHECK` lets `SET NOT NULL` skip
its scan.

### MG44 — A new column on a populated table

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE payments ADD COLUMN currency text NOT NULL;
ALTER TABLE payments ADD COLUMN token uuid NOT NULL DEFAULT gen_random_uuid();
```
The first fails on a populated table, and old code that inserts without `currency` fails too. The volatile default
rewrites the whole table.

**Good** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE payments ADD COLUMN currency text NOT NULL DEFAULT 'EUR';
ALTER TABLE payments ADD COLUMN captured_at timestamptz;
```
A constant default is a metadata change. The nullable column is backfilled later, in batches (MG22).

### MG22 — A batched backfill, apart from the DDL

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN total_cents bigint;
UPDATE orders SET total_cents = (total * 100)::bigint;
```
The DDL lock is held until the whole-table `UPDATE` ends, in one long transaction.

**Good** (neutral)
```sql
-- DDL in V50; this file only DML, one committed batch per key range,
-- repeated by the job or runner until 0 rows are updated
UPDATE orders
SET    total_cents = (total * 100)::bigint
WHERE  id >= :from_id AND id < :from_id + 10000
  AND  total_cents IS NULL;
```
Each batch locks a bounded set of rows and commits. A rerun skips the rows already done.

## Decided edges

- **Skip when** the table is created in the same migration: a plain `CREATE INDEX` or an inline constraint is fine,
  because no rows or readers exist yet (MG41, MG45, MGN1; squawk "This rule ignores indexes added to tables created
  in the same transaction", r47 :170). — **Do not skip when** the table existed before this migration, even if it is
  empty. — **Confidence** high
- **Skip when** the new column's `DEFAULT` is a constant: no rewrite happens (MG44; PG ALTER TABLE "a non-volatile
  DEFAULT … In neither case is a rewrite of the table required", r47 :195). — **Do not skip when** the default calls a
  volatile function such as `clock_timestamp()` or `gen_random_uuid()`: the table and its indexes are rewritten.
  — **Confidence** high

## Review checks

Walk every changed or added migration file, and every statement in it that touches a table created before it.

- [ ] MG5 — In each migration that runs `ALTER TABLE`, `CREATE`/`DROP INDEX` or `ADD CONSTRAINT` on an existing
  table, `grep -n "lock_timeout"` before the first such statement. A missing timeout is a finding.
- [ ] MG10 — `grep -n -i -E "RENAME|DROP (COLUMN|TABLE)|ALTER COLUMN .* TYPE"`. For each hit, find the earlier release
  that stopped the app reading the old shape. A rename, drop or type change with no such release is a finding.
- [ ] MG41 — `grep -n -i "INDEX"`. On an existing table, a `CREATE` or `DROP INDEX` without `CONCURRENTLY`, one in a
  transactional migration or beside other DDL, or a `CREATE` with no `DROP INDEX CONCURRENTLY IF EXISTS` first, is a
  finding.
- [ ] MGN1 — `grep -n -i -E "ADD (CONSTRAINT [a-z_]+ )?(UNIQUE|PRIMARY KEY)"`. On an existing table, one without
  `USING INDEX` over an index built `CONCURRENTLY` is a finding.
- [ ] MG45 — `grep -n -i -E "ADD CONSTRAINT|SET NOT NULL|VALIDATE CONSTRAINT"`. On an existing table, a `CHECK` or
  foreign key added without `NOT VALID`, a `VALIDATE` in the same migration as its `ADD`, or a `SET NOT NULL` with no
  validated `CHECK (col IS NOT NULL)` before it, is a finding.
- [ ] MG44 — `grep -n -i "ADD COLUMN"`. On an existing table, a `NOT NULL` column with no `DEFAULT`, or a `DEFAULT`
  that calls a volatile function, is a finding.
- [ ] MG22 — `grep -n -i -E "^\s*(UPDATE|DELETE|INSERT)"`. A data statement in a file that also holds DDL, or an
  `UPDATE`/`DELETE` with no `WHERE` bounding a key range, is a finding.
- [ ] MG1 — `git diff --name-status` against the target branch over the migration directory. A modified, renamed or
  deleted versioned migration that is already merged is a finding.
