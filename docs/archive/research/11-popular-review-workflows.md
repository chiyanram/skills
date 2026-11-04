# R9 · Popular (>10k★) review workflows — how they pick criteria

Issue: `issues/18-research-popular-review-workflows.md` · Informs: G3 (`issues/07-grill-review-shape.md`).
Stars read 2026-10-01 via `gh api repos/OWNER/REPO --jq .stargazers_count`. Sources: shallow clones of each repo
(paths below are repo-relative) and the local `refs/` copies. No secondary sources.

## 1 · Ranked comparison (by stars, 2026-10-01)

| # | repo · ★ | (a) shape | (b) criteria chosen by | (c) input | (d) noise / cost bound |
|---|---|---|---|---|---|
| 1 | openclaw/openclaw · 391,125 | `autoreview`: one external reviewer, Codex preferred over Claude (cross-model). Separate deterministic security tier | autoreview: **model judgement** ("Let the reviewer choose how to analyze"). Security tier: **path globs → category → one `review:` line** (`.github/security-review-policy.yml`, first match wins) | helper script assembles the git target; reviewer gets target + context | default threshold **P0 only**; `--max-priority` widens (`.agents/skills/autoreview/SKILL.md`) |
| 2 | obra/superpowers · 293,744 | one reviewer per task, **two verdicts** (spec + quality), plus one whole-branch final review | **fixed checklist** in the prompt + the plan's "Global constraints". No repo standards file | **pushed**: `scripts/review-package` writes commits + stat + diff to a file; reviewer "Read the diff file once" | ≤5 fix rounds; reviewer may not spawn sub-reviewers; model tier scaled to diff risk (`skills/subagent-driven-development/SKILL.md`) |
| 3 | mattpocock/skills · 273,530 | two parallel axes, Standards ‖ Spec, reported side by side, never reranked | **all** repo standards files found (`CODING_STANDARDS.md`, `CONTRIBUTING.md`) + fixed Fowler-smell baseline pasted | diff **command** passed (sub-agent runs it); smell baseline pasted | "Under 400 words" per axis; skip what tooling enforces |
| 4 | affaan-m/ECC · 270,476 | `/orch-review`: one agent per dimension in parallel → dedup → adversarial verifier on every CRITICAL/HIGH | **router**: quality always + **language reviewer by dominant file extension** + **security by regex** over diff/paths (`workflows/orch-review.workflow.js`). Rules carry `paths:` frontmatter (`rules/java/coding-style.md`) | caller computes diff + language, passes `args` | `/review-pr`: confidence ≥ 80; orch: verifier splits blocking vs advisory; concurrency capped |
| 5 | anthropics/claude-code · 148,807 | `code-review` plugin: haiku gate → 2× CLAUDE.md agents + 2× Opus bug agents in parallel → **one validator sub-agent per finding** | **path-scoped CLAUDE.md**: root + those "in directories containing files modified"; only files sharing a path with the code count | haiku agent returns CLAUDE.md **paths**; agents get PR title/desc; diff fetched with `gh pr diff` | "only HIGH SIGNAL issues"; unvalidated findings dropped; explicit false-positive list. (`README.md` still says 0–100, threshold 80; the command now validates instead.) `pr-review-toolkit`: **router by what changed** — tests → test-analyzer, error handling → silent-failure-hunter, types → type-design-analyzer |
| 6 | github/spec-kit · 139,674 | no diff reviewer in product; `/analyze` (artifacts) and `/converge` (code vs spec) are single read-only passes | **whole constitution, always**; MUST violations auto-CRITICAL (`templates/commands/analyze.md`) | spec/plan/tasks + constitution; converge is "not a diff tool" | "Limit to 50 findings total" |
| 7 | openai/codex · 127,507 | `/review`: single pass, structured JSON | **scoped AGENTS.md "applicable to changed files"**, more-specific wins (`codex-rs/prompts/templates/review/rubric.md`) | git target chosen by user | P0–P3 tag + `confidence_score` per finding + overall verdict; only bugs "introduced in the commit" |
| 8 | addyosmani/agent-skills · 100,268 | `/review`: one reviewer, five axes. `/ship`: 3 personas in parallel (code-reviewer, security-auditor, test-engineer) → go/no-go | **all five axes always**; project conventions referenced generically | staged changes / recent commits | Critical/Important/Nit labels; "a few high-conviction comments beat a long list" |
| 9 | OpenHands/OpenHands · 89,704 | single agent, keyword-triggered skill `/codereview` | public `code-review` skill + **one repo guide** (`.agents/skills/custom-codereview-guide.md`) + `AGENTS.md` | linked issue, ACs, review threads, PR head | APPROVE or COMMENT only; "Never use REQUEST_CHANGES" |
| 10 | bmad-code-org/BMAD-METHOD · 53,697 | `thorough`: 4 parallel context-free lenses (Blind Hunter, Edge Case Hunter, Verification Gap, Intent Alignment) → lead triage | lenses fixed; `quick` lens reads `AGENTS.md`/`CLAUDE.md` "at the repository root and in the directories the diff touches" (`skills/bmad-code-review/customize.toml`) | **pushed as file path**: "a launch prompt never carries diff text" | lens severities ignored; lead renders one verdict each → patch / decision_needed / defer / reject; Blind Hunter has a *floor* `min(√kB+1, 10)` |
| 11 | wshobson/agents · 40,130 | `/full-review`: 5 sequential phases, 2 agents in parallel per phase, human checkpoint between phases | **all dimensions always**; flags (`--security-focus`, `--framework`) tune | target path; phase outputs written to `.full-review/` and fed forward | human approval at each `PHASE CHECKPOINT` |
| 12 | continuedev/continue · 36,078 | **one agent per check file**, each its own PR status | checks: one file = one criterion set, all run. Rules: `globs:` / `regex:` / `alwaysApply` / description-pull (`docs/customize/deep-dives/rules.mdx`) | PR diff; "only suggest changes adjacent to/within the scope" | one commit per check; no finding → no PR |
| 13 | The-PR-Agent/pr-agent (was qodo-ai) · 13,219 | single LLM call per `/review` | fixed prompt sections toggled by `require_*` + `extra_instructions` + **fixed** `repo_context_files` (default `["AGENTS.md"]`) — not by path | **pushed**, compressed diff, `max_model_tokens = 32000`, `large_patch_policy = "clip"` | `num_max_findings = 3` (`pr_agent/settings/configuration.toml`); config from default branch only |

