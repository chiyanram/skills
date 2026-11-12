# Principles

Approved by the operator, 2026-11-11. Changed only by pull request.

What this repo holds to. Each principle is guidance: a change that departs from one says which and why in its pull
request. `AGENTS.md` holds the hard rules; `CONTRIBUTING.md` holds the procedures.

## Index

- [K1](#k1) — Knowledge only, and it works on its own.
- [K2](#k2) — One rule, two readers.
- [K3](#k3) — A rule is short, says why, and enters with its owner's yes.
- [K4](#k4) — A skill is a short entry that points to its references.
- [K5](#k5) — Rules grow from our own failures.
- [K6](#k6) — Say only what the model wouldn't do, and keep it short.
- [K7](#k7) — A script or lint beats a prose rule.
- [K8](#k8) — This repo publishes the versioned format of what it ships.
- [K9](#k9) — A change ships only if the evals say so.

## K1

What ships is knowledge only. The plugins hold instructions, data and the small check scripts a skill tells the agent
to run, never engine code; the repo's own tests and design stay outside them. It works without the engine.

**Why.** Plain files can be read by any agent, and `/crq` runs on a laptop with no engine installed. Small check
scripts may ship so that K7 can hold.

The `toolbox` plugin follows the same rule and adds two: every tool is typed-only (`disable-model-invocation: true`),
with no push or merge, because a person chooses when a tool runs; and it versions and releases on its own line, so a
tool change never bumps the rulebook.

**How it's checked.** `check_plugin.py` fails a plugin that is not in its own folder under `plugins/`, and only those
folders ship. That no engine code enters them is review only.

## K2

One rule, two readers. The writer follows a rule and the reviewer checks that same rule by its ID; no second copy for
the reviewer.

**Why.** When the writer and the reviewer read different text, the review blocks on rules the writer was never shown.

**How it's checked.** `check_process.py` fails a role card that cites a rule ID no reference holds. The rest is review
only.

## K3

A rule is short and says why. It enters only with its rulebook owner's yes; where it came from lives in the ledger,
never in the rule.

**Why.** The agent needs the rule and its reason, not its history. "Owner" rather than one named person, so a team's own
rulebook works the same way.

**How it's checked.** `check_sizes.py` fails a rule over 35 words, `check_provenance.py` fails a source in a shipped
file, and `check_ledger.py` checks the ledger. The owner's yes is review only.

## K4

A skill is a short entry that points to its references, and its description says when to use it.

**Why.** A run loads only the references its task needs, and an agent picks a skill by its description.

**How it's checked.** `check_skills.py` fails a skill with no description or one over 1024 characters,
`check_routers.py` and `check_index.py` fail a router that does not link each reference, and `check_routing.py` fails a
router that does not win its own requests.

## K5

Rules grow from our own failures: a lesson lands as a rule or a decided edge with its origin, and which rules runs
actually read is measured.

**Why.** Our own failures show where a rule is missing. A lesson lands in the Rules and Decided edges sections every
reference already has, so the format does not change.

**How it's checked.** Review only.

## K6

Say only what the model wouldn't do anyway, and keep it short: prune and condense rules like code, and give the goal
and the limits, not every step.

**Why.** Every line costs context on every run, so text the model would follow anyway is waste. A run given the goal
and the limits is not railroaded. The Good / Bad pairs stay until an eval measures them.

**How it's checked.** `check_sizes.py` fails a rule over 35 words and an instruction chain over its budget. Pruning,
at each rule's review-by date, is review only.

## K7

Where a check can run, ship a script or lint, not a prose rule.

**Why.** A script beats prose: a check that runs fails every time, and a prose rule can be missed.

**How it's checked.** Review only.

## K8

This repo publishes the versioned format of its cards, lanes and findings, and its CI checks every card against it.

**Why.** This repo stands alone and owns its formats. A tool that uses it pins a version and reads that version's
format.

**How it's checked.** `check_process.py` validates every role card and the lanes file against the versioned schemas in
`process/schema/`, and fails when a schema is missing.

## K9

A change to a rule, card or reference ships only if this repo's evals, on cases it was not tuned on, show it no worse,
and better than the noise on what it aims at.

Until an eval covers it, its pull request says "untested by an eval".

**Why.** "No worse" alone lets aimless changes through, and "better everywhere" would block a change that only lowers
cost.

**How it's checked.** Review only: the role evals run by hand, and the pull request shows their result or says "untested
by an eval".
