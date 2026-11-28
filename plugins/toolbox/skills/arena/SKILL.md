---
name: arena
description: Run several agents on the same design task, score their results against a fixed rubric, and build the best one with the good parts of the rest. Use for /arena.
disable-model-invocation: true
---

# Arena

**You own the choice, not the candidates. Each one gets the same task; the rubric, not your taste, picks.**

## Before you start

Load the rulebook's `crq` skill for its worker notes, and its `code` and `planning` skills for the verify step. If the
rulebook is not installed, stop and say this tool needs it. Write a todo with one entry per phase before you start
anything.

## Phases

1. **Frame.** Write the one prompt every candidate gets: the artifact to produce and the grounding files. Write a
   rubric of 3 to 6 criteria that can be graded on this task, such as "each piece of state has one owner". The
   candidates never see the rubric. Done when the prompt and the rubric are written.
2. **Fan out.** Start 3 candidates at once by `crq`'s worker notes, each kickoff naming the same SHA, each in its own
   git worktree (with none, its own folder under the scratchpad), because two writers in one place overwrite each
   other. Each returns its artifact and a short reason naming the shapes it rejected. A candidate with no output drops
   out; go on with the rest and say so. With no way to start helpers, stop and say so, because candidates from one
   author share that author's blind spots. Done when each candidate has returned or dropped out.
3. **Judge.** Start one read-only judge on a different model from yours where the harness offers one (another
   vendor's model in Copilot CLI, another Claude model in Claude Code). It scores each candidate on each criterion and
   names a base. With no other model, skip the judge and say so. Done when the judge has scored, or is skipped.
4. **Pick a base.** Read every candidate whole, and score each candidate on each criterion, not by feel. Compare with
   the judge: agreement confirms the base; a disagreement means a bias or an unclear rubric, so read both reasons
   before you decide. On a tie, take the cleaner boundary or the smaller interface. When no candidate leads on more
   than one criterion, the frame was unclear: write it again and go back to phase 2. Done when a base is named with
   its scores.
5. **Graft.** Walk each losing candidate once for one or two parts worth taking, and fold each in by hand so the
   result keeps one design. When all candidates agree, say so and take the shared shape. Done when each loser has a
   graft or "nothing taken" with a reason.
6. **Verify.** Verify a code result by `code`'s verify notes, and a design result against the rubric and `planning`'s
   spec-review list. A problem found here means the frame was wrong or a graft was missed; go back to that phase.
   Done when the check passes.

## Report

One artifact, and a note beside it: the base and why, the judge's scores or that it was skipped, each graft with its
source, what was rejected and why, any agreement or dropout, and the verification result.
