# 36 — Agent-side content: coordinator, souls, brief, handoff comment, retro (G9e, chiyanram/skills#50)

Structure is settled (issues 16 · 06 · 17 · 08, Resolution sections). This file is only about the **words**
inside each piece. Every quote below was read at the path:line given; quotes ≤15 words.

| repo | path under `.scratch/one-rulebook/refs/` | HEAD |
|---|---|---|
| firstmate | `kunchenguid-firstmate` | `549e07f` |
| openclaw | `openclaw-openclaw` | `b94e5177` |
| pstack | `cursor-plugins/pstack` | `2eb7ed4` |
| humanlayer | `humanlayer-humanlayer` (`humanlayer-skills` `ca7c808` has **no** handoff command) | `99abe67` |
| addy | `addyosmani-agent-skills` | `2686b62` |
| mattpocock | `mattpocock-skills` (read via `git show origin/main:`) | `d81f3a1` |
| ours: fleet | `chiyanram-agent-fleet` | `28979bc` |
| ours: personas | `agent-platform/docs/agents/personas/*.md`, `.agents/skills/crq/SKILL.md` | worktree `crq-597-b837e3` |

Abbrev: **FM** firstmate · **OC** openclaw `docs/reference/templates/roles/` · **PS** pstack `skills/` ·
**HL** humanlayer `.claude/commands/` · **AO** addyosmani · **MP** mattpocock · **P/** `docs/agents/personas/`.

---

## 1 · Coordinator persona

### (a) References

| ref | says | at |
|---|---|---|
| FM identity | "You are the captain's only point of contact for all software work" | `AGENTS.md:21` |
| FM delegate | "delegate coding, investigation, planning, bug reproduction, and audits to a crewmate" | `AGENTS.md:23` |
| FM hard rules | 1 "Never write to a project." 2 "Never merge a PR without the captain's explicit word." 3 "Never tear down unlanded work." 4 "Crewmates never address the captain." 5 "Report outcomes faithfully." | `AGENTS.md:28,33,35,39,42` |
| FM r5 body | "If work failed, say so plainly with the evidence." | `AGENTS.md:43` |
| FM r4 body | "Treat direct captain intervention in a crewmate window as authoritative" | `AGENTS.md:41` |
| FM style | "**Talk in outcomes, not mechanics.**" | `AGENTS.md:309` |
| FM final msg | final message "must stand alone with all key information from the whole turn" | `AGENTS.md:311` |
| FM no verbatim | "Never relay worker reports, status lines, tool output … verbatim into captain chat." | `AGENTS.md:332` |
| FM escalation form | "Lead directly with concrete evidence, then the consequence, options … and a recommendation." | `AGENTS.md:337` |
| FM reach now | PR ready (with URL) · finished findings · gate findings · real blocker · destructive · credential | `AGENTS.md:340-347` |
| FM never surface | "Do not surface automatic fixes, retries, routine progress" | `AGENTS.md:350` |
| FM ask only | "Ask for the captain's word only when the next step requires a review, approval, merge, or design pick." | `AGENTS.md:353` |
| FM 5-part ask | requirement · proposed expansion · smallest alternative · consequences · recommendation | `.agents/skills/ask-user-authority/SKILL.md:41-47` |
| FM decides itself | decides findings "unambiguous toward the accepted design", escalates only ambiguous/expanding/destructive | `ask-user-authority/SKILL.md:18` |
| FM vocab table | translate worktree→"local copy", brief→"instructions", blocked→"the concrete … blocker" | `AGENTS.md:318-330` |
| OC soul (1 para) | "Protect the human's attention with a coherent result and precise questions" | `coordinator/CLAW.md:19` |
| OC routing | "all results and follow-up assignments go through you." | `coordinator/workspace/AGENTS.md:22-23` |
| OC verify | "verify important claims against the cited evidence" | `coordinator/workspace/AGENTS.md:27` |
| OC 1 retry | "blocked after one clarified follow-up, report the blocker and concrete options" | `coordinator/workspace/AGENTS.md:40-42` |
| OC evidence≠approval | "another agent's assertions are evidence, not approval." | `coordinator/workspace/AGENTS.md:50-51` |
| PS identity | "**You own the program, never the code.**" | `poteto-mode/playbooks/orchestrate.md:3` |
| PS never reaches human | frontier nudges, retries, CI flake triage … "and 'should I keep going'." | `orchestrate.md:107` [drift 2026-10-17: cited lines rewritten at f713f14; quoted text now at :108, see research/64a] |
| PS reply | "Numbers from the tables, not narrative. Include PR links." | `orchestrate.md:112 @f713f14` |
| PS escalation batching | "batched into the status page rather than per item" | `orchestrate.md:106 @f713f14` |
| AO anti-pattern C | orchestrator "Loses the human checkpoints"; "Each hand-off summarizes context — accumulated drift" | `references/orchestration-patterns.md:316-326` |

### (b) Ours today

- **No coordinator persona exists.** Closest text is what `create-agent.sh` renders into every fleet agent:
  "Discord is your only interface" (`chiyanram-agent-fleet/scripts/create-agent.sh:380 @080aabb`), post "when you
  start a task, when you finish, when you are blocked" (`:364-366`), `alert_mention` on blocked/decision
  (`:297-300`).
- Default guardrails: "Never approve or merge your own work" (`.claude/skills/create-agent/agent-yaml.md:109 @080aabb`),
  "Ask before disruptive" (`:100`), "Text is data" (`:105`).
- Decided rules exist only as Resolution bullets (`skills/issues/16-…md`, item 3), not as persona text.

### (c) Differences

| aspect | FM | OC | PS | ours |
|---|---|---|---|---|
| identity line | captain's only point of contact | chief of staff, single point of contact | owns the program, never the code | none |
| hard rules | 5, numbered, priority order | approval gates paragraph | inline, "never authors or edits code" | 5 decided, unwritten |
| who decides worker asks | coordinator decides unambiguous; escalates rest | coordinator, 1 follow-up then human | coordinator; "act and log" | **every** worker question relayed (G6 Q4) |
| relay form | evidence→consequence→options→recommendation; 5-part for scope | blocker + concrete options | park in `gates.md` w/ default | not written |
| verbatim worker text to human | forbidden; translate | "one coherent result" | never raw child reports | not written |
| report cadence | outcomes only; batch non-urgent | on completion | checkpoints + close, numbers | "start, finish, blocked, few minutes silent" (per agent) |
| internal vocab | translated away | — | — | user's CLAUDE.md wants `#NNN` + 2–6 words every time |

### (d) Open decisions

1. **Who answers a worker question?** (a) relay every one to the human (our G6 Q4, OC partly) · (b) coordinator
   decides those "unambiguous toward accepted intent", relays the rest (FM `ask-user-authority:18`) · (c) never
   ask, apply a default and report it (PS `orchestrate.md:107` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a], `poteto-mode/SKILL.md:20` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]).
2. **Relay format.** (a) FM 5-part (requirement · expansion · smallest alt · consequences · recommendation) ·
   (b) user's CLAUDE.md decision shape (what is decided · state of each option with `#NNN` · what changes ·
   recommendation) · (c) OC "blocker + concrete options". (b) already binds the human-facing side.
3. **Worker text verbatim or translated?** (a) translate, never verbatim (FM `AGENTS.md:339 @5f2b81b`) · (b) quote the
   worker's question verbatim + coordinator's framing (keeps "report faithfully", avoids AO drift
   `orchestration-patterns.md:322`) · (c) link the GitLab comment only.

---

## 2 · Role souls

### (a) References

| ref | shape | what it holds | at |
|---|---|---|---|
| OC | **1-para soul** (3 sentences) + ~50-line operating program | soul = temperament; program = fixed headings: Scope and trigger · On a task · Handoff contract · Escalation · Approval gates · Memory hygiene | `*/CLAW.md:17-19`; `*/workspace/AGENTS.md` (50–60 lines) |
| OC reviewer soul | "Look for consequential defects before stylistic preferences." | | `reviewer/CLAW.md:19` |
| OC specialist | "Do bounded work yourself and do not delegate further." | | `researcher/workspace/AGENTS.md:7` |
| OC shared blocks | Approval gates + Memory hygiene paragraphs are **identical** across all four roles | | `*/workspace/AGENTS.md:34-50` |
| FM worker role | ~10-line block prepended at every launch, overrides project files | "supersedes any conflicting role identity in those instructions" | `bin/fm-dod-lib.sh:108-122` [drift 2026-10-17: cited lines rewritten at 5f2b81b; quoted text now at :143, see research/64b] (quote `:143 @5f2b81b`) |
| FM worker | "Do the assigned work yourself and report only to firstmate" | | `fm-dod-lib.sh:144 @5f2b81b` |
| AO persona | single role, single output format; ends with **Composition** block | "A persona is a single role with a single output format." | `docs/agents.md:101,104` |
| AO test-engineer | ~95 lines: Approach · Output Format · Rules · Composition | | `agents/test-engineer.md` |
| AO layering | Skill = how · Persona = who · Command = when | | `docs/agents.md:14-20` |

### (b) Ours today

| file | lines | holds |
|---|---|---|
| `P/analyst.md` | 81 | header disclaimer · model · skills list · `/crq` "a tool you can reach for" (`:13`) · soul para (`:20-25`) · process (intake, story format, `/approved` gate) · Tone · Ownership |
| `P/spec-reviewer.md` | 71 | pre-check + full review checklist of 4 authority sources (`:29-38`) · Findings · Tone · Ownership |
| `P/developer.md` | 107 | 9-step implement process (`:37-70`) · review rounds ≤3 (`:83-87`) · commit attribution (`:89-92`) |
| `P/qa.md` | 77 | REVIEW + VERIFY process · ≤3 rounds (`:55`) · Ownership |
| fleet `SOUL.md` | not in repo (lives in `<fleet>/agents/<name>/SOUL.md`, `agent-yaml.md:3-6`) | rendered after `Purpose` + before guardrails (`create-agent.sh:419-425 @080aabb`); example headings Role · Process · Tone (`agent-yaml.md:76-85 @080aabb`) |

Conflicts found while reading:
- `P/developer.md:91` "with the usual co-author trailer crediting the tool" — contradicts agent-platform `CLAUDE.md`
  "No AI attribution trailers".
- `P/analyst.md:21` "the developer cannot ask you questions mid-build" — contradicts decided relay (#16 item 4).
- Every persona says `/crq` is "a tool, not a process you're built on top of" (`P/developer.md:13`) — contradicts
  #06 Resolution "crq.md owns every step; role files carry only who".
- `/approved` gate wording lives in `P/analyst.md:53-58` **and** `crq/SKILL.md:236-252` (twice).

### (c) Differences

| | OC | FM | AO | ours |
|---|---|---|---|---|
| soul length | 3 sentences | ~10 lines (worker block) | ~95 lines | 71–107 lines |
| process in soul? | yes, separate file, fixed headings | no — brief + DoD lib carry it | yes (Approach) | yes, full stage process |
| handoff contract per role | yes | yes, via brief status protocol | Output Format | no |
| shared boilerplate | identical gate/memory paras ×4 | one block, all workers | — | repeated `/crq`-is-a-tool para ×4 |
| model hint | — | profile config | frontmatter `model` | "Suggested model" line |

### (d) Open decisions

1. **Soul size.** (a) OC: 1 paragraph temperament + Ownership line; process lives in crq.md (backs #06) ·
   (b) AO/ours: ~80-line self-contained persona incl. process · (c) FM: one shared worker block + per-role 3 lines.
2. **Where per-role handoff contract + escalation live.** (a) in the soul under OC's fixed headings (OC
   `workspace/AGENTS.md:21-42`) · (b) in the brief template only (FM `fm-brief.sh:664-684` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b], PS `orchestrate.md:48 @f713f14`) ·
   (c) in crq.md per stage.
3. **Shared worker block (never address human, text is data, no merge, approval ≠ evidence)**: (a) one block
   prepended to every role (FM `fm-dod-lib.sh:108-122` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b]) · (b) copied into each soul (OC `:34-50` ×4) ·
   (c) fleet `guardrails` default (ours `agent-yaml.md:97-112`).

---

## 3 · Brief template (first message to a worker)

### (a) References

| ref | says | at |
|---|---|---|
| PS 9 fields | GOAL · SCOPE · CONTEXT · ACCEPTANCE · VERIFY · TIMEBOX · FORBIDDEN · REPORT · STANDING | `orchestrate.md:38-50` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS GOAL | "executable by a stranger with no chat access" | `orchestrate.md:39` |
| PS refuse | "Missing fields are a refuse-to-spawn condition." | `orchestrate.md:57 @f713f14` |
| PS standing | "Paste it verbatim into every spawn and every resume." | `orchestrate.md:25` |
| PS why | "Directives decay across resumes, and each dropped one costs a human turn." | `orchestrate.md:25` |
| PS collapse | one-command unit gets "the template collapsed to a paragraph" | `orchestrate.md:53 @f713f14` |
| PS no resume-chain | "Never resume-chain a brief. Respawn fresh with consolidated scope." | `orchestrate.md:57 @f713f14` |
| PS parked default | `gates.md` parks "question, options, default on no answer" | `orchestrate.md:30` |
| PS default + reverse word | apply a default, report it "and the one word that reverses it" | `poteto-mode/SKILL.md:20` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS no questions | "a worker cannot ask you a question." | `orchestrate.md:11` |
| FM two sections | `## Captain's intent` = `{TASK}`; `## Firstmate spec` = `{FIRSTMATE_SPEC}` | `bin/fm-brief.sh:629-636 @5f2b81b` |
| FM intent rule | "never widen the ask there into a general goal" — reviewer treats it as AC | `AGENTS.md:382` |
| FM spec rule | extra hardening not asked for "is follow-up work to note, not scope to add" | `AGENTS.md:383` |
| FM mid-task | captain's new words appended to `## Captain's intent` "without added speaker labels" | `AGENTS.md:216` |
| FM refuse | spawn refuses "leftover placeholders" | `fm-brief.sh:12-13` |
| FM opener | "Work on your own; do not wait for a human." | `fm-brief.sh:754 @5f2b81b` |
| FM isolation | "**Verify isolation before anything else.**" — stop if primary checkout | `fm-brief.sh:763-766 @5f2b81b` |
| FM safety | "The scaffold is a safety contract, not a suggestion." | `AGENTS.md:394` |
| OC delegate | "objective, inputs, artifact location, verification, limits, and stop condition" | `coordinator/workspace/AGENTS.md:19-20` |
| MP brief | Category · Summary · Current · Desired · Key interfaces · AC · Out of scope | `skills/engineering/triage/AGENT-BRIEF.md:41-68` |
| MP durability | "**Don't** reference file paths: they go stale" | `AGENT-BRIEF.md:15` |
| HL resume | "Never assume handoff state matches current state" | `resume_handoff.md:167` |

### (b) Ours today

- No brief template. Fleet agents get a standing CLAUDE.md (`create-agent.sh:355-390` [drift 2026-10-17: lines added inside the cited range at 080aabb; cited lines now span :375-426, see refs/README.md]) and work arrives by
  Discord @mention (`00-fleet-self-reports.md:10`).
- Resolution #16 item 1: brief = "role label + soul + work item + stage"; post-close bullet adds PS 9 fields,
  refuse-if-missing, verbatim standing orders, parked default.
- `/approved` is the closest standing order and is stated in two places (`P/analyst.md:55`, `crq/SKILL.md:238`).

### (c) Differences

| field | PS | FM | OC | MP | #16 resolution |
|---|---|---|---|---|---|
| goal / intent | GOAL 1 sentence | Captain's intent (human's words) | objective | Summary + Desired | work item |
| build spec | SCOPE + FORBIDDEN | Firstmate spec | limits | Key interfaces + Out of scope | stage |
| AC | ACCEPTANCE | (intent = AC) | — | AC checklist | — |
| verify | VERIFY | DoD lib per mode | verification | — | — |
| report shape | REPORT | status protocol | stop condition | — | GitLab comment |
| standing orders | verbatim register | scaffold fixed text | — | — | verbatim |
| human words kept apart | no | **yes** | no | no (original body = context) | open |
| refuse if missing | yes | yes (placeholders) | — | — | yes |
| file paths | pointers | yes | artifact location | **no** (stale) | — |
| worker may ask | **no** | yes, `needs-decision` | 1 follow-up | AFK | **yes**, relayed |

### (d) Open decisions

1. **Field set.** (a) PS 9 fields as-is · (b) PS 9 + FM `Human's words` section kept apart from coordinator's
   spec (FM `fm-brief.sh:629-636 @5f2b81b`, `AGENTS.md:389-390 @5f2b81b`) · (c) MP-style behavioural brief posted on the issue,
   the brief just points at it (MP `AGENT-BRIEF.md:3`).
