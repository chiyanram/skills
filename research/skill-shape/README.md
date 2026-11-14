# pstack + humanlayer: how they hold large rule bodies

Measured with `wc -w`. "Side" = every other `.md` in the skill folder (scripts, test corpora, yaml excluded).
Clones (depth 1) under `research/`: `cursor-plugins/`, `humanlayer/`, `hl-skills/`, `ace/`.

## Paths that exist / do not

| Asked for | Status |
|---|---|
| `cursor/plugins` `pstack/skills/*` | exists, 58 skills |
| `pstack/playbooks/` | **does not exist**. Playbooks live at `pstack/skills/poteto-mode/playbooks/` (23 files) |
| `principle-*` skills | exist, 24 |
| `humanlayer/humanlayer/.claude/commands`, `.claude/agents` | **do not exist**. `.claude/skills/` has 27 skills |
| `humanlayer/skills` | exists, 7 plugins (`plugins/*/skills/*`), plus `plugins/rpi/agents/` (5 agents) |
| humanlayer extra sets | `apps/riptide-rpi-claude-plugin/skills` (22), `apps/riptide-pi-extension/skills` (17, near copy), `apps/riptide-humanlayer-claude-plugin/skills` (3) |
| 12-factor-agents | not cloned: about agent apps, not skill shape |
| advanced-context-engineering | cloned; no guidance on skill size (only `ace/wsff.md:489` says their first program-design skill "was hard to read") |

## 1. pstack (cursor/plugins/pstack)

### Numbers (58 skills)

| | min | median | max | total |
|---|---|---|---|---|
| SKILL.md words | 40 (`bro`) | 401 | 3,397 (`poteto-mode`) | 36,085 |
| side .md words | 0 | 0 | 13,948 (`poteto-mode`) | 32,205 |
| 24 `principle-*` SKILL.md | 54 | 208 | 451 | 5,147 |

49 of 58 skills have zero side files. Skills with side files:

| skill | SKILL | side files | side words | shape |
|---|---|---|---|---|
| poteto-mode | 3,397 | 24 (23 playbooks + 1 ref) | 13,948 | hub: triggers + principle index + playbook index |
| why | 1,316 | 12 | 6,570 | steps + per-source refs (`references/sources/<mcp>.md`) |
| statechart | 1,707 | 34 (mostly test corpus) | 3,285 | tool skill |
| reflect | 715 | 4 | 2,392 | steps + subagent prompts |
| architect | 815 | 3 | 1,420 | steps + prompts |
| typescript-best-practices | 437 | 1 | 1,381 | rule table + `references/patterns.md` examples |
| create-verification-skill | 1,059 | 3 | 1,367 | steps + example |
| poteto-help | 2,438 | 2 | 1,194 | help/map |
| how | 399 | 2 | 648 | steps + prompt |

Full per-skill table: `../pstack.tsv` (cols: name, SKILL words, side count, side words, non-md files).

Playbooks (poteto-mode/playbooks): 127 (`authoring-a-skill`) to 2,242 (`multi-phase-plan`); median ~370.

### Pattern: "hub + atomic principle skills + playbooks that cite them"

```
poteto-mode/SKILL.md (hub, 3.4k)
 ├─ Non-negotiables: trigger -> skill name          (one line each)
 ├─ Principles index: name + WHEN + one-line rule   (24 lines, ~25 words each)
 │     └─ leaf: principle-<kebab>/SKILL.md           (54–451 words, read in full when applied)
 └─ Playbooks index: name + when                    (23 lines)
       └─ playbooks/<kebab>.md: numbered steps       (127–2,242 words)
             step text names **principle-x** inline at the step where it bites
```

- One principle = one skill. Body = rule, `**Why:**`, `**Pattern:**` bullets, "sign you skipped this". E.g. `principle-fix-root-causes` 324 words.
- The **description carries the rule**, not only the trigger: `principle-exhaust-the-design-space/SKILL.md:3` holds "Build 2-3 competing prototypes and compare side by side"; the body (54 words) adds only the edge case.
- 57/58 skills set `disable-model-invocation: true` (only `setup-pstack` does not). Principles are never auto-loaded; reached only through the hub index or a playbook step.
- The hub index line duplicates the rule in ~20 words, so the agent gets the gist without a read; full read required before citing (`poteto-mode/SKILL.md:15`, `:41`).
- Playbooks are step lists that weave principles in at the step: `playbooks/refactoring.md:8-12` cites model-the-domain, foundational-thinking, redesign, subtract-before-you-add, migrate-callers, prove-it-works — one per step.
- Name-as-handle: the principle name is a steering word (`docs/guide/08-principles.md:5` "Each name points at a complete rule the agent has already read, so one phrase redirects the work more precisely than a paragraph").
- Stack rules = rule table: `typescript-best-practices/SKILL.md:12-29` — 16 rows `| Rule | Summary |`, examples pushed to `references/patterns.md`, and "Apply the **type-system-discipline** principle skill first" (`:10`) instead of restating it.
- Lookup-by-source: `why/SKILL.md:52` loads `references/sources/<source>.md` only for the MCP present.

