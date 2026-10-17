# R28 · Verification runner — how references run the gate, and where ours runs

Resolves chiyanram/skills#60 (part of #9, raised in G9d #35). Read-only research, 2026-10-02.

## Sources (HEAD at time of reading)

| repo | path | HEAD |
|---|---|---|
| kunchenguid-firstmate | `refs/kunchenguid-firstmate` | `549e07f` |
| cursor-plugins (pstack, orchestrate) | `refs/cursor-plugins` | `2eb7ed4` |
| openclaw-openclaw | `refs/openclaw-openclaw` | `b94e5177` |
| addyosmani-agent-skills | `refs/addyosmani-agent-skills` | `2686b62` |
| humanlayer-humanlayer | `refs/humanlayer-humanlayer` | `99abe67` |
| mattpocock-skills | `refs/mattpocock-skills` | `d81f3a1` |
| chiyanram-agent-fleet | `refs/chiyanram-agent-fleet` | `28979bc` |
| agent-platform (ours) | worktree `crq-597-b837e3`, branch `chore/643-one-rulebook-skeleton` | `71b5deb4` |

`refs/` = `/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/`.

**no-mistakes** is not cloned anywhere under refs. What is visible is how firstmate consumes it:
`.no-mistakes.yaml`, the `require-no-mistakes` action pinned at v1.80.1
(`.github/workflows/no-mistakes-required.yml:27`), and status captures from v1.70.1
(`tests/captures/no-mistakes-v1.70.1/README.md`). Its internals below are as firstmate describes them, not read from its source.

GitLab facts: docs.gitlab.com (primary), fetched 2026-10-02, plus a live `glab api` read of our project.

---

## 1. Per reference

### firstmate + no-mistakes

- **Implementer before handoff:** commits on the ship branch, then hands over to the pipeline —
  "Firstmate will then instruct you to run /no-mistakes" (`bin/fm-dod-lib.sh:589 @5f2b81b`). The
  pipeline steps are `review`, `test`, `document`, `lint`, plus `push`, `pr`, `ci`
  (`docs/gerrit-forge-integration.md:262`); "skip nothing else: `review`, `test`, `document`, and
  `lint` are the whole point" (`bin/fm-dod-lib.sh:497 @5f2b81b`). Lint is pinned to the same script CI runs
  (`.no-mistakes.yaml:34` `lint: 'bin/fm-lint.sh'`).
- **Verifier:** forge CI on GitHub-hosted runners (`.github/workflows/ci.yml:32` `runs-on: ubuntu-latest`).
  A second workflow refuses any PR not raised through the pipeline — "PR must be raised via
  no-mistakes" (`no-mistakes-required.yml:24`). VISION states the split: "validation belongs to no-mistakes, CI belongs to the forge"
  (`VISION.md:71`).
- **SHA tie:** the ready report is `done: PR {url} checks green` (`fm-dod-lib.sh:598 @5f2b81b`), "accepted
  only when this copy's HEAD … is one the /no-mistakes run pushed" (`:451`). GitLab merge path
  needs "a successful pipeline at the current head" (`docs/architecture.md:404 @5f2b81b`).
- **Serialisation:** per-PR concurrency group with `cancel-in-progress` on PRs (`ci.yml:23`), so a newer push replaces older runs.
- **Posted back:** natively. The forge check on the PR is the result.

### cursor-plugins — pstack / orchestrate

- **Implementer:** the worker self-reports one of `live-ui-verified | unit-test-verified |
  type-check-only | not-verified` (`orchestrate/.../prompts/worker.md:55`). The script then "re-runs
  declared `measurements` on your branch" (`worker.md:52`).
- **Verifier:** a separate cloud agent. "Run the code. Reading the diff is not verification."
  (`prompts/verifier.md:23`). If the environment fails it sets `verifier-blocked` instead of a weaker pass
  (`verifier.md:26`). There are five verdicts (`verifier.md:41`), and "A later verifier overrides that self-report"
  (`references/handoffs.md:140`).
- **Where:** Cursor cloud agents through the Cursor SDK (`orchestrate/skills/orchestrate/SKILL.md:9`).
  Each verifier is a fresh environment.
- **SHA tie / posted back:** branch-scoped, not SHA-scoped. The verdict is persisted on the target task's row in
  `state.json` (`handoffs.md:130`). It goes to the planner only, never to a forge.