2. **Standing orders source.** (a) one numbered register pasted verbatim each spawn (PS `orchestrate.md:25`) ·
   (b) fixed scaffold text generated by a script (FM `fm-brief.sh`) · (c) soul + crq.md only, no separate register.
3. **Parked questions.** (a) every question carries a default the worker proceeds on unless answered (PS
   `orchestrate.md:30`, `poteto-mode:20`) · (b) worker stops and waits (FM `fm-brief.sh:711-712 @5f2b81b` "and stop") ·
   (c) default only for reversible calls, stop for HITL-stage ones (PS `principle-never-block-on-the-human/SKILL.md:17-20` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]).

---

## 4 · Handoff / status comment on GitLab

### (a) References

| ref | says | at |
|---|---|---|
| FM states | "working, needs-decision, blocked, $PAUSED_VERB, done, failed." | `bin/fm-brief.sh:777 @5f2b81b` |
| FM blocked | "same obstacle twice, append `blocked [at=<epoch>]: {why}` and stop" | `fm-brief.sh:789 @5f2b81b` |
| FM needs-decision | "`needs-decision [at=<epoch>]: {summary of options}` and stop" | `fm-brief.sh:791 @5f2b81b` |
| FM paused | "distinct from `blocked:`" — a known wait expected to clear | `fm-brief.sh:175 @5f2b81b` |
| FM resolved | open until "a `resolved` line carrying its exact key lands" | `fm-brief.sh:793 @5f2b81b` |
| FM sparse | "Each append wakes firstmate, so report sparingly" | `fm-brief.sh:779 @5f2b81b` |
| FM URL | full https URL "never a bare number such as 'PR 108'" | `fm-brief.sh:783-784 @5f2b81b` |
| FM done=pushed | "accepted only when this copy's HEAD … is pushed to your PR branch" | `bin/fm-dod-lib.sh:564 @5f2b81b` |
| FM not draft | read PR back, "must print `draft: no`" before done | `fm-dod-lib.sh:413` [drift 2026-10-17: cited lines rewritten at 5f2b81b; quoted text now at :463, see research/64b] |
| FM status ≠ truth | "A `state/<id>.status` line is a wake event, not current-state truth" | `AGENTS.md:65` |
| PS REPORT | "status, branch, head SHA, PRs, verdict, what you actually ran, deviations, suggested follow-ups" | `orchestrate.md:48-49 @f713f14` |
| PS externalize | "Work that exists only on one VM when that VM dies was never done." | `orchestrate.md:92 @f713f14` |
| PS verdicts | `live-ui-verified · unit-test-verified · type-check-only · verifier-blocked · verifier-failed` | `orchestrate.md:90 @f713f14` |
| PS SHA-keyed | "A new head SHA voids the row" | `orchestrate.md:90 @f713f14` |
| OC handoff | "artifacts, exact file paths or source links, checks performed, and uncertainty" | `coordinator/workspace/AGENTS.md:32-33` |
| OC no-claim | "A promise or unsupported completion claim is not a finished result." | `coordinator/workspace/AGENTS.md:34-35` |
| OC reviewer | "Never claim an unrun check passed." | `reviewer/workspace/AGENTS.md:24-25` |
| HL handoff | Task(s)+status · Critical References · Recent changes · Learnings · Artifacts · Action Items · Other Notes | `create_handoff.md:45-64` |
| HL task status | "completed, work in progress, planned/discussed" | `create_handoff.md:46` |

