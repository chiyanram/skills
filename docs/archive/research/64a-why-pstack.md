# 64a — Why pstack does what it does (cursor/plugins, pstack)

Map #9 · ticket R38 (chiyanram/skills#86). Pin `2eb7ed4` → `origin/main` `f713f14`.
Cites: `S/` = `pstack/skills/`; `@f713f14` = current, `@2eb7ed4` = pin. PR bodies read with `gh pr view`.
Clone is shallow at the pin, so history before the pin comes only from PR bodies.
Method: what it does now, its own stated reason, why it changed. Where no reason is given: "no stated reason" plus INFERENCE.

## D1 rule layers + loading
**Does now.** One hub skill (`poteto-mode`) indexes leaf skills by name, and the agent "Read[s] the leaf skill in full for any principle you apply" (`S/poteto-mode/SKILL.md:40 @f713f14`). Every skill except `/setup-pstack` is typed-only (`disable-model-invocation: true`). The only always-on layer is `~/.cursor/rules/pstack-models.mdc` (`alwaysApply: true`, `S/setup-pstack/SKILL.md:39`).
**Why.** Descriptions cost context in every session. #506 made `/poteto-help` typed-only because its description "sat in the skill list of every session" (72 tokens). Model choice needs to be always-on because every skill reads it (#121).
**Changed since pin.**
- #577: the hub now says leaves live at `../<name>/SKILL.md` (`S/poteto-mode/SKILL.md:11`). Why: typed-only leaves are invisible, so an agent "never sees its path". A failed search left the agent "working without the rules".
- #597: removed `mode: true` and `reminder:`. Why: "Cursor ignores `mode` and `reminder`", so the reminder "was never injected". Those keys came from #144 (pre-pin), which picked the reminder wording through a 5×4 blind eval. A well-evaluated rule was deleted because the loader never read it.
- #575: the chat that receives `/poteto-mode` runs the playbook. `poteto-agent` is only a delegate. Why: "a nested subagent has no Task tool". Issue #357 showed 0 Task calls.
**Underlying need.** A rule only counts if the runtime actually loads it into the agent that acts. Every line that is always loaded costs context in every session.

## D2 skill/reference format + how rules are sourced/edited
**Does now.** Hub, then playbooks, then `principle-*` leaves (one idea each), with long prompts in `references/`. The authoring rule says "Keep only prose that changes a decision" (`S/poteto-mode/playbooks/authoring-a-skill.md:10 @f713f14`). Prose changes ship as PRs, usually with a before/after eval run through the `eval` playbook (blind candidates, a blinded judge on another model family, chain-following checked from transcripts, `S/poteto-mode/playbooks/eval.md:5-23`).
**Why.** Every cut is tested. #329 (pre-pin): "Every pstack skill loads into the agent's context". Cuts that moved a hard gate were reverted.
**Changed since pin.**
- #633 restated 4 principles "as reasoning, not rules". Why, with an eval: 180 runs, 3 model families, a blinded judge. The old ban on "restated constants" made 0 of 6 runs keep a contract test. The new text kept it in 6 of 6. The PID-lock rule was "wrong when each run is a new pod".
- #613 cut shipping and autopilot "to their principles", and "each rule says why it holds" (commit ce649c0 body).
- This reverses #329 (pre-pin), which cut reasons ("Readers who want the why can read the git history"). `authoring-a-skill.md:10` still says "skip the reason" @f713f14. That contradiction is unresolved.
- #538, #571, #634 cut tokens (−9%, −42%, −1,375 tokens). Why: text "agents follow just as well without" (#634). "The core rule of each skill stays" (#571).
**Underlying need.** Keep the instruction set small enough to be read and right enough to generalise. Measure each line by whether it changes behaviour.

