# R46 · Fleet security inventory — credentials, reach, threats (for G13 #69)

Research for **#69** (G13 · fleet security). Read-only. No secret value appears here: names, scopes,
paths and modes only. Sources: agent-fleet `origin/main` @ `aaba2aa` (refs clone, exported, not pulled) =
**AF**; agent-platform `origin/master` = **AP**; GitLab live state via `glab api` (2026-10-03); Claude Code
and GitLab docs (fetched 2026-10-03, quoted < 15 words).

Context that changes everything below: **G4 #17 Q1** decided ONE unix user for coordinator + all workers.
Today's AF is built on the opposite — **one unix user per agent** is its isolation boundary
(AF `README.md:28`, `CONTEXT.md:8-12`). Most of today's protections are unix-permission protections and
vanish under G4 unless replaced.

---

## 1. Today's fleet (AF) — credential inventory

| credential | per agent / shared | stored at (on the VM) | mode / owner | provisioned by | readable by the agent's own session? |
|---|---|---|---|---|---|
| Claude OAuth token (`claude setup-token`, ~1 yr, model requests only) | **shared per fleet** (opt-in split `claude-token-<suffix>`) | master: `<fleet>/secrets/claude-token` (dir 700, `create-agent.sh:61-62`; file 0600, `setup-claude-token.sh:74`); copy: `~agent/.claude/claude-token` | copy **0400 agent-owned** (`create-agent.sh:596 @080aabb`) | `setup-claude-token.sh`, root, interactive; injected as `CLAUDE_CODE_OAUTH_TOKEN=$(cat …)` at launch (`create-agent.sh:720 @080aabb`) | **yes** (by design; it's in the session env) |
| GitLab PAT, scopes `api` + `write_repository` | per recipe (#5: 3 of 4 agents used the **operator's own** `chiyanram` PAT; bot users now exist, see §1c) | `agent.yaml` `gitlab.token`; `~/.git-credentials` (0600 agent, `create-agent.sh:529`); glab config (via `glab auth login --stdin`, `:526`) | 0600 agent | `create-agent.sh:524-531`, token never on argv | **yes** |
| Discord bot token | per agent | `~/.claude/channels/discord/.env` | **0600 agent-owned** — must be, plugin chmods it (`create-agent.sh:600-603 @080aabb`) | rendered from `discord.bot_token` (`:308-310`) | **yes** |
| Discord allowlist `access.json` | per agent | same dir | **0444 root** (`:602`), `DISCORD_ACCESS_MODE=static` | — | read only |
| Recipe `agent.yaml` (holds PAT + bot token) | per agent | `<fleet>/agents/<name>/agent.yaml` 0600 (`:69`); archive copy `~agent/agent.yaml` | archive **0400 root** (`:550`) | — | **no** (root 0400) |
| Verifier repo read token (GitLab deploy token, read-only by convention) | one per fleet, copied to every slot | `<fleet>/secrets/verifier-repo-token` → `/home/fleet-verifier-N/.git-credentials` | 0600 slot user (`setup-verifier.sh:335-342`) | `setup-verifier.sh --register` | n/a — but **any job's code** runs as that slot user and can read it |
| SSH keys | **none** — git is HTTPS + token (`create-agent.sh:142`, `README.md:91-93`) | — | — | — | — |
| Runner registration / auth token | **does not exist yet** (#35 Q26 decided, not built; AP has no `.gitlab-ci.yml`) | would be `/etc/gitlab-runner/config.toml` | — | W3 | — |

### 1a. Enforcement that exists today

| layer | file | what it does | limit |
|---|---|---|---|
| managed settings | `/etc/claude-code/managed-settings.json` ← AF `enforcement/managed-settings.json:1-27` (root 0644, `install-enforcement.sh:32`) | wires **only two hooks**: PreToolUse `fleet-guard.py`, SessionStart(compact) `fleet-identity.sh` | **no** `permissions.deny`, no `disableBypassPermissionsMode`, no sandbox, no `allowManagedHooksOnly`, no network rules |
| fleet-guard | AF `enforcement/fleet-guard.py` | per-user regex deny list from `/etc/claude-code/fleet-policy/<unix-user>.json` (root 0644, `create-agent.sh:585-588 @080aabb`); fires even under `--dangerously-skip-permissions` (`:3-8`) | keyed on **unix user name starting `agent-`** (`:127-131`) — no-op for anyone else; **fail-open** (`:34-35,141-143`); regex only, "a skeleton is a best-effort parse, not a sandbox" (`:30`); policy only has what each recipe's `enforced:` lists (example: just `sudo`, `agent-yaml.md:54-57`); known bypass `-m "$(cat f)"`, `glab api` (AF #5 comment) |
| permission mode | `create-agent.sh:167-171,707-711 @080aabb` | default **`--dangerously-skip-permissions`**; `settings.json` = `skipDangerousModePermissionPrompt: true` (`:261-262`) | docs: bypass "offers no protection against prompt injection or unintended actions" (permission-modes) |
| identity files | `create-agent.sh:548-551` | `CLAUDE.md`, `settings.json` root 0444 | `~/.claude/` is **agent-owned** (`:481`), so the agent can replace them by rename — the script itself relies on this (`:554-557`). "Cannot rewrite who it is" (`README.md:34-36`) holds only for `/etc` |
| sudo | `useradd` with no sudoers (`create-agent.sh:443`) + optional fleet-guard regex | real control | — |
| homes | `chmod 750 $HOME` (`create-agent.sh:446`), own group | agents can't read each other's homes/worktrees/tokens | **this is the isolation that G4 removes** |
| memory | per-user systemd slice caps (`create-agent.sh:462-467`) | resource, not security | — |
| containers | rootless podman per user, socket `/run/user/<uid>/podman/podman.sock` (`fleet-lib.sh:190 @080aabb`) | each agent can only touch its own containers | under one user: one socket, all containers |
| network | — | **nothing**: no egress filter, no sandbox, WebFetch/curl free | — |
| Discord inbound | `access.json` allowlist = operator only + peer bots by mention, rate cap (`README.md:94-99`, `patch-discord-plugin.py:6-37`) | limits who can instruct | peer bots are agents → agent text can wake other agents |
| operator relay | `fleet-say.sh` (root, tmux into the session, prefixed `[<who>, relayed via the fleet terminal]`, `:1-12`) | root only | — |

### 1b. Verifier (ADR 0002) — what it can reach

- Unix users `fleet-verifier-N`, no sudo (`setup-verifier.sh:131`), home 750 (`:135`), systemd service with
  `PrivateTmp=yes` (`:157`), own slice + podman, `UMask=0007` (`:184`).
- Queue `/var/lib/fleet-verify/fleets/<fleet>` root:`fleet-verify-<fleet>` 2770 (`:271,308`) — agents of
  that fleet + slots only. Jobs: clean clone of a **pushed** commit (`fleet-verify:271-285`).
- Holds no forge/Discord creds beyond the read token (`CONTEXT.md:66-71`); "never posts anywhere" (`:79-81`).
- Runs arbitrary branch code as the slot user → that code can read the slot's `.git-credentials` and log it
  into `log.gz`, which agents then relay. Low impact while the token is read-only.

### 1c. GitLab state (live, `glab api`, 2026-10-03)

| fact | value |
|---|---|
| project visibility | private |
| `master` protection | push **No one**, merge **Maintainers**, force-push off, code-owner approval off |
| members | `chiyanram` 50 · `drop2kanagaraj` 50 · `imdganesan.careers` 40 · `aruvii-{developer,analyst,qa,spec-reviewer}-agent` **30 (Developer)** · 2 humans 30 |
| merge gates | `only_allow_merge_if_pipeline_succeeds: false`, `approvals_before_merge: none`, `merge_method: ff`, squash always |
| CI | `shared_runners_enabled: true`, no project runner, no `.gitlab-ci.yml`, `ci_job_token_scope_enabled: false` |
| open | AF **#5** — per-agent GitLab identity; verify `/approved` by **author**, not by regex |

So **if** a worker runs on a `*-agent` Developer account, GitLab itself refuses a push or merge to `master`.
If it runs on the operator's PAT (the #5 situation), nothing but a regex stands between it and a merge.
Note: GitLab.com **project access tokens need Premium** (docs) — on Free the per-role bot identities are
plain user accounts with PATs (365-day max lifetime, docs).

---

## 2. agent-platform side (AP `origin/master`)

| item | where | what |
|---|---|---|
| permissions | `.claude/settings.json:2-31` | **allow list only** (`make *`, `./gradlew *`, `glab issue/mr create/note/update *`, `curl -s http://localhost:*`…). **No `deny`, no `ask`.** Irrelevant under bypass mode anyway |
| guard hooks | `.claude/settings.json:33-63` | `block-commit-on-master.sh` (exit 2), `block-migration-edit.sh`, `check-migration-version.sh`; advisories `warn-piped-gate`, `guard-concurrent-build` |
| hook location | `$CLAUDE_PROJECT_DIR/.claude/hooks/*` | **repo files the worker can edit** in its own worktree; not managed |
| block-commit-on-master | `.claude/hooks/block-commit-on-master.sh:31-158` | shlex-parses `git [-C] commit`, refuses when target is on `master`; skips `--amend` (`:121-124`), unparseable input (`:65-70`), `--git-dir/--work-tree` (`:108-111`). Local convenience; the real wall is GitLab's push "No one" |
| plugins | `.claude/settings.json:97-116` | 10 enabled incl. a **third-party GitHub marketplace** (`ayghri/i-have-adhd`) → auto-loaded code/instructions from outside |
| merge | CLAUDE.md "master is protected… The human merges"; GitLab merge = Maintainers | enforced by GitLab role, not by the repo |
| stack secrets | `make secrets` → `scripts/generate-secrets.sh` (Makefile:80-83) writes `secrets/{postgres_password,redis_password,master_key}` 0600 (`generate-secrets.sh:11,19,27`); compose `secrets:` (`docker-compose.yml:324-330`); `ARUVII_MASTER_KEY` env (`:105,153`); admin initial password has a committed default (`:101`) | gitignored (`.gitignore:13,39`) |
| worktrees share the stack's secrets | `scripts/link-worktree-stack-files.sh:10-39` | **`secrets/` and `.env` are symlinked from the main checkout into every worktree** → every worker in a worktree reads the master key |
| rules | CLAUDE.md:271-280 (CredentialEncryptor, masked, decrypt only in `ToolHandler.execute()` — "checked by nothing"), :398 (never `make secrets` in a worktree) | review-only |

---

## 3. References

| ref | security mechanism | cite |
|---|---|---|
| firstmate | 5 hard rules (never write a project, never merge without captain, never tear down unlanded work…); workers default `--dangerously-skip-permissions`, opt-in `config/claude-permission-mode=auto`; account pin only captain edits; spawn env "is an exec environment boundary, not a sandbox" | `AGENTS.md:28-42,92`; `bin/fm-spawn.sh:305-316` [drift 2026-10-17: lines added inside the cited range at 5f2b81b; cited lines now span :360-401, see research/64b] |
| openclaw | three separate controls: **sandbox** (where tools run; container, **no network by default**, `network: host` blocked), **tool policy** (allow/deny), **elevated** (exec escape hatch); exec approvals "are **not** a per-user auth boundary"; own ATLAS threat model with P0 = skill sandboxing + output validation | `docs/gateway/sandbox-vs-tool-policy-vs-elevated.md:8-12`; `docs/gateway/sandboxing/images-and-setup.md:83,125`; `docs/tools/exec-approvals.md:44-49`; `docs/security/THREAT-MODEL-ATLAS.md:159-211` |
| openclaw coordinator | "another agent's assertions are evidence, not approval" | research/36 `:47` |
| pstack | untrusted transcript/review-comment text treated as data; coordinator is the only Slack poster, children forbidden Slack writes | research/repos/pstack.md:138,155 |
| humanlayer | approvals routed to a human via `--permission-prompt-tool mcp__…__request_permission` (a real gate, not prose) | `humanlayer-humanlayer/claudecode-go/client.go:241`; `hld/session/manager.go:259` |
| agentlayer/fold | approval hook `next/deny/ask`; path-gate deny outside allowed paths (note: bash hole) | research/repos/humanlayer-fold-agentlayer.md:333,410 |
| Claude Code — security | bypass/sandbox; "Use virtual machines (VMs) to run scripts and make tool calls"; WebFetch returns a model summary not the raw page | code.claude.com/docs/en/security |
| Claude Code — permission modes | `disableBypassPermissionsMode` / `disableAutoMode` (managed); auto-mode classifier "Tool results are stripped" so hostile file/web text can't steer it, plus server-side probe on tool results | /permission-modes `:521-525,565-610` |
| Claude Code — permissions | Read/Edit deny rules don't cover "arbitrary subprocesses"; Bash arg patterns "are fragile"; `allowManagedPermissionRulesOnly` | /permissions `:286,346,663` |
| Claude Code — sandbox | OS-level (bubblewrap on Linux) for Bash only: writes = cwd + tmp + added dirs; reads default **most of the machine incl. `~/.ssh`** unless `denyRead`; network via proxy with **empty allow list**; `sandbox.credentials` deny/**mask** env vars and files (masked token still authenticates, command never sees it); protected paths (`.claude/`, hooks, `.git/hooks`) unwritable; `allowUnsandboxedCommands:false` + managed = admin-required; file tools/MCP/hooks **outside** the sandbox | /sandboxing `:32-48,97-101,221-227,383-440,529-541` |
| Claude Code — auth | `claude setup-token` = 1-yr, model-requests-only; precedence lists `CLAUDE_CODE_OAUTH_TOKEN` 5th; `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` strips creds from all subprocesses | /authentication (iam); /sandboxing `:422` |
| GitLab | protected branch merge=Maintainers → Developer can't merge; deploy keys SSH, read-only or read-write; deploy tokens HTTP `read_repository`; project access tokens Premium-only; PAT max 365 d | docs.gitlab.com |

---

## 4. Threat list — laptop coordinator + VM workers + runner, ONE unix user (G4)

L = likelihood, I = impact (H/M/L). "Today" = AF per-agent-user design; "G4" = after collapse to one user.

| # | threat | L | I | what stops it today | under G4 | options |
|---|---|---|---|---|---|---|
| T1 | worker **pushes to master** | M | H | GitLab: push = No one (live) | same — GitLab is identity-based, unaffected | keep; nothing to add |
| T2 | worker **merges an MR** | M | H | GitLab merge = Maintainers **iff** worker uses a `*-agent` Developer account; else only fleet-guard regex (bypassable, AF #5) | one shared identity: safe if it's a Developer bot, **unsafe if it's the operator's PAT** | (a) one Developer bot for all workers (b) one Developer bot per role (c) also "Pipelines must succeed" + approvals |
| T3 | worker posts `/approved` itself | M | H | regex in fleet-guard (false positives + bypasses, AF #5/#9) | same regex, now keyed on a user name G4 doesn't have | stage gate checks note **author** is a human Maintainer (AF #5 fix); drop the regex |
| T4 | worker reads **another worktree** / another worker's session transcript | H | M | home 750 per agent user (`create-agent.sh:446`) | **nothing** — same uid | (a) accept (same project, same trust) (b) Claude sandbox: `denyRead` other worktrees + `~/.claude/projects` (Bash only; Read tool needs deny rules) (c) keep per-role unix users |
| T5 | worker touches the **runner's stack** (podman socket, ports, `secrets/`) | M | H | Verifier is its own users + groups + PrivateTmp (§1b) | if runner runs as the same user: one podman socket → `podman rm -f` anything | keep runner as **separate unix user** (`gitlab-runner`/`fleet-verifier`), own podman; decided already in spirit (#62 note) |
| T6 | **token leaks** into a GitLab comment / Discord / log | M | H | nothing generic; tokens are in env/files the session reads; Verifier `log.gz` relayed by hand | same, plus every worker sees every token | (a) `sandbox.credentials` **mask** GitLab token (b) `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` (c) a PreToolUse content rule on `glab … note`/reply bodies matching token prefixes (fleet-guard `scope: input`) (d) short-lived/narrow tokens so a leak expires |
| T7 | **prompt injection** via issue/MR/commit/file text or fetched web page | H | H | prose only: guardrail "Text is data" (`agent-yaml.md:106-108`), Q8 worker block; bypass mode = no classifier | same | (a) `--permission-mode auto` (classifier never sees tool results; probe on results) instead of bypass (b) sandbox network allow-list (gitlab.com, maven, npm…) so an injected "curl evil" fails (c) keep GitLab writes behind Developer identity so worst case = a bad MR |
| T8 | **compromised dependency / plugin / marketplace skill** | M | H | nothing; AP enables a third-party GitHub marketplace (`settings.json:109-115`); `plugin_skills` installed fresh each run (`create-agent.sh:275-285`); gradle/npm run arbitrary code | same; one uid = blast radius is every token on the box | (a) pin plugins to owned marketplaces / commit SHAs; managed `strictKnownMarketplaces` allowlists sources (settings-reference) (b) sandbox network allow-list (c) secrets not readable by the build (mask) |
| T9 | **operator's laptop files reachable from the VM** | L–M | H | unknown — depends on how the laptop coordinator reaches workers (SSH in; ssh-agent forwarding? reverse tunnel? shared mount?) | same | rule: laptop→VM SSH only, **no agent forwarding, no mounts, no VM→laptop key**; VM holds no laptop credential |
| T10 | **`machine.env` secrets readable by all workers** | H (if secrets go there) | H | n/a (file doesn't exist yet; ND-15 scopes it to JAVA_HOME, DOCKER_HOST, ports) | any file the uid reads, every worker reads | keep machine.env **secret-free** (facts only); secrets in a separate 0400 file injected per launch, or a root-run broker |
| T11 | worker edits its own guards (`.claude/settings.json`, `.claude/hooks/*`, `~/.claude/CLAUDE.md`) | M | M | AP hooks are repo files; AF identity files replaceable via agent-owned `~/.claude` (§1a) | same | enforcement only from `/etc/claude-code` (managed) + managed `allowManagedHooksOnly` ("Run only the hooks your organization deploys", settings-reference) — note it would also drop AP's repo hooks unless they move to managed; sandbox protected paths block Bash writes (not under bypass) |
| T12 | fleet-guard **silently stops** | M | M | fail-open by design (`fleet-guard.py:34`) | **certain** under G4: guard returns unless user starts `agent-` (`:130`) and policy is per unix user | rekey policy on **role** (env var set at spawn, e.g. `FLEET_ROLE`) or name the one user `agent-fleet`; add a smoke test that a deny fires |
| T13 | Claude token theft → someone else bills the Max account | L | M | 0400 copy, but in session env | same | accept (model-requests-only, rotate yearly); or `apiKeyHelper` |
| T14 | agent wakes another agent with injected text (Discord peer bots) | M | M | mention required + rate cap | under G6 workers don't talk to Discord; only coordinator | workers get **no** Discord token at all (G6) |
| T15 | no audit trail of who did what | H | M | per-user transcripts; GitLab author = bot account; Verifier results | one uid, one GitLab identity → role only in comment header (G4 Q1) | role in commit trailer + comment header; keep transcripts per worktree; OTel later |

---

## 5. Decisions for the operator

**D1 — GitLab identity for workers.** What a leaked/misused worker token can do.
| option | state now | effect |
|---|---|---|
| **A. one Developer bot shared by all workers** (`aruvii-developer-agent` or a new `aruvii-fleet-agent`) | 4 Developer bots exist (live members) | GitLab blocks merge/master push; role attribution only via comment header (G4 Q1 already accepts) |
| B. one Developer bot per role | exists today; #5 wants it | per-role attribution in GitLab; 4 tokens to rotate yearly; collides with "one GitLab identity" in G4 Q1 |
| C. operator's own PAT | was the #5 situation for 3 agents | worker can merge; `/approved` unverifiable — **reject** |
Recommend **A** (B if per-role attribution in GitLab matters more than G4's simplicity). Backing: GitLab docs (Developer can't merge to Maintainers-only), AF #5.

**D2 — Permission mode for workers.**
| option | effect |
|---|---|
| A. keep `--dangerously-skip-permissions` + fleet-guard | today; docs: no prompt-injection protection; protected paths unchecked |
| **B. `--permission-mode auto` + managed `disableBypassPermissionsMode`** | classifier never sees tool results (docs); firstmate supports it as opt-in (`fm-spawn.sh:394-401 @5f2b81b`); cost: some denials, classifier usage |
| C. `dontAsk` + explicit allow list | strictest, most breakage |
Recommend **B**, measured on one pilot work item before rollout.

**D3 — Isolation under one unix user.** G4 removed the per-user wall; what replaces it?
| option | effect |
|---|---|
| A. accept: workers trust each other (same project, same identity) | cheapest; T4/T10/T11 open; secrets must then be few and narrow |
| **B. Claude sandbox per worker, managed**: writes = own worktree + TMPDIR; `denyRead` other worktrees, `~/.claude/projects`, secrets; network allow-list; `allowUnsandboxedCommands:false` | OS-enforced for Bash (bubblewrap); file tools need matching deny rules; podman/compose likely need `excludedCommands` → hole |
| C. reopen G4: keep per-role unix users (today's AF) | strongest; reintroduces the /tmp/ports/env collisions G4 + ADR 0002 fought |
Recommend **B**, with the runner on its own user regardless (D4).

**D4 — Runner identity and stack.** Runner = Verifier (#35 Q26).
| option | effect |
|---|---|
| **A. separate unix user (`gitlab-runner` or today's `fleet-verifier`), own podman, own `secrets/`** | T5 closed by unix perms; matches ADR 0002 and #62 note |
| B. same user as workers | one podman socket; a worker can kill/inspect the gate's stack — **reject** |
Also: shell executor runs any pushed branch's code (GitLab docs: "Generally it's unsafe") — acceptable only because the repo is private with trusted pushers.

**D5 — Where secrets live.**
| option | effect |
|---|---|
| A. `machine.env` | readable by every worker; easy to `cat` into a comment — **reject for secrets** |
| **B. machine.env = facts only; secrets in one 0400 file per credential, injected at spawn, and masked in the sandbox (`sandbox.credentials` mask)** | worker's commands authenticate without ever seeing the token |
| C. root-run broker (glab/git via a setuid helper or a socket) | strongest, most build work |
Recommend **B**. Also: AP `secrets/` symlinked into worktrees (`link-worktree-stack-files.sh`) means every worker reads the stack master key — fine for a dev stack, but the runner must keep its own copy (D4).

**D6 — Prompt injection and audit, the floor.** Recommend all of: workers get **no** Discord token (G6, coordinator only); network allow-list (D3-B); `/approved` verified by note author (AF #5) not regex; role in comment header + commit trailer; managed-only hooks (`allowManagedHooksOnly`) so a worker can't edit its own guards. Unknown to settle first: how the laptop reaches the VM (T9) — forbid agent forwarding and VM→laptop keys.