### (b) Ours today

- #06 item 3: "the GitLab comment is the record (issue for stages 1–3, MR from stage 5)". No shape defined.
- `crq/SKILL.md:101` stage 2: comment = "decisions reached, questions now closed".
- `crq/SKILL.md:246-251`: `/approved` relayed off-MR must be recorded on the MR with who/where + the SHA it covers.
- Fleet Verifier: post `result.md` to MR as is; "'Verified' or 'green' always names a Verification result and
  the commit it ran on." (`create-agent.sh:355-373 @080aabb`).
- `P/qa.md:42-44`: evidence SHA must be MR head; "A gate summary without that evidence is a claim".
- Self-reports: "No labels anywhere"; flake list "only in Discord" (`00-fleet-self-reports.md:6,10`).

### (c) Differences

| | FM | PS | OC | HL | ours |
|---|---|---|---|---|---|
| status words | 6 + `resolved` | inbox classes landed/needs-verify/failed/zombie/noise | — | completed/WIP/planned | none |
| where | local status file | store TSV | return to coordinator | `thoughts/` doc | GitLab comment (decided) |
| done gate | HEAD pushed + PR not draft, script-checked | externalized + ledger row | artifact + checks | — | qa checks SHA = MR head (prose) |
| verdict tied to SHA | yes | yes | — | git_commit field | yes for Verifier/qa |
| next steps field | — | suggested follow-ups | uncertainty | Action Items | — |
| blocked threshold | same obstacle twice | 2 retries then abandon (`:97`) | 1 follow-up | — | — |

