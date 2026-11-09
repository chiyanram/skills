# rulebook design

This page says what the rulebook plugin is, how a person and an engine use it, what changes from today, and the order we
build it in. Decisions live in `docs/adr/` and in the ledger, and this page points at them. The words follow
agent-factory's `GLOSSARY.md` (chiyanram/agent-factory#144), which uses Matt Pocock's software-factory vocabulary.

## 1. What it is

`rulebook@chiyanram` is a Claude Code plugin with two kinds of content:

| kind | what | today |
|---|---|---|
| **rules** | skills with references: `code`, `testing`, `planning`, `migrations`, `obs`, `deslop`, `meta` | built (ADR-0002, 0004) |
| **process** | `crq`: the change pipeline from request to merge, with lanes and phases | built as a workflow skill (ADR-0008) |

It stays generic: no project names, no engine names and no provenance in `plugins/` (ADR-0001, 0005). The role cards
name the process's own files (the spec, `.factory/report.json`, `.factory/pr.md`) as part of a contract any engine can
keep, never as a product's paths.

## 2. Who uses it, and how

```text
a person in Claude Code            an engine (for example agent-factory)
  installs rulebook@chiyanram        lists rulebook@chiyanram in a project's settings, pinned
  types /crq, or the skills          reads the lanes file and the role cards,
  load as they work                  runs each card as a fresh run, enforces its frontmatter
```

- The plugin works with **no engine**.
- An engine works with **no rulebook**.
- A project can use the rulebook, its own repo files, another team's plugin, or any mix.

## 3. What a project points at

- **Rules:** a project's `AGENTS.md` names the skill and reference to read, by name.
- **An engine** gives the automated review the enabled plugins, plus the repo's own files from the default branch. No
  special "(rulebook plugin)" wording is needed.

## 4. The process: lanes and role cards (new)

The crq process gets a side an engine can read, so an engine runs the same process a person runs with `/crq`.

**Lanes as data.** One small file holds, per lane:

| lane | approval (releases the build) | design review | test-first | lenses | retro |
|---|---|---|---|---|---|
| tiny | no (START only) | no | no | 1 | timeline record |
| bug | yes | yes | yes | ~3 | timeline record; a full retro run if a human starts one |
| feature | yes | yes | no | ~3 | the same |
| one-way door | yes, covering each irreversible step | yes | no | all, on the strongest model | the same |

- An engine may make a lane stricter, never looser.
- No lanes file can drop approval for a lane above tiny: the approval floor is enforced by the engine.
- The timeline record is written by the engine, with no model. A full retro is an extra task, and it runs only when a
  human starts it (RT1–RT6).

**Role cards.** One markdown file per role: coordinator, design-reviewer, test-first, implementer, cleanup, finder,
verify pass, retro and onboarder. The onboarder writes a project's brief and glossary once, for every other role.
- **Frontmatter** (the same fields everywhere): role, steps, input, `must_not_see`, hand-off, tools, enforced
  guardrails, rules (by id) and next. An engine enforces it.
- **Body:** the job, a "done when" line, numbered steps, and an "it's working if" list.
- **No persona and no capitals.** A prohibition appears only for a hard guardrail.
- **One glossary** is used by every card.
  - Its factory words: task, trigger, run, runner, ticket tracker, git host, orchestrator, automated review.
  - Its process words: spec, AC, design, slice, lane, evidence row, finding, lens, judge files, hand-off, ask, ready
    check.

