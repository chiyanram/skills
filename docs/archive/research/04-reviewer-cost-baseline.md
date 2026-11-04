# R4 · Reviewer cost baseline

Answers `issues/04-research-reviewer-cost-baseline.md`. Source: subagent transcripts
`~/.claude/projects/*/*/subagents/*.jsonl` (agent type from sibling `.meta.json`). Pricing:
platform.claude.com/docs/en/about-claude/pricing (fetched 2026-10-01). Scripts: session scratchpad
`turns.py` (per-call breakdown), `measure.py` / `m2.py` (original measurement).

## 0 · Correction to the 208M figure

```
jsonl: one line per content block, each repeating the same message.id + usage
measure.py summed per LINE  ->  ~2x overcount
```

| metric (57 reviewer runs) | as first reported | deduped by `message.id` |
|---|---|---|
| cumulative input tokens | 208M | **101.2M** |
| median per run | 3–4M | **1.3M spec · 1.5M arch · 1.7M standards** |
| "turns" | 40–80 | **16–19 API calls** (median) |
| first-call ctx · peak ctx | ~30k · 90–177k | unchanged (28–37k · 103–147k median) |

Token mix: **92.2% cache read · 7.8% cache write (all 5-minute) · ~0% fresh input.**
Logged `output_tokens` are captured at stream start (single digits per call) and are unusable;
output is estimated below from context growth.

## 1 · Summary table — three representative runs

| run | model | API calls | first · peak ctx | billed input | est. cost |
|---|---|---|---|---|---|
| `code-standards-reviewer` #577 (Ollama bounds) !223, stage 7 | Opus 5.5 | 24 | 37.9k · 125k | 2.23M | **$1.95** |
| `architecture-reviewer` #577 (Ollama bounds) !223, stage 7 | Opus 5.5 | 19 | 32.5k · 133k | 1.76M | **$1.92** |
| `spec-design-reviewer` #308 (IT HTTP connection reuse) !220, stage 5 | Opus 5 | 16 | 29.2k · 134k | 1.43M | **$2.85** |

Prices used ($/MTok, 5m write · cache read · output): Opus 5.5 `5 · 0.20 · 20`; Opus 5 `6.25 · 0.50 · 25`.
Fleet-wide (101M input, mixed Opus 5 / 5.5): roughly **$2–2.8 per review, ~$110–160 for the 57.**

## 2 · Turn-by-turn shape (standards run, abbreviated)

```
call  ctx     added by previous call's tools                  bucket
 1    37.9k   — (preload: system + CLAUDE.md + agent def + 45.5k-char rubric)
 2    39.9k   git merge-base/status/diff --stat   0.3k        code/diff
 3    63.2k   git diff (code)  6.3k  x2 — SAME command twice  code/diff
 4    75.5k   cat 3 changed files in full  6.9k + thinking    code/diff
 5–9  ~82k    docker run probes, grep siblings   <1k each     verify
10–12 ~90k    cat references/{error-handling,types-and-null,
              comments,testing,test-quality}.md   ~9k         REF
14    101k    cat .claude/rules/{java-standards,observability,
              it-testing}.md   3.6k                           rules
15–22 ~118k   greps, sed -n of siblings          ~0.2–1k each verify
23    120k    SubagentHandback (report ~2k)                   output
```

Every row is re-sent on every later call. Context grows ~4k/call, of which ~45% is the model's own
thinking + tool-call text, not tool results.

## 3 · Bucket attribution

Token share = tokens × calls they ride through. Dollar share = cache write once + cache reads +
output price for generated tokens.

| bucket | standards tok · $ | architecture tok · $ | spec tok · $ |
|---|---|---|---|
| (1) fixed preload (first-call ctx × N) | 41% · 19% | 35% · 15% | 33% · 15% |
| (2) rubric re-read | 0 · 0 | 0 · 0 | 8% · 4% |
| (2) REF / rules / authority docs | 8% · 6% | 10% · 7% | 14% · 10% |
| (3) code / diff / glab / REQ | 22% · 11% | 24% · 12% | 7% · 4% |
| (4) verification greps + sibling reads | 2% · 2% | 5% · 3% | 3% · 3% |
| (5) model output: thinking, tool calls, report | 27% · **62%** | 25% · **63%** | 35% · **66%** |

Caveat: tool-result tokens estimated at chars/3.5; the 4.7+ tokenizer runs ~30% denser, so
bucket (5) may be overstated by ~10 points and (3)/(2) understated. Ranking does not change.

## 4 · "Rubric loaded twice" — confirmed, but cheap

| reviewer | runs | runs that re-read own `SKILL.md` via tool |
|---|---|---|
| `architecture-reviewer` | 22 | 18 |
| `spec-design-reviewer` | 24 | 17 |
| `code-standards-reviewer` | 9 | 4 |
| `smoke-spec-reviewer` | 2 | 0 |

Evidence: the `skills:` preload injects the full file (standards 45.5k chars = `SKILL.md` 46.2k;
spec 23.5k = 23.9k) as the second user message; spec run call 1 then `Read`s
`spec-review/SKILL.md` (6.2k tok) + `MEMORY.md`. Cost: 8% of tokens, **4% of dollars (~$0.10)**.
Side finding: that re-read hit the **main checkout** path, not the worktree — it can read a
different rubric version than the one preloaded.

## 5 · Top 5 cost drivers (by dollars)

1. **Model output, mostly thinking — 62–66%.** ~44–52k generated tokens per run at $20–25/MTok,
   then cache-written and re-read. Driven by number of calls × deliberation per criterion walked.
2. **Fixed preload re-sent every call — 15–19%** (33–41% of tokens). ~30–38k × 16–24 calls.
   Rubric is ~6–12k of it; the rest is system prompt, CLAUDE.md, agent definition.
3. **Diff + full changed-file reads early — 11–12%** (22–24% of tokens). Front-loaded, so carried
   through every later call. Standards run ran the identical `git diff` twice (+6.3k).
4. **REF / authority reading — 6–10%.** Spec reviewer: ADR README, ADRs, CONTEXT, PRODUCT-DESIGN,
   ROADMAP (29k tokens added).
5. **Rubric re-read — 0–4%** where it happens (39 of 57 runs).

Verification greps — the thing the rubric's CHECK steps ask for — are the cheapest bucket (2–3%).

## 6 · Fleet QA comparison (!230, #554)

| | laptop stage 7 (#577, !223) | fleet QA round 1 (!230) |
|---|---|---|
| standards subagent | peak ctx 125k · 2.23M billed · $1.95 | ~135k |
| architecture subagent | peak ctx 133k · 1.76M billed · $1.92 | ~167k |

The fleet's 135k / 167k matches the **peak-context** scale (Agent tool's `total_tokens`), not the
cumulative billed input. Like for like, the fleet round is ~10–25% larger per subagent; at the
laptop ratio (billed ≈ 13–18× peak) one fleet round is ~$4–5 of reviewer spend, ~$12–15 over
!230's three QA rounds.

## Implications for G3

- Cutting the rubric re-read saves ≤4%. Diff-scoping criteria (decision A) attacks driver 1:
  fewer criteria walked = fewer calls and less thinking.
- Dropping `spec-design-reviewer` removes the most expensive per-run reviewer (~$2.85 on Opus 5).
- Shrinking preload helps linearly with call count; fewer calls helps everything.
