# 64e — What industry does for coding-agent systems, and why

Map #9 · ticket R38 (github.com/chiyanram/skills/issues/86). Researched 2026-10-16.
Primary sources only: vendor engineering posts/docs, papers, DORA, Google eng-practices, martinfowler.com.
Quotes ≤15 words. "fetched" = page read on 2026-10-16. Unreached pages listed at the end.

## Sources (short keys)

| key | source | date |
|---|---|---|
| BEA | anthropic.com/engineering/building-effective-agents | 2024-12-19 |
| MARS | anthropic.com/engineering/multi-agent-research-system | 2025-06-13 |
| CTX | anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2025-09-29 |
| TOOLS | anthropic.com/engineering/writing-tools-for-agents | 2025-09-11 |
| SKL | anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | 2025-10-16 (upd. 2025-12-18) |
| LRA | anthropic.com/engineering/effective-harnesses-for-long-running-agents | 2025-11-26 |
| EVAL | anthropic.com/engineering/demystifying-evals-for-ai-agents | 2026-01-09 |
| CCC | anthropic.com/engineering/building-c-compiler | 2026-02-05 |
| CC-BP | code.claude.com/docs/en/best-practices | fetched |
| CC-MEM | code.claude.com/docs/en/memory | fetched |
| CC-SKL / CC-SUB / CC-SBX / CC-COST | code.claude.com/docs/en/{skills,sub-agents,sandboxing,costs} | fetched |
| AGM | agents.md | fetched |
| CDX-AG | learn.chatgpt.com/docs/agent-configuration/agents-md (redirect from developers.openai.com/codex/guides/agents-md) | fetched |
| CDX-SEC | developers.openai.com/codex/agent-approvals-security (via search snippet only) | n/d |
| GH-CA | docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent | fetched |
| GH-RISK | docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations | fetched |
| GH-CR | docs.github.com/en/copilot/concepts/agents/code-review | fetched |
| GER | google.github.io/eng-practices/review/reviewer/standard.html | fetched |
| GSC | google.github.io/eng-practices/review/developer/small-cls.html | fetched |
| DORA-SB | dora.dev/capabilities/working-in-small-batches/ | 2025-12-08 |
| COG-1 | cognition.com/blog/dont-build-multi-agents (Walden Yan) | 2025-06-12 |
| COG-2 | cognition.com/blog/multi-agents-working (Walden Yan) | 2026-04-22 |
| COG-3 | cognition.com/blog/how-cognition-uses-devin-to-build-devin | 2026-02-27 |
| AMP | ampcode.com/docs/models-and-subagents | fetched |
| MF-CTX | martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html (Böckeler) | 2026-02-05 |
| MF-HAR | martinfowler.com/articles/harness-engineering.html (Böckeler) | 2026-04-02 |
| MF-HC | martinfowler.com/articles/are-harnesses-worth-the-cost.html (Naresh Jain) | 2026-10-13 |
| MF-TDD | martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html (Böckeler) | date not shown |
| SWEA | arxiv.org/abs/2405.15793 SWE-agent (Yang et al.) | 2024-05 (v3 2024-11) |
| SWEB | arxiv.org/abs/2310.06770 SWE-bench (Jimenez et al., ICLR 2024) | 2023-10 |
| LT | simonwillison.net/2025/Jun/16/the-lethal-trifecta/ | 2025-06-16 |

---

## D1 rule layers + loading

**Industry does**
- Layered instruction files, loaded by directory: ancestors at launch, subdirectory files "load on demand" when the agent touches files there (CC-MEM). Managed-policy file "cannot be excluded" (CC-MEM).
- Codex concatenates root→cwd; "Files closer to your current directory override earlier guidance"; 32 KiB cap (CDX-AG). AGENTS.md spec: in monorepos "the closest one takes precedence"; "explicit user chat prompts override everything" (AGM).
- Path-scoped rules + skills keep the always-on file small: "target under 200 lines per CLAUDE.md file" (CC-MEM); "For each line, ask: Would removing this cause Claude to make mistakes?" (CC-BP).
- Cross-vendor convergence on one file: AGENTS.md "stewarded by the Agentic AI Foundation under the Linux Foundation" (AGM); Claude Code reads it when no CLAUDE.md exists (CC-MEM); Copilot review reads it (GH-CR).

