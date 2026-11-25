# Migration examples

Good / Bad pairs for the rules in [SKILL.md](SKILL.md).

## `text` with a named length check

From "Design: types, keys, names".

**Bad**
```sql
CREATE TABLE customers (
  id    bigint GENERATED ALWAYS AS IDENTITY,
  email varchar(120) NOT NULL,
  CONSTRAINT pk_customers PRIMARY KEY (id)
);
```
Raising the limit later is `ALTER COLUMN … TYPE`, which takes an `ACCESS EXCLUSIVE` lock on the table.

**Good**
```sql
CREATE TABLE customers (
  id    bigint GENERATED ALWAYS AS IDENTITY,
  email text NOT NULL,
  CONSTRAINT pk_customers PRIMARY KEY (id),
  CONSTRAINT ck_customers_email_length CHECK (char_length(email) <= 120)
);
```
The limit is a named constraint. A new limit is a new `CHECK` added `NOT VALID`, so the table stays open.

## `UNIQUE` on a column that can be NULL

From "Design: types, keys, names".

**Bad**
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

**Good**
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
foreign key locks the existing `customers` table. The unique constraint leads with
`customer_id`, so it is also the foreign-key index. When one NULL per customer is meant, keep the column
nullable and write `UNIQUE NULLS NOT DISTINCT (customer_id, external_ref)` (PostgreSQL 15+).

## A lock timeout before a lock on a live table

From "Changing a live table", Lock timeout first.

**Bad**
```sql
ALTER TABLE orders ADD COLUMN note text;
```
It waits for the lock with no limit, and every query on `orders` queues behind it.

**Good**
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN note text;
```
After two seconds it gives up, and the queue behind it drains. On "canceling statement due to lock timeout", rerun the
migration.

## Rename through expand and contract

From "Changing a live table", Expand and contract.

**Bad**
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers RENAME COLUMN name TO full_name;
```
The running app still selects `customers.name` and fails until the new version is deployed everywhere.

**Good**
```sql
-- Release N   (V30): expand
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers ADD COLUMN full_name text;
-- Release N   app: writes name and full_name, reads full_name, falls back to name
-- Release N   (V31, data job): batched backfill full_name from name
-- Release N+1 app: reads and writes full_name only
-- Release N+2 (V40): contract
SET LOCAL lock_timeout = '2s';
ALTER TABLE customers DROP COLUMN name;
```
Every deployed version finds the columns it queries. The drop waits until no running version reads `name`.

## A concurrent index in its own migration

From "Changing a live table", Indexes concurrently.

**Bad**
```sql
SET LOCAL lock_timeout = '2s';
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
```
The build blocks every write to `orders` until it ends.

**Good**
```sql
-- its own migration; Flyway runs a CONCURRENTLY script outside a transaction
-- (set flyway.postgresql.transactional.lock=false once, in the Flyway config)
SET lock_timeout = '2s';
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_customer_id;
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```
Writes go on during the build. A rerun first drops an INVALID index that a failed build left behind.

## `NOT VALID`, then validate in a later migration

From "Changing a live table", Validate later.

**Bad**
```sql
-- V19, its own migration: CREATE INDEX CONCURRENTLY idx_invoices_order_id ON invoices (order_id)
SET LOCAL lock_timeout = '2s';
ALTER TABLE invoices
  ADD CONSTRAINT fk_invoices_order_id FOREIGN KEY (order_id)
  REFERENCES orders (id) ON DELETE RESTRICT;
ALTER TABLE invoices ALTER COLUMN order_id SET NOT NULL;
```
Both statements scan `invoices` while they hold the lock, and the foreign key also blocks writes on `orders`.

**Good**
```sql
-- V19, its own migration: CREATE INDEX CONCURRENTLY idx_invoices_order_id ON invoices (order_id)
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

## A new column on a live table

From "Changing a live table", New columns.

**Bad**
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE payments ADD COLUMN currency text NOT NULL;
ALTER TABLE payments ADD COLUMN token uuid NOT NULL DEFAULT gen_random_uuid();
```
The first fails on a populated table, and old code that inserts without `currency` fails too. The volatile default
rewrites the whole table.

**Good**
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE payments ADD COLUMN currency text NOT NULL DEFAULT 'EUR';
ALTER TABLE payments ADD COLUMN captured_at timestamptz;
```
A constant default is a metadata change. The nullable column is backfilled later, in batches.

## A batched backfill, apart from the DDL

From "Changing a live table", Backfill apart.

**Bad**
```sql
SET LOCAL lock_timeout = '2s';
ALTER TABLE orders ADD COLUMN total_cents bigint;
UPDATE orders SET total_cents = (total * 100)::bigint;
```
The DDL lock is held until the whole-table `UPDATE` ends, in one long transaction.

**Good**
```sql
-- DDL in V50; this file only DML. The job runs it once per key range, commits each,
-- and advances :from_id by 10000 until :from_id > max(id)
UPDATE orders
SET    total_cents = (total * 100)::bigint
WHERE  id >= :from_id AND id < :from_id + 10000
  AND  total_cents IS NULL;
```
Each batch locks a bounded set of rows and commits. A rerun skips the rows already done.
