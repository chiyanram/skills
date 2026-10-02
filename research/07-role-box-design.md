# D1 · Role boxes: a paper design (Agent SDK + AG-UI, one compose for laptop and VM)

Answers `issues/12-design-role-boxes.md`. This is a paper design written 2026-10-01. Nothing is built. Execution is blocked by G1–G4 and P1.

Source keys used below:

| key | location |
|---|---|
| `ML/` | `refs/imdganesancareers-MasterLaundry/` (Ask Me box, infra only) |
| `AF/` | `refs/chiyanram-agent-fleet/` |
| `cc:` | `https://code.claude.com/docs/en/` |
| `agui:` | `https://docs.ag-ui.com/` |
| `TC:` | `https://java.testcontainers.org/supported_docker_environment/continuous_integration/dind_patterns/` |

---

## 1 · The whole system in one picture

```
 browser (laptop or phone)
 ┌──────────────────────────┐
 │  web UI  (one page,      │   AG-UI over HTTP + SSE  (agui:concepts/events)
 │  4 role tabs + inbox of  │◄──────────────────────────────────────────────┐
 │  open interrupts)        │──── RunAgentInput {threadId, messages,        │
 └──────────────────────────┘      resume[]} ──────────────┐                │
                                                           ▼                │
 ┌─────────────────────────────── compose project "fleet" ─────────────────┼──────┐
 │  gateway (Node)  — auth, routing by role, threadId = "#NNN"; holds the   │      │
 │  operator's identity; polls GitLab for the gates; persists run log ──────┘      │
 │     │ internal net only (like ML/docker/ask-me/docker-compose.yml:20-25)        │
 │     ├──────────┬──────────────┬──────────────┬──────────────┐                   │
 │     ▼          ▼              ▼              ▼              ▼                   │
 │  analyst   spec-reviewer   developer        qa          verifier               │
 │  box       box             box ─┐           box ─┐      (no Claude)            │
 │                                 ▼                ▼          │                   │
 │                            dind-dev          dind-qa      dind-verify          │
 │                                                                                │
 │  egress proxy (CONNECT allowlist) ◄── the only route out for every box          │
 └───────────────┬────────────────────────────────────────────────────────────────┘
                 ▼
     api.anthropic.com · gitlab.com · Maven/Gradle/npm registries · Docker Hub
```

Each box is an Ask-Me-style container: Node, the Agent SDK, and a `claude` subprocess (`cc:agent-sdk/hosting` "The subprocess model"). Each box speaks AG-UI to the gateway, and the gateway relays it to the UI.

GitLab stays the system of record for issues, MRs, `/approved` and merge. The web UI replaces Discord and tmux. It does not replace GitLab.

---

## 2 · What a role box is, compared with the Ask Me box

```
 role-box image (one image, ROLE env picks the role)
 ┌─────────────────────────────────────────────────────────────┐
 │ L4  box app: AG-UI server · session map · canUseTool · trace │  ← like ML/packages/askme-box/src
 │ L3  /etc/claude-code/managed-settings.json + fleet-guard.py  │  ← AF/enforcement/ (same hook)
 │ L2  toolchain: git · glab · make · JDK 25 · Node · docker CLI│  ← absent from Ask Me
 │ L1  node:20 + @anthropic-ai/claude-agent-sdk (pinned CLI)    │  ← ML/docker/ask-me/Dockerfile:23
 └─────────────────────────────────────────────────────────────┘
 volumes: /work (repo clone + worktrees)  ·  /home/agent/.claude (CLAUDE_CONFIG_DIR: sessions, memory)
```