Checked, no review workflow: anthropics/skills 179,264 (no review skill in `skills/`), Aider-AI/aider 49,314,
humanlayer/12-factor-agents 26,515 (principles doc), VoltAgent/awesome-agent-skills 35,087 (list).
Not examined (time): sst/opencode 211,272, google-gemini/gemini-cli 107,215, cline/cline 69,657.
Under 10k, dropped: anthropics/claude-code-action 9,311, coderabbitai (largest OSS repo 1,784).

**(e) Roles / handoff, where present.** superpowers: implementer → task reviewer → fix rounds → final reviewer;
reviewer lists "Declined to judge" items and "The executor rules on each line". BMAD: lenses report, the lead
triages (lenses "lack the context to grade"). ECC: reviewers → verifier → blocking/advisory. wshobson: phases with
human gates.

## 2 · Part 2 — the three we lean on

| | (a) shape | (b) criteria | (c) input | (d) bound | (e) roles |
|---|---|---|---|---|---|
| **pstack** `interrogate` (cursor-plugins/pstack) | one reviewer **per model** (Opus / GPT / Grok) [drift 2026-10-17: now two reviewers, Opus + Grok (#511), see research/64a], same prompt; "signal comes from model diversity, not assigned personas" | **fixed**: `references/rubric.md` (6 lenses) + `code-quality-review.md`, all pasted; reviewer applies those "that you find relevant" | **pushed**: intent paragraph + diff/files + rubric + lens filled into `reviewer-prompt.md` | lead buckets Act on / Consider / Noted / Dismissed; "more than 5 items, you're probably not filtering hard enough" (`lead-judgment.md`) | lead = "pragmatic senior engineer, not a neutral aggregator"; consensus across models weighted up |
| **pstack** `poteto-mode` | routes contested design to `interrogate`; no reviewer of its own | **trigger-per-principle**: "Each entry names when it applies" — model judgement against those triggers | file pointers, not inlined context | `bugbot-triage.md`: fix / dismiss / ask | owner reviews every sub-agent diff itself |
| **firstmate** → **no-mistakes** (kunchenguid; 7,406★ / 8,710★) | pipeline `review → test → docs → lint → push → PR → CI`; one review agent per run, configurable harness | **path globs, deterministic**: `review.path_instructions` (`path` + `instructions`) in `.no-mistakes.yaml`; "selects the trusted rules whose glob matches at least one changed path" (`internal/pipeline/steps/review_path_instructions.go`). Unmatched/duplicate/unusable rules are logged by id | base/head given; "Read the relevant history and diff yourself" (fetched). Path rules read **only from default-branch config** so a branch cannot steer its own review | severity error/warning/info × action **auto-fix vs ask-user**; `auto_fix.review: 0` by default | firstmate worker drives the run; ask-user findings go to firstmate / human (`.agents/skills/validation-supervision/SKILL.md`) |
| **mattpocock** `code-review` | Standards ‖ Spec, parallel, side by side | Standards: every standards doc found, all at once + Fowler baseline; Spec: issue/spec found by commit refs | diff command + file list (agent reads) | 400 words / axis; "Do not merge or rerank" | none beyond the caller |

## 3 · How criteria get chosen — the patterns

```
P1  everything, every time      spec-kit, addyosmani, wshobson, superpowers, mattpocock, pstack
P2  fixed file list             pr-agent (repo_context_files), OpenHands (one guide)
P3  directory-scoped agent file claude-code code-review, codex, BMAD quick   (CLAUDE.md/AGENTS.md of touched dirs)
P4  glob → rule block           no-mistakes path_instructions, openclaw security tier, Continue globs, ECC rules paths:
P5  router → reviewer agent     ECC (extension→language reviewer, regex→security), claude-code pr-review-toolkit
P6  model judgement             openclaw autoreview, poteto-mode triggers, Continue description-pull
```

- **P3/P4 are the path-selection family.** P3 selects by *directory ancestry*; P4 by *explicit glob per rule*.
  Only no-mistakes logs which rules matched and which did not.
- **Trust boundary appears twice**: no-mistakes and pr-agent read review config from the default branch only, so
  a branch cannot rewrite the rules that gate it.
- **Noise control splits two ways**: a cap or threshold (pr-agent 3, spec-kit 50, codex/ECC/openclaw confidence or
  priority), or a second judge (claude-code validator per finding, ECC verifier, BMAD lead, pstack lead).
- **Input pushed vs fetched**: pushed — superpowers, BMAD (as a file path), pstack, pr-agent. Fetched by the
  reviewer — mattpocock, no-mistakes, claude-code (`gh pr diff`).

## 4 · Against the decided G3 shape (facts only)

Decided: mattpocock two axes (Standards ‖ Spec) + pstack code-quality lens + pstack lead judgment by qa (Act on ≤5 …);
Standards criteria = repo reference files selected by changed path, each ending "Review checks"; inputs pushed;
≤400 words/axis.

**Confirms**
- Path-selected criteria is an established pattern (P3/P4) in claude-code `code-review`, codex, BMAD `quick`,
  no-mistakes, ECC, Continue. no-mistakes is the closest match: glob → instruction block → appended to the prompt.
- ECC already uses the exact `paths:` frontmatter on rule files that our `.claude/rules/` uses.
- A judge after the reviewers is common (claude-code, ECC, BMAD, pstack). BMAD also discards reviewer severity.
- Spec as a separate verdict: superpowers (spec + quality), BMAD (Intent Alignment), mattpocock.
- Pushing the diff: superpowers and BMAD write it to a file and pass the path.

**Contradicts / differs**
- mattpocock itself feeds **all** standards docs, not a path-selected subset; and passes a diff *command*, not the diff.
- pstack applies **all** lenses every time and gets diversity from **multiple models**; G3 uses one model per axis.
- claude-code runs **two** independent CLAUDE.md agents plus a validator per finding — more seats than G3.
- No surveyed project ends each standards file in a "Review checks" section; criteria are prose rules or one
  `review:`/`instructions:` string per glob.

**Missing pieces (present elsewhere, absent from the G3 decision)**
- **Matched/unmatched log**: no-mistakes logs which path rules applied and which did not.
- **Trust source for criteria**: no-mistakes/pr-agent read rules from the default branch, not the branch under review.
- **Bug/correctness seat**: claude-code, codex, ECC, BMAD run a correctness reviewer independent of standards; G3
  has Standards and Spec only.
- **Findings validation**: claude-code validates each finding before reporting; ECC verifies CRITICAL/HIGH.
- **"Declined to judge" list** (superpowers) so set-aside items are ruled on, not silently dropped.
- **Fix-round cap** (superpowers 5; no-mistakes `auto_fix.review: 0`).
