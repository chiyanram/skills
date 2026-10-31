# PostgreSQL design

Which types, keys, constraints and indexes a PostgreSQL schema uses. Read it when you write or review a migration that
creates a table, adds a column, a key, a constraint or an index.

Contents: Rules · When X, use Y · Good / Bad (MG31, MG35) · Decided edges · Review checks

How to apply these on a table that already holds rows, without blocking it, is in [review.md](review.md) (MG5, MG10,
MG41, MGN1, MG44, MG45).

## Rules

- **MG33** — For every foreign key, create an index whose leading column is the referencing column, because PostgreSQL
  creates none and each parent `DELETE` then scans the child table.
- **MG32** — Write an explicit `ON DELETE CASCADE | SET NULL | RESTRICT` on every `REFERENCES`, because the silent
  default `NO ACTION` makes parent deletes fail in ways nobody designed for.
- **MG35** — Make every column of a `UNIQUE` constraint `NOT NULL`, or declare it `NULLS NOT DISTINCT`, because NULLs
  count as distinct, so duplicate rows containing NULL pass.
- **MG30** — Declare every point-in-time column `timestamptz`, never `timestamp`, because `timestamp` drops the UTC
  offset, so instants written from different zones compare and sort wrongly.
- **MG31** — Declare new string columns `text` with `CHECK (char_length(col) <= n)` for a business limit, never
  `varchar(n)` or `char(n)`, because changing a varchar limit locks the table while a CHECK is replaced `NOT VALID`.
- **MG36** — Never declare `serial`, `integer` keys, `char(n)` or `json`; use `bigint GENERATED … AS IDENTITY` (or
  `uuid`), `text` and `jsonb`, because int keys overflow, char(n) pads, json lacks equality, and serial complicates
  permissions.
- **MG38** — Name every index and constraint with a fixed prefix (`pk_`, `fk_`, `uq_`, `ck_`, `idx_`), because later
  `VALIDATE`, `DROP` and `IF NOT EXISTS` must name it, and a generated name hits the wrong object.

## When X, use Y

| the migration declares | use | why |
|---|---|---|
| a column that holds an instant | `timestamptz` (MG30) | squawk prefer-timestamptz; GitLab migration style guide · r47 :103-104 |
| a new string column with a business length limit | `text` + a `CHECK (char_length(col) <= n)` (MG31; its name, MG38) | squawk prefer-text-field; GitLab strings guide · r47 :111-112 |
| a fixed-length string | `text`, never `char(n)` (MG31, MG36) | PG 8.3 "character(n) is usually the slowest"; squawk ban-char-field · r47 :110, :141 |
| a primary key | `bigint GENERATED … AS IDENTITY`, or `uuid` (MG36) | squawk prefer-identity, prefer-bigint-over-int; GitLab downtime guide · r47 :139-140, :143 |
| a JSON document | `jsonb` (MG36) | PG 8.14 "prefer to store JSON data as jsonb"; strong_migrations · r47 :142 |
| a `REFERENCES` clause | an explicit `ON DELETE` action (MG32) and an index led by the referencing column (MG33) | PG 5.5.5; GitLab foreign keys guide · r47 :118-119, :125-126 |
| a `UNIQUE` constraint or unique index | `NOT NULL` on each column, or `NULLS NOT DISTINCT` (MG35) | PG 5.5.3; GitLab adding indexes guide · r47 :132-133 |
| an index or a constraint | a name with a fixed prefix: `pk_`, `fk_`, `uq_`, `ck_`, `idx_` (MG38) | GitLab constraint naming; PG CREATE INDEX "Index name is required when IF NOT EXISTS is specified" · r47 :148-150 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file.

## Good / Bad

### MG31 — `text` with a named length check

**Bad** (neutral)
```sql
CREATE TABLE customers (
  id    bigint GENERATED ALWAYS AS IDENTITY,
  email varchar(120) NOT NULL,
  CONSTRAINT pk_customers PRIMARY KEY (id)
);
```
Raising the limit later is `ALTER COLUMN … TYPE`, which takes an `ACCESS EXCLUSIVE` lock on the table.

