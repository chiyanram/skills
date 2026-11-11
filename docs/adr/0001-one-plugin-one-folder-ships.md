# 1. One plugin, and only its folder ships

Status: accepted

Amended by [ADR-0009](0009-a-second-plugin-of-typed-only-tools.md). Superseded in part by
[ADR-0010](0010-plugins-may-ship-small-check-scripts.md): a plugin may ship small check scripts.

## Context

Other repos and worker containers install the rulebook. Design work, checks and tests also live in this repo.

## Decision

The repo ships one plugin, `rulebook`, from `plugins/rulebook/`. The marketplace entry points only at that folder.

## Consequences

- A project installs one thing.
- Design work, the repo's own scripts and tests never reach an agent's plugin cache (ADR-0010 lets a plugin ship small
  check scripts).