### Written guidance in repo

- `skills/poteto-mode/playbooks/authoring-a-skill.md:10` — "When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. ... Delegate to other skills by path. Don't restate."
- `skills/principle-encode-lessons-in-structure/SKILL.md:3` — on a repeated instruction, "Encode the rule as a lint, metadata flag, runtime check, or script instead of more text"; `:11` "If the fix is structural, only use the structural fix. The instruction is the symptom."
- `docs/guide/09-make-it-yours.md:35-40` — ranking: architecture > types/lint > test > "doc or agent rule ... comes last". `:31` "Approve a proposal only if it would change a future decision. One weird session is an anecdote, not a rule."
- `skills/poteto-mode/SKILL.md:116` — "Each playbook's own reply lines name only the content unique to that playbook" (shared rules once, in the hub).
- No numeric size cap found (grep for word/line budget, progressive disclosure: none).

### Two examples

1. **Engineering judgment (~5.1k words of principles).** Split into 24 one-rule skills in 4 groups (Core 10, Architecture 6, Verification 5, Delegation 2, Meta 1; `poteto-mode/SKILL.md:43-80`). Hub carries a 1-line WHEN + rule per principle; leaf holds why/pattern/symptom.
2. **"How to do a task" (~14k words).** Split by task type into 23 playbooks (bug-fix 368, refactoring 477, feature 399, shipping 771, babysit 1,225...). Each is numbered steps + a `**Reply:**` line; cross-cutting reply/comment rules live once in the hub (`:104-120`).

## 2. humanlayer

### Numbers

| set | n | SKILL min | median | max | side median | side max | SKILL sum | side sum |
|---|---|---|---|---|---|---|---|---|
| `humanlayer/.claude/skills` | 27 | 44 | 914 | 3,047 | 0 | 12,579 | 26,797 | 28,391 |
| `apps/riptide-rpi-claude-plugin/skills` | 22 | 244 | 1,009 | 2,595 | 106 | 2,128 | 26,119 | 6,841 |
| `humanlayer/skills` plugins | 7 | 462 | 1,183 | 2,241 | 742 | 14,860 | 8,550 | 22,746 |
| `humanlayer/skills/plugins/rpi/agents` | 5 | 673 | 814 | 1,017 | – | – | 4,104 | – |

Per-skill tables: `../hl-.claude_skills.tsv`, `../hl-apps_riptide-rpi-claude-plugin_skills.tsv`, `../hlskills.tsv`.

Largest bodies:

| skill | SKILL | side files | side words | shape |
|---|---|---|---|---|
| `.claude/skills/effect-program-design` | 1,277 | 17 refs + attribution | 12,579 | creed + defaults + trigger-keyed router |
| `hl-skills/plugins/rpi` | 768 | 52 | 14,860 | phase router -> `references/<step>/process.md` |
| `.claude/skills/no-use-effect` | 914 | 1 | 6,420 | rules + one big reference doc |
| `.claude/skills/agent-browser` | 3,047 | 7 | 4,683 | CLI manual + per-feature refs |
| `hl-skills/plugins/design-control-loop` | 2,241 | 8 | 4,262 | steps + templates |
| `.claude/skills/ui-copy` | 2,476 | 0 | 0 | flat rule list |

### Pattern A: "creed + defaults + trigger-keyed reference router" (effect-program-design)

```
SKILL.md 1,277 words
 ├─ Source rule (4 lines: check CLAUDE.md, installed versions, docs, source)
 ├─ References: "<trigger words>: references/X.md"   (17 lines)   :28-53
 │     "Read only the references relevant to the task; read all matching branches when work crosses concerns." :30
 │     MUST-read flags inline: DEEP_MODULES :32, TESTING :78
 ├─ The creed: 7 numbered non-negotiables, bold lead word   :55-84
 ├─ Core defaults: ~20 one-line bullets                      :86-113
 └─ Testing defaults
references/ 372 – 1,311 words each (median ~660)
```
The always-on rules (creed + defaults) sit in SKILL.md; refs hold per-concern depth. Closest analogue to our `code` skill (651 router + 37k / 17 refs) but refs total 12.4k, ~1/3 of ours.

### Pattern B: "phase router + one process file per step + shared style refs" (rpi)

Same workflow shipped twice:

