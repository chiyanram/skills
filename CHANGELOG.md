# Changelog

What the `rulebook` plugin ships, by version. semantic-release writes this file from the commit messages on
`main`; do not edit it by hand. Design work under `research/` and `review/` ships nothing and is not listed.

## [3.0.0](https://github.com/chiyanram/skills/compare/rulebook--v2.0.0...rulebook--v3.0.0) (2026-11-14)

### ⚠️ Breaking changes

* **crq** — ** no. Nothing reads lanes-v2 at run time yet. The
enum goes back to the published v1.

**Rollback:** revert the squash commit.
* **crq** — ** no. The card-v1 role enum widens (additive). A
lanes-v2 file with a counted edge and no
`round-cap` now fails `check_process.py`; the shipped file is updated.

**Rollback:** revert the PR's squash commit. Nothing reads lanes-v2 at
run time yet.

**Notes for review.**
- `tests/test_check_process.py`: the valid fixture's `gate` phase gains
`"round-cap": "human"`, because the new rule
(AC-4b) would otherwise reject the valid fixture. The spec changed this
behaviour; no assertion was removed.
- `CONTRIBUTING.md` check table and the `check_process.py` docstring
name the new graph rule.

### Changed files

```
CONTRIBUTING.md                                   check table: round-cap rule
docs/DESIGN.md                                    §4 role list names breaker
docs/rulebook/approved-rules.md                   BK1–BK4, approved
plugins/rulebook/evals/breaker/                   3 scenarios, 9 graders
plugins/rulebook/skills/crq/SKILL.md              Phases row, role list, diagram (generated)
plugins/rulebook/skills/crq/process/glossary.md   break scenario, breaker
plugins/rulebook/skills/crq/process/lanes-v2.json design-break, break_rounds, round-cap on verify and gate
plugins/rulebook/skills/crq/process/roles/breaker.md      new card
plugins/rulebook/skills/crq/process/roles/verify-pass.md  checks scenarios; closures
plugins/rulebook/skills/crq/process/schema/card-v1.schema.json  enum + breaker
plugins/rulebook/skills/crq/references/lanes.md   lanes table (generated)
plugins/rulebook/skills/planning/SKILL.md         router row (generated)
plugins/rulebook/skills/planning/references/break-the-design.md  new reference
scripts/check_process.py, scripts/lanes_graph.py  no_round_cap rule
tests/test_check_process.py                       planted case
```

### Where to look first

1. `scripts/lanes_graph.py` `no_round_cap`: the only new code.
2. `lanes-v2.json`: the design-break phase, and `round-cap` on verify
and gate.
3. `breaker.md` and `verify-pass.md`: how a kept scenario closes.

### One-way door readiness

Not a one-way door: every change is a file revert.

### Operator review

- **Rules:** BK1–BK4 are new rules under `plugins/`, approved by the
operator word for word, with ledger rows.
- **Gate files:** `scripts/lanes_graph.py` and
`scripts/check_process.py` run in `make lint` on every PR.
- **Schema:** `card-v1.schema.json` role enum widened in place with
`breaker` (additive; operator decision Q9).
- **Size:** 424 added lines, over the 400-line limit. **The operator
waived the limit for this PR.**

### Review

- Design review: 1 round (6 findings fixed) plus operator decisions D1
(round-cap → human on every counted phase) and
  D2 (how kept scenarios close).
- Code review round 1: 3 findings fixed in 0306a87 with the operator's
yes (closure by bucket; round-cap must target
`human`, proved by mutation; docstring width). A 4th, the approval
request having no owner, is filed as #374.
* **crq** — ** no. No reader depends on report-v1 yet. The check
is stricter: a card or lanes-v2 that cites an
id no schema declares now fails `make lint`. Nothing in the repo does.

**Roll back:** revert the two commits. No data or state to migrate.

### Changed files

```text
plugins/rulebook/skills/crq/process/
├── schema/report-v1.schema.json   new: anyOf done | asked | blocked, each closed
└── roles/
    ├── implementer.md             hand_off cites report:1; deviation also in report `deviations`; recommended from 0
    ├── test-first.md              hand_off cites report:1; recommended from 0
    ├── cleanup.md                 hand_off cites report:1; deferred line kept
    └── finder.md                  hand_off cites finding:1; category points at the schema
scripts/check_process.py           SCHEMAS += report; URN, cited_ids, unknown_id_problems, schema_ids
tests/test_check_process.py        REPORTS table + ReportSchemaTest; PLANTED unknown-id rows; extra-schema pass test
```

**Where to look first.** `scripts/check_process.py` `process_problems`:
the lanes-v2 unknown-id line runs beside the
lanes-v2 schema and graph check, so a schema or graph stop cannot hide
it. Then `report-v1.schema.json` `choices`:
the 2-to-4 cap is `prefixItems` of 4 with `items: false`, because
`schema_lite` has no `maxItems`.

**Notes.**
- `deviations[].line` copies finding-v1's `line` definition inline:
`schema_lite` has no `$ref`.
- The report schema also types `status` at the top level as an enum, so
an unknown status prints one plain line
(`status: 'stuck' is not one of done, asked, blocked`) before the anyOf
line.
- `card_problems` takes the declared ids as a fifth argument and checks
the card's parsed frontmatter.
- The finder card's step 5 said "one of the `hand_off` list" for the
category; it now says "one of the finding
schema's `category` list", since the hand_off no longer spells the list
out.

### Review

- Design review: 1 round, 8 findings, all fixed before approval.
- Code review round 1: 3 findings, fixed in 7c08dae with the operator's
yes: 8 report-schema rows that each catch a
schema mutation (closed done/asked shapes, required fields, status/shape
mismatch); cleanup and test-first say their
  allowed status again; one test that each card cites its schema id.
- Evals (AC-5, one run per case, the operator judged "no worse"):
implementer 1/3 → 1/3, test-first 3/3 → 3/3,
  cleanup 1/3 → 2/3.
* **crq** — ** no.

**Roll back:** revert the commit. No generated file and no check depends
on the new text.

## Changed files

```text
docs/DESIGN.md                                   §2 diagram line, §4 Lanes as data, approval floor, Schemas
plugins/rulebook/skills/crq/process/glossary.md  intro, lane row, six new rows
```

## Where to look first

`docs/DESIGN.md` §4 "Lanes as data" and the Schemas bullet: the finding
schema line says plainly that no check reads a
finding file.

## Notes
* **crq** — no. Generated docs and repo scripts only; a skill
without `process/lanes-v2.json` builds as before.

Rollback: revert this PR; the hand-written blocks come back with it.

## Change

```text
scripts/
  A lanes_render.py      diagram(doc), lanes_table(doc), with_block, files(skill): pure render + one reader
  M build_index.py       build(skill) as before, then build_lanes(skill): index table first, lanes blocks second
  M check_index.py       router_problems as before + lanes_problems: missing / doubled / stale block
plugins/rulebook/skills/crq/
  M SKILL.md             diagram between lanes-diagram markers; Phases table rows named by lanes-v2 ids
  M references/lanes.md  lanes table between lanes-table markers
M CONTRIBUTING.md        make index and check_index.py rows
tests/
  A test_lanes_render.py 20 tests: pure rows, build then check, each failure path
```

```text
lanes_render.files(skill)
  1. no process/lanes-v2.json        -> nothing to do
  2. check_process.load_schemas      -> a schema missing / not JSON: its line
  3. check_process.lanes_v2_problems -> any line: "<path>: not valid; run check_process.py"
  4. render each *.md holding a START marker; a block missing, doubled or with no END after START is a line
```

## Operator review needed

