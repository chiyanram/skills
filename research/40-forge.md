# R31 · rameezk/forge — what applies to our coordinator/workers, rulebook and gate (#64)

Source: https://github.com/rameezk/forge @ `43d360e` (2026-10-02), shallow clone at
`agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/rameezk-forge`. Read only; nothing run.
Compared against #9 "Decisions so far", #35 comments (Q23 · Q24 · Q26 · ND-5 · ND-15), #50 resolution (groups 1–5, Q18).

## What forge is

A "declarative software factory": a Nix-defined NixOS box (Hetzner) that runs **workers** (harness `pi` + model + prompt)
as sandboxed, unattended **workloads** against GitHub tickets, and records transcript, tokens and billed cost per run
on a tailnet-only dashboard (`README.md:5-11`). No coordinator agent — a timer polls the ticket frontier and dispatches.

## Structure

```
forge/
├── AGENTS.md                 35 lines, universal rules only (no comments, no em dash, no attribution)
├── docs/CONTEXT.md           glossary (worker, workload, frontier, dispatch, cohort, skill load …)
├── docs/adr/0001–0037        one decision each, immutable except Status
├── .agents/skills/<15>       canonical skills ── .claude/skills/<15> are symlinks into it
│     refine → to-spec → to-tickets → work-on   (pipeline; disable-model-invocation: true)
│     work-on drives: git-worktree · tdd · git-committing · code-review ‖ security-review · git-pr · before-after
│     git-pr-address-comments · decision-context · tracker-config · git-branching
├── runtime/packages/         runner (spawns pi, sandbox, transcript) · frontier (poll) · billing · frontend · pi-subagent
├── infra/nix/*.nix           NixOS module + VM tests (dispatch, sandbox, contract checks)
├── templates/operator/       scaffold for the per-operator repo (config.json, divergence-guard.sh)
└── Makefile                  check = flake-check + tofu-test + repo-generic + template-scaffold
```

## Per area

