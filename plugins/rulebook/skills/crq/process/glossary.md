# Glossary

One word per idea. Every role card, lanes-v2 (`lanes-v2.json`) and every hand-off use these words, and only these.
When you reach for a word under "avoid", use the term instead.

## The factory

| term | meaning | avoid |
|---|---|---|
| **engine** | the code that runs the process for a project: the orchestrator plus every check it runs (ready check, push guards, approval records, settings); never the model | the system, the code (for the engine) |
| **orchestrator** | the part of the engine that receives triggers, starts runs on runners, and records which runs are queued, in flight or finished | dispatcher, scheduler, control plane |
| **task** | a kind of work, defined once and run many times: implement, automated review, rework, retro | job, workflow, action |
| **trigger** | the event that starts a run: a human START, a human approval, or the run before | — |
| **run** | one execution of a task on one runner, from its trigger to its end; a run never waits for a human, and the human's later answer triggers a new run | session |
| **runner** | the disposable machine a run executes on; nothing on it survives the run | box, sandbox, server, host |
| **ticket tracker** | where tickets live | issue tracker, project board |
| **ticket** | one tracked piece of work | issue (for a ticket), story |
| **git host** | where branches, PRs and reviews live | forge, code host, repo |
| **PR** | a pull request | MR, merge request |
| **automated review** | the task that reviews a PR: one finder run per lens, then one verify pass run; design review has the same shape, a design-reviewer run then a verify pass | reviewer (alone), verifier |
| **extra task** | a task outside a ticket's flow, such as a full retro; it runs only when a human starts it | — |
| **project home** | a place outside the product repo where the engine keeps a project's settings, brief and glossary | — |

## A ticket's way through

| term | meaning | avoid |
|---|---|---|
| **START** | a human's instruction to open a ticket; nothing runs without one | — |
| **lane** | how much process a change gets: tiny, bug, feature or one-way door; lanes-v2 says which phases each lane takes | size, type, category |
| **phase** | one step of the flow, named by a kebab id, done by one actor: a role, the engine or a human | stage, step |
| **outcome** | a named way a phase ends, such as `done`, `act-on` or `red`; each outcome has one edge | result, status |
| **edge** | where an outcome goes: `next` (the lane's next phase), a named phase, `human` (the ticket waits for a human), `human, then same` (a human answers, then the same phase runs again) or `end`; a back edge to a phase the lane skipped lands on the nearest earlier phase the run took | transition |
| **cap** | the most times a counted edge may be taken in one ticket, since its last lane raise; a lane's lens cap is the most lenses its code review runs | limit, budget |
| **lane condition** | a named question the coordinator answers yes or no on the ticket, which decides whether a lane takes a phase marked with it | flag |
| **lane raise** | moving a change to a heavier lane after intake: it returns to spec, needs approval again, and its round counts restart at zero | upgrade, escalation |
| **approval** | a human's yes to a spec and its design, bound to their hashes, that releases the build; tiny needs START only; any later edit makes it stale; a model never approves | — |
| **spec** | the approved contract, one file with the intent, the lane, the ACs, a link to the design or `none`, and what is out of scope | requirements, story (for this file) |
| **AC** | one acceptance criterion in the spec, named AC-n, decidable by a test | requirement, condition |
| **design** | the chosen shape, one rejected alternative, and the slices; the spec links it | plan (alone), architecture doc |
| **slice** | one thin end-to-end piece of the design, with the command that proves it | task (for a slice), chunk |
| **spec home** | where a project keeps its specs | — |
| **ask** | a run that needs a human's decision ends with status `asked` and every open question at once, in one numbered round; a coordinator asks at most three and turns the rest into marked defaults that "accept all" takes; each question carries 2 to 4 short choices and one recommended choice, so the human answers with taps, "1A 2B" or "accept all"; the project's `questions` setting can be `one-at-a-time` instead; never a guess; the answer goes into the spec | clarify inline, assume |
| **evidence row** | `{criterion, command, result}`: one AC and the plain command that proves it | proof, output |
| **hand-off** | what a role leaves for the next role: a file, or the JSON a read-only run returns | summary, notes |
| **ready check** | the engine re-running every evidence row at the head, checking that every AC has a row, plus the test checks and the lane check; the engine runs it in the `verify` phase | — |
| **test checks** | what the engine stops without a model: a test removed, a skip added, fewer assertions, a judge file changed | — |
| **judge files** | tests, test config, the gate command and what it runs | test setup, harness |
| **gate** | the full test run before a human is asked to merge: CI, a queue, or a local run on a runner | — |
| **finding** | one problem at `file:line`, with the rule it breaks | comment, remark |
| **severity** | how bad a finding is, set by the finder: blocker, warning or nit; each review check's Severity line gives it, and a style finding is always a nit | Act on, Consider (for a severity) |
| **bucket** | what happens to a finding, set by the verify pass: Act on (`act_on`), Consider (`consider`), noted or dismissed; the cited rule's severity decides it, blocker → Act on and warning → Consider | severity (for a bucket) |
| **lens** | one rubric a fresh finder applies | perspective, reviewer type |
| **break scenario** | one way a design fails: a trigger, its chain of effects, the first sign, the AC-n or decision it hits, and one closure (a failure AC, a mitigation or an accepted risk) | edge case, risk (alone), what-if |

## Roles

A **role card** is one markdown file per role. The engine enforces its frontmatter; the model reads its body.

| role | job | avoid |
|---|---|---|
| **coordinator** | talks with the human: research, questions, spec and design; it never approves and never starts a run | — |
| **design-reviewer** | gives every decision in a design one verdict (aligned, conflict, open) before approval | — |
| **test-first** | in the bug lane, the separate run that writes the failing test before the implementer runs | — |
| **implementer** | builds the spec and proves each AC | writer |
| **cleanup** | tidies the branch's own lines without changing behaviour; what would change behaviour goes in `deferred` | — |
| **finder** | one fresh run per lens that reports findings; it never approves | reviewer (alone) |
| **verify pass** | the run that tries to refute each finding and gives it one bucket: act_on, consider, noted or dismissed | verifier |
| **retro** | the timeline record the engine writes for every merge, and the full retro run a human starts | — |
| **onboarder** | writes a project's brief and glossary once, for every other role; it writes only to the project home; its card is the engine's | — |