- **create-verification-skill / maintain-verification-skill:** these make the *drive the real app* step
  repeatable. A Doctor step comes first (`create-verification-skill/SKILL.md:28`). On isolation: "refusing to double-drive a
  shared instance beats corrupting the user's session" (`:19`). For servers, "one long-lived instance driven serially"
  (`maintain-verification-skill/SKILL.md:33`).

### openclaw

- **Implementer:** "Prove changes with focused local runs (Crabbox/Testbox for suites too heavy for the
  host)" (`AGENTS.md:91`). The contributor baseline is `pnpm build && pnpm check && pnpm test`
  (`CONTRIBUTING.md:93`). Each test states its measured CI cost (`AGENTS.md:93`).
- **Verifier:** GitHub CI with the required `openclaw/ci-gate`. Merge "requires completed review, the exact
  prepared head, and the enforced `openclaw/ci-gate`" (`scripts/AGENTS.md:30` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d]). Heavy suites can run off-host:
  `OPENCLAW_PR_GATES_REMOTE=testbox` runs full `pnpm test` on a Blacksmith Testbox, and the lease id and run URL are recorded
  (`scripts/AGENTS.md:40` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d]).
- **SHA tie:** "Prior-head CI remains prior-head evidence" (`AGENTS.md:38`).
- **Serialisation:** concurrency groups per PR number (`.github/workflows/ci.yml:90`).
- **Stance:** "CI is expensive; do not spend it on proof" (`AGENTS.md:91`). There are no reruns to get green
  (`AGENTS.md:88`).

### addyosmani-agent-skills

- **Implementer:** the CI-failure loop ends "verify locally before pushing again"
  (`skills/ci-cd-and-automation/SKILL.md:178`).
- **Verifier:** CI runs lint → unit → integration → build. "No gate can be skipped" (`:54`). The skill also requires
  "Required status checks: CI must pass before merge" (`:305`) and a Build Cop who owns red (`:300`).
- **Where / SHA:** generic GitHub Actions on `ubuntu-latest` (`:72`). The skill shows no SHA-binding mechanism beyond the forge's status checks.

### humanlayer

- **Implementer:** a pre-push hook installed by `make githooks`: `echo 'make check test' > .git/hooks/pre-push`
  (`Makefile:114`). `/implement_plan` runs "the success criteria checks (usually `make check test` covers everything)"
  (`.claude/commands/implement_plan.md:46`), then pauses for human manual verification (`:50`).
- **Verifier:** `/validate_plan` re-runs `make check test` (`.claude/commands/validate_plan.md:27`).
  CI runs the same targets (`.github/workflows/main.yml:93` `make check`, `:167` `make test`) on `ubuntu-latest`.
- **SHA tie / posted back:** forge status checks only. The PR description carries the checklist of commands run
  (`describe_pr.md:44`).

### mattpocock-skills — retro

- No runner. It treats a missing one as a defect: "A repo with no **guardrail** (no pre-commit hook and no CI
  job…) is itself a finding" (`skills/engineering/retro/SKILL.md:18`). Mechanical violations get a
  deterministic check, "Default to building the check over writing the rule" (`:19`).

### chiyanram-agent-fleet — the Verifier (ours, already built)

- **Implementer:** "targeted tests in your own checkout are fine" (`scripts/create-agent.sh:361-362 @080aabb`).
  The agent must not bring up the full stack itself (`:340-341`). Before any heavy step it checks memory: `free -m`, with 3500 MB
  free as the floor (`:325-327`).
- **Verifier:** the `fleet-verifier` unix user runs the full verification "one job at a time, on a clean checkout of a pushed
  commit" (`create-agent.sh:359-360 @080aabb`). Mechanics in `verifier/fleet-verify`:
  - a fresh detached clone at the exact SHA (`:241-261`)
  - a per-job `TMPDIR` and `-Djava.io.tmpdir` (`:305-311`, `:471-475`)
  - memory gating: the oldest job waits if it doesn't fit (`:661-675`)
  - an OOM-kill count from the cgroup, written into the result (`:409-420`, `:519-522`)
  - SUPERSEDED for still-queued older jobs on the same branch (`:14`)
