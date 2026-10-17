# 66 · Gate scope — run only what a change needs, re-run the failed job, retry flakes (G29 · chiyanram/skills#105)

Read-only research, 2026-10-17. Quotes ≤15 words. Web pages carry no date unless stated; "read 2026-10-17" = fetched today.

| tag | source | pin |
|---|---|---|
| [oc] | openclaw/openclaw | clone `b94e5177`; reversal commit `299d289e9` via `gh api` |
| [forge] | rameezk/forge | clone `origin/main 57f3619` |
| [fm] | kunchenguid/firstmate | clone `549e07f` |
| [ps] | cursor/plugins pstack | clone `2eb7ed4`, `pstack/skills/poteto-mode/playbooks/orchestrate.md` |
| [ap] | agent-platform | `71b5deb4` (this worktree) |
| [af] | agent-fleet | `~/workspace/agent-fleet @ 3ba7883` |

## 1 · Re-run mechanics

### GitHub Actions — https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs (read 2026-10-17)

| action | what runs | status at the SHA |
|---|---|---|
| Re-run all jobs | whole run | new attempt; "Latest" dropdown keeps earlier attempts |
| Re-run failed jobs (`gh run rerun --failed`) | failed jobs + dependents (REST endpoint `rerun-failed-jobs`; dependents per GHES 3.8 page) | same run, new attempt |
| Re-run one job (`gh run rerun --job`) | "a new workflow run will start for the job and any dependents" (GHES 3.8 page) | other jobs' outputs and artifacts reused |

- Re-runs keep the original `GITHUB_SHA` / `GITHUB_REF`; limit 30 days, max 50 attempts.
- Required checks: "Required checks must pass on the latest commit SHA." — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks (read 2026-10-17).
- **Skip semantics (same page):** a job skipped by `if:` — "The job reports "Success"." A workflow skipped by path/branch filter — checks "stay in a "Pending" state and block merging"; advice: "Avoid requiring workflows that can be skipped."
- Merge queue: "creates temporary branches with a special prefix to validate pull request changes"; workflows must listen on `merge_group` or the required check never reports — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue (read 2026-10-17).

### GitLab CI — https://docs.gitlab.com/ci/yaml/ · /ci/jobs/ · /user/project/merge_requests/auto_merge/ (read 2026-10-17)

| keyword / action | behaviour | effect on pipeline status at the SHA |
|---|---|---|
| retry one job (UI/API) | allowed "regardless of its final state"; "A new job instance is created with a new job ID" | later skipped jobs are reassigned and run; status recompute not documented (**not found**) |
| retry all failed | "retry all of them at once" | same pipeline, same SHA |
| `retry:max` | `0` (default), `1`, or `2` | automatic, inside the job |
| `retry:when` | `always` (default), `unknown_failure`, `script_failure`, `runner_system_failure`, … ; `retry:exit_codes` narrows further | a retried-then-passed job is green; no flaky mark (**not found**) |
| `needs:` | DAG — "run some jobs without waiting for others to complete" | failure semantics of a needed job: **not found** on that page |
| `rules:changes` | MR pipeline compares to target branch; new branch: "always evaluates to true and the job always runs"; `compare_to` sets the ref | job absent = not in pipeline at all |
| `when: manual` | `allow_failure` defaults `true`; inside `rules` defaults `false`; `allow_failure: false` makes it **blocking** | un-run manual job does not block dependents |
| `allow_failure: true` | failed job shows orange warning, yet "the pipeline is successful" and the commit "marked as passed" | **pass at the SHA despite a red job** |
| `interruptible` | auto-cancel redundant pipelines; deploy jobs "usually shouldn't be canceled" | older pipeline canceled |
| Pipelines must succeed | "requires the existence of a successful pipeline"; MR pipelines take priority | separate checkbox "Skipped pipelines are considered successful", else skipped blocks merge |

## 2 · Scoped test selection in industry — what and why