**Good** (neutral)
```sql
CREATE TABLE customers (
  id    bigint GENERATED ALWAYS AS IDENTITY,
  email text NOT NULL,
  CONSTRAINT pk_customers PRIMARY KEY (id),
  CONSTRAINT ck_customers_email_length CHECK (char_length(email) <= 120)
);
```
The limit is a named constraint. A new limit is a new `CHECK` added `NOT VALID`, so the table stays open.

### MG35 — `UNIQUE` on a column that can be NULL

**Bad** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
CREATE TABLE payments (
  id           bigint GENERATED ALWAYS AS IDENTITY,
  customer_id  bigint NOT NULL,
  external_ref text,
  CONSTRAINT pk_payments PRIMARY KEY (id),
  CONSTRAINT fk_payments_customer FOREIGN KEY (customer_id)
    REFERENCES customers (id) ON DELETE RESTRICT,
  CONSTRAINT uq_payments_customer_ref UNIQUE (customer_id, external_ref)
);
```
Two payments for one customer, each with `external_ref` NULL, both pass the constraint.

**Good** (neutral)
```sql
SET LOCAL lock_timeout = '2s';
CREATE TABLE payments (
  id           bigint GENERATED ALWAYS AS IDENTITY,
  customer_id  bigint NOT NULL,
  external_ref text NOT NULL,
  CONSTRAINT pk_payments PRIMARY KEY (id),
  CONSTRAINT fk_payments_customer FOREIGN KEY (customer_id)
    REFERENCES customers (id) ON DELETE RESTRICT,
  CONSTRAINT uq_payments_customer_ref UNIQUE (customer_id, external_ref)
);
```
Every column of the constraint is `NOT NULL`, so it means what it says. The lock timeout is there because the
foreign key locks the existing `customers` table (MG5, `review.md`). The unique constraint leads with
`customer_id`, so it is also the foreign-key index (MG33). When one NULL per customer is meant, keep the column
nullable and write `UNIQUE NULLS NOT DISTINCT (customer_id, external_ref)` (PostgreSQL 15+).

## Decided edges

- **Skip when** a composite index or unique constraint already leads with the referencing column: it is the
  foreign-key index, so add no second one (MG33; GitLab foreign keys guide "OK to have a composite index … so long as
  the foreign key is in the first position", r47 :126). — **Do not skip when** the referencing column is second or
  later in every index on the table. — **Confidence** high

## Review checks

Walk every changed migration file, and every `CREATE TABLE`, `ADD COLUMN`, `REFERENCES`, `UNIQUE`, `CREATE INDEX` and
`ADD CONSTRAINT` in it.

- [ ] MG33 — For each `REFERENCES`, find an index in the same or an earlier migration whose first column is the
  referencing column. A foreign key with none is a finding.
- [ ] MG32 — `grep -n "REFERENCES"` in each changed migration. A clause with no `ON DELETE CASCADE`, `SET NULL` or
  `RESTRICT` is a finding.
- [ ] MG35 — For each `UNIQUE` constraint or unique index, check that every column in it is `NOT NULL`, or that it
  says `NULLS NOT DISTINCT`. A nullable column in a plain `UNIQUE` is a finding.
- [ ] MG30 — `grep -n -i -E "\btimestamp\b"` in each changed migration. A column declared `timestamp` or
  `timestamp without time zone` is a finding; `timestamp with time zone` is `timestamptz` and is not.
- [ ] MG31 — `grep -n -i -E "varchar|character varying|\bcharacter\b|\bchar\b|bpchar"` in each changed migration. A new
  column declared `varchar(n)` or `char(n)` is a finding; a length limit is a `CHECK (char_length(col) <= n)`.
- [ ] MG36 — `grep -n -i -E "\bserial[248]?\b|bigserial|smallserial|\bjson\b"` in each changed migration, and read the
  type of each new key column. `serial`, an `integer` key or `json` is a finding; `char(n)` hits come from the MG31
  grep.
- [ ] MG38 — For each `CREATE INDEX` and each `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE` and `CHECK` (inline or
  `ADD CONSTRAINT`), find its explicit name with a `pk_`, `fk_`, `uq_`, `ck_` or `idx_` prefix. One with no name, or
  with another prefix, is a finding.
