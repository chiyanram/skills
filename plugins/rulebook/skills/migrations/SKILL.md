---
name: migrations
description: "Use when you write or review a database migration: a new table, column, key, constraint or index, or a change that alters, indexes, renames, drops or backfills an existing table, or edits a merged migration. PostgreSQL types, keys and names, lock timeouts, concurrent indexes and batched backfills."
---

# Migrations

A migration earns its place when every deployed version of the app keeps working while it runs, and after. Everything
below serves that. The SQL for each rule, bad and good: [examples.md](examples.md).

## Before you write

Sort each statement by the table it touches:

- **New table**: created in this same migration. Only the design rules apply.
- **Live table**: it existed before this migration, holds rows and serves the running app. The design rules apply,
  and so does every rule under "Changing a live table", because a lock on it queues every query behind it.

A merged or applied versioned migration is history: fix it with a new migration, because an edited one fails its
checksum on `validate` and environments that ran the old text diverge.

## Design: types, keys, names

- An instant is `timestamptz`, because `timestamp` drops the UTC offset, so instants from different zones compare and
  sort wrongly.
- A string is `text`; a business length limit is a named `CHECK (char_length(col) <= n)`, because changing a
  `varchar(n)` limit locks the table, while a new `CHECK` goes in `NOT VALID`. `char(n)` pads with spaces.
- A key is `bigint GENERATED … AS IDENTITY` or `uuid`, and a column that references it has the same type, because an
  `integer` key overflows and `serial` complicates permissions.
- A JSON document is `jsonb`, because `json` has no equality operator.
- Each `REFERENCES` says `ON DELETE CASCADE`, `SET NULL` or `RESTRICT`, because the silent default `NO ACTION` fails
  parent deletes nobody designed for.
- Each foreign key has an index led by the referencing column, because PostgreSQL creates none and each parent
  `DELETE` then scans the child table. An existing index or unique constraint that leads with that column is that
  index already.
- Each column of a `UNIQUE` constraint is `NOT NULL`, or the constraint says `NULLS NOT DISTINCT` (PostgreSQL 15+),
  because NULLs count as distinct and duplicate rows with a NULL pass.
- Each index and constraint has an explicit name with its prefix, `pk_`, `fk_`, `uq_`, `ck_` or `idx_`, because a
  later `VALIDATE`, `DROP` or `IF NOT EXISTS` must name it, and a generated name hits the wrong object.

## Changing a live table

- **Lock timeout first.** Start each migration that locks a live table with `SET LOCAL lock_timeout = '2s'` (plain
  `SET` in a non-transactional migration, where `SET LOCAL` does nothing), and rerun it on a timeout. This covers
  `ALTER TABLE`, `CREATE` or `DROP INDEX`, `DROP TABLE`, `TRUNCATE`, and a `CREATE TABLE` that `REFERENCES` it.
- **Expand and contract.** To rename, drop or retype a column or table the app uses: add the new shape, dual-write,
  backfill, switch reads, and drop the old shape in a later release, because running app versions still query it.
- **Indexes concurrently.** Build or drop an index with `CONCURRENTLY`, alone in its own non-transactional migration,
  after `DROP INDEX CONCURRENTLY IF EXISTS`, because a plain build blocks writes and a failed concurrent build leaves
  an INVALID index. An index on a new table is a plain `CREATE INDEX`.
- **Unique and primary keys by index.** Build `CREATE UNIQUE INDEX CONCURRENTLY` in one migration, then
  `ADD CONSTRAINT … USING INDEX` in the next, because the inline form builds the index while it blocks reads and
  writes.
- **Validate later.** Add a `CHECK` or a foreign key `NOT VALID`, then `VALIDATE CONSTRAINT` in a later migration,
  because a direct add scans the table under lock. Reach `SET NOT NULL` through a validated
  `CHECK (col IS NOT NULL)`, which lets it skip the scan.
- **New columns.** Add a column nullable, or `NOT NULL` with a constant `DEFAULT`, because `NOT NULL` with no default
  breaks inserts from old code, and a volatile default such as `gen_random_uuid()` rewrites the table.
- **Backfill apart.** Update or delete rows in their own migration or job, in `WHERE`-bounded key-range batches, each
  committed alone and safe to rerun, because a whole-table statement holds its locks in one long transaction.

## Reviewing a migration

Walk every added or changed migration file, and every statement in it. Read each whole `ALTER TABLE` statement,
since one can span lines. Each line below is a finding when it holds.

- `git diff --name-status` against the target branch: a merged versioned migration is modified, renamed or deleted.
- `grep -n -i -E "\btimestamp\b"`: a column is `timestamp` or `timestamp without time zone`.
- `grep -n -i -E "varchar|character varying|\bchar\b|bpchar"`: a new column is `varchar(n)` or `char(n)`.
- `grep -n -i -E "\bserial[248]?\b|bigserial|smallserial|\bjson\b"`, and the type of each key and key reference: a
  `serial`, an `integer` key or reference, or `json`.
- `grep -n "REFERENCES"`: a clause has no `ON DELETE` action, or no index in this or an earlier migration leads with
  its column.
- Each `UNIQUE`: a nullable column without `NULLS NOT DISTINCT`.
- Each index and constraint: no explicit name, or a name without its prefix.

On a live table, also:

- `grep -n "lock_timeout"`: no timeout before the first locking statement, or `SET LOCAL` in a non-transactional file.
- `grep -n -i -E "RENAME|DROP|TYPE "`: a rename, drop or retype with no earlier release that stopped the app reading
  the old shape.
- `grep -n -i "INDEX"`: an index built or dropped without `CONCURRENTLY`, in a transactional file, beside another
  statement, or with no `DROP INDEX CONCURRENTLY IF EXISTS` first.
- `grep -n -i -E "UNIQUE|PRIMARY KEY"`: one added inline rather than `USING INDEX` over a concurrent build.
- `grep -n -i -E "ADD +(CONSTRAINT|CHECK|FOREIGN KEY)|REFERENCES|SET NOT NULL|VALIDATE"`: a `CHECK` or foreign key
  without `NOT VALID`, a `VALIDATE` beside its `ADD`, or `SET NOT NULL` with no validated `CHECK` before it.
- `grep -n -i "ADD COLUMN"`: `NOT NULL` with no `DEFAULT`, or a volatile `DEFAULT`.
- `grep -n -i -E "\b(UPDATE|DELETE|INSERT)\b"`: data beside DDL, an `UPDATE` or `DELETE` with no key-range `WHERE`,
  or more than one batch in one transaction.
