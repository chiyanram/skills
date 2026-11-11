import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import skill_eval  # noqa: E402

FLOOR = 1 / 3


def result(passes: dict[str, dict[str, list[bool]]], version: int = 1) -> dict:
    return {"schemaVersion": version, "claudeVersion": "x", "startedAt": "2026-11-11T10:00:00Z", "costUsd": 0,
            "partial": False,
            "cases": [{"name": case, "arms": {"with": [
                {"graders": [{"name": g, "passed": runs[i], "withOnly": False} for g, runs in graders.items()]
                 + [{"name": "fired", "passed": False, "withOnly": True}]}
                for i in range(len(next(iter(graders.values()))))]}}
                for case, graders in passes.items()]}


def summary(passes, words=100, arm="full", slice_="tune") -> dict:
    return skill_eval.summarize(result(passes), "demo", arm, slice_, words)


ALL_PASS = {"a": {"g1": [True, True, True], "g2": [True, True, True]}}
ONE_MISS = {"a": {"g1": [True, True, False], "g2": [True, True, True]}}
TWO_MISS = {"a": {"g1": [True, False, False], "g2": [True, True, True]}}


class SkillEvalTest(unittest.TestCase):
    def compare(self, cand, words=60, approved="operator", held_out=True):
        rounds = [summary(ALL_PASS), summary(ALL_PASS)]
        base = {"approved": approved}
        held = summary(ALL_PASS, slice_="held-out") if held_out else None
        cand_held = summary(ALL_PASS, words, "candidate", "held-out") if held_out else None
        return skill_eval.compare(base, rounds, held, summary(cand, words, "candidate"), cand_held, FLOOR)

    def test_should_count_scored_graders_only(self):
        self.assertEqual(summary(ONE_MISS)["cases"]["a"], {"g1": {"passed": 2, "runs": 3},
                                                             "g2": {"passed": 3, "runs": 3}})

    def test_should_refuse_an_unknown_result_schema(self):
        with self.assertRaises(SystemExit):
            skill_eval.summarize(result(ALL_PASS, version=2), "demo", "full", "tune", 1)

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

    def test_should_keep_nothing_against_an_unapproved_baseline(self):
        keep, _ = self.compare(ALL_PASS, approved=None)
        self.assertFalse(keep)

    def test_should_keep_nothing_without_the_held_out_slice(self):
        keep, _ = self.compare(ALL_PASS, held_out=False)
        self.assertFalse(keep)

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


class SkillEvalCasesTest(unittest.TestCase):
    def test_should_give_each_skill_eval_both_slices_with_graded_cases(self):
        skills = [d for d in skill_eval.EVALS.iterdir() if d.is_dir() and not d.name.startswith(".")]
        self.assertTrue(skills)
        for skill in skills:
            self.assertTrue((skill_eval.PLUGIN / "skills" / skill.name / "SKILL.md").is_file(), skill.name)
            for slice_ in skill_eval.SLICES:
                cases = [c for c in (skill / slice_).iterdir() if c.is_dir()]
                self.assertTrue(cases, f"{skill.name}/{slice_} has no cases")
                for case in cases:
                    with self.subTest(case=str(case.relative_to(ROOT))):
                        self.assertTrue((case / "prompt.md").read_text().startswith("---\ndescription: "))
                        self.assertTrue(list((case / "graders").glob("*.md")))

    def test_should_name_every_case_once_across_all_evals(self):
        names = [p.parent.name for root in (skill_eval.EVALS, skill_eval.PLUGIN / "evals")
                 for p in root.glob("**/prompt.md") if ".work" not in p.parts]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
