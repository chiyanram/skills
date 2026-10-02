# R14 · Skill and reference writing standards + validation tooling

Ticket: `../issues/29-research-skill-writing-tooling.md` · feeds G10 · read 2026-10-01.
Our target shape (G5, `../issues/13-grill-standards-structure.md:13-14,23-28`): every reference =
**Rules · When X, use Y · Good/Bad pinned file:line · Decided edges · Review checks** (checks last; the
Standards reviewer reads the same file). Rules live in one place (`../issues/05-grill-where-rules-live.md:61-62`).

Sources (abbrev used below):

| id | source | location |
|---|---|---|
| AN | Anthropic skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| CC | Claude Code skills doc · memory doc | https://code.claude.com/docs/en/skills · https://code.claude.com/docs/en/memory |
| SC | installed `skill-creator` | `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/` |
| MP | mattpocock `writing-for-agents` | `refs/mattpocock-skills/skills/productivity/writing-for-agents/SKILL.md`, `SKILL-MECHANICS.md` |
| SP | superpowers `writing-skills` | `r9/obra_superpowers/skills/writing-skills/SKILL.md`, `testing-skills-with-subagents.md` |
| AD | addy `skill-anatomy` + validators + evals | `refs/addyosmani-agent-skills/docs/skill-anatomy.md`, `scripts/`, `evals/README.md` |
| BM | BMAD agent-instructions best practices | `r9/bmad-code-org_BMAD-METHOD/skills/bmad-project-context/references/best-practices.md` |
| PS | pstack playbooks | `refs/cursor-plugins/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md`, `eval.md` |

## 1 · Writing rules per source

| | Length cap | Description shape | Progressive disclosure | Examples | Prohibition vs recipe | Completion criteria |
|---|---|---|---|---|---|---|
| **AN** | SKILL.md body <500 lines; ref >100 lines gets a TOC | 3rd person, what **and** when, ≤1024 chars, no XML | refs **one level deep** from SKILL.md (Claude may `head -100` nested ones) | input/output pairs; "Examples are concrete, not abstract" (checklist) | degrees of freedom: low-freedom exact script for fragile ops, high for judgment | workflow checklist copied into the reply; validator → fix → repeat loop |
| **CC** | SKILL.md <500 lines; CLAUDE.md "target under 200 lines" | description+`when_to_use` capped 1,536 chars; listing budget 1% of context | supporting files; after compaction only the first 5,000 tokens of a skill survive → "put most important instructions near the top" | — | "Write instructions that are concrete enough to verify" (memory) | must-happen → hook, not prose; rules are "context, not enforced configuration" |
| **SC** | <500 lines; >300-line ref needs TOC; metadata ~100 words | what + when, deliberately **"pushy"** to fight under-triggering (`SKILL.md:67`) | 3 levels: metadata · body · bundled (`:86-93`) | one Input/Output pattern | **explain the why**; ALL-CAPS MUST is "a yellow flag" (`:139,302`) | eval loop until user happy / feedback empty |
| **MP** | no number; *sprawl* is the failure | front-load the leading word; one trigger per branch; cut identity | "inline what every branch needs" — disclose what only some branches reach (`SKILL.md:39`) | — | **positive** target; prohibition only as a hard guardrail, paired with the positive (`:74`) | every step ends on a **checkable and exhaustive** criterion (`:47-52`) |
| **SP** | <150 / <200 / <500 **words** by load frequency (`SKILL.md:218`) | "Use when…" triggers **only**, never the workflow — agents follow the summary and skip the body | heavy ref (100+ lines) in separate file; no `@` links (force-load) | **one excellent example**, not multi-language | **Match the Form to the Failure** (`SKILL.md:461-476`): prohibition+rationalization table for discipline slips; positive recipe for wrong shape; REQUIRED slot for omissions; conditional on observable predicate | RED-GREEN-REFACTOR checklist per skill |
| **AD** | SKILL.md <500 lines; inline patterns <50 lines | what (3rd person) + "Use when", ≤1024 | refs one level deep; shared checklists in repo-root `references/` | Good/Bad pairs in sections | rationalizations table + red flags in every skill | **Verification** section: every box needs evidence |
| **BM** | fixed budget; "never raise the budget" (`:45`) | pointer names an **observable** trigger (path, file type, task), never a judged one (`:51`) | load-bearing stays in-block; nested AGENTS.md only if subtree-exclusive | — | "Prefer prohibitions to advice, and name the permitted alternative" (`:22`) | deletion needs 1 of 4 grounds (`:75-82`) |
| **PS** | "When in doubt, delete" (`authoring-a-skill.md:10`) | — | point at structural sources | — | do the thing, skip the reason | validate frontmatter + links; test cases "if structural" |

