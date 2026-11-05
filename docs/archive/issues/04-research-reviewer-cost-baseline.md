# R4 · Reviewer cost baseline

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G3

## Question

What does one review cost today, per reviewer and per stage, and where do the tokens go (rubric load,
REF reads, per-criterion Bash checks, receipts)? Start from the 57-run / 208M measurement; break down
2–3 representative runs turn by turn. Include the fleet QA's per-round figure (135k + 167k).

## Resolution (2026-10-01)

Findings: `../research/04-reviewer-cost-baseline.md`. Earlier 208M figure double-counted (one jsonl line per
content block repeats usage); deduped **101.2M over 57 runs**, median 1.3–1.7M / run, 16–19 API calls,
~$2–2.8 per review (Opus 5.5). Cost: thinking/output 62–66% · per-call preload 15–19% · diff+files 11–12% ·
rule/REF docs 6–10% · rubric re-read ≤4% (happens in 39/57 runs) · greps 2–3%. Fleet QA round on !230
≈ $4–5, 3 rounds ≈ $12–15. Lever for G3: fewer calls + less thinking via diff-scoped criteria.
