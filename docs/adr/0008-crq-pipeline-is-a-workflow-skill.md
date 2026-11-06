# 8. The /crq pipeline ships inside the rulebook as the `crq` skill

Status: accepted

## Context

The rulebook says what good work looks like, but it shipped no pipeline that takes a change from request to merge.
Every project wrote its own, and agent-factory's coordinator followed a playbook outside the plugin. The operator
approved one pipeline with lanes, phases and review rubrics (skills#210, decisions D1–D17, 2026-11-06), first as a
second plugin, then amended to stay inside `rulebook` so ADR-0001 holds.

## Decision

The pipeline is the `crq` skill in `plugins/rulebook/skills/crq/`. Its `SKILL.md` describes the phases and who runs
each one. Its references hold the rules only this pipeline needs (lanes, how a review runs, proof of done, code
review, pull request readiness, retro), in the five-section format. Phases reuse the `planning`, `testing` and `code`
references by name instead of repeating their rules.

## Consequences

- A project installs one plugin and gets both the rules and the pipeline.
- The pipeline's own rules go through the ledger and the operator's yes like every other rule.
- agent-factory's coordinator and workers point at the `crq` skill; its scripts enforce what a model must not judge.