**Why** — context is finite and degrades: "context rot" (CTX); "Bloated CLAUDE.md files cause Claude to ignore your actual instructions" (CC-BP). Rules are probabilistic: CLAUDE.md is "context, not enforced configuration" (CC-MEM); hooks are for "actions that must happen every time with zero exceptions" (CC-BP).

**Disagree** — precedence model differs: Codex = concatenate + later wins (CDX-AG); AGENTS.md = closest wins (AGM); Claude Code = CLAUDE.md *replaces* AGENTS.md by default (CC-MEM). Böckeler: build rules up "iteratively"; prune as models improve (MF-CTX) — i.e. no vendor prescribes a large upfront rulebook.

## D2 skill/reference format + how rules are sourced/edited/evaluated

**Industry does**
- SKILL.md + frontmatter `name`/`description`; description is the load trigger; 3-level progressive disclosure (metadata → body → linked files) (SKL, CC-SKL). Keep SKILL.md "under 500 lines", move detail to linked files (CC-SKL). Open standard since 2025-12-18 (SKL).
- Side-effecting workflows: `disable-model-invocation: true` so only a human triggers them (CC-BP).
- Source skills from observed failures: "Identify specific gaps in your agents' capabilities" (SKL); "Monitor how Claude uses your skill in real scenarios" (SKL).
- Evaluate: with-skill vs without-skill comparison (skill-creator / `claude plugin eval`) (CC-SKL); "20-50 simple tasks drawn from real failures is a great start" (EVAL); held-out sets "to ensure we did not overfit" (TOOLS).

**Why** — tool/skill descriptions "can collectively steer agents" (TOOLS); "Treat CLAUDE.md like code: review it when things go wrong, prune it regularly" and test whether behaviour shifts (CC-BP).

**Disagree** — who triggers context: LLM (skills), human (slash command), or software (hooks); skills may not load when expected (MF-CTX). Vendors lean on model-invoked; Fowler/Thoughtworks flags its unreliability.

## D3 orchestration (single vs multi-agent)

**Industry does**
- Start simplest: "only increasing complexity when needed"; maybe "not building agentic systems at all" (BEA).
- Orchestrator-worker for breadth: lead Opus + Sonnet subagents beat single Opus by 90.2% on research eval (MARS).
- But for coding: "most coding tasks involve fewer truly parallelizable tasks than research" (MARS). Cognition: "just use a single-threaded linear agent" (COG-1); 2026 update: multi-agent works when writes stay "single-threaded" and extra agents add analysis, not edits (COG-2).
- Subagents mainly as context isolation: "returns only the summary" (CC-SUB); Anthropic's 16-agent C compiler used no orchestrator — "I don't use an orchestration agent"; git lock files coordinate (CCC).

**Why** — "Actions carry implicit decisions, and conflicting decisions carry bad results" (COG-1); multi-agent costs "about 15× more tokens than chats" (MARS).

**Disagree** — Anthropic ships agent teams/fan-out (`/batch` 5–30 worktree subagents, CC-BP); Cognition says parallel-writer swarms lack adoption (COG-2). Manager agents become "overly prescriptive" without codebase context (COG-2).

## D4 brief + handoff record

**Industry does**
- Brief = "an objective, an output format", tool guidance, task boundaries; vague briefs caused duplicated work (MARS).
- Subagents write artifacts to external storage and return references (MARS); return "condensed, distilled summary", ~1–2k tokens (CTX).
- Long-running handoff = files + git: "claude-progress.txt file alongside the git history"; feature list in JSON because model less likely to overwrite JSON than Markdown; end each session "in a clean state" (LRA).
- Spec as handoff to a fresh session: specs "name the files and interfaces", state out-of-scope, end with an e2e verification step (CC-BP).

**Why** — fresh context is the default; "it is important to retain the plan" when context truncates (MARS).

**Disagree** — Cognition: "share full agent traces, not just individual messages" (COG-1) vs Anthropic: condensed summaries (CTX). Cognition 2026 also: agents "assume they share state with their children" when they don't (COG-2).

## D5 human channel, escalation, status

**Industry does**
- Pause "for human feedback at checkpoints or when encountering blockers" (BEA).
- Visible session logs; steer mid-run via prompt box (GitHub track-sessions doc, fetched). Copilot agent opens a PR per task, cannot mark Ready, approve or merge (GH-RISK).
- Interview-first for larger features, then write SPEC.md (CC-BP). Course-correct early; after two failed corrections, `/clear` and re-prompt (CC-BP).
- Show evidence, not claims: "Have Claude show evidence rather than asserting success" (CC-BP).

