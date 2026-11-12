# Pruning method

How this repo cuts a skill down without losing what it does, and how the cut is measured. Read it before you
prune a skill, a reference or a role card, or before you change the skills eval that judges a cut. K6 says prune
rules like code; K9 says a skill is judged by use, with this eval run locally when a cut needs measuring.
This page says how the cut is measured.

## The source

Thariq Shihipar, ["The new rules of context engineering for Claude 5 generation models"](https://claude.dev/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models/),
Anthropic, 24 July 2026 (first linked as `claude.com/blog/…`, which now redirects there). It reports removing over
80% of Claude Code's system prompt for the newest models "with no measurable loss on our coding evaluations".

## What the article says was cut

The article groups the cut into six shifts. Each names what was removed and what took its place.

| then | now | what was cut |
|---|---|---|
| give Claude rules | let Claude use judgement | absolute rules written for the worst case ("default to writing no comments"), replaced by one line of intent ("match its comment density, naming, and idiom") |
| give Claude examples | design interfaces | usage examples, which "constrain them to a certain exploration space"; an expressive parameter, such as an enum of states, does the teaching |
| put it all upfront | use progressive disclosure | detail that is needed only sometimes, such as code review and verification, moved into skills loaded when needed; tools load late too |
| repeat yourself | simple tool descriptions | the same instruction in two places; it now lives once, where it is used |
| memory in CLAUDE.md files | auto-memory | asking the user to save memories by hand |
| simple specs | rich references | prose descriptions where a file in code, a test suite or a rubric says it better |

For skills it says: keep them light guides that help Claude find information when needed, not overconstrained
except in highly important areas; split a long skill into many files; and keep what is particular to you, your team
or your product. It also names `/doctor` in Claude Code, which rightsizes skills and CLAUDE.md files.

## What the article does not say

The article gives the result and the kinds of cut, not the procedure. It is silent on:

- the order of the cuts, or whether they were made one at a time or all at once;
- which coding evaluations ran, on how many tasks, and with what score;
- what threshold counted as "no measurable loss";
- how run-to-run noise was measured or handled, and whether any tasks were held out.

The steps below fill those gaps. They are this repo's choices, not the article's, and the operator approves them
with the eval that runs them.

## The method here

1. **Fix the tasks.** Each skill gets a small fixed set of real tasks of the kind it governs: small changes, each
   with the review checks from that skill's own references that decide pass or fail. Some tasks are held out: they
   never run while a cut is tuned, only at the gate.
2. **Measure the baseline.** Run the full skill on the tuning tasks, more than once, and keep the results. The
   baseline is the operator-approved result: the pass rate of each check, and the size of what the skill loads.
3. **Measure the noise.** The spread between repeated baseline runs is the noise. A difference smaller than the
   noise is no difference.
4. **Cut one kind at a time**, in this order, safest first; the order is ours: a repeated instruction; an
   instruction the model follows anyway (K6); an example where the interface or the rule already teaches; detail
   that can move behind a link (progressive disclosure). A rule's ID, its "because" and its review check stay: the
   reviewer reads the same rule (K2), and a rule leaves only by the ledger.
5. **Measure the candidate** on the same tuning tasks, the same number of runs.
6. **Keep it only if** no check that must hold passes less often than the baseline by more than the noise, and the
   skill is smaller than before. Size is counted, not sampled, so any real cut is beyond noise.
7. **Run the held-out slice at the gate.** A cut that is no worse on the tuning tasks and worse on the held-out
   ones was tuned to the tasks: it does not ship.
8. **One pruning pass, one PR.** The PR shows the candidate's result beside the baseline, and the held-out result.
   A per-reference word cap is added only if the data says it helps; today's cap is 35 words per rule
   (`scripts/check_sizes.py`).

## Where it is checked

Review only, until the skills eval exists. Every run there is a real model call, so it runs by hand, never in
`make lint`, `make test` or CI.