| Concern | Ask Me box (fact) | Role box (proposal) |
|---|---|---|
| Rules loaded | `settingSources: []`, so no CLAUDE.md (`ML/.../session.ts:90`) | `settingSources: ['project']`, with `cwd` set to the clone. That loads CLAUDE.md, `.claude/rules`, skills, agents and hooks (`cc:agent-sdk/claude-code-features`) |
| Leaving out `'user'` | n/a | This is deliberate: the laptop's `~/.claude` is never mounted, so the box does not drift with it. The cost: the operator's global reply rules do not load (OQ 4) |
| Plugins (G4 marketplace) | none | Managed `enabledPlugins` + `CLAUDE_CODE_PLUGIN_SEED_DIR` baked into the image (R5, `cc:plugins/org`), or `plugins: [{type:'local', path}]` (`cc:agent-sdk/typescript`) |
| System prompt | custom string from `persona.md` | `{type:'preset', preset:'claude_code', append: <persona>}`. The persona is read from the **clone's** `docs/agents/personas/<role>.md`, the same file the laptop reads. A spec-reviewer file does not exist yet |
| Built-in tools | `tools: []`, only 2 MCP tools (`session.ts:84`) | Claude Code preset tools, narrowed per role (table below) |
| Permission | `default` + `canUseTool` allow-list (`session.ts:78-82`) | The same shape. The fleet today runs `bypassPermissions` (`AF/scripts/create-agent.sh:153`) |
| Auto memory | disabled (`session.ts:67`) | **On**, on the config volume. This is the fleet's "project knowledge" (`AF/CONTEXT.md:60`) |
| Session persistence | `persistSession: false` | `true`, on the volume, so resume survives a restart (§5) |
| Spend caps | `maxTurns: 8`, `maxBudgetUsd: 0.5` | Set per role, per run. R4 measured about $2–2.8 per review |
| Env hygiene | `subprocessEnv` passes an allow-list of variables (`session.ts:58`) | Same pattern, plus `JAVA_HOME`, `DOCKER_HOST` and `LANG`. These are the fleet's env failures (`research/00`) |

### Tools per role and the `canUseTool` policy

| role | tools allowed | Bash scope | may write repo | docker |
|---|---|---|---|---|
| analyst | Read Grep Glob Skill Agent WebFetch Bash | `git` read-only, `glab issue *`, `glab mr create --draft` | spec/docs only | no |
| spec-reviewer | Read Grep Glob Skill Agent Bash | `git` read-only, `glab mr note` | no | no |
| developer | full preset | `make *`, `git *` (not push to master), `glab mr *` (not merge) | yes | own dind |
| qa | full preset | `make *`, `glab mr note`, `fleet-verify` | test files | own dind |

How a tool call is decided:

```
tool call ─► PreToolUse fleet-guard (managed, runs in every mode: AF/enforcement/fleet-guard.py:6-9)
             │ deny? ─► denied, with a reason
             ▼
          allowedTools match? ─► run
             ▼ (falls through)
          canUseTool(role policy)            (cc:agent-sdk/typescript canUseTool)
             ├─ hard deny: glab mr merge · note "/approved" · push master · make secrets
             ├─ allow: known-safe patterns
             └─ unknown ─► AG-UI interrupt {reason:"tool_call"} ─► human decides (§4)
```

Two notes on this flow:
- The hard denies restate this repo's CLAUDE.md git rules as code. That follows ADR-0021's principle: if forgetting a rule would cause harm, put it in code (`ML/docs/adr/0021-…`).
- What `canUseTool` sees depends on the permission mode. It is only called when evaluation "falls through to a prompt" (`cc:agent-sdk/typescript`). So the mode must be `default`, not `bypassPermissions`.

### Sandbox and egress

The box copies Ask Me's three pieces: an `internal` network, a one-shot `firewall` container with `NET_ADMIN` (`ML/docker/ask-me/firewall.sh`), and a CONNECT `egress` proxy (`ML/docker/ask-me/egress.mjs`). The box runs `read_only`, with `cap_drop: [ALL]` and `no-new-privileges` (`ML/.../docker-compose.yml:152-157`).

The egress allowlist (`ASK_ME_EGRESS_ALLOW`-style):

```
api.anthropic.com:443          model
gitlab.com:443                 git + glab (+ the plugin marketplace if hosted there)
repo.maven.apache.org:443      Gradle deps
plugins.gradle.org:443  services.gradle.org:443  downloads.gradle.org:443
registry.npmjs.org:443         aruvii-ui
```

Docker Hub is **not** on the box's list. Image pulls are made by the dind daemon (§3), which gets its own allowlist.

Three caveats:
- Node `fetch` ignores `HTTPS_PROXY` unless `NODE_USE_ENV_PROXY=1` is set. Gradle needs proxy JVM properties (`cc:agent-sdk/secure-deployment` "Traffic forwarding").
- A CONNECT proxy cannot stop exfiltration *to* gitlab.com, which is an allowed host (same page, "No TLS inspection").

### Credentials

| secret | today (fleet) | role box |
|---|---|---|
| Claude | one OAuth token per fleet (`AF/docs/adr/0001-…`) | The same token, kept in a compose `secret` file and passed only into the CLI subprocess env (`session.ts:60`). A `setup-token` token "can only make model requests" (`cc:agent-sdk/claude-code-features`) |
| GitLab | a per-recipe PAT in `~/.git-credentials` (`AF/README.md:91-93`) | A per-role PAT as a compose secret, read by a git credential helper and by `glab`. **The agent can read it.** The alternative is a git/glab MCP tool whose request is made outside the box (`cc:agent-sdk/secure-deployment` "Custom tools"). That costs a rewrite of every skill that shells out to `glab` (OQ 6) |
| Operator (for gates) | Discord DM allowlist | Only the gateway holds it, never a box |

