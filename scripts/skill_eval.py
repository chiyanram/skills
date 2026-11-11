"""The skills eval: one skill's fixed tasks, run with the full skill and with a shorter candidate, scored by the
skill's own review checks, and compared against an approved baseline (docs/rulebook/pruning-method.md).

Every run is a real model call on the operator's login, so this script only stages and prints the command unless
`--go` is given. It never runs in `make lint`, `make test` or CI.

  stage     copy the plugin, swap in a candidate skill, add one slice of the skill's cases; print the eval command
  summarize reduce one `claude plugin eval --json` result to a kept summary under evals/skills/<skill>/results/
  baseline  record the full skill's tune rounds and held-out run as the skill's baseline, awaiting the operator
  compare   set a candidate's summaries beside the baseline and say keep or drop
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "rulebook"
EVALS = ROOT / "evals" / "skills"
SLICES = ("tune", "held-out")
ARMS = ("full", "candidate")
STAGED_EVAL_DIR = "skill-evals"


def settings() -> dict:
    return json.loads((EVALS / "settings.json").read_text())


def skill_dir(skill: str, candidate: Path | None) -> Path:
    return candidate if candidate else PLUGIN / "skills" / skill


def skill_words(folder: Path) -> int:
    return sum(len(f.read_text().split()) for f in sorted(folder.rglob("*.md")))


def cases_dir(skill: str, slice_: str) -> Path:
    folder = EVALS / skill / slice_
    if not any(folder.glob("*/prompt.md")):
        raise SystemExit(f"{folder}: no cases")
    return folder


def stage(skill: str, slice_: str, candidate: Path | None, work: Path) -> Path:
    staged = work / "rulebook"
    if staged.exists():
        shutil.rmtree(staged)
    shutil.copytree(PLUGIN, staged, ignore=shutil.ignore_patterns("results", "evals"))
    target = staged / "skills" / skill
    shutil.rmtree(target)
    shutil.copytree(skill_dir(skill, candidate), target)
    shutil.copytree(cases_dir(skill, slice_), staged / STAGED_EVAL_DIR)
    return staged


def eval_command(staged: Path, runs: int, result: Path) -> list[str]:
    return ["claude", "plugin", "eval", str(staged), "--eval-dir", STAGED_EVAL_DIR, "--ablation", "none",
            "--runs", str(runs), "--no-publish", "--json", str(result)]


def grader_counts(case: dict) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for run in case["arms"]["with"]:
        for grader in run["graders"]:
            if grader.get("withOnly") or grader.get("scored") is False:
                continue
            tally = counts.setdefault(grader["name"], {"passed": 0, "runs": 0})
            tally["runs"] += 1
            tally["passed"] += 1 if grader["passed"] else 0
    return counts


def summarize(result: dict, skill: str, arm: str, slice_: str, words: int) -> dict:
    if result.get("schemaVersion") != 1:
        raise SystemExit(f"unknown eval result schemaVersion {result.get('schemaVersion')!r}; update skill_eval.py")
    if result.get("partial"):
        raise SystemExit(f"the eval run is partial ({result.get('partialReason')}); run it again")
    return {"skill": skill, "arm": arm, "slice": slice_, "skill_words": words,
            "claude_version": result["claudeVersion"], "started_at": result["startedAt"],
            "cost_usd": result["costUsd"],
            "cases": {case["name"]: grader_counts(case) for case in result["cases"]}}


def rates(summary: dict) -> dict[tuple[str, str], float]:
    return {(case, grader): t["passed"] / t["runs"]
            for case, graders in summary["cases"].items() for grader, t in graders.items() if t["runs"]}


def baseline_rates(rounds: list[dict], floor: float) -> dict[tuple[str, str], tuple[float, float]]:
    per_round = [rates(r) for r in rounds]
    keys = set().union(*per_round)
    found = {}
    for key in keys:
        values = [r.get(key, 0.0) for r in per_round]
        found[key] = (sum(values) / len(values), max(max(values) - min(values), floor))
    return found


def worse(base: dict[tuple[str, str], tuple[float, float]], candidate: dict) -> list[str]:
    cand = rates(candidate)
    return [f"{case} / {grader}: {cand.get((case, grader), 0.0):.2f} against {mean:.2f} ± {noise:.2f}"
            for (case, grader), (mean, noise) in sorted(base.items()) if cand.get((case, grader), 0.0) < mean - noise - 1e-9]


def compare(baseline: dict, rounds: list[dict], held_out: dict | None, cand_tune: dict, cand_held_out: dict | None,
            floor: float) -> tuple[bool, list[str]]:
    lines, keep = [], True
    if not baseline.get("approved"):
        lines.append("baseline: not approved by the operator yet, so no candidate can be kept")
        keep = False
    tune_worse = worse(baseline_rates(rounds, floor), cand_tune)
    lines += [f"tune worse beyond noise: {w}" for w in tune_worse]
    full_words = rounds[0]["skill_words"]
    if cand_tune["skill_words"] >= full_words:
        lines.append(f"size: {cand_tune['skill_words']} words, not smaller than {full_words}")
        keep = False
    if held_out is None or cand_held_out is None:
        lines.append("held-out: not run, so the candidate cannot ship yet")
        keep = False
    else:
        held_worse = worse(baseline_rates([held_out], floor), cand_held_out)
        lines += [f"held-out worse beyond noise: {w}" for w in held_worse]
        keep = keep and not held_worse
    keep = keep and not tune_worse
    lines.append(f"size: {full_words} → {cand_tune['skill_words']} words")
    lines.append("verdict: keep" if keep else "verdict: drop")
    return keep, lines


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("stage")
    p.add_argument("skill")
    p.add_argument("--slice", choices=SLICES, default="tune")
    p.add_argument("--candidate", type=Path, help="a folder holding the shorter skill; omit for the full skill")
    p.add_argument("--work", type=Path, help="where to stage; default evals/skills/.work/<skill>-<arm>-<slice>")
    p.add_argument("--go", action="store_true", help="run the eval and summarize it (real model calls)")

    p = sub.add_parser("summarize")
    p.add_argument("result", type=Path)
    p.add_argument("skill")
    p.add_argument("--arm", choices=ARMS, required=True)
    p.add_argument("--slice", choices=SLICES, required=True)
    p.add_argument("--candidate", type=Path)
    p.add_argument("--out", type=Path)

    p = sub.add_parser("baseline")
    p.add_argument("skill")
    p.add_argument("--tune", type=Path, nargs="+", required=True, help="full-skill tune summaries, one per round")
    p.add_argument("--held-out", type=Path, help="the full skill's held-out summary")

    p = sub.add_parser("compare")
    p.add_argument("skill")
    p.add_argument("--tune", type=Path, required=True, help="the candidate's tune summary")
    p.add_argument("--held-out", type=Path, help="the candidate's held-out summary")

    args = parser.parse_args(argv)
    conf = settings()
    floor = conf["noise_floor_runs"] / conf["runs_per_case"]

    if args.command == "stage":
        arm = "candidate" if args.candidate else "full"
        work = args.work or EVALS / ".work" / f"{args.skill}-{arm}-{args.slice}"
        staged = stage(args.skill, args.slice, args.candidate, work)
        result = work / "result.json"
        command = eval_command(staged, conf["runs_per_case"], result)
        summary = ["python3", "scripts/skill_eval.py", "summarize", str(result), args.skill, "--arm", arm,
                   "--slice", args.slice] + (["--candidate", str(args.candidate)] if args.candidate else [])
        print(f"staged {staged}\n\nrun (real model calls):\n  {' '.join(command)}\nthen:\n  {' '.join(summary)}")
        if args.go:
            subprocess.run(command, check=True)
            return main(summary[2:])
        return 0

    if args.command == "summarize":
        folder = skill_dir(args.skill, args.candidate)
        summary = summarize(load(args.result), args.skill, args.arm, args.slice, skill_words(folder))
        stamp = summary["started_at"][:19].replace(":", "")
        write(args.out or EVALS / args.skill / "results" / f"{stamp}-{args.arm}-{args.slice}.json", summary)
        return 0

    if args.command == "baseline":
        rounds = [load(p) for p in args.tune]
        if len(rounds) < conf["baseline_rounds"]:
            raise SystemExit(f"a baseline needs {conf['baseline_rounds']} tune rounds, got {len(rounds)}")
        if any(r["arm"] != "full" or r["slice"] != "tune" for r in rounds):
            raise SystemExit("a baseline's tune rounds are full-skill tune summaries")
        rel = lambda p: str(Path(p).resolve().relative_to(ROOT))  # noqa: E731
        write(EVALS / args.skill / "baseline.json",
              {"skill": args.skill, "recorded": date.today().isoformat(), "approved": None,
               "tune": [rel(p) for p in args.tune], "held_out": rel(args.held_out) if args.held_out else None})
        print("the operator approves it by setting \"approved\" in a pull request")
        return 0

    baseline = load(EVALS / args.skill / "baseline.json")
    rounds = [load(ROOT / p) for p in baseline["tune"]]
    held_out = load(ROOT / baseline["held_out"]) if baseline.get("held_out") else None
    keep, lines = compare(baseline, rounds, held_out, load(args.tune),
                          load(args.held_out) if args.held_out else None, floor)
    print("\n".join(lines))
    return 0 if keep else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
