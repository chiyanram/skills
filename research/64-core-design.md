# 64 — Core design from first principles (R38, map #9, chiyanram/skills#86)

Inputs: 64a pstack · 64b firstmate · 64c mattpocock + humanlayer · 64d openclaw + forge + addy · 64e industry.
Method: we take a reference's **reason**, never its rule. A principle enters only when ≥2 independent
sources reach it for a stated reason (a measured incident, an eval, or a vendor's own data).
Each principle is checked against our current design (research/00-decision-register.md).

Status: ✓ we already do it · ◐ partly · ✗ gap.

## A. How rules work

| id | principle (ours) | why — evidence | our design today | status |
|---|---|---|---|---|
| CP1 | **A rule that can be a check becomes a check.** Prose is the fallback, not the default. | forge ADR-0074 (attribution leaked twice despite AGENTS.md); addy #608 (rule in a doc, "nothing enforces it"); matt subagent-recursion.md:7; CC-MEM "context, not enforced configuration"; firstmate layered enforcement doc:17-22 | 4 layers incl. L4 gates; checklist #4 cites gates. But semgrep deleted, many MUSTs have only review behind them | ◐ |
| CP2 | **A rule counts only if it reaches the acting agent, whole.** Size is a hard budget; delivery is tested. | oc: >20K chars → fragments (#163325, #171161); firstmate: hook output >10k truncated to 2k (#7298), 9,000-word ceiling; pstack #597 (evaluated reminder never injected), #577; CC-MEM <200 lines | AGENTS.md <200 lines (AP #646); nested AGENTS.md + CLAUDE.md shims (G1b). No test that a nested file actually loads in each harness | ◐ |
| CP3 | **A rule carries its reason; a line that changes no behaviour is cut.** | pstack #633 (bans → reasons: 0/6 → 6/6 kept the contract test); #571/#634 cuts A/B tested; CC-BP "would removing this cause mistakes?"; firstmate AGENTS.md:430 | checklist #15 no-op test ✓; Rules section is imperative ≤30 words with **no reason** | ◐ |
| CP4 | **A rule changes on evidence: an observed failure in, a measured result out, every "no" written down.** | matt SCOPE.md:9 + .out-of-scope/ (#1190 "reasoning was recorded nowhere"); addy evals/skill-impact.md ledger, #678 fires/stays-quiet numbers; oc reversed its CI rule on 1,892 lanes (299d289e9); firstmate issues quote tokens/minutes | sources rule (SRC1): a rule comes from a reference, our code supplies the Bad. Rejected rules: kept in review pages, no single record. Proof by replay for testing refs (G10) | ◐ |

## B. How agents work

| id | principle | why | ours | status |
|---|---|---|---|---|
| CP5 | **One writer per change; extra agents read, review or research.** | Cognition COG-1/COG-2; Anthropic MARS (coding is less parallel, 15× tokens); pstack orchestrate.md:17 one writer per worktree | developer is the only writer per work item; coordinator never codes (G6) | ✓ |
| CP6 | **Done is read from the forge at a SHA, never claimed.** | forge ADR-0065 ("not the agent's word"); firstmate fm-dod-lib.sh:564 + issue #5944; pstack ledger by head SHA; oc "PR CI = broad proof" | runner pipeline at head SHA blocks merge (AP #671); post-status refuses unpushed done (G9e) | ✓ |
| CP7 | **Authority is declared and enforced below the prompt; capability is not permission.** | firstmate #7172 role gate, #7368 push guard (3 layers); Copilot cannot approve/merge (GH-RISK); forge per-run empty config + read-only token | per-role bots with Developer role (cannot merge); container secrets; egress + plugin allow-lists (G13) | ✓ |
| CP8 | **Never rewrite what a reviewer has seen; keep changes small.** | forge ADR-0069:17; oc AGENTS.md:44 integrate only for a named reason; DORA small batches; oc pr-simplify ~800-line stage rule (from openai/codex) | ① decided 2026-10-16 (#50 comment). No size rule | ◐ |

## C. Humans and cost

| id | principle | why | ours | status |
|---|---|---|---|---|
| CP9 | **Spend the human only on calls only a human can make; silence must mean healthy.** | firstmate VISION.md:16-17, #6682/#6518 (stuck worker looked idle); pstack never-block-on-the-human; matt #1193 (yes = accept) | 3 lanes of escalation, status words, watchdog (G9e, G14). Watchdog keys on missing status for N hours, not on a stuck dialog | ◐ |
| CP10 | **One fresh-context reviewer advises; a human merges.** | CC-BP fresh context; GH-CR advisory by default; COG-2; "reviewers told to find gaps will report some" (CC-BP) | one reviewer, two verdicts, lead validates (G3) ✓; Act-on ≤5 cap whose source pstack deleted after A/B (#634) | ◐ |
| CP11 | **Effort and spend are measured per task, bounded, and attributable.** | hl-ace SlopCodeBench (xhigh 2–4× cost, no reliable gain); forge ADR-0044/45 budgets fail closed; firstmate #5354 per-task ledger (26.5% unattributed); MARS 80% variance = tokens | tokens + wall time per stage, report-only then caps (G14); metrics row (G11). Effort per role not decided | ◐ |
| CP12 | **Tests are the oracle: judge a test by whether it fails on a real defect.** | pstack #633 two imagined edits; addy #618 one-mutant probe; matt #1209 prove the mutation landed; Böckeler MF-TDD (no measured gain from test-first, uses mutation) | test-first for bugs only, PIT on touched classes (G12) | ✓ |

## Open questions this raises (grill one at a time)

1. CP4 — the sources rule: does a rule need **our** observed failure as well as a reference's reason?
2. CP3 — add a one-clause reason to every Rule line in the reference format?
3. CP2 — add a delivery test (each harness actually loads root + nested AGENTS.md) to `make lint`?
4. CP1 — which approved MUSTs move to a check first (the ungated list after semgrep's deletion)?
5. CP10 — drop the Act-on ≤5 cap (②)?
6. CP4/D9 — lesson routing (③): re-source on these principles instead of pstack's deleted ladder?
7. CP8 — a change-size stage rule?
8. CP9 — watchdog detects a worker parked on a dialog, not only silence?
9. CP11 — effort per role/stage as a measured setting?
10. ④ — worker scratch uncommitted, the GitLab comment is the record?