- **Gate files:** `scripts/check_index.py` runs in `make lint` on every
PR; `scripts/build_index.py` is `make index`.
- **Instruction files:** `crq/SKILL.md` and `crq/references/lanes.md`
(now generated blocks), and two
  `CONTRIBUTING.md` rows.
- **Size:** 424 added lines, over the 400-line limit. Production code is
187 lines; tests are 206. **The operator waived
  the limit for this PR (tests only).**

## Where to look

1. `scripts/lanes_render.py` `with_block` and `placement`: the marker
rules (exactly one START and one END, END after
   START, one file per block).
2. `scripts/build_index.py` `__main__`: `build` before `build_lanes`, so
the two blocks in `SKILL.md` never overwrite
   each other.
3. The rendered blocks in `crq/SKILL.md` and `crq/references/lanes.md`:
the formats the design left open
   (`cap <name> = <value>`, `—` for a lane with no human gate).

## Evidence (base main, head 09bb374)

| AC | command | result |
|---|---|---|
| AC-1 | `make index && git diff --exit-code` | no diff, exit 0 |
| AC-1 | `test_should_rewrite_a_stale_block_so_the_index_check_passes` |
`gate_red` 2 → 4, build writes `cap gate_red = 4`, check passes |
| AC-2 | `sed -n '/lanes-diagram:/,/\/lanes-diagram/p' crq/SKILL.md` |
16 phase ids in order, `HUMAN approval`, `HUMAN merge`, 7 edge lines
with caps |
| AC-3 | `test_should_show_each_lane_in_file_order_with_its_when_cells`,
`test_should_list_a_condition_once_when_two_lanes_use_it` | OK |
| AC-4 | hand-edit lanes.md, `python3 scripts/check_index.py .` |
`.../references/lanes.md: lanes block is stale; run make index`, exit 1
|
| AC-5 | missing block, twice in one file, in two files, no END, END
above START | 5 tests OK; END above START prints one line, no traceback
|
| AC-6 | `printf '{' > lanes-v2.json && python3 scripts/build_index.py
.` | `.../lanes-v2.json: not valid; run check_process.py`, exit 1;
schema-missing and graph-rule tests OK |
| AC-7 | `grep -c '^\| test-first \|'` · old-names `grep -cE '^[|]
(design review…) [|]'` · phase-id check | `1` · `0` · `every phase id
has a Phases row: 16` |
| AC-8 | `tests.test_build_index`, `-k without_lanes_v2` | OK |
| all | `make test` · `make lint` | 78 tests OK · exit 0 |

Revert check: removing the `lanes_problems` call from `check_index`
fails 9 of the lanes tests. Each round-1 test was
proved by a mutation that made it fail (write → `pass`, the END guard
removed, `entry_phase` for `cell`, lanes
reversed, the condition dedupe removed).

Review: design review 3 rounds (12 findings, all fixed). Code review 2
rounds: round 1 found 5 test and doc gaps,
fixed in `09bb374`; round 2 clean.

## Notes

- The implementer split `build` and `router_problems` to keep complexity
at 5 or less; cleanup restored `main`'s names
  and put `build_lanes` and `lanes_problems` beside them.
- `lanes_render` prints one summary line for an invalid lanes-v2;
`check_process` names each broken rule.
* **crq** — no. lanes-v2.json sits beside lanes.json; nothing reads
it yet, and v1 is unchanged.

Rollback: revert this PR; no data or reader depends on lanes-v2 yet.

## Change

```text
plugins/rulebook/skills/crq/
  A process/lanes-v2.json                 the approved draft, act_on -> act-on
  A process/schema/lanes-v2.schema.json   urn:rulebook:crq:lanes:2, closed objects, lanes as prefixItems
  M SKILL.md                              one "Process files" line
scripts/
  A lanes_graph.py                        problems(doc, roles): RULES, 15 pure rules
  M check_process.py                      SCHEMAS += lanes-v2; load_json; lanes_v2_problems; process_problems
M CONTRIBUTING.md                         check_process.py row lists the lanes-v2 failures
tests/
  M test_check_process.py                 valid lanes-v2 in the temp tree; 46 lanes-v2 planted rows, each with its expected text
```

```text
check_process.problems
  └─ process_problems(process)
       ├─ load_schemas            missing / unknown keyword -> stop
       ├─ required(lanes.json, lanes-v2.json, review.json, glossary.md)
       │    └─ lanes_v2_problems  load_json -> validate(schema) -> lanes_graph.problems(doc, card roles)
       └─ card_problems
```

## Operator review needed

- **Gate file:** `scripts/check_process.py` runs in `make lint` on every
PR. A wrong rule blocks every later PR.
- **Instruction files:** `plugins/rulebook/skills/crq/SKILL.md` (one
"Process files" line) and the
  `CONTRIBUTING.md` check_process row.
- **Size waiver:** the diff is 450 added lines, over the 400-line limit.
The operator waived the limit for this PR in
  code review round 1.

## Where to look

1. `scripts/lanes_graph.py` `out_of_order` and `bad_targets`: the rank
of a duplicated id, and how a `{to, counts}` edge
   with extra keys is refused.
2. `scripts/check_process.py` `process_problems`: the file rule list
replaces the inline checks in `problems()`; the
   messages for a missing file stay `"<process>: no <file>"`.
3. `lanes-v2.schema.json`: `$schema` is declared as a string, not pinned
to `urn:rulebook:crq:lanes:2`.

## Evidence (base 2fdd2bc, head 84c46c1)

`<planted>` plants each named `PLANTED` case in a temp process tree,
runs `check_process`, and prints the line that
holds the row's expected text. Every row below exits 1.

| AC | command | result |
|---|---|---|
| AC-1 | `make test && make lint; echo exit=$?` | `Ran 58 tests ... OK`;
`Validation passed` |
| AC-1 | `sed 's/"act_on"/"act-on"/g' <draft> \| diff -
process/lanes-v2.json` | `diff exit=0` |
| AC-2 | `<planted> v2-lane-unknown-phase v2-lane-out-of-phase-order
v2-lane-phase-repeated v2-phase-twice` | ``lane `feature`: phase
`triage` is not in the phase order``; ``lane `tiny`: phase `gate` comes
after `timeline-record`, against the phase order``; ``lane `tiny`: phase
`intake` appears twice``; ``phase `build`: appears 2 times in the phase
order`` |
| AC-3 | `<planted> v2-no-outcomes v2-edge-number v2-edge-extra-key
v2-edge-target` | ``phase `build`: has no outcomes``; ``phase `build`,
outcome `done`: must be a string, or an object with a string `to`, an
optional string `counts` and no other key``; the same for ``phase
`gate`, outcome `red` ``; ``phase `approval`, outcome `changes`: points
at `design`, which is not a phase id, next, end, human or `human, then
same` `` |
| AC-4 | `<planted> v2-counts-uncapped v2-cap-zero` | ``phase `gate`,
outcome `red`: counts `ready`, which has no cap``; ``cap `gate_red`: 0
is not an integer of at least 1`` |
| AC-5 | `<planted> v2-when-unknown v2-condition-empty
v2-condition-number` | ``lane `bug`: phase `build` has when
`big-change`, which names no condition``; ``condition `design-needed`:
its text is empty``; ``condition `design-needed`: is not text`` |
| AC-6 | `<planted> v2-no-approval v2-approval-with-when
v2-no-timeline-record` | ``lane `one-way door`: no plain `approval`
entry (the approval floor)``; ``lane `feature`: no plain `approval`
entry (the approval floor)``; ``lane `feature`: does not end with a
plain `timeline-record` entry`` |
| AC-7 | `<planted> v2-lane-out-of-order v2-lens-cap-missing
v2-review-model-bad v2-effort-bad` | `lanes[1].lane: 'feature' is not
'bug'`; ``lanes[1]: `lens_cap` is missing``; `lanes[2].review_model:
'best' is not one of standard, strongest`; `lanes[3].effort: 'max' is
not one of low, medium, high` |
| AC-7 | accept side: the valid fixture uses `lens_cap` 1, 3 and
`"all"`, both `review_model` values, all three `effort` values,
`report`, a `human` target and an edge with no `counts` | removing any
one of these from the schema or `ENDS` fails `tests.test_check_process`
|
| AC-8 | `git diff --quiet main -- process/lanes.json
process/schema/lanes-v1.schema.json; python3 scripts/check_process.py .`
| `v1 diff exit=0`; `check_process exit=0` |
| AC-9 | `<planted> v2-no-schema v2-schema-unknown-keyword` |
`lanes-v2.schema.json: missing, or not JSON`;
``#/properties/lanes/allOf/1: unsupported keyword `maxItems` `` |
| AC-10 | `grep -n 'lanes-v2.json](process/lanes-v2.json)' SKILL.md;
python3 scripts/check_links.py .` | one match; `check_links exit=0` |
| AC-11 | `<planted> v2-missing` | `.../skills/crq/process: no
lanes-v2.json` |
| AC-12 | `<planted> v2-actor-unknown` | ``phase `build`: actor
`builder` is not a card role, human or engine`` |
| AC-13 | `<planted> v2-lens-cap-zero v2-lane-raise-target` | ``lane
`bug`: lens_cap 0 is below 1``; ``lane_raise: `to` names `spec`, which
is not a phase id`` |