- **SHA tie:** `summary.json` carries `status, sha, branch` (`fleet-verify:24`). "'Verified' or 'green' always names a Verification result and the commit"
  (`create-agent.sh:373 @080aabb`). In ADR 0002: "Done" means "a PASS Verification result at the MR head"
  (`docs/adr/0002-machine-wide-verifier.md:31`).
- **Posted back:** **by the agent, by hand.** "Post `result.md` from the job folder to the MR as is"
  (`create-agent.sh:368 @080aabb`). The Verifier itself posts nothing — "the Verifier never posts anywhere" (`CONTEXT.md:78`).
- **The ADR deferred a CI runner,** because "registering a runner needs Maintainer rights, and the Verifier becomes the runner
  later" (`0002…:23-25`). Measured: ~1h45 per job, ~13 jobs/day (`:29-30`).

---

## 2. Comparison

| | firstmate + no-mistakes | pstack orchestrate | openclaw | addy | humanlayer | agent-fleet Verifier |
|---|---|---|---|---|---|---|
| implementer runs | commit; pipeline does review/test/doc/lint | self-reported verdict level | focused local runs; heavy suites → Testbox | local fix before re-push | pre-push `make check test` | targeted tests only |
| verifier runs | forge CI | separate verifier agent runs the code | CI `ci-gate` (+ optional Testbox) | CI lint/unit/IT/build | CI `make check` / `make test` | full suite, `fleet-verify` |
| where | GitHub-hosted | Cursor cloud agents | GitHub + Blacksmith | GitHub-hosted | GitHub-hosted | one unix user on the VM |
| one runner / serialised | per-PR cancel-in-progress | n/a (parallel tree) | per-PR groups | — | — | **one job at a time per VM**, memory-gated |
| clean env | fresh hosted VM | fresh cloud agent | fresh hosted VM / lease | fresh hosted VM | fresh hosted VM | fresh clone at SHA, own `/tmp` |
| SHA-tied | done accepted only at pushed head | branch, not SHA | "prior-head CI remains prior-head" | status check | status check | `summary.json` sha |
| reaches the PR/MR | **native check** | planner only | **native check** | **native check** | **native check** | **agent pastes `result.md`** |
| blocks merge | yes (required check) | n/a | yes (`ci-gate`) | yes (required checks) | — | **no** |

Every reference treats one machine-run gate as the truth. The only one that does not put its result on the forge is ours.

---

## 3. Our current state and concrete failure modes

**State.** There is no CI. Both CI files were deleted in **#440** (AGENTS.md:144-150). The definition of done is
"`make verify-full` green on a clean tree at the MR head commit" (AGENTS.md:467). That definition names no runner
(`:470-472`), and the MR records the SHA, where the run happened, and the `deployed: <branch> @ <sha>` line (`:473-476`).

`make verify` = doctor + `gradlew check` + lint + UI tests + Playwright property + prod build (Makefile:379-389).
`make verify-full` adds `smoke FULL=1`, which deploys onto the one shared Compose stack (Makefile:394-396).

**Live GitLab state (glab api, 2026-10-02):**
- our access level is 50 (Owner)
- `shared_runners_enabled: true`
- zero project-type runners
- `only_allow_merge_if_pipeline_succeeds: false`
- no `.gitlab-ci.yml`

