# Reference format — the template every reference follows

Draft consolidated 2026-10-02 from decisions already taken. Each line cites where it was decided. G10 (#37) owns this file; its checklist and proof method are decided there.
Amended 2026-10-17: Rule line (G21 #91), Good/Bad examples and location (G23 #93).
Amended 2026-10-29: `references/examples/<topic>.md` holds every approved pair when a reference cannot (operator, #31).
Amended 2026-11-02: the router table is built by `make index` from each reference (agent-factory#46).

## Where a reference sits

```
chiyanram/skills  (plugin marketplace — generic, installed as a plugin, never copied)
├── <domain>/                            knowledge skill: testing · code · obs · migrations · delivery · planning
│   ├── SKILL.md                         router: frontmatter + "which reference to load" table (`make index`)
│   ├── references/<topic>.md            ← THIS TEMPLATE (neutral-domain examples)
│   ├── references/examples/<topic>.md   every approved Good/Bad pair, when the reference cannot hold them all
│   └── scripts/                         mechanical checks the references name
└── <workflow>/SKILL.md                  generic workflow skill (flat, own /name): crq · deslop · …

agent-platform  (Aruvii only)
├── AGENTS.md · <dir>/AGENTS.md          index + Aruvii MUSTs; CLAUDE.md = @AGENTS.md
├── docs/agents/*.md                     Aruvii answers for generic skills: crq.md (gate, lane floor paths,
│                                        role labels) · issue-tracker.md (forge adapter = glab) · …
└── .agents/skills/<aruvii-skill>/       Aruvii-only skills: flyway-migration · aruvii-git · aruvii-cleanup ·
                                         v1-status · smoke-spec
```
The plugin's exact directory layout is build work (skills #99, map #9 G24). Sources: G1 (#5, 4 layers), #643 design
(hybrid: workflows flat, knowledge in domains), G5 (#13, one file per topic), G1b skills #72 (`.claude/rules/` deleted →
nested AGENTS.md), G23 #93 (generic vs project; crq is generic).

## Above the five sections

A title, then one paragraph: what the reference covers, and one sentence starting "Read it when …" or "Read it
before …". `make index` copies that sentence and the rule IDs into the domain router's table (agent-factory#46).

## The five sections, in this order

| section | holds | rule for writing it | decided in |
|---|---|---|---|
| **Rules** | the approved rules, one line each, with their ledger id | only rules the operator approved (`research/19-approved-rules.md`); one sentence = imperative + "because" + the failure it prevents, ≤35 words; a rule with no statable reason is flagged for deletion | G5 · map #9 Notes ("no rule enters without the operator's yes") · G21 #91 (supersedes "imperative; ≤30 words") |
| **When X, use Y** | decision table for choices inside the topic | a table, situation → choice → why | G5 |
| **Good / Bad** | one pair per rule that can be misread | see the Good/Bad rules below; omit for rules whose sentence says it all | G5 · #35 (misreadable-only) |
| **Decided edges** | cases that look like violations but are allowed, and the reverse | pstack bugbot shape: *Skip when* · *Do not skip when* · *Confidence* | G5 post-close (pstack) |
| **Review checks** | what the one reviewer checks, at the end of the file | each check names the rule id it enforces and what to open; mechanical ones name their script | G5 · G3 (one reviewer reads the same file by changed path) |

## Good / Bad rules

Amended 2026-10-17 (G23 #93 Q3). Rules 2–3 before this date said "Bad = real code from our repo, Good = that Bad
rewritten" (#37 correction, 2026-10-03); that is superseded.
Amended 2026-10-31 (agent-factory#32 source audit): rules 2 and 4 now take examples from the rule's sources and
admit a rule by two independent sources or the operator-preference label (SRC2).
Amended 2026-11-01 (agent-factory#32): a rule line holds the rule only. The operator-preference mark moved off the
rule line into one "Operator preference" line under the reference's When X, use Y table.
Amended 2026-11-04 (agent-factory#59): a rule file holds only what an agent needs to act. Provenance (sources,
citations, example credits, the operator-preference status, evidence notes, dates) lives only in the ledger and the
research files; `scripts/check_provenance.py` fails a shipped skill file that carries any of it.
Tool names stay in a reference when they are the action itself (operator, 2026-11-04); a name that only credits a
source moves to the ledger.

1. A Good obeys **every** approved rule and house style, not only its own (GB1a, `31-good-bad-v2-BRIEF.md:9`).
2. **Bad and Good come from the reference that sources the rule**, adapted into one neutral domain. Where no source
   has a pair, write fresh neutral code. Never re-skin project code. No project names, paths or business terms.
   ≤15 lines each. The pair carries no label or credit; its source is recorded in the ledger.
3. **The real case is evidence, not text.** The Aruvii `path:lines` that showed the mistake (a ticket, an MR round, a QA
   finding) goes in the ledger `research/19-approved-rules.md` as the rule's evidence, never into the reference, and
   never as the start of an example.
4. **A rule enters the rulebook in one of two ways (SRC2).** (a) Two independent sources state it, each read at
   `path:line` or URL and section. Pages from one company or project count as one source. (b) The operator states it
   as a preference, and the ledger row's status contains `OPERATOR PREFERENCE (SRC2)`, followed by `in whole or in part`
   when the preference may cover only part of the rule. The reference
   carries no mark of either way: the rule line holds the rule only. Our repo supplies
   evidence that a rule is needed, never the rule itself.
5. House style in examples: test names are "should …" sentences; `final var` in Java, `def` in Groovy; one argument per
   line with the closing parenthesis on the last argument; Spock for new tests (CV1–CV6, `31e-conventions.md`).
6. One pair per rule. A rule whose text cannot be misread gets none (#35).

## Register

~80% ASD-STE100: sentences ≤20 words (≤25 descriptive), one instruction per sentence, active voice, one meaning per
word, no idioms (#35 ND-10). No `[confirmed:]` stamps, no counts that rot (WD1, WD2). Each fact has one owner (WD7).

## Skeleton

````markdown
# <Topic>

One sentence: what this reference governs and when it is read.

## Rules

- **V1** — <imperative>, because <the failure it prevents>. Example from G21 #91: "AssertJ only, never JUnit
  assertions — because one assertion style keeps failure messages readable across every module".
- **V2** — …

## When X, use Y

| situation | use | why |
|---|---|---|
| … | … | … |

## Good / Bad

### V1 — <title>

**Bad**
```groovy
…≤15 lines, neutral domain…
```
What goes wrong.

**Good**
```groovy
…the same code, rewritten to the rule…
```
Why this is right.

## Decided edges

- **Skip when** … — **Do not skip when** … — **Confidence** high/medium

## Review checks

- [ ] V1 — what to open and what to look for (`scripts/<check>.sh` if mechanical)
````

## Writing checklist (G10 #37, from R14 research/16 §4a)

```
[ ] 1  ≤300 lines; >100 lines → contents line at top; links one level deep, none into another ref's body; a
       reference that cannot hold every approved Good/Bad pair in 300 lines keeps its most telling pairs and links
       `references/examples/<topic>.md`, which holds them all (operator, 2026-10-29)
[ ] 2  Rules: one sentence = imperative + "because" + the failure it prevents, ≤35 words; a grep or a reader can
       decide it (no "consider", no "prefer"); no statable reason → flag for deletion (G21 #91)
[ ] 3  Rules: each discipline rule names the permitted alternative in the same sentence, inside the ≤35 words
[ ] 4  Rules: no rule a hook/Checkstyle/ArchUnit already fails — cite the gate instead
[ ] 5  When X, use Y: X is an observable predicate (file type, annotation, tier, path), never a judgement
[ ] 6  Good/Bad taken from the rule's source, in one neutral domain, no project names; the real Aruvii path:line is
       ledger evidence (re-verified at write time), never reference text; the rule has two sources or its
       ledger row says operator preference (SRC2)
[ ] 7  Good/Bad: one pair per rule that can be misread; none for rules whose sentence says it all
[ ] 8  Decided edges: Skip when / Do not skip when / Confidence
[ ] 9  Decided edges: exceptions live here as their own predicate, never inside a Rule
[ ] 10 Review checks: last section; one check per Rule, same id, each with its evidence (file:line or grep)
[ ] 11 Review checks: state the exhaustive bar ("every changed test file walked", not "check tests")
[ ] 12 One term per concept across all references
[ ] 13 No dates, counts that rot, narration or provenance: no source citations, example credits or preference
       lines; the ledger and research files hold them (`check_provenance.py`)
[ ] 14 Most load-bearing rule first (after compaction only the first 5,000 tokens of a skill survive)
[ ] 15 No-op test: if deleting a line changes no agent behaviour, delete it
[ ] 16 The MR maps every old line → kept / moved / deleted-with-reason
```

## Proof before a rewritten reference replaces the old one (G10 #37)

- **Testing references:** full replay — 2–3 past MRs whose real review hit the reference; old ref vs new ref, 3 runs
  each, same diff and organic prompt, blinded judge with the hidden real findings as rubric. PASS when the new ref
  finds at least as much, hits every finding it owns in ≥2/3 runs, adds no false positive the lead rejects, and costs
  ≤1.2× the old tokens. Runner: `claude plugin eval`. Method proven on P1 (!230).
- **Other references:** static checks + 1 past MR × 3 runs.

## Descriptions and the static gate (G10 #37)

- A skill description (domain routers and workflow skills; references carry none) = **"Use when <observable
  trigger>"** + what it holds. Never the procedure — an agent that reads the steps in the description skips the body.
  Tone and wording are settled by a trigger test (20 should / should-not prompts, `claude plugin eval` or
  skill-creator `run_eval`), not by taste.
- `make lint` runs: `claude plugin validate .agents/skills --strict` · check-doc-drift §5 (rulebook paths) · a
  heading check (the five sections present, in order, in every reference).

## How a domain gets its references (the process G9a and G9d used)

1. Candidate rules with sources → operator approves each on a review page (`review/build-planning.py`, `template.html`).
2. Approved rules → ledger `research/19-approved-rules.md` (id · target file · rule · source · status).
3. Good/Bad for the rules that can be misread → review page → approved log `research/33-good-bad-approvals.md`.
4. Generic references are written in chiyanram/skills from the ledger and the neutral examples (skills #99); Aruvii
   answers go in agent-platform `docs/agents/*.md` (G23 #93, G24 #94).
