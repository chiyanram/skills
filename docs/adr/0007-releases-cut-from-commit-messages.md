# 7. Releases are cut from commit messages

Status: accepted

Amended by [ADR-0009](0009-a-second-plugin-of-typed-only-tools.md), and by #276 and #285: a release runs only when
someone starts `release.yml` on `main`.

## Context

Claude Code pins a plugin to the `version` in its manifest. Users see an update only when that version changes.

## Decision

semantic-release cuts every release from the Conventional Commits on `main`, when someone runs `release.yml` by hand.
A `feat` or `fix` to what ships bumps the version, writes `CHANGELOG.md` and tags `rulebook--v<version>`.

## Consequences

- A shipped change always reaches users as a new version.
- Nobody edits a version or the changelog by hand.