**Why** — human attention is the scarce resource: "direct it to where our input is most important" (MF-HAR); "the bottleneck shifted from writing code to reviewing it" (COG-3).

**Disagree** — none material; differences are surface (PR thread vs chat vs Slack tag "@Devin", COG-3).

## D6 review (AI reviewer + human)

**Industry does**
- Fresh-context AI reviewer: "A fresh context improves code review since Claude won't be biased" (CC-BP); Devin Review on every PR; reviewer with "a completely clean context" (COG-2, COG-3).
- Scope the reviewer: flag only gaps affecting correctness/requirements, else "over-engineering" (CC-BP). Coder filters reviewer findings against user intent (COG-2).
- AI review is advisory: Copilot reviews "do not count toward required approvals" by default; "Supplement Copilot's feedback with a human review" (GH-CR). Requester cannot approve the agent's PR (GH-RISK).
- Human standard: approve when it "definitely improves the overall code health", not perfection (GER).

**Why** — inferential sensors are "Slower and more expensive" and less predictable than computational ones (MF-HAR); reviewers asked to find gaps "will usually report some" (CC-BP).

**Disagree** — count: Anthropic/Cognition = one fresh reviewer; GitHub allows Copilot approval to count if enabled (GH-CR). No vendor recommends multiple parallel AI review axes as a default.

## D7 verification gate

**Industry does**
- "Give Claude a check it can run" — tests, build, linter, screenshot; strongest form is a Stop hook that blocks ending until it passes (CC-BP).
- Benchmarks grade by execution (SWE-bench, SWEB); "code solutions are verifiable through automated tests" (BEA).
- Agent CI runs gated: workflows "not triggered until Copilot cloud agent's code is reviewed" and approved (GH-RISK); branch protections and required checks apply to the agent (GH-RISK via search).
- Verifier quality is the ceiling: "the task verifier is nearly perfect" or agent solves wrong problem (CCC). Factory scores repos on deterministic signals ("agent readiness"; factory.ai/news/agent-readiness, via search).

**Why** — "Claude stops when the work looks done" (CC-BP); agents "mark a feature as complete without proper testing" (LRA).

**Disagree** — when to run: MF-HC finds frontier models pass anyway; run tests "as a deterministic final verification gate" rather than continuously; cheaper models need sensors during work (MF-HC).

## D8 branch/push/merge + agent permissions

**Industry does**
- Agent pushes to one branch only (new `copilot/` branch); "cannot approve or merge a pull request" (GH-RISK).
- Only write-access users can trigger it; requester marked co-author for traceability (GH-RISK).
- Small batches: AI "massive pull requests" are the risk; small batches "amplifies the positive impact of AI adoption" (DORA-SB); small CLs "Reviewed more thoroughly" (GSC). Copilot: "Break complex tasks into smaller, focused tasks"; 59-min session cap (GH-CA).
- Worktree per parallel session (CC-BP).

**Why** — keep required-review rules meaningful (GH-RISK); AI adoption "often leads to increased software delivery instability" (DORA-SB).

**Disagree** — none: every vendor keeps merge with a human.

## D9 lessons / learning loop

**Industry does**
- Agent-written memory: auto memory saves `feedback` = "corrections you give Claude"; index MEMORY.md loaded each session (CC-MEM).
- Human-curated: Devin Knowledge + Playbooks — "Once anyone succeeds with Devin, others can replicate that success" (COG-3).
- Harness improvement: when an issue recurs, strengthen the guide/sensor so it can't recur (MF-HAR); "capture its successful approaches and common mistakes" into skills (SKL).
- Convert repeated misses to hooks: "If Claude already does something correctly... delete it or convert it to a hook" (CC-BP).

**Why** — human role is "to steer the agent by iterating on the harness" (MF-HAR).

**Disagree** — automatic memory (Anthropic) vs curated playbooks (Cognition) vs deliberate harness edits (Thoughtworks). None publish evidence of which works better.

## D10 cost / effort / model routing

