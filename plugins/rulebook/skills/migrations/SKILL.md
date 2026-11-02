---
name: migrations
description: Use when you write or review a database migration: a new table, column, key, constraint or index, or a change that alters, indexes, renames, drops or backfills an existing table, or edits a merged migration. Lists each migrations reference and when to read it.
---

# Migrations

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [postgres-design](references/postgres-design.md) | MG30–MG33, MG35–MG36, MG38 | when you write or review a migration that creates a table, adds a column, a key, a constraint or an index |
| [review](references/review.md) | MG1, MG5, MG10, MG22, MG41, MG44–MG45, MGN1 | when you write or review a migration that alters, indexes, constrains, renames, drops or backfills an existing table, or that touches an applied migration |
<!-- /index -->
