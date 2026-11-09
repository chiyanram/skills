# rulebook design

The one page that says what the rulebook plugin is, how a project and an engine use it, what changes from today, and
the order we build it. Decisions live in `docs/adr/` and in the ledger. This file points at them.

## 1. What it is

`rulebook@chiyanram` is a Claude Code plugin with two kinds of content:

| kind | what | today |
|---|---|---|
| **rules** | skills with references: `code`, `testing`, `planning`, `migrations`, `obs`, `deslop`, `meta` | built (ADR-0002, 0004) |
| **process** | `crq`: the change pipeline from request to merge, with lanes and phases | built as a workflow skill (ADR-0008) |

It stays generic: no project names, no engine name, no provenance in `plugins/` (ADR-0001, 0005).

## 2. Who uses it, and how

```text
a person in Claude Code            an engine (for example agent-factory)
  installs rulebook@chiyanram        lists rulebook@chiyanram in a project's settings
  types /crq, or the skills          reads the process file and the role cards,
  load as they work                  runs each card as a fresh worker, enforces its frontmatter
```

- The plugin works with **no engine**.
- An engine works with **no rulebook**.
- A project can use the rulebook, its own repo files, another team's plugin, or any mix.

## 3. What a project points at

- Rules: a project's `AGENTS.md` names the skill and reference to read, by name.
- An engine gives the reviewer the enabled plugins and the repo's own files from the default branch. No special
  "(rulebook plugin)" wording is needed.

## 4. The process: lanes and role cards (new)

The crq process gets a machine-readable side, so an engine runs the same process a person runs with `/crq`.

**Lanes as data.** One small file holds, per lane:

| lane | approval | design review | test-first | lenses | retro |
|---|---|---|---|---|---|
| tiny | no | no | no | 1 | record |
| bug | yes | yes | yes | ~3 | full |
| feature | yes | yes | no | ~3 | full |
| one-way door | yes | yes | no | all, strongest model, irreversible steps listed | full |

An engine may make a lane stricter, never looser.

**Role cards.** One markdown file per step: coordinator, design-reviewer, test-first, writer, cleanup, finder,
verify-pass, retro.
- **Frontmatter** names the job's steps, inputs, what it must not see, the hand-off file, tools, the rules it applies,
  and the next role. An engine enforces it.
- **Body:** the job, a "done when" line, numbered steps, and an "it's working if" list.
- **No persona and no capitals.** A prohibition appears only for a hard guardrail.
- **One glossary** used by every card (spec, AC, design, slice, lane, evidence row, finding, lens, judge files,
  hand-off, ask, ticket, ready check).

**Role evals.** Three scenarios per role, each with a grader. A card change ships only if its scenarios do not get
worse. The finder's set starts from `evals/review/` (#229).

## 5. What changes from today

| today | changes to |
|---|---|
| crq is prose for a person only | plus a lanes file and role cards an engine can run |
| the writer and reviewer prompts live in agent-factory | they live here, as role cards |
| the approval is recorded with the spec's hash only (LN4, `crq/references/lanes.md:16`), though the human approves spec and design (`crq/SKILL.md:29`) | the approval covers spec and design |
| no review-round cap in the skill (the engine has 3) | the cap is stated in the skill |
| CR2 splits a change beyond 20 files; PD9 makes a slice over 15 files its own issue | one size rule |
| acceptance criteria must be Gherkin scenarios (GA1–GA6); the role cards' glossary uses numbered lines | **open:** one form for both (see section 8) |
| `check-cites` is named but does not exist | the script is added, or the mention removed |
| test protection is one sentence (VB6) | plus a `test-integrity` rubric for the review lens |
| reviewer evals here (3) and in agent-factory (#214) | one set |

## 6. How the content stays good

Every card and rubric follows the same discipline as the references:
- the five-section format where it applies (ADR-0004);
- a ledger row for every rule (ADR-0005);
- the scripted checks;
- the eval set;
- releases cut from commits (ADR-0007).

A card that grows is proven with its scenarios first. Mechanical rules move to checks; prose is kept for judgement
calls (RT6).

## 7. Order of work

| step | what | needed by |
|---|---|---|
| 1 | crq fixes: spec + design approval, round cap, size rule, `check-cites` | the factory's safety core |
| 2 | `test-integrity` rubric | the review lens |
| 3 | one reviewer eval set, joined with agent-factory#214 | the factory's eval step |
| 4 | the lanes file, glossary and role cards, each with 3 eval scenarios | the factory's plugin step, then the ledger pilot |
| later | agent-engineering references (#130, #134) | an RCA agent at work |

New content needs the operator's yes and a ledger row, as every rule does.

## 8. Open

- Where the lanes file and the cards sit in the plugin (`plugins/rulebook/skills/crq/...` or a sibling folder), and
  how `check_*.py` and `make index` treat them. Decided with the first card.
- How acceptance criteria are written: Gherkin scenarios (GA1–GA6, approved) or numbered lines (the role cards' glossary,
  and `spec.ts` today). Changing GA1–GA6 needs the operator's yes and a ledger row.
- Whether a role card counts as "a rule" (it needs a ledger row) or as a prompt that cites rules (it needs eval
  scenarios). Proposed: the card cites rules by ID and needs eval scenarios; the rules keep their ledger rows.
