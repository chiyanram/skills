# 2. One skill per domain, with a router table

Status: accepted

## Context

A rulebook that an agent must read in full costs context on every task, and most of it does not apply.

## Decision

Each domain (`testing`, `code`, `agent`, `migrations`, `obs`, `planning`, `meta`, `deslop`) is one skill. Its
`SKILL.md` is a router: a table of its references, their rule IDs and when to read each.

## Consequences

- An agent reads only the references the task needs.
- A project points at a reference by skill and name, never by path, because the install folder differs per machine.
