# Reference format — the template every reference follows

Draft consolidated 2026-10-02 from decisions already taken. No new decisions here; each line cites where it was
decided. G10 (#37, "how we write skills and references") owns this file and may refine it.

## Where a reference sits

```
.agents/skills/<domain>/                 knowledge skill (domain): testing · code · obs · migrations · delivery · planning
├── SKILL.md                             router: frontmatter + "which reference to load" table, nothing else
├── references/<topic>.md                ← THIS TEMPLATE
└── scripts/                             mechanical checks the references name
.agents/skills/<workflow>/SKILL.md       workflow skill (flat, own /name): crq · flyway-migration · deslop · …
.claude/rules/<area>.md                  L2: MUSTs only, path-scoped — never the examples
```
Sources: G1 (#5, 4 layers), #643 design (hybrid: workflows flat, knowledge in domains, firstmate/openclaw/pstack),
G5 (#13, one file per topic).

## The five sections, in this order

| section | holds | rule for writing it | decided in |
|---|---|---|---|
| **Rules** | the approved rules, one line each, with their ledger id | only rules the operator approved (`research/19-approved-rules.md`); imperative; ≤30 words | G5 · map #9 Notes ("no rule enters without the operator's yes") |
| **When X, use Y** | decision table for choices inside the topic | a table, situation → choice → why | G5 |
| **Good / Bad** | one pair per rule that can be misread | see the Good/Bad rules below; omit for rules whose sentence says it all | G5 · #35 (misreadable-only) |
| **Decided edges** | cases that look like violations but are allowed, and the reverse | pstack bugbot shape: *Skip when* · *Do not skip when* · *Confidence* | G5 post-close (pstack) |
| **Review checks** | what the one reviewer checks, at the end of the file | each check names the rule id it enforces and what to open; mechanical ones name their script | G5 · G3 (one reviewer reads the same file by changed path) |

## Good / Bad rules

1. A Good obeys **every** approved rule and house style, not only its own (GB1a, `31-good-bad-v2-BRIEF.md:9`).
2. Real code with `path:lines` at a pinned commit, or labelled **adapted** with what it was built from. ≤15 lines.
3. Prefer real Bads — things that actually went wrong here (a ticket, an MR round, a QA finding).
4. House style in examples: test names are "should …" sentences; `final var` in Java, `def` in Groovy; one argument per
   line with the closing parenthesis on the last argument; Spock for new tests (CV1–CV6, `31e-conventions.md`).
5. One pair per rule. A rule whose text cannot be misread gets none (#35).

## Register

~80% ASD-STE100: sentences ≤20 words (≤25 descriptive), one instruction per sentence, active voice, one meaning per
word, no idioms (#35 ND-10). No `[confirmed:]` stamps, no counts that rot (WD1, WD2). Each fact has one owner (WD7).

## Skeleton

````markdown
# <Topic>

One sentence: what this reference governs and when it is read.

## Rules

- **V1** — A new test answers the four value questions before it is written.
- **V2** — …

## When X, use Y

| situation | use | why |
|---|---|---|
| … | … | … |

## Good / Bad

### V1 — <title>

**Good** (real)
```groovy
…≤15 lines…
```
`path/to/File.groovy:40-52` — why this is right

**Bad** (real)
```groovy
…
```
`path/to/Other.groovy:12-20` — what went wrong (#NNN)

## Decided edges

- **Skip when** … — **Do not skip when** … — **Confidence** high/medium

## Review checks

- [ ] V1 — open the new test; can each of the four questions be answered from it? (`scripts/<check>.sh` if mechanical)
````

## How a domain gets its references (the process G9a and G9d used)

1. Candidate rules with sources → operator approves each on a review page (`review/build-planning.py`, `template.html`).
2. Approved rules → ledger `research/19-approved-rules.md` (id · target file · rule · source · status).
3. Good/Bad for the rules that can be misread → review page → approved log `research/33-good-bad-approvals.md`.
4. Work item 1 (agent-platform, via `/crq`) writes the files from the ledger and the approved examples.