**Review rubrics** (the finder's lenses) follow the same shape:
- each check is binary, with something you can observe ("met if …, unmet if …");
- every finding has evidence (`file:line` or a quoted rule): no evidence, no finding;
- severity is defined for the project, with at most five nits;
- each has a "do not report" list: what lint, types or the gate enforce, generated files, and other lenses' concerns;
- each lens runs in a fresh run, followed by a separate verify pass.

**Evals live here, for this plugin.**
- Three scenarios per role card, each with a grader. A card change ships only if its scenarios do not get worse.
- The finder's set starts from the three review cases (skills PR #229). Every role's scenarios sit in
  `plugins/rulebook/evals/<role>/<case>/`, apart from the cards, so they fit whichever placement section 8 picks.
- These test the plugin on its own, in plain Claude Code. agent-factory's golden set (chiyanram/agent-factory#214) tests
  the engine's whole automated review. **Two sets, two jobs** (decided 2026-11-09).

## 5. What changes from today (`main` `27880dc`)

| today | changes to |
|---|---|
| crq is prose for a person only | plus a lanes file and role cards an engine can run |
| the implementer and review prompts live in agent-factory | they live here, as role cards |
| crq says writer and reviewer | implementer, finder and verify pass, per the term map (chiyanram/agent-factory#144 phase 6) |
| the approval is recorded with the spec's hash only (LN4, `crq/references/lanes.md:14-15`), though the human approves spec and design (`crq/SKILL.md:29`) | the approval covers spec and design |
| no review-round cap in the skill (the engine has 3) | the cap is stated in the skill |
| CR2 splits a change beyond 20 files; PD9 makes a slice over 15 files its own issue | one size rule |
| acceptance criteria must be Gherkin scenarios (GA1–GA6); the role cards use numbered lines | numbered AC-n lines, each decidable by a test, for specs and cards (decided 2026-11-09, #237 decision 2; #244): GA1, GA2, GA4–GA6 superseded; GA3, CV1 and GT2 dropped; no Gherkin |
| `check-cites` is named only as an example (`planning/references/spec-review.md:115`), and no script exists | the script is added, or the example names no missing tool |
| test protection is one sentence (VB6) | plus a `test-integrity` rubric for the review lens |
| "fails on revert" (VB2) and "the smallest regression" (CR6) are judged by reading | a revert script, and mutation on the changed lines, where a project can run them |
| crq assumes a CI system | the gate is whatever the project has: CI, a queue, or a local run |
| some findings are cosmetic: the PR5 file tree, a mandatory alternative for a small feature | demoted to nits or dropped; decided with the operator per rule |

## 6. How the content stays good

Every card and rubric follows the same discipline as the references:
- the five-section format where it applies (ADR-0004);
- a ledger row for every rule (ADR-0005);
- the scripted checks;
- its evals;
- releases cut from commits (ADR-0007).

A card that grows is proven with its scenarios first. Mechanical rules move to checks, and prose is kept for judgement
calls (RT6).

## 7. Order of work

| step | what | ticket | needed by |
|---|---|---|---|
| 1 | crq fixes: spec + design approval, round cap, size rule, `check-cites` | #234 | the factory's safety core |
| 2 | `test-integrity` rubric | #235 | the review lens |
| 3 | the rulebook's own evals: keep the review cases here as the finder's set | #236 | the role cards' evals |
| 4 | the lanes file, the glossary and nine role cards, each with 3 eval scenarios | #237 | the factory's plugin step, then the ledger pilot |
| 5 | crq's own wording moves to the glossary's words | (after #237) | the cards and references match |
| later | agent-engineering references | #130 #134 | an RCA agent at work |

New content needs the operator's yes and a ledger row, as every rule does.

## 8. Open

- **Placement:** where the lanes file and the cards sit in the plugin (`plugins/rulebook/skills/crq/...` or a sibling
  folder), and how `check_*.py` and `make index` treat them. Decided with the first card.
- **Card status:** whether a role card counts as a rule (it needs a ledger row) or as a prompt that cites rules (it
  needs eval scenarios). Proposed: the card cites rules by id and needs eval scenarios, and the rules keep their ledger
  rows.
- **Questions:** asked one at a time, or as one numbered round. Proposed: a project setting.
- **The PR body:** written by the implementer, as crq gives the PR phase to the build. To be confirmed.