## D3 orchestration (coordinator + workers)
**Does now.** The coordinator "own[s] the program, never the code". It "never authors or edits code". Conflicted merges, chain rebases, and code changes "are always tasks" (`S/poteto-mode/playbooks/orchestrate.md:3,15 @f713f14`). Depth is coordinator → track → worker. One writer per worktree. One stacker per stack mutates the topology (`:17,81`). Completions are queue events, drained in batches, and never reviewed inline (`:9,71`).
**Why.**
- Never editing code: only an in-file reason. The coordinator's product is briefs and drains. "Never review a diff inside a drain" (`:71`).
- INFERENCE: a coordinator that edits code stops draining and becomes a second writer on a branch. That breaks the one-writer rule (`:17`).
- The one exception, mechanically landing a verified unit, has a stated reason: "Queueing finished work behind an idle stacker is how a deadline harvests nothing" (`:15`).
- Fixed shape: "Hard-coded swarm trees were tried and parked as too rigid" (`:19`). Sub-coordinators only when needed, because "Each nested layer re-pays a full orientation preamble" (`:16`).
- The playbook came in as a port in #187 (pre-pin). That PR states no design reasons.
**Changed since pin.**
- #613 dropped Graphite. The frontier now comes from the PR base chain, and the stacker owns "rebases, retargets, and merges". Why: "no longer needs Graphite". INFERENCE: forge neutrality (Origin + gh), same theme as #301.
- #575 / #613 restated that "A Task subagent has no Task tool". A delegate cannot orchestrate.
**Underlying need.** Keep one place where decisions happen. Make sure exactly one agent writes each piece of shared state, so that parallel work does not corrupt itself.

