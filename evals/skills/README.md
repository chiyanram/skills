# Skills eval

Measures one skill with its full text and with a candidate, on a small fixed set of real tasks, scored by that
skill's own review checks. The rules for a run you can trust, and the tiers, are in
[CONTRIBUTING.md, Prove a skill change](../../CONTRIBUTING.md#prove-a-skill-change). This file is the how-to.

Every run is a real model call on your own Claude login, so it runs by hand: never in `make lint`, `make test` or CI.
`scripts/skill_eval.py` stages and prints the command; it calls the model only with `--go`.

## Layout

```text
evals/skills/settings.json                    pinned judge and agent model, tiers, each skill's tier, planted gate
evals/skills/reference-grader.md              the grader a case's approved reference answer is written into
evals/skills/<skill>/tune/<case>/             the cases a change is tuned on: prompt.md, graders/*.md, reference.md
evals/skills/<skill>/held-out/<case>/         run only at the gate, never while tuning
evals/skills/<skill>/planted/<set>/           planted.json and one file per planted answer, for one grader
evals/skills/<skill>/planted/results.json     each grader's last planted check: false PASS, false FAIL, gate
evals/skills/<skill>/results/<run>.json       each run's kept summary: pass counts, errors, models, case-file hashes
evals/skills/<skill>/baseline.json            the full skill's rounds, and the operator's approval
```

A case name is unique across every eval in the repo, because the report lists cases by folder name. A case prompt
starts with the skill's typed slash, so the skill loads. A `reference.md` holds the answer the operator approved;
until its `approved` field is set, `stage` leaves it out (`--draft-references` grades it anyway, for a trial).

## What counts

`summarize` reads each run's session file, which `claude plugin eval --keep-temp` leaves beside the run's trace. A
run with an error, with no session file, or whose session does not show the skill loaded, is listed under `errors`
and counts neither as a PASS nor as a FAIL. A grader that threw is an error too. Each summary records the pinned
judge, the agent models the sessions name, and a hash of every case file. `compare` drops a candidate whose
summary differs from the baseline in any of these.

## Record a baseline

```bash
python3 scripts/skill_eval.py stage deslop --go                    # full skill, tune slice, the tier's run count
python3 scripts/skill_eval.py stage deslop --slice held-out --go   # the held-out slice, once
python3 scripts/skill_eval.py baseline deslop \
  --tune evals/skills/deslop/results/<tune summary>.json --held-out evals/skills/deslop/results/<held-out>.json
```

A CORE baseline needs two tune rounds: run the first command twice. Open a pull request with the summaries and
`baseline.json`. The operator approves the baseline by setting `"approved"` in it.

## Judge a candidate

```bash
python3 scripts/skill_eval.py stage deslop --candidate <folder> --go
python3 scripts/skill_eval.py stage deslop --candidate <folder> --slice held-out --go
python3 scripts/skill_eval.py compare deslop --tune <candidate tune summary> --held-out <candidate held-out summary>
```

For a CORE skill, `--go` with a candidate runs one round at a time, the full skill and the candidate in turn, and
writes a summary for each; pass the full skill's summary to `compare` with `--full`, and it joins the baseline's
noise. `compare` exits `0` and says "keep" only when the baseline is approved, the inputs match, no case and grader
passes less often than the baseline by more than the noise, the held-out slice is no worse, and the candidate has
fewer words. The noise is the spread between the baseline's rounds, never less than `noise_floor_runs` runs' worth.

## Check a grader with planted answers

```bash
python3 scripts/skill_eval.py planted deslop --go
```

Each planted answer becomes a case whose prompt makes the model reply with that answer, word for word. The grader
under test then judges known text. `planted-report` counts false PASS and false FAIL per grader against the gate in
`settings.json`, and writes `planted/results.json`. A reply that is not the planted text is an error. The operator
approves a planted set by setting `approved` in its `planted.json`.
