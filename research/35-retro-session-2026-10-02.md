# 35 — Retro: session 33b4f667 (2026-10-01 02:35 → 2026-10-02 13:46 UTC)

Method: mattpocock `retro` v1.3 (`skills/engineering/retro/SKILL.md` @ origin/main) + `writing-for-agents`.
Source: main transcript `~/.claude/projects/-Users-chiyanram-workspace-agent-platform--claude-worktrees-crq-597-b837e3/33b4f667-….jsonl`
(8,046 lines) and its 51 subagent transcripts. Tokens deduped on `message.id`; `output_tokens` in these logs
are captured at stream start and are unusable (see `04-reviewer-cost-baseline.md` §0), so cost = input side.
AGENTS.md size/structure findings are in `34-agents-md-survey.md` and are not repeated here.

```
 session shape
 ─────────────────────────────────────────────────────────────────────────
 main      667 API calls · context 86K (first turn) → 966K (13:16) · 1 compaction (13:18)
           363M cache-read + 3.4M cache-write input tokens
 subagents 51 dispatched · 308M input tokens · median ~6–8M each
 work      wayfinder map (R1–R27, G1–G9) → 129 approved rules → Good/Bad pass → #643 skeleton, !244
```

Severity order: an inert guardrail first, then the biggest token sinks, then repeated mistakes, then load.

---

## 1 · Global git guardrail is inert — fails on every Bash call