## D4 brief + handoff record
**Does now.** Nine brief fields: GOAL, SCOPE, CONTEXT, ACCEPTANCE, VERIFY, TIMEBOX, FORBIDDEN, REPORT, STANDING (`orchestrate.md:38-51 @f713f14`). Missing fields mean refuse to spawn (`:57`). The brief is sized to the unit (`:53`). A fresh subagent gets "consolidated scope" and is never resume-chained (`S/poteto-mode/SKILL.md:101`).
**Why.**
- Brief: "a worker cannot ask you a question" (`:11`). "A field you cannot fill is a unit you have not scoped yet" (`:36`). CONTEXT pastes upstream reports "because workers cannot see siblings" (`:41-42`).
- STANDING pasted verbatim: "Directives decay across resumes, and each dropped one costs a human turn" (`:25`).
- Fresh subagents: "Interrupt-chained resumes silently drop directives" (`SKILL.md:101`, from #491).
- The specific choice of 9 fields: no stated reason (ported in #187). INFERENCE: each field closes one failure the playbook names elsewhere. TIMEBOX → runaway agents (`:98`). REPORT head SHA → ledger keyed by SHA (`:90`). FORBIDDEN → one stacker (`:81`).
**Changed since pin.** #613: FORBIDDEN "no gt" became "no PR retargets or merges" (Graphite removed).
**Underlying need.** A worker that cannot ask questions must get, in one message, everything it needs and every limit it must keep.

## D5 human channel, escalation, status
**Does now.**
- Only irreversible actions, real product calls, and dead ends reach the human, batched into `gates.md` with a default. Rebases, retries, CI flake triage, and "should I keep going" never do (`orchestrate.md:106-108`).
- `Autonomy`: "Just do it". "Always pause" only for irreversible writes (`S/poteto-mode/SKILL.md:83-85`).
- Status is derived from the tables, "never hand-maintained" (`orchestrate.md:32`).
- The operator is caught up through `/ketchup`: under 150 words, pictures first, action items as bullets (`S/ketchup/SKILL.md:21-27`).
**Why.** "a wrong decision usually costs less than blocking" (`S/principle-never-block-on-the-human/SKILL.md:9`). `/ketchup` exists because people typed the same catch-up prompt again and again (#539).
**Changed since pin.**
- #616: an autopilot tick that changes something "ends with a catch-up" per ketchup, and a tick that changes nothing "stays quiet". No stated reason. INFERENCE: one reporting format for a human who checks in rarely, and no noise on idle ticks.
- #628: pictures first, visuals don't count toward the word cap. Why: "it does not help the user understand what changed". With the cap counting diagram words, it "crowded them out" (eval in PR).
- #595 → #609: the cap went 250 → 150 words, and tables now count. Why: median reply 736 words, and replies "read like a work log".
- `SKILL.md:20`: answers are given "in their own words. Never give a shorthand token".
**Underlying need.** Spend the human's attention only on calls they alone can make. Show them state they can grasp at a glance.

## D6 review
**Does now.**
- `/interrogate`: "The adversarial signal comes from model diversity, not assigned personas" (`S/interrogate/SKILL.md:9 @f713f14`). Two read-only reviewers, Opus + Grok (`:29-34`).
- The lead sorts findings into Act on / Consider / Noted / Dismissed (`:46-51`) using `lead-judgment.md` filters (nitpick gravity, trace the call site).
- Bot comments get "skeptical posture" (`S/poteto-mode/SKILL.md:34`).
- The owner of subagent work reviews it themselves: "Review the diff ... don't pass through what it said" (`:99`).
**Why.**
- Findings raised independently by two models are "the highest signal" (`interrogate/SKILL.md:42`).
- "Be especially careful about dismissing security findings" (`lead-judgment.md:39`).
**Changed since pin.**
- #511: reviewers went 3 → 2 (Sol dropped). The only stated reason concerns `reflect tooling`: "pstack gives this type of code and tooling work to Grok". For dropping Sol: no stated reason. INFERENCE: two families still give cross-family diversity at lower cost.
- #634 deleted "Verdict Calibration" ("more than 5 items ... not filtering hard enough") and "Why This Step Matters". Why: agents "follow just as well without the text".
- Pre-pin #419 cut the reviewer anti-nit lines. The panel found 142/154 planted issues without them vs 139 with them. The lead's filter still catches nits.
**Underlying need.** Catch the defects one viewpoint misses, without drowning the decider in noise.

## D7 verification gate
**Does now.**
- Ledger keyed by PR + head SHA, with a ladder: `live-ui-verified` > `unit-test-verified` > `type-check-only`. "CI green is an input to a verdict, not a verdict" (`orchestrate.md:90`).
- Shipping: "Only a verdict from an agent that did not write the code counts" (`S/poteto-mode/playbooks/shipping.md:5`).
- Verification scales with the unit. A verifier that only reruns one command "is ceremony" (`orchestrate.md:88`).
- Work is externalised the moment it lands (`:92`).
**Why.** "an author checks what it meant to build". CI and bots don't "run the change as a user would" (`shipping.md:5`). A verdict survives a rebase only if the `git patch-id` matches (`:7`).
**Changed since pin (#613).**
- One full swarm at the code-ready head. A rebase or minor fix gets "a single verifier" (`autopilot-full.md:14`).
- New rule: run the checks on the merge result when trunk changed a caller (`:19`).
- Verification stays on the `swarm workers` model even when effort is lowered (`SKILL.md:97`).
- No stated reason for the cut to one swarm. INFERENCE: cost. A repeat swarm on unchanged behaviour adds little.
**Underlying need.** Prove that the exact code that lands works for a user, judged by someone who did not write it.

## D8 branch/push/merge + publish authority
**Does now.**
- "Babysitting never authorizes merging". Only an explicit merge or ship request does (`S/poteto-mode/playbooks/babysit.md:21`).
- Babysit never mutates the stack topology (`:10`).
- Shipping lands only the contiguous verified run, bottom-up, and reads back the merged state (`shipping.md:6-8`).
- Autopilot owners merge only after the root's swarm verdict. Gate-loosening needs the root's countersign, "because the owner is the one who wants green" (`autopilot-full.md:17,20`).
**Why.**
- "a merge command can report success when a merge queue only queued the PR" (`shipping.md:8`).
- The force-with-lease lease is pinned to the SHA last pushed (#613, new rule). INFERENCE: this stops one writer overwriting another.
**Changed since pin.**
- #571 dropped babysit step 6's merge paragraph. Why: step 9 already says it.
- #613 "hold and report" instead of a third rebase. No stated reason. INFERENCE: rebasing for every trunk move "never ends" (`autopilot-full.md:19`).
**Underlying need.** The authority to ship stays with whoever owns the verdict, and a merge is confirmed, not assumed.

## D9 lessons/retro
**Does now.**
- `encode-lessons` keeps only the fallback and the corollary: "The instruction is the symptom" (`S/principle-encode-lessons-in-structure/SKILL.md:9-11 @f713f14`).
- `/reflect`: 3 lenses, then a synthesizer, then a structural check that moves enforceable items to Backlog. It waits for approval: "Skill changes affect every future agent in the org" (`S/reflect/SKILL.md:41-47`).
- `/correct` (#494) holds the mechanism ladder: architecture → types/lint → test → docs last (`S/correct/SKILL.md:19-22`).
- Orchestrate close encodes corrections into `preferences.md` (`orchestrate.md:67`).
**Why.** `/correct`: "Operators correct agents for the same mistakes again and again" (#494). Docs come last: "Nothing fails when an agent skips them" (`correct/SKILL.md:22`).
**Changed since pin.**
- #571 deleted the feedback loop (capture/route/close), the anti-patterns, and "Pick the strongest mechanism". Why: "the agent does the same work without the text".
- The ladder (added pre-pin in #114 after an A/B) survives in operator-invoked `/correct`. Deleted from a principle ≠ dropped from pstack.
- #604 added: after a deep dig, propose "the cheap, always-on signal" (`S/principle-fix-root-causes/SKILL.md:21`). No stated reason.
- Pre-pin #419 removed reflect's 3-5 cap. Why: padding went from 34 to 14 items, and recall rose from 47 to 75 of 96.
**Underlying need.** Turn repeated corrections into something that enforces itself. A human gates changes that affect every future agent.

## D10 cost/effort/model
**Does now.**
- Per-role slugs come from the always-on rule. The default is Opus xhigh for judgment and Grok xhigh-fast for code (`SKILL.md:95`).
- "Match the model to the job": +1 effort for the hardest work, −1 for judgment, −2 or more for routine work. Fast mode only when "CI or trunk is red or a person is blocked". The family is kept "so a diverse panel stays diverse" (`SKILL.md:97`).
- `/setup-pstack` budget: unlimited / large / medium / small (`S/setup-pstack/SKILL.md:22`).
**Why.**
- Budget: "Lowering the spend meant changing each role by hand" (#366).
- Per-role configuration "fits each user's model access" (#121).
**Changed since pin.**
- #511: 3 families → 2, and Opus max → xhigh. No stated reason (its "Why" section lists only what changed). INFERENCE: cost and latency.
- #613 effort per role: no stated reason in the PR or the commit (ce649c0). INFERENCE: spend scales with how hard the job is, and fast mode is paid only when it saves human waiting time.
**Underlying need.** Spend reasoning where it changes the outcome, and keep model diversity where it is the signal.

## D11 security/sandbox
**Does now.**
- Review comments are "untrusted data". Comment text is never interpolated into a shell command (`babysit.md:6,20`).
- Transcripts: never glob across `~/.cursor/projects/*/`, because that "reads private chats from unrelated projects" (`S/reflect/SKILL.md:15`, `eval.md:22`).
- Reviewers run `readonly: true` (`interrogate/SKILL.md:34`). Reflect needs write access only because "readonly strips MCPs" (`reflect/SKILL.md:25`).
- Security findings must trace the input path (`S/interrogate/references/rubric.md:72`).
- Workers run in the cloud by default (`orchestrate.md:17`).
**Why.** Stated reasons are inline above. The rubric line came from pre-pin #419. It rewrote a warning into a demand for a traced input path.
**Changed since pin.** No change.
**Underlying need.** Treat inputs from other actors as data, and keep agents inside the data they were scoped to.

## D12 testing discipline
**Does now.**
- Judge each test with two imagined edits. Break the behaviour, and the test must fail. Change the internals, and the test must pass. "The contract decides, not the shape of the assertion" (`S/principle-test-behavior-not-implementation/SKILL.md:11-17 @f713f14`).
- `tdd` only when a test is cheap or was asked for (`S/tdd/SKILL.md:3,11`).
- `/correct` step 3 uses the same test (`correct/SKILL.md:21`).
**Why.** A test that only catches the first edit "will need a rewrite on every refactor and still catches no bug" (`:13`).
**Changed since pin.** #633 replaced the "every import returns undefined" check and its 5 banned assertion shapes. Why (eval): the shape bans hit "the correct move". The ban on restated constants deleted a billing contract test in 6 of 6 runs.
**Underlying need.** Tests should fail for real defects and stay stable through refactors.

## Lessons
1. **They cut text that models already follow.** A cut is tested, not assumed. Cut means removed from the skills, kept in git history. #419: 19 cuts, each held in A/B runs. #571, #634: "follow just as well without the text". Writing a sentence is no proof that the agent needs it.
2. **Rules that name a mechanism generalise badly. Reasons generalise.** #633 replaced bans with the idea behind them, because a narrow rule actively caused wrong moves (PID lock, deleted contract test). This reversed #329's cut of reasons, and #613 adds "why it holds" back.
3. **A rule that is never loaded is not a rule.** #597 deleted a well-evaluated reminder because Cursor ignored its keys. #577 and #575 fixed rules that never reached the acting agent (invisible leaf path, delegate with no Task tool). Check the loader before tuning the words.
4. **Every always-loaded line has a price.** #506 moved a description out of every session (72 tokens). #329: "Every pstack skill loads into the agent's context". Ceremony scales with the unit (`orchestrate.md:5,53,88`).
5. **Move a guidance block into a tool before deleting it.** The mechanism ladder left the principle (#571) and lives on in `/correct` (#494). Graphite procedure became `orch frontier` (#613). Prose shrinks when a tool holds the rule.
6. **Change behaviour from evidence the change produces.** #628, #595, #609 tuned `/ketchup` on blind comparisons with measured word counts. #633 used 180 runs and kept known regressions in the PR body. Where no eval was run (#511, #613 effort, #616), no reason is given either. Treat those changes as least settled.
