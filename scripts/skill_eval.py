"""The skills eval: one skill's fixed tasks, run with the full skill and with a shorter candidate, scored by the
skill's own review checks, and compared against an approved baseline.

Every run is a real model call on the operator's login, so this script only stages and prints the command unless
`--go` is given. It never runs in `make lint`, `make test` or CI; `check_eval_proof.py` checks what it wrote.

A run counts only when it is valid: it ended without an error, and its session file shows that the skill under test
was loaded. Any other run is recorded as an error, never as a FAIL. The judge and the agent model are pinned in
`evals/skills/settings.json`, and every summary records them with a hash of each case file, so `compare` refuses
two summaries made from different inputs.

  stage     copy the plugin, swap in a candidate skill, add one slice of the skill's cases; print the eval command
  summarize reduce one or more `claude plugin eval --json` results to a kept summary under evals/skills/<skill>/results/
  baseline  record the full skill's tune rounds and held-out run as the skill's baseline, awaiting the operator
  compare   set a candidate's summaries beside the baseline and say keep or drop
  planted   stage the planted answers, which check that each grader passes right answers and fails wrong ones
  planted-report  score one planted run against the gate
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
EVALS = ROOT / "evals" / "skills"
SLICES = ("tune", "held-out")
ARMS = ("full", "candidate")
STAGED_EVAL_DIR = "skill-evals"
REFERENCE_TEMPLATE = EVALS / "reference-grader.md"
REFERENCE_GRADER = "reference-match.md"
GRADER_THREW = "grader threw"


def settings() -> dict:
    return json.loads((EVALS / "settings.json").read_text())


def tier_of(conf: dict, skill: str) -> dict:
    name = conf["skills"].get(skill)
    if name is None:
        raise SystemExit(f"{skill}: no tier in evals/skills/settings.json; add it under \"skills\"")
    return {"name": name, **conf["tiers"][name]}


def plugin_of(skill: str, plugins: Path = PLUGINS) -> Path:
    found = [p for p in sorted(plugins.iterdir()) if (p / "skills" / skill / "SKILL.md").is_file()]
    if len(found) != 1:
        raise SystemExit(f"{skill}: expected one plugin that ships it, found {len(found)}")
    return found[0]


def skill_dir(skill: str, candidate: Path | None) -> Path:
    return candidate if candidate else plugin_of(skill) / "skills" / skill


def skill_words(folder: Path) -> int:
    return sum(len(f.read_text().split()) for f in sorted(folder.rglob("*.md")))


def cases_dir(skill: str, slice_: str, evals: Path = EVALS) -> Path:
    folder = evals / skill / slice_
    if not any(folder.glob("*/prompt.md")):
        raise SystemExit(f"{folder}: no cases")
    return folder


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def case_inputs(folder: Path) -> dict[str, str]:
    """A hash of every file that decides a verdict: each case's prompt, graders and reference answer, and the
    reference grader they are written into."""
    found = {str(p.relative_to(folder)): sha(p) for p in sorted(folder.glob("*/**/*.md"))
             if p.name in ("prompt.md", "reference.md") or p.parent.name == "graders"}
    template = folder.parent.parent / REFERENCE_TEMPLATE.name
    if any(k.endswith("/reference.md") for k in found) and template.is_file():
        found[template.name] = sha(template)
    return found


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    fields = {}
    for line in head.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields, body


def approved(fields: dict[str, str]) -> bool:
    return fields.get("approved", "") not in ("", "null", "~")


def add_reference_graders(cases: Path, drafts: bool) -> list[str]:
    """Write each case's reference answer into a grader once its `approved` field is set, or when drafts are asked for."""
    skipped = []
    template = frontmatter(REFERENCE_TEMPLATE)[1]
    for reference in sorted(cases.glob("*/reference.md")):
        fields, body = frontmatter(reference)
        if not approved(fields) and not drafts:
            skipped.append(reference.parent.name)
        else:
            (reference.parent / "graders" / REFERENCE_GRADER).write_text(
                "---\ntype: llm\n---\n" + template.replace("{{reference}}", body.strip()))
        reference.unlink()
    return skipped