| # | failure | evidence | root cause |
|---|---|---|---|
| F1 | 100 pipelines, 98 failed, 0 succeeded, `ci_quota_exceeded` at 0s | AGENTS.md:145-148 (#440) | jobs went to GitLab instance runners; Free = "400 compute minutes per month" (docs, below) |
| F2 | `make verify` OOM on the VM | 00-fleet-self-reports.md:5 (developer) | ~8 GB VM shared by every agent (create-agent.sh:344-345 @080aabb); Gradle daemon `-Xmx4g` (gradle.properties:7) + IT fork `maxHeapSize = "2g"` (integration-test-conventions:34) + Testcontainers |
| F3 | unset `JAVA_HOME` / `DOCKER_HOST` / locale in agent sessions | 00-fleet-self-reports.md:5-6 | per-unix-user env. Partly fixed in agent-fleet `28979bc` (`DOCKER_HOST` → podman socket) |
| F4 | `/tmp/spring.log` owned by another user | 00-fleet-self-reports.md:6 (qa) | single-user dev tooling across several unix users (ADR 0002:5-8) |
| F5 | whole-module IT failure, "Could not connect to Ryuk" | `.claude/hooks/guard-concurrent-build.sh:4-7` ("71 tests failed … none of them real"), AGENTS.md:160-164 | concurrent IT suites on one container daemon. The hook only advises (`exit 0`, `:26`) |
| F6 | leftover postgres/redis containers | DEVELOPING.md:441-446 | rootless podman needs `TESTCONTAINERS_RYUK_DISABLED=true`, so nothing reaps the singletons |
| F7 | smoke green for code never built | DEVELOPING.md:567-575, AGENTS.md:475-479 | one Compose project, fixed ports, last-deployed-branch wins |
| F8 | "gate status unclear": early-stopped Verifier, flake list only in Discord | 00-fleet-self-reports.md:6 (qa) | Verifier result is relayed by hand; nothing on the MR is authoritative |
| F9 | hour-long gate; 5 Verifier jobs + 3 QA rounds over 2 days on #554/!230 | 00-fleet-self-reports.md:5; ADR 0002:29 (~1h45) | full `verify-full` per push, serial |

The Verifier (agent-fleet) already fixes F2–F7 *for the gate run*: one job, its own user, `/tmp`, clean clone, memory gate, and OOM notes.
What no fix touches is **F8**: the result never lands on the MR as a machine-written, merge-blocking status.
F1 is what happens if a pipeline is reintroduced while instance runners stay enabled.

---

## 4. Options

R10 (`skills/issues/19-research-claude-cloud-backend.md:18-20`) rules out a Claude cloud runner: there is no GitLab push-back from
Anthropic-hosted environments. It is not an option here.

GitLab facts used below (docs.gitlab.com):
- "The usage of instance runners by projects running CI/CD jobs is measured in compute minutes." (`/ci/pipelines/compute_minutes/`). Only instance runners are named as metered. A project runner on our own VM is outside that sentence.
- "Free tier namespaces receive 400 compute minutes per month." (same page)
- Creating a project runner: "You must have the Maintainer role for the project" (`/ci/runners/runners_scope/`). We are Owner (50).
- Shell executor: "executes builds locally on the machine where GitLab Runner is installed". Jobs run "as either the `gitlab-runner`…" user. "Generally it's unsafe to run jobs with shell executors" — a job can read other projects' code on that host (`/runner/executors/shell/`).
- `concurrent`: "Limits how many jobs can run concurrently, across all registered runners". `limit`: "`0` (default) means do not limit" (`/runner/configuration/advanced-configuration/`).
- `resource_group`: "Limit job concurrency". `interruptible`: "can be canceled when made redundant by a newer run" (`/ci/yaml/`).
- "Pipelines must succeed" blocks MRs from merging "if there is no pipeline" (`/user/project/merge_requests/auto_merge/`).
- Install: `sudo apt install gitlab-runner` after the packages.gitlab.com repo script (`/runner/install/linux-repository/`).

### Option A — keep the serialised Verifier queue on the VM; make it post its own result

The `fleet-verify` that exists today, plus one change: the slot writes `result.md` to the MR itself, and sets a commit status on the SHA
(`POST /projects/:id/statuses/:sha`). This needs a project access token held by the `fleet-verifier` user.

| | |
|---|---|
| cost | ~0. Already built and running; one token plus a post step in `write_result` (`fleet-verify:563`) |
| fixes | F2–F7 (already); F8 once the post is automatic; F9 partly (SUPERSEDED drops stale queued jobs) |
| doesn't fix | merge is not blocked without "Pipelines must succeed", and an external commit status alone may not satisfy that check (unverified); F9 throughput (~13/day serial); the Verifier is a second system beside GitLab |
| result reaches MR | Verifier posts a note + commit status at the SHA; no agent relays it |
| backed by | agent-fleet ADR 0002; firstmate "CI belongs to the forge" (`VISION.md:71`) is the gap it closes |

### Option B — self-hosted GitLab project runner on the VM, shell executor, `concurrent = 1` — **recommended**

Register a project runner on the VM as its own unix user (the existing `fleet-verifier`'s environment). Use the shell executor, set
`concurrent = 1`, and disable instance runners for the project, which is currently `shared_runners_enabled: true`.
`.gitlab-ci.yml` gets one job whose body is the existing Verifier command. That is ADR 0002's own plan: "the Verifier becomes the runner".
Mark the job `interruptible: true` so a newer push cancels a stale pipeline. Turn on "Pipelines must succeed".

| | |
|---|---|
| cost | runner install + registration (we hold the role); one small `.gitlab-ci.yml`; zero compute minutes on the stated rule. The Verifier's memory gate and OOM notes are kept only if the job calls `fleet-verify`'s logic rather than raw `make verify-full` |
| fixes | **F8** (native pipeline status at `CI_COMMIT_SHA`, merge-blocking); **F1** if instance runners are disabled; F2–F7 as A; superseded pushes via `interruptible` |
| doesn't fix | shell-executor trust (any branch's code runs as the runner user — acceptable only on a private repo with trusted pushers); F3 must be set in the runner's own `environment` (`JAVA_HOME`, `DOCKER_HOST`, `TESTCONTAINERS_RYUK_DISABLED`); F9 throughput; a VM outage = no gate |
| result reaches MR | GitLab pipeline widget on the MR, tied to the head SHA; job log + artifacts (`result.md`, report) on the pipeline |
| backed by | firstmate (`VISION.md:71`, `architecture.md:404 @5f2b81b`), openclaw (`scripts/AGENTS.md:30` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d]), addy (`ci-cd…/SKILL.md:305`), humanlayer (`main.yml:93,167`), retro (`SKILL.md:18`) |

