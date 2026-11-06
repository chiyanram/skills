# 6. Router tables are generated

Status: accepted

## Context

A hand-edited index drifts from the references it lists.

## Decision

`make index` builds each router's table from its references: the "Read it when …" sentence and the rule IDs.
`check_index.py` fails a table that differs from what `make index` builds.

## Consequences

- Never edit a router table by hand.
- When two pull requests conflict on a table, take either side and run `make index` again.
