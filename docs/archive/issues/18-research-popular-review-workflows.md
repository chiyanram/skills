# R9 · Highly-rated (>10k★) agent SDLC / review workflows — how they pick review criteria

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G3

## Question

Which open-source agent workflow / skills / review projects have >10k GitHub stars (verified today), and for each:
how is code review shaped, how are review criteria chosen for a given diff (all at once, by path, by router, by
model judgement), what is fed in, how is cost bounded, and how do roles/personas hand off? Plus the same five
questions for pstack, firstmate and mattpocock from their source.

## Resolution (2026-10-01)

Findings: `../research/11-popular-review-workflows.md` (stars via gh api 2026-10-01; spot-checked superpowers 293,750,
openclaw 391,125, pr-agent 13,219, no-mistakes 8,710). 13 repos >10k with a review workflow. Six criteria-selection
patterns; **by changed path is established** (no-mistakes `review.path_instructions` →
`internal/pipeline/steps/review_path_instructions.go`, verified; ECC rules `paths:`; openclaw security tier; Continue
globs). Differences: matt feeds all docs; pstack diversity = models; nobody ends standards files with Review checks.
Missing from G3, present elsewhere: matched-rules log; rules read from default branch only; separate correctness
reviewer; validate each finding before reporting; "declined to judge" list; cap on fix rounds. Not examined: opencode,
gemini-cli, cline.