## 2 · Validation tooling

| Tier | Tool | What it checks | How to run | Cost |
|---|---|---|---|---|
| Static | SC `scripts/quick_validate.py` | frontmatter keys, kebab name ≤64, description ≤1024, no `<>` | `python quick_validate.py <skill-dir>` | free |
| Static | CC `claude plugin validate` (local 2.1.285 ✓) | skills/agents/commands frontmatter; `--strict` fails on warnings | `claude plugin validate .claude/skills --strict` | free |
| Static | AD `validate-skills.js` → `lib/skill-lint.js` | name = dir, required sections present, dead cross-refs, step↔section parity | `node scripts/validate-skills.js` | free |
| Static | AD `validate-reference-links.js` | every `references/*.md` link resolves (they found all 18 links broken) | `node scripts/validate-reference-links.js` | free |
| Static | CC `/doctor prompt-audit` | stale paths/commands, contradictions across CLAUDE.md, rules, skills | in session, ≥v2.1.283 | 1 model pass |
| Trigger | SC `scripts/run_eval.py` / `run_loop.py` | does the description fire on 20 realistic should/should-not queries (×3 each); loop rewrites it, 60/40 train/test | `python -m scripts.run_loop --eval-set … --skill-path … --model <id>` | `claude -p` × 60 per iteration |
| Trigger | AD `run-evals.js` (Tier 2) | lexical TF-IDF: positive prompt ranks its skill top-k; no two descriptions collide | `node scripts/run-evals.js --min-rank1 95` | free, CI-safe |
| Trigger+Δ | CC `claude plugin eval` | whole plugin loaded, case = `prompt.md` + `graders/*.md`; with vs without arm; `tool_used: Skill` grader | `claude plugin eval . --case X --runs 3 --no-publish` | runs × arms; haiku judge |
| Behaviour | SC with-skill vs baseline/old-skill subagents + `agents/grader.md` + `aggregate_benchmark.py` | assertions per eval → pass rate, tokens, time, mean±sd, delta; analyst flags non-discriminating assertions | spawn pairs, grade, aggregate, `generate_review.py` | 2 agent runs per case |
| Behaviour | AD `run-evals.js --behavioral <skill>` | headless `claude` in throwaway git repo from fixtures; grader reads stream-json trace vs `expectations[]`; pressure cases | `--behavioral X --dry-run` first | tokens |
| Behaviour | SP pressure scenarios + micro-tests (`SKILL.md:577-588`) | RED baseline without skill, GREEN with; wording micro-test: **no-guidance control, 5+ reps, read every match** | subagents | cheap per rep |
| Blinded A/B | SC `agents/comparator.md` + `analyzer.md` | judge sees outputs A/B, not which version; analyst explains the winner | subagents | 2 runs + judge |
| Blinded A/B | PS `eval.md` | candidate never sees "eval/test/judge/rubric"; organic prompt; rubric (3-6 criteria) held back; judge different model family; chain graded from **transcripts**, not self-report; lead reads every output | arena skill | N candidates + 1 judge |

AN ships no runner ("no built-in way to run these evaluations"); SC and `claude plugin eval` are the runners.

## 3 · Where sources disagree

| Question | Side A | Side B | Our call |
|---|---|---|---|
| Description: what + when, or when only? | AN, AD, SC: both | SP: triggers only; workflow summary becomes a shortcut | References carry no description; only the 7 router SKILLs do — use **when + what-it-holds, no procedure** |
| Description tone | SC: "pushy" | MP: prune, one trigger per branch | trigger-eval decides, not taste |
| Prohibition vs positive | BM: prefer prohibitions + alternative · SP: prohibition for discipline | MP: negation primes the banned act · SC: MUST is a yellow flag | SP's form-to-failure table: **Rules** = prohibition + alternative only where the baseline is a discipline slip; Good/Bad pair where it is a shape failure |
| Explain why? | SC: always explain why | PS, CC: "State what to do, not why" | one-clause why only when a rule is non-obvious (fits *Decided edges*) |
| Length unit | AN/CC/AD: 500 lines | SP: 150-500 **words** | lines for refs; words only for always-loaded text |
| Test everything? | SP: "No exceptions" · AN: ≥3 evals | SC/PS: skip for subjective · SP testing doc: skip pure reference | our refs are rubric-shaped and objectively gradable (P1 proved it) → test |
| Skills = process or knowledge? | AD: "Process over knowledge" | MP: all-reference document is fine | ours are reference + Review checks; AD's rule does not fit |

## 4a · Writing checklist for our 5-section references (≤20 lines)

