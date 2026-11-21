"""The eval proof each skill's tier asks for is committed and still matches its cases, checked with no model call.

`evals/skills/settings.json` names each skill's tier. A skill with no tier is skipped. For each tiered skill:
- the plugin ships the skill, and both slices (`tune`, `held-out`) hold cases with a `prompt.md` and graders;
- each case has a `reference.md` whose `approved` field is set;
- `baseline.json` exists with its `approved` field set, and every summary it names exists;
- each summary was made from the case files on disk and the pinned judge: a hash that no longer matches is stale;
- a CORE skill also has `planted/results.json`, where every llm grader passed its planted answers, with an approved
  planted set and the same grader file.

A tier that requires approval (CORE) fails on any missing or unapproved part. Other tiers print a warning for it and
pass, so a skill can grow its proof one pull request at a time. A stale summary behind an approved baseline fails in
every tier, because that approval no longer covers the cases.
"""
import json
import sys
from pathlib import Path

from skill_eval import SLICES, approved, case_inputs, frontmatter, sha


def summary_drift(summary: dict, cases: Path, judge: str) -> list[str]:
    current = case_inputs(cases)
    recorded = summary.get("inputs", {})
    changed = sorted(k for k in set(current) | set(recorded) if current.get(k) != recorded.get(k))
    found = [f"case file {k} changed" for k in changed]
    if summary.get("judge_model") != judge:
        found.append(f"judge {summary.get('judge_model')} is not the pinned {judge}")
    return found


def llm_graders(skill_evals: Path) -> dict[str, str]:
    return {f"{g.parent.parent.name}/{g.stem}": sha(g) for slice_ in SLICES
            for g in sorted((skill_evals / slice_).glob("*/graders/*.md")) if frontmatter(g)[0].get("type") == "llm"}


def check_skill(root: Path, skill: str, tier: dict, conf: dict) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    soft = problems if tier.get("requires_approval") else warnings
    if not list(root.glob(f"plugins/*/skills/{skill}/SKILL.md")):
        problems.append("no plugin ships this skill")
    evals = root / "evals" / "skills" / skill
    for slice_ in SLICES:
        cases = sorted(c for c in (evals / slice_).glob("*") if c.is_dir())
        if not cases:
            problems.append(f"{slice_}: no cases")
        for case in cases:
            if not (case / "prompt.md").is_file() or not list((case / "graders").glob("*.md")):
                problems.append(f"{slice_}/{case.name}: needs a prompt.md and at least one grader")
            reference = case / "reference.md"
            if not reference.is_file():
                soft.append(f"{slice_}/{case.name}: no reference answer")
            elif not approved(frontmatter(reference)[0]):
                soft.append(f"{slice_}/{case.name}: reference answer not approved")
    baseline_file = evals / "baseline.json"
    if not baseline_file.is_file():
        soft.append("no baseline")
    else:
        baseline = json.loads(baseline_file.read_text())
        is_approved = bool(baseline.get("approved"))
        if not is_approved:
            soft.append("baseline not approved")
        stale = problems if is_approved else warnings
        named = [("tune", p) for p in baseline.get("tune", [])] + (
            [("held-out", baseline["held_out"])] if baseline.get("held_out") else [])
        for slice_, rel in named:
            path = root / rel
            if not path.is_file():
                problems.append(f"baseline names {rel}, which does not exist")
                continue
            for drift in summary_drift(json.loads(path.read_text()), evals / slice_, conf["judge_model"]):
                stale.append(f"{rel} is stale: {drift}")
    if tier.get("requires_approval"):
        results = evals / "planted" / "results.json"
        graders = json.loads(results.read_text())["graders"] if results.is_file() else {}
        for key, grader_sha in sorted(llm_graders(evals).items()):
            found = graders.get(key)
            if not found:
                problems.append(f"grader {key}: no planted check")
            elif found.get("grader_sha") != grader_sha:
                problems.append(f"grader {key}: changed since its planted check")
            elif not found.get("gates") or not found.get("approved"):
                problems.append(f"grader {key}: its planted check did not pass, or its planted set is not approved")
    return problems, warnings


def problems(root: Path) -> tuple[list[str], list[str]]:
    settings = root / "evals" / "skills" / "settings.json"
    if not settings.is_file():
        return [], []
    conf = json.loads(settings.read_text())
    found, warned = [], []
    for skill, tier_name in sorted(conf.get("skills", {}).items()):
        tier = conf.get("tiers", {}).get(tier_name)
        if tier is None:
            found.append(f"{skill}: unknown tier {tier_name!r}")
            continue
        skill_problems, skill_warnings = check_skill(root, skill, tier, conf)
        found += [f"{skill} ({tier_name}): {p}" for p in skill_problems]
        warned += [f"warning: {skill} ({tier_name}): {w}" for w in skill_warnings]
    return found, warned


if __name__ == "__main__":
    found, warned = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if warned:
        print("\n".join(warned))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
