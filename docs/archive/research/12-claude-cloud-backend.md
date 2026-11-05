# Claude Cloud Backend Feasibility Research

**Research date:** 2026-10-01  
**Question:** Can Claude Code cloud sessions and the Claude Agent SDK serve as a worker backend for a coordinator/worker agent platform architecture?

## Capability Matrix

| Capability | Cloud Sessions | Managed Agents | Agent SDK |
|---|---|---|---|
| **1. START session with repo + branch + initial prompt** | Supported | Supported | Supported |
| | `claude --cloud "prompt"` | API: POST /sessions with initial_events | SDK: `query()` with prompt |
| | Clones from GitHub; bundled for other repos | Clones from GitHub (primary); bundled for other Git | Operates on local filesystem |
| | **Docs:** https://code.claude.com/docs/en/claude-code-on-the-web.md | **Docs:** https://platform.claude.com/docs/managed-agents/sessions | **Docs:** https://code.claude.com/docs/en/agent-sdk/quickstart.md |

| **2. WATCH session: list + status + transcript** | Supported | Supported | Partial |
| | List at claude.ai/code; stream progress to terminal/browser | API: list sessions, stream events via SSE | Streaming in-process; no server state |
| | Machine-readable: `--output-format json` | Full event history persisted server-side | Cannot query external state |
| | **Docs:** https://code.claude.com/docs/en/claude-code-on-the-web.md | **Docs:** https://platform.claude.com/docs/managed-agents/sessions | N/A |

| **3. SEND follow-up message into running session** | Supported | Supported | N/A |
| | `claude -p "msg" --cloud <id>` queues asynchronously | API: send events to session | In-process only; no network queue |
| | **Docs:** https://code.claude.com/docs/en/claude-code-on-the-web.md §Send follow-ups | **Docs:** https://platform.claude.com/docs/managed-agents/events-and-streaming | N/A |

| **4. END / archive / cleanup session** | Supported | Supported | Supported |
| | Archive + delete from sidebar or API | Archive, delete via API; budget enforcement | Local cleanup (SDK user responsibility) |
| | **Docs:** https://code.claude.com/docs/en/claude-code-on-the-web.md | **Docs:** https://platform.claude.com/docs/managed-agents/session-operations | N/A |

| **5. CONFIG loading: CLAUDE.md, rules, skills, agents, hooks, MCP, plugins** | **Partial** | **Not automatic** | **Yes** |
| | ✓ CLAUDE.md, rules/, skills/, agents/, commands/ | Agent defined via API; no repo file discovery | ✓ All auto-loaded from repo .claude/ |
| | ✓ Hooks from repo .claude/settings.json | No hooks in cloud session | ✓ Hooks, permissions, MCP, skills |
| | ✗ **Plugins (enabledPlugins) do NOT load** | Define explicitly in agent config | ✓ Plugins (local path or marketplace) |
| | ✓ MCP from repo .mcp.json (single-repo sessions) | ✓ mcp_servers in agent config | ✓ MCP servers |
| | **Docs:** https://code.claude.com/docs/en/cloud-environments.md §What carries over | **Docs:** https://platform.claude.com/docs/managed-agents/agent-setup | **Docs:** https://code.claude.com/docs/en/agent-sdk/configuration.md |

| **6a. Repo access: GITLAB supported?** | **NOT natively** | **NOT documented** | **Yes (filesystem)** |
| | ✗ Native: GitHub only (GitHub App + /web-setup) | GitHub proxy documented; GitLab not mentioned | ✓ SDK is filesystem-agnostic; `git` operations in Bash |
| | ✓ Workaround: Local bundle with CCR_FORCE_BUNDLE=1 | Platform restrictions: "require GitHub" | Can clone any git remote via Bash |
| | ✗ BUT: Cannot push back to GitLab (bundle limitation) | No push to non-GitHub remotes documented | ✓ Full git support via Bash tool |
| | **Docs:** https://code.claude.com/docs/en/claude-code-on-the-web.md §Limitations; https://code.claude.com/docs/en/cloud-environments.md | **Docs:** https://platform.claude.com/docs/managed-agents/github-access (404) | **Docs:** https://code.claude.com/docs/en/agent-sdk/quickstart.md |