Revert check: with `RULES = []` in `lanes_graph.py`,
`tests.test_check_process` fails on every graph row.

Code review: 3 rounds (RV9 cap). Round 3 found 2 test gaps on the accept
side; `84c46c1` closes both.

## Notes

- DEVIATION: `problems()` in `scripts/check_process.py` is split into
`required()` and `process_problems()`, instead of
growing in place, so each function stays at cyclomatic complexity 5 or
less.
- The design's ten rule groups are 15 functions in `RULES`: order is
`duplicate_phase_ids`, `unknown_lane_phases` and
`out_of_order`; edges is `no_outcomes`, `bad_edges` and `bad_targets`
(both use `is_valid_edge`); conditions is
  `unknown_conditions` and `empty_conditions`.
- Not in this PR: kebab-case enforcement for outcome keys is noted on
#364.

### 

* **crq** — describe lanes-v2 as the flow in the design doc and glossary · [#364](https://github.com/chiyanram/skills/issues/364) (PR [#371](https://github.com/chiyanram/skills/pull/371))

### ✨ Features

* **crq** — a breaker run tries to break a one-way-door design before approval · [#367](https://github.com/chiyanram/skills/issues/367) (PR [#375](https://github.com/chiyanram/skills/pull/375))
* **crq** — lanes-v2 holds the phase graph, outcome edges and caps · [#361](https://github.com/chiyanram/skills/issues/361) (PR [#368](https://github.com/chiyanram/skills/pull/368))
* **crq** — make index builds the lanes diagram and table from lanes-v2 · [#363](https://github.com/chiyanram/skills/issues/363) (PR [#370](https://github.com/chiyanram/skills/pull/370))
* **crq** — report-v1 schema, and each card cites the schema of its hand-off · [#362](https://github.com/chiyanram/skills/issues/362) (PR [#372](https://github.com/chiyanram/skills/pull/372))

### 🐛 Fixes

* **crq** — the breaker leaves the automatic process, and card-v1 goes back to the roles the engine runs · [#384](https://github.com/chiyanram/skills/issues/384) (PR [#386](https://github.com/chiyanram/skills/pull/386))

Update: `claude plugin update rulebook@chiyanram`

## [2.0.0](https://github.com/chiyanram/skills/compare/rulebook--v1.1.2...rulebook--v2.0.0) (2026-11-12)

### ⚠️ Breaking changes

* **crq** — the onboarder card leaves the plugin; the engine owns it (#345) (#347)
* **testing** — one short procedure in place of thirteen references (#339) (#343)

### ✨ Features

* **crq** — apply the agent-factory design audit's rule changes · [#295](https://github.com/chiyanram/skills/issues/295) (PR [#296](https://github.com/chiyanram/skills/pull/296))
* **crq** — codebase health (DSN2, CR8) and a red check stays red (VB9) · [#308](https://github.com/chiyanram/skills/issues/308) (PR [#318](https://github.com/chiyanram/skills/pull/318))
* **crq** — coordinator card follows K6 and design review asks refactor first (SR23) · [#307](https://github.com/chiyanram/skills/issues/307) (PR [#317](https://github.com/chiyanram/skills/pull/317))
* **crq** — evidence is real command output, never a gate run as proof of content · [#302](https://github.com/chiyanram/skills/issues/302) (PR [#322](https://github.com/chiyanram/skills/pull/322))
* **crq** — new design-reviewer, cleanup and onboarder card bodies · [#311](https://github.com/chiyanram/skills/issues/311) (PR [#319](https://github.com/chiyanram/skills/pull/319))
* **crq** — one closed set of values per finding field · [#305](https://github.com/chiyanram/skills/issues/305) (PR [#320](https://github.com/chiyanram/skills/pull/320))
* **crq** — quarantine one test with a capped expiry, and say so where people read ([chiyanram/agent-factory#460](https://github.com/chiyanram/agent-factory/issues/460)) · PR [#326](https://github.com/chiyanram/skills/pull/326)
* **crq** — role card format and role-eval rubric for the shared records · [#298](https://github.com/chiyanram/skills/issues/298) (PR [#301](https://github.com/chiyanram/skills/pull/301))
* **crq** — role cards list guardrail ids and drop next · [#295](https://github.com/chiyanram/skills/issues/295) (PR [#297](https://github.com/chiyanram/skills/pull/297))
* **crq** — severity is blocker, warning or nit, and the bucket is the verify pass's · [#305](https://github.com/chiyanram/skills/issues/305) (PR [#321](https://github.com/chiyanram/skills/pull/321))
* **crq** — the onboarder card leaves the plugin; the engine owns it · [#345](https://github.com/chiyanram/skills/issues/345) (PR [#347](https://github.com/chiyanram/skills/pull/347))
* **crq** — versioned card, lanes and finding schemas, and check every card and lanes file against them · [#305](https://github.com/chiyanram/skills/issues/305) (PR [#316](https://github.com/chiyanram/skills/pull/316))
* **testing** — one short procedure in place of thirteen references · [#339](https://github.com/chiyanram/skills/issues/339) (PR [#343](https://github.com/chiyanram/skills/pull/343))
* **testing** — planted cases for every check, and numbers only as settings keys · [#312](https://github.com/chiyanram/skills/issues/312) (PR [#323](https://github.com/chiyanram/skills/pull/323))

### 🐛 Fixes

* **crq** — a quarantine is one test, never a job, and a person's quarantine is not a VB6 skip ([chiyanram/agent-factory#460](https://github.com/chiyanram/agent-factory/issues/460)) · PR [#336](https://github.com/chiyanram/skills/pull/336)
* **crq** — the onboarder card says the engine lists the project's MUSTs in the brief · [#299](https://github.com/chiyanram/skills/issues/299) (PR [#300](https://github.com/chiyanram/skills/pull/300))

Update: `claude plugin update rulebook@chiyanram`

## [1.1.2](https://github.com/chiyanram/skills/compare/rulebook--v1.1.1...rulebook--v1.1.2) (2026-11-10)

### 🐛 Fixes

* **crq** — the design-reviewer card hands off the JSON it returns · PR [#279](https://github.com/chiyanram/skills/pull/279)
* **repo** — leave git trailers out of breaking-change release notes · [#283](https://github.com/chiyanram/skills/issues/283) (PR [#284](https://github.com/chiyanram/skills/pull/284))

Update: `claude plugin update rulebook@chiyanram`

## [1.1.1](https://github.com/chiyanram/skills/compare/rulebook--v1.1.0...rulebook--v1.1.1) (2026-11-09)

### Bug Fixes

* **crq:** ask every open question at once, with choices ([#275](https://github.com/chiyanram/skills/issues/275)) ([bd1622b](https://github.com/chiyanram/skills/commit/bd1622b4b00e4941d68a7b2db7f130b1add2a3e8))
* **crq:** the finder card hands off the design's finding contract ([#237](https://github.com/chiyanram/skills/issues/237)) ([#274](https://github.com/chiyanram/skills/issues/274)) ([44d4a13](https://github.com/chiyanram/skills/commit/44d4a13678621bb21d143e503abd7a501d274147))

## [1.1.0](https://github.com/chiyanram/skills/compare/rulebook--v1.0.0...rulebook--v1.1.0) (2026-11-09)

### Features

* **agent:** add the agent domain with its seven references ([#134](https://github.com/chiyanram/skills/issues/134)) ([#266](https://github.com/chiyanram/skills/issues/266)) ([0d2744c](https://github.com/chiyanram/skills/commit/0d2744c73e5c319de46acbddfb7acda5c0b1e5f2)), closes [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#271](https://github.com/chiyanram/skills/issues/271) [#132](https://github.com/chiyanram/skills/issues/132)

## [1.0.0](https://github.com/chiyanram/skills/compare/rulebook--v0.45.0...rulebook--v1.0.0) (2026-11-09)

### ⚠ BREAKING CHANGES

* **planning:** rule IDs GA3 and CV1 are removed, and acceptance
criteria are no longer Gherkin scenarios.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012EphAgXmJeLDVFfEgSjwGe
* **planning:** rule ID GT2 is removed.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012EphAgXmJeLDVFfEgSjwGe

### Features

* **planning:** numbered AC-n lines replace Gherkin, with the AC-to-tests and glossary wording passes ([#244](https://github.com/chiyanram/skills/issues/244)) ([#260](https://github.com/chiyanram/skills/issues/260)) ([f9702ef](https://github.com/chiyanram/skills/commit/f9702ef83a51eb4b93943e8f9f82ba8bf417de43)), closes [#237](https://github.com/chiyanram/skills/issues/237)

## [0.45.0](https://github.com/chiyanram/skills/compare/rulebook--v0.44.0...rulebook--v0.45.0) (2026-11-09)

### Features

* **crq:** a full retro runs only when a human starts one ([#244](https://github.com/chiyanram/skills/issues/244)) ([#262](https://github.com/chiyanram/skills/issues/262)) ([d9ab715](https://github.com/chiyanram/skills/commit/d9ab71598665d098d1feb514bd015e3a5c9cf672))

## [0.44.0](https://github.com/chiyanram/skills/compare/rulebook--v0.43.0...rulebook--v0.44.0) (2026-11-09)

### Features

* **crq:** add the review baseline as process/review.json, checked by check_process.py ([#265](https://github.com/chiyanram/skills/issues/265)) ([0438085](https://github.com/chiyanram/skills/commit/0438085c93cf74f26a5926809b5b58d5c082a354))

## [0.43.0](https://github.com/chiyanram/skills/compare/rulebook--v0.42.0...rulebook--v0.43.0) (2026-11-09)

### Features

* **crq:** add the cleanup, retro and onboarder cards and their scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#252](https://github.com/chiyanram/skills/issues/252)) ([bff98af](https://github.com/chiyanram/skills/commit/bff98afd2c797546b1d39e322fe5b4165d709c4c))

## [0.42.0](https://github.com/chiyanram/skills/compare/rulebook--v0.41.0...rulebook--v0.42.0) (2026-11-09)

### Features

* **crq:** add the implementer card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#249](https://github.com/chiyanram/skills/issues/249)) ([24a3616](https://github.com/chiyanram/skills/commit/24a3616dbd0cd80cc0c9d878baaa579a10664602))

## [0.41.0](https://github.com/chiyanram/skills/compare/rulebook--v0.40.0...rulebook--v0.41.0) (2026-11-09)

### Features

* **crq:** add the test-first card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#248](https://github.com/chiyanram/skills/issues/248)) ([aee0579](https://github.com/chiyanram/skills/commit/aee0579e3ab98ba0f502252a325b8b0c4a4106e6))

## [0.40.0](https://github.com/chiyanram/skills/compare/rulebook--v0.39.0...rulebook--v0.40.0) (2026-11-09)

### Features

* **crq:** add the design-reviewer card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#247](https://github.com/chiyanram/skills/issues/247)) ([f7abca0](https://github.com/chiyanram/skills/commit/f7abca0c37e911047becba5810b24e4836372b42))

## [0.39.0](https://github.com/chiyanram/skills/compare/rulebook--v0.38.0...rulebook--v0.39.0) (2026-11-09)

### Features

* **crq:** add the coordinator card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#246](https://github.com/chiyanram/skills/issues/246)) ([73397bb](https://github.com/chiyanram/skills/commit/73397bbb75e4f9b77a4056826606e577e1f4ea38))

## [0.38.0](https://github.com/chiyanram/skills/compare/rulebook--v0.37.0...rulebook--v0.38.0) (2026-11-09)

### Features

* **crq:** add the verify-pass card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#245](https://github.com/chiyanram/skills/issues/245)) ([e8f93cd](https://github.com/chiyanram/skills/commit/e8f93cd0729bb87540ff6d96f03e6c9355b7a32c))

## [0.37.0](https://github.com/chiyanram/skills/compare/rulebook--v0.36.0...rulebook--v0.37.0) (2026-11-09)

### Features

* **crq:** add the lanes file, the glossary and the finder card ([#237](https://github.com/chiyanram/skills/issues/237)) ([#243](https://github.com/chiyanram/skills/issues/243)) ([2cee43b](https://github.com/chiyanram/skills/commit/2cee43b69362dd00d961d584351222af31253eb3))

## [0.36.0](https://github.com/chiyanram/skills/compare/rulebook--v0.35.1...rulebook--v0.36.0) (2026-11-09)

### Features

* **crq:** add the test-integrity review rubric ([#235](https://github.com/chiyanram/skills/issues/235)) ([#241](https://github.com/chiyanram/skills/issues/241)) ([3888c9e](https://github.com/chiyanram/skills/commit/3888c9ea041527acfdccce19b75ae44cfc195353))

### Bug Fixes

* **crq:** role evals live in evals/<role>/, the review cases become the finder's ([#236](https://github.com/chiyanram/skills/issues/236)) ([#242](https://github.com/chiyanram/skills/issues/242)) ([e37f14f](https://github.com/chiyanram/skills/commit/e37f14fcf2b19bf81134622ddde1674775fee4fe))

## [0.35.1](https://github.com/chiyanram/skills/compare/rulebook--v0.35.0...rulebook--v0.35.1) (2026-11-09)

### Bug Fixes

* **crq:** approval binds spec and design, a three-round review cap, one size rule ([#234](https://github.com/chiyanram/skills/issues/234)) ([#240](https://github.com/chiyanram/skills/issues/240)) ([2055d87](https://github.com/chiyanram/skills/commit/2055d873ef427726cca99196076e8b2544bf367d))

## [0.35.0](https://github.com/chiyanram/skills/compare/rulebook--v0.34.1...rulebook--v0.35.0) (2026-11-09)

### Features

* **planning:** every review check names when it applies, its evidence, its edges, severity and verify ([#210](https://github.com/chiyanram/skills/issues/210)) ([#232](https://github.com/chiyanram/skills/issues/232)) ([2db978f](https://github.com/chiyanram/skills/commit/2db978fb8f850a00ca2b8ecafecebab89f1b15c6))

## [0.34.1](https://github.com/chiyanram/skills/compare/rulebook--v0.34.0...rulebook--v0.34.1) (2026-11-08)

### Bug Fixes

* **code:** name JPA entities and repositories in the router, with a free routing check ([#223](https://github.com/chiyanram/skills/issues/223)) ([#228](https://github.com/chiyanram/skills/issues/228)) ([734fb63](https://github.com/chiyanram/skills/commit/734fb633da2f3417062615d3b1ef9c05bfe5bb7f))

## [0.34.0](https://github.com/chiyanram/skills/compare/rulebook--v0.33.0...rulebook--v0.34.0) (2026-11-08)

### Features

* **crq:** Group B rules from the outside skill repos ([#223](https://github.com/chiyanram/skills/issues/223)) ([#227](https://github.com/chiyanram/skills/issues/227)) ([369f28f](https://github.com/chiyanram/skills/commit/369f28f847eedc019e23bdb119b8480c814f9263))

## [0.33.0](https://github.com/chiyanram/skills/compare/rulebook--v0.32.1...rulebook--v0.33.0) (2026-11-07)

### Features

* **planning:** seven rules from the outside skill repos ([#223](https://github.com/chiyanram/skills/issues/223)) ([#226](https://github.com/chiyanram/skills/issues/226)) ([49c312e](https://github.com/chiyanram/skills/commit/49c312e07ad8d89c4a816ad8ab31ff908ad7b035))

### Bug Fixes

* **repo:** merge the ledger with union and check it for repeated rows ([#224](https://github.com/chiyanram/skills/issues/224)) ([f8a91d6](https://github.com/chiyanram/skills/commit/f8a91d6117556256818ec4343a34752ef97c9042))

## [0.32.1](https://github.com/chiyanram/skills/compare/rulebook--v0.32.0...rulebook--v0.32.1) (2026-11-06)

### Bug Fixes

* **crq:** approval gate counts a human-only control recorded with the spec hash ([#210](https://github.com/chiyanram/skills/issues/210)) ([#222](https://github.com/chiyanram/skills/issues/222)) ([2c54c46](https://github.com/chiyanram/skills/commit/2c54c4677c51e0a363a3c1329911414180c4472f))

## [0.32.0](https://github.com/chiyanram/skills/compare/rulebook--v0.31.1...rulebook--v0.32.0) (2026-11-06)

### Features

* **crq:** review never approves, approval is human-signed, new deps go to the human ([#210](https://github.com/chiyanram/skills/issues/210)) ([#221](https://github.com/chiyanram/skills/issues/221)) ([abfec90](https://github.com/chiyanram/skills/commit/abfec90f3d72dfd4be2b1ca38c5efe956ac57018))

## [0.31.1](https://github.com/chiyanram/skills/compare/rulebook--v0.31.0...rulebook--v0.31.1) (2026-11-06)

### Bug Fixes

* **crq:** name the approval gate, not a /approved token ([#210](https://github.com/chiyanram/skills/issues/210)) ([#220](https://github.com/chiyanram/skills/issues/220)) ([02b0d50](https://github.com/chiyanram/skills/commit/02b0d50c9416ca41723d38669531afee29721008))

## [0.31.0](https://github.com/chiyanram/skills/compare/rulebook--v0.30.0...rulebook--v0.31.0) (2026-11-06)

### Features

* **code:** Redis reference and Redis Streams messaging rules ([#219](https://github.com/chiyanram/skills/issues/219)) ([3b78b10](https://github.com/chiyanram/skills/commit/3b78b103e25cf3240d50ff36760f50ae3c402f77)), closes [#71](https://github.com/chiyanram/skills/issues/71) [#56](https://github.com/chiyanram/skills/issues/56) [#71](https://github.com/chiyanram/skills/issues/71)

## [0.30.0](https://github.com/chiyanram/skills/compare/rulebook--v0.29.0...rulebook--v0.30.0) (2026-11-06)

### Features

* **code:** rules from a production-incident check of the merged references ([#218](https://github.com/chiyanram/skills/issues/218)) ([1247551](https://github.com/chiyanram/skills/commit/12475510841e153e341b8d32abb72d4a1873f7eb))

## [0.29.0](https://github.com/chiyanram/skills/compare/rulebook--v0.28.0...rulebook--v0.29.0) (2026-11-06)

### Features

* **code:** scheduling and batch jobs reference ([#217](https://github.com/chiyanram/skills/issues/217)) ([9fcf7c4](https://github.com/chiyanram/skills/commit/9fcf7c4c01747f3514129c5ce3c3ffcfdc131700)), closes [#52](https://github.com/chiyanram/skills/issues/52) [#52](https://github.com/chiyanram/skills/issues/52)

## [0.28.0](https://github.com/chiyanram/skills/compare/rulebook--v0.27.0...rulebook--v0.28.0) (2026-11-06)

### Features

* **code:** API design reference — pagination, compatibility, versioning ([#216](https://github.com/chiyanram/skills/issues/216)) ([9af215e](https://github.com/chiyanram/skills/commit/9af215ecc0f7cce5f188f22eaa4ee32059ed3f7c)), closes [#74](https://github.com/chiyanram/skills/issues/74) [#74](https://github.com/chiyanram/skills/issues/74) [#74](https://github.com/chiyanram/skills/issues/74)

## [0.27.0](https://github.com/chiyanram/skills/compare/rulebook--v0.26.0...rulebook--v0.27.0) (2026-11-06)

### Features

* **crq:** the /crq pipeline skill with its six references, and four planning rules ([chiyanram/skills#210](https://github.com/chiyanram/skills/issues/210)) ([#214](https://github.com/chiyanram/skills/issues/214)) ([58ac935](https://github.com/chiyanram/skills/commit/58ac93511acbfd8b2d523cc5b6925f9e9ffe8e17))

## [0.26.0](https://github.com/chiyanram/skills/compare/rulebook--v0.25.0...rulebook--v0.26.0) (2026-11-06)

### Features

* **code:** concurrent-edit rules — ETag and If-Match, 409 for lost races, required idempotency keys ([#215](https://github.com/chiyanram/skills/issues/215)) ([a7ed9da](https://github.com/chiyanram/skills/commit/a7ed9da9ad82390b424d2a04d7a99045477319c1)), closes [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75)

## [0.25.0](https://github.com/chiyanram/skills/compare/rulebook--v0.24.0...rulebook--v0.25.0) (2026-11-06)

### Features

* **code:** resilience rules — one retry layer, deadline propagation, idempotency keys, Retry-After ([#213](https://github.com/chiyanram/skills/issues/213)) ([512998b](https://github.com/chiyanram/skills/commit/512998b0cbc592949c59c01acf6e8a255f33841e)), closes [#54](https://github.com/chiyanram/skills/issues/54) [#54](https://github.com/chiyanram/skills/issues/54) [#54](https://github.com/chiyanram/skills/issues/54)

## [0.24.0](https://github.com/chiyanram/skills/compare/rulebook--v0.23.0...rulebook--v0.24.0) (2026-11-06)

### Features

* **code:** persistence reference — JPA fetching, paging, batching, ids, locking, pool ([#212](https://github.com/chiyanram/skills/issues/212)) ([547841f](https://github.com/chiyanram/skills/commit/547841f9a8809a0d4f2bd639fc0007f4248f68ae)), closes [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57)

## [0.23.0](https://github.com/chiyanram/skills/compare/rulebook--v0.22.0...rulebook--v0.23.0) (2026-11-04)

### Features

* **planning:** design-review rules SR9–SR15 in spec-review; SR4 asks for options and a recommendation (SR8) ([#207](https://github.com/chiyanram/skills/issues/207)) ([d77e110](https://github.com/chiyanram/skills/commit/d77e1103a794bd54956c2de601d76afb1cc853ae))

## [0.22.0](https://github.com/chiyanram/skills/compare/rulebook--v0.21.4...rulebook--v0.22.0) (2026-11-04)

### Features

* **code:** modern-java reference for current JDKs ([#208](https://github.com/chiyanram/skills/issues/208)) ([c1a2f70](https://github.com/chiyanram/skills/commit/c1a2f70f947251e6621438509abe8f5f3564c90f))

## [0.21.4](https://github.com/chiyanram/skills/compare/rulebook--v0.21.3...rulebook--v0.21.4) (2026-11-04)

### Bug Fixes

* **testing:** S6, a bug fix's failing test runs locally first ([#152](https://github.com/chiyanram/skills/issues/152)) ([#205](https://github.com/chiyanram/skills/issues/205)) ([90a7fb6](https://github.com/chiyanram/skills/commit/90a7fb63391e2504e3ef911fe67ece427645c64f))

## [0.21.3](https://github.com/chiyanram/skills/compare/rulebook--v0.21.2...rulebook--v0.21.3) (2026-11-04)

### Features

* **repo:** rule files hold only rules; check_provenance enforces it ([#204](https://github.com/chiyanram/skills/issues/204)) ([e81dd2d](https://github.com/chiyanram/skills/commit/e81dd2dc2880aba4059ba374c9e43ed3cfd0c980))

### Bug Fixes

* **code:** drop CM6; ER1, MS6 and DS12 examples keep decisions free of I/O ([#206](https://github.com/chiyanram/skills/issues/206)) ([b7c3511](https://github.com/chiyanram/skills/commit/b7c3511c808dd57f3438797424b36ca9091ff215))

## [0.21.2](https://github.com/chiyanram/skills/compare/rulebook--v0.21.1...rulebook--v0.21.2) (2026-11-04)

### Bug Fixes

* **obs:** migrations and obs files hold only rules ([#203](https://github.com/chiyanram/skills/issues/203)) ([6b23875](https://github.com/chiyanram/skills/commit/6b2387534012d8f77a5b00afb3a274dcc07c1670))

## [0.21.1](https://github.com/chiyanram/skills/compare/rulebook--v0.21.0...rulebook--v0.21.1) (2026-11-04)

### Bug Fixes

* **code:** industry re-check applied; code files hold only rules ([#200](https://github.com/chiyanram/skills/issues/200)) ([985d4dd](https://github.com/chiyanram/skills/commit/985d4ddaf3452c081014d66c97a2016246645f31))
* **planning:** planning and meta files hold only rules; SRC2 keeps provenance in the ledger ([#202](https://github.com/chiyanram/skills/issues/202)) ([8cb3682](https://github.com/chiyanram/skills/commit/8cb36826a11179eec5c40b8b286f3e12fde29f1b))
* **testing:** testing files hold only rules ([#201](https://github.com/chiyanram/skills/issues/201)) ([e9d9a0f](https://github.com/chiyanram/skills/commit/e9d9a0f9804e9d9b194ac516d1e44ee8d0f031f3))

## [0.21.0](https://github.com/chiyanram/skills/compare/rulebook--v0.20.0...rulebook--v0.21.0) (2026-11-04)

### Features

* **rulebook:** build each router's reference table with make index ([#199](https://github.com/chiyanram/skills/issues/199)) ([638d357](https://github.com/chiyanram/skills/commit/638d357ec5bba9700c2ef572b10d69bfcb5d6acf))

## [0.20.0](https://github.com/chiyanram/skills/compare/rulebook--v0.19.0...rulebook--v0.20.0) (2026-11-02)

### Features

* **meta:** writing-references reference from industry sources ([#197](https://github.com/chiyanram/skills/issues/197)) ([314a934](https://github.com/chiyanram/skills/commit/314a9349bdab212164f6f8d7bdc106ec01f871ac))
* **planning:** diagrams reference from industry sources ([#195](https://github.com/chiyanram/skills/issues/195)) ([b4b67ff](https://github.com/chiyanram/skills/commit/b4b67ff7fa6a329673b00dabbd42900fa2847414))
* **planning:** writing-docs reference from industry sources ([#196](https://github.com/chiyanram/skills/issues/196)) ([519f082](https://github.com/chiyanram/skills/commit/519f08256f89db537408b15f94015c6152afd97b))

## [0.19.0](https://github.com/chiyanram/skills/compare/rulebook--v0.18.0...rulebook--v0.19.0) (2026-11-02)

### Features

* **planning:** program-design reference from industry sources ([#194](https://github.com/chiyanram/skills/issues/194)) ([7dee76f](https://github.com/chiyanram/skills/commit/7dee76f11a9f83fa5f25611dec6b9f96d39bce99))

## [0.18.0](https://github.com/chiyanram/skills/compare/rulebook--v0.17.0...rulebook--v0.18.0) (2026-11-02)

### Features

* **planning:** spec-review reference from industry sources ([#193](https://github.com/chiyanram/skills/issues/193)) ([07e2efa](https://github.com/chiyanram/skills/commit/07e2efadcbde309db29dade23499c68274179f37))

## [0.17.0](https://github.com/chiyanram/skills/compare/rulebook--v0.16.3...rulebook--v0.17.0) (2026-11-02)

### Features

* **planning:** acceptance-criteria reference from industry sources ([#192](https://github.com/chiyanram/skills/issues/192)) ([0d19d09](https://github.com/chiyanram/skills/commit/0d19d0920dd99110a9d92c4b98e9d3b9128b7192))

## [0.16.3](https://github.com/chiyanram/skills/compare/rulebook--v0.16.2...rulebook--v0.16.3) (2026-11-01)

### Bug Fixes

* **code:** comments-concurrency-ui-services Good/Bad pairs come from sources, not project code ([#189](https://github.com/chiyanram/skills/issues/189)) ([6aba449](https://github.com/chiyanram/skills/commit/6aba449f933fd076589b8e51727eb62da2c4a4d2))
* **code:** errors-messaging Good/Bad pairs come from sources, not project code ([#187](https://github.com/chiyanram/skills/issues/187)) ([d25e8f5](https://github.com/chiyanram/skills/commit/d25e8f59cf8d57ac38e8bb3cf8cd1fd7b03cae18))
* **code:** java-types Good/Bad pairs come from sources, not project code ([#188](https://github.com/chiyanram/skills/issues/188)) ([0d694b2](https://github.com/chiyanram/skills/commit/0d694b202114f0a9be7085910a090fbaa77695cc))
* **code:** security Good/Bad pairs come from sources, not project code ([#185](https://github.com/chiyanram/skills/issues/185)) ([11ec167](https://github.com/chiyanram/skills/commit/11ec1678cba4cc27d22cb15a4f289ddd3224aaf3))
* **code:** smells-design Good/Bad pairs come from sources, not project code ([#186](https://github.com/chiyanram/skills/issues/186)) ([1d77a3e](https://github.com/chiyanram/skills/commit/1d77a3e431c9a4e117867b857980a3ae78ebb848))
* **code:** spring Good/Bad pairs come from sources, not project code ([#184](https://github.com/chiyanram/skills/issues/184)) ([d6fe8ab](https://github.com/chiyanram/skills/commit/d6fe8ab88dfa8634790f74d7b20e7b5a25128ae4))

## [0.16.2](https://github.com/chiyanram/skills/compare/rulebook--v0.16.1...rulebook--v0.16.2) (2026-11-01)

### Bug Fixes

* **code:** a rule line holds the rule only; preference moves to one line ([#183](https://github.com/chiyanram/skills/issues/183)) ([a2af313](https://github.com/chiyanram/skills/commit/a2af3136611c646bd722e3335cfd533e4fe3fcdd))

## [0.16.1](https://github.com/chiyanram/skills/compare/rulebook--v0.16.0...rulebook--v0.16.1) (2026-11-01)

### Bug Fixes

* **code:** angular-ui rules cite two sources or the preference label ([#170](https://github.com/chiyanram/skills/issues/170)) ([1deeabc](https://github.com/chiyanram/skills/commit/1deeabc03d1153f4ef858c071428d347f47b124e))
* **code:** comments rules cite two sources or the preference label ([#171](https://github.com/chiyanram/skills/issues/171)) ([6cba5f6](https://github.com/chiyanram/skills/commit/6cba5f60c0a5983136008bfa43fd047439308e3a))
* **code:** concurrency rules cite two sources or the preference label ([#172](https://github.com/chiyanram/skills/issues/172)) ([b3d8f0f](https://github.com/chiyanram/skills/commit/b3d8f0f9c8bdebbbb935227e81ef8791eb82750f))
* **code:** design rules cite two sources or the preference label ([#173](https://github.com/chiyanram/skills/issues/173)) ([2f5bc75](https://github.com/chiyanram/skills/commit/2f5bc750f33401c221e7f0634977c92f43342e50))
* **code:** deslop rules cite two sources or the preference label ([#174](https://github.com/chiyanram/skills/issues/174)) ([48a9229](https://github.com/chiyanram/skills/commit/48a92296a1a322f3a05882c50afb98041e960a89))
* **code:** errors rules cite two sources or the preference label ([#175](https://github.com/chiyanram/skills/issues/175)) ([5c34e38](https://github.com/chiyanram/skills/commit/5c34e38ec4ba00a9eaf5ebc3004bf73321c75e84))
* **code:** java rules cite two sources or the preference label ([#176](https://github.com/chiyanram/skills/issues/176)) ([742aa95](https://github.com/chiyanram/skills/commit/742aa956423926f727cf9356224d5028776d7400))
* **code:** messaging rules cite two sources or the preference label ([#177](https://github.com/chiyanram/skills/issues/177)) ([4d7c66e](https://github.com/chiyanram/skills/commit/4d7c66e24a989ed7af6a41f5f8d707d396491999))
* **code:** security rules cite two sources or the preference label ([#178](https://github.com/chiyanram/skills/issues/178)) ([4263af4](https://github.com/chiyanram/skills/commit/4263af4dda20c5f76478d23a91d482f51cef2d64))
* **code:** services rules cite two sources or the preference label ([#179](https://github.com/chiyanram/skills/issues/179)) ([d258c52](https://github.com/chiyanram/skills/commit/d258c52b421bf0746d2c95636ccfe13a40757671))
* **code:** smells rules cite two sources or the preference label ([#180](https://github.com/chiyanram/skills/issues/180)) ([fda57e4](https://github.com/chiyanram/skills/commit/fda57e4be1ac28ad37444a5a95a477b0aae7f54a))
* **code:** spring rules cite two sources or the preference label ([#181](https://github.com/chiyanram/skills/issues/181)) ([3ae91ca](https://github.com/chiyanram/skills/commit/3ae91ca5bfb924d8f9d90bf490d1676f789c67bc))
* **code:** types rules cite two sources or the preference label ([#182](https://github.com/chiyanram/skills/issues/182)) ([7a6f307](https://github.com/chiyanram/skills/commit/7a6f30725f16b4c7408846deba9437d66bb46a31))

## [0.16.0](https://github.com/chiyanram/skills/compare/rulebook--v0.15.0...rulebook--v0.16.0) (2026-10-31)

### Features

* **rulebook:** one SKILL.md router per domain, so references load ([#169](https://github.com/chiyanram/skills/issues/169)) ([7ce8e2d](https://github.com/chiyanram/skills/commit/7ce8e2dbe48fd5bd1f23c2ddedcc996c59e27388))

## [0.15.0](https://github.com/chiyanram/skills/compare/rulebook--v0.14.0...rulebook--v0.15.0) (2026-10-31)

### Features

* **obs:** tracing reference from industry sources ([#164](https://github.com/chiyanram/skills/issues/164)) ([f7980ed](https://github.com/chiyanram/skills/commit/f7980ed9451102247b6832356612af1237fe42d4))

## [0.14.0](https://github.com/chiyanram/skills/compare/rulebook--v0.13.0...rulebook--v0.14.0) (2026-10-31)

### Features

* **obs:** metrics reference from industry sources ([#163](https://github.com/chiyanram/skills/issues/163)) ([7ab70d7](https://github.com/chiyanram/skills/commit/7ab70d74d6f9918c43a5df7ed5d65045ef864e0a))

### Bug Fixes

* **obs:** review round 2 for the logging reference ([#166](https://github.com/chiyanram/skills/issues/166)) ([629c64f](https://github.com/chiyanram/skills/commit/629c64f035dffafb871e35a67c10e2d003d04f12))

## [0.13.0](https://github.com/chiyanram/skills/compare/rulebook--v0.12.0...rulebook--v0.13.0) (2026-10-31)

### Features

* **testing:** LLM testing references, fake tier and live tier ([#165](https://github.com/chiyanram/skills/issues/165)) ([3232cf1](https://github.com/chiyanram/skills/commit/3232cf1380c78a49c387a8be8b837de8216bf88a))

## [0.12.0](https://github.com/chiyanram/skills/compare/rulebook--v0.11.0...rulebook--v0.12.0) (2026-10-31)

### Features

* **obs:** logging reference from industry sources ([#161](https://github.com/chiyanram/skills/issues/161)) ([c82b50b](https://github.com/chiyanram/skills/commit/c82b50b15746746ba6a9ca4f932742a640e41225))

### Bug Fixes

* **migrations:** review round 1 for postgres-design, review and levels ([#162](https://github.com/chiyanram/skills/issues/162)) ([d8a8f3a](https://github.com/chiyanram/skills/commit/d8a8f3a7abee8f12883c76e33f249dc139b4c9a3))

## [0.11.0](https://github.com/chiyanram/skills/compare/rulebook--v0.10.0...rulebook--v0.11.0) (2026-10-31)

### Features

* **migrations:** review reference for safe changes to live tables ([#160](https://github.com/chiyanram/skills/issues/160)) ([697a3c1](https://github.com/chiyanram/skills/commit/697a3c1fecf67f041388fb87319257ccb6ad9f60))
* **obs:** levels reference, the log-level table from industry sources ([#158](https://github.com/chiyanram/skills/issues/158)) ([b534713](https://github.com/chiyanram/skills/commit/b534713d482a86b61b5028354555079ae6e22a6a))

## [0.10.0](https://github.com/chiyanram/skills/compare/rulebook--v0.9.0...rulebook--v0.10.0) (2026-10-31)

### Features

* **code:** security rule file ([#150](https://github.com/chiyanram/skills/issues/150)) ([bf58042](https://github.com/chiyanram/skills/commit/bf58042cdf97236f6ae5f4cc69cc32a08abaf8ff))

## [0.9.0](https://github.com/chiyanram/skills/compare/rulebook--v0.8.0...rulebook--v0.9.0) (2026-10-31)

### Features

* **code:** angular-ui rule file ([#151](https://github.com/chiyanram/skills/issues/151)) ([4ad861b](https://github.com/chiyanram/skills/commit/4ad861bd4939348a6b75e7fa990b7104fce3dc5e))
* **code:** messaging rule file ([#149](https://github.com/chiyanram/skills/issues/149)) ([62353ea](https://github.com/chiyanram/skills/commit/62353ea8156e57267bcba66e52698ac0d006ab67))

## [0.8.0](https://github.com/chiyanram/skills/compare/rulebook--v0.7.0...rulebook--v0.8.0) (2026-10-31)

### Features

* **code:** concurrency rule file ([#148](https://github.com/chiyanram/skills/issues/148)) ([3505519](https://github.com/chiyanram/skills/commit/3505519849aff3c28755fccd4edeeef6d3e8f03c))
* **code:** services rule file ([#146](https://github.com/chiyanram/skills/issues/146)) ([1865f60](https://github.com/chiyanram/skills/commit/1865f6041fc1fe8220ecb7cfed02bf0f428feffe))
* **code:** spring rule file ([#147](https://github.com/chiyanram/skills/issues/147)) ([49209e6](https://github.com/chiyanram/skills/commit/49209e6d80dbb2549cdedb681165c57f887f6a36))
* **migrations:** postgres-design reference from industry sources ([#157](https://github.com/chiyanram/skills/issues/157)) ([7f685cf](https://github.com/chiyanram/skills/commit/7f685cf2e1c20e1a9bb8ce1c3a7ae6fdb1f88e3d))

## [0.7.0](https://github.com/chiyanram/skills/compare/rulebook--v0.6.1...rulebook--v0.7.0) (2026-10-31)

### Features

* **code:** deslop rule skill ([#145](https://github.com/chiyanram/skills/issues/145)) ([38dbd61](https://github.com/chiyanram/skills/commit/38dbd619bf999f5cb207e782bdf8537e484573ab))

## [0.6.1](https://github.com/chiyanram/skills/compare/rulebook--v0.6.0...rulebook--v0.6.1) (2026-10-31)

### Bug Fixes

* **ci:** check only the PR's own commits for a skip-ci marker ([#156](https://github.com/chiyanram/skills/issues/156)) ([db7af03](https://github.com/chiyanram/skills/commit/db7af03f7bcf38bf43500aafdad862c4f2385e6b))

## [0.6.0](https://github.com/chiyanram/skills/compare/rulebook--v0.5.0...rulebook--v0.6.0) (2026-10-31)

### Features

* **code:** comments rule file ([#143](https://github.com/chiyanram/skills/issues/143)) ([5f3b9e0](https://github.com/chiyanram/skills/commit/5f3b9e007861a5fc3a3d863e86fce41f3d1d45dc))
* **code:** errors rule file ([#142](https://github.com/chiyanram/skills/issues/142)) ([001ad6e](https://github.com/chiyanram/skills/commit/001ad6e1d1234314761a4013d278d59f167b31e2))
* **code:** smells rule file ([#144](https://github.com/chiyanram/skills/issues/144)) ([fef4eb5](https://github.com/chiyanram/skills/commit/fef4eb55d7ae7d4e48846cb27cd7c50f48713ab4))

## [0.5.0](https://github.com/chiyanram/skills/compare/rulebook--v0.4.0...rulebook--v0.5.0) (2026-10-30)

### Features

* **code:** java rule file ([#141](https://github.com/chiyanram/skills/issues/141)) ([f1a4d94](https://github.com/chiyanram/skills/commit/f1a4d94c8f4ed9b3e0e88189e09c4e21d5ec1270))

## [0.4.0](https://github.com/chiyanram/skills/compare/rulebook--v0.3.0...rulebook--v0.4.0) (2026-10-30)

### Features

* **code:** types rule file ([#140](https://github.com/chiyanram/skills/issues/140)) ([08c0e1b](https://github.com/chiyanram/skills/commit/08c0e1bdfc5637807c8753fb7c24a8a099f3d75b))

## [0.3.0](https://github.com/chiyanram/skills/compare/rulebook--v0.2.0...rulebook--v0.3.0) (2026-10-30)

### Features

* **code:** design rule file ([#139](https://github.com/chiyanram/skills/issues/139)) ([4bea42f](https://github.com/chiyanram/skills/commit/4bea42f73edcdecf06e73de08fcf77de5a71e551))

### Bug Fixes

* **repo:** link cross-repo issue references to their own repo in release notes ([#129](https://github.com/chiyanram/skills/issues/129)) ([ba2a7a2](https://github.com/chiyanram/skills/commit/ba2a7a21c0713104c8d89ad9e380f9c8559a4817)), closes [#N](https://github.com/chiyanram/skills/issues/N) [owner/repo#N](https://github.com/owner/repo/issues/N) [repo#N](https://github.com/chiyanram/repo/issues/N) [owner/repo#N](https://github.com/owner/repo/issues/N)

## [0.2.0](https://github.com/chiyanram/skills/compare/rulebook--v0.1.0...rulebook--v0.2.0) (2026-10-30)

### Features

* **testing:** boundaries rule file (, 1 of 11) ([#113](https://github.com/chiyanram/skills/issues/113)) ([7a4d5e0](https://github.com/chiyanram/skills/commit/7a4d5e04828e2822b77119697902a4bfa81082b7)), closes [skills#112](https://github.com/chiyanram/skills/issues/112)
* **testing:** coverage-design rule file ([#116](https://github.com/chiyanram/skills/issues/116)) ([24f6c0b](https://github.com/chiyanram/skills/commit/24f6c0b2357279b720fa890bbb056cd340de6faa))
* **testing:** integration-tests rule file ([#119](https://github.com/chiyanram/skills/issues/119)) ([55187cc](https://github.com/chiyanram/skills/commit/55187cc89840da348a911ed35d846ceab1f60605))
* **testing:** mutation rule file ([#122](https://github.com/chiyanram/skills/issues/122)) ([09f7674](https://github.com/chiyanram/skills/commit/09f7674bbcdffc008feb432f848cb4fb08ba0176))
* **testing:** property-based rule file ([#123](https://github.com/chiyanram/skills/issues/123)) ([70ef00f](https://github.com/chiyanram/skills/commit/70ef00f6e768831267e2fc1754a66ce3dc6713a7))
* **testing:** scenario-to-tests rule file ([#121](https://github.com/chiyanram/skills/issues/121)) ([715aa11](https://github.com/chiyanram/skills/commit/715aa111795cecbf998b15e3b75f54a3909543fa))
* **testing:** smoke-specs rule file ([#124](https://github.com/chiyanram/skills/issues/124)) ([b57c2f8](https://github.com/chiyanram/skills/commit/b57c2f8e38012e9d97549884f923e9d8d1f82b87))
* **testing:** spock rule file ([#120](https://github.com/chiyanram/skills/issues/120)) ([366dcec](https://github.com/chiyanram/skills/commit/366dceccaa0bef2a7af300772922290527ef1c6b))
* **testing:** strategy rule file ([#115](https://github.com/chiyanram/skills/issues/115)) ([782b7a7](https://github.com/chiyanram/skills/commit/782b7a7c3aac16315ff9853f71a1577d6b1837b4))
* **testing:** unit-tests rule file ([#118](https://github.com/chiyanram/skills/issues/118)) ([7b25c8a](https://github.com/chiyanram/skills/commit/7b25c8ace1f6fdb1b98d332f998a43a0a3907cb4))
* **testing:** value-bar rule file ([#117](https://github.com/chiyanram/skills/issues/117)) ([cd0e23b](https://github.com/chiyanram/skills/commit/cd0e23ba493e0e9ba04a5eaa1e66d57fff1318f9))

### Bug Fixes

* **testing:** examples obey every rule; four rule conflicts resolved ([#126](https://github.com/chiyanram/skills/issues/126)) ([26d92b1](https://github.com/chiyanram/skills/commit/26d92b17c56b5e2dda022b4989606ff81e48e86b))

## 0.1.0 (2026-10-17)

### Features

* the `chiyanram` marketplace and the `rulebook` plugin, with an empty skills tree (G23 #93) ([4d69442](https://github.com/chiyanram/skills/commit/4d69442))