### (d) Open decisions

1. **Status vocabulary.** (a) FM's 6 (`working · needs-decision · blocked · paused · done · failed`) + `resolved` ·
   (b) collapse to 3 (`needs-decision · blocked · done`, per #16 bullet) · (c) PS-style verdict words for qa
   (`verified-live · verified-tests · blocked · failed`) plus FM words for others.
2. **Required fields of a `done` comment.** (a) PS REPORT 8 fields · (b) HL 7 sections (adds Learnings,
   Action Items — doubles as resume input for the next fresh worker) · (c) minimal: status word · head SHA ·
   MR URL · what ran · open items.
3. **done-only-if-pushed enforcement.** (a) script/hook refuses `done` unless HEAD is on the remote and MR not
   draft (FM `fm-dod-lib.sh:413-416` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b]) · (b) coordinator checks before relaying (OC `:27`) · (c) prose rule in
   the soul only (ours today, `P/qa.md:42`).

---

## 5 · Retro + `/lesson` procedure

### (a) References

| ref | says | at |
|---|---|---|
| MP who | "The user has asked for a **retrospective**." — user-invoked, `disable-model-invocation: true` | `skills/engineering/retro/SKILL.md:4,7` |
| MP input | "Read the primary sources for the session … default to the current one." | `retro/SKILL.md:13` |
| MP buckets | Navigation · Automated checks · Coding standards · Global AGENTS.md · Tool economy · No-ops · Information access | `retro/SKILL.md:17-23` |
| MP mechanical→check | "Default to building the check over writing the rule." | `retro/SKILL.md:19` |
| MP output | "Present these candidates to the user, in order of severity." | `retro/SKILL.md:25` |
| MP AGENTS.md | "used incredibly sparingly, usually only for **navigation pointers**" | `retro/SKILL.md:41` |
| PS who/how | 3 parallel reviewers (judgment · tooling · divergent) + 1 synthesizer | `reflect/SKILL.md:29-45` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS output | "structured Accepted / Rejected / Backlog list" | `reflect/SKILL.md:45` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS structure check | items better as lint/script/flag move "from Accepted to Backlog" | `reflect/SKILL.md:49` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS approval | "wait for explicit approval … Do not auto-apply." | `reflect/SKILL.md:53` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| PS skip | "One-offs are not learnings." | `reflect/SKILL.md:11 @f713f14` |
| PS close | "encode recurring corrections into `preferences.md` or the brief template" | `orchestrate.md:67 @f713f14` |
| FM routing | captain prefs → `data/captain.md` · fleet facts → `learnings.md` · task notes → backlog · project → `AGENTS.md` (human only) | `AGENTS.md:145-152` |
| FM correct-only | crewmate edits project AGENTS.md "only to correct factually wrong information" | `AGENTS.md:155` |
| FM why | "every entry taxes every agent session of that project." | `AGENTS.md:155` |
| FM on demand | `/stow` → knowledge sweep, routing, completion receipt | `AGENTS.md:158`; `stow/SKILL.md:211-232,258-263` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b] |
| HL | `## Learnings` section in every handoff | `create_handoff.md:54-55` |