| technique | how it scopes | why (source's own) | source |
|---|---|---|---|
| path-based job rules | `rules:changes` / workflow `paths:` | run jobs only when files change; GitHub warns this breaks required checks | GitLab yaml; GH troubleshooting page above |
| Nx affected | git diff base..head → project graph → **plus dependents** | "only runs tasks on those affected projects"; set base to last green `main` | https://nx.dev/docs/features/ci-features/affected (read 2026-10-17) |
| Gradle build cache | skip a task "when it is determined that inputs have not changed" → `FROM-CACHE` | "save time by reusing outputs produced by other builds" | https://docs.gradle.org/current/userguide/build_cache.html (Gradle 9.8.1, read 2026-10-17) |
| Bazel | per-target caching; `flaky` attr reruns | (see §3) | https://bazel.build/reference/be/common-definitions |
| Test impact analysis | call-graph map from test → code | speeds the test phase; caveats: map costly, misses non-code inputs, new tests uncovered; teams keep a nightly full run | Paul Hammant, https://martinfowler.com/articles/rise-test-impact-analysis.html (2017-08-07, rev. 08-22) |
| Google TAP pre/post-submit | presubmit "gates submission"; post-submit decides release readiness | scale: "unable to regression test each code change individually" | testing.googleblog.com 2016-05-27 (Micco); ICSE '17 "Taming Google-Scale Continuous Testing" https://research.google/pubs/taming-google-scale-continuous-testing/ |
| merge queue full run | full required checks on base + PRs ahead | each PR validated against what will actually land | GH merge-queue page above |

Pattern across all: **narrow before merge, broad at one place that is the truth (post-submit / queue / main CI)**. None found that skips the broad run entirely.

## 3 · Flake policy — retry, quarantine, fail; and how flakes stay visible

| system | mechanism | does a flake stay visible? | source |
|---|---|---|---|
| Google | presubmit can "re-run only failing tests" + auto re-run; a tool "automatically quarantines the test" when flakiness is too high | measured: ~1.5% of runs flaky, ~16% of tests have some flakiness, ~84% of pass→fail transitions involve a flaky test; staff reply: rerun only for tests "marked as flaky or when users specifically request" | https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html (2016-05-27) |
| Playwright | `retries` (off by default); outcome classes passed / **flaky** ("failed on the first run, but passed when retried") / failed; worker discarded on failure | yes — own category; `failOnFlakyTests` "exit with an error if any tests are marked as flaky" (v1.52) | https://playwright.dev/docs/test-retries · /docs/api/class-testconfig (read 2026-10-17) |
| Gradle test-retry plugin | `maxRetries` (default 0), `maxFailures` stops retrying on systemic break, `failOnPassedAfterRetry` (default false) | Develocity marks failed-then-passed as "flaky" | https://github.com/gradle/test-retry-gradle-plugin (read 2026-10-17) |
| Bazel | `flaky = True`: "executes the test up to three times", fails only if every run fails | FLAKY reporting not stated on that page (**not found**) | bazel.build common-definitions |
| GitLab | `retry:` + `when:` | no flaky mark found in the yaml/jobs docs (**not found**) | §1 |
| GitHub Actions | re-run failed jobs | no native flaky-test report **found** | §1 |
| [oc] | no retries to hide failures; manual **FRV flake classification** workflow records a flake decision: exact failed job URL + tracking issue on `main` + 20–300-char reason | yes — a record with an owner | `AGENTS.md:88 @ b94e5177`; `.github/workflows/full-release-flake-classification.yml:1-30 @ b94e5177` |

[oc] rule text: "conceal failures with retries, longer timeouts, weaker assertions" is banned (`AGENTS.md:88`); "Reruns do not clear a red `main`" (`:89`); pre-existing reds on files a PR does not touch may land, named in the PR (`:92`).

## 4 · What our references do, and WHY

| ref | rule | stated why | cite |
|---|---|---|---|
| [oc] | "**PR CI is the default broad proof.**" Pre-PR: touched tests + targeted typecheck/lint/format; "Never rerun or re-push just for green" | measured 2026-10-07..11 over 1,892 Codex lanes: "only 33% of 3,133 box runs exited 0", 1,040 lane-hours, PR CI ~9 min | `AGENTS.md:86 @ 299d289e9`; commit body `299d289e9` (2026-10-12) |
| [oc] | **reversal**: before, "CI is expensive; do not spend it on proof." | — the old rule, replaced on the numbers above | `AGENTS.md:91 @ b94e5177` |
| [oc] | PR CI itself is scoped: a changed-lanes manifest picks lanes; full `main` CI hourly, pushes to `main` run only `security-fast` | not stated in file | `.github/workflows/ci.yml:180-191,762 @ b94e5177` (`scripts/changed-lanes.mts`); `AGENTS.md:90` |
| [forge] | ADR-0064: agents run "only the commands for the areas they touched"; report ends "full suite: CI"; a required scoped command that cannot run → stop, never substitute | full check OOM-killed on 3.7 GB box, slow on Mac; workers already fell back and "mentioned it only in passing" | `docs/adr/0064-…md:9,12,17 @ 57f3619`; `AGENTS.md:29-42` |
| [forge] | ADR-0065: done = ready PR + every required check green, **read by forge** via GitHub's required-check flag | before: draft or red PR counted done; forge "does not take the agent's word for it" | `docs/adr/0065-…md:9,18,22 @ 57f3619` |
| [forge] | consequence accepted: failures outside touched areas "surface only in CI, after a push" | — | `0064:21` |
| [fm] | local no-mistakes Test "stays intent-targeted"; `--changed` is the normal path; `--all` is "deliberate full regression only"; "CI owns broad regression" across shards; new head cancels PR CI | gate attestation binds to the PR head SHA, stale or skipped step fails | `CONTRIBUTING.md:12-13,94,106,113,129-131 @ 549e07f` |
| [ps] | "Scale verification to the unit"; a verifier only rerunning one command "is ceremony, not verification" | cost scales to blast radius | `orchestrate.md:87 @ 2eb7ed4` |
| [ps] | ledger keyed PR + head SHA; "CI green is an input to a verdict, not a verdict"; `verifier-blocked` is not a pass; "A new head SHA voids the row" | — | `orchestrate.md:89` |
| [ps] | "retries, CI flake triage" never reach the human | spend the human only on irreversible/product calls | `orchestrate.md:107` |

Shared shape: **touched/intent-scoped locally → broad on one shared runner → done read at the head SHA by a machine, not claimed.** forge and oc both name the evidence line ("full suite: CI", "report unrun checks").

## 5 · Our facts

| fact | value | cite |
|---|---|---|
| Done means | `make verify-full` green on a clean tree at the MR head, smoke 0 failed, evidence in the MR | AGENTS.md §Done means @ 71b5deb4 |
| `verify-full` shape | one serial chain: `verify` then `smoke FULL=1`; "a verify failure means nothing was deployed" | `Makefile:391-396` |
| `verify` | doctor, `gradlew check` (units + ITs together), npm ci, lint, UI units, property, prod build | `Makefile:379-389` |
| `verify-fast` | units + lint + UI units, `-x integrationTest`, no smoke | `Makefile:367-374` |
| per-module | `test-module` / `it-module` / `verify-module MOD=` | `Makefile:197,204,215` |
| smoke tiers | core = `@core` tag, workers 1, **retries 0**; full = workers 2, `llm` project 1 worker, **retries 1** | `aruvii-ui/playwright.core.config.ts:32,39-40`; `playwright.smoke.config.ts:41,49,79-80` |
| full-smoke retry why | CPU Ollama degrades; a retried test "is reported as "flaky", not "passed"" | `playwright.smoke.config.ts:42-48` |
| where 61 min goes | smoke FULL 24m33 (40%); Gradle 21m40 of which one serial IT task (790 tests) 18m50; deploy ~10m | research/38 §"Where the 61 minutes go" (job `133306-d28641`, 2026-10-02) |
| IT serialism | `maxParallelForks = 1` | `build-logic/.../aruvii.integration-test-conventions.gradle.kts:30` |
| flake list | lived **only in Discord**; gate read "FAIL, only known flakes" (#554 — flaky smoke-69 T1 + `CustomPiiEndpointClientTest`, its MR !230) | research/39 row 2026-09-30 |
| workers 3–4 | flaked from API/DB host strain, not Ollama (E7/#38) | research/39 row 2026-07-25; `playwright.smoke.config.ts:36` |
| side tier | #440 (CI files deleted, 98/100 pipelines failed on quota) lesson: a failing signal that gates nothing; Q27 puts real-Ollama in a nightly tier with no runner/owner yet | research/39 rows 09-12, 10-02; §Q27 cons |
| decided (Q26) | runner on VM, `concurrent=1`, job = the Verifier; dev minimum = touched-module tests + `verify-fast` + what-ran note | research/39 row 2026-10-02 |
| Verifier today | one fleet-configured `command`, one job at a time, PASS iff exit 0; no partial re-run, no retry; newer queued job of a branch → SUPERSEDED | `af verifier/fleet-verify:5-15,515-520` |
| Verifier flake record | parses Playwright JSON, counts `flaky` per suite into `result.md` — visible but not gating | `fleet-verify:395-424,555,569-572` |
| which command the VM runs | **not found** in the repo (config lives in `/etc/fleet-verify`, absent here); research/37 says `verify-full` | research/37:132 |
| lanes | quick / standard / full + floor decided (G8, #35 Q24), lands in `/crq` stage 1 via W1 #645 | `00-decision-register.md:40`; **not yet** in `.agents/skills/crq/SKILL.md @ 71b5deb4` |

What this means: today any failure anywhere re-runs **~61 min** (no job split), the one retry lives only in full smoke, and the flake record is a count in `result.md` plus Discord.

## Options for us

### (a) Job split

| option | pros | cons | source |
|---|---|---|---|
| A1 keep one job = `verify-full` | one PASS at the SHA, nothing to reconcile | any red re-runs 61 min; smoke can't start until ITs end | af `fleet-verify:515`; R29 |
| A2 split into jobs with `needs:` — `unit+lint` · `it` (per module group) · `deploy→smoke-core` · `smoke-full`; retry one job | re-run only the red job (GitLab single-job retry, same SHA); 18m50 IT task can shard across modules | shared Compose stack means smoke jobs still serial; Verifier is one-job-at-a-time, so the split needs the runner (Q26) or Verifier support | GitLab yaml `needs`; GH re-run failed jobs; oc lanes `ci.yml:762` |
| A3 split inside the Verifier only (stages + resume from failed stage) | no GitLab dependency | rebuilds GitLab retry ourselves; second system beside the forge (research/37 Option A con) | research/37:193-202 |

One line: A2 — it is the forge's own retry, and it attacks the 61 min.

### (b) Scope per lane (quick / standard / full / floor)

| option | pros | cons | source |
|---|---|---|---|
| B1 every lane runs the full gate at the SHA; lanes differ only in pre-push work | one meaning of done; no skip semantics | quick lane pays ~1 h per push | AGENTS.md §Done; research/39 Q26 con |
| B2 path/module-scoped jobs (`rules:changes` + dependents, Nx-style) for quick/standard; full only for full lane + merge | cheap for docs/skill-only changes | "touched module" misses dependents' ITs (5 jobs on #554/!230); GitHub warns skipped required workflows; new-branch `changes` = always true | research/39 Q26 cons; GH troubleshooting; GitLab yaml; Nx |
| B3 floor = fixed always-on set (unit+lint+`smoke:core`) on every push; full gate on the MR head before merge (oc/forge shape) | matches oc 299d289e9 + forge ADR-0064 + fm; floor is never skipped | broad failures surface late, after push (forge 0064:21) | oc, forge, fm §4 |

One line: B3 — floor everywhere, full once at the head, scope only what's above the floor.

### (c) Re-run + retry + flake record

| option | pros | cons | source |
|---|---|---|---|
| C1 no auto-retry; manual single-job retry; flakes recorded as an in-repo file/issue with failed-job URL + owner + reason | nothing hidden; record survives fresh workers | manual cost per flake | oc AGENTS.md:88, FRV workflow; research/39 (flake list in Discord) |
| C2 keep Playwright `retries: 1` (full only) + `retry:when: runner_system_failure` on jobs; gate fails on *new* flakes only, counts reported per run | absorbs CPU-Ollama noise; flake stays its own category | a flake becomes "green" unless counted against a list; `failOnFlakyTests` would turn every one red | Playwright retries + failOnFlakyTests; GitLab `retry:when`; `fleet-verify:395-424` |
| C3 quarantine tag (`@quarantine`) out of the gate into a tier that files/updates an issue | gate can PASS honestly; Google precedent | a tier that gates nothing = #440 pattern unless it has an owner | Google 2016 blog; research/39 Q27 cons |

One line: C2 + C1's record — retry the known env noise, but every flake lands in a repo-tracked record.

### (d) What "done at a SHA" means when jobs are skipped

| option | pros | cons | source |
|---|---|---|---|
| D1 done = every job of the lane's declared set PASS at the head SHA; skip allowed only as `skip: <reason>` in the lane | explicit, matches register "skipped stage = `skip: <reason>`" | needs the lane set written down per lane | `00-decision-register.md:40` |
| D2 done = forge's own check green (Pipelines must succeed), skipped/`allow_failure` counted as GitLab counts them | machine-read, forge ADR-0065 shape | `allow_failure` red still = "passed"; "Skipped pipelines are considered successful" is a checkbox — a silent false pass | GitLab yaml/auto_merge; forge 0065:18 |
| D3 done = pstack ledger verdict at (MR, head SHA), CI one input | separates "green" from "verified"; new SHA voids | another record beside the forge | ps orchestrate.md:89 |

One line: D1 enforced by D2 — no `allow_failure` and no skipped-pipeline checkbox on gate jobs.