| area | what forge does (path:line) | our decision | verdict |
|---|---|---|---|
| roles / agents | No roles or souls. A worker is "harness + model + prompt + optional effort" (`docs/CONTEXT.md:17-18`); the skill is the process. | G2 (#15) roles say only *who*; #50 g2 soul = 3 sentences + "you own" | **match** (process owns steps); forge goes further — no soul at all |
| roles / agents | Builder spawns its own reviewers as subagents, "separate sub-agents launched in one message" (`.agents/skills/work-on/SKILL.md:39`); subagent depth capped at 1 (`docs/adr/0009…:19`) | G2 + Q23 (#35): qa is a separate fresh read-only worker at stages 7–8 | **contradicts** (reviewer is a child of the developer, not its own worker) |
| coordinator / orchestration | None. Timer polls frontier; dispatch when ticket is on frontier AND labelled `forge:ready` (`docs/adr/0016…:18`) | G6 (#25) one always-on coordinator; relays every question | **contradicts** — forge is the fully autonomous end, closer to D1 (#21) without the human channel |
| coordinator / orchestration | Workers run unattended: "no human will answer questions … stop, and end with the question" (`runtime/packages/runner/src/harness.ts:13-17`) | G6 interactive worker; #50 g3 reversible → default, high-level → stop + relay | **partial** — same split (settled → proceed, else stop), but nobody relays |
| coordinator / orchestration | Claim lives on the ticket: `forge:ready → running → done/failed`, retry = set `forge:ready` again (`docs/adr/0016…:18`); blocked + labelled = queued (`docs/CONTEXT.md:86-88`) | G6 / G2: GitLab comment = handoff record; WIP limit "not yet specified" on #9 | **new idea** (claim survives coordinator loss; queue by blockers) |
| coordinator / orchestration | Tickets classed `ready-for-agent` / `ready-for-human` at slicing; human-flagged ones need confirmation before build (`to-tickets/SKILL.md:36`, `work-on/SKILL.md:29`) | G8 (#30) floor → full path; #50 g1 "high-level" definition | **match** in intent; forge decides it per ticket at slicing time, we per stage at relay time |
| coordinator / orchestration | One recipe for every ticket; no lanes | G8 + Q24 (#35) quick / standard / full lanes | **contradicts** (we chose lanes) |
| skills / rules layering | `.agents/skills` canonical, `.claude/skills/*` symlinks; AGENTS.md universal-only (35 lines) | G1 (#14) agent-agnostic AGENTS.md index; WIP `71b5deb4` moves skills to `.agents/skills` | **match** — same layout we are moving to |
| skills / rules layering | Workflow skills are `disable-model-invocation: true` and called by name: "load that skill and follow its instructions in full" (`work-on/SKILL.md:25`), never a `head` or line range | R2 (#11) skills fire when a command says "run X"; R4 (#13) rubric re-read | **match** + **new**: explicit "read every line, no partial read" rule |
| skills / rules layering | Runner passes skills and root AGENTS.md as explicit args from a fresh clone; dispatch **fails before start** if the named skill is missing or two files share its name (`docs/adr/0018…:22-27`, `docs/adr/0023…:23`) | G4 (#17) identical files on laptop and VM; #50 g3 missing brief field → refuse to spawn | **match** + **new**: fail-closed on missing/ambiguous skill |
| skills / rules layering | Nothing loaded from run-writable state; bubblewrap sandbox (`docs/adr/0015…:18`, `docs/CONTEXT.md:31-33`) | G4 tiers; D1 (#21) role boxes | **new idea** for D1 — a worker can rewrite skills/hooks in its own worktree that later runs load |
| skills / rules layering | Upstream-shaped skills (refine ≈ grilling, to-spec, to-tickets, tdd) are **copied** into the repo | G1 upstream = plugins, never copies | **contradicts** |
| review | Two axes kept apart, "Do not merge or re-rank findings across axes" (`code-review/SKILL.md:68`); nested → two inline passes in one context (`:46`) | G3 (#16) AMENDED: one reviewer, two verdicts, lead validates each finding | **match** — forge's nested mode *is* our amended shape |
| review | Standards axis always carries a Fowler smell baseline, repo overrides, "always a judgement call" (`code-review/martin-fowler-code-smells.md:5-6`) | G3 correctness + code-judo lenses; review direction A (repo criteria by diff) | **new** — overlaps code-judo; generic list on top of repo criteria |
| review | `security-review` is a third always-run reviewer (OWASP + CWE + STRIDE, severity, `file:line`) (`security-review/SKILL.md:10`) | G8 floor treats security as a lane trigger; no dedicated security reviewer | **new idea** |
| review | Re-review scoped by what the fix commits changed, not by who raised the finding (`work-on/SKILL.md:43`) | G3 fix diff only after round 1 | **match** |
| review | Loop "until every review comes back clean"; surface to user only when the same finding repeats (`work-on/SKILL.md:45`) | G3 3-round cap | **contradicts** (no cap) |
| review | Review report opens `Reviewed <base-sha>...<head-sha>`; PR opens only if each review's last clean SHA covers HEAD or later commits "provably cannot reach the review's domain" (`work-on/SKILL.md:47`, `git-pr/SKILL.md:61-65`) | #9 not-yet-specified "verdict tied to head SHA, reused after rebase when patch-id unchanged"; #50 g4 qa verdict tied to SHA | **match** + **new**: per-commit domain-reachability exemption written into the MR |
| verification / CI | Developer runs formatter/lint/type-check before review so reviewers skip them (`work-on/SKILL.md:35`) | Q26 (#35) developer minimum = touched-module tests + verify-fast + honest what-ran | **match** |
| verification / CI | Required checks read from branch-protection API; "no checks reported" is "never a result"; poll until they appear (`work-on/SKILL.md:51`) | R28 (#60) / Q26 self-hosted runner + "Pipelines must succeed" | **new idea** for the runner wiring |
| verification / CI | `make check` fails when the Linux builder is unreachable rather than skipping VM tests; CI is a required check (`docs/adr/0036…:18`) — but no `.github/` exists at `43d360e` | Q26 runner; CLAUDE.md "no CI" lesson (#440) | **match** (fail, don't skip) · ADR/repo **drift** worth noting: the decided CI is absent |
| handoff / status | Only ticket writes are labels; "never comments, links runs, or posts logs" (`docs/adr/0016…:18`); failure reason on dashboard only | G2 GitLab comment = handoff record; #50 g4 `post-status` done comment = REPORT 8 + LEARNINGS | **contradicts** |
| handoff / status | PR body fixed sections incl. `## Testing` "state honestly what was and was not tested" and `## Reviews` (`git-pr/SKILL.md:50-55`); work-on final report lists worktree, branch, red/green runs, checks, review SHAs, PR URL (`work-on/SKILL.md:61`) | #50 g4 REPORT 8; Q18 `visual-pr` owned adaptation | **match** |
| handoff / status | `git-pr-address-comments`: act on thread *state*, not author; reply, never resolve (`git-pr-address-comments/SKILL.md:14-21`) | none decided | **new** (small) |
| lessons / retro | No retro skill. Instead each run records a **config fingerprint** (model, effort, prompt/system/tool/skill-file hashes) and runs sharing it form a **cohort** to compare (`docs/adr/0034…:18`); a subagent's kind = skills it loaded (`docs/adr/0037…:17`) | G7 (#26) retro worker + /lesson → MRs; #50 g5 mattpocock `retro` | **new idea** — measures whether a rule change helped; we only propose changes |
| distribution / plugins | Library + per-operator repo (flake input pinned, template scaffold, divergence guard) (`docs/adr/0003…:19-23`) | G4 (#17) plugins everywhere + one machine file; ND-15 `machine.env` | **match** in shape (shared logic upstream, thin per-machine repo) |
| distribution / plugins | Managed repo brings its own skills; forge loads them from the checkout, not from a marketplace (`docs/adr/0018…:22`) | G1 / G4 project rules in agent-platform, agent side as plugins | **match** for project side; forge has no plugin layer for agent side |

## Worth considering

1. **Head-SHA coverage with a named exemption per later commit**, written into the MR's Reviews section (`work-on/SKILL.md:47`, `git-pr/SKILL.md:61-65`). Why: closes the "fix landed after the last review" hole without forcing a full re-review for a docs-only commit. Feeds: #9 not-yet-specified "verdict tied to head SHA" → G3 (#16) REQ text and #50 g4 status comment.
2. **Config fingerprint + cohort per worker run, plus counting which skills each run loaded** (`docs/adr/0034…:18`, `docs/adr/0037…:17`). Why: the only way to tell whether a rulebook change made reviews cheaper/better (R4 baseline, P1 re-run AC) instead of guessing. Feeds: G7 (#26) / D1 (#21) event log.
3. **Fail closed at spawn when a named skill or rule file is missing or ambiguous** (`docs/adr/0018…:27`, `docs/adr/0023…:23`). Why: our skills move to `.agents/skills` + plugins; a silently missing skill on the VM is the laptop/fleet drift G4 exists to stop. Feeds: G4 (#17) work item 3, #50 g3 refuse-to-spawn.
4. **Claim/lifecycle label on the issue** (`forge:ready/running/done/failed`, `docs/adr/0016…:18`). Why: the coordinator's state survives a crash and the WIP limit becomes a label count. Complements, not replaces, the status comment. Feeds: G6 (#25) and the WIP-limit item on #9.
5. **Read required checks from branch protection; "no checks reported" never counts as green** (`work-on/SKILL.md:51`). Why: once the self-hosted runner and "Pipelines must succeed" land, a pipeline that never registered must not read as pass. Feeds: R28 (#60) / Q26 (#35).

## Not for us

- **Unattended, nobody relays** (`harness.ts:13-17`) — G6 chose interactive workers with the coordinator relaying every question.
- **Unbounded review loop** (`work-on/SKILL.md:45`) — G3 caps at 3 rounds; forge's own stop is only "same finding repeats".
- **Labels only, never comment** (`docs/adr/0016…:18`) — G2/#50 make the GitLab comment the handoff and retro input.
- **Developer spawns its own reviewers** (`work-on/SKILL.md:39`) — Q23 puts qa in its own fresh worker; a child of the author inherits its brief.
- **Copied upstream-style skills** (refine/to-spec/to-tickets/tdd) — G1: upstream = plugins, never copies.
- **Blanket "never write code comments"** (`AGENTS.md:5`) — our rule bans restating comments only; a blanket ban loses the why.
- **One recipe for every ticket** — Q24 lanes already decided.
- **Nix/NixOS/bubblewrap substrate** — stack mismatch; only the "load nothing run-writable" idea carries, to D1.
