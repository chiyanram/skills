# Lanes

Which lane a change takes through the pipeline, and what each lane adds or skips. Read it when you take in a new
change, or when a change turns out bigger, riskier or smaller than its lane.

## Rules

- **LN1** — At intake, pick the lane from what the change touches (tiny, bug, feature or one-way door) and show it to
  the human, because one workflow for every size slows small fixes and under-reviews irreversible ones.
- **LN2** — Run a tiny change without spec, design or the approval gate, and move it to the bug or feature lane once it
  changes behaviour, because the full pipeline costs more than a typo is worth.
- **LN3** — In the one-way-door lane, list each irreversible step for the human's explicit yes and add the readiness
  items, because a step that cannot be undone needs inspection before it ships.
- **LN4** — Count only an approval the agent cannot produce, a human forge action or a prompt only the human answers,
  recorded with the spec's hash, because an agent-made approval passes its own work.

## When X, use Y

| situation | use | why |
|---|---|---|
| docs, comments, a config value that changes no behaviour, or a patch-level dependency bump | the tiny lane | nothing a spec or design would decide (LN2) |
| today's behaviour is wrong and the expected behaviour is known | the bug lane | the spec is current, expected and unchanged behaviour, proved by a failing test |
| new or changed behaviour | the feature lane | the full pipeline: spec, design, design review, the approval gate |
| the change touches stored data or a schema, a public API or event contract, or a deploy | the one-way-door lane | a wrong step cannot be undone (LN3) |
| unsure between two lanes | the heavier lane | a review that was too heavy costs time; a mistake in stored data cannot be undone |

The phases each lane runs:

| lane | phases | human gates |
|---|---|---|
| tiny | intake → build → verify → code review → gate → pull request → the retro record; a full retro only after a rescue or a revert | merge |
| bug | intake → research → spec → design (only when an internal interface or more than one module changes) → design review of the spec and any design → build → verify → cleanup → code review → gate → pull request → retro | approval, merge |
| feature | every phase | approval, merge |
| one-way door | every phase, plus the readiness items of the `pr-readiness` reference | approval with each irreversible step listed, merge |

## Good / Bad

### LN1 — Pick the lane from what the change touches

**Bad**
```text
Issue: Rename the column loans.due_on to loans.due_date
Lane: feature
```
A renamed column changes stored data. The feature lane never lists the drop of the old column for the human's yes.

**Good**
```text
Issue: Rename the column loans.due_on to loans.due_date
Lane: one-way door (changes stored data)
Irreversible steps for your yes:
  - drop loans.due_on, after every reader uses loans.due_date
```
The lane follows from what the change touches, and the irreversible step waits for the human.

## Decided edges

- **Skip the full pipeline when** a dependency bump is a patch release with no behaviour change: it is tiny (LN2). —
  **Do not skip when** the bump is a minor or major release, or changes behaviour: it is a feature. — **Confidence**
  high
- **Skip the one-way door when** a bug fix only changes code inside a body: it stays a bug. — **Do not skip when** the
  fix changes a stored format or a public contract: it is a one-way door (LN3). — **Confidence** high
- **Skip the one-way door when** a migration only adds a nullable column or a table that nothing reads yet: it is a
  feature. — **Do not skip when** it renames, retypes, drops or backfills: it is a one-way door (LN3). —
  **Confidence** medium

## Review checks

Walk the issue, the pull request and its diff.

- [ ] LN1 — Find the lane on the issue. Compare it with what the diff touches: stored data or a schema, a public
  contract or a deploy means the one-way door, except the decided edges above. A lane that is missing or too light is
  a finding.
- [ ] LN2 — For a tiny-lane change, check that the diff changes no behaviour: docs, comments, config values or a patch
  bump only. A tiny change with new logic is a finding.
- [ ] LN3 — For a one-way-door change, find the list of irreversible steps and the human's yes on each, and the
  readiness items in the pull request. Each one missing is a finding.
- [ ] LN4 — Find the approval record the pull request cites: who approved, when, how, and the spec hash. Check that the
  hash matches the spec the change built. An approval with no record, a record an agent could write, or a hash that
  does not match is a finding.