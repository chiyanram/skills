# G8 · Does /crq route by task type (bug / feature / refactor / chore), and how?

Type: wayfinder:grilling (HITL) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md

## Question

Today every change walks all /crq stages (a 5-line bug fix gets grill → REQ → draft MR → /approved). Should /crq pick a
stage set by task type or size, inside the ONE crq.md (G2), and who decides the type? Inputs: pstack poteto-mode's 23
playbooks (steps copied verbatim, `skip: <reason>`), ECC size tier → phase mask (research/repos/ecc-and-claude-code-plugins.md),
BMAD quick-flow (retired into dev, CHANGELOG.md:388), humanlayer oneshot / oneshot_plan commands, fleet self-reports.

## Grilling log

- Facts: crq.md:40 "never skip a stage"; crq.md:110-111 already routes the SPEC by type (bug amends REQ; chore/refactor/
  docs use the issue). ECC orch-pipeline/SKILL.md:39-54 size tier → phase mask, highest signal wins, user overrides.
- **Q1 DECIDED (operator, 2026-10-01): A — one crq.md with an intake step mapping (type × size) to a stage mask**,
  stated in one line at stage 1, operator can override; floor: migration / security / public API / new dependency →
  at least standard (full spec gate); skipped stages stay listed as `skip: <reason>`.
- Q2 asked: who classifies, and can a classification change mid-flight?
- **Q2 DECIDED (operator): A — the analyst proposes (type × size) at stage 1, the coordinator relays it, the operator OKs
  or overrides; any worker may ESCALATE (e.g. hits a floor trigger → stops, handoff comment, back to stages 2–5 +
  /approved); a downgrade needs the operator's explicit word.**

## Resolution (2026-10-01)

One crq.md; stage 1 sets a stage mask from (type × size), stated in one line, operator can override. Floor: migration /
security / public API / new dependency → at least standard (full spec gate + /approved). Skipped stages stay listed as
`skip: <reason>`. Analyst proposes; workers escalate only, never downgrade. Backing: ECC orch-pipeline:39-54, pstack
poteto-mode:117, humanlayer oneshot, no-mistakes scope-growth rule, firstmate §11.
