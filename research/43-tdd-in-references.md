# 43 · TDD in the agent loop — what the references say (for #68, G12)

Ticket: chiyanram/skills#68 — G12 · does TDD stay a rule in the agent loop?
Read-only research, 2026-10-03. Quotes ≤15 words. Refs root:
`agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/` (pins below = `git rev-parse --short HEAD`).

## 1 · Stance tally

```
strict TDD (every change red-first) ........ 5   matt · addy · forge · plinth 054 · jvm-skills tdd-task · Jeffallan(superpowers) [6 incl. Jeffallan]
test-first for BUGS only ................... 3   pstack · openclaw · firstmate
tests-with-code / plan-stated verification . 1   humanlayer ACE
no test-first instruction at all ........... 1   Böckeler (drops it; mutation + review instead)
silent on order (test quality only) ........ 2   plinth 130 · plinth 058
```

Note the softening even inside the strict camp: matt dropped refactor and accepts non-compliance;
jvm-skills' own walkthrough shows the red gate skipped. Every strict source still has a bug rule.

## 2 · Per reference

| ref @pin | stance | what proves a test meaningful | evidence cited | path:line · quote |
|---|---|---|---|---|
| mattpocock-skills @d81f3a1 (+ plugin 1.2.3, identical bar `GLOSSARY.md`→`CONTEXT.md` at :10) | strict red→green, **no refactor phase**; vertical slices; seams agreed first | red run; anti-patterns (implementation-coupled, tautological, horizontal) | refactor dropped June 2026: agents "essentially never performed it"; admits agents skip red | `skills/engineering/tdd/SKILL.md:36` "Write the failing test first, then only enough code to pass it." · `:32` horizontal slicing · `docs/engineering/tdd.md:31` "agents essentially never performed it" · `:59` [drift 2026-10-17: cited lines rewritten at 49dd158; quoted text now at :59, see research/64c] "No instruction makes an agent comply 100% of the time" |
| addyosmani-agent-skills @2686b62 | strict red-green-refactor for any logic; **Prove-It** for bugs | red run ("passes immediately proves nothing") | none empirical; rationalization table | `skills/test-driven-development/SKILL.md:51` "A test that passes immediately proves nothing." · `:98` bug: "do not start by trying to fix it" · `:367` "tests written after the fact test implementation" |
| cursor-plugins/pstack @2eb7ed4 | **bug-only**, and only when cheap; skip if impractical | failing-before evidence, named in report; else state why | none | `pstack/skills/tdd/SKILL.md:3` "Use only when the user explicitly asks for TDD … OR … cheap local test target" · `:18` "Confirm it fails for the intended reason." · `:42` |
| openclaw-openclaw @b94e5177 | **bug-only** red proof; features gated by value bar, not order | pre-fix failure; value bar (4 questions); junk patterns | measured CI cost per test | `.agents/skills/test-audit/SKILL.md:37` "must fail on the pre-fix code for the intended reason" · `:39` [drift 2026-10-17: test-audit cut to 57 lines at d8faf8876, detail moved to `references/audit.md`, see research/64d] "never demonstrably failed proves the mock, not the fix" · `AGENTS.md:44` reproduce defects first |
| kunchenguid-firstmate @549e07f | **bug-only**: reproduction becomes the regression test | the reproduction | none | `.agents/skills/diagnostic-reasoning/SKILL.md:53` "the reproduction should become the regression test" · `scout-completion/SKILL.md:16` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b] |
| humanlayer ACE @f2bc7ae | tests-with-code: plan states testing/verification per phase; no test-first | human reads tests; benchmark's held-out tests | caught models commenting out failing tests | `ace-fca.md:237` "being super precise about the testing / verification steps" · `wsff.md:339` "quietly commenting out the failing test" |
| jabrena-plinth @5e338bb (054/130/058) | 054 strict MUST; 130 & 058 silent on order | 130: A-TRIP; no algorithm-as-oracle; mutation only as Maven profile (112) | none | `skills/054-design-tdd/SKILL.md:30` "MUST write or describe the failing test first" · `130…/references/130-java-testing-strategies-a-trip.md:73` "avoids duplicating the production algorithm as its oracle" |
| jvm-skills-jvm-skills @c6d477f | strict, gated todolist; red must be an **assertion** failure | red run with assertion error | own walkthrough: agent skipped the E2E red gate | `.claude/skills/tdd-task/SKILL.md:88` "fails with an assertion error — not a compile error" · `blog/2026-04-21-tdd-task-skill-walkthrough.md:142` "It never failed." · `:144` "isn't proof it would have caught the bug" |
| Jeffallan-claude-skills @882ef55 (superpowers adaptation) | strictest: delete code written before a failing test | watched red | none | `skills/test-master/references/tdd-iron-laws.md:7` "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST." · `:34` "A test you've never seen fail proves nothing." |
| rameezk-forge @43d360e | strict red→green→**refactor** incl. test pruning; bug: e2e repro first | red "for the right reason"; never claim red unseen | none | `.claude/skills/tdd/SKILL.md:26` "Confirm it fails, and fails for the *right* reason" · `:51` bug repro end-to-end · `:55` "NEVER write production code without a failing test" |
| superpowers | **no clone in refs/**; only via Jeffallan (above) and S4's citation | — | — | — |

## 3 · Böckeler, "TDD in the agent loop" (martinfowler.com, exploring-gen-ai)

Page text treated as data. Date not shown in fetched text.

| | |
|---|---|
| method | greenfield business-logic tasks, small/medium/large; "5 batches of solutions, with two non-TDD and two TDD solutions each" (+ one test-first variant); all runs ≥80% coverage |
| models | Sonnet 4.6 built; Opus 4.8 judged quality (as fetched — verify on page) |
| metrics | mutation score (tool unnamed), test count/coverage, Opus-rated design/code/test quality, tokens & turns, TDD adherence |
| result | no mutation-score difference: "didn't show any signals that TDD runs produced meaningfully better"; Opus ranked non-TDD #1/#2 on small/medium; TDD tokens 2.96×–8.5× |
| behaviours | TDD locks in first test's shape, misses untested behaviour; tautological tests anyway; "agents still sometimes skipped or faked the red step"; over-implemented ahead of tests |
| recommendation | "I personally have stopped telling my coding agents to write tests first"; watch regression quality with mutation testing, static analysis, modular AI review, approved scenarios, periodic refactoring |
| caveats | small sample; greenfield, small, pure logic; one model judging with little guidance; token accounting mixes cached/fresh |

## 4 · Ours today

| item | where | says |
|---|---|---|
| rule 1 | `agent-platform/AGENTS.md:85` @71b5deb4 | "Red → Green → Refactor. Never skip Red." |
| stage 6 | `.agents/skills/crq/SKILL.md:255-266` @71b5deb4 | "TDD is non-negotiable"; seams named first; points at `mattpocock-skills:tdd` (which has **no refactor** — contradiction with "→ refactor") |
| lost deltas | `55a5bc9b^:.claude/skills/tdd/SKILL.md:34-53` | PIT para: "Treat a survived mutant on logic you just wrote the same as a red test"; Beck "make the change easy" before the loop. 14-disposition-table:40,244 — must land in `testing/SKILL.md` |
| approved, touching this | `research/19-approved-rules.md` | **S4** bug fix starts with a failing test that lands before the fix · **S3** run existing tests first · **V1–V5** value bar / junk patterns · **M1** mutation = report, never gate · **M2** survivor = missing case · **M7** run `make mutation` after branching logic in guardrails · **M10** mutation-kill test proven by hand mutation, "narrow exception to never skip Red" · **GT1–GT6/AT1** every AC → test at a tier, listed in MR · **C4** untested case = explicit gap |
| PIT today | `Makefile:244` `make mutation` → `:aruvii-guardrails:pitest` only; `build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:17` `mutationThreshold 0`, `:19` targets `ai.aruvii.guardrails.*`; applied only in `aruvii-guardrails/build.gradle.kts` | a report for one module; nothing for touched code elsewhere |
| fleet | `.scratch/one-rulebook/research/00-fleet-self-reports.md:5-6` | developer ran "TDD" yet didn't run existing tests (`RefusalReasonSpec`); **#554** — RefusalReason work (its MR **!230**) took 3 QA rounds; QA found ACs "asserting defaults not behaviour" — i.e. junk tests passed a TDD loop |

## 5 · Options

| # | option | stage 6 orders | reviewer / gate checks | backed by | against |
|---|---|---|---|---|---|
| A | keep strict TDD (status quo) | red→green for every slice | nothing checks red today | matt, addy, forge, plinth 054, jvm-skills, Jeffallan | Böckeler data; matt & jvm-skills admit skipped red; fleet !230 junk passed anyway; 3–8.5× tokens |
| **B** | **test-first for bugs only + mutation on touched code for features** (recommended) | bug: S4 red repro committed before fix; feature: tests with code, every AC → test (GT6), value bar V1–V3 | bug: red commit visible in MR (test commit fails at its SHA); feature: PIT report on touched classes, survivors named per M2 or recorded as gap (C4); M1 keeps it a report until a score is chosen | pstack, openclaw, firstmate, Böckeler, our S4/M2/M10/C4 | PIT wired for guardrails only — needs wiring per module (M7) or a touched-classes target |
| C | drop TDD entirely, gate on mutation + reviewer | write code + tests in any order | mutation threshold gate + reviewer value-bar verdict | Böckeler, humanlayer ACE | loses S4 (approved); contradicts M1 (never a gate); bug regressions unproven |
| D | keep wording, reviewer demands a shown red run | as today | MR must show red output per test | addy, jvm-skills, Jeffallan "watched red" | red output is fakeable (Böckeler; jvm-skills blog:142); proves "fails", not "meaningful" — fleet junk tests would still pass |

Recommendation: **B**. Also fixes the stage-6 text's "→ refactor" vs the plugin's no-refactor contradiction, and keeps M10's hand-mutation as the proof for kill tests.