def copy_plugin(skill: str, work: Path) -> Path:
    plugin = plugin_of(skill)
    staged = work / plugin.name
    if staged.exists():
        shutil.rmtree(staged)
    shutil.copytree(plugin, staged, ignore=shutil.ignore_patterns("results", "evals"))
    return staged


def stage(skill: str, slice_: str, candidate: Path | None, work: Path, drafts: bool = False) -> Path:
    staged = copy_plugin(skill, work)
    target = staged / "skills" / skill
    shutil.rmtree(target)
    shutil.copytree(skill_dir(skill, candidate), target)
    shutil.copytree(cases_dir(skill, slice_), staged / STAGED_EVAL_DIR)
    for skipped in add_reference_graders(staged / STAGED_EVAL_DIR, drafts):
        print(f"{skipped}: reference answer not approved, so it is not graded")
    return staged


def eval_command(staged: Path, runs: int, result: Path, conf: dict) -> list[str]:
    return ["claude", "plugin", "eval", str(staged), "--eval-dir", STAGED_EVAL_DIR, "--ablation", "none",
            "--runs", str(runs), "--judge-model", conf["judge_model"], "--model", conf["agent_model"],
            "--keep-temp", "--trust-plugin", "--no-publish", "--json", str(result)]


def loaded_marker(skill: str) -> re.Pattern:
    return re.compile(r"Base directory for this skill: [^\"\\\n]*/skills/" + re.escape(skill) + r"(?![\w-])")


def session_text(run: dict) -> str | None:
    trace = run.get("tracePath")
    if not trace:
        return None
    projects = Path(trace).parent.parent / "config" / "projects"
    sessions = sorted(projects.rglob("*.jsonl")) if projects.is_dir() else []
    return "\n".join(s.read_text(errors="replace") for s in sessions) if sessions else None


def run_error(run: dict, skill: str) -> tuple[str | None, list[str]]:
    """Why a run proves nothing, or None when it is valid; and the agent models its session names."""
    if run.get("error"):
        return f"run error: {run['error']}", []
    text = session_text(run)
    if text is None:
        return "no session file, so no load proof (the eval must run with --keep-temp)", []
    models = sorted(set(re.findall(r'"model":\s*"(claude-[^"]+)"', text)))
    if not loaded_marker(skill).search(text):
        return f"{skill} was not loaded", models
    return None, models


def grader_counts(runs: list[dict]) -> tuple[dict[str, dict[str, int]], list[str]]:
    counts: dict[str, dict[str, int]] = {}
    errors = []
    for run in runs:
        for grader in run["graders"]:
            if grader.get("withOnly") or grader.get("scored") is False:
                continue
            if str(grader.get("explanation", "")).startswith(GRADER_THREW):
                errors.append(f"{grader['name']}: {grader['explanation']}")
                continue
            tally = counts.setdefault(grader["name"], {"passed": 0, "runs": 0})
            tally["runs"] += 1
            tally["passed"] += 1 if grader["passed"] else 0
    return counts, errors


def summarize(results: list[dict], skill: str, arm: str, slice_: str, words: int, conf: dict,
              inputs: dict[str, str]) -> dict:
    for result in results:
        if result.get("schemaVersion") != 1:
            raise SystemExit(f"unknown eval result schemaVersion {result.get('schemaVersion')!r}; update skill_eval.py")
        if result.get("partial"):
            raise SystemExit(f"the eval run is partial ({result.get('partialReason')}); run it again")
    runs: dict[str, list[dict]] = {}
    for result in results:
        for case in result["cases"]:
            runs.setdefault(case["name"], []).extend(case["arms"]["with"])
    cases, errors, models = {}, {}, set()
    for name, case_runs in runs.items():
        valid = []
        for run in case_runs:
            error, run_models = run_error(run, skill)
            models.update(run_models)
            if error:
                errors.setdefault(name, []).append(error)
            else:
                valid.append(run)
        cases[name], grader_errors = grader_counts(valid)
        if grader_errors:
            errors.setdefault(name, []).extend(grader_errors)
    return {"skill": skill, "arm": arm, "slice": slice_, "skill_words": words,
            "claude_version": sorted({r["claudeVersion"] for r in results}),
            "started_at": min(r["startedAt"] for r in results),
            "cost_usd": round(sum(r["costUsd"] for r in results), 4),
            "judge_model": conf["judge_model"], "agent_models": sorted(models), "inputs": inputs,
            "cases": cases, "errors": errors}


