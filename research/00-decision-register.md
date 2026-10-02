# Decision register — every decision, and the file it becomes

One line per decision: where it was decided, which repo and file it lands in, and which work item writes it.
No new decisions here. Consolidated 2026-10-02. Rule-level decisions (each approved rule) live in the ledger
`research/19-approved-rules.md`, whose rows already carry their target file; this register covers everything else.

Repos: **AP** agent-platform (GitLab) · **AAF** aruvii-agent-fleet (new) · **AF** agent-fleet (GitHub, generic) ·
**U** user level on the laptop (`~/.claude`) · **UP** upstream plugin. Work items: **W1** agent-platform (#643 → #646 →
#644 → #645), **W2** aruvii-agent-fleet, **W3** agent-fleet.

## Where rules live and how they load

| decision | from | lands in | by |
|---|---|---|---|
| 4 layers: AGENTS.md index · path rules (MUSTs) · domain skills · hooks/lint | G1 #14 | AP structure | W1 #643 |
| AGENTS.md is the real file, `CLAUDE.md` = `@AGENTS.md`; <200 lines with operator-approved MUSTs | G1 · #643 Q2 · #646 | AP `AGENTS.md`, `CLAUDE.md` | W1 #643, #646 |
| one skills tree `.agents/skills/`, `.claude/skills` → symlink; commands become skills | #643 Q1 (ND-1) | AP `.agents/skills/` | W1 #643 |
| workflows stay flat skills; knowledge goes in domain skills (router + references) | #643 hybrid | AP `.agents/skills/<domain>/` | W1 #643 |
| `meta/` is its own domain | ND-11 | AP `.agents/skills/meta/` | W1 #643 |
| reference shape: Rules · When X use Y · Good/Bad · Decided edges · Review checks | G5 #22 | every AP reference | W1 + `00-reference-format.md` |
| upstream skills as plugins, never copies; adapted ones owned and credited (D26) | G1 · Q-5 · #587 | AP `.claude/settings.json` enabledPlugins | done (#587) |
| doc-writing rules → `planning/references/writing-docs.md` | ND-8 | AP planning/ | W1 |
| module `aruvii-*/CLAUDE.md` → nested AGENTS.md | ND-13 | AP, own ticket | later |

## The pipeline (`crq`)

| decision | from | lands in | by |
|---|---|---|---|
| one crq text; stages tagged by project-owned role labels; roles say only who | G2 #15 | AP `.agents/skills/crq/SKILL.md`, `docs/CONTEXT.md` §Roles | W1 #645 |
| labels: coordinator · analyst · spec-reviewer · developer · qa · human; per-stage owner table | #35 Q23 | AP crq + CONTEXT §Roles | W1 #645 |
| three lanes (quick / standard / full) + floor; skipped stage = `skip: <reason>` | G8 #30 · #35 Q24 | AP crq stage 1 | W1 #645 |
| full stage text 0–10 (approved page `review/crq-stages.html`) | #35 | AP crq | W1 #645 |
| `/dod` deleted; stage 8 = runner pipeline + AC citing; dod items → references' Review checks | ND-5 | AP crq, references | W1 #645 |
| `visual-pr` adapted and owned; `untouched-and-risk` folded into it; stages 5 and 9 | #50 Q18 · ND-16 | AP `.agents/skills/visual-pr/` | W1 #645 |
| GitLab comment = handoff record; Discord only pings | G2 | AP crq · AAF briefs | W1, W2 |
| TDD as a rule — under review | #68 G12 | AP crq stage 6, AGENTS.md rule 1 | open |

## Review

| decision | from | lands in | by |
|---|---|---|---|
| ONE fresh read-only reviewer, two verdicts (Standards + Spec), references by changed path, inputs pushed in | G3 #16 (amended) | AP `.agents/skills/review/`, `.claude/agents/reviewer.md` | W1 #645 |
| lead judgment: Act on ≤5 · Consider · Noted · Dismissed; 3-round cap; rounds 2–3 see the fix diff only | G3 · pstack | AP review/references/lead-judgment.md | W1 #645 |
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
| workers commit and push their own branch; master protected; operator merges | #50 Q19 | AAF worker-rules.md | W2 |
| rebase onto origin/master at spawn, before verify, before done; conflicts via resolving-merge-conflicts + module build; behaviour change → needs-decision; --force-with-lease own branch | #50 Q20 | AAF worker-rules.md · AP crq | W1, W2 |

## Agent side

| decision | from | lands in | by |
|---|---|---|---|
| one always-on coordinator; fresh interactive worker per (work item, role), own tmux window + worktree | G6 #25 | AAF `agents/coordinator.md` · AF launch scripts | W2, W3 |
| coordinator hard rules (never edits code, never /approved or merge, never tears down unlanded work) | G6 · firstmate | AAF coordinator.md | W2 |
| relay layout = firstmate 5 parts + our reasons + recommendation; high-level → artifact (mermaid fallback) | #50 Q1–Q4 | AAF coordinator.md | W2 |
| high-level = design/REQ, >1 work item, irreversible, G8 floor, stage-5 /approved | #50 Q3 | AAF coordinator.md · AP crq | W2 |
| fleet PRINCIPLES.md = transferable subset of AP `docs/design/AGENT-PRINCIPLES.md` (#620) | #50 Q5 | AAF `PRINCIPLES.md` | W2 |
| coordinator speaks for needs-decision, blocked, done + one daily digest; watchdog for stalled items | #50 Q6 · builder.io | AAF coordinator.md | W2 |
| souls = 3 sentences + "you own" (approved text) | #50 Q7 | AAF `agents/{analyst,spec-reviewer,developer,qa}.md` | W2 |
| one shared worker block (guardrails, escalation, principles pointer) prepended at spawn | #50 Q8–Q9 | AAF `worker-rules.md` | W2 |
| model choice in agent frontmatter | #50 default | AAF agents/*.md | W2 |
| brief = pstack 9 + HUMAN'S WORDS; CONTEXT/ACCEPTANCE point at the issue; refuse if missing | #50 Q10 | AAF `briefs/worker-brief.md` | W2 |
| reversible question → default + report; high-level → stop + relay | #50 Q11 | AAF worker-rules.md | W2 |
| status words needs-decision · blocked · done + qa verdict on SHA; done = REPORT 8 + LEARNINGS + NEXT | #50 Q12–Q13 | AAF `briefs/handoff-comment.md` | W2 |
| `post-status` refuses done unless pushed and not draft | #50 Q14 | AAF `scripts/post-status` | W2 |
| refuse to spawn when a named skill is missing or two share a name | #64 idea 2 | AAF/AF spawn script | W2, W3 |
| one unix user; laptop = coordinator; tiers 0/1/2; agent side as plugins + one machine file | G4 #17 | AF provisioning | W3 |
| machine file `~/.config/agent-fleet/machine.env` (JAVA_HOME, DOCKER_HOST → podman socket, ports) | ND-15 · R29 | AF template | W3 |
| delete `~/.claude/knowledge/<repo>.md` | ND-14 | AF / U | W3 |
| reply card: shapes + ~80% ASD-STE100, one file | ND-10 | AF `plugins/reply-card/` | W3 |

## Lessons and measurement

| decision | from | lands in | by |
|---|---|---|---|
| agents propose MRs to the one owning file; operator merges; ≤2 per work item | G7 #26 | AP `docs/agents/lessons.md` (routing) | W1, W2 |
| retro = mattpocock `retro` plugin as-is; thread first; operator picks from a ranked list; crq stage 10 retro worker types `/retro` | #50 Q15–Q17 · ND-12 | AP crq stage 10 · AAF brief | W1, W2 |
| factory metrics per work item, shown in the digest | #66 G11 | open | — |

## Open (not yet decided — do not write)

TDD as a rule (#68) · factory metrics (#66) · G9b code+obs (#33) · G9c migrations+delivery+review packet (#34) ·
G10 writing standard (#37) · WIP limit (map fog) · pilot (#67) · D1 role boxes (#21).