| **6b. Git credentials / tokens** | Proxy model | GitHub proxy | Pass to Bash |
| | GitHub proxy (GitHub App or /web-setup token) | GitHub proxy attaches on server side | Developer provides via git config, SSH, env vars |
| | Credentials never enter sandbox | Scoped credentials, push protection | No inherent credential handling |
| | Local bundle: Git credentials from your machine | N/A | SSH key or HTTPS token needed |
| | **Docs:** https://code.claude.com/docs/en/cloud-environments.md §GitHub proxy | **Docs:** https://platform.claude.com/docs/managed-agents/github-access | **Docs:** https://code.claude.com/docs/en/agent-sdk/quickstart.md |

| **6c. Egress: can reach gitlab.com, Maven Central, npm, Docker** | Configurable | Not documented | Yes (your network) |
| | Trusted (default): npm, PyPI, Docker Hub, GitHub, Maven Central | Session runs in Anthropic cloud; no network config documented | Runs on your infra; full network access |
| | Custom: explicit allowlist; Trusted + custom | No API credentials yet (Team/Enterprise) | Pass credentials via env vars / git config |
| | Full: any domain | Managed Agents: no separate network control | Your network boundary applies |
| | None: Anthropic API only | MCP tunnels may constrain egress | N/A |
| | **Docs:** https://code.claude.com/docs/en/cloud-environments.md §Network access | **Docs:** https://platform.claude.com/docs/managed-agents/reference | **Docs:** https://code.claude.com/docs/en/agent-sdk/hosting.md |

| **7. Limits & cost model** | **Free with Pro/Max** | **API usage** | **You host** |
| | 4 vCPU, 16 GB RAM, 30 GB disk | Rate limits: 300 create/min, 1200 read/min | Your compute cost |
| | Command timeout: 2 min default, 10 min max | Beta: Requires managed-agents-2026-04-01 header | Session budgeting: User responsibility |
| | Background: 30 min; Idle: reclaim after minutes | No separate compute charge announced | No per-session billing model |
| | Included in Pro ($20/mo) / Max ($100/mo) subscription | Pricing TBD (currently beta) | Depends on deployment |
| | One-time credit: $100–$250 until Oct 7, 2026 | Stateful sessions (may affect ZDR/HIPAA eligibility) | Full control; per-session cost tracking possible |
| | **Docs:** https://code.claude.com/docs/en/cloud-environments.md §Resource/Time limits | **Docs:** https://platform.claude.com/docs/managed-agents/reference §Rate limits | **Docs:** https://code.claude.com/docs/en/agent-sdk/hosting.md |

| **8. Can cloud session spawn other cloud sessions?** | **UNCONFIRMED** | **Yes (multiagent)** | **No** |
| | No documented API for session to spawn sessions | Multiagent orchestration: coordinator delegates to workers | SDK cannot create remote sessions |
| | `claude --cloud` requires terminal/browser; not in-session | Each worker is a Managed Agent session | Subagents: spawn locally via Agent tool |
| | Subagents possible but local to session (no fork to cloud) | Coordinator + roster of delegate agents | No remote session spawn capability |
| | N/A | **Docs:** https://platform.claude.com/docs/managed-agents/multiagent-orchestration | **Docs:** https://code.claude.com/docs/en/agent-sdk/subagents.md |

| **9. Agent SDK as alternative coordinator?** | N/A | N/A | **Partial Yes** |
| | N/A | N/A | SDK runs in your process (Python/TypeScript) |
| | N/A | N/A | Built-in tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch |
| | N/A | N/A | Can shell out to spawn CLI workers (tmux, SSH) |
| | N/A | N/A | No session resume from cloud; local session only |
| | N/A | N/A | Web app = SDK host, spawning `claude` CLI in worktrees is documented path |
| | N/A | N/A | **Docs:** https://code.claude.com/docs/en/agent-sdk/quickstart.md |

## Verdict

### For a **coordinator/worker architecture on GitLab**:

**✗ Cloud Sessions: NOT viable**
- GitHub native only; GitLab only via local bundle (no push-back)
- No server API to spawn sessions from coordinator
- Single-user (browser/CLI); not designed for programmatic multi-worker orchestration
- SessionStart hooks don't run in resumed cloud sessions, limiting persistence