def rates(summary: dict) -> dict[tuple[str, str], float]:
    return {(case, grader): t["passed"] / t["runs"]
            for case, graders in summary["cases"].items() for grader, t in graders.items() if t["runs"]}


def baseline_rates(rounds: list[dict], floor: float) -> dict[tuple[str, str], tuple[float, float]]:
    per_round = [rates(r) for r in rounds]
    keys = set().union(*per_round)
    found = {}
    for key in keys:
        values = [r[key] for r in per_round if key in r]
        found[key] = (sum(values) / len(values), max(max(values) - min(values), floor))
    return found


def worse(base: dict[tuple[str, str], tuple[float, float]], candidate: dict) -> list[str]:
    cand = rates(candidate)
    found = []
    for (case, grader), (mean, noise) in sorted(base.items()):
        if (case, grader) not in cand:
            found.append(f"{case} / {grader}: no valid run, so no result")
        elif cand[(case, grader)] < mean - noise - 1e-9:
            found.append(f"{case} / {grader}: {cand[(case, grader)]:.2f} against {mean:.2f} ± {noise:.2f}")
    return found


def input_drift(reference: dict, other: dict, label: str) -> list[str]:
    lines = []
    for key in ("judge_model", "agent_models"):
        if reference.get(key) != other.get(key):
            lines.append(f"{label}: {key} {other.get(key)} differs from the baseline's {reference.get(key)}")
    ref_inputs, other_inputs = reference.get("inputs", {}), other.get("inputs", {})
    changed = sorted(k for k in set(ref_inputs) | set(other_inputs) if ref_inputs.get(k) != other_inputs.get(k))
    lines += [f"{label}: case file {k} changed since the baseline; record a new baseline" for k in changed]
    return lines


def compare(baseline: dict, rounds: list[dict], held_out: dict | None, cand_tune: dict, cand_held_out: dict | None,
            floor: float, fresh_full: list[dict] | None = None) -> tuple[bool, list[str]]:
    lines, keep = [], True
    if not baseline.get("approved"):
        lines.append("baseline: not approved by the operator yet, so no candidate can be kept")
        keep = False
    drift = input_drift(rounds[0], cand_tune, "tune")
    if held_out is not None and cand_held_out is not None:
        drift += input_drift(held_out, cand_held_out, "held-out")
    for summary in [cand_tune] + ([cand_held_out] if cand_held_out else []):
        lines += [f"error, not counted: {summary['slice']}: {case}: {e}"
                  for case, errors in sorted(summary.get("errors", {}).items()) for e in errors]
    lines += drift
    keep = keep and not drift
    tune_worse = worse(baseline_rates(rounds + (fresh_full or []), floor), cand_tune)
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


def planted_dir(skill: str, evals: Path = EVALS) -> Path:
    return evals / skill / "planted"


def planted_specs(skill: str, evals: Path = EVALS):
    """Each planted set: its spec, the grader file it checks, and its answers as (case name, should pass, text)."""
    for spec_file in sorted(planted_dir(skill, evals).glob("*/planted.json")):
        spec = json.loads(spec_file.read_text())
        grader = next(evals.glob(f"{skill}/*/{spec['case']}/graders/{spec['grader']}.md"))
        answers = [(f"{spec['case']}--{spec['grader']}--{answer}", expect == "pass",
                    (spec_file.parent / f"{answer}.md").read_text().strip())
                   for answer, expect in spec["answers"].items()]
        yield spec, grader, answers


def stage_planted(skill: str, work: Path, evals: Path = EVALS) -> Path:
    """Each planted answer becomes a case: the prompt makes the model reply with that answer, and the one grader
    under test judges it. The real case's prompt is not used, so the skill is not loaded and no load proof is asked."""
    staged = copy_plugin(skill, work)
    out = staged / STAGED_EVAL_DIR
    for spec, grader, answers in planted_specs(skill, evals):
        for name, should_pass, text in answers:
            case = out / name
            (case / "graders").mkdir(parents=True)
            shutil.copy(grader, case / "graders" / grader.name)
            (case / "prompt.md").write_text(
                f"---\ndescription: A planted {'right' if should_pass else 'wrong'} answer for {spec['grader']}.\n"
                "expected_outcome: The reply is the planted text, word for word.\nmax_turns: 2\n---\n\n"
                "Reply with the text between the two marker lines, word for word, and nothing else. "
                "Do not add the marker lines and do not use any tool.\n\n=== BEGIN ===\n" + text + "\n=== END ===\n")
    return staged


