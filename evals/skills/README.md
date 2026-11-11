# Skills eval

Measures one skill with its full text and with a shorter candidate, on a small fixed set of real tasks, scored only
by that skill's own review checks. It is how a pruning PR shows that the cut is no worse
(the pruning method, `docs/rulebook/pruning-method.md`).

Every run is a real model call on your own Claude login, so it runs by hand: never in `make lint`, `make test` or CI.
`scripts/skill_eval.py` stages and prints the command; it calls the model only with `--go`.

## Layout

```text
evals/skills/settings.json                    runs per case, baseline rounds, noise floor
evals/skills/<skill>/tune/<case>/             the cases a cut is tuned on: prompt.md + graders/*.md
evals/skills/<skill>/held-out/<case>/         run only at the gate, never while tuning
evals/skills/<skill>/results/<run>.json       each run's kept summary: pass counts per case and grader, skill size
evals/skills/<skill>/baseline.json            the full skill's rounds, and the operator's approval
```

Each grader states one of the skill's review checks, applied to the case. A case name is unique across every eval in
the repo, because the report lists cases by folder name.

## Record a baseline

```bash
python3 scripts/skill_eval.py stage deslop --go                    # round 1, full skill, tune slice
python3 scripts/skill_eval.py stage deslop --go                    # round 2
python3 scripts/skill_eval.py stage deslop --slice held-out --go   # the held-out slice, once
python3 scripts/skill_eval.py baseline deslop \
  --tune evals/skills/deslop/results/<round-1>.json evals/skills/deslop/results/<round-2>.json \
  --held-out evals/skills/deslop/results/<held-out>.json
```

Open a PR with the summaries and `baseline.json`. The operator approves the baseline by setting `"approved"` in it.

## Judge a candidate

```bash
python3 scripts/skill_eval.py stage deslop --candidate <folder> --go
python3 scripts/skill_eval.py stage deslop --candidate <folder> --slice held-out --go
python3 scripts/skill_eval.py compare deslop --tune <candidate tune summary> --held-out <candidate held-out summary>
```

`compare` exits `0` and says "keep" only when the baseline is approved, no case and grader passes less often than
the baseline by more than the noise, the held-out slice is no worse, and the candidate has fewer words. The noise is
the spread between the baseline's rounds, never less than `noise_floor_runs` runs' worth.
