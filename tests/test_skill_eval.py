import json
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import skill_eval  # noqa: E402

FLOOR = 1 / 3
CONF = {"judge_model": "claude-sonnet-5-5", "agent_model": "claude-opus-5-5",
        "planted": {"answers_per_grader": 9, "false_pass_max": 0, "false_fail_max": 1}}
SESSIONS = tempfile.TemporaryDirectory()


def session(skill: str | None = "demo", model: str = "claude-opus-5-5") -> str:
    """A run folder as `claude plugin eval --keep-temp` leaves it; returns the run's trace path."""
    run = Path(tempfile.mkdtemp(dir=SESSIONS.name))
    projects = run / "config" / "projects" / "p"
    projects.mkdir(parents=True)
    body = f"Base directory for this skill: /tmp/x/skills/{skill}" if skill else "no skill here"
    (projects / "s.jsonl").write_text(json.dumps({"message": {"model": model, "content": body}}) + "\n")
    return str(run / "out" / "trace.jsonl")


LOADED = session()


def result(passes: dict[str, dict[str, list[bool]]], version: int = 1, trace: str = LOADED,
           error: str | None = None) -> dict:
    return {"schemaVersion": version, "claudeVersion": "x", "startedAt": "2026-11-11T10:00:00Z", "costUsd": 0,
            "partial": False,
            "cases": [{"name": case, "arms": {"with": [
                {"tracePath": trace, "error": error,
                 "graders": [{"name": g, "passed": runs[i], "withOnly": False} for g, runs in graders.items()]
                 + [{"name": "fired", "passed": False, "withOnly": True}]}
                for i in range(len(next(iter(graders.values()))))]}}
                for case, graders in passes.items()]}


def summary(passes, words=100, arm="full", slice_="tune", inputs=None, **kw) -> dict:
    return skill_eval.summarize([result(passes, **kw)], "demo", arm, slice_, words, CONF, inputs or {"a/prompt.md": "1"})


ALL_PASS = {"a": {"g1": [True, True, True], "g2": [True, True, True]}}
ONE_MISS = {"a": {"g1": [True, True, False], "g2": [True, True, True]}}
TWO_MISS = {"a": {"g1": [True, False, False], "g2": [True, True, True]}}


