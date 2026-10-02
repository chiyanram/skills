# P1 · Scoped reviewer on a past MR

Type: wayfinder:prototype (HITL) · Status: closed · Assignee: claude · Blocked by: G3 (closed)
Part of: ../map.md

## Question

Run the G3 reviewer shape on one past MR (!230, the fix for #554) and compare tokens, turns and findings
against the original QA rounds.

## Run log (2026-10-01)

Setup — G3 shape on !230's ROUND-1 head, so it compares with the real QA round 1:
- diff: `git diff 92cbf4b5...70b84c0b` (merge-base) → `../p1/diff-round1.patch`, 20 files, +673/−4 (same 20 files QA round 1 read).
- Standards packet `../p1/packet-standards.md` (19.7k words): intent + 13 path-matched files read from master
  (java-standards, it-testing, migrations rules; types-and-null, type-design, error-handling, comments, test-value-bar,
  coverage-design, boundaries-correct, testing, test-quality, migration-review) + pstack correctness and code-quality
  lenses + mattpocock Fowler smells + diff. NOTE: today's references, not yet rewritten to the 5-section shape and
  with no Review checks — this run tests shape and cost, not the future content.
- Spec packet `../p1/packet-spec.md` (14.6k words): #554 body (no comments) + REQ-075 + diff.
- Original QA rounds 1–3 saved to `../p1/hidden/` — reviewers are told not to read it; the lead reads it only after judging.
- Two fresh general-purpose subagents launched in parallel, read-only, ≤400 words each.
- Results: `../p1/report-standards.md`, `../p1/report-spec.md`, `../p1/lead-judgment.md`. Found real F1–F5 + 5 new
  (2 shipped to master); missed F6 (`final`), F7 (boundaries). Cost 246k vs ~302k subagent tokens. Awaiting operator.

## Resolution (2026-10-01)

Run 1 confirms the G3 shape (round 1 found real F1–F5 + 5 new, 2 of them shipped; missed F6 `final`, F7 boundaries;
246k vs ~302k subagent tokens). Operator: **show the comparison again once the standards are rewritten.** → Not a map
ticket any more: it becomes an acceptance criterion of the REQ — "after the references are rewritten to the G5 shape,
re-run P1 on !230 round 1 with the same packets builder; report run 2 vs run 1 vs real QA (findings, misses, tokens)".
Packet builder steps and inputs are in this log and `../p1/`.