**✓ Managed Agents: Partially viable**
- **Strengths:** Multiagent orchestration (coordinator + roster workers), stateful server-side sessions, API-driven, long-running autonomous work
- **Gaps:** GitLab support not documented or not in platform restrictions ("require GitHub"); no built-in CLAUDE.md/rules/skills auto-loading; agent config only via API
- **Use case:** If GitLab is supported (undocumented), this is the best fit for server-hosted coordinator spawning worker sessions
- **Risk:** Confirm GitLab support with Anthropic before committing

**✓ Claude Agent SDK: Best for self-hosted path**
- **Strengths:** Full control, filesystem-agnostic (any git repo), auto-loads repo config, hooks/MCP/skills all built-in, subagent support
- **Gaps:** No cloud session resume; coordinator and workers must run in your own process(es)
- **Architecture:** Web app hosts SDK; spawns `claude -p` CLI workers in git worktrees (documented workflow); coordinator monitors worktrees via shell, sends follow-ups via `claude -p` 
- **Viable:** Yes — no dependency on GitHub/GitLab platform choice for sessions

### **Recommended Path**

For **on-premise GitLab** with **coordinator/worker in the cloud**:
- **Managed Agents** if GitLab is supported (reach out to Anthropic)
- Fallback: **Agent SDK** + self-hosted runners spawning CLI workers (sacrifices cloud hosting but gains GitLab support)

For **GitHub + cloud coordinator**:
- **Managed Agents** multiagent orchestration (purpose-built, fully featured)
- **Cloud Sessions** if single interactive worker per session suffices (simpler, included in subscription)

For **maximum control + GitLab**:
- **Agent SDK** coordinator as a web app on your infrastructure, spawning worktree workers via CLI (documented workflow in Agent SDK docs)

---

## Sources

- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web.md) — Cloud sessions, session lifecycle, limitations
- [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments.md) — Network, config loading, time/resource limits
- [Managed Agents overview](https://platform.claude.com/docs/managed-agents/overview) — Stateful sessions, long-running work
- [Start a session (Managed Agents)](https://platform.claude.com/docs/managed-agents/sessions) — Session API, initial events, multiagent orchestration
- [Define your agent](https://platform.claude.com/docs/managed-agents/agent-setup) — Agent configuration via API
- [Managed Agents reference](https://platform.claude.com/docs/managed-agents/reference) — Rate limits, event types, self-hosted worker
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk.md) — SDK vs Cloud vs Managed Agents comparison
- [Agent SDK quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart.md) — SDK usage, built-in tools

## Lead verification (2026-10-01, read https://code.claude.com/docs/en/claude-code-on-the-web directly) — CORRECTIONS

- **WRONG above: "no programmatic session spawn".** The doc shows: `claude --cloud "<task>"` creates a cloud session
  for the current repo/branch (one per call, parallel OK); `claude -p "<msg>" --cloud <session-id>` queues a follow-up
  into a running session from any machine (`--output-format json` → `{ok, session_id, url}`); `claude --teleport <id>`
  pulls it local. Listing/archiving/deleting: shown only in the claude.ai UI (sidebar) on this page.
- **GitLab: confirmed limit.** "repository cloning and pull request creation require GitHub"; a GitLab repo can be sent
  as a local bundle (`CCR_FORCE_BUNDLE=1`) "but the session can't push results back to that remote" — on
  Anthropic-hosted environments. Self-hosted environments supply their own git credentials (not verified for GitLab).
- Loads: repo `.claude/agents/` subagents picked up; `/plugin` not available in cloud sessions; settings via repo
  `.claude/settings.json` or environment variables.
- Also exists: "Projects" (Claude coordinates parallel cloud sessions and reports back), routines (scheduled / API /
  GitHub-event triggered), self-hosted environments. Not read in depth.
Verdict for us: Anthropic-hosted cloud = a viable WORKER backend only once results can reach GitLab (self-hosted
environment, or a GitHub mirror); a Claude cloud "Project" is the closest documented cloud coordinator.