def words(text: str) -> list[str]:
    return re.sub(r"[`*_#>\s]+", " ", text).strip().split()


def planted_report(result: dict, skill: str, conf: dict, evals: Path = EVALS) -> dict:
    gate = conf["planted"]
    expected, graders = {}, {}
    for spec, grader, answers in planted_specs(skill, evals):
        key = f"{spec['case']}/{spec['grader']}"
        graders[key] = {"answers": 0, "false_pass": 0, "false_fail": 0, "errors": [], "grader_sha": sha(grader),
                        "approved": spec.get("approved")}
        expected.update({name: (key, should_pass, text) for name, should_pass, text in answers})
    for case in result["cases"]:
        key, should_pass, text = expected[case["name"]]
        tally = graders[key]
        for run in case["arms"]["with"]:
            verdict = next((g for g in run["graders"] if not g.get("withOnly")), None)
            if run.get("error") or verdict is None or str(verdict.get("explanation", "")).startswith(GRADER_THREW):
                tally["errors"].append(f"{case['name']}: {run.get('error') or (verdict or {}).get('explanation')}")
            elif words(verdict.get("evidence", ""))[:40] != words(text)[:40]:
                tally["errors"].append(f"{case['name']}: the reply is not the planted text")
            else:
                tally["answers"] += 1
                tally["false_pass"] += 1 if verdict["passed"] and not should_pass else 0
                tally["false_fail"] += 1 if not verdict["passed"] and should_pass else 0
    for tally in graders.values():
        tally["gates"] = (tally["answers"] >= gate["answers_per_grader"] and tally["false_pass"] <= gate["false_pass_max"]
                          and tally["false_fail"] <= gate["false_fail_max"])
    return {"skill": skill, "judge_model": conf["judge_model"], "claude_version": result["claudeVersion"],
            "started_at": result["startedAt"], "cost_usd": result["costUsd"], "graders": graders}


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


