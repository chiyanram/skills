# R30 · Verification history — from per-agent builds to the Verifier, against the new design

Resolves chiyanram/skills#63 (part of #9; follows R28 #60 → `37-verification-runner.md`, R29 #62 → `38-vm-gate-runner.md`).
Read-only research, 2026-10-02. Compared against: #35 Q26 / Q27 (operator decisions) and #50 (coordinator, fresh workers, `post-status`).

Sources:
- agent-fleet: `refs/chiyanram-agent-fleet` at `0b82826`; GitHub issues/PRs on `chiyanram/agent-fleet`.
  The local history is squashed: the whole Verifier + ADR 0002 lands in `28979bc` (#47). The real sequence is the PRs, cited as `af!NN` / issues as `af#NN`.
- agent-platform: GitLab issues/MRs (`#NNN`, `!NNN`) and `origin/master` commits.
- `00-fleet-self-reports.md`.
- firstmate: `gh api` commit history. The local clone is shallow at `549e07f`.
- cursor/plugins (pstack, orchestrate): `gh api` commit history.

---

## 1. Timeline

| date | change | why | evidence |
|---|---|---|---|
| 2026-07-25 | Smoke workers held at **2**; `@llm` project pinned to **1** worker | E7/#38: workers 3 and 4 "both surfaced contention casualties that pass serially — API/DB strain". #34: Ollama contention was "the sole cause of the `@llm` flakes" | `5547c4f5`; `aruvii-ui/playwright.smoke.config.ts:32-41,76-80` |
| 2026-08-08 | `make doctor / next / verify` become the front door | one gate definition, so hand-assembled gates can't drift | `4c2f82c1` (#102 #105 #107) |
| 2026-08-16 | agent-fleet created. Persistent role agents (developer, qa, analyst, spec-reviewer) each run as their own unix user in tmux | fleet lifecycle tooling | `b25514c`, `12562c6` |
| 2026-08-31 → 09-03 | **#343 / REQ-067**: first GitLab CI on instance runners, sized to the 400-minute Free tier. ITs and smoke deliberately left out. D3: "a red pipeline blocks the merge" needs "Pipelines must succeed" set by hand (AC6) | "every merge … gated only by whatever the author ran locally" | `66dcb4ea`; REQ-067:144-193 |
| 2026-09-12 → 09-14 | **#440** deletes `.gitlab-ci.yml` and the GitHub workflow | 100 pipelines: 98 failed, 0 succeeded, all `ci_quota_exceeded` at 0 s. "Pipelines must succeed" was never switched on (still `false` on 10-02, R28 §3) | `37706bd7`; AGENTS.md "There is no CI" block |
| 2026-09-14 → 09-19 | `make verify-fast` becomes the unattended-agent target | full verify too heavy for agents | `37706bd7`, `377a8bcb`; DEVELOPING.md:567 |
| 2026-09-26 → 09-27 | Contabo VM migration: all 4 agents on a new 23 GB VM, rootless podman, per-agent slices | move hosts | `b0b1cbb`, `5328d39` |
| 2026-09-27 → 09-28 | **Every agent runs full stacks itself.** Developer for the DoD, QA again for independent checks. What it cost: 116 OOM kills in the developer slice (af#10); swap 0 B (af#13); the session sat outside its cap (af#14); `memory_high` stalled QA at load 85, which three agents blamed on "other agents" (af#21); QA spent 48 of 56 min hand-fixing ports (#581) | single-user dev tooling × several unix users | af#10 af#13 af#14 af#21; #581 |
| 2026-09-28 | #583 bounds api/worker/Ollama memory and runs `check` once. #581 parameterises role stacks (still **open**) | the same collisions, attacked app-side | `328ee9d4`; #581 |
| 2026-09-29 | **ADR 0002 + spec af#23: the machine-wide Verifier.** Its own unix user, one job at a time, a pushed SHA in, a result keyed by SHA out. "Done" = a PASS at the MR head. A **CI runner is deferred** ("needs Maintainer rights; the Verifier becomes the runner later"), and so is posting to the forge ("Agents relay them") | per-agent stacks collide. "Done" was "an agent's claim in chat, not evidence bound to a commit", and every ticket paid for two full runs | af!24, af!32, af!33, af!35; `docs/adr/0002-machine-wide-verifier.md` |
| 2026-09-29 | Dry runs find 7 Verifier bugs (podman socket timeout, umask, two userns, provisioning restarting busy slots…). Run 7: 767 passed / 1 failed in 1h10, against QA's manual 712 / 48 | live acceptance | af#31 comment; af!36–af!39 |
| 2026-09-30 | First real job: `1 failed / 4782 tests`, with no suite split and no cause shown → per-suite counts and a paste-ready `result.md` | the result has to be readable without the log | af#42, af!43 |
| 2026-09-30 | **#554 / !230.** The gate reads "FAIL, only known flakes". The known-flake list lived **only in Discord**; ram accepted it in Discord | flakes: smoke-69 T1, `CustomPiiEndpointClientTest` | !230 notes 09-30 12:43, 14:06 |
| 2026-10-01 | Merging master into !230 voided the gate. The next job died **ERROR**: `setup-verifier.sh --register` restarted the slot mid-job. Then an `npm ci ECONNRESET` made it **INCOMPLETE**. The 5th job confirmed the gate. Tally: 5 jobs, 3 QA rounds, 2 days | reconcile restarts unconditionally; network in the image build | !230 notes 10-01 06:10–08:19; af#48 → af!49 |
| 2026-10-01 | `DOCKER_HOST` exported in agent sessions. Agents' own ITs had failed ("no Docker environment"); the Verifier unit already set it | the developer minimum needs ITs runnable in-session | af#46 → `28979bc` (af!47); af#44 (locale) |
| 2026-10-01 | **#585: done = `make verify-full` green at the MR head, *whoever runs it*.** Targeted checks while working. Build cache trusted; IT image tags pinned | the DoD sent every implementer to a full stack (#554: 1.5 h, OOM, Keycloak timeout) | `309982e1` |
| 2026-10-01 | #576 scripted fake model (`smoke-92`). #608 moves smoke-69 onto it. **#609 (convert the other `@llm` specs) and #610 (real-provider run) stay open** | `@llm` flakes on CPU Ollama | `453a644b`, `276483aa`; #609, #610 |
| 2026-10-02 | Verifier `list` marks jobs `current` / `behind head`. needrestart never restarts a slot. **af#56 cancel / auto-cancel on newer submit: open.** That day the operator cancelled twice by hand as root, about 2 h lost on superseded SHAs | stale-SHA runs | af#55, af!66, af#56 |
| 2026-10-02 | R28: Option B, a self-hosted runner wrapping the Verifier. R29: 61 min = smoke 40 % · serial IT task 31 % · deploy 16 %; memory is not the cause | — | `37-…md`, `38-…md` |
| 2026-10-02 | **Decided.** Q26: runner on the VM, shell executor, `concurrent=1`, job = the Verifier; instance runners off → register → "Pipelines must succeed"; developer minimum = touched-module `test-module`/`it-module` + `verify-fast` + an honest what-ran note; only the runner runs `verify-full`/smoke. Q27: the gate's smoke runs on the scripted model only; real-Ollama goes to a nightly / on-demand tier; Playwright workers 2 → 4. #50: coordinator + fresh workers; `post-status` refuses `done` unless pushed and non-draft; rebase voids SHA-tied evidence | — | #35 comments, #62 comment, #50 resolution |

---

## 2. Kept / repeated / new risk, per decided element

| decided element | kept (lesson honoured) | repeated (a mistake already made) | new risk |
|---|---|---|---|
| **Self-hosted runner wrapping the Verifier** (Q26) | One job at a time, clean clone at the SHA, own user, memory gate, OOM note (ADR 0002). The result lands on the forge at the SHA and blocks merge, which closes F8 (relay by hand). Instance runners go off first, so the #440 quota failure can't recur | **"Pipelines must succeed" left off.** REQ-067 AC6 said exactly this in 09-03, and it was never done. Keep it as an explicit acceptance item, checked with `glab api`, not assumed. **Restart mid-job**: af#48 (reconcile) and af!66 (needrestart) both killed or threatened running jobs, and a `gitlab-runner` package upgrade or service restart is a third path to the same failure | **Two queues.** Agents still calling `fleet-verify submit` beside the pipeline brings back "every ticket pays two full runs" (af#23). Either the job calls the slot runner directly (af#23 story 28) or agents stop submitting. **Cancel**: GitLab `interruptible` kills the job, but af#56 shows hand-cancel left stacks needing a root cleanup, so teardown on cancel is unproven. **Trust**: the slot user held no forge credentials (af#23 story 23); a shell-executor job carries a `CI_JOB_TOKEN`. **Quick-lane / draft pushes** each trigger a ~1 h pipeline unless `workflow:rules` filters them |
| **Scripted model in the gate + 4 workers** (Q27) | Removes CPU-Ollama contention, the cause of #34 and the `@llm` flakes behind "FAIL, only known flakes" on !230 | **Workers 2 → 4** was already tried: E7/#38 (`5547c4f5`, `playwright.smoke.config.ts:36-41`) showed workers 3 and 4 fail from *API/DB* host strain, which has nothing to do with Ollama. The comment allows raising it on "a beefier CI node". The runner VM also hosts the agents, so it is not one. Measure 4 vs 2 on the VM before the gate depends on it. **A tier that gates nothing**: a nightly real-Ollama run nobody reads is the #440 pattern ("a failing signal that gates nothing") | **Coverage hole.** Only smoke-92 and smoke-69 are scripted; #609 (convert the rest) is open. "Real-Ollama specs leave the gate" therefore drops most `@llm` behaviour from the gate until #609 lands. The nightly tier also has no runner, schedule or owner yet |
| **Developer minimum** = touched-module tests + `verify-fast` + what-ran note | `create-agent.sh:361 @080aabb` "targeted tests in your own checkout"; #585 "targeted checks while working"; pstack's honest evidence levels | **`it-module` beside the gate on the same VM.** R29 traced the agents' "OOM on make verify" to a developer `-Xmx4g` Gradle plus containers running *beside* the Verifier. The minimum still includes `it-module`, so that pairing survives, and Ryuk contention with it (F5; the guard hook only advises). **Skipped existing tests**: the self-report "didn't run existing tests (`RefusalReasonSpec`)". "Touched module" misses dependents' ITs, which first show up an hour later in the gate (5 jobs on !230) | The what-ran note is free text. Nothing checks it against what actually ran, and the earlier "green" claims in chat are the failure ADR 0002 was written to end |
| **Only the runner runs `verify-full` / smoke** | ADR 0002: agents never bring up full stacks. #585: the DoD names no runner | #585's fallback, *"where … nothing names a runner, the MR author produces the result"*, contradicts it. The AGENTS.md DoD text must name the runner once it exists, or fresh workers will read the fallback and run the stack themselves (the 09-27/28 failure) | **Single point of failure**: VM down means no merges, and there is no documented bypass. A bypass people invent under pressure is the #440 lesson |
| **Coordinator + fresh workers** (#50) | Ends the 100-turn / 3-day-silent sessions and the Discord-only state. The GitLab thread becomes the state; respawn fresh rather than resume | **The known-flake list lives in chat.** On !230 it was in Discord, and QA needed an analyst to confirm it. A fresh worker has no Discord memory, so the list must be a file or a quarantine tag in the repo | **Parallel fresh workers share one unix user's slice.** N developers each running `it-module` hits the af#10 / af#21 memory caps: OOM kills, or stalls blamed on "other agents" |
| **`post-status` refuses unpushed / draft `done`** | firstmate `a8a2959` (head only in the worker copy) and `dbc0bc4` (non-draft PR), ported as-is. Ends "done = an agent's word" (af#23) | — | It checks *pushed*, not *verified*. `done` should also require a pipeline at that SHA, or the qa verdict does all the work. The verdict words (verified-live · verified-tests · failed) have no slot for "FAIL, only known flakes", the !230 reality. Either flakes are quarantined so the gate can PASS, or every such MR becomes `needs-decision`. **Rebase voids evidence**, so each rebase-before-done costs about 1 h of gate |

---

## 3. How the references evolved theirs

**firstmate + no-mistakes** (gh api; 2026-06 → 09)

| date | change | evidence |
|---|---|---|
| 06-12 | contributor guardrails in CI | `683b8cf` (#5) |
| 07-13 | no-mistakes gate agents may not drive the fleet (verifier separated from the doers) | `6556882` (#518) |
| 07-22 → 08-02 | one canonical timed test runner, then shards across CI runners using CI timings (speed came from splitting, not from more local workers) | `f02eef1`, `673b6ad`, `f5ab708`, `869ae90` |
| 08-14 | test evidence stored in the repo | `1238402` (#2355) |
| 08-21 → 08-25 | required check for a pipeline attestation, then the **attestation bound to the PR head** | `a0cec26` (#2710), `3e5577b` (#3027) |
| 09-12 | superseded PR CI auto-cancelled; unbounded jobs bounded | `83c63cc` (#4281) |
| 09-19 | workflow timeouts in three tiers | `2bcb88c` (#4910) |
| 09-21 → 09-23 | `done` refused for a draft PR (`dbc0bc4`), then for a head that exists only in the worker copy (`a8a2959`); required check pinned to v1.80.1 (`8c1cdb7`) | as cited |
| 09-26 → 09-30 | waiting workers declare their waits and spend no turns | `bb69be6`, `fd325b1` |

Order: separate the verifier → make it required → bind it to the head SHA → cancel stale runs → refuse `done` without push / non-draft.
We are taking the last step (`post-status`) and the first (Verifier) together. The middle ones — required **and** head-bound, stale-cancel — are what Q26 must actually deliver. firstmate never tried more local parallelism for speed; it sharded on CI timings.

**pstack / orchestrate** (cursor/plugins)

| date | change | evidence |
|---|---|---|
| 05-06 | orchestrate ships with a separate verifier agent ("reading the diff is not verification"), a `verifier-blocked` verdict instead of a weaker pass, and a self-report that a later verifier overrides | `03192a5`; `prompts/verifier.md:23,26` |
| 07-12 | `create-verification-skill`: the generator must prove its own output once. Revised 6 times from the friction reports of 4 cloud agents | `e42d29f` (#150) |
| 07-12 | `maintain-verification-skill`: re-doctor after every failed drive; never tear down a shared instance mid-pass; evidence must survive cleanup | `6714489` (#151) |
| 09-01 | playbooks made forge-neutral; Shipping lands only the contiguous *verified* run, one fresh agent per PR | `23a56e2`; `06-verify-and-ship.md:128 @f713f14` |

What transfers:
- `blocked` beats a thinner pass. That fits our INCOMPLETE / ERROR jobs.
- Health-check after anything surprising. That fits the npm ECONNRESET and slot-restart runs.
- The judge is never the writer. That fits Q23's fresh qa.

---

## 4. Net

The decided design keeps the core lessons:
- one serialised gate at the SHA;
- agents off full stacks;
- evidence on the forge;
- no relay by hand.

It risks repeating four already-paid mistakes:

1. "Pipelines must succeed" never enabled (REQ-067 AC6, 09-03).
2. Workers 3/4 flaking on host strain (E7/#38, 07-25).
3. A side tier that gates nothing (#440).
4. The flake list in chat (!230).

New risks to close in the work items:
- double queue (agent submit + pipeline);
- cancel teardown (af#56);
- the #609 coverage hole;
- parallel fresh workers inside one slice;
- `done` not requiring a pipeline at the head.