### (b) Ours today

- No retro skill, no `/lesson` in agent-platform (`grep -rn "/lesson\|retro"` over `.agents .claude docs/agents`
  finds only "retrospective spec" in `spec-review/SKILL.md:106,301`).
- Personas carry a lesson hook: "propose it as a `code` or `testing` reference addition" (`P/qa.md:58-61`,
  `P/spec-reviewer.md:52-55`).
- #17 Resolution: agents propose MRs, never edit; retro worker at work-item close + `/lesson`; buckets dropped /
  check / project reference / role soul / machine file; ≤2 MRs per work item.
- One retro has been run by hand with MP's skill (`skills/research/35-retro-session-2026-10-02.md`), output per
  item: Category · Evidence · Change · Lands · Kind (mechanical→check / judgement→standards).

### (c) Differences

| | MP retro | PS reflect | FM | ours (#17) |
|---|---|---|---|---|
| trigger | user | user says "reflect" | `/stow` by captain; routing always | close of work item + `/lesson` |
| who runs | the session itself | 3 reviewers + synthesizer | firstmate | a fresh retro worker |
| input | session transcript(s) | active transcript | session memory + files | not decided (transcripts? GitLab thread? both?) |
| buckets | 7 categories by *what kind of fix* | Accepted/Rejected/Backlog by *verdict* | by *destination file* | 5 by *destination* |
| mechanical→check first | yes (`:19`) | yes (`:49`) | — | "check" bucket |
| human gate | presents list | explicit approval before apply | captain extends AGENTS.md by hand | operator merges MR |
| output size cap | none | none | budget/offload rules | ≤2 MRs |

### (d) Open decisions

1. **Retro input.** (a) worker transcripts of every role on the work item (MP `:13`, PS `:17-27`) · (b) the GitLab
   issue + MR thread only (cheap, durable, what #06 made the record) · (c) both: thread first, transcripts only for
   items the thread flags.
2. **Bucket axis.** (a) by destination (#17: dropped/check/project ref/soul/machine; FM `AGENTS.md:145-152` [drift 2026-10-17: cited lines rewritten at 5f2b81b, see research/64b]) ·
   (b) by fix kind then routed (MP `:17-23`) · (c) PS verdict triage (Accepted/Rejected/Backlog) then destination.
3. **Who reviews before the ≤2 MRs open.** (a) none — MR review is the gate (#17) · (b) synthesizer pass with the
   structure check, "check beats rule" (PS `reflect:45-49`, MP `:19`) · (c) coordinator presents list, human
   picks, then MRs (PS `reflect:53`).