| form | files | words |
|---|---|---|
| 22 standalone skills, `apps/riptide-rpi-claude-plugin/skills` | 22 SKILL.md + 39 side | 26,119 + 6,841 = ~33k |
| 1 router skill, `hl-skills/plugins/rpi` | 768 SKILL + 52 side (+5 agents 4.1k) | 768 + 14,860 = ~15.6k |

`create-research`: 2,465-word SKILL (headings incl. "Document Style and Format", "Writing and citation style", "Visual structure") -> 792-word `references/create-research/process.md`, 9 numbered steps. The style sections left the step file and became shared `references/prose.md` (257) + `references/show-me.md` (460), read once at a fixed step: `rpi/SKILL.md:57` "After writing or updating a workflow document, read ... prose.md and ... show-me.md, then review the document against both." Final-answer templates moved to per-step `final_answer` files, read at the last step. Router table `rpi/SKILL.md:26-35`. Conditional loads use `<important if="...">` (`:69-81`).

### Written guidance in repo

- `hl-skills/plugins/improve-claude-md/skills/improve-claude-md/SKILL.md`:
  - `:14` "The more content that isn't applicable to the current task, the more likely Claude is to ignore everything — including the parts that matter."
  - `:28` "if it's relevant to 90%+ of tasks, leave it bare. If it's relevant to a specific kind of work, wrap it."
  - `:59` "Do not shard into separate files that require the agent to make tool calls to discover, unless the extra context is incredibly verbose or complex."
  - `:67` "Frontier models can reliably follow a few hundred [instructions]."
  - `:68-70` cut what a linter/hook enforces, what code patterns show, and code snippets ("go stale and bloat").
  - `:119` "split any list of rules into individual `<important if>` blocks ... never group unrelated rules under one broad condition."
- `hl-skills/plugins/build-iterated-agentic-loop/.../references/skill-template.md:3` — description template "<leading verb> <task> when <trigger>; use <source of truth> instead of <wrong source>".
- `rpi/SKILL.md:57` — "cut words and sections that do not earn their place".
- No numeric SKILL.md cap found.

### Two examples

1. **Effect program design (~13.9k).** Split by concern (17 refs: services/layers, errors, schema, config, persistence, concurrency, scheduling, streams, caching, HTTP, testing, platform, node, atom, TS contracts, examples). Always-on creed + defaults in the 1,277-word SKILL.md.
2. **RPI workflow (~33k as 22 skills -> ~15.6k as 1 router).** Split by sequence (phase x create/iterate = 14 process files) with cross-cutting style factored into 2 shared refs and templates into per-step files.

## How both keep rules without bloat

| technique | pstack | humanlayer |
|---|---|---|
| one rule = one unit with a name | 24 `principle-*` skills | `<important if>` block per rule (CLAUDE.md) |
| always-on index with the rule's gist | hub principle index, ~20 words/rule | creed + core defaults in SKILL.md |
| depth loaded by trigger | "read leaf in full when applied" | "<trigger words>: references/X.md" |
| procedure = numbered steps citing rules at the step | playbooks name **principle-x** inline | process.md steps; read prose/show-me at review step |
| cross-cutting rules said once | reply/comment rules in hub only | prose.md + show-me.md shared by 14 phases |
| move rules out of text into structure | encode-lessons-in-structure, `/correct` ranking | cut linter/hook territory (`:68`) |
| rule in description | principle descriptions hold the rule | template: verb + trigger + source of truth |

## Compared to baselines

| collection | SKILL.md words | side words |
|---|---|---|
| mattpocock | 60–2,075 | 0–2.1k |
| obra/superpowers | 485–4,825 | up to 9.4k |
| vercel-labs | 177–2,130 router | 5k–27.5k |
| pstack | 40–3,397, median 401 (principles 54–451, median 208) | 0–13.9k, median 0 |
| humanlayer `.claude` / skills repo | 44–3,047, median 914–1,183 | 0–14.9k |
| our `code` | 651 router | 37k / 17 refs |

1. Neither repo has a numeric cap; both cut by "does it change a decision" and by moving rules into lint/structure.
2. pstack keeps rule count high by making each rule tiny and named (median 208 words), indexed in a hub, cited inside step-based playbooks.
3. humanlayer's effect-program-design is our shape (router + 17 refs) but with always-on creed/defaults in SKILL.md and refs at ~660 words median, 728 mean (ours 37k/17 = ~2.2k mean).
4. rpi shows the reshape we want: per-step process files (~200–800) + shared style refs read at one fixed step, ~53% fewer words than the 22-skill form.
5. Our 37k is ~2.7x effect-program-design refs and ~2.5x pstack's whole playbook set; the move is principle-sized leaves + step procedures that cite them, not one-file-per-topic refs.