**Industry does**
- Scale effort to task: "Simple fact-finding requires just 1 agent with 3-10 tool calls" (MARS).
- Route by model: "Sonnet handles most coding tasks well"; reserve Opus; `model: haiku` for simple subagents (CC-COST). Amp: "Choose a mode based on the task rather than the model name" (AMP).
- Harness lets cheap model match frontier: harnessed cost-optimized run "cost about 33% less" than unharnessed frontier (MF-HC).
- Measured overheads: agents ~4×, multi-agent ~15× chat tokens (MARS); agent teams ~7× standard sessions (CC-COST).

**Why** — "token usage by itself explains 80% of the variance" (MARS).

**Disagree** — Cognition: routing is a "capability router" not "a difficulty escalator" (COG-2) vs Anthropic/Amp effort tiers.

## D11 security / sandbox / egress

**Industry does**
- Network off by default: Codex "runs with network access turned off" (CDX-SEC, search snippet); Copilot firewall "restricts... access to the internet" (GH-RISK); Claude sandbox allowed domains "start empty" (CC-SBX).
- Sandbox is what removes prompts: sandboxed commands run "without asking" (CC-SBX); approval fatigue — "After the tenth approval you're clicking through" (CC-BP).
- Known gaps documented: Copilot firewall does not cover MCP servers or setup steps (GH-RISK via search); Claude sandbox covers shell only (CC-SBX).
- Threat model: avoid the "lethal trifecta" — private data + untrusted content + external comms (LT). Skills: "installing skills only from trusted sources" (SKL).

**Why** — prompt injection + exfiltration; sandbox defines boundary, approval policy decides when to ask (CDX-SEC).

**Disagree** — Claude auto mode uses a classifier to replace human approval (CC-BP); Codex auto-review routes approvals to a reviewer agent but "does not... enable network access" (CDX-SEC). Both still keep the hard boundary deterministic.

## D12 testing discipline with agents

**Industry does**
- Tests first as verification target: "write a failing test that reproduces the issue, then fix it" (CC-BP); one Claude writes tests, another code (CC-BP).
- Protect tests from the agent: "It is unacceptable to remove or edit tests" (LRA).
- E2E as a human would: browser automation fixed premature "done" (LRA).
- Quiet test output: harness "should not print thousands of useless bytes" (CCC).

**Why** — tests are the oracle the agent optimises against (CCC).

**Disagree** — Böckeler's small eval: "no clearly discernable difference" TDD vs no-TDD; she "stopped telling my coding agents to write tests first", uses mutation testing instead (MF-TDD; small sample, LLM judge). Anthropic docs still recommend test-first.

---

## Cross-cutting principles

1. **Verification beats instruction.** A runnable check closes the loop; rules are advisory, hooks/tests are deterministic (CC-BP, CC-MEM, MF-HAR, CCC).
2. **Context is the budget.** Small always-on file, everything else on demand; prune rules that don't change behaviour (CTX, CC-BP, CDX-AG 32 KiB, MF-CTX).
3. **Single writer, many readers.** Extra agents add review/research, not parallel edits to one change (COG-2, MARS, COG-1).
4. **Fresh-context reviewer, human merge.** One unbiased AI reviewer advises; a human who didn't request the work approves; agent never merges (CC-BP, GH-RISK, GH-CR, COG-2).
5. **Small batches.** AI raises volume and instability; small, self-contained changes keep review real (DORA-SB, GSC, GH-CA, COG-3).
6. **Deny by default for egress and permissions.** Sandbox + allowlist; single branch; gated CI (GH-RISK, CC-SBX, CDX-SEC, LT).
7. **Improve the harness from real failures, measured.** Rules/skills sourced from observed misses, evaluated with/without (SKL, EVAL, MF-HAR, TOOLS).
8. **Spend effort proportional to task.** Route by model/effort; multi-agent only where value covers ~15× tokens (MARS, CC-COST, AMP, MF-HC).

## Not reached / unverified

- openai.com/index/running-codex-safely/ — 403. openai.com/index/introducing-swe-bench-verified/ — 403.
- developers.openai.com/codex/agent-approvals-security — quotes come from search-result snippet, not a direct fetch.
- factory.ai agent-readiness — search snippet only; Factory's acceleration claims self-reported.
- GitHub "about coding agent" page did not state draft-PR or `copilot/` naming; those come from GH-RISK.
- DORA 2025 full report (dora.dev) not fetched; only the small-batches capability page.
- SWE-bench abstract does not state grading mechanism; execution-based grading is from the paper body (not fetched).
