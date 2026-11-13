# rulebook design

This page says what the rulebook plugin is, how a person and an engine use it, and how its content stays good. Decisions live in `PRINCIPLES.md` and in the ledger, and this page points at them.

## 1. What it is

`rulebook@chiyanram` is a Claude Code plugin with two kinds of content:

| kind | what | state |
|---|---|---|
| **rules** | skills with references: `code`, `testing`, `planning`, `migrations`, `obs`, `deslop`, `meta` | built |
| **process** | `crq`: the change pipeline from request to merge, with lanes and phases | built as a workflow skill |

It stays generic: no project names, no engine names and no provenance in `plugins/`. The role cards
name the process's own files (the spec, `.factory/report.json`, `.factory/pr.md`) as part of a contract any engine can
keep, never as a product's paths.

## 2. Who uses it, and how

```text
a person in Claude Code            an engine (any orchestrator)
  installs rulebook@chiyanram        lists rulebook@chiyanram in a project's settings, pinned
  types /crq, or the skills          reads lanes-v2 and the role cards,
  load as they work                  runs each card as a fresh run, enforces its frontmatter
```

- The plugin works with **no engine**.
- An engine works with **no rulebook**.
- A project can use the rulebook, its own repo files, another team's plugin, or any mix.

## 3. What a project points at

- **Rules:** a project's `AGENTS.md` names the skill and reference to read, by name.
- **An engine** gives the automated review the enabled plugins, plus the repo's own files from the default branch. No
  special "(rulebook plugin)" wording is needed.

## 4. The process: lanes and role cards

The crq process gets a side an engine can read, so an engine runs the same process a person runs with `/crq`.

**Lanes as data.** Lanes-v2 (`process/lanes-v2.json`) holds the flow. It names the phases, and gives each phase its
actor and its outcome edges. It holds the caps and the lane conditions. For each lane, it lists the phases the lane
takes, the lens cap, the review model and the effort. `make index` builds the lanes table from it, in
[`crq/references/lanes.md`](../plugins/rulebook/skills/crq/references/lanes.md). Read the table there. V1
(`process/lanes.json`) stays beside v2 until an engine reads v2.

- An engine may make a lane stricter, never looser.
- The approval floor is a graph rule: every lane above tiny takes the approval phase. `check_process.py` enforces it
  on lanes-v2 and v1 in this repo. The engine enforces it on any lane change of its own.
- The timeline record is written by the engine, with no model. A full retro is an extra task, and it runs only when a
  human starts it (RT1–RT6).

**Role cards.** One markdown file per role: coordinator, design-reviewer, breaker, test-first, implementer, cleanup,
finder, verify pass and retro. The onboarder, which writes a project's brief and glossary, is the engine's card: its
job is what the engine strips, lists and stages.
- **Frontmatter** (the same fields everywhere): role, steps, input, `must_not_see`, hand-off, tools, enforced
  guardrails (IDs from the closed list in the card schema), rules (by id). An engine enforces it. `next` is dropped:
  lanes-v2 holds the flow.
- **Schemas** (#305): this repo owns the format of its cards, lanes and findings. Each is a versioned JSON schema in
  `process/schema/` that ships with the plugin, so an engine reads the version it pins; a new version is a new file
  beside the old one. `check_process.py` fails when a schema is missing or uses a keyword `schema_lite.py` cannot run.
  The schema files, and how each is checked:
  - `card-v1.schema.json`: `check_process.py` checks the frontmatter of every role card against it.
  - `lanes-v1.schema.json`: `check_process.py` checks `process/lanes.json` against it.
  - `lanes-v2.schema.json`: `check_process.py` checks `process/lanes-v2.json` against it, then checks the graph
    (`scripts/lanes_graph.py`).
  - `finding-v1.schema.json`: one finding of a finder run. The repo holds no finding file, so `check_process.py`
    reads none. `tests/test_schema_lite.py` checks sample findings against it.
  - `report-v1.schema.json` (#362): the `.factory/report.json` of the implementer, test-first and cleanup, one of
    three closed shapes on `status`: done with evidence, asked with questions, or blocked with the blocker. The repo
    holds no report file, so `check_process.py` reads none: it only loads the schema. `tests/test_check_process.py`
    checks sample reports against it.

  A card or `lanes-v2.json` may cite a `urn:rulebook:crq:<name>:<n>` id only when a file in `process/schema/`
  declares it as its `$id`. `check_process.py` fails, naming the file and the id, when no file does.

  A card and a finding take no field the schema does not name, and a finding's `line` is a number, or text such as
  `12` or `40-44`, so every cite points at a real line. Each other finding field has one closed set of values, set
  here: `severity` is blocker, warning or nit; `category` is one of bug, security, concurrency, data, api, perf,
  observability, maintainability, test_gap, doc_defect, style or speculative (only "not proven", never "other"); a
  style finding is always a nit; `rule` is a rule ID or null. Severity is the finder's and the bucket is the verify
  pass's; the glossary defines both.
- **Body:** the job, a "done when" line, numbered steps, and an "it's working if" list.
- **No persona and no capitals.** A prohibition appears only for a hard guardrail.
- **One glossary** is used by every card.
  - Its factory words: task, trigger, run, runner, ticket tracker, git host, orchestrator, automated review.
  - Its process words: spec, AC, design, slice, lane, evidence row, finding, lens, judge files, hand-off, ask, ready
    check.
- **Questions** (decided, operator 2026-11-09):
  a run that needs decisions asks every open question at once, in one numbered round. Each question carries 2 to 4
  short choices and one recommended choice, so the human answers with taps, "1A 2B", or "accept all". The project
  setting `questions` can be `one-at-a-time` instead. Never a guess. A coordinator round holds at most 3 questions;
  every other open question becomes a marked default that "accept all" takes (decided 2026-11-10, #295).

**Review rubrics** (the finder's lenses) follow the same shape:
- each check is binary, with something you can observe ("met if …, unmet if …");
- every finding has evidence (`file:line` or a quoted rule): no evidence, no finding;
- severity is defined for the project, with at most five nits;
- each has a "do not report" list: what lint, types or the gate enforce, generated files, and other lenses' concerns;
- each lens runs in a fresh run, followed by a separate verify pass.

**Evals live here, for this plugin.**
- Three scenarios per role card, each with a grader. A card change ships only if its scenarios do not get worse.
- Every role's scenarios sit in `plugins/rulebook/evals/<role>/<case>/`, apart from the cards.
- These test the plugin on its own, in plain Claude Code. An engine's own golden set tests
  its whole automated review. **Two sets, two jobs** (decided 2026-11-09).

## 5. How the content stays good

Every card and rubric follows the same discipline as the references:
- the five-section format where it applies;
- a ledger row for every rule;
- the scripted checks;
- its evals;
- releases cut from commits.

A card that grows is proven with its scenarios first. Mechanical rules move to checks, and prose is kept for judgement
calls (RT6).
