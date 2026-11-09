# 5. Provenance lives only in the ledger

Status: accepted

Amended by [ADR-0009](0009-a-second-plugin-of-typed-only-tools.md).

## Context

Citations, dates and credits in a reference cost the agent context and change nothing it does.

## Decision

A shipped file holds only what an agent needs to act. Where each rule came from lives in the ledger,
[approved-rules.md](../rulebook/approved-rules.md): one row per rule with its source, evidence and status.
`check_provenance.py` fails a shipped file that carries a citation, URL, date, credit or evidence note outside code.

## Consequences

- References stay short.
- Every rule still traces to a source, through its ledger row.
