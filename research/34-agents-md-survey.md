# 34 — What belongs in the root AGENTS.md (survey)

For **#646** — cut AGENTS.md (today's 482-line CLAUDE.md) to <200 lines, `<important if>` blocks
kept, each ≤3 MUST bullets + a pointer. Skeleton of target paths: `docs/design/ONE-RULEBOOK-SKELETON.md`
(**#643**). Date 2026-10-02. All counts below were produced by `wc`/`grep`/`awk`; the commands are
in §6.

Reference root: `agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/` (`refs/` below).

---

## 0. Headline findings

```
 ours today                               what the references do
 ───────────────────────────────────      ────────────────────────────────────────
 482 lines · 32,775 bytes                 11 of 14 root files ≤ 150 lines
 > Codex 32 KiB cap by 7 bytes  ◄── BUG    Anthropic: < 200 lines · HumanLayer: < 300
 17 <important if> blocks                 0 of 17 reference files use <important if>
 137 bold spans on 129 lines              Anthropic: emphasis on ONE line or none
 17 issue refs, incident histories        histories only in nested files (openclaw test/, ui/)
 rules duplicated in .claude/rules/*      "update instructions at their owner" (openclaw:8)
```

1. **Our file is already truncated in Codex.** 32,775 bytes vs Codex's 32 KiB default
   `project_doc_max_bytes` (32,768) — the tail of the *Done means* block is cut. firstmate (47,958 B)
   has the same problem.
2. **`<important if>` has one backer** (humanlayer `improve-claude-md` skill) and **zero** practising repos.
   It is harmless to other tools (plain text), so the decision stands, but it is not the industry norm —
   nested files, path-scoped rules and skills are.
3. **Three of our claims are verified false/stale**: "Two `SessionStart` hooks" (`CLAUDE.md:56`;
   `.claude/settings.json` has one), the block condition "pom.xml" (`CLAUDE.md:200`; repo has no
   `pom.xml`, it is Gradle), and "a launch-time load does not survive a compaction" (`CLAUDE.md:60-61`;
   Anthropic: "Project-root CLAUDE.md survives compaction").

---

## 1. Per-repo table

Pinned SHAs from `git -C <repo> rev-parse --short HEAD`.

| repo@sha | file | lines (bytes) | sections in order | kinds of line | deliberately leaves out | notable technique |
|---|---|---|---|---|---|---|
| humanlayer-fold@864a60e | `AGENTS.md` | 41 (1,721) | identity :3 · Stack :5 · Commands :14 · Dependency versions :22 · Shared packages :27 · Effect v4 source :33 | identity, stack, commands, one gotcha (v4≠v3 docs :35-41), pointer to source | style rules (oxlint/oxfmt own them :10), architecture, process, git | "read this, not v3 docs" — corrects a training-data default (:41) |
| humanlayer-agentlayer@a7e3a20 | `AGENTS.md` = `CLAUDE.md` (byte-identical copies) | 36 (1,821) | identity :3 · Monorepo Map :5 · Key Commands :17 · OSS Contribution :31 | map, commands, one preferred gate (`bun check` :26-27), contributor policy pointer | style, architecture detail, testing patterns ("read the docs" :29) | single preferred verify command marked `_IMPORTANT_` once |
| humanlayer-humanlayer@99abe67 | `CLAUDE.md` + `hld/`, `humanlayer-wui/`, `scripts/` | 88 root (3,176); nested 55 / 64 / 106 | Overview :5 · Project 1 :12 · Project 2 :24 · Architecture Flow :32 · Dev Commands :39 · Technical Guidelines :62 · Conventions (TODO priorities) :74 · Resources :87 | map, ASCII arch flow :33-37, commands, light style, convention | per-component detail → nested files; root says "check package.json" (:53-55) | **nested CLAUDE.md per component**: `hld/CLAUDE.md:3` "You cannot run this process"; logs + sqlite paths (:5-31) |
| humanlayer-claudelayer@558f7bc | `CLAUDE.md` | 106 (2,455) | Bun defaults :2 · APIs :11 · Testing :21 · Frontend :33 | tool substitutions ("use X not Y" :4-19), code snippets :25-104 | everything project-specific (it is Bun's stock template) | identical to `humanlayer/scripts/CLAUDE.md` (diff clean) — a vendored template |
| humanlayer-12-factor-agents@d20c728 | `CLAUDE.md` | 91 (3,252) | Persona selection :5 · How to choose :19 · Project Context :27 · Core Principles :37 · File Structure :45 · Commands :61 · CRITICAL REMINDER :79 | persona routing, ALL-CAPS mandates, placeholders | real project content (template "[CUSTOMIZE…]" :29,47,63) | anti-example: shouting (`MANDATORY`, `CRITICAL`, `DO NOT PROCEED` :5-17, 79-87) |
| humanlayer-skills@ca7c808 | `plugins/improve-claude-md/skills/improve-claude-md/SKILL.md` (= `~/.claude/skills/improve-claude-md/SKILL.md`, identical) | 258 | Core Problem :8 · `<important if>` :16 · Principles 1-5 :20-74 · Output Structure :76 · How to Apply :111 · Example :125 | guidance, not a root file | — | **the only source for `<important if>`**; "Keep all commands" (:72-74); "Do not shard into separate files" (:59) |
| humanlayer-ACE@f2bc7ae | `ace-fca.md` etc. | — | — | no CLAUDE.md guidance found (`grep -i claude.md` → 0 hits) | — | — |
| addyosmani-agent-skills@2686b62 | `AGENTS.md` | 92 (5,386) | scope disclaimer :5 · Overview :7 · OpenCode Integration :11 (Core Rules, Intent→Skill, Lifecycle, Execution, Anti-Rationalization) · Orchestration :70 · Creating a Skill :86 | skill-routing mandates, intent map :24-32, pointers | skill anatomy ("Do not restate that guidance here, link to it" :92) | intent→skill mapping table; anti-rationalization list :56-66 |
| addyosmani-agent-skills@2686b62 | `CLAUDE.md` (separate, different content) | 60 (4,094) | Project Structure :7 · Skills by Phase :19 · Conventions :28 · Contributing :37 · Commands :41 · Pull Requests :47 · Boundaries :54 | map, conventions, commands, PR etiquette, Always/Never boundaries | CONTRIBUTING checklist ("do not restate its checklist here" :39) | **Boundaries Always/Never** (:54-60); two different files per tool (no import) |
| addyosmani — `docs/agents.md` | 123 | persona docs (not a root file) | — | — | `skills/context-engineering/SKILL.md:38-72` template: Tech Stack · Commands · Conventions · **Boundaries** · Patterns |
| openclaw-openclaw@b94e5177 | `AGENTS.md` (no root CLAUDE.md; `.claude/skills -> ../.agents/skills`) | 145 (27,918 — very long lines) | precedence + "nearest scoped AGENTS.md" :3-8 · Design priorities :10 · Working agreement :16 · Execution discipline :29 · One owner, complete cutover :42 · Runtime safeguards :66 · Product and validation :81 · Execution gotchas :99 · Authority and safety :109 · **Read when relevant** :126 | principles, process, prohibitions (authority/safety), gotchas, **pointer index** | commands ("`package.json` owns current commands" :25; "Commands and implementation detail stay with these owners" :129) | **34 nested AGENTS.md**; nested `CLAUDE.md` are symlinks → `AGENTS.md` (4/4); "Update instructions at their owner instead of adding competing rules here" (:8); trigger-phrased pointer list :131-145 |
| openclaw nested | `ui/` 111 · `scripts/` 227 · `docs/` 68 · `extensions/` 86 · `test/` 4 | — | each opens with an ownership line ("This directory owns…" `ui/AGENTS.md:3`) and ends with **Scope** ("Keep UI-specific rules here" `ui/AGENTS.md:103-106`) | domain rules, incident-cited rules (`test/AGENTS.md:4` cites #125441…) | repo-global rules ("Leave repo-global … rules in the root" `ui/AGENTS.md:106`) | incident citations live only in nested files |
| mattpocock-skills@d81f3a1 | `CLAUDE.md` (real) ← `AGENTS.md` symlink | 25 (3,850) | no headings: bucket map :1-7 · promotion invariants :9-19 · router upkeep :21 · link script :23 · no em-dashes :25 | repo invariants (README/plugin.json/docs sync), one command (`claude plugin validate` :11), one style rule | commands beyond one, architecture, process | pointers to `.agents/*.md` for every body (:11,17,19) |
| mattpocock — `skills/productivity/writing-for-agents/SKILL.md` | 81+ | guidance | — | — | "context pointer", "two loads", "Negation" failure mode, "environment is a source of truth … a document that restates it is a cache" |
| kunchenguid-firstmate@549e07f | `AGENTS.md` ← `CLAUDE.md` = `@AGENTS.md` | 426 (47,958) | persona :7-17 · §1 Identity & prime directives (5 hard rules :26-43) · §2 Layout · §3 Session start · §4 Harness · §5 Recovery · §6 Projects · §7 Task lifecycle · §8 Supervision · §9 Escalation · §10 Backlog · §11 Briefs · §12 Self-update · §13 Agent-only skills · §14 Relay · Captain precedence :412 · **Maintaining this file** :421 | persona, numbered hard prohibitions, process, pointers to skills | — (it is the whole job description, :9) | **`CLAUDE.md` is `@AGENTS.md` (`CLAUDE.md:1-2`)**; "Skill descriptions are the always-loaded trigger index" (:405); maintenance rule :423-426 |
| jabrena-plinth@5e338bb | `AGENTS.md` | 204 (13,035) | Your role :3 · Tech stack :12 · Change workflow :37 · File structure (READ/WRITE tags) :52 · Commands :69 · Skill acceptance :134 · Website workflow :142 · Git workflow :150 · **Boundaries** :200 | persona, stack, READ-only/WRITE map, full command block, git conventions table | — | **✅ Always / ⚠️ Ask first / 🚫 Never** (:202-204); READ/WRITE tags on map entries (:54-66) |
| imdganesancareers-MasterLaundry@0099d66 | `CLAUDE.md` (real) ← `AGENTS.md` 3-line pointer | 68 (5,186) | identity + prod facts :3 · Quick resume :5 · The owner :12 · How work happens :16 · Think vs build layer :30 · Agent skills :34 · Standards :52 · Commands :56 · After every merge :64 | identity, reading order, human persona, pipeline, pointers, 2 bite-most-often rules, commands, post-merge checklist | standards bodies (`.claude/rules/` × 8, all `paths:`-scoped) | "Two that bite most often" (:54) — names only the top 2 rules in root; nested `docs/CLAUDE.md` (170); E2E guard enforced by config (:62) |
| Jeffallan-claude-skills@882ef55 | `CLAUDE.md` | 311 (11,249) | Skill Authorship Standards :7 · Project Workflow :135 · Release Checklist :157 · Attribution :305 | authoring rules with BAD/GOOD snippets, release checklist with commands | — | progressive-disclosure tiers spec (:116-133); everything inline (counter-example to size advice) |
| cursor-plugins@2eb7ed4 | `continual-learning/agents/agents-memory-updater.md`, `pstack/skills/principle-encode-lessons-in-structure/SKILL.md` | — | guidance | — | — | AGENTS.md learned sections capped "at most 12 bullets" (memory-updater :29); "If the fix is structural, only use the structural fix. The instruction is the symptom." (encode-lessons :21) |
| **ours** (agent-platform@33119a92) | `CLAUDE.md` ← `AGENTS.md` symlink | **482 (32,775)** | identity :1 · Where things live :7 · rules/hooks essay :22-65 · Slash commands :67 · 17 `<important if>` blocks :78-482 | everything: commands, prohibitions, pointers, architecture, style, process, history/incidents, counts | — | `<important if>`; hook table; 6 module `aruvii-*/CLAUDE.md` exist (77-181 lines) but root never points at them |

---

## 2. Published practice (primary sources)

Quotes ≤15 words. Anthropic pages fetched raw; agents.md, Codex and HumanLayer pages came through the
fetch tool's summariser — quoted text is as returned, not byte-checked against the page.

URLs: **[M]** https://code.claude.com/docs/en/memory · **[BP]** https://code.claude.com/docs/en/best-practices ·
**[A]** https://agents.md · **[CX]** https://developers.openai.com/codex/guides/agents-md (308 → https://learn.chatgpt.com/docs/agent-configuration/agents-md) ·
**[HL]** https://www.humanlayer.dev/blog/writing-a-good-claude-md

### Size
| quote | src |
|---|---|
| "target under 200 lines per CLAUDE.md file." | M |
| "Longer files consume more context and reduce adherence." | M |
| "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" | BP |
| "< 300 lines is best, and shorter is even better" | HL |
| "Frontier thinking LLMs can follow ~ 150-200 instructions with reasonable consistency." | HL |
| "32 KiB by default" (`project_doc_max_bytes`) | CX |
| "stops adding files once the combined size reaches the limit." | CX |

### What to include
| quote | src |
|---|---|
| "Bash commands Claude can't guess" | BP |
| "Code style rules that differ from defaults" | BP |
| "Repository etiquette (branch naming, PR conventions)" | BP |
| "Architectural decisions specific to your project" | BP |
| "Common gotchas or non-obvious behaviors" | BP |
| "Developer environment quirks (required env vars)" | BP |
| "Project overview, Build and test commands, Code style guidelines, Testing instructions, Security considerations" | A |
| "Run `npm test` before committing" instead of "Test your changes" | M |
| "tell Claude about the tech, your stack, the project structure" (WHAT/WHY/HOW) | HL |

### What to exclude
| quote | src |
|---|---|
| "Would removing this cause Claude to make mistakes?" If not, cut it. | BP |
| "Anything Claude can figure out by reading code" | BP |
| "Information that changes frequently" | BP |
| "Long explanations or tutorials" | BP |
| "File-by-file descriptions of the codebase" | BP |
| "If you emphasize many lines, none of them stands out." | BP |
| "Never send an LLM to do a linter's job" | HL |
| "avoid auto-generating it" | HL |

### Conditional loading
| quote | src |
|---|---|
| "For domain knowledge or workflows that are only relevant sometimes, use skills instead." | BP |
| "Move instructions that matter for only part of the codebase into path-scoped rules" | M |
| "Imports help you organize a long file but don't reduce its context cost" | M |
| "Claude treats them as context, not enforced configuration." | M |
| "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic" | BP |
| "Prefer pointers to copies" | HL |
| "Block-level HTML comments … are stripped before the content is injected" | M |
| "Project-root CLAUDE.md survives compaction" | M |
| "CLAUDE.md content is delivered as a user message after the system prompt" | M |

### Nesting
| quote | src |
|---|---|
| "The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything." | A |
| "Files in subdirectories load on demand when Claude reads files in those directories." | M |
| "Files closer to your current directory override earlier guidance" | CX |
| "Codex concatenates files from the root down, joining them with blank lines." | CX |

### Tool-agnostic
| quote | src |
|---|---|
| "we chose a name and format that could work for anyone." | A |
| "putting an `@AGENTS.md` import in a `CLAUDE.md` next to it" | M |
| "Keeping the import never makes Claude read `AGENTS.md` twice" | M |

---

## 3. Distilled rules for our AGENTS.md

Backers counted across the 17 reference files (14 root + 3 humanlayer nested) + 5 guidance sources (improve-claude-md,
writing-for-agents, addy context-engineering, pstack, firstmate §Maintaining).

| # | rule | backed by | contradicted by |
|---|---|---|---|
| D1 | **< 200 lines, < 32 KiB** — hard ceiling, Codex truncates past 32 KiB | 13: M, BP, HL, CX, improve-claude-md :63-67, fold 41, agentlayer 36, humanlayer 88, mattpocock 25, MasterLaundry 68, addy 60/92, openclaw 145, firstmate :426 ("keep the always-loaded contract concise") | firstmate (426 L), Jeffallan (311 L), plinth (204 L) by practice |
| D2 | **Only what the agent gets wrong without being told** — corrections to training defaults, project-specific gotchas | 9: BP ("Would removing this…"), mattpocock writing-for-agents (no-ops), improve-claude-md :69, HL (universally applicable), firstmate :424, fold :33-41 (v4 not v3), claudelayer :4-19 (Bun not Node), MasterLaundry :54 ("two that bite most often"), A | none |
| D3 | **Commands it must run and cannot guess** | 10: BP, A, improve-claude-md :72-74 ("Keep all commands"), fold, agentlayer, humanlayer, plinth, MasterLaundry, addy CLAUDE, addy context-engineering | **openclaw :25/:129** and **writing-for-agents** (environment is source of truth; restating `make help` is a cache) — resolve: list only the few gate commands, point at `make help` for the rest |
| D4 | **Pointers, not bodies** — one line naming the target + its trigger | 9: HL, BP ("link to docs instead"), M (path rules, skills), writing-for-agents (context pointers), openclaw :126-145, addy AGENTS :92 / CLAUDE :39, MasterLaundry :7-10, firstmate :424, mattpocock :11-19 | **improve-claude-md :59** ("Do not shard … unless incredibly verbose") — ours is verbose, so the exception applies |
| D5 | **Prohibitions only where damage is unrecoverable or reaches someone else**; pair with the positive target | 8: firstmate hard rules :28-43, plinth :204, addy :54-60, openclaw :109-124, hld :3, MasterLaundry :28, writing-for-agents (Negation: prohibition "only as a hard guardrail"), BP (hooks "zero exceptions") | 12-factor (blanket shouting) — anti-example |
| D6 | **Anything a hook/linter/compiler enforces leaves the root** (or shrinks to one line naming the tool) | 6: improve-claude-md :68, HL, BP, M, pstack encode-lessons :21, fold :10 | none. Corollary: an **ungated** rule (semgrep deleted, `CLAUDE.md:167`) is exactly what *must* stay as text |
| D7 | **No history, incidents, rationale essays, or counts in root** — WHY goes to the reference or an HTML comment | 6: BP (long explanations; changes frequently), M (HTML comments stripped), firstmate :423, openclaw (incidents only in nested `test/AGENTS.md:4`), our own `CLAUDE.md:439` | none in a root file |
| D8 | **Identity + map bare at top** | 9: improve-claude-md :22-28, HL, A, fold, agentlayer, humanlayer, addy CLAUDE, plinth, MasterLaundry | none |
| D9 | **Scoped content goes to the scope's own mechanism** (nested file / path rule / skill), not a root block | 7: M, BP, A, CX, openclaw (34 nested), humanlayer (3 nested), MasterLaundry (8 `paths:` rules + `docs/CLAUDE.md`) | improve-claude-md (inline `<important if>` instead) — 1 source, 0 repos |
| D10 | **One meaning, one owner** — root never restates a rule file/skill | 5: openclaw :8, writing-for-agents (Pruning), addy :92, M (Consistency), ui/AGENTS.md :103-106 | none |
| D11 | **One file for all tools**: AGENTS.md real, `CLAUDE.md` = `@AGENTS.md` | 4: firstmate `CLAUDE.md:1-2`, M, A, openclaw (nested CLAUDE→AGENTS symlinks) | MasterLaundry (inverted), addy (two divergent files), agentlayer (two copies) |
| D12 | **Emphasis rationed** — bold/IMPORTANT on the one line that keeps being skipped | 3: BP, agentlayer :27 (one `_IMPORTANT_`), writing-for-agents (leading words) | 12-factor |
| D13 | **Say how the file is maintained** (what may enter root) | 3: firstmate :421-426, openclaw :8, cursor memory-updater (≤12 bullets per section) | — |

---

## 4. Applied to ours

Target paths per `ONE-RULEBOOK-SKELETON.md:21-31` (`.agents/skills/<domain>/references/…`).
Rule tags = §3. "Ln" = `CLAUDE.md` line on master (identical to this worktree).

### 4.0 Header — `CLAUDE.md:1-77` (77 lines → ~25)

| lines | keep / drop | proposed root text | rule |
|---|---|---|---|
| 1-5 | **keep, 1 line** | "Aruvii — self-hosted AI agent platform. Java 25 · Spring Boot 4 · Spring AI 2 · PostgreSQL · Redis · Angular 21 · Gradle." | D8 |
| 4-5 "Spock 2 for every new test" | move into tests block | (see 4.6) | D2 |
| 9-14, 19-20 | **keep** (pointer table, 6 rows) | CONTEXT.md read-first · spec/arch/adr · roadmap/guides · issue tracker `glab` · triage labels | D4, D8 |
| 15 Wiremock | drop → `docs/guides/DEVELOPING.md` | — | D2 (rare) |
| 16 skills list | drop | skill descriptions are the trigger index (firstmate :405) | D10 |
| 17 subagent/stage essay (1 row, ~600 chars) | drop → `.agents/skills/crq/SKILL.md` | — | D7, D10 |
| 18 agent-skill config | keep, shortened | "`docs/agents/` — per-repo answers for mattpocock skills; edit there." | D4 |
| 22-28 rules mechanics | drop (Claude Code docs own it) | — | D2 (not project-specific) |
| 30-31 | **keep, 1 bullet** | "Path rules in `.claude/rules/` load when you READ a matching file, not create one — read a sibling first (L30-31)." | D2 gotcha |
| 32-33 #500 story | drop → `meta/references/rule-layers.md` | — | D7 |
| 35-65 hook table, advisory list, semgrep note, SessionStart, hook-from-rule | drop → `.agents/skills/meta/references/rule-layers.md` | — | D6 (a hook speaks when it fires), D7 |
| 56 "Two `SessionStart` hooks" | **false** — settings.json has 1 | fix in reference | D7 |
| 60-61 compaction claim | **contradicts [M]** for the root file; may hold only for `paths:`-less rules | re-verify before moving | — |
| 67-76 slash commands | **keep, 4 lines** | `/crq` · `/issue` · `/refine` · `/dod` one line each; drop L75-76 | D3 |
| **new** | add | "Nearest `aruvii-*/AGENTS.md` (today `CLAUDE.md`) owns module rules; read it before editing that module." | D9, gap G5 |

### 4.1 Block `:78` — starting a change (12 lines)
1. "Every change starts with `/crq`; implementation waits for the human's `/approved` on the draft MR (L80-82)." — D5
2. "Never post `/approved` yourself and never merge to `master` (L82-83)." — D5 (reaches others)
3. "Write the failing test first; take business rules and names from `docs/spec/`, never invent them (L85-88)." — D2

Pointer → `.agents/skills/crq/SKILL.md`. Drop: L86-87 "one question per blocker / no extra fields" (crq grill owns it, D10).

### 4.2 Block `:91` — build/test/deploy (50 lines)
1. "Run every gate through `make` — never hand-assemble `verify`, `smoke`, `deploy`; `npm run smoke*` does not deploy (L93-97)." — D3, D2
2. "Use absolute paths, not `cd <dir> && <cmd>` — the `cd` forces a permission prompt (L134-135)." — D2
3. (optional) 4-row command list: `make doctor` · `make verify-module MOD=` · `make verify-full` · `make smoke [FULL=1]` (L100-106); "`make help` lists the rest." — D3 vs openclaw/writing-for-agents: keep only the four

Pointer → `.agents/skills/delivery/references/verification.md` + `make help`. Drop: L109-122 remaining commands (in `make help`), L124-133 Maven-era history (D7), L137-139 (discoverable / pointer already in header).

### 4.3 Block `:142` — relying on a green build (42 lines) — **merge into 4.17**
1. "There is no CI: `make verify-full` on your machine is the only gate (L144)." — D2
2. "Never pipe a gate through `| tail`; redirect and `echo $?` (L165-166)." — D2; advisory hook `warn-piped-gate.sh` exists → drop if the hook is made blocking (D6)
3. "Check no other build is running before starting one; a whole-module failure is Docker contention (L160-163)." — D2; advisory hook `guard-concurrent-build.sh` → same D6 note

Pointer → `delivery/references/verification.md`. Drop: L145-150 #440 history (D7), L151-159 cache essay, L167-170 + L180-182 semgrep (duplicated twice inside one block — D10) → `meta/references/rule-layers.md`, L171-175 CVE gap → ARCHITECTURE §Doc drift / #456, L176-179 coverage floors ("eleven modules" = rotting count, D7).

### 4.4 Block `:185` — Java (14 lines) — **references would delete from root**
`.claude/rules/java-standards.md` (`paths: **/*.java`) loads on the first `.java` read; this block restates it (D9, D10).
Before deleting, move what the rule lacks: `grep -c 'domain/' java-standards.md` → 0, so L187-189 (layers) must move first.
If one line stays: "`domain/` imports no framework; never leak JPA or Spring types into it (L187-189)." — D2.
Drop: L190-196 (style — D6 Checkstyle/review owns), L197 pointer (rule file is itself the pointer).

### 4.5 Block `:200` — imports/dependencies (17 lines) — **keep; fix condition**
Condition names `pom.xml` — repo has none (Gradle). New condition: "adding an import or dependency, or editing `build.gradle.kts` / `package.json`".
`dependencies.md` is scoped to build files, so import rules in `.java` would never load from it → these stay in root.
1. "Jackson 3 only: `tools.jackson.*`, never `com.fasterxml.jackson.{core,databind,…}`; `jackson.annotation` is allowed (L209-211)." — D2 (training default is fasterxml), ungated (L167)
2. "Jakarta only: never `javax.persistence|servlet|validation|annotation|inject`; Java SE `javax.*` is fine (L205-208)." — D2, ungated
3. "Spring AI types never leave `aruvii-worker`; `aruvii-shared` imports no Spring/JPA (L202-204)." — D2 (also in module files: worker 5 hits, shared 4)

Pointer → `.claude/rules/dependencies.md`. Drop: L212-215 BOM rule from root (already in `dependencies.md`, which loads on exactly those files — D10).

### 4.6 Block `:218` — tests (18 lines)
1. "ITs go under `src/integrationTest`, never `src/test` — a misplaced IT passes silently (L223-225)." — D2, advisory hook only
2. "Testcontainers not H2, `RestTestClient` not MockMvc, fake ports not `@MockitoBean` (L233)." — D2
3. "New tests are Spock; every new class gets unit tests, every new endpoint an `*IT` (L4, L220-221)." — D2

Pointer → `.agents/skills/testing/references/{unit-tests,integration-tests}.md`. Drop: L226-228 #440 history (D7), L229-232 parallelism config (reference), "80%+" (coverage gate enforces — D6).

### 4.7 Block `:237` — smoke (8 lines) — **references would delete; fold into 4.17**
L239-241 restate *Done means*; authoring is `.claude/rules/smoke.md` (`paths: **/smoke-*.spec.ts`) + `testing/references/smoke-specs.md`. Root keeps nothing extra (D10). Read-before-create gotcha is covered by header bullet.

### 4.8 Block `:246` — Angular (10 lines) — **references would delete from root**
`angular-ui.md` (`paths: aruvii-ui/**`) owns it. Move first: "Standalone, no NgModules" (L248 — `grep NgModule angular-ui.md` → 0). L253-254 "wired to the real API" already in *Done means* (L464-465). Root keeps nothing (D9, D10).

### 4.9 Block `:257` — API endpoints (11 lines) — **references would move to `aruvii-api` nested file**
`aruvii-api/CLAUDE.md` already mentions `PUBLIC_PATHS` (2) and `ApiResponse` (2). If kept in root:
1. "Adding to `SecurityConfig.PUBLIC_PATHS` is a security decision — state what replaces the JWT (L262-265)." — D5
2. "Every RBAC rule is enforced and tested; errors are ProblemDetail, bodies `ApiResponse<T>` (L259-261)." — D2
3. "No edition checks — feature flags only (L266)." — D2

Pointer → `aruvii-api/AGENTS.md`. Recommend keeping only #1 in root (the one whose damage reaches customers).

### 4.10 Block `:269` — credentials/LLM (15 lines) — **keep**
1. "Encrypt every credential with `CredentialEncryptor` before DB write; never return one unmasked (L271-272)." — D5
2. "Rate limiting must be active before any LLM call reaches a provider (L273)." — D5
3. "Add no new `decrypt(...)` outside `ToolHandler.execute()`; existing sites are not precedent (L274, L281-282)." — D5, ungated

Pointer → `.agents/skills/code/references/security.md`. Drop: L275-280 site inventory ("15 production sites" — rotting count; `grep -c 'decrypt('` over `aruvii-*/src/main` now finds 31 call expressions, not comparable but shows drift risk) → reference / ARCHITECTURE §Doc drift.

### 4.11 Block `:285` — migrations (8 lines)
1. "Never edit an applied migration; create new ones only via `migrations/workflows/new-migration.md` (L287-288)." — D5; both halves hook-blocked (`block-migration-edit.sh`, `check-migration-version.sh`) so D6 says one line suffices; kept because `migrations.md` does not load on *create* (L30-31)

Pointer → `.agents/skills/migrations/workflows/new-migration.md`. Drop: L290-291 feature flags — unrelated to migrations (improve-claude-md principle 2: never group unrelated rules) → `docs/CONTEXT.md`.

### 4.12 Block `:294` — logging (8 lines) — **references would delete from root**
`observability.md` (`paths: **/*.java`) loads on any Java read. Before deleting, check it carries L297-299 (`grep -c 'action=' observability.md` → 0; verify wording). If one line stays: "Customer is on-call: a failed run must be triageable from logs alone (L296)." — D8 (WHY).
Pointer → `.agents/skills/obs/references/logging.md`.

### 4.13 Block `:303` — branch/commit/MR (**88 lines**, largest)
1. "One issue → one branch → one MR, in a worktree; stage explicit paths, never `git add -A` (L305-307)." — D5
2. "MR title `type(area): subject (#NNN)`; description opens `Closes #NNN` (L313, L374)." — D2 (unvalidated by anything, L316)
3. "No AI attribution trailers — no `Co-Authored-By: Claude`, no `Generated with` footer (L380-381)." — D2, D5 (harness default appends one; this session's own system prompt does)

Pointer → `.agents/skills/delivery/SKILL.md` + `references/git.md`, `workflows/cleanup.md`. Drop: L307-308 never-merge (in 4.1 #2 + hook), L310-311, L318-361 examples/commitizen/what-is-checked (body rule hook-enforced by `.husky/commit-msg` — D6; `make doctor` reports missing `cz`), L362-372 #455 history box (D7), L377-379 editorialising, L382-383 git config, L384-389 → delivery.

### 4.14 Block `:392` — worktrees (13 lines) — **keep**
1. "Never run `make secrets` in a worktree — a new master key cannot decrypt the shared volume (L398-399)." — D5 (unrecoverable)
2. "Never `COMPOSE_PROJECT_NAME=agent-platform make smoke FULL=1 DEPLOY=0` — it smokes another checkout's images (L400-401)." — D5
3. "All worktrees share one Compose stack; last deploy wins — check `make status` for `STALE` (L394-396)." — D2

Pointer → `.agents/skills/delivery/references/worktrees.md`.

### 4.15 Block `:406` — new tool type (23 lines) — **references would move to `aruvii-tools` nested file**
1. "A new tool type owes `outputSchemaJson`, `sampleResponseJson` and a smoke dry-run test (L408-410)." — D2 (review-only, "have been missed" L419)
2. "Read the required arguments off the handler; never declare a schema stricter than it (L423-426)." — D2

Drop: L413-416 `inputContract` (compiler enforces — D6, the block says so itself), L418-421 history (D7). Pointer → `aruvii-tools/AGENTS.md` (today `CLAUDE.md`, mentions dry-run once, `inputContract` 0×).

### 4.16 Block `:430` — documentation (25 lines)
1. "No `[confirmed: …]` stamps and no counts that rot — name the thing, not the tally (L432, L439)." — D2
2. "A new REQ takes the issue number (`#344` → `REQ-344-…`), never the next free slot (L449-450)." — D5 (cross-branch collision, happened 3×)
3. "A bug corrects the existing REQ in place; never open a second spec beside it (L446-448)." — D2

Pointer → `.agents/skills/planning/references/writing-docs.md`. Drop: L434-437, L440-444, L451-453 (D7). **Note:** the root file breaks rule 1 itself — "seven rule files" (L22), "Three block" (L40), "Two `SessionStart` hooks" (L56, false), "76+" (L106), "115 actionable tasks" (L155), "eleven modules" (L176), "15 production sites" (L275), "nine of twelve" (L419), "65 stamps" (L434), "81 tests" (L214), "100 pipelines, 98 failed" (L147).

### 4.17 Block `:456` — declaring done (27 lines) — absorb 4.3 and 4.7
1. "Done = `make verify-full` green on a clean tree at the MR head, smoke report 0 failed (L467)." — D3, D2
2. "The MR records SHA, where it ran, report link, and the `deployed: <branch> @ <sha>` line (L473-476)." — D2
3. "Never stop or deploy over a running smoke or deploy — the shared stack is a queue (L478)." — D5 (reaches others)

Pointer → `.agents/skills/dod/SKILL.md` + `docs/guides/DEVELOPING.md` §Handing off. Drop: L458-460 pre-sprint checklist (→ DEVELOPING), L464-466 (spec/RBAC/UI — already in 4.1/4.9), L470-472, L477, L481 (D7). This block's tail is what Codex currently truncates.

### 4.18 Blocks the references would remove from root entirely

```
 :185 Java        → .claude/rules/java-standards.md   (move "domain/" bullet first)
 :237 smoke       → .claude/rules/smoke.md + Done means
 :246 Angular     → .claude/rules/angular-ui.md       (move "no NgModules" first)
 :294 logging     → .claude/rules/observability.md    (verify action= wording first)
 :257 API         → aruvii-api nested file            (keep PUBLIC_PATHS line if anything)
 :406 tool type   → aruvii-tools nested file
 :142 + :237      → merged into :456
```

Projected size: header ~25 + 10 surviving blocks × ~6 = ~85-100 lines, ≈ 8-10 KB.

---

## 5. Gap list — in reference roots, absent from ours

| # | gap | where it is done |
|---|---|---|
| G1 | **Boundaries triad** — one place listing Always / Ask first / Never | plinth `AGENTS.md:200-204`; addy `CLAUDE.md:54-60`; addy context-engineering template :64-68 |
| G2 | **Precedence line** — explicit user instruction overrides file rules; nearest file wins | openclaw :3-7; firstmate :412-419; agents.md |
| G3 | **"Maintaining this file"** — what may enter root, prune-over-append | firstmate :421-426; openclaw :8 |
| G4 | **Trigger-phrased pointer index** ("Storage: read X before changing schema") rather than a noun table | openclaw :126-145 |
| G5 | **Pointer to nested files** — ours has 6 `aruvii-*/CLAUDE.md` (77-181 lines) and never mentions them | openclaw :6-7 ("Read the nearest scoped `AGENTS.md`") |
| G6 | **What the agent cannot do / where logs are** for debugging the running system | `hld/CLAUDE.md:3-11`; `humanlayer-wui/CLAUDE.md:5-16` |
| G7 | **Maintainer notes as HTML comments** — keep WHY/history out of context but in the file | [M] block-level HTML comments stripped |
| G8 | **Compaction instruction** ("when compacting, preserve …") | [BP] Manage context |
| G9 | **"Two that bite most often"** — naming the top rules from the path-scoped set in one line | MasterLaundry `CLAUDE.md:54` |
| G10 | **Ownership/scope header in nested files** ("This directory owns…" / "Keep X rules here") — for the coming module `AGENTS.md` ticket | openclaw `ui/AGENTS.md:3,103-106`, `docs/AGENTS.md:3` |

Not gaps (ours has them): issue tracker + labels pointers (MasterLaundry :36-42), read-first orientation doc (MasterLaundry :7), single front-door command (`make`, cf. agentlayer `bun check`).

---

## 6. Verification commands run

```
wc -l / wc -c on every file in §1                    # line + byte counts
git -C refs/<repo> rev-parse --short HEAD            # SHAs
grep -c '<important if' <each ref file>              # 0 in all 17
grep -c '<important if' CLAUDE.md → 17 ; '</important>' → 17
awk block ranges → :78-89 … :456-482 (sizes in §4)
wc -c CLAUDE.md → 32775 (Codex cap 32768)
grep -o '\*\*' CLAUDE.md | wc -l → 274 (137 spans) ; grep -c '\*\*' → 129 lines
grep -o '#[0-9]\{3\}' CLAUDE.md | wc -l → 17
python3 … settings.json SessionStart → 1 hook (always-on-output-rules.sh)
ls pom.xml → absent ; build.gradle.kts present
find refs/openclaw-openclaw -name AGENTS.md → 34 ; nested CLAUDE.md symlinks → 4/4
diff humanlayer/scripts/CLAUDE.md claudelayer/CLAUDE.md → identical
diff humanlayer-skills/.../improve-claude-md/SKILL.md ~/.claude/skills/... → identical
grep -c in .claude/rules/* for AssertJ, domain/, app-icon, NgModule, action=, tools.jackson, javax, RestTestClient, FULL=1
grep -c -i in aruvii-*/CLAUDE.md for dry-run, inputContract, Spring, PUBLIC_PATHS, ApiResponse, decrypt
```
