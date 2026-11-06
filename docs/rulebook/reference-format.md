# Reference format

The template every reference in `plugins/rulebook/skills/<domain>/references/` follows. Read it before you write or
rewrite a reference. Which rules a reference may hold is the `meta` skill's `writing-references` reference.

## Where a reference sits

```text
plugins/rulebook/skills/<domain>/
├── SKILL.md                         router: frontmatter + "which reference to load" table (make index)
├── references/<topic>.md            ← this template
└── references/examples/<topic>.md   every approved Good / Bad pair, when the reference cannot hold them all
```

## Above the five sections

A title, then one paragraph: what the reference covers, and one sentence starting "Read it when …" or "Read it
before …". `make index` copies that sentence and the rule IDs into the domain router's table.

## The five sections, in this order

| section | holds | how to write it |
|---|---|---|
| **Rules** | the approved rules, one line each, with their ledger ID | only rules the operator approved; one sentence = instruction + "because" + the failure it prevents, ≤35 words; a rule with no reason is flagged for deletion |
| **When X, use Y** | a decision table for choices inside the topic | situation → choice → why |
| **Good / Bad** | one pair per rule that can be misread | see the Good / Bad rules below |
| **Decided edges** | cases that look like violations but are allowed, and the reverse | *Skip when* · *Do not skip when* · *Confidence* |
| **Review checks** | what the reviewer checks, at the end of the file | each check names the rule ID it enforces and what to open; a mechanical one names its script |

## Good / Bad rules

1. A Good obeys **every** approved rule and house style, not only its own.
2. Bad and Good come from the rule's source, adapted into one neutral domain. Where no source has a pair, write fresh
   neutral code. Never re-skin project code. No project names, paths or business terms. ≤15 lines each. The pair
   carries no label or credit; its source is in the ledger.
3. A real project mistake that shows the rule is needed is evidence. It goes in the rule's ledger row, never into the
   reference, and never as the start of an example.
4. House style in examples: test names are "should …" sentences; `final var` in Java, `def` in Groovy; one argument
   per line with the closing parenthesis on the last argument; Spock for new tests.
5. One pair per rule. A rule whose text cannot be misread gets none.

## Register

About 80% ASD-STE100: sentences ≤20 words (≤25 descriptive), one instruction per sentence, active voice, one meaning
per word, no idioms. No counts that rot. Each fact has one owner.

## Skeleton

````markdown
# <Topic>

One paragraph: what this reference covers. Read it when …

## Rules

- **V1** — <instruction>, because <the failure it prevents>.
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

- [ ] V1 — what to open and what to look for (`scripts/<check>` if mechanical)
````

## Writing checklist

```text
[ ] 1  ≤300 lines; >100 lines → a contents line at the top; links one level deep, none into another reference's
       body; a reference that cannot hold every approved pair keeps its most telling pairs and links
       references/examples/<topic>.md, which holds them all
[ ] 2  Rules: instruction + "because" + the failure it prevents, ≤35 words; a grep or a reader can decide it
       (no "consider", no "prefer")
[ ] 3  Rules: each discipline rule names the permitted alternative in the same sentence
[ ] 4  Rules: no rule that a hook, linter or architecture test already fails; name the gate instead
[ ] 5  When X, use Y: X is an observable predicate (file type, annotation, tier, path), never a judgement
[ ] 6  Good / Bad: from the rule's source, one neutral domain, no project names
[ ] 7  Good / Bad: one pair per rule that can be misread; none for a rule whose sentence says it all
[ ] 8  Decided edges: Skip when / Do not skip when / Confidence; exceptions live here, never inside a rule
[ ] 9  Review checks: last section; one check per rule, same ID, each with its evidence (file:line or grep)
[ ] 10 Review checks: state the exhaustive bar ("every changed test file walked", not "check tests")
[ ] 11 One term per concept across all references
[ ] 12 No dates, counts that rot, narration or provenance (check_provenance.py)
[ ] 13 Most important rule first: after compaction only the first 5,000 tokens of a skill survive
[ ] 14 No-op test: if deleting a line changes no agent behaviour, delete it
[ ] 15 The pull request maps every old line of a rewritten reference → kept / moved / deleted with a reason
```

## Skill descriptions

A skill description (domain routers only; references carry none) is **"Use when <observable trigger>"** plus what
the skill holds. Never put the procedure in it: an agent that reads the steps in the description skips the body.
Settle its wording with a trigger test (should and should-not prompts, `claude plugin eval`), not by taste.

## Proof before a rewritten reference replaces the old one

- **Testing references:** replay 2–3 past pull requests whose real review hit the reference. Run the old and the new
  reference 3 times each on the same diff, with a blind judge that holds the real findings. The new one passes when
  it finds at least as much, hits each finding it owns in ≥2 of 3 runs, adds no false positive, and costs ≤1.2× the
  old tokens.
- **Other references:** the static checks, and 1 past pull request × 3 runs.