```
[ ] 1  ≤300 lines; >100 lines → contents line at top; links one level deep, none to another ref's body
[ ] 2  Rules: ours only — each a checkable sentence a grep or a reader can decide (no "consider", no "prefer")
[ ] 3  Rules: each discipline rule names the permitted alternative in the same line (BM:22)
[ ] 4  Rules: no rule that a hook/Checkstyle/ArchUnit already fails — cite the gate instead (BM:78)
[ ] 5  When X, use Y: X is an observable predicate (file type, annotation, tier, path), never a judgement
[ ] 6  Good/Bad: every sample is file:line in THIS repo, re-verified at write time; Bad is a real past MR finding
[ ] 7  Good/Bad: one pair per rule whose failure is a SHAPE failure (SP form table); no invented code
[ ] 8  Decided edges: Skip when / Do not skip when / Confidence (pstack bugbot format, 13:27-28)
[ ] 9  Decided edges: no nuance clause in a Rule — every exception lives here as its own predicate (SP:475)
[ ] 10 Review checks: last section; one check per Rule, same id, each with its evidence (file:line or grep)
[ ] 11 Review checks: exhaustive bar stated — "every changed test file walked", not "check tests"
[ ] 12 One term per concept across all refs (AN consistent terminology); leading word reused, not redefined
[ ] 13 No dates, counts that rot, or narration ("in !230 we…") — a pinned file:line carries the history
[ ] 14 Most load-bearing rule first (compaction keeps the top 5,000 tokens, CC)
[ ] 15 Every line passes the no-op test: would deleting it change agent behaviour? If not, delete (MP, AD, BM)
[ ] 16 Old reference's lines each mapped to kept / moved / deleted-with-ground (BM 4 grounds) in the MR
```

## 4b · Proof before a rewritten reference replaces the old one

Method: a **P1-style replay** — the shape `../p1/` already used on **#554** (its MR **!230**): frozen diff
(`p1/diff-round1.patch`), ground-truth findings hidden from candidates (`p1/hidden/original-qa-rounds.md`), lead
compares (`p1/lead-judgment.md`). Extend it to a blinded old-vs-new A/B per reference.

```
  pick 2-3 past MRs whose real review hit this ref        e.g. !230 round 1 (F5 vacuous test, F6 final, F7 boundaries)
        │  ground truth = real QA findings + lead verdict, kept in hidden/
        ▼
  ┌── arm OLD: reviewer + old ref ──┐   ┌── arm NEW: reviewer + new ref ──┐   same diff, same organic prompt,
  │  3 runs                         │   │  3 runs                          │   no "eval/judge" words (PS:7-8)
  └──────────────┬──────────────────┘   └───────────────┬──────────────────┘
                 ▼                                       ▼
        blinded judge (other model, sees A/B labels + hidden ground truth as rubric)
                 ▼
  PASS iff  recall(NEW) ≥ recall(OLD) on ground truth  AND  every ground-truth finding owned by this ref is hit
            in ≥2/3 NEW runs  AND  no new false positive the lead rejects  AND  tokens(NEW) ≤ 1.2× OLD
        + author-side twin: implementer arm writes the change from the issue with NEW ref; graded on the same
          Review checks (does the author now avoid what only the reviewer caught — the G5 complaint)
```

| Step | Tool that runs it | Why this one |
|---|---|---|
| Static gate on the new ref (links, frontmatter, 5 headings present) | `claude plugin validate --strict` + a 20-line heading/link check (AD `validate-reference-links.js` is the model) | free; catches the broken-link class AD found |
| Replay arms + grading | **`claude plugin eval`** — one case dir per past MR: `prompt.md` = organic review request, fixture = diff, `graders/*.md` = one `llm` grader per hidden finding + one regex grader for file:line citations; `--ablation` off, old/new run as two plugin dirs; `--runs 3 --model <pinned>` | already installed (2.1.285); scores, HTML report, cost ceiling; record CLI version (AD lesson) |
| Blinded comparison when scores tie | SC `agents/comparator.md` → `analyzer.md` | explains *why* the winner won |
| Final read | lead reads every NEW output (PS step 7) | judges disagree with rubrics; P1 found 5 NEW findings no grader would list |

Cost anchor: P1 single replay = ~246k subagent tokens for two axes (`p1/lead-judgment.md`), so 2 arms × 3 runs ×
1 axis ≈ 0.4-0.8M tokens per reference per MR. Run the full replay for the testing/ refs (where G5's complaint
lives); cheap path (static + 1 MR × 3 runs) for the rest.

Not verified: `claude plugin eval` on a repo-local skills dir (not a packaged plugin) — help text says
"skills-dir plugins both resolve", untried here. AN's Haiku/Sonnet/Opus advice is not applied: fleet pins one model.