---

## 3 · The compose layout

The same file runs on the laptop and on the VM. Only `.env` differs, as Ask Me does with `ASK_ME_NET` (`ML/.../docker-compose.yml:10-13`).

```
fleet/compose.yml   (COMPOSE_PROJECT_NAME=fleet — never aruvii's project name)
 always on : gateway · ui · egress · netns · firewall
 profiles  : analyst │ spec-reviewer │ developer (+dind-dev) │ qa (+dind-qa) │ verifier (+dind-verify)
 .env      : COMPOSE_PROFILES=analyst,developer   ← laptop runs 2
             COMPOSE_PROFILES=analyst,spec-reviewer,developer,qa,verifier   ← VM runs all
```

### How developer and qa get Docker for Testcontainers

| option | how | isolation | the shared-stack problem (aruvii CLAUDE.md) | memory | verdict |
|---|---|---|---|---|---|
| A · host socket ("wormhole") | mount `/var/run/docker.sock` and the repo **at the same path** (`TC:`) | none: the socket is root on the host, so the sandbox is void | The box's `make smoke` redeploys **the operator's own** aruvii stack. "Last-deployed-branch wins" gets worse | host | reject |
| B · dind sidecar per box | `docker:dind` privileged sidecar, `DOCKER_HOST=tcp://dind-dev:2376`, its own volume | The box is unprivileged; only the sidecar is privileged | Each box gets its own daemon, so its own aruvii stack. This fixes the shared-stack problem | its own limit, plus the image cache per box | **pick, for targeted ITs and smoke** |
| C · rootless podman inside the box | the fleet's current model (`AF/scripts/create-agent.sh:407-430`) | needs user namespaces in the container, close to privileged | own | in the box | a fallback if B is blocked |
| D · machine-wide Verifier only | the box runs no containers; it submits a SHA (`AF/docs/adr/0002-…`) | best | n/a | Verifier only | **pick, for the DoD gate** |

Testcontainers calls DinD "an instrument of last resort" (`TC:`). The reason here is that the socket alternative destroys the sandbox.

The recommendation is **B + D**:
- developer and qa run targeted ITs against their own dind.
- `make verify-full` / `smoke FULL=1` run in the `verifier` profile. That is the fleet Verifier (`AF/verifier/fleet-verify`) moved into a compose service with its own dind.
- The laptop gets the Verifier for free, which today exists only on the VM.

### Memory limits

The fleet's OOM on `make verify` (`research/00`) comes from three things stacked together: Gradle `-Xmx4g` (`gradle.properties:7`), the Testcontainers postgres and redis, and the box itself.