def run_rounds(skill: str, slice_: str, candidate: Path | None, conf: dict, drafts: bool) -> int:
    """Run the eval for real. A CORE comparison runs one round at a time, full and candidate in turn, so both arms
    see the same conditions; every other run is one command with the tier's run count."""
    tier = tier_of(conf, skill)
    alternate = candidate is not None and tier["name"] == "CORE"
    arms = [("full", None), ("candidate", candidate)] if alternate else [
        ("candidate" if candidate else "full", candidate)]
    rounds, per_round = (tier["runs"], 1) if alternate else (1, tier["runs"])
    results: dict[str, list[Path]] = {arm: [] for arm, _ in arms}
    for i in range(rounds):
        for arm, folder in arms:
            work = EVALS / ".work" / f"{skill}-{arm}-{slice_}"
            staged = stage(skill, slice_, folder, work, drafts)
            result = work / f"result-{i}.json"
            subprocess.run(eval_command(staged, per_round, result, conf), check=False)
            results[arm].append(result)
    for arm, folder in arms:
        main(["summarize", *map(str, results[arm]), skill, "--arm", arm, "--slice", slice_]
             + (["--candidate", str(folder)] if folder else []))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("stage")
    p.add_argument("skill")
    p.add_argument("--slice", choices=SLICES, default="tune")
    p.add_argument("--candidate", type=Path, help="a folder holding the shorter skill; omit for the full skill")
    p.add_argument("--work", type=Path, help="where to stage; default evals/skills/.work/<skill>-<arm>-<slice>")
    p.add_argument("--draft-references", action="store_true", help="also grade reference answers not yet approved")
    p.add_argument("--go", action="store_true", help="run the eval and summarize it (real model calls)")

    p = sub.add_parser("summarize")
    p.add_argument("result", type=Path, nargs="+")
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
    p.add_argument("--full", type=Path, nargs="*", help="full-skill summaries run beside the candidate (CORE)")

    p = sub.add_parser("planted")
    p.add_argument("skill")
    p.add_argument("--go", action="store_true", help="run the planted answers and report (real model calls)")

    p = sub.add_parser("planted-report")
    p.add_argument("result", type=Path)
    p.add_argument("skill")

    args = parser.parse_args(argv)
    conf = settings()

    if args.command == "stage":
        if args.go:
            return run_rounds(args.skill, args.slice, args.candidate, conf, args.draft_references)
        arm = "candidate" if args.candidate else "full"
        work = args.work or EVALS / ".work" / f"{args.skill}-{arm}-{args.slice}"
        staged = stage(args.skill, args.slice, args.candidate, work, args.draft_references)
        result = work / "result.json"
        command = eval_command(staged, tier_of(conf, args.skill)["runs"], result, conf)
        summary = ["python3", "scripts/skill_eval.py", "summarize", str(result), args.skill, "--arm", arm,
                   "--slice", args.slice] + (["--candidate", str(args.candidate)] if args.candidate else [])
        print(f"staged {staged}\n\nrun (real model calls):\n  {' '.join(command)}\nthen:\n  {' '.join(summary)}")
        return 0

    if args.command == "summarize":
        folder = skill_dir(args.skill, args.candidate)
        summary = summarize([load(r) for r in args.result], args.skill, args.arm, args.slice, skill_words(folder),
                            conf, case_inputs(cases_dir(args.skill, args.slice)))
        stamp = summary["started_at"][:19].replace(":", "")
        write(args.out or EVALS / args.skill / "results" / f"{stamp}-{args.arm}-{args.slice}.json", summary)
        for case, errors in sorted(summary["errors"].items()):
            print("\n".join(f"error, not counted: {case}: {e}" for e in errors))
        return 0

    if args.command == "baseline":
        rounds = [load(p) for p in args.tune]
        needed = tier_of(conf, args.skill)["baseline_rounds"]
        if len(rounds) < needed:
            raise SystemExit(f"a baseline needs {needed} tune rounds, got {len(rounds)}")
        if any(r["arm"] != "full" or r["slice"] != "tune" for r in rounds):
            raise SystemExit("a baseline's tune rounds are full-skill tune summaries")
        rel = lambda p: str(Path(p).resolve().relative_to(ROOT))  # noqa: E731
        write(EVALS / args.skill / "baseline.json",
              {"skill": args.skill, "recorded": date.today().isoformat(), "approved": None,
               "tune": [rel(p) for p in args.tune], "held_out": rel(args.held_out) if args.held_out else None})
        print("the operator approves it by setting \"approved\" in a pull request")
        return 0

    if args.command == "planted":
        work = EVALS / ".work" / f"{args.skill}-planted"
        staged = stage_planted(args.skill, work)
        result = work / "result.json"
        command = eval_command(staged, 1, result, conf)
        print(f"staged {staged}\n\nrun (real model calls):\n  {' '.join(command)}\nthen:\n"
              f"  python3 scripts/skill_eval.py planted-report {result} {args.skill}")
        if args.go:
            subprocess.run(command, check=False)
            return main(["planted-report", str(result), args.skill])
        return 0

    if args.command == "planted-report":
        report = planted_report(load(args.result), args.skill, conf)
        write(planted_dir(args.skill) / "results.json", report)
        for key, t in sorted(report["graders"].items()):
            print(f"{key}: {t['answers']} answers, {t['false_pass']} false PASS, {t['false_fail']} false FAIL, "
                  f"{len(t['errors'])} errors → {'gates' if t['gates'] else 'may not gate'}")
        return 0 if all(t["gates"] for t in report["graders"].values()) else 1

    baseline = load(EVALS / args.skill / "baseline.json")
    rounds = [load(ROOT / p) for p in baseline["tune"]]
    held_out = load(ROOT / baseline["held_out"]) if baseline.get("held_out") else None
    floor = conf["noise_floor_runs"] / tier_of(conf, args.skill)["runs"]
    keep, lines = compare(baseline, rounds, held_out, load(args.tune),
                          load(args.held_out) if args.held_out else None, floor,
                          [load(p) for p in (args.full or [])])
    print("\n".join(lines))
    return 0 if keep else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