class SkillEvalTest(unittest.TestCase):
    def compare(self, cand, words=60, approved="operator", held_out=True, rewrite=False):
        rounds = [summary(ALL_PASS), summary(ALL_PASS)]
        base = {"approved": approved}
        held = summary(ALL_PASS, slice_="held-out") if held_out else None
        cand_held = summary(ALL_PASS, words, "candidate", "held-out") if held_out else None
        return skill_eval.compare(base, rounds, held, summary(cand, words, "candidate"), cand_held, FLOOR,
                                  rewrite=rewrite)

    def test_should_count_scored_graders_only(self):
        self.assertEqual(summary(ONE_MISS)["cases"]["a"], {"g1": {"passed": 2, "runs": 3},
                                                             "g2": {"passed": 3, "runs": 3}})

    def test_should_refuse_an_unknown_result_schema(self):
        with self.assertRaises(SystemExit):
            skill_eval.summarize([result(ALL_PASS, version=2)], "demo", "full", "tune", 1, CONF, {})

    def test_should_keep_a_smaller_candidate_no_worse_than_the_baseline(self):
        keep, lines = self.compare(ALL_PASS)
        self.assertTrue(keep, lines)

    def test_should_keep_a_drop_within_the_noise(self):
        keep, lines = self.compare(ONE_MISS)
        self.assertTrue(keep, lines)

    def test_should_drop_a_candidate_worse_beyond_the_noise(self):
        keep, lines = self.compare(TWO_MISS)
        self.assertFalse(keep)
        self.assertTrue(any("a / g1" in line for line in lines), lines)

    def test_should_drop_a_candidate_that_is_not_smaller(self):
        keep, _ = self.compare(ALL_PASS, words=100)
        self.assertFalse(keep)

    def test_should_keep_a_larger_rewrite_no_worse_than_the_baseline(self):
        keep, lines = self.compare(ALL_PASS, words=100, rewrite=True)
        self.assertTrue(keep, lines)

    def test_should_drop_a_rewrite_worse_beyond_the_noise(self):
        keep, _ = self.compare(TWO_MISS, words=100, rewrite=True)
        self.assertFalse(keep)

    def test_should_keep_nothing_against_an_unapproved_baseline(self):
        keep, _ = self.compare(ALL_PASS, approved=None)
        self.assertFalse(keep)

    def test_should_keep_nothing_without_the_held_out_slice(self):
        keep, _ = self.compare(ALL_PASS, held_out=False)
        self.assertFalse(keep)

    def test_should_count_an_errored_run_as_an_error_not_a_fail(self):
        found = summary(ONE_MISS, error="timed out after 300s")
        self.assertEqual(found["cases"]["a"], {})
        self.assertEqual(len(found["errors"]["a"]), 3)

    def test_should_count_a_run_without_the_skill_loaded_as_an_error(self):
        found = summary(ALL_PASS, trace=session(skill="other"))
        self.assertEqual(found["cases"]["a"], {})
        self.assertIn("demo was not loaded", found["errors"]["a"][0])

    def test_should_count_a_run_without_a_session_file_as_an_error(self):
        found = summary(ALL_PASS, trace="/nowhere/out/trace.jsonl")
        self.assertIn("no session file", found["errors"]["a"][0])

    def test_should_not_count_a_grader_that_threw(self):
        res = result(ALL_PASS)
        res["cases"][0]["arms"]["with"][0]["graders"][0]["explanation"] = "grader threw: Request was aborted."
        found = skill_eval.summarize([res], "demo", "full", "tune", 1, CONF, {})
        self.assertEqual(found["cases"]["a"]["g1"], {"passed": 2, "runs": 2})
        self.assertTrue(found["errors"]["a"])

    def test_should_record_the_pinned_judge_and_the_agent_model(self):
        found = summary(ALL_PASS)
        self.assertEqual((found["judge_model"], found["agent_models"]), ("claude-sonnet-5-5", ["claude-opus-5-5"]))

    def test_should_merge_runs_from_several_results(self):
        found = skill_eval.summarize([result(ALL_PASS), result(ONE_MISS)], "demo", "full", "tune", 1, CONF, {})
        self.assertEqual(found["cases"]["a"]["g1"], {"passed": 5, "runs": 6})

    def test_should_drop_a_candidate_whose_case_files_changed(self):
        rounds = [summary(ALL_PASS), summary(ALL_PASS)]
        cand = summary(ALL_PASS, 60, "candidate", inputs={"a/prompt.md": "2"})
        held = summary(ALL_PASS, slice_="held-out")
        keep, lines = skill_eval.compare({"approved": "operator"}, rounds, held, cand,
                                         summary(ALL_PASS, 60, "candidate", "held-out"), FLOOR)
        self.assertFalse(keep)
        self.assertTrue(any("a/prompt.md changed" in line for line in lines), lines)

    def test_should_drop_a_candidate_run_on_another_agent_model(self):
        rounds = [summary(ALL_PASS), summary(ALL_PASS)]
        cand = summary(ALL_PASS, 60, "candidate", trace=session(model="claude-haiku-5-5"))
        keep, lines = skill_eval.compare({"approved": "operator"}, rounds, summary(ALL_PASS, slice_="held-out"), cand,
                                         summary(ALL_PASS, 60, "candidate", "held-out"), FLOOR)
        self.assertFalse(keep)
        self.assertTrue(any("agent_models" in line for line in lines), lines)

    def test_should_drop_a_candidate_with_no_valid_run_for_a_case(self):
        rounds = [summary(ALL_PASS), summary(ALL_PASS)]
        cand = summary(ALL_PASS, 60, "candidate", error="interrupted")
        keep, lines = skill_eval.compare({"approved": "operator"}, rounds, summary(ALL_PASS, slice_="held-out"), cand,
                                         summary(ALL_PASS, 60, "candidate", "held-out"), FLOOR)
        self.assertFalse(keep)
        self.assertTrue(any("no valid run" in line for line in lines), lines)

    def test_should_pin_the_judge_and_agent_model_and_keep_the_session_files(self):
        command = skill_eval.eval_command(Path("/s"), 3, Path("/r.json"), CONF)
        for flag, value in (("--judge-model", "claude-sonnet-5-5"), ("--model", "claude-opus-5-5")):
            self.assertEqual(command[command.index(flag) + 1], value)
        self.assertIn("--keep-temp", command)

    def test_should_widen_the_noise_to_the_spread_between_baseline_rounds(self):
        base = skill_eval.baseline_rates([summary(ALL_PASS), summary(TWO_MISS)], FLOOR)
        self.assertAlmostEqual(base[("a", "g1")][1], 2 / 3)

    def test_should_stage_the_candidate_skill_and_one_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "short"
            candidate.mkdir()
            (candidate / "SKILL.md").write_text("---\nname: deslop\ndescription: short\n---\n")
            staged = skill_eval.stage("deslop", "tune", candidate, Path(tmp) / "work")
            self.assertEqual((staged / "skills" / "deslop" / "SKILL.md").read_text(),
                             (candidate / "SKILL.md").read_text())
            self.assertTrue(any((staged / skill_eval.STAGED_EVAL_DIR).glob("*/prompt.md")))
            self.assertFalse((staged / "evals").exists())

    def test_should_grade_a_reference_answer_only_once_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            staged = skill_eval.stage("deslop", "tune", None, Path(tmp) / "work")
            cases = staged / skill_eval.STAGED_EVAL_DIR
            self.assertFalse(list(cases.glob(f"*/graders/{skill_eval.REFERENCE_GRADER}")))
            self.assertFalse(list(cases.glob("*/reference.md")))
            staged = skill_eval.stage("deslop", "tune", None, Path(tmp) / "work", drafts=True)
            graders = list((staged / skill_eval.STAGED_EVAL_DIR).glob(f"*/graders/{skill_eval.REFERENCE_GRADER}"))
            self.assertTrue(graders)
            self.assertNotIn("{{reference}}", graders[0].read_text())
            self.assertTrue(graders[0].read_text().startswith("---\ntype: llm\n---\n"))

    def test_should_stage_each_planted_answer_as_its_own_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            staged = skill_eval.stage_planted("deslop", Path(tmp) / "work")
            cases = sorted((staged / skill_eval.STAGED_EVAL_DIR).glob("*/prompt.md"))
            self.assertEqual(len(cases), 9)
            self.assertIn("=== BEGIN ===", cases[0].read_text())
            self.assertEqual([g.name for g in cases[0].parent.glob("graders/*.md")], ["dead-parameter.md"])


class PlantedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.evals = Path(self.tmp.name)
        case = self.evals / "demo" / "tune" / "demo-case"
        (case / "graders").mkdir(parents=True)
        (case / "graders" / "g1.md").write_text("---\ntype: llm\n---\n\nPASS if right.\n")
        planted = self.evals / "demo" / "planted" / "set"
        planted.mkdir(parents=True)
        answers = {f"right-{i}": "pass" for i in range(3)} | {f"wrong-{i}": "fail" for i in range(6)}
        (planted / "planted.json").write_text(json.dumps(
            {"case": "demo-case", "grader": "g1", "approved": "operator", "answers": answers}))
        for name in answers:
            (planted / f"{name}.md").write_text(f"The answer {name}.")
        self.answers = answers

    def tearDown(self):
        self.tmp.cleanup()

    def report(self, verdicts: dict[str, bool], evidence=None) -> dict:
        cases = [{"name": f"demo-case--g1--{name}", "arms": {"with": [{"error": None, "graders": [
            {"name": "g1", "passed": passed, "evidence": (evidence or {}).get(name, f"The answer {name}.")}]}]}}
            for name, passed in verdicts.items()]
        res = {"claudeVersion": "x", "startedAt": "t", "costUsd": 0, "cases": cases}
        return skill_eval.planted_report(res, "demo", CONF, self.evals)["graders"]["demo-case/g1"]

    def test_should_gate_a_grader_that_judges_every_planted_answer_right(self):
        found = self.report({n: e == "pass" for n, e in self.answers.items()})
        self.assertEqual((found["false_pass"], found["false_fail"], found["gates"]), (0, 0, True))

    def test_should_not_gate_a_grader_with_one_false_pass(self):
        found = self.report({n: e == "pass" or n == "wrong-0" for n, e in self.answers.items()})
        self.assertEqual((found["false_pass"], found["gates"]), (1, False))

    def test_should_gate_a_grader_with_one_false_fail(self):
        found = self.report({n: e == "pass" and n != "right-0" for n, e in self.answers.items()})
        self.assertEqual((found["false_fail"], found["gates"]), (1, True))

    def test_should_count_a_reply_that_is_not_the_planted_text_as_an_error(self):
        found = self.report({n: e == "pass" for n, e in self.answers.items()}, {"right-0": "Something else."})
        self.assertEqual((found["answers"], len(found["errors"]), found["gates"]), (8, 1, False))


class SkillEvalCasesTest(unittest.TestCase):
    def test_should_give_each_skill_eval_both_slices_with_graded_cases(self):
        skills = [d for d in skill_eval.EVALS.iterdir() if d.is_dir() and not d.name.startswith(".")]
        self.assertTrue(skills)
        for skill in skills:
            self.assertTrue((skill_eval.plugin_of(skill.name) / "skills" / skill.name / "SKILL.md").is_file(), skill.name)
            for slice_ in skill_eval.SLICES:
                cases = [c for c in (skill / slice_).iterdir() if c.is_dir()]
                self.assertTrue(cases, f"{skill.name}/{slice_} has no cases")
                for case in cases:
                    with self.subTest(case=str(case.relative_to(ROOT))):
                        self.assertTrue((case / "prompt.md").read_text().startswith("---\ndescription: "))
                        self.assertTrue(list((case / "graders").glob("*.md")))

    def test_should_name_every_case_once_across_all_evals(self):
        names = [p.parent.name for root in (skill_eval.EVALS, skill_eval.PLUGINS / "rulebook" / "evals")
                 for p in root.glob("**/prompt.md") if ".work" not in p.parts]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