| service | `mem_limit` (starting guess, to be measured) |
|---|---|
| analyst, spec-reviewer | 2g (Ask Me's figure, `docker-compose.yml:162`; `cc:` floor is 1 GiB) |
| developer, qa | 6g box + 4g dind |
| verifier | 12g box+dind, one job at a time (`AF/CONTEXT.md:63-68`) |

With every profile on, that adds up to about 34g. That fits the VM, not a 16 GB laptop, which is why the profiles exist (OQ 3).

---

## 4 · How AG-UI events map to what the boxes do

| What happens | Agent SDK message | AG-UI event (`agui:concepts/events`) |
|---|---|---|
| a turn starts | a user msg is pushed into the streaming `query()` | `RunStarted {threadId:"#585", runId}` |
| text | `stream_event` deltas (`includePartialMessages`) | `TextMessageStart/Content/End` |
| thinking | thinking blocks | `ReasoningStart…End` |
| tool use | `tool_use` / `tool_result` blocks | `ToolCallStart/Args/End/Result` |
| subagent (reviewers) | the `Agent`/Task tool + `agent_id` | `SubagentStarted/Finished`. The adapter does not emit these yet (ag-ui issue #2755) |
| cost, stage, Verifier status | the result message + box state | `StateSnapshot`, then `StateDelta` (JSON Patch) |
| the turn ends | `result` | `RunFinished {outcome:{type:"success"}}` |
| a gate or question | see below | `RunFinished {outcome:{type:"interrupt", interrupts:[…]}}` |

### Human gates as interrupts

AG-UI interrupt fields: `id`, `reason`, `message`, `toolCallId`, `responseSchema`, `expiresAt`. The resume must address **every** open interrupt (`agui:concepts/interrupts`).

```
 box                         gateway                           human
  │ request_human(gate=approve, mr=!230)
  ├──────────────► RunFinished interrupt{reason:"confirmation",
  │                 message:"#554 spec ready — /approved on !230?",
  │                 metadata:{mrUrl}}  ─────────────────────►  UI card + link
  │                                                            │
  │                 polls GitLab: "/approved" note on !230 by operator ◄─ human posts it IN GITLAB
  │                 found ─► resume [{interruptId, status:"resolved"}]
  ◄─────────────────┘ new run continues stage 6
```

| gate | interrupt `reason` | what resolves it |
|---|---|---|
| `/approved` (stage 5) | confirmation | The operator's own note on the MR, seen by the gateway. Under this repo's CLAUDE.md the agent never posts it; the UI only links to it |
| merge (stage 9) | confirmation | The MR state becomes `merged` in GitLab |
| "needs decision" | input_required, with a `responseSchema` of options | The UI answer. The gateway also echoes it to the issue as a comment, so the record lives in GitLab |
| unknown tool (`canUseTool`) | tool_call, with `toolCallId` | approve/deny in the UI, with an `expiresAt` of 30 min |

**One design tension.** Ask Me ends the session at a *proposal* so that it never holds a subprocess open while a human reads (`ML/docs/adr/0021-…` §Context). A `canUseTool` promise, by contrast, *does* hold the subprocess open. Proposal: a `tool_call` interrupt keeps the query alive until `expiresAt`. A gate interrupt ends the run and the session goes idle (§5), and the resume arrives as a fresh turn.

### Handoff between roles (replaces the Discord @mention)

```
 analyst box ──handoff(to:"developer", thread:"#554", note)──► gateway
   (an in-process MCP tool, like ML/.../tools.ts)                   │
                                     ├─ comment on the issue/MR (the GitLab record stays)
                                     ├─ Custom{name:"handoff"} to the UI
                                     └─ RunStarted on the developer box {threadId:"#554", parentRunId}
```

Today's bot-to-bot rate cap (`AF/README.md:95-99`) becomes a counter in the gateway. Handoffs are explicit tool calls, not text mentions, so there is no mention loop.

**Adapter choice.** `@ag-ui/claude-agent-sdk` exists and is at v0.0.4 on npm (search result, jsdelivr). It does approvals through a frontend tool (`docs.copilotkit.ai/claude-sdk-typescript`). The alternative is a thin mapper of our own, about the size of `ML/.../trace.ts`. That decision is OQ 7.

---

## 5 · Session lifecycle

```
 container (long-lived, restart: unless-stopped)
   └─ session per THREAD (= one work item #NNN, per role)
        start  : query({resume?: sid, cwd:/work/wt/<branch>, settingSources:['project']})
        turns  : streamInput() into the open query   (cc:agent-sdk/hosting "Long-running")
        idle   : 30 min with no turn ─► end the subprocess, keep the sid
        next   : a new turn ─► query({resume: sid})
        cap    : lifetime / budget hit ─► end; the next turn starts fresh from the MR thread
```

The trade-off: per-task sessions keep context small (12-factor F10, `research/05`). Long-lived *containers* keep the warm Gradle cache and the toolchain. The SDK has "no top-level session timeout" and memory grows over long sessions (`cc:agent-sdk/hosting` "Known limitations"), so the idle and lifetime sweep is ours to write, as in `ML/.../session.ts:269-273`.

What survives a restart:

| thing | where | after `docker compose restart` | after `down -v` |
|---|---|---|---|
| transcripts (resume) | `$CLAUDE_CONFIG_DIR/projects/*.jsonl` on a volume (`cc:agent-sdk/sessions`) | yes | no. A `SessionStore` would fix that (OQ 8) |
| auto memory / project knowledge | the same volume | yes | no |
| repo clone + worktrees + Gradle cache | the `/work` volume | yes | no |
| `/crq` state | the GitLab issue/MR (12-factor F5, `research/05`) | yes | **yes** |
| sid ↔ thread map, run log | gateway volume | yes | no |

The design rule: **anything that must survive goes to GitLab.** The volumes are only a cache.

---

## 6 · Migration from tmux + Discord

Each step is reversible: the step before it keeps running until the step is proven.

| step | change | proven when | undo |
|---|---|---|---|
| 0 | G1–G4 + P1 land; the rulebook loads through the project settings and the marketplace | the laptop and the VM load identical files (G4's check) | — |
| 1 | Build the role-box image. Run **today's CLI in tmux inside it** (`--channels plugin:discord`) for one role | that role works a ticket end to end from the container | stop the container; the unix-user agent is untouched |
| 2 | Add the egress + firewall pieces to that container | there are no `refused CONNECT` lines for legitimate work over a week | remove `HTTPS_PROXY` |
| 3 | Move the Verifier into the `verifier` profile, parallel to `fleet-verifier` | the same SHA gives the same PASS/FAIL in both | keep using `fleet-verify` |
| 4 | Swap tmux for the box app (SDK + AG-UI) for **analyst** only. Discord stays for the other roles | one intake through the UI, with the handoff echoed to Discord | point that role back at step 1 |
| 5 | Add the gateway gate-polling and the interrupts. `/approved` and merge stay in GitLab | one full `/crq` with both gates crossed from UI cards | gates fall back to Discord pings |
| 6 | spec-reviewer, then qa, then developer (the dind one is last) | each role does one MR | per role, back to step 1 |
| 7 | The laptop runs `COMPOSE_PROFILES=…` from the same file | the same ticket gives the same result on the laptop and the VM | the laptop keeps interactive `/crq` |
| 8 | Retire the Discord plugin and `create-agent.sh` tmux launch | 2 weeks with no Discord use | the recipes and registry survive (`AF/README.md:76`) |

---

## 7 · Risks and unknowns

| risk | why it matters | mitigation |
|---|---|---|
| dind memory + image cache per box | 3 daemons each pull postgres, redis and ollama images | a shared pull-through registry mirror on the compose net |
| `canUseTool` holds the subprocess open while a human decides | memory, and a stale turn | `expiresAt`; deny on expiry |
| The adapter is immature (v0.0.4; no Activity/Subagent events, #2755) | the reviewer subagents are invisible in the UI | our own mapper (OQ 7) |
| The PAT is readable inside the box | a prompt-injected push or comment | a scoped bot PAT per role, protected `master` (already), an MCP git tool later |
| gitlab.com is allowlisted, so it is an exfil channel | the lethal trifecta (`cc:agent-sdk/secure-deployment`) | a PAT scoped to one project; audit at the proxy |
| `'user'` source dropped | the operator's reply-shape rules vanish in the boxes | move them into the project or managed `CLAUDE.md` (G1) |
| One shared OAuth token = one rate limit | 4 boxes + reviewer subagents at once | `maxBudgetUsd`, and stagger qa behind the developer |
| Laptop RAM | about 34g with every profile | profiles; the Verifier on the VM only (OQ 3) |
| The gateway is a new single point | the UI is dark if it dies; the boxes keep working | GitLab is still the record; the boxes keep running headless |

## Open questions for the operator

1. **Gate resolution**: should the gateway *only observe* `/approved` and merge in GitLab (recommended), or post `/approved` with your PAT when you tap the UI card?
2. **Docker for developer and qa**: B (a privileged dind sidecar per box) + D (Verifier), or C (rootless podman, the fleet's current model)? A (host socket) is rejected.
3. **Laptop scope**: which profiles run on the laptop? Does the Verifier run there, or only on the VM?
4. **Your global `~/.claude/CLAUDE.md`** (ADHD reply rules): move it into project or managed settings so the boxes load it, or leave the boxes without it?
5. **The persona file**: is the source `docs/agents/personas/<role>.md` (aruvii) or the fleet's `SOUL.md` (`AF/scripts/create-agent.sh:52-55`)? spec-reviewer has no aruvii persona yet.
6. **GitLab identity**: one bot PAT per role (four GitLab users) or your PAT shared? Accept the PAT being inside the box, or invest in an outside-the-box git/glab tool?
7. **AG-UI adapter**: adopt `@ag-ui/claude-agent-sdk`, or write our own mapper?
8. **Session durability**: is a volume enough (lost on `down -v`), or do you want a `SessionStore` (e.g. the aruvii postgres)?
9. **Gateway auth on the VM**: Caddy plus what (basic auth, OIDC, Tailscale only)? The fleet's Caddy is at `AF/scripts/setup-proxy.sh`.
10. **Permission mode**: `default` + `canUseTool` (recommended), or keep `bypassPermissions` with fleet-guard as the only fence?
11. **Spend caps**: should `maxBudgetUsd` be set per run per role? R4's ~$2–2.8 per review suggests qa at about $5 and developer at about $15. Your numbers?
12. **Web UI stack**: Angular (aruvii's; AG-UI has no Angular client, per `research/05`) or React + CopilotKit (supported out of the box)?
