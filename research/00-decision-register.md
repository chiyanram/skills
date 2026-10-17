# Decision register — every decision, and the file it becomes

One line per decision: where it was decided, which repo and file it lands in, and which work item writes it.
No new decisions here. Consolidated 2026-10-02. Rule-level decisions (each approved rule) live in the ledger
`research/19-approved-rules.md`, whose rows already carry their target file; this register covers everything else.

Repos: **AP** agent-platform (GitLab) · **AF** agent-fleet (GitHub) — holds ALL agent-side files for now (G1 amendment 2026-10-03: no separate aruvii-agent-fleet until a second project needs it) ·
**SK** chiyanram/skills — generic skills, references and the crq workflow, published as a plugin marketplace (G23 #93, 2026-10-16) ·
**U** user level on the laptop (`~/.claude`) · **UP** upstream plugin.

**Location change (amended 2026-10-17, G23 #93).** Rows below that say "AP crq", "AP review" or "every AP reference"
now split in two: the generic text (crq stages, roles, lanes, review, references) lands in **SK**; agent-platform keeps
only the Aruvii answers — `AGENTS.md`, nested `<dir>/AGENTS.md`, `docs/agents/*.md` (incl. `docs/agents/crq.md`) and the
Aruvii-only skills. The build ticket in the "by" column is unchanged unless a row says so.
Build order (G24 #94): fleet first (AF), SK in parallel, AP project layer after. Tickets (2026-10-03): **W1** agent-platform #643 #646 #644 #645 + #659 #662 #670 #671 #652 · **W2/W3** chiyanram/agent-fleet (private) #72 roles/coordinator/briefs · #73 dev container · #74 zones/runner/machine.env · #75 retro wiring.

Work items: **W1** agent-platform (#643 → #646 →
#644 → #645), **W2** agent-fleet: roles, coordinator, briefs (was aruvii-agent-fleet), **W3** agent-fleet: provisioning, runner, machine file.

## Where rules live and how they load

| decision | from | lands in | by |
|---|---|---|---|
| 4 layers: AGENTS.md index · path rules (MUSTs) · domain skills · hooks/lint | G1 #14 | AP structure | W1 #643 |
| AGENTS.md is the real file, `CLAUDE.md` = `@AGENTS.md`; <200 lines with operator-approved MUSTs | G1 · #643 Q2 · #646 | AP `AGENTS.md`, `CLAUDE.md` | W1 #643, #646 |
| one skills tree `.agents/skills/`, `.claude/skills` → symlink; commands become skills | #643 Q1 (ND-1) | AP `.agents/skills/` | W1 #643 |
| workflows stay flat skills; knowledge goes in domain skills (router + references) | #643 hybrid | AP `.agents/skills/<domain>/` | W1 #643 |
| `meta/` is its own domain | ND-11 | AP `.agents/skills/meta/` | W1 #643 |
| reference shape: Rules · When X use Y · Good/Bad · Decided edges · Review checks | G5 #22 | every reference — generic ones in SK (amended 2026-10-16, G23 #93: "pinned from this repo" superseded) | W1 + `00-reference-format.md` |
| upstream skills as plugins, never copies; adapted ones owned and credited (D26) | G1 · Q-5 · #587 | AP `.claude/settings.json` enabledPlugins | done (#587) |
| doc-writing rules → `planning/references/writing-docs.md` | ND-8 | AP planning/ | W1 |
| layer 2 agent-agnostic: directory MUSTs → `<dir>/AGENTS.md` + `CLAUDE.md`=`@AGENTS.md`; file-type MUSTs → root AGENTS.md blocks; `.claude/rules/` deleted; module CLAUDE.md → AGENTS.md (ND-13) | G1b #72 | AP nested AGENTS.md, root AGENTS.md | W1 #646 |

## The pipeline (`crq`)

| decision | from | lands in | by |
|---|---|---|---|
| one crq text; stages tagged by project-owned role labels; roles say only who | G2 #15 | AP `.agents/skills/crq/SKILL.md`, `docs/CONTEXT.md` §Roles | W1 #645 |
| labels: coordinator · analyst · spec-reviewer · developer · qa · human; per-stage owner table | #35 Q23 | AP crq + CONTEXT §Roles | W1 #645 |
| three lanes (quick / standard / full) + floor; skipped stage = `skip: <reason>` | G8 #30 · #35 Q24 | AP crq stage 1 | W1 #645 |
| full stage text 0–10 (approved page `review/crq-stages.html`) | #35 | AP crq | W1 #645 |
| `/dod` deleted; stage 8 = runner pipeline + AC citing; dod items → references' Review checks | ND-5 | AP crq, references | W1 #645 |
| `visual-pr` adapted and owned; `untouched-and-risk` folded into it; stages 5 and 9 | #50 Q18 · ND-16 | AP `.agents/skills/visual-pr/` | W1 #645 |
| the forge thread (issue or change-request comment) = handoff record; Discord only pings (amended 2026-10-16, G19 #89: forge-neutral) | G2 · G19 #89 | crq stage text (SK per G23) · AF briefs | W1, W2 |
| TDD only for bugs (failing test first, S4); features: any order; PIT on touched classes with decisions at 6a, every survivor dispositioned, qa checks | #68 G12 | AP crq stage 6, AGENTS.md rule 1, testing/SKILL.md | W1 #644/#645 |
| mutation runner job for touched modules, report-only → measured baselines → operator thresholds → blocking; every module wired | #68 Q3–Q4 | AP build-logic, Makefile, runner pipeline | AP #659 |

## Review

| decision | from | lands in | by |
|---|---|---|---|
| ONE fresh read-only reviewer, two verdicts (Standards + Spec), references by changed path, inputs pushed in | G3 #16 (amended) | AP `.agents/skills/review/`, `.claude/agents/reviewer.md` | W1 #645 |
| lead judgment: Act on · Consider · Noted · Dismissed, the lead validates every finding; 3-round cap; rounds 2–3 see the fix diff only. No cap on Act on (amended 2026-10-16, G17 #87) | G3 · pstack · G17 #87 | review/references/lead-judgment.md (SK per G23) | W1 #645 |
| a review counts only if it covered the head commit | #64 forge idea 1 | AP review packet | #34 → W1 |
| delete standards-review, code-standards-reviewer, smoke-spec-reviewer, spec-design-reviewer, architecture-reviewer agents | G3 · R12 | AP | W1 #645 |
| architecture-review A–E merges into spec-review; F-01 → Spec verdict | SR8 (ND-7) | AP planning/references/spec-review.md | W1 |
| P1 re-run on !230 with the one reviewer (acceptance) | A-1 | AP MR evidence | W1 #645 |

## Verification and the gate

| decision | from | lands in | by |
|---|---|---|---|
| self-hosted GitLab runner on the VM, shell executor, concurrent=1, job = the Verifier; instance runners off → register → "Pipelines must succeed" | #35 Q26 · R28 #60 | AP `.gitlab-ci.yml` + project settings · AF runner provisioning | W1, W3 |
| "no checks reported" is never green; required checks from branch protection | #64 idea 3 | AP crq stage 8 · runner | W1 |
| gate smoke: scripted model only for specs #609 converted, Ollama for the rest, 2 workers; no nightly tier | #62 Q27 (revised after R30) | AP playwright config, crq stage 8 | W1 (needs AP #609) |
| developer minimum before qa: touched-module test-module/it-module + verify-fast + what-ran note; only the runner runs verify-full/smoke | #35 Q26 · R28 | AP crq stages 6–6a | W1 #645 |
| runner owns its own Compose stack; agents never deploy to it | #62 note (builder.io) | AF runner · AP Makefile | W3 |
| workers commit and push their own branch; master protected; operator merges | #50 Q19 | AF worker-rules.md | W2 |
| before stage 7 starts: a worker may rebase onto origin/master (--force-with-lease, own branch only). Once stage 7 has started: merge origin/master into the branch, never force-push. Conflicts via resolving-merge-conflicts + module build; behaviour change → needs-decision. Squash-on-merge keeps master linear (amended 2026-10-16, #50 amendment; replaces "rebase before verify, before done") | #50 Q20 · #50 amendment (forge ADR-0069) | AF worker-rules.md · crq stage text (SK per G23) | W1, W2 · AF #72 |

## Agent side

| decision | from | lands in | by |
|---|---|---|---|
| one always-on coordinator; fresh interactive worker per (work item, role), own tmux window + worktree | G6 #25 | AF `agents/coordinator.md` · AF launch scripts | W2, W3 |
| coordinator hard rules (never edits code, never /approved or merge, never tears down unlanded work) | G6 · firstmate | AF coordinator.md | W2 |
| relay layout = firstmate 5 parts + our reasons + recommendation; high-level → artifact (mermaid fallback) | #50 Q1–Q4 | AF coordinator.md | W2 |
| high-level = design/REQ, >1 work item, irreversible, G8 floor, stage-5 /approved | #50 Q3 | AF coordinator.md · AP crq | W2 |
| fleet PRINCIPLES.md = transferable subset of AP `docs/design/AGENT-PRINCIPLES.md` (#620) | #50 Q5 | AF `PRINCIPLES.md` | W2 |
| coordinator speaks for needs-decision, blocked, done + one daily digest; watchdog for stalled items | #50 Q6 · builder.io | AF coordinator.md | W2 |
| souls = 3 sentences + "you own" (approved text) | #50 Q7 | AF `agents/{analyst,spec-reviewer,developer,qa}.md` | W2 |
| one shared worker block (guardrails, escalation, principles pointer) prepended at spawn | #50 Q8–Q9 | AF `worker-rules.md` | W2 |
| model choice in agent frontmatter | #50 default | AF agents/*.md | W2 |
| brief = pstack 9 + HUMAN'S WORDS; CONTEXT/ACCEPTANCE point at the issue; refuse if missing | #50 Q10 | AF `briefs/worker-brief.md` | W2 |
| reversible question → default + report; high-level → stop + relay | #50 Q11 | AF worker-rules.md | W2 |
| status words needs-decision · blocked · done + qa verdict on SHA; done = REPORT 8 + LEARNINGS + NEXT | #50 Q12–Q13 | AF `briefs/handoff-comment.md` | W2 |
| `post-status` refuses done unless pushed and not draft | #50 Q14 | AF `scripts/post-status` | W2 |
| refuse to spawn when a named skill is missing or two share a name | #64 idea 2 | AF spawn script | W2, W3 |
| laptop = coordinator; tiers 0/1/2; agent side as plugins + one machine file (one-unix-user part amended by #69) | G4 #17 | AF provisioning | W3 |
| machine file `~/.config/agent-fleet/machine.env` (JAVA_HOME, DOCKER_HOST → podman socket, ports) | ND-15 · R29 | AF template | W3 |
| delete `~/.claude/knowledge/<repo>.md` | ND-14 | AF / U | W3 |
| reply card: shapes + ~80% ASD-STE100, one file | ND-10 | AF `plugins/reply-card/` | W3 |

## Lessons and measurement

| decision | from | lands in | by |
|---|---|---|---|
| agents propose change requests to the one owning file; operator merges; ≤2 per work item; destinations tried strongest first (amended 2026-10-16, G18 #88 — row below) | G7 #26 · G18 #88 | AP `docs/agents/lessons.md` (routing) | W1, W2 |
| retro = mattpocock `retro` plugin as-is; thread first; operator picks from a ranked list; crq stage 10 retro worker types `/retro` | #50 Q15–Q17 · ND-12 | AP crq stage 10 · AF brief | W1, W2 |
| cost budget: tokens + wall time per stage; report-only → p90×1.5 per lane+stage set by operator; watchdog warns at 80 %, stops at 100 % (blocked: budget); spawn pause at ~70 % of the shared window | #70 G14 | AF coordinator watchdog | AF #72 |
| five metrics per work item in the closing comment, fingerprinted by rulebook + fleet SHA; digest compares per fingerprint, ≥5 per side | #66 G11 | AF retro worker + digest | AF #75, #72 |

## API errors

| decision | from | lands in | by |
|---|---|---|---|
| typed outcomes up to the controller; failures implement `Failure` with an ErrorCode; one mapper + global handler for the unexpected; ArchUnit bans other paths | #58 Q4, Q2, Q7 | AP shared outcome/, web layer, ArchUnit | AP #662 |
| ProblemDetail { type https://aruvii.ai/errors/<kebab>, title, status, detail, instance, code UPPER_SNAKE, traceId } | #58 Q5, Q-TYPE, Q-WIRE | AP global handler, UI | AP #662 |
| status by kind (400/401/403/404/409/422/429/500/502/503/504); 104-code catalogue | #58 Q6, catalogue | AP ErrorCode enum | AP #662 |
| api/errors rules for the reference | #58 | AP code/references/api.md, errors.md | W1 (G9b #33) |

## Fleet security (G13 #69)

| decision | from | lands in | by |
|---|---|---|---|
| two zones: workers share `fleet-worker`; coordinator `fleet-coord`, runner `fleet-runner` own users (amends G4) | #69 Q1 | AF provisioning | W3 |
| workers run in one dev container image on laptop and VM (non-root, toolchain baked, managed settings, no host secrets, egress firewall) | #69 Q2 | AF `.devcontainer/` + launch scripts | W2, W3 |
| per-role GitLab bots (aruvii-*-agent, Developer); token by role at spawn; never the operator's token | #69 Q3 | AF spawn | W2 |
| tokens as read-only container secrets per worker; machine.env facts only | #69 Q4 | AF | W3 |
| no Discord token in workers; /approved by note author; auto mode, bypass disabled | #69 floor | AF worker-rules, managed settings, coordinator | W2, W3 |
| master key not linked into worktrees | #69 floor | AP scripts | AP #670 |
| egress allow-list; plugin allow-list; audit = GitLab + 30-day transcripts; no laptop forwarding/mounts | #69 Q5–Q8 | AF managed settings, firewall, runbook | W3 |
| workers read chiyanram/skills via one read-only fine-grained GitHub token (contents: read); github.com in the egress allow-list | #69 amendment | AF #73, #74 | W2, W3 |

## Writing standard (G10 #37)

| decision | from | lands in | by |
|---|---|---|---|
| 16-point writing checklist. Line 6 as amended: Good/Bad pairs are generic, in one neutral domain (same mistake, same fix); the Aruvii `path:line` that shows the mistake is ledger evidence, not reference text (amended 2026-10-17, G23 #93 Q3). History: "adapted examples allowed when labelled" (#37 Q1) was corrected 2026-10-03 on #37 to "Bad = our real path:line, Good = that Bad rewritten" — both superseded | #37 Q1 · #37 correction · G23 #93 Q3 | research/00-reference-format.md → every SK reference | W1 #644, #646, later G9 domains · skills #99 (rewrite pairs) |
| Rule line = one sentence: imperative + "because" + the failure it prevents, ≤35 words; a rule with no statable reason is flagged for deletion. Supersedes "imperative ≤30 words" | G21 #91 | research/00-reference-format.md §five sections · ledger research/19 reason column | skills #98 |
| proof before replace: full replay for testing refs, static + 1 MR × 3 for others | #37 Q2 | AP MR evidence | W1 #644, #645 |
| descriptions = "Use when <observable trigger>" + what it holds, trigger-tested | #37 Q3 | AP .agents/skills/*/SKILL.md | W1 #643 onward |
| `make lint` = plugin validate --strict + doc-drift §5 + 5-section heading check | #37 Q4 | AP Makefile, scripts | W1 #643 |

## R38 follow-ups (decided 2026-10-16/17)

| decision | from | lands in | by |
|---|---|---|---|
| keep each reference's **reason**, not its rule; method: reference change → why → true for us? → our principle → our decision; principles CP1–CP12 | R38 #86 | SK `research/64-core-design.md` (cited by every later decision) | — (this map) |
| lesson destinations, strongest first: check → reference (rule + reason) → soul → machine file → dropped (one line in a rejected record, with the reason); the retro states why each stronger level could not hold the lesson | G18 #88 | AF retro brief · AP `docs/agents/lessons.md` | AF #75 |
| the forge thread is the record: each stage handoff = a comment with the decision, what ran, head SHA, open questions; worker scratch stays uncommitted on its host; a long spec/design is committed in the change request; no thoughts/ folder | G19 #89 | crq stage text (SK) · AF `scripts/post-status` | AP #645 · AF #72 |
| forge-neutral wording in rules, skills and souls (forge · issue · change request · thread); glab today / gh later live in one adapter | G19 #89 | AP `docs/agents/issue-tracker.md` (adapter) | AP #645 |
| manual /crq plays every role and posts the same stage comments as the fleet | G19 #89 | crq stage text (SK) | AP #645 |
| static delivery check in every `make lint`: root AGENTS.md <200 lines · root→leaf chain under Codex's 32 KiB cap · every CLAUDE.md shim is exactly `@AGENTS.md` · `.claude/skills` symlink resolves | G20 #90 | AP check-doc-drift §5 | AP #643, #646 |
| delivery probe when any AGENTS.md or skill changes: a sentinel line per nested AGENTS.md; headless `claude -p` and `codex exec` must quote it; red if not loaded; failures fixed in #646 | G20 #90 | AP runner job | AP #671 |
| a rule that can be a check becomes a check; prose is the fallback | G22 #92 | the concrete list | AP #696 |
| three layers: generic skills, references (neutral-domain examples) and the crq workflow in SK as a plugin · AP = Aruvii only (AGENTS.md, nested AGENTS.md, `docs/agents/*.md` answers incl. `crq.md`, Aruvii-only skills) · AF = fleet, generic part extracted later | G23 #93 | SK plugin marketplace · AP `docs/agents/crq.md` | skills #99 · AP #645 (split the Aruvii answers out of crq) · #81 |
| build order: fleet first, SK in parallel, AP project layer after; workers run on today's AP files until then | G24 #94 | map #9 destination | — |
| improve chiyanram/agent-fleet beside the old scripts; install fresh into the zone users on VM and laptop; pilot #67 on it; retire old agents after the pilot passes; one update command per host (git pull + plugin update + container rebuild) | G25 #95 | AF provisioning, install + update scripts | AF #74 |
| the forge assignee is the claim on a work item, so two fleets never take the same issue | G25 #95 | AF coordinator | AF #72 |
| caps by resource: ≤2 workers building per host · analysts and reviewers uncapped · runner 1 gate at a time · ≤3 items waiting on the operator; over a cap = queued, not failed; tune from the G11 row | G26 #101 | AF `agents/coordinator.md` · runner | AF #72, #74 |
| builders get a fresh worktree from the pushed branch, set up by `make worktree-setup` before the worker starts; deleted once done is accepted; a dirty tree is never deleted (flagged); reviewers get no worktree | G27 #102 | AF coordinator + launcher · AP Makefile `worktree-setup` | AF #72 · AP target: owner not named on #102 |
| crash or hang → one fresh worker from the forge thread + pushed branch (never resume); dead worktree kept and named; second failure → blocked to the operator | G27 #102 | AF coordinator | AF #72 |
| prevent stuck boxes: auto mode in the container, ask-the-user tool off for workers (they post needs-decision); detect: coordinator checks each worker screen every few minutes, a waiting box → "stuck on: <question>" | G27 #102 | AF managed settings · coordinator | AF #73, #72 |
| keep ours minimal (no AI design critic, one writer, one reviewer); add a piece only when a recorded switch trigger fires | G28 #103 | `review/pipeline-comparison.html` | — |

## Open (not yet decided — do not write)

G9b code+obs (#33) · G9c migrations+delivery+review packet (#34) ·
pilot (#67) · D1 role boxes (#21) · G16 thread per ticket (#82). (WIP limit decided 2026-10-17, G26 #101.)
