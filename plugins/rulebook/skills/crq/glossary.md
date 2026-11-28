# Glossary

One word per idea. crq and planning use these words, and only these.
When you reach for a word under "avoid", use the term instead. A check fails a crq or planning file that uses a word under "checked".

## A ticket's way through

| term | meaning | avoid | checked |
|---|---|---|---|
| **ticket tracker** | where tickets live, named in `docs/agents/issue-tracker.md` | issue tracker, project board | — |
| **ticket** | one tracked piece of work | issue (for a ticket), story | story, stories |
| **PR** | a pull request | MR, merge request | MR, merge request |
| **lane** | which stages a change gets, by its kind: feature, bug, tests only, docs only, or config or command | size, type, category | — |
| **one-way-door flag** | the mark on any lane for a change to stored data, a schema, a public contract or a deploy; it adds the yes per irreversible step and the readiness items | one-way-door lane | — |
| **stage** | one step of crq's flow, done by one skill: intake, grill, spec, red test, build, review, deslop, check, PR, watch, report | phase, step | — |
| **status** | how a stage ends: `done`, `blocked` or `needs-human` | outcome, result | — |
| **stop** | one of the four points where crq waits for the person | gate (for a stop), checkpoint | — |
| **grill record** | one ticket comment per grill round: Settled (each answer quoted), Still open (each with its decider), and glossary and ADR gaps | grill notes, grill log | — |
| **plan card** | the session's todo list of each stage, ticked, pending or skipped with `n/a: <why>`; a new session rebuilds it from the branch, the PR and the ticket | checklist, status comment | — |
| **grill round** | every question whose prerequisites are settled, asked at once, each with a recommended answer | — | — |
| **approval** | the person's words that release the build, quoted in the PR body with the commit of the spec they approved; a later edit to the spec needs it again; an agent never approves | sign-off | — |
| **spec** | the approved contract: the intent, the ACs, a link to the design or `none`, and what is out of scope | requirements, story (for this file) | story, stories, requirements |
| **AC** | one acceptance criterion in the spec, named AC-n, decidable by a test | requirement, condition | — |
| **design** | the chosen shape, one rejected alternative, and the slices; the spec links it | plan (alone), architecture doc | — |
| **slice** | one thin end-to-end piece of the design, with the command that proves it | task (for a slice), chunk | — |
| **forbidden state** | a set of field values a type can hold that the domain never allows, such as a refund time on an open order; the fix is one variant per allowed state, each with only its own fields | invalid state, illegal state, forbidden combination | — |
| **derived value** | a stored field that other fields already decide, such as the count of a list; work it out on read, or keep it only as a cache with one owner | stored copy, second copy, redundant state | — |
| **evidence row** | `{criterion, command, result}`: one AC and the plain command that proves it | proof, output | — |
| **check rung** | one command from `docs/agents/checks.md`: lint, changed tests, module, smoke or full gate; each lane names its rung | — | — |
| **finding** | one problem at `file:line`, with the rule it breaks, quoted | comment, remark | — |
| **bucket** | what happens to a verified finding: Act on, Consider, nit, Noted or Dismissed | severity (for a bucket) | — |
| **verdict** | `PASS`, `ISSUES` or `BLOCKED` at a PR's head, from an agent that did not write the PR | sign-off, approval (for a verdict) | — |
| **stack** | a chain of PRs, each based on the branch of the one below it | train, chain | — |
| **trunk** | the branch every PR finally merges into, such as `main` | master (for the role) | — |
| **lens** | one set of review lists a fresh reviewer applies, set by the lane | perspective, reviewer type | — |
| **break scenario** | one way a design fails: a trigger, its chain of effects, the first sign, the AC-n or decision it hits, and one closure (a failure AC, a mitigation or an accepted risk) | edge case, risk (alone), what-if | — |