- **Category:** automated checks
- **Evidence:** 426 `hook_non_blocking_error` attachments, all the same:
  `PreToolUse:Bash ~/.claude/hooks/block-dangerous-git.sh` → "No such file or directory".
  `~/.claude/settings.json:13` wires it; `ls ~/.claude/hooks/` has only `always-on-orientation.sh`,
  `herdr-agent-state.sh`. The script ships in `mattpocock-skills/1.2.3/skills/misc/git-guardrails-claude-code/scripts/`
  and was never copied (that skill's `SKILL.md:30-35` says to copy + `chmod +x`).
- **Change:** copy the script into `~/.claude/hooks/` and `chmod +x`, or delete the settings entry. A
  `make doctor`-style check that every hook `command` in user + project settings resolves to an executable.
- **Lands:** `~/.claude/hooks/block-dangerous-git.sh`; check in `make doctor` (`scripts/doctor*`).
- **Kind:** mechanical → check.

## 2 · One 35-hour session at up to 966K context; 35% of it spent on one-line approvals

- **Category:** tool economy
- **Evidence:** context per call by hour: 86K (10-01T02) → 586K (10-01T17) → 784K (10-02T06) → 939K
  (10-02T13). 71 user turns are "yes, adopt X" / "yes, approve X". The one-at-a-time rule window
  (10-01T17:48 "ask me one at atime here" → 10-02T05:54) = **180 calls, 127M tokens**, each re-reading
  600–750K of context. After 12:42 ("That file is not openable can you crare aa rtifact"), 114 Good/Bad
  rules were approved through the Rule Review artifact in **10 minutes** (13:04–13:14).
  `~/.claude/settings.json` sets `"model": "opus[1m]"`, so nothing compacted until 13:18.
- **Change:** (a) review queues of >10 items go to an artifact page with per-item approve/reject read back
  in one turn, from the start; (b) one session per wayfinder ticket: the map + issue files already hold
  the state, so a fresh session per G-ticket costs one map read instead of ~700K per turn.
- **Lands:** `~/.claude/always-on/orientation.md` (one line: "a review of more than 10 items → artifact
  page"); wayfinder config `docs/agents/` (a "start a fresh session per ticket" line in the map header).
- **Kind:** judgement → standards (no gate can decide session boundaries).

## 3 · `cd` into an in-repo directory silently moves the session's working directory

- **Category:** navigation / automated checks
- **Evidence:** transcript `cwd` changed and stayed changed 3×:
  10-01T05:38 → `…/refs/imdganesancareers-MasterLaundry` (clone command), 10-01T08:59 → `…/.claude/skills`
  (`cd …/.claude/skills; for s in …`), 10-02T13:42 → `…/.scratch/one-rulebook/refs`
  (`cd …/refs 2>/dev/null || exit; …`). The harness resets cwd only when it leaves the project
  ("Shell cwd was reset" 17× in main); inside the project it sticks. This retro's own subagent was
  launched with primary working directory `…/refs`. `AGENTS.md:134` forbids `cd <dir> && <cmd>` only
  because of permission prompts, so the stronger reason is missing.
- **Change:** PreToolUse Bash hook that warns (exit 0 + stderr) on a command starting with `cd `, naming
  `git -C` / absolute paths. Add the cwd-drift reason to the existing line.
- **Lands:** `~/.claude/hooks/warn-leading-cd.sh` (global: the drift happened in third-party clones too) +
  `AGENTS.md:134`.
- **Kind:** mechanical → check.

## 4 · Counts from text grep were wrong twice; the shipped hook has the same flaw

- **Category:** information access / automated checks
- **Evidence:** 10-02T03:48 "14 ITs on master still use @MockitoBean (verified)" → 03:57 "That was wrong…
  My grep matched the *text*… inside javadoc"; real count 0. 10-02T05:05 "master has **0** spies" →
  12:39 "Master has **4**" (`SetupServiceTest.java:361`, `WorkspaceCallerRoleSpec.groovy:57`,
  `ChatOrchestratorFixture.java:102,167`). Both counts were shown to the user while they decided a rule
  (IT4, K17). `.claude/hooks/warn-mockitobean-in-it.sh` does `grep -q '@MockitoBean'`, so the javadoc
  "no `@MockitoBean`" trips it too; it is wired only on `Write` (`.claude/settings.json`, PostToolUse
  matcher `Write`), so an `Edit` is never checked. `AruviiTestCodeRules.java` holds only
  `noJunitAssertions`.
- **Change:** make the rules gates and let the gate supply the number: ArchUnit
  `noMockitoBeanInIntegrationTests()` and `noSpies()` (annotation/method-call based, not text) in
  `AruviiTestCodeRules`, run by `make test ONLY=arch`. A K17 legacy list (the 4 spies) as a frozen
  baseline. Widen the hook matcher to `Edit|MultiEdit|Write`.
- **Lands:** `aruvii-test-support/src/main/java/ai/aruvii/testsupport/arch/AruviiTestCodeRules.java`,
  `.claude/settings.json`.
- **Kind:** mechanical → check.

## 5 · Good/Bad examples broke house style; a whole v2 pass re-ran

- **Category:** coding standards / automated checks
- **Evidence:** 10-02T12:48 user: "test methid names doesnt follow… shouldXXX… fiunal var or def… why
  some exampels use junit… arguments in multiline". v1 briefs (`31-good-bad-BRIEF.md`) did not name house
  style. v2 (`31-good-bad-v2-BRIEF.md`) added GB1a/U2a/ST1/ST2 and rewrote 81 of 115 Goods. Cost: v1 four
  parts ≈42M tokens, v2 four parts ≈25M. Every adapted example is still labelled `NEEDS COMPILE CHECK`;
  nothing compiles or lints them.
- **Change:** keep example code as real files in a compiled test source set and point the reference docs
  at `path:lines`; then Checkstyle (final locals, one-arg-per-line) and a CodeNarc rule for
  `def "should …"` check them inside `make verify`. Judgement half: an example-writing brief names the
  house-style references (GB1a is that line; keep it in the brief template).
- **Lands:** a `src/test/groovy/…/examples/` source set in `aruvii-test-support`; CodeNarc config next to
  `config/checkstyle/`; brief template (see #7).
- **Kind:** mechanical → check (style); judgement → standards (what makes a Good).

## 6 · `glab` forms the repo already documents were used wrong; `aruvii-git` was never loaded

- **Category:** automated checks / navigation
- **Evidence:** 10-02T13:19 `glab issue create … -F …/issue.md` → "Try --help for usage." (`-F` is a `gh`
  flag). 13:45 `glab mr note 244 -m …` → "Flag --message has been deprecated, use `glab mr note create`";
  13:46 then used `glab mr note create`, which `references/glab.md:17` says opens a resolvable discussion
  and should be `glab api`. Skill calls in the session: `grilling`, `wiki`, `crq` — `aruvii-git` never.
  glab is 1.119.0; `glab.md` was written against 1.115.0 and lists neither failure.
- **Change:** PreToolUse Bash hook built from the `glab.md` failure table: warn on `glab issue create … -F`,
  `glab mr note … -m`, `glab mr note create`, `glab api … --jq`, each naming the working form. Add the two
  new rows to the table.
- **Lands:** `.claude/hooks/warn-glab-forms.sh` + `.claude/settings.json`;
  `.claude/skills/aruvii-git/references/glab.md:38-44`. Use the `hook-from-rule` skill.
- **Kind:** mechanical → check.

## 7 · A long subagent stalled and saved nothing; research briefs lack a completion criterion

- **Category:** tool economy
- **Evidence:** "Good/Bad pass for testing rules" (10-02T07:27, ~150 rules in one agent, 90 calls, 17.1M
  tokens) → "Agent stalled: no progress for 600s"; at 12:20 `31-good-bad-testing.md` did not exist. User
  waited 07:39 → 12:20 ("Try again"). The re-run split 4 ways with per-rule appends finished in 9–18 min
  each. Separately, 10-01T16:18 "did you even read actual filesd… detailed report for ech repo" → 10
  repo-report agents (≈70M) because R3/R5/R9 briefs asked for a synthesis, not per-repo evidence; and
  10-01T15:41 "the subagent got the key point wrong" (R10).
- **Change:** one brief template for research/bulk subagents: ≤30 items per agent; create the output file
  first and append per item; completion criterion = "every source has a section with `path:line`
  evidence"; report "verified vs. claimed".
- **Lands:** `docs/agents/research-brief.md` (pointer from the wayfinder config).
- **Kind:** judgement → standards.

## 8 · Output-format rules live in four places, contradict each other, and miss the two failures

- **Category:** global AGENTS.md / no-ops
- **Evidence:** 10-02T05:55 "The baove format is ntor readble… it collpases" — the reply at 05:54 was an
  aligned code block 167 columns wide. 10-02T12:42 "That file is not openable… artifact… always follws
  this". Sources: `~/.claude/CLAUDE.md:30` "Tables for anything compared" vs
  `~/.claude/always-on/orientation.md:62` "an ALIGNED CODE BLOCK, not a table" vs repo
  `.claude/always-on/agent-output.md:51` (same as orientation) vs the `i-have-adhd` plugin. Global
  `CLAUDE.md:42-58` and `orientation.md:33` both carry "work item is the identity" / "never a bare A or B".
  None caps width or says local files cannot be opened by the reader.
- **Change:** one source (`orientation.md`); delete the duplicates from `~/.claude/CLAUDE.md` and
  `agent-output.md`; add "code blocks ≤ 100 columns" and "material to review or approve → artifact, never
  a path". Optional Stop hook that measures the last reply's code-block width.
- **Lands:** `~/.claude/always-on/orientation.md`, `~/.claude/CLAUDE.md`, `.claude/always-on/agent-output.md`.
- **Kind:** judgement → standards (wording); width cap is mechanical → Stop hook.

## 9 · Worktree names lie about their branch; the plan lived in two copies

- **Category:** navigation
- **Evidence:** 10-02T13:26 Write to `…/worktrees/chore+643-one-rulebook-skeleton/…` refused by the harness
  isolation hook ("belongs to a different worktree"); the agent removed that worktree and checked out
  `chore/643-one-rulebook-skeleton` inside `crq-597-b837e3`. `git worktree list` now shows the same drift
  elsewhere: `crq-577-4869ae → chore/639-…`, `crq-585-d366f1 → claude/crq-488-…`. `AGENTS.md:306` says
  `.claude/worktrees/<prefix>+<rest>`, which a harness-pinned session cannot follow. The map exists in
  both `.scratch/one-rulebook/map.md` and `~/workspace/skills/map.md` (moved 10-02T04:30; old copy has no
  pointer); 13:29 user: "oh we are bntio doing this in skilsl project ? we are doign strght into ariuvii".
- **Change:** one `AGENTS.md` line: "a session pinned to a harness worktree checks the work item's branch
  out there; `git worktree list` shows branch, not the directory name". Replace `.scratch/one-rulebook/`
  with a one-line pointer to `~/workspace/skills`.
- **Lands:** `AGENTS.md:306` / `aruvii-git` `references/worktrees.md`; `.scratch/one-rulebook/map.md`.
- **Kind:** judgement → standards.

## 10 · zsh `==` and missing `timeout` broke 1 in 2 subagents at least once

- **Category:** tool economy
- **Evidence:** "(eval):1: = not found" in 42 tool results across 25 of 51 subagents, plus 4 in main
  (e.g. 10-01T05:47, and this retro's first call). Cause: zsh EQUALS expansion of `echo == x` /
  `echo =====`. "command not found: timeout" 6× (macOS has no GNU `timeout`; 10-01T16:25).
  `--include=*.jsonl` unquoted → "no matches found" (10-01T04:47).
- **Change:** `unsetopt EQUALS` (and `setopt NO_NOMATCH`) in the shell profile the harness snapshots, so
  bash idioms behave. Install `coreutils` or drop `timeout` from briefs.
- **Lands:** `~/.zshenv`.
- **Kind:** mechanical → environment fix.

## 11 · Repo AGENTS.md sediment beyond survey 34

- **Category:** no-ops / global AGENTS.md
- **Evidence (master `CLAUDE.md`):** semgrep's deletion is narrated 4× (`:53`, `:167-170`, `:180`,
  `:279-281`); incident histories in the always-loaded file (`:145-146` the CI minutes story, `:362-371`
  "Corrected (#455)" block, `:226` "#440"). Survey 34 already lists 482 lines, the Codex 32 KiB overrun
  and 3 false claims (`:56` "Two SessionStart hooks" — settings has one).
- **Change:** keep one "ungated rules: review only" line with a pointer; move histories to the ADR /
  `ARCHITECTURE.md` §Doc drift. This is #646's scope (AGENTS.md cut <200 lines) — feed it these line refs.
- **Lands:** `AGENTS.md` via #646 — the AGENTS.md cut to under 200 lines.
- **Kind:** judgement → standards.

## 12 · Always-loaded baseline: 86K before the first word

- **Category:** tool economy
- **Evidence:** first-turn context 86,087 tokens. A 35KB `skill_listing` was injected 11× (~150 skills,
  incl. finance, redis, amazon-location, ultrapowers — none used). "Semgrep Guardian" Stop-hook messages
  237× although the repo deleted semgrep (#440). Two MCP servers asked for auth (finance bigquery/slack).
- **Change:** turn off unrelated plugins for this repo in `.claude/settings.json` `enabledPlugins`
  (false), and the semgrep plugin here.
- **Lands:** `.claude/settings.json` (project) — or `.claude/settings.local.json` for personal ones.
- **Kind:** mechanical → config.

---

## Not findings

- 32 `api_error` ENOTFOUND (10-02T04:10–09:13): network outage, not environment.
- Commits: every commit after 05:24 followed an explicit "commit" from the user; the 04:30/04:57 ones
  followed option lists that included a commit — ambiguous, not counted.