### Option C — laptop as runner

Either register a runner on the operator's Mac, or keep today's rule: the MR author runs `make verify-full` and pastes the evidence (AGENTS.md:470-476).

| | |
|---|---|
| cost | zero |
| fixes | F2 if the laptop has more memory than the VM's ~8 GB (not measured here); F3/F4 (one user) |
| doesn't fix | laptop asleep or offline = no gate; contends with the operator's own worktrees on the one shared Compose stack (F5, F7); VM agents cannot use it unattended; F8 stays manual if pasting |
| result reaches MR | runner: pipeline status. Pasting: a hand-written note (today's F8) |
| backed by | humanlayer pre-push `make check test` (`Makefile:114`); our own §Done means (AGENTS.md:470) |

**Recommendation: B.** It is A plus the one thing every reference has and we lack: the forge records the result at the SHA and blocks merge on it.
B's job runs A's Verifier, so nothing already built is thrown away. Do it in this order:
1. Disable instance runners first, or F1 repeats.
2. Register the runner.
3. Enable "Pipelines must succeed" last.

---

## 5. Developer-before-QA minimum the references converge on

```
 developer (own checkout, cheap)            one gate (one place, at the SHA)            QA
 ─────────────────────────────────          ────────────────────────────────           ────
 targeted tests for what changed      push   full suite on a clean checkout     PASS @  review +
 + lint/typecheck of touched code    ─────►  of that exact commit, serialised  ─────►  judgement
 + self-report: what ran, what didn't        result posted to the MR by the            (not re-running
   (never "green" without a SHA)             gate itself                                the full suite)
```

| step | ours | backed by |
|---|---|---|
| targeted tests on touched modules | `make test-module` / `make it-module MOD=… TEST=…` | agent-fleet `create-agent.sh:361-362 @080aabb`; openclaw `AGENTS.md:91` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d]; firstmate `test` step |
| fast whole-repo checks | `make verify-fast` (units + lint + UI units, no ITs, no smoke) | humanlayer pre-push `Makefile:114`; addy `SKILL.md:178` |
| evidence level stated honestly | what ran, what did not, and "blocked" rather than a thinner pass | pstack `worker.md:55`, `verifier.md:26` |
| push, then hand to the one gate | Verifier / runner at the MR head | firstmate `fm-dod-lib.sh:599 @5f2b81b`; ADR 0002:31 |
| "green" always names a result and a SHA | — | `create-agent.sh:373 @080aabb`; openclaw `AGENTS.md:38` [drift 2026-10-17: cited lines rewritten at d8faf8876, see research/64d] |

The developer does not run `verify-full` or `smoke` on the shared VM. That is already DEVELOPING.md:567 ("Give unattended agents `make verify-fast`").
QA starts after a PASS at the head SHA, not before.
