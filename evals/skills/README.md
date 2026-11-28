# Skills eval

Measures one skill with its full text and with a candidate, on a small fixed set of real tasks, scored by that
skill's own review checks. A skill change ships with this proof, and the operator approves it.

Every run is a real model call on your own Claude login, so it runs by hand: never in `make lint`, `make test` or CI.
`scripts/skill_eval.py` stages and prints the command; it calls the model only with `--go`.

## Tiers

Each skill has a tier in `settings.json`:

| tier | skills | proof |
|---|---|---|
| CORE | code, testing | everything below, 5 runs per case, the arms in turn, a repeated baseline, planted answers for each llm grader, and the operator's hand check of 20 judge verdicts (18 or more must agree) |
| NORMAL | every other skill with cases | cases, approved reference answers, an approved baseline, 3 runs per case |
| NONE | a change to wording only | `make lint` |

## Rules for a run you can trust

1. Start each case prompt with the typed slash (for example `/toolbox:deslop`), so the skill loads.
2. The judge and the agent model are pinned in `settings.json`. Do not run with others.
3. A run counts only when it ended without an error and its session file shows the skill was loaded. Any other run
   is an error, never a FAIL.
4. Each case has a `reference.md` answer. The operator approves it by setting `approved` in its frontmatter.
5. Point a grader at the trace (`focus: trace`) when the work is in files or tool calls, not in the last message.
   Use a free grader (`tool_used`, `regex`, `file_exists`) when the fact is mechanical.
6. A CORE llm grader gates only after its 9 planted answers (3 right, 3 wrong, 3 near misses) give 0 false PASS and
   at most 1 false FAIL. Write a planted answer as a statement about the work, not as first-person reasoning: the
   API can refuse to copy reasoning word for word, and the refused run is an error.
7. Commit the cases, the summaries and `baseline.json`. Keep raw transcripts out of the repo.

The order: write the lesson as a rule and a case that fails without it; run the baseline and the candidate; open a
pull request with the summaries; the operator approves the cases, the graders and the baseline, and merges.

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
fewer words. A rewrite changes what the skill teaches and may grow it: pass `--rewrite` and the word rule is
skipped, the score rules still apply. The noise is the spread between the baseline's rounds, never less than `noise_floor_runs` runs' worth.

## Check a grader with planted answers

```bash
python3 scripts/skill_eval.py planted deslop --go
```

Each planted answer becomes a case whose prompt makes the model reply with that answer, word for word. The grader
under test then judges known text. `planted-report` counts false PASS and false FAIL per grader against the gate in
`settings.json`, and writes `planted/results.json`. A reply that is not the planted text is an error. The operator
approves a planted set by setting `approved` in its `planted.json`.
